---
title: "Conversation Registers for AI Coding Sessions"
term: "Conversation Registers"
description: "Name which of four interaction modes you are in with an LLM — exploring, brainstorming, deciding, implementing — and start a fresh context when the register changes."
tags:
  - context-engineering
  - human-factors
  - tool-agnostic
aliases:
  - conversational registers
  - register-switch context reset
last_reviewed: 2026-07-07
maturity: emerging
status: current
---

# Conversation Registers for AI Coding Sessions

> Conversation registers are four interaction modes — exploring, brainstorming, deciding, implementing — and switching register signals it is time to start a fresh context.

A conversation register is the intent behind how you talk to an LLM. It is independent of the topic you talk about. Chelsea Troy's DDD Europe 2026 talk on keeping the context window healthy names four registers, relayed by Martin Fowler as the idea he "hadn't thought about" ([Fowler, 2026](https://martinfowler.com/fragments/2026-06-16.html)). Two disciplines follow: name the register you are in, and when it changes, start a new conversation with fresh context ([Fowler, 2026](https://martinfowler.com/fragments/2026-06-16.html)).

## The four registers

Each register is a distinct request, quoted from Troy via Fowler ([Fowler, 2026](https://martinfowler.com/fragments/2026-06-16.html)):

| Register | What you are asking for |
|----------|-------------------------|
| Exploring | "I want to understand before touching anything" |
| Brainstorming | "Generate options, I'll evaluate them separately" |
| Deciding | "I need a recommendation with a rationale, not a list" |
| Implementing | "The decision is made, help me build it" |

The registers run in a rough order on one task: you explore a problem, brainstorm approaches, decide on one, then build it. The value is in naming which one you are in, because each wants a different response. Ask an Exploring question in the Implementing register and you get code when you wanted an explanation of how it works.

## Register drift as a reset signal

Register drift is a reset trigger separate from topic drift. You can stay on the same task and still switch register — from understanding a bug to building its fix. Troy's rule is that the switch itself warrants a fresh context, not just a new task ([Fowler, 2026](https://martinfowler.com/fragments/2026-06-16.html)).

This adds a human-facing axis to the [turn-level context decisions](turn-level-context-decisions.md) framework, where `/clear` handles switching to an unrelated task. It is also distinct from [phase-specific context assembly](phase-specific-context-assembly.md), which tailors the context bundle per agent role. Registers are about the intent you name for yourself before you prompt.

## Why it works

Each register leaves residue that is noise for the next one. Brainstorming fills the window with options you rejected; Exploring fills it with wide reads you no longer need. Once you move to Deciding or Implementing, that material becomes irrelevant context, which measurably degrades reasoning. A controlled benchmark finds LLMs are "significantly sensitive to [irrelevant context], affecting both reasoning path selection and arithmetic accuracy" ([Yang et al., 2025](https://arxiv.org/abs/2505.18761v2)). Anthropic describes the same effect as a steady [performance gradient](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) as the window fills. Starting fresh on a register switch drops the stale residue before it can distract. That is why register drift, not just topic drift, is a legitimate reset signal.

## When this backfires

A fresh context per register is not always worth its cost:

- Short sessions under a few thousand tokens: the residue is negligible, so resetting just forces re-priming and breaks momentum. [Claude Code best practices](https://code.claude.com/docs/en/best-practices) warn against clearing too early for the same reason.
- Tightly coupled explore-to-implement work: the exploration findings are often the exact context the build step needs. A hard reset strands that state unless you deliberately carry a summary across.
- One-shot prompts and quick edits: naming a register and opening a new conversation is ceremony that outweighs the benefit. The discipline targets longer, multi-mode sessions.

## Example

You are debugging a failing payment webhook. You open in the Exploring register: "walk me through how retries are handled here, do not change anything." The model reads five files and explains the flow. You now know the fix, so you switch to Implementing.

Rather than continue the thread, you start a fresh conversation and prompt: "In `webhooks/payment.py`, the retry handler double-charges on a 500 — add idempotency keyed on the event ID." The new context carries only the decision and the target file, not the five-file exploration transcript that would otherwise compete for the model's attention.

## Key Takeaways

- When unsure which register you are in, match your ask to the table's phrasing rather than guessing from the topic alone.
- Name the register before you prompt so you ask for the right kind of response.
- Switching register on the same task is a reset signal: start a fresh context, because register drift matters as much as topic drift.
- The mechanism is context hygiene, not memory: stale residue [degrades reasoning](https://arxiv.org/abs/2505.18761) before you'd notice, so reset proactively rather than after a wrong answer.
- Skip the reset for short, tightly coupled, or one-shot work, where re-priming costs more than the stale residue.

## Related

- [Turn-Level Context Decisions](turn-level-context-decisions.md) — the five-move menu where `/clear` handles switching to an unrelated task
- [Phase-Specific Context Assembly](phase-specific-context-assembly.md) — tailoring the context bundle per agent role, the machine-facing counterpart
- [Context Window Dumb Zone](context-window-dumb-zone.md) — how reasoning degrades as the window fills
- [Goal Recitation](goal-recitation.md) — keeping intent in the attention window within a session
- [The Kitchen Sink Session](../patterns/anti-patterns/session-partitioning.md) — the anti-pattern that clearing between contexts addresses
