---
title: "Copilot Memory: Autonomous Cross-Agent Persistence"
description: "Repository-scoped persistent memory that Copilot builds autonomously from agent interactions, shared across coding agent, code review, and CLI."
tags:
  - context-engineering
  - agent-design
  - memory
  - copilot
aliases:
  - Agentic Memory
  - Copilot Agentic Memory
---

# Copilot Memory and Cross-Agent Persistence

> Repository-scoped persistent memory that Copilot builds autonomously from agent interactions, shared across coding agent, code review, and CLI, with citation-based verification and 28-day auto-expiry. Enabled by default for Pro and Pro+ users since March 2026.

## How Copilot Memory Works

Copilot Memory captures knowledge from agent interactions without manual curation. Agents identify patterns worth remembering and store them as structured entries ([GitHub engineering blog](https://github.blog/ai-and-ml/github-copilot/building-an-agentic-memory-system-for-github-copilot/)).

Each entry contains four components ([GitHub engineering blog](https://github.blog/ai-and-ml/github-copilot/building-an-agentic-memory-system-for-github-copilot/)):

| Component | Purpose |
|-----------|---------|
| Subject | Topic identification |
| Fact | The learned knowledge |
| Citations | Specific code locations (file paths + line numbers) |
| Reason | Actionable implications for future tasks |

Memories are repository-scoped: write access to create, read access to use ([GitHub engineering blog](https://github.blog/ai-and-ml/github-copilot/building-an-agentic-memory-system-for-github-copilot/)).

## Cross-Agent Sharing

Three Copilot surfaces share the same memory pool ([GitHub engineering blog](https://github.blog/ai-and-ml/github-copilot/building-an-agentic-memory-system-for-github-copilot/)):

- **Coding agent** — reads and writes memories during code generation
- **Code review** — reads and writes memories during PR review
- **CLI** — reads and writes memories during terminal interactions

When code review discovers a naming convention violation, that knowledge becomes available to the coding agent on the next task — each agent both contributes to and benefits from the shared knowledge base ([GitHub engineering blog](https://github.blog/ai-and-ml/github-copilot/building-an-agentic-memory-system-for-github-copilot/)).

## Citation-Based Verification and Self-Healing

Every entry is grounded in specific code locations. Before applying a memory, the agent performs just-in-time verification — checking that cited locations still exist and align with the stored fact ([GitHub engineering blog](https://github.blog/ai-and-ml/github-copilot/building-an-agentic-memory-system-for-github-copilot/)).

When verification reveals a contradiction, the agent generates a corrected version. GitHub tested this by seeding adversarial memories — agents consistently detected and corrected the conflicts ([GitHub engineering blog](https://github.blog/ai-and-ml/github-copilot/building-an-agentic-memory-system-for-github-copilot/)). The memory pool corrects itself through use rather than requiring manual curation.

## Auto-Expiry

Memories expire after 28 days. Use refreshes the timestamp, so actively relevant memories persist while unused entries are pruned ([GitHub changelog, Jan 2026](https://github.blog/changelog/2026-01-15-agentic-memory-for-github-copilot-is-in-public-preview/)). By contrast, Claude Code's auto memory persists without built-in expiry ([Claude Code docs](https://code.claude.com/docs/en/memory)).

## Measured Impact

Internal evaluation results ([GitHub engineering blog](https://github.blog/ai-and-ml/github-copilot/building-an-agentic-memory-system-for-github-copilot/)):

| Surface | Metric | With Memory | Without Memory |
|---------|--------|-------------|----------------|
| Coding agent | PR merge rate | 90% | 83% |
| Code review | Positive feedback rate | 77% | 75% |

Both results were statistically significant (p < 0.00001).

## Availability and Controls

| Date | Change | Source |
|------|--------|--------|
| Jan 15, 2026 | Public preview, opt-in for all paid plans | [GitHub changelog](https://github.blog/changelog/2026-01-15-agentic-memory-for-github-copilot-is-in-public-preview/) |
| Mar 4, 2026 | Enabled by default for Pro and Pro+ individual users | [GitHub changelog](https://github.blog/changelog/2026-03-04-copilot-memory-now-on-by-default-for-pro-and-pro-users-in-public-preview/) |

**Developer controls:**

- Individual toggle: `github.com/settings/copilot` > Features > Copilot Memory ([GitHub changelog](https://github.blog/changelog/2026-03-04-copilot-memory-now-on-by-default-for-pro-and-pro-users-in-public-preview/))
- Repository owners: Repository Settings > Copilot > Memory — review and delete stored memories ([GitHub changelog](https://github.blog/changelog/2026-01-15-agentic-memory-for-github-copilot-is-in-public-preview/))
- Organization/enterprise admins: policy-level enable/disable ([GitHub changelog](https://github.blog/changelog/2026-03-04-copilot-memory-now-on-by-default-for-pro-and-pro-users-in-public-preview/))

## Comparison with Other Memory Approaches

| Dimension | Copilot Memory | Claude Code Memory | OPENDEV (Research) |
|-----------|---------------|-------------------|-------------------|
| Creation | Autonomous from interactions | Human-authored (`CLAUDE.md`) + agent-authored (auto memory) | Agent-authored [episodic summaries](../../agent-design/episodic-memory-retrieval.md) |
| Scope | Repository | Project, user, managed policy | Session + cross-session |
| Sharing | Cross-agent (coding, review, CLI) | Single tool only | Single agent only |
| Verification | Citation-based, just-in-time | None (manual curation) | None |
| Expiry | 28-day TTL with use-based renewal | None (manual cleanup) | N/A (research system) |
| Self-healing | Contradiction detection | No | No |

Sources: [GitHub engineering blog](https://github.blog/ai-and-ml/github-copilot/building-an-agentic-memory-system-for-github-copilot/), [Claude Code docs](https://code.claude.com/docs/en/memory), [Bui 2025](https://arxiv.org/abs/2603.05344)

## Example

This example shows how Copilot Memory accumulates knowledge across surfaces without manual curation. Suppose a code review agent finds that your repository's service layer always injects dependencies through the constructor rather than using a service locator. The agent stores a memory entry like:

```
Subject: Dependency injection pattern
Fact: All service classes in src/services/ use constructor injection; service locator pattern is never used
Citations: src/services/UserService.ts:12, src/services/OrderService.ts:8
Reason: When generating new service classes, always use constructor injection and add dependencies to the constructor signature
```

The next time the coding agent implements a new feature that adds a `NotificationService`, it reads this memory, applies constructor injection automatically, and avoids a code review failure — without being explicitly told about the convention.

If a refactor later moves `UserService.ts`, the citation becomes stale. When the coding agent next accesses this memory, it checks whether `src/services/UserService.ts:12` still exists and still shows constructor injection. If the file moved but the pattern holds, the agent updates the citation. If the pattern was removed, the agent marks the memory as contradicted and generates a corrected version.

To inspect or delete stored memories for a repository, navigate to **Repository Settings > Copilot > Memory** — entries are listed with their citations and can be removed individually.

## Key Takeaways

- Cross-agent sharing is the distinguishing feature: knowledge flows between coding agent, code review, and CLI without developer intervention.
- Citation-based just-in-time verification prevents stale memories from degrading agent behavior.
- 28-day auto-expiry with use-based renewal balances freshness against unbounded growth.
- Measured impact: 7% increase in PR merge rates for the coding agent (p < 0.00001).

## When This Backfires

Autonomous memory creation without human curation works against you in several conditions:

- **Security-sensitive repositories**: an incorrectly stored memory about a security pattern (e.g., "always skip validation for internal services") can propagate to the coding agent and be applied silently, bypassing code review for the specific violation that created the false memory.
- **Repositories with contested conventions**: when a codebase is mid-refactor, agents may store memories from the old convention and resist the new one, creating a feedback loop where stale patterns self-reinforce until the memory expires.
- **Teams using explicit context files**: organizations that manage `.github/copilot-instructions.md` as the authoritative source of truth may find autonomous memories create ambiguity when the two sources diverge — the explicit instruction file takes precedence, but the agent may still surface the contradicting memory as a suggestion.
- **Multi-repository workflows**: memories are repository-scoped, so patterns learned in one repo do not transfer to others. Teams working across a monorepo split or separate service repos must rebuild memory independently in each context.

## Related

- [Agent Memory Patterns](../../agent-design/agent-memory-patterns.md)
- [Context Priming](../../context-engineering/context-priming.md)
- [Layered Context Architecture](../../context-engineering/layered-context-architecture.md)
- [Copilot Instructions Convention](./copilot-instructions-md-convention.md)
- [Copilot Coding Agent](./coding-agent.md)
- [Copilot Agent Mode](./agent-mode.md)
- [Copilot CLI Agentic Workflows](./copilot-cli-agentic-workflows.md)
- [Copilot Spaces](./copilot-spaces.md)
