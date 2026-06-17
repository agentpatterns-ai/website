---
title: "Blast Radius Containment: Least Privilege for AI Agents"
term: "Blast Radius Containment"
description: "Grant agents only the permissions their task requires — read-only for research, branch-scoped for code changes, no external write access by default."
aliases:
  - Permission Scoping
  - Least Privilege
tags:
  - agent-design
  - tool-agnostic
  - security
last_reviewed: 2026-06-17
maturity: adopted
---

# Blast Radius Containment: Least Privilege for AI Agents

> Grant agents only the permissions their task requires — read-only for research, branch-scoped for code changes, no external write access by default.

!!! note "Also known as"
    **Permission Scoping** | **Least Privilege**

## The Principle

Every permission an agent does not need is an attack surface for hallucination-driven damage. A research agent with write access can corrupt files. A reviewer with merge access can close PRs it shouldn't. A draft writer with deploy access is one bad session away from a [production incident](../agent-design/rollback-first-design.md).

The damage an agent can do is bounded by the permissions you grant it. This works because tool access is enforced at the runtime layer — the execution environment filters which tools are available before the model ever sees a request, so even a successfully injected prompt cannot invoke a restricted tool. Isolation is structural, not probabilistic.

Anthropic frames this trade-off as `risk = likelihood × damage` and applies sandboxes, virtual machines, and egress controls uniformly across claude.ai, Claude Code, and Cowork to bound the damage term — including against cases where the model itself misbehaves, such as Claude "helpfully" escaping a sandbox or eval-awareness leading it to decrypt a benchmark answer key ([Anthropic — How we contain Claude](https://www.anthropic.com/engineering/how-we-contain-claude)).

## Permission Dimensions

Four dimensions to scope per agent:

**1. Tool access** — which tools the agent can invoke. A research agent needs Read but not Write or Bash. A formatter needs Write but not network tools. Claude Code sub-agent frontmatter supports explicit tool lists ([docs](https://code.claude.com/docs/en/sub-agents)):
```yaml
tools:
  - Read
  - WebFetch
  - WebSearch
```

**2. File scope** — which files the agent can touch. An agent working on `docs/` has no business in `.github/workflows/`. Worktrees provide hard filesystem boundaries.

**3. Permission mode** — the human interaction model. Claude Code permission modes ([docs](https://code.claude.com/docs/en/permissions)):

| Mode | Behavior |
|------|----------|
| `default` | Asks on first use of each tool type |
| `acceptEdits` | Auto-approves file edits, asks for Bash commands |
| `dontAsk` | Auto-denies tools unless pre-approved via `/permissions` or `permissions.allow` rules ([docs](https://code.claude.com/docs/en/permissions)) |
| `bypassPermissions` | Bypasses all permission checks (use only in sandboxed environments) |

**4. Repository access** — what the agent can read and push. GitHub Copilot's coding agent can only push to `copilot/` branches and cannot push to `main` directly — it opens one draft PR per task ([docs](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent)).

## Least-Privilege Profiles

| Agent Type | Typical Profile |
|-----------|----------------|
| Research / explorer | Read, WebFetch — no write tools |
| Content drafter | Read, Write to specific directory |
| Reviewer | Read, Comment — no merge, no push |
| Formatter / linter | Write, Bash (restricted commands) |
| Deployer | Bash (restricted), no file write |

## Auditing Permissions Before Deployment

Audit tools and data sources exposed to an agent before deployment. Three questions:

- What is the broadest action this agent could take with current permissions?
- If successfully injected, what is the worst-case outcome under the [lethal trifecta](lethal-trifecta-threat-model.md)?
- Which permissions are present for convenience rather than necessity?

Remove any permission that cannot be justified by the task definition. For file-writing agents, [worktrees](../workflows/worktree-isolation.md) supply hard filesystem isolation so the agent cannot affect the main branch or other agents' workspaces.

## Agent Decomposition as a Scoping Strategy

Rather than granting one agent broad permissions, decompose into separate agents with narrow scopes chained together. Each agent handles one operation and holds only the permissions for that operation.

This reduces the attack surface per agent: a successful injection against the research agent cannot trigger write operations that only the write agent holds. [Source: [Prompt Injections](https://openai.com/index/prompt-injections/)]

## When This Backfires

Narrow permission scopes impose a maintenance cost that grows with pipeline complexity:

- **Early-stage pipelines**: For a single developer iterating on a local-only pipeline, per-agent YAML adds friction with limited gain — the blast radius is already low by environment.
- **Permission creep**: Narrow initial scopes accumulate permissions as edge cases emerge. Without active audit, the YAML drifts toward broad access anyway, providing false confidence.
- **Tool enumeration complexity**: In multi-agent chains, mapping each agent's exact required `tools` list requires upfront analysis that teams skip under deadline pressure, defaulting to over-provisioned scopes.

Apply full scoping in production pipelines with external data access or write access to shared state. In sandboxed, ephemeral, or single-user environments, prioritize auditing permissions before deployment over maintaining minimal permission manifests.

Scoping also bounds *per-action* damage but does not bound *time-integrated* damage on its own. A Kiteworks 2026 industry report found 60% of organizations cannot terminate a misbehaving agent ([source](https://www.kiteworks.com/cybersecurity-risk-management/ai-blast-radius-governance-failure/)), meaning a narrowly-scoped agent can still accumulate damage between detection and termination if no out-of-band kill switch exists. Pair permission scoping with a termination path the agent itself cannot block — supervisor heartbeat, harness-level circuit breaker, or external orchestrator timeout — so bounded radius and bounded duration are enforced together.

## Key Takeaways

- Every unnecessary permission is potential blast radius — remove it
- Tool restrictions in agent frontmatter are enforced by the runtime, not the model — the `tools` field controls what the runtime exposes, not what the model requests ([docs](https://code.claude.com/docs/en/sub-agents))
- Worktrees provide filesystem containment for file-writing agents
- Decompose broad-scope agents into narrow-scope chains to reduce per-agent attack surface
- Audit before deployment; remove permissions justified only by convenience

## Example

A documentation pipeline uses three chained agents. Each receives only the permissions its operation requires:

**Research agent** — reads existing docs, fetches external references, writes nothing:

```yaml
tools:
  - Read
  - WebFetch
  - WebSearch
permissions:
  allow: []
```

**Draft agent** — writes only to the target directory, no network access:

```yaml
tools:
  - Read
  - Write
permissions:
  allow:
    - "Write(docs/drafts/**)"
```

**Review agent** — reads the draft and posts a comment, no file writes, no push:

```yaml
tools:
  - Read
  - Bash
permissions:
  allow:
    - "Bash(gh pr comment*)"
```

Each agent's worst-case injection outcome is bounded to its operation. A prompt injection into the research agent cannot write files; an injection into the draft agent cannot push to remote.

## Related

- [Worktree Isolation](../workflows/worktree-isolation.md) — filesystem containment for file-writing agents
- [Scoped Credentials via Proxy Outside the Agent Sandbox](scoped-credentials-proxy.md) — credential-layer scoping that complements tool-layer scoping
- [Permission-Gated Custom Commands for AI Agent Development](permission-gated-commands.md) — per-command permission gates inside agent workflows
- [Transcript-Driven Permission Allowlist](transcript-driven-permission-allowlist.md) — grow allowlists from observed usage rather than upfront design
- [Dual-Boundary Sandboxing](dual-boundary-sandboxing.md) — paired runtime + filesystem containment
- [Defense-in-Depth Agent Safety](defense-in-depth-agent-safety.md) — layered safety controls beyond permission scoping
- [Lethal Trifecta Threat Model for AI Agent Development](lethal-trifecta-threat-model.md) — why bounded permissions matter under prompt injection
- [Rollback-First Design: Every Agent Action Should Be Reversible](../agent-design/rollback-first-design.md) — reversibility as a complement to bounded permissions
