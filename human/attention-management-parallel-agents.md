---
title: "Developer Attention Management with Parallel Agents"
description: "When running parallel AI agents, your scarce resource is not coding but attention. Managing it well means applying CPU scheduling principles to human focus."
tags:
  - human-factors
  - agent-design
  - multi-agent
aliases:
  - "attention management"
  - "CPU scheduler metaphor"
  - "developer as scheduler"
---
# Developer as CPU Scheduler: Attention Management with Parallel Agents

> With multiple AI agents running simultaneously, your scarce resource is not coding ability but attention — and managing it resembles CPU scheduling more than traditional software engineering.

## The Scheduling Metaphor

When you run parallel agent sessions, your role shifts from executing work to dispatching and reviewing it. The [ClaudeLog "You Are the Main Thread"](https://claudelog.com/mechanics/you-are-the-main-thread) framing captures this: treat your attention as the main thread, agent sessions as worker threads, and apply the principle "do not block the main thread."

With N agents running, a single idle minute represents N units of forgone progress — each unspawned agent is an idle core. [Source: [ClaudeLog](https://claudelog.com/mechanics/you-are-the-main-thread)]

## Attention as the Bottleneck

The natural bottleneck in parallel agent workflows is not code generation — it is your review capacity. As Addy Osmani observes, "the highest-leverage developers will look like async-first managers running a small fleet of parallel AI coding agents," and the constraint shifts from producing code to evaluating it. [Source: [Addy Osmani — Your AI Coding Agents Need a Manager](https://addyosmani.com/blog/coding-agents-manager/)]

The Sora for Android team found simultaneous Codex sessions felt "uncannily similar to being a tech lead with several new engineers, all making progress, all needing guidance." [Source: [OpenAI — Shipping Sora for Android with Codex](https://openai.com/index/shipping-sora-for-android-with-codex/)]

Agents work in parallel without attention cost to each other; the human switches serially, each switch carrying cognitive overhead.

## Scheduling Strategies

### Idle Core Detection

The reflexive question: "What asynchronous process could I have running in the background that could be delivering value?" [Source: [ClaudeLog](https://claudelog.com/mechanics/you-are-the-main-thread)] Recognizing idle agent slots and filling them with delegatable tasks is a distinct skill from writing code.

### WIP Limits

Osmani describes pairing background agents (4-5 low-touch sessions handling mechanical tasks) with human-in-the-loop sessions (3-5 high-touch sessions requiring architectural judgment). [Source: [Addy Osmani — Your AI Coding Agents Need a Manager](https://addyosmani.com/blog/coding-agents-manager/)] This mirrors WIP limits in lean manufacturing — unbounded parallelism degrades review quality faster than it accelerates output.

### Task Classification for Delegation

Not all work benefits equally from parallel dispatch. Osmani distinguishes three tiers:

- **Fully delegated** — mechanical implementation, boilerplate, migrations. Fire and review later.
- **Checkpoint-based** — shared interfaces, integration points. Agent works autonomously between human review gates.
- **Human-only** — architecture decisions, product intent, security-critical judgment. Never delegated.

[Source: [Addy Osmani — Your AI Coding Agents Need a Manager](https://addyosmani.com/blog/coding-agents-manager/)]

### Context-Switch Efficiency

Parallel agent work inverts the focus-time ideal: you context-switch frequently, reviewing outputs and unblocking agents. [Source: [The Pragmatic Engineer](https://blog.pragmaticengineer.com/new-trend-programming-by-kicking-off-parallel-ai-agents/)]

Armin Ronacher: "it's only so much my mind can review." Context-switch throughput varies, but everyone has a ceiling. [Source: [The Pragmatic Engineer](https://blog.pragmaticengineer.com/new-trend-programming-by-kicking-off-parallel-ai-agents/)]

## When the Metaphor Breaks

CPU schedulers are deterministic; human attention is not. Key differences:

- **Fatigue degrades throughput.** Review quality drops over extended sessions, compounding error risk across active agents.
- **Not all switches are equal.** Switching between two boilerplate agents costs less than switching between an architecture decision and a debugging session.
- **Coordination overhead grows non-linearly.** Brooks's Law applies — each additional agent session increases the total coordination surface, and linear speedup is not guaranteed.

The metaphor helps recognize idle capacity and structure dispatch; it misleads if applied without accounting for human limits.

## Example

A developer runs four parallel Claude Code sessions across git worktrees, applying the three-tier task classification before spawning each agent:

```bash
# Create isolated worktrees for parallel agents
git worktree add ../feature-auth -b feature/auth-refactor
git worktree add ../feature-tests -b feature/test-coverage
git worktree add ../feature-docs -b feature/docs-update
git worktree add ../feature-migrate -b feature/db-migration
```

Each session gets a task classified before dispatch:

| Session | Task | Tier |
|---------|------|------|
| `../feature-tests` | Add unit tests for existing auth module | Fully delegated — fire and review later |
| `../feature-docs` | Update API reference from OpenAPI spec | Fully delegated |
| `../feature-migrate` | Write Alembic migration for new `user_roles` table | Checkpoint-based — review schema before applying |
| `../feature-auth` | Refactor auth to support OAuth2 + PKCE | Human-in-the-loop — architectural judgment required |

The developer monitors the fully-delegated sessions only when they emit completion signals, keeps one terminal pane open for the auth refactor, and uses the idle minutes (waiting for agents to complete) to classify the next batch of tasks. WIP is kept to four sessions — adding a fifth would push review load past the point where output quality can be validated.

## Key Takeaways

- Treat attention as the main thread; agent sessions are worker threads — keep spawning work when capacity allows
- WIP limit: 4–5 background sessions plus 3–5 high-touch sessions is a practical ceiling
- Classify tasks by delegation tier before spawning — architecture and product decisions stay with you

## Related

- [Parallel Agent Sessions](../workflows/parallel-agent-sessions.md)
- [/batch and Worktrees](../tools/claude/batch-worktrees.md)
- [Cognitive Load, AI Fatigue, and Sustainable Agent Use](cognitive-load-ai-fatigue.md)
- [The Delegation Decision](../agent-design/delegation-decision.md)
- [Worktree Isolation](../workflows/worktree-isolation.md)
- [Distributed Computing Parallels in Agent Architecture](distributed-computing-parallels.md)
- [Sub-Agents for Fan-Out Research and Context Isolation](../multi-agent/sub-agents-fan-out.md)
- [The Bottleneck Migration](bottleneck-migration.md)
- [The Addictive Flow State of Agent-Assisted Development](addictive-flow-agent-development.md)
- [Skill Atrophy](skill-atrophy.md)
- [Context Ceiling](context-ceiling.md)
- [Rigor Relocation](rigor-relocation.md)
- [Developer Control Strategies for AI Coding Agents](developer-control-strategies-ai-agents.md)
- [Progressive Autonomy and Model Evolution](progressive-autonomy-model-evolution.md)
