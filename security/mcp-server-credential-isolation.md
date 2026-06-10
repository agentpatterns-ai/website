---
title: "Per-Server MCP Environment Scoping for Credential Isolation"
term: "Per-Server MCP Environment Scoping"
description: "Spawn each MCP server with its own minimal environment scope so one server's credentials never leak to every other server the agent talks to."
tags:
  - security
  - tool-agnostic
  - mcp
last_reviewed: 2026-06-03
---

# Per-Server MCP Environment Scoping for Credential Isolation

> Spawn each MCP server with its own minimal environment scope so one server's credentials never leak to every other server.

Per-server MCP environment scoping is the configuration posture where every MCP server is spawned with an explicit, minimal environment block rather than inheriting the agent host's full environment. A GitHub MCP server sees `GITHUB_TOKEN`; a Postgres server sees `DATABASE_URL`; a Stripe server sees `STRIPE_KEY`. None sees the others. The credential blast radius for any single compromised, buggy, or tricked server is bounded by what the operator deliberately granted.

## The Default That Leaks

Without per-server scoping, the host spawns each MCP server with `os.environ` as the env block, so every secret the operator exported into the agent's shell is visible to every server. A backdoored MCP server with no business seeing a Stripe key can `getenv("STRIPE_KEY")` and exfiltrate it through its own egress channel. This is the Unix default — `execve(2)` passes the calling process's `environ` unless the caller builds a fresh block.

