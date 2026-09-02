---
title: "Agentic Skill Decay: Which Capabilities Erode Under Agent Delegation"
description: "Agent delegation removes the unprompted use of a capability at the point it used to fire, while the knowledge itself stays. The decay tracks which sub-tasks the agent absorbs and succeeds at quietly."
term: "Agentic Skill Decay"
aliases:
  - agent-driven skill decay
  - selective capability erosion
  - deliberate reps with agents
tags:
  - human-factors
  - anti-pattern
  - tool-agnostic
last_reviewed: 2026-09-01
maturity: emerging
status: current
---

# Agentic Skill Decay: Which Capabilities Erode Under Agent Delegation

> Agentic skill decay removes the unprompted use of a capability at the moment it used to fire, while the underlying knowledge stays.

Two conditions must hold together before a capability decays. The agent absorbs a sub-task you used to do by hand, and it succeeds there quietly. Miss either condition and the skill stays exercised. Bappy et al. observed 15 professional engineers and found that AI assistants "reorganize rather than eliminate security thinking, shifting it from the act of writing code to the act of reviewing it" ([arxiv 2605.23130v2](https://arxiv.org/abs/2605.23130v2)). None of their observed coding sessions put security requirements in the initial prompt, "even when they possessed the relevant knowledge." The knowledge was intact. Its trigger had moved.

## The mistake is the reflection trigger

Addy Osmani built his judgment out of work that agents now absorb: "try different approaches out, debug what went wrong, review other's code, read a lot" ([Osmani, 2026](https://addyo.substack.com/p/agentic-skill-decay)). Those repetitions were a byproduct of shipping rather than the goal, so removing them costs nothing visible.

Osmani's sharper point is why the loss stays hidden. "When a task is finished, it doesn't necessarily mean that you have learned something. It just means that the task has been finished." A failure raises the question of what went wrong. A clean success raises nothing. Decay runs fastest through the domains your agent handles well, and those are the domains you have least reason to open.

## Which capabilities hold

Osmani practices four deliberately: decision making, specifying, steering, and verifying. They hold because an agent workflow still routes you through each one on every task, so those reps keep arriving without planning. He compresses the limits: "verification is the floor and imagination is the ceiling."

What goes is domain depth the agent reaches without you. Thousands of hours in the Chrome DevTools performance panel built Osmani's profiling instinct. With a DevTools MCP running the trace and proposing the fix, "you don't necessarily then build up that expertise in performance quite as much."

Misjudging which side a capability sits on costs measurably. Anthropic rated roughly 400,000 Claude Code sessions by task-specific expertise. Novice-rated sessions reached verified success 15% of the time against 28-33% for sessions rated intermediate or above, and among sessions that hit trouble the gap widened from 4% to 15% ([Anthropic, 2026](https://www.anthropic.com/research/claude-code-expertise)). Expertise there is task-scoped: "A senior engineer asking their first Rust question is a beginner at Rust."

## Why it works

The decay is uneven because the repetitions were never the point of the work. They were a byproduct, and an agent removes the byproduct while preserving the outcome.

The two halves compound. Because the trigger is the mistake, decay concentrates where the agent performs well. Because the knowledge relocates downstream instead of disappearing ([arxiv 2605.23130v2](https://arxiv.org/abs/2605.23130v2)), it still answers whenever you deliberately check. A capability that fires only on inspection, over output that usually looks fine, reads as intact right up to the task that needs it.

## Example

Osmani's countermeasure is a dual loop: a rep should sharpen you and sharpen your agent in the same pass. The failure mode is leaving the lesson where only one of you can reach it.

He gives the case himself: you discover "some subtle scrolling bug in a UI component," work it out with the agent over a long session, and land the fix.

**Before** — the lesson dies with the session: the reasoning stays in the transcript, where compaction may drop it. Osmani's words: "that lesson could disappear when the chat window dies." You keep the fix and lose the constraint behind it.

**After** — the correction is codified where the next agent reads it: you spend a few minutes deciding what it generalizes to, then commit it as "specific lessons, tests, lint rules, anything, especially that is small enough that it can be codified in your repo."

Osmani's stated reason is durability. Without codification "every time that you're starting a new session, it can feel like you're onboarding a new hire that has amnesia" ([Osmani, 2026](https://addyo.substack.com/p/agentic-skill-decay)).

## When this backfires

A codified rule outlives its assumption. Osmani warns against "over investing in that as a strategy" and draws the boundary: "Skills and MCPs can encode a useful workflow. They cannot tell you when its assumptions no longer fit your system." A stale lint rule is worse than an unwritten lesson, because it now enforces.

Relocating a skill to review assumes review happens. Ghammam and Almukhtar analyzed 387 agent-authored pull requests and found "61.4% (238/387) of the analyzed PRs were merged by developers, and in most cases, the merge occurred immediately after automated checks passed, with no additional modifications from human reviewers" ([arxiv 2601.16839v1](https://arxiv.org/abs/2601.16839v1)). A capability moved to a step nobody performs is retired.

Session count outruns the attention the practice needs. Osmani ran five to ten concurrent sessions and caught himself asking the wrong project to add dark mode: "agent throughput scales faster than my attention." Two smaller failures follow. Because the Anthropic data scores expertise per task, reps in a domain the agent already handles reliably buy nothing. And delivery pressure eats what survives that filter, since "there are all these velocity expectations and there's this pressure to ship fast" ([Osmani, 2026](https://addyo.substack.com/p/agentic-skill-decay)): a half-kept regimen returns the reassurance without the rep.

The evidence cuts both ways. Osmani calls the quiz study behind the general atrophy case "a short-term study of just one Python library, so I wouldn't say it's conclusive necessarily," and declines to forecast how long code-level expertise stays this valuable.

## Key Takeaways

- Test a capability against both conditions before spending practice time on it. Ask whether the agent absorbed the sub-task, and whether it succeeds there without visible correction.
- Treat a clean run as a signal to inspect, not as evidence you still hold the skill it exercised.
- A closed task is not a rep. Reps come from corrected hypotheses, so form one before prompting or the run teaches nothing.
- Codify a correction as a rule, test, or convention only when you can state the assumption it rests on and would notice that assumption breaking.
- Check that the review step still happens before relying on it to keep a relocated capability alive.

## Related

- [Skill Atrophy: When AI Reliance Erodes Developer Capability](skill-atrophy.md) — the general case: whether atrophy happens, who it hits hardest, and the cognitive-offloading mechanism behind it
- [Deliberate AI-Assisted Learning: Accelerating Skill Acquisition](deliberate-ai-learning.md) — the interaction styles that put reps back into an agent workflow
- [From Preventive to Reactive: Front-Loading Security in AI Coding Prompts](preventive-to-reactive-security-prompting.md) — the same relocation observed in one domain, with the prompt-time remedy
- [Developer as CPU Scheduler: Attention Management with Parallel Agents](attention-management-parallel-agents.md) — the throughput constraint that breaks per-task practice
- [Comprehension Debt](../patterns/anti-patterns/comprehension-debt.md) — the codebase-level counterpart to a capability you no longer exercise
