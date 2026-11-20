---
title: "Eliciting Requirement Deviations Before the First Edit"
term: "Specification Satisficing"
description: "An elicit-then-recheck step before the first edit raised DeepSWE pass@1 by 3.8 to 6.0 points on three models. Gains are small and reverse when an agent reports many deviations."
tags:
  - testing-verification
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - requirement deviation elicitation
  - SatisFix
  - elicit then reconsider
last_reviewed: 2026-11-19
maturity: emerging
---

# Eliciting Requirement Deviations Before the First Edit

> Before its first edit, ask a coding agent to report where it read a requirement loosely, then recheck each choice against the task text.

On DeepSWE v1.1 (113 tasks, four runs each), the SatisFix method raised pass@1 from 44.25 to 50.22 with GPT-5.6-Luna, from 53.32 to 57.08 with DeepSeek V4 Flash, and from 42.26 to 47.79 with Qwen3.8-27B ([Wang and Zhang, 2026](https://arxiv.org/abs/2611.16289v1), Table 3). The paper writes these gains as "%". They are percentage points, and its 5.09 average covers these three models only.

Limits:

- The paper reports no significance test.
- The ablation uses single first runs. One task is 0.885 points.
- The paper publishes no prompt text, so this page paraphrases the method.

## The failure

The paper names it: "the agent considers an implementation choice that meets a requirement, but later decides to commit to another one that does not meet the requirement for a reason it finds acceptable" (abstract). Its four reason types are intended reinterpretation, narrowed scope, lowered standard and perceived conflict (Table 1).

In one DeepSWE task (mini-swe-agent, DeepSeek V4 Flash), an agent wrote that a merge was "arguably not 'preserving', but likely acceptable". It failed 2 of 69 tests. With the method it passed all 69 (§2). This is one task, not a rate.

## The method

1. A message framed as coming from the task's maintainers asks the agent, as an advisor, where it concluded a requirement could be handled differently. It asks for the requirement, the choice and the reason, and does not ask for a judgment (§3.1).
2. A second message says the maintainers will not revise the task. The agent lists alternatives and a plan to check each reported choice against the task text and repository, then carries out the plan (§3.2).

The method runs once, just before the agent writes code. The next message retracts the maintainer framing (Ethical Considerations).

## What the numbers show

- Baselines (DeepSWE, GPT-5.6-Luna, mini-swe-agent, four runs): Self-Refine 46.24±3.98, ProgCo 46.24±1.82, DeCRIM 44.25±2.61, base 44.25±2.98, method 50.22±2.64 (Table 2). The 3.98-point gap to the best baseline equals Self-Refine's standard deviation.
- Hard subset of SWE-bench Pro (51 tasks, reported without a standard deviation): gains of 3.92 to 11.77 points, or 2 to 6 tasks. On the full 642 tasks the gains are 0.16 to 3.27 points. Three models solve over 92% of the tasks outside the hard subset with either method (Table 3).
- Ablation (Luna, DeepSWE, first runs): full method 49.6, without elicitation 43.4, without reconsideration 47.8, a generic self-check that repeats the task text 44.2, base 43.4 (Table 5).
- Cost (Luna, mini-swe-agent): 58.6 steps against 49.0, and $0.897 against $0.644 per task (Table 2). DeepSeek's token cost fell 14.0% (§4.3).

## Counts, and a reversal

Two LLM annotators labeled each report item. For Luna, 90 items in 61 of 113 tasks reported satisficing. For DeepSeek it was 227 items in 105 tasks (§5.1). These label what the agent reported, not whether the code deviates, and the counts cover passing and failing tasks alike.

With DeepSeek, the method scored 67.6% against the base's 51.1% on 68 tasks with one or two reported items. On the 36 tasks with three or more it scored 44.4% against 54.2% (§5.2). The method is one run and the base is a four-run mean.

## What to do

Before the first edit, add one turn asking the agent to list each place it decided a requirement could be handled differently from the task text: requirement, choice, reason. Add a second turn saying the task text is unchanged and asking it to check each item before coding. Keep the list as a review artifact. Sending the list to a human reviewer, which drops the fictitious framing, is an extension the paper did not test.

## When this backfires

- The agent reports many deviations. The DeepSeek reversal above is the evidence.
- Base rates are high. Gains on full SWE-bench Pro stayed under 3.3 points.
- The model is weak. Two of five models hit a capability floor on DeepSWE (§4.3).
- Choices come later. The method fires once, so later deviations go unelicited (Limitations).
- A harness forbids fictitious messages. The authors "do not measure whether this changes how the coding agent treats later messages".

## Key Takeaways

- Reporting a deviation without judging it helped. Re-reading the task text alone did not (44.2 against base 43.4, single runs).
- Read every figure here as points, on one paper and one group.
- Log the elicited list, because it is a reviewable artifact.

## Related

- [Assumption Propagation](../patterns/anti-patterns/assumption-propagation.md)
- [A Separate Critic Over Completion-Time Self-Checking](separate-critic-over-self-recheck.md)
- [Interactive Clarification for Underspecified Tasks](../patterns/agent-design/interactive-clarification-underspecified-tasks.md)
- [Zero-Decision Plans Alternatives Rule](../instructions/zero-decision-plans-alternatives-rule.md)
- [Interpretive Lock-In in Revision Loops](../patterns/anti-patterns/interpretive-lock-in-revision-loops.md)
- [Self-Review Modernization Failure](../patterns/anti-patterns/self-review-modernization-failure.md)
- [Judge Agreement Is Not Correctness](judge-agreement-is-not-correctness.md)
