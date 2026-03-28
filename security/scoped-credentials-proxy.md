---
title: "Scoped Credentials via Proxy Outside the Agent Sandbox"
description: "Keep broad credentials entirely outside the agent's sandbox and use an external proxy that attaches scoped tokens only to validated, allowlisted requests"
tags:
  - agent-design
  - instructions
  - security
aliases:
  - Scoped Credentials Proxy
  - Secrets & Credentials
---
# Scoped Credentials via Proxy Outside the Agent Sandbox

> Keep broad credentials entirely outside the agent's sandbox and use an external proxy that attaches scoped tokens only to validated, allowlisted requests.

!!! note "Also known as"
    Secrets & Credentials, Scoped Credentials Proxy. For the broader secrets management landscape including environment variable injection and wrapper scripts, see [Secrets Management for Agent Workflows](secrets-management-for-agents.md).

## The Risk of In-Sandbox Credentials

Credentials stored inside an agent sandbox — environment variables, config files, shell history — are accessible to any code the agent executes or is manipulated into executing. A [prompt injection](prompt-injection-threat-model.md) that causes the agent to run `printenv` or read `~/.ssh/id_rsa` immediately converts a confused agent into a credential exfiltration channel.

Giving an agent access to a credential file — even with limited permissions — still means every tool call, subprocess, and injected instruction has potential access to that credential [unverified — general security principle; the specific "just read access" scenario is not discussed in the cited source]. [Source: [Claude Code Sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing)]

## Proxy-Based Credential Pattern

The proxy pattern moves credential storage to a process outside the sandbox boundary. The agent sends unauthenticated requests; the proxy intercepts them, validates they match an allowlist, and attaches the appropriate scoped token before forwarding.

```
Agent (sandbox) → unauthenticated request → Proxy (external)
                                                 │
                                        Validates request content
                                        Attaches scoped token
                                                 │
                                                 ↓
                                         Upstream service
```

The agent never holds credentials. A compromised agent can only make requests the proxy permits. [Source: [Claude Code Sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing)]

## Scoping Tokens to Operations

Token scope should match the narrowest operation the agent needs:

- A git token scoped to one repository (not the full account or org)
- A database connection role with `SELECT` only for read-heavy tasks
- An API key that can POST to one endpoint, not an admin key

This limits the blast radius: even if a token is misused, it can only affect the specific resource it was scoped to [unverified — general least-privilege principle; token scoping strategy not discussed in the cited source].

## Request Validation Before Token Attachment

A proxy does more than route — it validates the request content before attaching auth. Useful checks:

- The target URL matches an allowlist
- The HTTP method is permitted (e.g., reject DELETE on read-only tasks)
- Request body does not contain signs of injection (e.g., unexpected payload shape)

This prevents the agent from being tricked into making an authenticated request to an attacker-controlled endpoint with the agent's legitimate credentials attached.

## Audit Logging

All authenticated actions the agent takes — including the full request and attaching credential — are logged at the proxy layer. This produces a complete audit trail independent of the agent's own logs or conversation history, which may be truncated or manipulated.

## Comparison with Environment Variable Injection

Environment variable injection (the simpler alternative) keeps secrets out of context but still places them inside the sandbox process. The proxy pattern is appropriate when:

- The credential has significant blast radius (org-wide token, prod database)
- The agent processes untrusted external content (email, web pages, user uploads)
- Compliance or audit requirements mandate authenticated-action logging

For low-stakes local dev tasks, environment variable injection is sufficient. See [Secrets Management for Agent Workflows](secrets-management-for-agents.md).

## Example

The following shows a minimal credential proxy using Caddy as the external proxy process. The agent makes unauthenticated requests to `localhost:2019`; Caddy validates the target URL against an allowlist and attaches the scoped GitHub token before forwarding.

```caddyfile
# Caddyfile — runs outside the agent sandbox
{
  admin off
}

:2019 {
  @allowed path /repos/my-org/my-repo/*

  handle @allowed {
    header Authorization "token {env.GITHUB_SCOPED_TOKEN}"
    reverse_proxy https://api.github.com {
      header_up Host api.github.com
    }
  }

  handle {
    respond "Request blocked: target not in allowlist" 403
  }
}
```

The agent sends requests without any credentials:

```bash
# Inside the agent sandbox — no token available here
curl http://localhost:2019/repos/my-org/my-repo/contents/src/main.py
```

The proxy attaches `Authorization: token <scoped-token>` only for `my-org/my-repo` paths, and blocks anything else with 403. The `GITHUB_SCOPED_TOKEN` environment variable is set in the proxy's process environment, never injected into the sandbox.

To further restrict the token, generate it with the minimum required scope using the GitHub CLI before starting the proxy:

```bash
# Outside the sandbox — use a pre-issued fine-grained PAT scoped to one repo, read-only
export GITHUB_SCOPED_TOKEN="ghp_your-fine-grained-pat-here"  # or retrieve from a secrets manager
caddy run --config Caddyfile
```

## Key Takeaways

- Credentials inside the sandbox are reachable by any code the agent runs or is tricked into running
- An external proxy holds credentials and attaches them only to validated, allowlisted requests
- Scope tokens to the minimum required operation — one repo, one endpoint, one role
- Proxy-level request validation prevents injection-driven misuse of legitimate credentials
- All authenticated actions are auditable at the proxy layer independent of the agent's own session logs

## Unverified Claims

- Giving an agent "just read access" to a credential file still means every tool call has potential access [unverified — general security principle; the specific "just read access" scenario is not discussed in the cited source]
- Token scoping limits blast radius to the specific resource [unverified — general least-privilege principle; token scoping strategy not discussed in the cited source]

## Related

- [Secrets Management for Agent Workflows](secrets-management-for-agents.md)
- [Protecting Sensitive Files from Agent Context](protecting-sensitive-files.md)
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md)
- [Dual-Boundary Sandboxing](dual-boundary-sandboxing.md)
- [Designing Agents to Resist Prompt Injection](prompt-injection-resistant-agent-design.md)
- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md)
- [Enterprise Agent Hardening](enterprise-agent-hardening.md)
- [Defense-in-Depth Agent Safety](defense-in-depth-agent-safety.md)
- [Treat Task Scope as a Security Boundary](task-scope-security-boundary.md)
- [Scope Sandbox Rules to Harness-Owned Tools](sandbox-rules-harness-tools.md)
- [Guarding Against URL-Based Data Exfiltration in Agentic Workflows](url-exfiltration-guard.md)
- [Safe Outputs Pattern](safe-outputs-pattern.md)
- [Tool Signing and Signature Verification](tool-signing-verification.md)
- [Permission-Gated Custom Commands](permission-gated-commands.md)
- [Code Injection Defence in Multi-Agent Pipelines](code-injection-multi-agent-defence.md)
- [Human-in-the-Loop Confirmation Gates for Consequential Agent Actions](human-in-the-loop-confirmation-gates.md)
- [PII Tokenization in Agent Context](pii-tokenization-in-agent-context.md)
- [Close the Attack-to-Fix Loop](close-attack-to-fix-loop.md)
