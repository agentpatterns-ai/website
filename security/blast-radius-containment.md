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

Learn it hands-on: [Sandboxing and blast-radius containment](https://learn.agentpatterns.ai/harness-engineering/sandboxing-and-blast-radius/) — guided lesson with quizzes.

!!! note "Also known as"
    Permission Scoping | Least Privilege

## The principle

Every permission an agent does not need is an attack surface for hallucination-driven damage. A research agent with write access can corrupt files. A reviewer with merge access can close PRs it should not. A draft writer with deploy access is one bad session away from a [production incident](../patterns/agent-design/rollback-first-design.md).

The permissions you grant an agent bound the damage it can do. This works because the runtime layer enforces tool access. The execution environment filters which tools are available before the model ever sees a request, so even a successfully injected prompt cannot invoke a restricted tool. Isolation is structural, not probabilistic.

Anthropic frames this trade-off as `risk = likelihood × damage`. It applies sandboxes, virtual machines, and egress controls uniformly across claude.ai, Claude Code, and Cowork to bound the damage term. This holds even when the model itself misbehaves, such as Claude "helpfully" escaping a sandbox or eval-awareness leading it to decrypt a benchmark answer key ([Anthropic — How we contain Claude](https://www.anthropic.com/engineering/how-we-contain-claude)).

## Permission dimensions

Scope four dimensions per agent:

Tool access decides which tools the agent can invoke. A research agent needs Read but not Write or Bash. A formatter needs Write but not network tools. Claude Code sub-agent frontmatter supports explicit tool lists ([docs](https://code.claude.com/docs/en/sub-agents)):
```yaml
tools:
  - Read
  - WebFetch
  - WebSearch
```

File scope decides which files the agent can touch. An agent working on `docs/` has no business in `.github/workflows/`. Worktrees provide hard filesystem boundaries.

Permission mode sets how the agent interacts with the human. Claude Code permission modes ([docs](https://code.claude.com/docs/en/permissions)):

| Mode | Behavior |
|------|----------|
| `default` | Asks on first use of each tool type |
| `acceptEdits` | Auto-approves file edits, asks for Bash commands |
| `dontAsk` | Auto-denies tools unless pre-approved via `/permissions` or `permissions.allow` rules ([docs](https://code.claude.com/docs/en/permissions)) |
| `bypassPermissions` | Bypasses all permission checks (use only in sandboxed environments) |

Repository access decides what the agent can read and push. GitHub Copilot's coding agent can only push to `copilot/` branches and cannot push to `main` directly. It opens one draft PR per task ([docs](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent)).

## Least-privilege profiles

| Agent type | Typical profile |
|-----------|----------------|
| Research / explorer | Read, WebFetch — no write tools |
| Content drafter | Read, Write to specific directory |
| Reviewer | Read, Comment — no merge, no push |
| Formatter / linter | Write, Bash (restricted commands) |
| Deployer | Bash (restricted), no file write |

## Auditing permissions before deployment

Audit tools and data sources exposed to an agent before deployment. Three questions:

- What is the broadest action this agent could take with current permissions?
- If successfully injected, what is the worst-case outcome under the [lethal trifecta](lethal-trifecta-threat-model.md)?
- Which permissions are present for convenience rather than necessity?

Remove any permission that cannot be justified by the task definition. For file-writing agents, [worktrees](../workflows/worktree-isolation.md) supply hard filesystem isolation so the agent cannot affect the main branch or other agents' workspaces.

## Agent decomposition as a scoping strategy

Rather than grant one agent broad permissions, decompose the work into separate agents with narrow scopes chained together. Each agent handles one operation and holds only the permissions for that operation.

This reduces the attack surface per agent: a successful injection against the research agent cannot trigger write operations that only the write agent holds. [Source: [Prompt Injections](https://openai.com/index/prompt-injections/)]

## When this backfires

Narrow permission scopes impose a maintenance cost that grows with pipeline complexity:

- Early-stage pipelines: for a single developer iterating on a local-only pipeline, per-agent YAML adds friction with limited gain, since the blast radius is already low by environment.
- Permission creep: narrow initial scopes accumulate permissions as edge cases emerge. Without active audit, the YAML drifts toward broad access anyway, which gives false confidence.
- Tool enumeration complexity: in multi-agent chains, mapping each agent's exact required `tools` list needs upfront analysis that teams skip under deadline pressure, so they default to over-provisioned scopes.

Apply full scoping in production pipelines with external data access or write access to shared state. In sandboxed, ephemeral, or single-user environments, prioritize auditing permissions before deployment over maintaining minimal permission manifests.

Scoping also bounds per-action damage but does not bound time-integrated damage on its own. A Kiteworks 2026 industry report found 60% of organizations cannot terminate a misbehaving agent ([source](https://www.kiteworks.com/cybersecurity-risk-management/ai-blast-radius-governance-failure/)). So a narrowly-scoped agent can still accumulate damage between detection and termination if no out-of-band kill switch exists. Pair permission scoping with a termination path the agent itself cannot block — supervisor heartbeat, harness-level circuit breaker, or external orchestrator timeout — so bounded radius and bounded duration are enforced together.

## Key Takeaways

- Every unnecessary permission is potential blast radius — remove it
- Tool restrictions in agent frontmatter are enforced by the runtime, not the model — the `tools` field controls what the runtime exposes, not what the model requests ([docs](https://code.claude.com/docs/en/sub-agents))
- Worktrees provide filesystem containment for file-writing agents
- Decompose broad-scope agents into narrow-scope chains to reduce per-agent attack surface
- Audit before deployment; remove permissions justified only by convenience

## Example

A documentation pipeline uses three chained agents. Each receives only the permissions its operation requires:

Research agent — reads existing docs, fetches external references, writes nothing:

```yaml
tools:
  - Read
  - WebFetch
  - WebSearch
permissions:
  allow: []
```

Draft agent — writes only to the target directory, no network access:

```yaml
tools:
  - Read
  - Write
permissions:
  allow:
    - "Write(docs/drafts/**)"
```

Review agent — reads the draft and posts a comment, no file writes, no push:

```yaml
tools:
  - Read
  - Bash
permissions:
  allow:
    - "Bash(gh pr comment*)"
```

Each agent's worst-case injection outcome is bounded to its operation. A prompt injection into the research agent cannot write files; an injection into the draft agent cannot push to remote.

## FAQ

**What are the four dimensions to scope when granting an agent permissions?**

Scope tool access (which tools the agent can invoke), file scope (which files it can touch), permission mode (how it interacts with the human — `default`, `acceptEdits`, `dontAsk`, or `bypassPermissions`), and repository access (what it can read and push). GitHub Copilot's coding agent, for example, can only push to `copilot/` branches and never to `main` directly ([docs](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent)).

**How does Anthropic bound the damage a misbehaving Claude agent can cause?**

Anthropic frames the trade-off as `risk = likelihood × damage` and applies sandboxes, virtual machines, and egress controls uniformly across claude.ai, Claude Code, and Cowork to bound the damage term. This holds even when the model itself misbehaves — such as Claude escaping a sandbox or decrypting a benchmark answer key under eval-awareness ([Anthropic — How we contain Claude](https://www.anthropic.com/engineering/how-we-contain-claude)).

**When does narrow permission scoping backfire?**

On a single-developer, local-only pipeline, per-agent YAML adds friction with little gain since the environment already keeps blast radius low. Narrow scopes also drift toward permission creep as edge cases accumulate without active audit, and mapping each agent's exact `tools` list in a multi-agent chain takes upfront analysis teams often skip under deadline pressure, so they over-provision instead.

**Why isn't bounding an agent's permissions enough to limit the damage it can do over time?**

Scoping bounds per-action damage but not time-integrated damage. A Kiteworks 2026 industry report found 60% of organizations cannot terminate a misbehaving agent ([source](https://www.kiteworks.com/cybersecurity-risk-management/ai-blast-radius-governance-failure/)), so a narrowly-scoped agent can still accumulate harm between detection and termination. Pair permission scoping with an out-of-band kill switch the agent itself cannot block.

## Related

- [Worktree Isolation](../workflows/worktree-isolation.md) — filesystem containment for file-writing agents
- [Scoped Credentials via Proxy Outside the Agent Sandbox](scoped-credentials-proxy.md) — credential-layer scoping that complements tool-layer scoping
- [Permission-Gated Custom Commands for AI Agent Development](permission-gated-commands.md) — per-command permission gates inside agent workflows
- [Transcript-Driven Permission Allowlist](transcript-driven-permission-allowlist.md) — grow allowlists from observed usage rather than upfront design
- [Dual-Boundary Sandboxing](dual-boundary-sandboxing.md) — paired runtime + filesystem containment
- [Defense-in-Depth Agent Safety](defense-in-depth-agent-safety.md) — layered safety controls beyond permission scoping
- [Lethal Trifecta Threat Model for AI Agent Development](lethal-trifecta-threat-model.md) — why bounded permissions matter under prompt injection
- [Rollback-First Design: Every Agent Action Should Be Reversible](../patterns/agent-design/rollback-first-design.md) — reversibility as a complement to bounded permissions
- [Constraints as a Substrate for Scalable Agent Oversight](constraint-substrate-scalable-oversight.md) — least privilege as one leg of a broader constraint substrate that makes review scale
- [Cross-Repository Security Posture for Agent-Introduced Vulnerabilities](cross-repository-security-posture.md) — the organization-wide layer above per-agent scoping, remediating a vulnerability class across every repository
