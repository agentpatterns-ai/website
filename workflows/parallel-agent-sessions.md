---
title: "Parallel Agent Sessions Shift the Bottleneck from Writing"
description: "Running multiple agent sessions in parallel shifts the bottleneck from writing code to architectural decisions, feedback, and integration."
aliases:
  - Parallel Agent Infrastructure
  - Multi-Agent Parallelism
tags:
  - agent-design
  - human-factors
  - workflows
  - multi-agent
  - tool-agnostic
last_reviewed: 2026-06-12
maturity: established
---

# Parallel Agent Sessions Shift the Bottleneck from Writing Code to Making Decisions

> Running multiple agent sessions in parallel shifts the bottleneck from writing code to architectural decisions, feedback, and integration — the engineer becomes a tech lead.

Learn it hands-on with the [Becoming a Tech Lead](https://learn.agentpatterns.ai/workflows/becoming-a-tech-lead/) guided lesson, which includes quizzes.

!!! note "Also known as"
    Parallel Agent Infrastructure, Multi-Agent Parallelism. For the technical mechanism — git worktrees for filesystem isolation — see [Worktree Isolation](worktree-isolation.md).

## The shift in practice

At peak, the Sora team ran Codex sessions on playback, search, error handling, and tests at the same time. Each session reported its progress and flagged when it needed attention. The team described the experience as "uncannily similar to being a tech lead with several new engineers, all making progress, all needing guidance." [Source: [Shipping Sora for Android with Codex](https://openai.com/index/shipping-sora-for-android-with-codex/)]

The shift is real: the human stops writing code and starts making decisions. Architecture choices, UX trade-offs, systemic changes, and PR review become the throughput constraint — not typing speed or how well you know the codebase.

## What agents can parallelize

Sessions work best when you can divide the work along natural boundaries:

- Independent modules or components with clean interfaces
- Separate concerns (tests, error handling, logging, a specific feature)
- Tasks that can be integrated via PR review rather than requiring real-time coordination

Sessions conflict when they edit shared files, when their correct behavior depends on decisions the other session has not made yet, or when integration needs architectural judgment you cannot delegate to either session.

## Coordination overhead grows with parallelism

Brooks's Law applies to agent sessions: adding more sessions increases coordination overhead, and linear speedup is not guaranteed. [Source: [Shipping Sora for Android with Codex](https://openai.com/index/shipping-sora-for-android-with-codex/)]

Each active session requires:

- Periodic review of progress updates
- Answers to blocking questions
- Integration decisions when session outputs interact
- Final PR review before merge

How many sessions one engineer can manage well depends on task complexity and how often each session needs attention. Beyond a handful of concurrent sessions, the overhead of staying current may exceed the parallelism benefit.

## Agents do not context-switch, but humans do

Agents work in parallel at no attention cost to each other. Humans switch between sessions one at a time, and each switch carries cognitive overhead. This asymmetry means the human's capacity for careful review and decision-making, not the number of agent sessions available, becomes the real throughput constraint. [Source: [Shipping Sora for Android with Codex](https://openai.com/index/shipping-sora-for-android-with-codex/)]

This has practical implications:

- Design sessions to batch their questions rather than interrupting constantly
- Structure tasks so a session can make progress independently for extended periods before needing input
- Prioritize time spent on decisions that only the human can make over review of work the agent handles reliably

## Session lifecycle and interruption

When parallel work runs across multiple sessions, the distinction between foreground and background tasks shapes how the human can reset context without disrupting in-flight work.

- Foreground tasks — the current interactive prompt or command in a session; resetting the session context, for example with a clear-context command, ends them
- Background tasks — agents and bash processes launched in the background, for example via scheduled or loop commands in tools that support them; these continue independently of the foreground prompt

Check the release notes for the specific tool in use to confirm exactly how its clear-context command interacts with background work — behavior varies across tools and versions, and Claude Code's `/clear` semantics, in particular, have evolved across releases. [Source: [Claude Code release notes](https://docs.claude.com/en/release-notes/claude-code)]

The practical point: design parallel workflows so that resetting the foreground does not abort the work you most want to preserve.

## Review concentration and quality

When parallel sessions run, review and testing responsibilities concentrate on the human rather than being distributed across the implementation work. The human reviews more output per unit time than in a serial workflow, which is the [attention-management](../human/attention-management-parallel-agents.md) problem at the core of parallel supervision.

This makes each review decision matter more. Rigor does not decrease at scale; if anything, the integration complexity of multiple concurrent sessions makes careful review more important, not less.

## Example

The following shows a typical parallel session setup using git worktrees to isolate concurrent Claude Code sessions on the same repo. Each session works on a separate branch without touching shared working-tree state, the guarantee [worktree isolation](worktree-isolation.md) provides.

```bash
# Create three isolated worktrees from main
git worktree add ../feature-playback -b feature/playback
git worktree add ../feature-search -b feature/search
git worktree add ../feature-error-handling -b feature/error-handling

# Launch an agent session in each worktree
cd ../feature-playback && claude --no-auto-updater &
cd ../feature-search && claude --no-auto-updater &
cd ../feature-error-handling && claude --no-auto-updater &
```

Each session receives a scoped task prompt that defines its boundary and specifies when to pause for human review:

```
You are working in the feature/playback worktree.
Your task: implement the video playback module in src/playback/.
Do not modify files outside src/playback/.
When you have a design decision that affects the player API surface, stop and report — do not proceed.
```

With this structure, the engineer reviews progress updates from each session in turn, answers blocking architectural questions, and merges each branch via PR when the session completes. The bottleneck is the engineer's review bandwidth, not agent execution speed.

The same isolation can move off the laptop. Vercel describes Conductor [moving parallel coding agents from the laptop to cloud-isolated workspaces](https://vercel.com/blog/how-conductor-moved-parallel-coding-agents-from-the-laptop-to-the-cloud-with-vercel-sandbox), and Superset [running up to 10 coding agents in parallel, each in an isolated workspace, with every branch auto-creating a preview deployment](https://vercel.com/blog/how-superset-built-the-ide-for-ai-agents-on-vercel) — cloud-sandboxed equivalents of the local-worktree setup above. [Source: [Conductor on Vercel Sandbox](https://vercel.com/blog/how-conductor-moved-parallel-coding-agents-from-the-laptop-to-the-cloud-with-vercel-sandbox), [Superset IDE for AI agents](https://vercel.com/blog/how-superset-built-the-ide-for-ai-agents-on-vercel)] Moving sessions to the cloud does not relax the human bottleneck: it raises the ceiling on concurrent sessions, which only sharpens the review-bandwidth constraint described above.

## Key Takeaways

- Parallel sessions shift the bottleneck from writing code to making architectural decisions, giving feedback, and integrating changes
- Each session requires attention, feedback, and review — they are not fire-and-forget
- Brooks's Law applies: coordination overhead grows with parallelism, and linear speedup is not guaranteed
- The human's capacity for high-quality review, not the number of agent sessions, is the actual throughput constraint
- Design tasks so sessions batch their questions and can make extended progress independently
- Separate foreground tasks (the current prompt) from background tasks (scheduled or backgrounded agents and bash) so that resetting session context preserves the work you want to keep — confirm exact behavior in your tool's release notes

## Related

- [Worktree Isolation](worktree-isolation.md)
- [Human in the Loop](human-in-the-loop.md)
- [Background-to-Foreground Handoff](background-foreground-handoff.md)
- [The Delegation Decision](../agent-design/delegation-decision.md)
- [Agent Handoff Protocols](../multi-agent/agent-handoff-protocols.md)
- [Attention Management with Parallel Agents](../human/attention-management-parallel-agents.md)
- [Single-Branch Git for Agent Swarms](single-branch-git-agent-swarms.md)
- [Compound Engineering](compound-engineering.md)
- [Tiled Agent Layout: Supervising Parallel Agents Through Dedicated Panes](tiled-agent-layout.md) — the pane-per-agent screen layout for supervising the concurrent sessions this pattern creates
