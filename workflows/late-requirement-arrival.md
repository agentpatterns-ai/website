---
title: "Late Requirement Arrival in Agent Sessions"
description: "A requirement arriving after the agent's first edit is followed by about twice the deletion of prior agent code, and only the content half of the obvious fix has evidence behind it."
term: "Late Requirement Arrival"
aliases:
  - late requirement emergence
  - post-implementation requirement arrival
tags:
  - workflows
  - agent-design
  - human-factors
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-05
maturity: emerging
---

# Late Requirement Arrival in Agent Sessions

> A requirement that arrives after the agent's first edit is followed by about twice the deletion of prior agent code as an ordinary edit.

Across 3,553 eligible SWE-chat sessions, 18% to 22% of clean-start sessions carry at least one detected requirement that surfaced after implementation had started, and 54.0% of emergence events fall after the session midpoint. In the primary canonical matched analysis, 452 events average 57.5 invalidated lines of prior agent-written code against 29.4 for their set-weighted controls, a ratio of 1.96 (95% repository-bootstrap CI [1.31, 2.82]) or 28.2 additional lines [+10.1, +44.4] ([Jiang et al., 2026](https://arxiv.org/abs/2609.03028v1)).

## What the finding covers

The comparison is associational. The authors rematched on live lines and absolute edit index, and they state that "matching cannot remove unmeasured task-phase confounding or establish that a deletion semantically implements the arriving requirement" ([Jiang et al., 2026](https://arxiv.org/abs/2609.03028v1)). 1.96 is the size of a correlation. It is not a quantity of waste anyone has shown you can recover.

Three limits bound how much of that deletion is really requirement rework:

- A fixed-seed semantic audit of 150 sampled events returned 147 judgments: 55% requirement-driven, 31% incidental, 14% unclear ([Jiang et al., 2026](https://arxiv.org/abs/2609.03028v1)). About a third of the audited events had another cause.
- Most arrivals do not contradict what came before. 89.3% are neutral to the prior requirement ledger and 14.5% are destructive. Of 698 events with resolved operation labels, `constrain` is the most frequent at 340, ahead of `add` at 224 ([Jiang et al., 2026](https://arxiv.org/abs/2609.03028v1)).
- The reconstruction log reports a retention rate of approximately 58%, and the authors treat the observational sample as "a characterized convenience sample" they do not claim is representative of all eligible sessions ([Jiang et al., 2026](https://arxiv.org/abs/2609.03028v1)).

## Why it works

The measurement links each arrival to a proxy: deletion or replacement of prior agent-authored lines. `constrain` is the most frequent arriving operation, and constraints land on code the agent has already written ([Jiang et al., 2026](https://arxiv.org/abs/2609.03028v1)). The paper stops short of the obvious next step, stating that its design cannot "establish that a deletion semantically implements the arriving requirement" ([Jiang et al., 2026](https://arxiv.org/abs/2609.03028v1)). So the association is measured; the mechanism behind it is not.

Two controlled experiments in the same paper separate the timing lever from the anticipation lever, and only one of them moves. Delaying the reveal of an identical requirement relocated implementation into the post-reveal round, and advance warning carrying no requirement content produced no detected effect on overwriting ([Jiang et al., 2026](https://arxiv.org/abs/2609.03028v1)). What relocates the work is the content of the requirement. Knowing that one is coming does nothing measurable.

Elicitation that carries content has independent support. An uncertainty-aware multi-agent scaffold that "decouples underspecification detection from code execution" reached a 69.40% task resolve rate on an underspecified variant of SWE-bench Verified, closing the performance gap with agents given fully specified instructions ([Edwards and Schuster, 2026](https://arxiv.org/abs/2603.26233v2)).

## Where to spend the pre-edit turn

The practice below is tool-agnostic; nothing in it depends on Claude Code, Copilot, or Cursor specifics. The human gate sits between the task statement and the agent's first write.

1. Ask for constraints by name, not for confirmation. `constrain` is the operation that arrives most often, so "what must this not do, and what must it preserve" targets the majority case ([Jiang et al., 2026](https://arxiv.org/abs/2609.03028v1)).
2. Put the answers in the task, not in a warning. The arm that told the agent to expect a change, without saying what it was, moved overwriting by +0.16 lines with an interval spanning zero ([Jiang et al., 2026](https://arxiv.org/abs/2609.03028v1)).
3. Stop when the questions stop returning constraints. Just over half of arrivals land after the session midpoint, where the user is reacting to output rather than recalling a rule, and that half is not reachable from before the first edit ([Jiang et al., 2026](https://arxiv.org/abs/2609.03028v1)).

## When this backfires

Front-loading requirements costs the user's attention, and it does not always buy anything back.

- The requirement is reactive by construction. The paper's own framing is that stakeholders cannot express a constraint until part of the system exists to react to ([Jiang et al., 2026](https://arxiv.org/abs/2609.03028v1)). No pre-edit questioning surfaces a requirement the user forms by reading output.
- The intervention carries no content. Warning the agent that requirements may change measured +0.16 lines [−0.56, +1.06] ([Jiang et al., 2026](https://arxiv.org/abs/2609.03028v1)). Ask for the constraint itself or skip the step.
- The affected code is small. Invalidation here runs to tens of lines. A checkpoint costing more minutes than regeneration would is a net loss.
- The checkpoint is framed around what might have to be undone. Since 89.3% of arrivals leave the prior ledger intact, that framing targets the destructive minority and misses the `constrain` majority ([Jiang et al., 2026](https://arxiv.org/abs/2609.03028v1)).
- The budget is set from the raw ratio. With 31% of audited events judged incidental, planning against a full 1.96 over-states what elicitation could recover ([Jiang et al., 2026](https://arxiv.org/abs/2609.03028v1)).

The paper labels the fix as unfinished work: "A natural follow-on is a specification-checkpoint intervention that prompts elicitation before the first edit, which we develop as future work sized by the effect estimates reported here" ([Jiang et al., 2026](https://arxiv.org/abs/2609.03028v1)). Nobody has yet measured a specification checkpoint reducing this number.

## Example

The two experimental arms show which half of a checkpoint has evidence behind it. Both arms used two rounds, the same number of model calls, and the same token budget, differing only in what round 1 received.

In the delayed-disclosure arm, round 1 got the base task and round 2 got the addition. Round-2 churn rose to 9.3 lines against 0.1 when both parts arrived upfront. Cumulative two-round churn was lower under delay, by 4.4 lines [−7.9, −1.6], and the authors note that evidence about cumulative work is limited to the one instrumented backend ([Jiang et al., 2026](https://arxiv.org/abs/2609.03028v1)).

In the advance-warning arm, both arms implemented the identical addition in round 2, and round 1 differed only in whether the agent was told an addition was coming. Overwriting of prior code changed by +0.16 lines, an interval spanning zero ([Jiang et al., 2026](https://arxiv.org/abs/2609.03028v1)).

One arm changed where the work happened. The other changed nothing, and it is the one that a "requirements may change" preamble resembles.

## Key Takeaways

- Budget for late requirements in about one session in five rather than treating each one as a planning failure. They keep arriving well past the point where a plan is settled.
- When you spend a pre-edit turn, spend it eliciting a constraint, not announcing that constraints may follow. Only the content arm moved the number.
- Discount the 1.96 ratio before planning against it. A third of the audited events were judged incidental, and the design is associational.
- The specification checkpoint this evidence points at has not been tested. Treat it as a hypothesis you are running, and watch your own deletion counts rather than assuming the saving.

## Related

- [The Plan-First Loop: Design Before Code](plan-first-loop.md) — the design-before-code practice this measurement prices
- [Interactive Clarification for Underspecified Tasks](../patterns/agent-design/interactive-clarification-underspecified-tasks.md) — what asking buys on resolution rate, measured separately
- [Issue Requirements Preprocessing](../patterns/agent-design/issue-requirements-preprocessing.md) — structuring the initial issue before generation starts
- [Assumption Propagation](../patterns/anti-patterns/assumption-propagation.md) — the failure mode when the agent fills a gap instead of asking
- [Spec-Driven Development with Spec Kit](spec-driven-development.md) — holding intent in a durable artifact across sessions
