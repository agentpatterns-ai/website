---
title: "Decision Pins: Confirm an Acceptance Example Discriminates"
term: "Decision Pin"
description: "Name the point your requirement leaves open, run two implementations that differ only there, and keep the input where they disagree as the check."
tags:
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - decision pin
  - distinguishing input
  - execution-confirmed acceptance example
last_reviewed: 2026-10-05
maturity: emerging
---

# Decision Pins: Confirm an Acceptance Example Discriminates

> An acceptance example settles an ambiguity only when the two readings disagree on it, and nothing in the usual practice checks that they do.

A decision pin is an acceptance example whose discriminating power has been confirmed by execution. Name the point the requirement leaves open, write two throwaway implementations differing only at that point, and keep a candidate input only if running both produces different results. You record the named point, that input, and the result you picked ([Mitsui, 2026](https://arxiv.org/abs/2610.03237v1)).

Confirming the input earns its cost on two conditions: the decision will be checked or asked again, and its scope resists a clean one-sentence statement. Otherwise a prose rule stating that scope did as well.

## The example you wrote probably settles nothing

"Compute the volume of a sphere from its radius" does not say what a negative radius means. Choose `volume_sphere(3.5)` and both readings agree, so the question survives the test. Choose `volume_sphere(-2)` and they split: raise-on-negative gives a `ValueError`, use-the-value-as-given gives `-33.51` ([Mitsui, 2026](https://arxiv.org/abs/2610.03237v1)).

The generated suite does not catch it either. Across 600 suites from three models, "42.7 percent contain no test that distinguishes the competing readings of the decision point at all" ([Mitsui, 2026](https://arxiv.org/abs/2610.03237v1)).

## Why it works

Discriminating power belongs to the pair of readings, not to the example, so only running both decides it. Models handle the naming half and stumble on the input. Enumeration alone reached the injected decision point in 77.5% to 90.0% of benchmark tasks. Asked for an input separating a point it has just named, "a model frequently supplies one that does not" ([Mitsui, 2026](https://arxiv.org/abs/2610.03237v1)). Adding the execute-both check raised both models to 92.5%, rescuing six tasks on one and one on the other.

Sampling the model a few times and watching for disagreement fails. Under an underspecified requirement models "collapse onto a single incorrect interpretation of the task description, consistently generating coherent but behaviorally misaligned code" ([Richter and Papadakis, 2026](https://arxiv.org/abs/2607.01953v1)). A constructed contrast does not wait for disagreement to appear; [semantic collapse](../patterns/anti-patterns/semantic-collapse.md) carries the measured rates.

The payoff lands on checking. As acceptance checks over 703 independently generated implementations, pins agreed with the benchmark's own classification on 96% to 97%. Handed back as a constraint, the same record was honored at the input it names in all 210 generations ([Mitsui, 2026](https://arxiv.org/abs/2610.03237v1)).

## When this backfires

- You can state the scope in prose. Every prose-rule compliance failure in the study came from a rule that does not say which inputs it applies to. The study pre-registered the claim that pins beat prose rules for adherence: "Our pre-registered criterion required the pin to beat the prose rule on both models, and it does not." A rule with explicit scope matched the pin in all 19 cells compared ([Mitsui, 2026](https://arxiv.org/abs/2610.03237v1)).
- The pair differs in more than the point you named. Execution proves two implementations disagree, not that they disagree about your decision. Only 34 of 40 and 36 of 40 tasks (85% to 90%) ended with a pin on the intended decision. On one task the recorded value came from a candidate wrong in an unrelated dimension, and the pin rejected ten compliant implementations ([Mitsui, 2026](https://arxiv.org/abs/2610.03237v1)).
- The behavior is not visible in one call. A pin compares one observation against one recorded value. With exception types normalized, an accidental `IndexError` scored the same as a deliberate raise ([Mitsui, 2026](https://arxiv.org/abs/2610.03237v1)).
- Either reading would do. Choosing between the two results needs a person. The author reports they "have not measured the human cost of step (3), nor the cost of maintaining a store over time" ([Mitsui, 2026](https://arxiv.org/abs/2610.03237v1)).
- The decision lives above function scale. "The tasks are small. Forty functions derived from MBPP. A decision point in a forty-line function is not a decision point in a system, and nothing here speaks to the latter" ([Mitsui, 2026](https://arxiv.org/abs/2610.03237v1)).
- The store grows. A rule reading "invalid input must raise" swallowed a recorded decision to preserve a float's numeric type, turning `29.75` into a `TypeError` on both models. Asked to reconcile the two rules by their text, "neither model named the invalid-input rule, in five attempts out of five" ([Mitsui, 2026](https://arxiv.org/abs/2610.03237v1)). That is one pair, and the benchmark's tasks share no code, so conflict frequency at scale stays unmeasured. A broader warning agrees: "simply specifying all requirements does not consistently help, as models have limited instruction-following ability and requirements can conflict" ([Yang et al., 2026](https://arxiv.org/abs/2505.13360v3)).

## Example

Requirement: "Find the smallest number in a list." The open point is whether the function may reorder its argument.

**Before** — an example that settles nothing. Asked for an input distinguishing the two readings, a model proposes `smallest_num([3,1,2])`, "which is the same under both readings" ([Mitsui, 2026](https://arxiv.org/abs/2610.03237v1)), because both return 1. You keep it as `assert smallest_num([3,1,2]) == 1`. The implementation sorts in place, the caller's list is reordered, and the test stays green.

**After** — confirm the input first. Write two candidates differing only in that treatment, one sorting the argument in place and one copying it before sorting. Then fix what you observe: for a mutation decision that is the argument's state after the call, not the return value. Run both on `[3,1,2]`. The in-place candidate leaves `[1,2,3]` and the copying candidate leaves `[3,1,2]`, so the pair disagrees and the input is kept. You pick the copying result, and the record is the named point, that input, and that state. It goes back into the prompt and into the suite as one artifact.

## Key Takeaways

- Confirm by execution that your acceptance example separates the readings. In 600 generated test suites, 42.7% contained no test that did ([Mitsui, 2026](https://arxiv.org/abs/2610.03237v1)).
- Construct the contrast instead of sampling for it, because models collapse onto one reading rather than diverging ([Richter and Papadakis, 2026](https://arxiv.org/abs/2607.01953v1)).
- The evidence supports the record as a check, at 96% to 97% agreement over 703 implementations, and not as better steering: scope-explicit prose matched it in all 19 cells compared ([Mitsui, 2026](https://arxiv.org/abs/2610.03237v1)).
- A confirmed input may still pin something other than the point you named. The pin identified the intended decision for 85% to 90% of tasks, not all ([Mitsui, 2026](https://arxiv.org/abs/2610.03237v1)).
- Write the scope down whichever form you choose, because every prose-rule compliance failure in the study came from a rule that left its own scope open ([Mitsui, 2026](https://arxiv.org/abs/2610.03237v1)).

## Related

- [Test-Driven Intent Clarification: Tests as Intermediate Alignment Artifacts](test-driven-intent-clarification.md) — Ranks generated tests by how they split sampled candidates; this page names the point first and builds the contrast for it.
- [Semantic Collapse Under Underspecified Prompts](../patterns/anti-patterns/semantic-collapse.md) — Why sampling a model for disagreement does not surface the decision.
- [Probing Unstated Constraints in Generated Code (Intent Violation Rate)](unstated-constraint-probes.md) — Measures what a stated suite still misses once the named decisions are settled.
- [Ambiguity Stability as a Model-Selection Criterion](ambiguity-stability-model-selection.md) — Chooses a model by how far it falls on requirements with more than one reading.
- [Test-Driven Agent Development: Tests as Spec and Guardrail](tdd-agent-development.md) — The practice this inserts two steps into, for the case where the spec is already settled.
