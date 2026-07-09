---
title: "Scoped Credentials via Proxy Outside the Agent Sandbox"
description: "Keep broad credentials entirely outside the agent's sandbox and use an external proxy that attaches scoped tokens only to validated, allowlisted requests."
term: "Scoped Credentials Proxy"
tags:
  - agent-design
  - instructions
  - security
  - tool-agnostic
aliases:
  - Scoped Credentials Proxy
  - Secrets & Credentials
last_reviewed: 2026-06-12
maturity: established
---

# Scoped Credentials via Proxy Outside the Agent Sandbox

> Keep broad credentials entirely outside the agent's sandbox and use an external proxy that attaches scoped tokens only to validated, allowlisted requests.

Related lesson: [Keep the Keys Out](https://learn.agentpatterns.ai/security/keep-the-keys-out/) covers this concept in a hands-on lesson with quizzes.

!!! note "Also known as"
    Secrets & Credentials, Scoped Credentials Proxy. For broader secrets management, including environment variable injection and wrapper scripts, see [Secrets Management for Agent Workflows](secrets-management-for-agents.md).

## The risk of in-sandbox credentials

Any code the agent runs, or is tricked into running, can read credentials stored inside an agent sandbox — environment variables, config files, shell history. A [prompt injection](prompt-injection-threat-model.md) that makes the agent run `printenv` or read `~/.ssh/id_rsa` turns a confused agent into a credential exfiltration channel.

Every tool call, subprocess, and injected instruction can reach a credential file, even one with limited permissions. For this reason Anthropic's sandbox design keeps "sensitive credentials (such as git credentials or signing keys) never inside the sandbox with Claude Code". [[Source]](https://www.anthropic.com/engineering/claude-code-sandboxing)

## Proxy-based credential pattern

The proxy pattern moves credential storage outside the sandbox boundary. The agent sends unauthenticated requests. The proxy validates each one against an allowlist and attaches the scoped token before forwarding.

```
Agent (sandbox) → unauthenticated request → Proxy (external)
                                                 │
                                        Validates request content
                                        Attaches scoped token
                                                 │
                                                 ↓
                                         Upstream service
```

The agent never holds credentials. A compromised agent can only make requests the proxy permits — [blast-radius containment](blast-radius-containment.md) by construction. [[Source]](https://www.anthropic.com/engineering/claude-code-sandboxing)

## Scoping tokens to operations

Match the token scope to the narrowest operation the agent needs:

- A git token scoped to one repository (not the full account or org)
- A database connection role with `SELECT` only for read-heavy tasks
- An API key that can POST to one endpoint, not an admin key

This limits the blast radius: a misused token can only affect its scoped resource — least privilege applied to agent credentials. OWASP's AI Agent Security Cheat Sheet recommends the same pattern: "issue short-lived tokens that are narrowly scoped to a specific task" so an agent cannot reuse privileges across unrelated operations. [[Source]](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html)

## Request validation before token attachment

A proxy does more than route. It validates the request content before attaching auth. Useful checks:

- The target URL matches an allowlist
- The HTTP method is permitted (for example, reject DELETE on read-only tasks)
- The request body shows no signs of injection (for example, an unexpected payload shape)

This stops the agent from being tricked into sending an authenticated request to an attacker-controlled endpoint with its legitimate credentials attached. LangChain applies the same shape to outbound network traffic: its Auth Proxy mediates and scopes the egress of LangSmith agent sandboxes. [[Source]](https://blog.langchain.com/auth-proxy-langsmith-agent-sandboxes)

## Audit logging

The proxy layer logs all authenticated actions, including the full request and attached credential. This produces an audit trail independent of the agent's own logs or conversation history, which may be truncated or manipulated.

## Comparison with environment variable injection

Environment variable injection keeps secrets out of context but still places them inside the sandbox process. The proxy pattern fits when:

- The credential has significant blast radius (org-wide token, prod database)
- The agent processes untrusted external content (email, web pages, user uploads)
- Compliance or audit requirements mandate authenticated-action logging

For low-stakes dev tasks, environment variable injection is enough. See [Secrets Management for Agent Workflows](secrets-management-for-agents.md).

## Example

This example shows a minimal credential proxy that uses Caddy as the external proxy process. The agent makes unauthenticated requests to `localhost:2019`. Caddy validates the target URL against an allowlist and attaches the scoped GitHub token before forwarding.

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

## Why it works

The security guarantee comes from OS-level process isolation. The agent and the proxy run as separate OS processes with distinct address spaces. The agent cannot read another process's environment variables, open file descriptors, or memory — even under the same user account. Anthropic's Claude Code sandbox is "built on top of OS level primitives such as Linux bubblewrap and MacOS seatbelt to enforce these restrictions at the OS level," covering "any scripts, programs, or subprocesses that are spawned by the command." [[Source]](https://www.anthropic.com/engineering/claude-code-sandboxing) Placing credentials in the proxy's process environment puts them behind this kernel-enforced boundary.

## When this backfires

- Proxy is itself compromised: a supply chain attack on the proxy process (for example, Caddy or a misconfigured admin API) exposes all credentials. The proxy becomes a high-value target, so harden it accordingly.
- Allowlist is too permissive: a wildcard like `/repos/*` allows any org repo. A misconfigured allowlist gives false confidence while the blast radius stays the same.
- Single point of failure: if the proxy is unreachable, the agent cannot authenticate. Production deployments need health checks and restart policies.
- Latency overhead: every authenticated call adds a local network hop through the proxy, which doubles as an [egress-policy](agent-network-egress-policy.md) enforcement point. This is measurable for high-frequency tool use, so benchmark before adopting the pattern in latency-sensitive workflows.
- Operational complexity: one more process to deploy and secure. For low-blast-radius dev tasks, environment variable injection is simpler and enough.

## Key Takeaways

- Credentials inside the sandbox are reachable by any code the agent runs or is tricked into running
- An external proxy holds credentials and attaches them only to validated, allowlisted requests
- OS-level process isolation enforces the boundary — the agent process cannot read another process's environment
- Scope tokens to the minimum required operation — one repo, one endpoint, one role
- Proxy-level request validation prevents injection-driven misuse of legitimate credentials
- All authenticated actions are auditable at the proxy layer independent of the agent's own session logs

## Related

- [Secrets Management for Agent Workflows](secrets-management-for-agents.md)
- [Credential Hygiene for Agent Skill Authorship](credential-hygiene-agent-skills.md)
- [Protecting Sensitive Files from Agent Context](protecting-sensitive-files.md)
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md)
- [Dual-Boundary Sandboxing](dual-boundary-sandboxing.md)
- [Designing Agents to Resist Prompt Injection](prompt-injection-resistant-agent-design.md)
- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md)
- [Guarding Against URL-Based Data Exfiltration in Agentic Workflows](url-exfiltration-guard.md)
