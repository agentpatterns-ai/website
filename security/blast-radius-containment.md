---
title: "Blast Radius Containment: Least Privilege for AI Agents"
description: "Grant agents only the permissions their task requires — read-only for research, branch-scoped for code changes, no external write access by default."
aliases:
  - Permission Scoping
  - Least Privilege
tags:
  - agent-design
  - tool-agnostic
  - security
---

# Blast Radius Containment: Least Privilege for AI Agents

> Grant agents only the permissions their task requires — read-only for research, branch-scoped for code changes, no external write access by default.

!!! note "Also known as"
    **Permission Scoping** | **Least Privilege**

## The Principle

Every permission an agent does not need is an attack surface for hallucination-driven damage. A research agent with write access can corrupt files. A reviewer with merge access can close PRs it shouldn't. A draft writer with deploy access is one bad session away from a production incident.

The damage an agent can do is bounded by the permissions you grant it. This works because tool access is enforced at the runtime layer — the execution environment filters which tools are available before the model ever sees a request, so even a successfully injected prompt cannot invoke a restricted tool. Isolation is structural, not probabilistic.

## Permission Dimensions

Four dimensions to scope per agent:

**1. Tool access** — which tools the agent can invoke. A research agent needs Read but not Write or Bash. A formatter needs Write but not network tools. Tool access restrictions at the agent definition level are enforced by the runtime, not the model — a subagent's `tools` frontmatter field determines which tools the runtime makes available to it, regardless of what the model requests ([docs](https://code.claude.com/docs/en/sub-agents)).

Claude Code sub-agent frontmatter supports explicit tool lists ([docs](https://code.claude.com/docs/en/sub-agents)):
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

## Worktrees as Filesystem Containment

Worktrees provide hard isolation for file-writing agents — the agent operates in a separate working directory and cannot affect the main branch or other agents' workspaces. See [Worktree Isolation](../workflows/worktree-isolation.md).

## Reasoning by Analogy

Apply the same reasoning used in OAuth scopes and Unix file permissions: request only what the operation requires. [Source: [Prompt Injections](https://openai.com/index/prompt-injections/)]

## Auditing Permissions Before Deployment

Audit tools and data sources exposed to an agent before deployment. Questions:

- What is the broadest action this agent could take with its current permissions?
- If this agent were successfully injected, what is the worst-case outcome?
- Which permissions are present for convenience rather than necessity?

Remove any permission that cannot be justified by the task definition.

## Agent Decomposition as a Scoping Strategy

Rather than granting one agent broad permissions, decompose into separate agents with narrow scopes chained together. Each agent handles one operation and holds only the permissions for that operation.

This reduces the attack surface per agent: a successful injection against the research agent cannot trigger write operations that only the write agent holds. [Source: [Prompt Injections](https://openai.com/index/prompt-injections/)]

## When This Backfires

Narrow permission scopes impose a maintenance cost that grows with pipeline complexity:

- **Early-stage pipelines**: When a single developer is iterating rapidly on a single-user, local-only pipeline, per-agent YAML configuration adds friction with limited security gain — the blast radius is already low by environment.
- **Permission creep over time**: Agents granted narrow initial scopes often accumulate permissions incrementally as edge cases emerge. Without active audit, the YAML grows toward broad access anyway, providing false confidence.
- **Tool enumeration complexity**: In multi-agent chains with many tool categories, mapping each agent's exact required tools requires upfront analysis that teams skip under deadline pressure, leading to over-provisioned scopes as the path of least resistance.

Apply full scoping in production pipelines with external data access or write access to shared state. In sandboxed, ephemeral, or single-user environments, prioritize auditing permissions before deployment over maintaining minimal permission manifests.

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

- [Worktree Isolation](../workflows/worktree-isolation.md)
- [Rollback-First Design: Every Agent Action Should Be Reversible](../agent-design/rollback-first-design.md)
- [Human-in-the-Loop Placement: Where to Gate Agent Pipelines](../workflows/human-in-the-loop.md)
- [Scoped Credentials via Proxy Outside the Agent Sandbox](scoped-credentials-proxy.md)
- [Use Explicit, Narrow Task Instructions to Reduce Agent Susceptibility to Injection](task-scope-security-boundary.md)
- [Permission-Gated Custom Commands for AI Agent Development](permission-gated-commands.md)
- [Prompt Injection: A First-Class Threat to Agentic Systems](prompt-injection-threat-model.md)
- [Dual-Boundary Sandboxing](dual-boundary-sandboxing.md)
- [Defense-in-Depth Agent Safety](defense-in-depth-agent-safety.md)
- [Enterprise Agent Hardening: Governance, Observability, and Reproducibility](enterprise-agent-hardening.md)
- [Scope Sandbox Rules to Harness-Owned Tools, Not Third-Party MCP Tools](sandbox-rules-harness-tools.md)
- [Designing Agents to Resist Prompt Injection](prompt-injection-resistant-agent-design.md)
- [Confirmation Gates for Consequential Agent Actions](human-in-the-loop-confirmation-gates.md)
- [Protecting Sensitive Files from Agent Context Access](protecting-sensitive-files.md)
- [Safe Outputs Pattern for Trustworthy Agent Responses](safe-outputs-pattern.md)
- [Lethal Trifecta Threat Model for AI Agent Development](lethal-trifecta-threat-model.md)
- [Secrets Management for AI Agents: Credential Injection](secrets-management-for-agents.md)
- [Tool Signing and Signature Verification](tool-signing-verification.md)
- [Credential Hygiene for Agent Skill Authorship](credential-hygiene-agent-skills.md)
- [Tool-Invocation Attack Surface in Coding Agents](tool-invocation-attack-surface.md)