The MCP specification does not mandate env scoping; each host decides. The reference [MCP Python SDK's `stdio_client`](https://github.com/modelcontextprotocol/python-sdk) constructs the spawned server's env from `StdioServerParameters.env` merged with a hard-coded allowlist (`HOME`, `PATH`, `SHELL`, `USER`, and a handful of platform variables); application secrets are not on it. The SDK ships default-deny; whether a host preserves it is a host choice.

## How Each Host Exposes the Knob

Three first-party host implementations name the configuration:

| Host | Surface | Scope shape |
|------|---------|-------------|
| Claude Code | `.mcp.json` per-server `env: {}` map; `claude mcp add --env KEY=value` | Explicit map per server; `${VAR}` and `${VAR:-default}` expansion ([Claude Code MCP](https://code.claude.com/docs/en/mcp)) |
| VS Code Copilot | `.vscode/mcp.json` per-server `env: {}` + `envFile` path; `${input:id}` references | Per-server map; `password: true` inputs stored in OS credential store ([VS Code MCP configuration](https://code.visualstudio.com/docs/copilot/reference/mcp-configuration)) |
| Codex CLI 0.134.0 (2026-05-26) | Per-server environment targeting plus OAuth options for streamable HTTP servers | Explicit per-server env declaration paired with OAuth-token routing ([Codex changelog](https://developers.openai.com/codex/changelog)) |

In all three, the operator opts into which variables cross the boundary. The default-deny stance is structurally distinct from runtime allowlisting because the credential never enters the server's process address space — no later check can be bypassed by a confused or malicious server.

## OAuth for Streamable HTTP Servers

For remote MCP servers over HTTP, the env field is not the right surface — tokens belong in a per-server credential store, not exported variables. Claude Code stores OAuth client secrets in the OS keychain or a credentials file, not in `.mcp.json`, and scopes a server's tokens to that server's identifier; the `oauth.scopes` field pins the requested scope set so a server cannot widen its authority beyond what the operator approved ([Claude Code MCP OAuth](https://code.claude.com/docs/en/mcp)). Codex CLI 0.134.0 adds the same posture for streamable HTTP servers ([Codex changelog](https://developers.openai.com/codex/changelog)). The credential never exists in env at all; it lives in a per-server keychain entry the agent retrieves on demand.

## Diagnostic Signal vs Silent Inheritance

A per-server scoping posture produces a useful failure mode: an MCP server that needs a credential the operator forgot to grant fails to authenticate, loudly, at startup. Under env inheritance, the same misconfiguration silently succeeds — the server picks up an unrelated credential from the ambient env and either fails confusingly downstream or, worse, authenticates as the wrong principal. Explicit grants convert silent credential misrouting into visible authentication errors.

## Why It Works

Process boundaries provide kernel-enforced isolation of address space, file descriptors, and the environment block passed at `execve(2)`. The MCP Python SDK's `stdio_client` constructs the spawned server's env from a parameter-supplied map merged with a default allowlist — not from `os.environ` directly ([python-sdk stdio](https://github.com/modelcontextprotocol/python-sdk)). An agent host that builds the env block per server cannot accidentally leak credentials that were never copied into that block. Even an LLM tricked by indirect prompt injection into asking the server to enumerate its environment sees only what the host granted. Default-deny at the env layer is structurally distinct from runtime checks because the secret never reaches the server process; this is the env-layer analogue of the structural argument in [Scoped Credentials via Proxy](scoped-credentials-proxy.md).

## When This Backfires

Per-server scoping has costs and limits:

- **Trusted single-tenant dev environments** with only operator-authored MCP servers running audited code — the configuration overhead is real and the attacker model is theoretical
- **Hosts that already isolate at a lower layer** — separate containers, separate user accounts, or `setresuid`-separated processes make env scoping redundant
- **Servers that need broad ambient access** — build tooling wrappers around `make`, `cargo`, `npm`, or language runtimes need many `LANG`, `LC_*`, `PYTHONPATH`, `NODE_OPTIONS`, `JAVA_HOME`, `CARGO_*` variables; enumerating each is operationally expensive
- **Residual env in the agent process itself** — env scoping protects servers, not the agent. If the agent's own process holds `STRIPE_KEY` and runs arbitrary Bash, an indirect injection that gets the agent to `printenv` bypasses every per-server grant. [Workload Identity Federation for Agent Runtimes](workload-identity-federation-for-agents.md) and [Scoped Credentials via Proxy](scoped-credentials-proxy.md) close that gap; env scoping is the configuration layer, not the structural one
- **Misconfigured grants** — pasting `env: ${env:GITHUB_TOKEN}` into one server's block and then copy-pasting into another server's block silently widens access. Treat the per-server env block as a security-relevant config artifact under review

The pattern is the cheapest hardening available because the mechanism exists in every host that supports stdio MCP servers — the question is whether the operator opts into default-deny or accepts the host's default. It is not a substitute for proxy-based credential isolation or federated identity; it is a complement that closes the configuration-layer path.

## Example

A team running an agent with three MCP servers — GitHub, Postgres, Stripe — using per-server env scoping in Claude Code's `.mcp.json`:

```json
{
  "mcpServers": {
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "postgres": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@bytebase/dbhub", "--dsn", "${DATABASE_URL}"],
      "env": {}
    },
    "stripe": {
      "type": "http",
      "url": "https://mcp.stripe.com",
      "oauth": {
        "scopes": "balance:read"
      }
    }
  }
}
```

The GitHub server sees only `GITHUB_PERSONAL_ACCESS_TOKEN`. The Postgres server sees an empty application-env block — its DSN is passed as a command argument, which is its own trade-off but at least keeps the credential out of `os.environ` for the spawned process. The Stripe server holds no env credential; OAuth-minted tokens with `balance:read` scope live in the OS keychain ([Claude Code MCP OAuth](https://code.claude.com/docs/en/mcp)). A prompt injection that tricks the GitHub server into enumerating its environment exfiltrates the GitHub PAT and nothing else.

## Key Takeaways

- Per-server MCP environment scoping bounds the credential blast radius of any single MCP server to what the operator explicitly granted it
- The MCP specification does not mandate env scoping — each host implementation decides; the reference Python SDK ships a hard-coded `DEFAULT_INHERITED_ENV_VARS` allowlist that does not include application secrets
- Claude Code, VS Code Copilot, and Codex CLI 0.134.0 all expose per-server `env` configuration; the question is whether your team opts into default-deny or accepts the host default
- OAuth options for streamable HTTP MCP servers keep credentials in a per-server keychain entry rather than env at all — the credential never reaches a spawnable env block
- Explicit per-server grants convert silent credential misrouting into visible authentication errors at startup — a diagnostic improvement on top of the security improvement
- The pattern is the configuration-layer complement to [Scoped Credentials via Proxy](scoped-credentials-proxy.md) and [Workload Identity Federation](workload-identity-federation-for-agents.md), not a substitute

## Related

- [Secrets Management for Agent Workflows](secrets-management-for-agents.md) — env-var injection into the agent process itself, the parent layer this pattern bounds
- [Scoped Credentials via Proxy Outside the Agent Sandbox](scoped-credentials-proxy.md) — the structural alternative when broad-scope credentials must never reach the agent process
- [Workload Identity Federation for Agent Runtimes](workload-identity-federation-for-agents.md) — removes long-lived API keys entirely, so even per-server env scoping has nothing high-blast-radius to protect
- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md) — env scoping is one tool for removing the private-data leg from an MCP server's execution path
- [Credential Hygiene for Agent Skill Authorship](credential-hygiene-agent-skills.md) — the authoring-time analogue: keep credentials out of skill files, the way per-server scoping keeps them out of server env blocks
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md) — the broader principle this pattern instantiates at the MCP config layer
- [MCP Server Design: Building Agent-Friendly Servers](../tool-engineering/mcp-server-design.md) — what an MCP server author can do; this page covers what the host operator can do
