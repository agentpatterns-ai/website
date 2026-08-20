---
title: "Copilot Memory and Cross-Agent Persistence"
description: "Persistent memory that Copilot builds from agent and editor sessions without manual curation, holding repository-level facts and user-level preferences across an open list of surfaces that now includes JetBrains IDEs."
tags:
  - context-engineering
  - agent-design
  - memory
  - copilot
  - long-form
aliases:
  - Agentic Memory
  - Copilot Agentic Memory
applies_to: "copilot@1.x"
last_reviewed: 2026-08-12
status: current
---

# Copilot Memory and Cross-Agent Persistence

> Persistent memory that Copilot builds from agent and editor sessions without manual curation, shared across surfaces with citation-based verification and 28-day auto-expiry.

## How Copilot Memory works

Copilot Memory captures knowledge from agent interactions without manual curation. Agents identify patterns worth remembering and store them as structured entries ([GitHub engineering blog](https://github.blog/ai-and-ml/github-copilot/building-an-agentic-memory-system-for-github-copilot/)).

Each entry contains four components ([GitHub engineering blog](https://github.blog/ai-and-ml/github-copilot/building-an-agentic-memory-system-for-github-copilot/)):

| Component | Purpose |
|-----------|---------|
| Subject | Topic identification |
| Fact | The learned knowledge |
| Citations | Specific code locations (file paths + line numbers) |
| Reason | Actionable implications for future tasks |

The pool holds two kinds of entry, and they carry different scopes. A repository-level fact is "visible to all contributors on the repository"; a user-level preference is "visible only to you, used in your sessions across repositories" ([GitHub changelog, May 2026](https://github.blog/changelog/2026-05-26-copilot-memory-has-more-controls-for-deletion-scope-and-the-copilot-cli/)). Preferences capture "communication style, tool stack, or git conventions", and Business and Enterprise plans gained them in June 2026 ([GitHub changelog, Jun 2026](https://github.blog/changelog/2026-06-02-copilot-memory-supports-user-preferences-for-business-enterprise)). Repository-level facts follow the original access model: write access to create, read access to use ([GitHub engineering blog](https://github.blog/ai-and-ml/github-copilot/building-an-agentic-memory-system-for-github-copilot/)).

## Which surfaces share the pool

GitHub describes Copilot Memory as "shared across multiple GitHub Copilot surfaces, including Copilot cloud agent, Copilot code review, and Copilot CLI" ([VS Code docs](https://code.visualstudio.com/docs/copilot/agents/memory)). The word is "including": read any count as a snapshot.

| Surface | How it participates |
|---|---|
| Coding agent | Reads and writes memories during code generation |
| Code review | Reads and writes memories during PR review |
| CLI | Reads and writes memories during terminal interactions |
| VS Code | Repository-scope memory moves into the shared pool once you enable Copilot Memory |
| JetBrains IDEs | From August 11, 2026, memory "can now retain and recall useful information across agent chat sessions", governed by the Copilot Memory toggle in the Copilot settings portal |

Sources: [GitHub engineering blog](https://github.blog/ai-and-ml/github-copilot/building-an-agentic-memory-system-for-github-copilot/) for coding agent, code review, and CLI; [VS Code docs](https://code.visualstudio.com/docs/copilot/agents/memory) for VS Code; [GitHub changelog, Aug 2026](https://github.blog/changelog/2026-08-11-copilot-memory-and-ollama-in-github-copilot-for-jetbrains/) for JetBrains

When code review discovers a naming convention violation, that knowledge becomes available to the coding agent on the next task ([GitHub engineering blog](https://github.blog/ai-and-ml/github-copilot/building-an-agentic-memory-system-for-github-copilot/)).

## What an editor surface adds

An editor contributes only part of what it remembers. VS Code splits memory into three scopes ([VS Code docs](https://code.visualstudio.com/docs/copilot/agents/memory)):

| Scope | Persistence | Default storage |
|---|---|---|
| User | Across all workspaces and conversations; the first 200 lines load into context at the start of every session | Local |
| Repository | Across conversations in the current workspace | Local, until you enable Copilot Memory |
| Session | Cleared when the conversation ends | Local |

"When you enable Copilot Memory, repository memory is stored in Copilot Memory instead, so it's shared across Copilot surfaces" ([VS Code docs](https://code.visualstudio.com/docs/copilot/agents/memory)). User and session memory stay on your machine.

The mechanism is unchanged. What changes is where entries come from: the three original surfaces write from autonomous agent runs, and an editor writes from a human-driven conversation. No one curates the content either way. The capture itself is consented. A permission prompt states which of the two scopes above an entry will land in before it is stored ([GitHub changelog, May 2026](https://github.blog/changelog/2026-05-26-copilot-memory-has-more-controls-for-deletion-scope-and-the-copilot-cli/)).

JetBrains is documented more thinly. Its changelog says nothing about scopes, expiry, or citation verification on that surface ([GitHub changelog, Aug 2026](https://github.blog/changelog/2026-08-11-copilot-memory-and-ollama-in-github-copilot-for-jetbrains/)), so treat the VS Code scope model as a guide to editor behavior rather than a specification of it.

## Citation-based verification and self-healing

Every entry is grounded in specific code locations. Before applying a memory, the agent performs just-in-time verification — checking that cited locations still exist and align with the stored fact ([GitHub engineering blog](https://github.blog/ai-and-ml/github-copilot/building-an-agentic-memory-system-for-github-copilot/)).

When verification reveals a contradiction, the agent generates a corrected version. GitHub tested this by seeding adversarial memories — agents consistently detected and corrected the conflicts ([GitHub engineering blog](https://github.blog/ai-and-ml/github-copilot/building-an-agentic-memory-system-for-github-copilot/)). The memory pool self-corrects through use rather than manual curation.

## Auto-expiry

Memories expire after 28 days. Use refreshes the timestamp, so actively relevant memories persist while unused entries are pruned ([GitHub changelog, Jan 2026](https://github.blog/changelog/2026-01-15-agentic-memory-for-github-copilot-is-in-public-preview/)). By contrast, Claude Code's auto memory persists without built-in expiry ([Claude Code docs](https://code.claude.com/docs/en/memory)).

## Measured impact

Internal evaluation results ([GitHub engineering blog](https://github.blog/ai-and-ml/github-copilot/building-an-agentic-memory-system-for-github-copilot/)):

| Surface | Metric | With Memory | Without Memory |
|---------|--------|-------------|----------------|
| Coding agent | PR merge rate | 90% | 83% |
| Code review | Positive feedback rate | 77% | 75% |

Both results were statistically significant (p < 0.00001).

## Availability and controls

| Date | Change | Source |
|------|--------|--------|
| Jan 15, 2026 | Public preview, opt-in for all paid plans | [GitHub changelog](https://github.blog/changelog/2026-01-15-agentic-memory-for-github-copilot-is-in-public-preview/) |
| Mar 4, 2026 | Enabled by default for Pro and Pro+ individual users | [GitHub changelog](https://github.blog/changelog/2026-03-04-copilot-memory-now-on-by-default-for-pro-and-pro-users-in-public-preview/) |
| May 26, 2026 | Repository-level off switch, preference-versus-fact permission prompt, `/memory` commands in the CLI | [GitHub changelog](https://github.blog/changelog/2026-05-26-copilot-memory-has-more-controls-for-deletion-scope-and-the-copilot-cli/) |
| Jun 2, 2026 | User preferences supported for Business and Enterprise plans | [GitHub changelog](https://github.blog/changelog/2026-06-02-copilot-memory-supports-user-preferences-for-business-enterprise) |
| Aug 11, 2026 | Memory reaches GitHub Copilot for JetBrains IDEs | [GitHub changelog](https://github.blog/changelog/2026-08-11-copilot-memory-and-ollama-in-github-copilot-for-jetbrains/) |

Developer controls:

- Individual toggle: `github.com/settings/copilot` > Features > Copilot Memory ([GitHub changelog](https://github.blog/changelog/2026-03-04-copilot-memory-now-on-by-default-for-pro-and-pro-users-in-public-preview/))
- Repository owners: Repository Settings > Copilot > Memory — review and delete stored memories one at a time, with each entry's citations shown ([GitHub changelog](https://github.blog/changelog/2026-01-15-agentic-memory-for-github-copilot-is-in-public-preview/))
- Repository admins: disable Copilot Memory for the whole repository through the existing Copilot feature controls. Repository-level facts stop being stored or read, and facts already stored remain ([GitHub changelog](https://github.blog/changelog/2026-05-26-copilot-memory-has-more-controls-for-deletion-scope-and-the-copilot-cli/))
- Copilot CLI users: `/memory on`, `/memory off`, and `/memory show`, persisting across sessions ([GitHub changelog](https://github.blog/changelog/2026-05-26-copilot-memory-has-more-controls-for-deletion-scope-and-the-copilot-cli/))
- Organization/enterprise admins: policy-level enable/disable ([GitHub changelog](https://github.blog/changelog/2026-03-04-copilot-memory-now-on-by-default-for-pro-and-pro-users-in-public-preview/))

Sources conflict on the default state: the March changelog records memory on by default for Pro and Pro+ ([GitHub changelog](https://github.blog/changelog/2026-03-04-copilot-memory-now-on-by-default-for-pro-and-pro-users-in-public-preview/)), while VS Code's documentation calls it "turned off by default and must be enabled" ([VS Code docs](https://code.visualstudio.com/docs/copilot/agents/memory)). Check your own toggle.

## Comparison with other memory approaches

| Dimension | Copilot Memory | Claude Code Memory | OPENDEV (Research) |
|-----------|---------------|-------------------|-------------------|
| Creation | Autonomous from interactions | Human-authored (`CLAUDE.md`) + agent-authored (auto memory) | Agent-authored [episodic summaries](../../patterns/agent-design/episodic-memory-retrieval.md) |
| Scope | Repository-level facts plus cross-repository user preferences | Project, user, managed policy | Session + cross-session |
| Sharing | Cross-surface (agents, review, CLI, editors) | Single tool only | Single agent only |
| Verification | Citation-based, just-in-time | None (manual curation) | None |
| Expiry | 28-day TTL with use-based renewal | None (manual cleanup) | N/A (research system) |
| Self-healing | Contradiction detection | No | No |

Sources: [GitHub engineering blog](https://github.blog/ai-and-ml/github-copilot/building-an-agentic-memory-system-for-github-copilot/), [Claude Code docs](https://code.claude.com/docs/en/memory), [Bui 2025](https://arxiv.org/abs/2603.05344)

## Example

Suppose a code review agent finds that your repository's service layer always injects dependencies through the constructor rather than using a service locator. The agent stores a memory entry like:

```
Subject: Dependency injection pattern
Fact: All service classes in src/services/ use constructor injection; service locator pattern is never used
Citations: src/services/UserService.ts:12, src/services/OrderService.ts:8
Reason: When generating new service classes, always use constructor injection and add dependencies to the constructor signature
```

The next time the coding agent adds a `NotificationService`, it reads this memory, applies constructor injection, and avoids a code review failure without being told the convention.

If a refactor moves `UserService.ts`, the citation goes stale. The agent's next access checks whether the cited line still shows constructor injection, then updates the citation if the pattern held or marks the memory contradicted if it did not.

## Key Takeaways

- Cross-surface sharing is the distinguishing feature. GitHub publishes the participant list with "including", so check `last_reviewed` on any page that enumerates it, this one included.
- An editor contributes only its repository scope. Auditing what a team has published means auditing repository-level facts, the only entries visible to every contributor, not the user or session memory sitting on each machine.
- Citation-based just-in-time verification prevents stale memories from degrading agent behavior.
- 28-day auto-expiry with use-based renewal balances freshness against unbounded growth.
- Measured impact: 7% increase in PR merge rates for the coding agent (p < 0.00001).

## When this backfires

Autonomous memory creation without human curation works against you in several conditions:

- Security-sensitive repositories: an incorrectly stored memory (for example, "always skip validation for internal services") can propagate to the coding agent and be applied silently, bypassing code review for the violation that created the false memory.
- Repositories with contested conventions: during a mid-refactor, agents may store memories from the old convention and resist the new one, creating a feedback loop where stale patterns self-reinforce until the memory expires.
- Teams using explicit context files: organizations that treat `.github/copilot-instructions.md` as the source of truth may find autonomous memories create ambiguity when the two diverge — the instruction file takes precedence, but the agent may still surface the contradicting memory.
- Multi-repository workflows: repository-level facts do not transfer across repos, so teams spanning a monorepo split or separate service repos must rebuild them in each context. Only user-level preferences follow you.
- Repositories where contributors and agents carry different trust: a repository-level fact is visible to every contributor ([GitHub changelog, May 2026](https://github.blog/changelog/2026-05-26-copilot-memory-has-more-controls-for-deletion-scope-and-the-copilot-cli/)), and an editor surface lets one originate in an interactive chat rather than an audited agent run.
- Teams that enable the feature account-wide without auditing editor scopes. Switching it on moves repository memory out of local storage and into the shared pool ([VS Code docs](https://code.visualstudio.com/docs/copilot/agents/memory)), publishing workspace notes a developer assumed were private.

## Related

- [Agent Memory Patterns](../../patterns/agent-design/agent-memory-patterns.md)
- [Context Priming](../../context-engineering/context-priming.md)
- [Layered Context Architecture](../../context-engineering/layered-context-architecture.md)
- [Copilot Instructions Convention](copilot-instructions-md-convention.md)
- [Copilot Coding Agent](coding-agent.md)
- [Copilot Agent Mode](agent-mode.md)
- [Unified Sessions View](unified-sessions-view.md)
- [Copilot CLI Agentic Workflows](copilot-cli-agentic-workflows.md)
