---
title: "Per-Server MCP Environment Scoping for Credential Isolation"
term: "Per-Server MCP Environment Scoping"
description: "Spawn each MCP server with its own minimal environment scope so one server's credentials never leak to every other server the agent talks to."
tags:
  - security
  - tool-agnostic
  - mcp
last_reviewed: 2026-06-03
maturity: established
---

# Per-Server MCP Environment Scoping for Credential Isolation

> Spawn each MCP server with its own minimal environment scope so one server's credentials never leak to every other server.

Per-server MCP environment scoping is a configuration posture. The host spawns each MCP server with its own explicit, minimal environment block, not the agent host's full environment. A GitHub server sees `GITHUB_TOKEN`. A Postgres server sees `DATABASE_URL`. A Stripe server sees `STRIPE_KEY`. None sees the others, so a compromised or tricked server's blast radius stays bounded by what the operator granted.

## The default that leaks

Without per-server scoping, the host spawns each MCP server with `os.environ` as its env block, so every server can see every secret the operator exported into the agent's shell. A backdoored server with no business seeing a Stripe key can call `getenv("STRIPE_KEY")` and exfiltrate it through its own egress channel. This is the Unix default: `execve(2)` passes the calling process's `environ` unless the caller builds a fresh block.

The MCP specification does not mandate env scoping. The reference [MCP Python SDK's `stdio_client`](https://github.com/modelcontextprotocol/python-sdk) builds the spawned server's env from `StdioServerParameters.env` merged with a hard-coded allowlist (`HOME`, `PATH`, `SHELL`, `USER`, and a few platform variables), not application secrets. The SDK ships default-deny; whether a host preserves that is a host choice.

## How each host exposes the knob

Three hosts expose the configuration:

| Host | Surface | Scope shape |
|------|---------|-------------|
| Claude Code | `.mcp.json` per-server `env: {}` map; `claude mcp add --env KEY=value` | Explicit map per server; `${VAR}` and `${VAR:-default}` expansion ([Claude Code MCP](https://code.claude.com/docs/en/mcp)) |
| VS Code Copilot | `.vscode/mcp.json` per-server `env: {}` + `envFile` path; `${input:id}` references | Per-server map; `password: true` inputs securely stored for reuse ([VS Code MCP configuration](https://code.visualstudio.com/docs/copilot/reference/mcp-configuration)) |
| Codex CLI | `config.toml` per-server `mcp_servers.<name>.env` map | Explicit per-server env map, forwarded to the stdio server ([Codex config reference](https://learn.chatgpt.com/docs/config-file/config-reference)) |

In all three, the operator chooses which variables cross the boundary. Default-deny differs from runtime allowlisting because the credential never enters the server's process address space, so no confused or malicious server can bypass a later check.

## OAuth for streamable HTTP servers

For remote MCP servers over HTTP, the env field is not the right surface — tokens belong in a per-server credential store. Claude Code stores OAuth client secrets in the OS keychain or a credentials file, scoped to that server's identifier. The `oauth.scopes` field pins the requested scope when the upstream authorization server advertises more than the operator wants to grant ([Claude Code MCP OAuth](https://code.claude.com/docs/en/mcp)). Codex CLI 0.134.0 adds the same posture for streamable HTTP servers ([Codex changelog](https://developers.openai.com/codex/changelog)). The credential lives in a per-server keychain entry, never in env.

## Why it works

Process boundaries give kernel-enforced isolation of address space, file descriptors, and the environment block passed at `execve(2)`. A host that builds the env block per server cannot leak a credential it never copied into that block. The secret never reaches the server process, which is why default-deny beats a runtime check here. This is the env-layer version of the structural argument in [Scoped Credentials via Proxy](scoped-credentials-proxy.md).

The pattern also produces a useful failure mode. A server missing a granted credential fails to authenticate, loudly, at startup, instead of silently picking up an ambient credential and authenticating as the wrong principal. Explicit grants turn silent misrouting into a visible error.

## When this backfires

Costs and limits:

- Trusted single-tenant dev environments running only operator-authored, audited MCP servers: the configuration overhead is real and the attacker model is theoretical
- Hosts that already isolate lower down: separate containers, user accounts, or `setresuid`-separated processes make env scoping redundant
- Servers needing broad ambient access: `make`, `cargo`, or `npm` wrappers need many `LANG`, `PYTHONPATH`, `NODE_OPTIONS`, and `JAVA_HOME` variables, expensive to enumerate
- Residual env in the agent process itself: env scoping protects servers, not the agent. If the agent's own process holds `STRIPE_KEY` and runs arbitrary Bash, an indirect injection that triggers `printenv` bypasses every per-server grant. [Workload Identity Federation for Agent Runtimes](workload-identity-federation-for-agents.md) and [Scoped Credentials via Proxy](scoped-credentials-proxy.md) close that gap
- Misconfigured grants: pasting `env: ${env:GITHUB_TOKEN}` into one block, then copying it into another, silently widens access. Treat the env block as a security-relevant artifact under review

This pattern is the cheapest hardening available, because the mechanism exists in every host that supports stdio MCP servers. The question is whether the operator opts into default-deny or accepts the host's default. It complements proxy-based credential isolation and federated identity, closing the configuration-layer path.

## Example

A team running an agent with three MCP servers — GitHub, Postgres, Slack — using per-server env scoping in Claude Code's `.mcp.json`:

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
    "slack": {
      "type": "http",
      "url": "https://mcp.slack.com/mcp",
      "oauth": {
        "scopes": "channels:read chat:write search:read"
      }
    }
  }
}
```

The GitHub server sees only `GITHUB_PERSONAL_ACCESS_TOKEN`. The Postgres server sees an empty application-env block. Its DSN passes as a command argument instead, which is its own trade-off but at least keeps the credential out of `os.environ` for the spawned process. The Slack server holds no env credential. OAuth-minted tokens scoped to `channels:read chat:write search:read` live in the OS keychain ([Claude Code MCP OAuth](https://code.claude.com/docs/en/mcp)). A prompt injection that tricks the GitHub server into enumerating its environment exfiltrates the GitHub PAT and nothing else.

## Key Takeaways

- Per-server MCP environment scoping bounds the credential blast radius of any single MCP server to what the operator explicitly granted it
- The MCP specification does not mandate env scoping — each host implementation decides; the reference Python SDK ships a hard-coded `DEFAULT_INHERITED_ENV_VARS` allowlist that does not include application secrets
- Claude Code, VS Code Copilot, and Codex CLI all expose per-server `env` configuration; the question is whether your team opts into default-deny or accepts the host default
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
