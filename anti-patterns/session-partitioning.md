---
title: "The Kitchen Sink Session Anti-Pattern in AI Agents"
description: "Mixing unrelated tasks in a single Claude Code session fills the context window with irrelevant history, degrades output quality, and increases token costs."
tags:
  - cost-performance
  - context-engineering
aliases:
  - kitchen sink session
  - session partitioning
  - context pollution
---

# The Kitchen Sink Session

> Mixing unrelated tasks in a single Claude Code session fills the context window with irrelevant history and degrades output quality.

## The Problem

It is tempting to keep one Claude Code session running all day and pile tasks onto it — review a PR, then start a feature, then debug a test failure. Each task leaves residue: file contents, command outputs, failed approaches, and off-topic reasoning. As the context fills, Claude begins making decisions influenced by stale information from earlier tasks.

The [Claude Code best practices](https://code.claude.com/docs/en/best-practices) documentation describes this as the "kitchen sink session" anti-pattern: context full of irrelevant information that degrades performance on the current task. According to the same source, LLM performance degrades as context fills — the context window is the primary resource to manage. Independent research by Chroma on [context rot](https://github.com/chroma-core/context-rot) corroborates this: across 18 frontier models, performance varies significantly with input length even on simple tasks, and irrelevant tokens degrade reliability more than length alone would predict.

Token costs reflect this directly. A session that runs through code review, feature development, and a debugging investigation accumulates far more context than three focused sessions would. You pay for the noise.

## What to Do Instead

Give each session a single objective. When you finish a task and move to something unrelated, start a new session — not a `/clear`.

**Clear context within a session** when switching between loosely related tasks where shared background still applies:

```
/clear
```

**Resume a specific thread** without re-entering context manually:

```bash
claude --continue    # resume the most recent session
claude --resume      # choose from recent sessions
```

Claude Code saves conversations locally, so starting a new session does not mean losing prior work ([Claude Code best practices](https://code.claude.com/docs/en/best-practices)). Use `/rename` to give sessions descriptive names (`oauth-migration`, `debugging-memory-leak`) so you can find them later with `--resume`.

**For multi-step workflows with a clear dependency chain**, structured sub-agents are the correct model. Each sub-agent runs in its own context window and reports back a summary, keeping your main session clean.

## Example

A developer spends the morning reviewing a pull request in Claude Code, then switches to scaffolding a new feature, then investigates a flaky test — all in the same session. By the third task, the context contains diff hunks, file reads, and unrelated error logs. Claude now has tens of thousands of tokens of history, most irrelevant. When asked what to name a new service class, Claude may anchor on naming patterns from the PR rather than the feature being built.

**Correct approach — three focused sessions:**

```bash
# Session 1: PR review only
claude "Review PR #412 — focus on auth logic"

# Session 2: Feature scaffolding only
claude "Scaffold the new billing service under src/billing/"

# Session 3: Debug flaky test only
claude "Investigate why tests/integration/auth_test.py fails intermittently"
```

Each session starts clean. Context stays low, costs stay low, and output quality is higher because Claude reasons only over relevant history.

## When This Backfires

Splitting sessions adds overhead. Claude re-reads CLAUDE.md and any shared context files on startup; if two tasks share significant background (a codebase you have already walked through, an architectural decision you established earlier), that re-loading cost can outweigh the noise reduction from a clean start.

Auto-compaction also changes the calculus. Claude Code now automatically compacts long conversations when approaching context limits — summarizing decisions, file states, and patterns while discarding ephemeral noise. For loosely coupled tasks where auto-compaction fires before quality degrades, an explicit session split may not be necessary. Use `/compact` manually for finer control.

Split sessions remain the right call when: tasks are unrelated enough that shared history actively misleads (naming anchored to a prior PR, debugging instincts from a fixed bug); context is already full of failed approaches; or you are starting a review of code Claude itself just wrote in the same session.

## Key Takeaways

- One objective per session; use `/clear` between loosely related tasks in the same session.
- Use `claude --continue` or `claude --resume` to pick up prior threads — session history is always available.
- Token cost scales with context size; focused sessions are cheaper than long-running mixed sessions.

## Related

- [Infinite Context Anti-Pattern](infinite-context.md)
- [Objective Drift](objective-drift.md)
- [Context Poisoning](context-poisoning.md)
- [The Anthropomorphized Agent](anthropomorphized-agent.md) — misattributing stateless session behavior to agent memory or personality
- [Agent Memory Patterns: Learning Across Conversations](../agent-design/agent-memory-patterns.md) — how to persist knowledge across sessions intentionally
- [Perceived Model Degradation](perceived-model-degradation.md) — bloated sessions can mimic apparent model quality loss
- [Reasoning Overuse](reasoning-overuse.md) — excess reasoning compounds token cost in long sessions
- [Demo-to-Production Gap](demo-to-production-gap.md) — session management habits from demos that break at scale
- [Shadow Tech Debt](shadow-tech-debt.md) — hidden costs from unmanaged context accumulation
- [Distractor Interference](distractor-interference.md) — how semantically related but irrelevant instructions degrade compliance
- [Token Preservation Backfire](token-preservation-backfire.md) — competing cost-reduction objectives that reduce output quality
