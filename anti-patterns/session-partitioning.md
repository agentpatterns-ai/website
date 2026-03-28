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

The [Claude Code best practices](https://code.claude.com/docs/en/best-practices) documentation describes this as the "kitchen sink session" anti-pattern: context full of irrelevant information that degrades performance on the current task. According to the same source, LLM performance degrades as context fills — the context window is the primary resource to manage.

Token costs reflect this directly. A session that runs through code review, feature development, and a debugging investigation accumulates far more context than three focused sessions would [unverified]. You pay for the noise.

## What to Do Instead

Give each session a single objective. When you finish a task and move to something unrelated, start a new session — not a `/clear`.

**Clear context within a session** when switching between loosely related tasks where shared background still applies:

```
/clear
```

**Resume a specific thread** without re-entering context manually:

```bash
claude --continue    # resume the most recent session [unverified]
claude --resume      # choose from recent sessions [unverified]
```

Sessions auto-save with full history [unverified], so starting a new session does not mean losing prior work. Use `/rename` to give sessions descriptive names [unverified] (`oauth-migration`, `debugging-memory-leak`) so you can find them later with `--resume`.

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

## Key Takeaways

- One objective per session; use `/clear` between loosely related tasks in the same session.
- Use `claude --continue` or `claude --resume` to pick up prior threads — session history is always available.
- Token cost scales with context size; focused sessions are cheaper than long-running mixed sessions.

## Related

- [Infinite Context Anti-Pattern](infinite-context.md)
- [Objective Drift](objective-drift.md)
- [Context Poisoning](context-poisoning.md)
- [The Anthropomorphized Agent](anthropomorphized-agent.md) — misattributing stateless session behavior to agent memory or personality
- [Perceived Model Degradation](perceived-model-degradation.md) — bloated sessions can mimic apparent model quality loss
- [Reasoning Overuse](reasoning-overuse.md) — excess reasoning compounds token cost in long sessions
