---
title: "Conceptual Integrity Erosion in Agent-Built Codebases"
term: "Conceptual Integrity Erosion"
description: "When a feature costs an hour instead of a week, the time cost that used to reject weak features is gone and the system's design stops cohering."
tags:
  - anti-pattern
  - human-factors
  - tool-agnostic
aliases:
  - design drift
  - architectural incoherence
last_reviewed: 2026-08-25
maturity: emerging
---

# Conceptual Integrity Erosion in Agent-Built Codebases

> Time cost used to reject weak features for you. At an hour per feature it rejects nothing, and conceptual integrity erodes.

Conceptual integrity erosion is the loss of a system's coherent design once the cost of building a feature collapses. Fred Brooks named the property in *The Mythical Man-Month*; Simon Willison summarizes it as software that holds no surprises and fits together. The discipline protecting it was never a review step. It was the price. "It used to be that the discipline was enforced on you by the amount of time it took... If it takes an hour, it's so much easier to justify" ([Willison, August 2026](https://simonwillison.net/2026/Aug/19/conceptual-integrity-and-counting-lines-of-code/)). Claire Giordano's analogy in the same conversation is the Winchester Mystery House: 140 rooms, added over forty years. No single addition was the mistake.

## What it looks like

A small change touches an implausible number of files. Birgitta Böckeler rebuilt an internal analytics app with coding agents, and changing how a user picks a date range needed edits in more than 40 files ([Böckeler, May 2026](https://martinfowler.com/articles/sensors-for-coding-agents.html)). She already suspected something was wrong, and a modularity review confirmed it: request parameters "repeated at every level", and a third page that "deviated from that and reimplemented similar behaviour in its own way" rather than reuse the hook the first two shared.

## Why it works

The mechanism is cost, not model quality. A week of work weighed itself against a week of your life, so time ran the rejection filter nobody had to run deliberately. Remove the week and the filter goes with it. That is the uncomfortable half of the argument: it predicts the failure worsens as agents improve.

Nothing supplies the missing filter. GitClear analyzed 623 million code changes across 2023–2026 and found newly written code connects to existing code 35% less often than in 2023. Refactored code fell from 21% of changed lines in 2022 to 3.8% year-to-date in 2026: "New code is less and less woven into the existing codebase. Instead, it is isolated in self-contained files" ([GitClear, 2026](https://www.gitclear.com/the_ai_code_quality_maintainability_gap)). Böckeler saw the same behavior: agents "usually don't go ahead and start refactoring without an explicit nudge when they repeat a piece of code for the third or fourth time, they are quite happy to copy and paste" ([Böckeler, May 2026](https://martinfowler.com/articles/sensors-for-coding-agents.html)). The reviewer runs out of room first: "I don't have the cognitive capacity to stay on top of 100 times the amount of code" ([Willison, August 2026](https://simonwillison.net/2026/Aug/19/conceptual-integrity-and-counting-lines-of-code/)).

## When this backfires

These conditions make paying for coherence a bad trade.

- The code is disposable. Phillip Mortimer's QCon London position is the honest opposite of this page: keep the tests, throw away the implementation, have it written again ([InfoQ, August 2026](https://www.infoq.com/news/2026/08/code-AI-write-only-disposable/)). On a spike he is right.
- The codebase still fits in one head. Below that ceiling the owner spots the odd room on the next pass.
- The design is not settled. Freezing layer rules before you understand the domain is premature commitment.
- The structural checks misfire. The LLM analysis of Böckeler's coupling data flagged a deliberate dependency-injection factory and a shared schema contract as defects, and she warns of "feedback overload for the agent, sending it into a spiral of over-engineered refactorings" ([Böckeler, May 2026](https://martinfowler.com/articles/sensors-for-coding-agents.html)).

## What to do instead

- Say no on purpose. The week that used to reject a feature is gone, so someone has to reject it out loud.
- Encode structure as a check, not a guide file. Böckeler's `dependency-cruiser` layer rules carried the layering concept in their error text, and the agent self-corrected against them. She calls the rules "quite a useful replacement for describing code structure in a markdown guide" ([Böckeler, May 2026](https://martinfowler.com/articles/sensors-for-coding-agents.html)).
- Track files-per-change as a drift signal, and review the design on a schedule rather than only per diff. Whole-system drift is invisible to per-diff review.

## Key Takeaways

- The discipline that protected system design was the time a feature cost. Agents removed it, and nothing took its place.
- The argument predicts the failure worsens as agents improve, because it turns on cost rather than on output quality.
- The first observable symptom is a small change touching more files than it should, not a bad-looking diff.
- On short-lived or single-owner code the opposite position holds, and paying for coherence is waste.

## Related

- [Comprehension Debt](comprehension-debt.md) — the gap between agent-produced code and developer understanding; the counterpart in people rather than in system design
- [Abstraction Bloat](abstraction-bloat.md) — over-production inside one change, as against drift across many
- [Shadow Tech Debt](shadow-tech-debt.md) — architectural drift accumulating where agents lack structural understanding of the codebase
- [The Reasoning-Complexity Trade-off](reasoning-complexity-tradeoff.md) — stronger models produce more coupled code, so capability gains buy maintainability losses
- [Cognitive Load and AI Fatigue](../../human/cognitive-load-ai-fatigue.md) — the reviewer-side ceiling that decides when this erosion starts to bite
