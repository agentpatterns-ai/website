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
---
# Parallel Agent Sessions Shift the Bottleneck from Writing Code to Making Decisions

> When multiple agent sessions run simultaneously, the human engineer's role transforms from individual contributor to tech lead — the bottleneck shifts from writing code to making architectural decisions, giving feedback, and integrating changes.

!!! note "Also known as"
    Parallel Agent Infrastructure, Multi-Agent Parallelism. For the technical mechanism — git worktrees for filesystem isolation — see [Worktree Isolation](worktree-isolation.md).

## The Shift in Practice

At peak, the Sora team ran simultaneous Codex sessions on playback, search, error handling, and tests in parallel. Each session periodically reported back with progress and required attention. The experience was described as "uncannily similar to being a tech lead with several new engineers, all making progress, all needing guidance." [Source: [Shipping Sora for Android with Codex](https://openai.com/index/shipping-sora-for-android-with-codex/)]

The shift is substantive: the human stops producing code and starts producing decisions. Architecture choices, UX trade-offs, systemic changes, and PR review become the throughput constraint — not typing speed or familiarity with the codebase.

## What Agents Can Parallelize

Sessions work best when the work can be divided along natural boundaries:

- Independent modules or components with clean interfaces
- Separate concerns (tests, error handling, logging, a specific feature)
- Tasks that can be integrated via PR review rather than requiring real-time coordination

Sessions conflict when they edit shared files, when their correct behavior depends on decisions the other session hasn't made yet, or when integration requires significant architectural judgment that can't be delegated to either session.

## Coordination Overhead Grows with Parallelism

Brooks's Law applies to agent sessions: adding more sessions increases coordination overhead, and linear speedup is not guaranteed. [Source: [Shipping Sora for Android with Codex](https://openai.com/index/shipping-sora-for-android-with-codex/)]

Each active session requires:

- Periodic review of progress updates
- Answers to blocking questions
- Integration decisions when session outputs interact
- Final PR review before merge

Three to five sessions may be a practical ceiling for one engineer, depending on task complexity and how frequently sessions need attention [unverified]. Beyond that, the overhead of staying current with all sessions may exceed the parallelism benefit.

## Agents Don't Context-Switch; Humans Do

Agents work in parallel without attention cost to each other. Humans switch between sessions serially — each switch carries cognitive overhead. The asymmetry means the human's capacity for high-quality review and decision-making, not the number of available agent sessions, becomes the actual throughput constraint. [Source: [Shipping Sora for Android with Codex](https://openai.com/index/shipping-sora-for-android-with-codex/)]

This has practical implications:

- Design sessions to batch their questions rather than interrupting constantly
- Structure tasks so a session can make progress independently for extended periods before needing input
- Prioritize time spent on decisions that only the human can make over review of work the agent handles reliably

## Session Lifecycle and Interruption

When running parallel sessions, `/clear` cancels only the foreground task — background agent and bash tasks continue running. This means `/clear` is safe to use mid-session without losing background agent work that is still in flight. [Source: [Claude Code changelog, v2.1.72](https://docs.anthropic.com/en/docs/claude-code)]

The distinction matters for parallel workflows:

- **Foreground tasks** — the current interactive prompt or command; cancelled by `/clear`
- **Background tasks** — agents and bash processes launched in the background (e.g., via `/loop` or Cron tools); survive `/clear`

This pairs with scheduled and background work patterns: long-running background agents now survive session clears, so an engineer can reset context without aborting in-progress background work.

## Review Concentration and Quality

When parallel sessions run, review and testing responsibilities concentrate on the human rather than being distributed across the implementation work. The human reviews more output per unit time than in a serial workflow.

This increases the importance of each review decision. Rigor doesn't decrease at scale — if anything, the integration complexity of multiple concurrent sessions makes careful review more important, not less.

## Example

The following shows a typical parallel session setup using git worktrees to isolate concurrent Claude Code sessions on the same repo. Each session works on a separate branch without touching shared working-tree state.

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

## Key Takeaways

- Parallel sessions shift the bottleneck from writing code to making architectural decisions, giving feedback, and integrating changes
- Each session requires attention, feedback, and review — they are not fire-and-forget
- Brooks's Law applies: coordination overhead grows with parallelism, and linear speedup is not guaranteed
- The human's capacity for high-quality review, not the number of agent sessions, is the actual throughput constraint
- Design tasks so sessions batch their questions and can make extended progress independently
- `/clear` cancels only the foreground task — background agents and bash tasks survive, making it safe to reset context mid-session

## Unverified Claims

- Three to five sessions may be a practical ceiling for one engineer [unverified]

## Related

- [Worktree Isolation](worktree-isolation.md)
- [Human in the Loop](human-in-the-loop.md)
- [The Delegation Decision](../agent-design/delegation-decision.md)
- [Agent Handoff Protocols](../multi-agent/agent-handoff-protocols.md)
- [Claude Code ↔ Copilot CLI: Changelog-Driven Feature Parity](changelog-driven-feature-parity.md)
- [Attention Management with Parallel Agents](../human/attention-management-parallel-agents.md)
- [Single-Branch Git for Agent Swarms](single-branch-git-agent-swarms.md)
