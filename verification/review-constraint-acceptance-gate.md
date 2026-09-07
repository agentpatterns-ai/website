---
title: "Review Constraint Tests as a Second Acceptance Gate"
term: "Review Constraint Gate"
description: "A functional suite built from the bug report cannot see a constraint separable from it, so run review-derived constraints as a second executable suite scored on its own."
tags:
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - review constraint gate
  - constraint compliance test suite
  - hidden failure rate
last_reviewed: 2026-09-06
maturity: emerging
---

# Review Constraint Tests as a Second Acceptance Gate

> An agent patch that passes the functional suite can still violate a stated review constraint, so the constraint needs its own executable gate.

A functional suite built from a bug report checks that the reported behavior is fixed, and nothing else. What a maintainer raises in review sits outside it: preserving backward compatibility, maintaining established exception semantics, following repository-specific implementation conventions ([arXiv:2609.04167v1](https://arxiv.org/abs/2609.04167v1)). Run those as a second executable suite, scored separately, and they become a gate instead of a comment. On the SWE-Gate benchmark, 644 agent patches passed the functional tests and only 423 passed both suites. The other 221, 34.3% of every functional success, would have cleared a protocol watching only the functional side ([arXiv:2609.04167v1](https://arxiv.org/abs/2609.04167v1), Table 3).

Take 34.3% as evidence the gap exists, not as a rate for your codebase. The 303 instances span 75 Python repositories, the bugs are injected mutants, and the pipeline "mitigates direct solution memorization without claiming to eliminate all training-data contamination" ([arXiv:2609.04167v1](https://arxiv.org/abs/2609.04167v1)). Selecting instances for separability pushes the rate up by construction.

## Conditions this holds under

Three things have to be true, and the first is the one teams get wrong.

The constraint has to be separable from the fix. SWE-Gate discards a candidate task when "every plausible functional repair would necessarily satisfy the constraint, or the functional and constraint dimensions cannot be validated separately" ([arXiv:2609.04167v1](https://arxiv.org/abs/2609.04167v1)). A constraint that any reasonable patch meets is a suite green on arrival.

Nothing cheaper already enforces it. Check what your type checker, public-API diff, and deprecation lint already reject on every commit, and write a bespoke test only for what they miss.

The constraint has to be expressible as an executable assertion. Naming and design taste sit outside the mechanism: the authors list requirements that "cannot yet be expressed as executable tests" as open work ([arXiv:2609.04167v1](https://arxiv.org/abs/2609.04167v1)).

## What a constraint suite catches

The constraints come from real pull request review comments and carry multiple labels each, so the counts overlap and do not sum. Compliance is the share of functionally successful patches that also satisfy the constraint, across the three stronger backends ([arXiv:2609.04167v1](https://arxiv.org/abs/2609.04167v1), Table 5).

| Constraint category | Instances | Compliance after functional success |
|---|---|---|
| Error semantics | 152 | 66.4–72.8% |
| Schema, metadata, typing | 143 | 60.7–68.3% |
| Ordering and argument preservation | 86 | 75.0–79.6% |
| Encoding, escaping, quoting | 74 | 51.1–68.3% |
| Scope generalization | 62 | 46.3–63.0% |
| Compatibility and deprecation | 55 | 71.0–77.1% |
| Missing versus empty or sentinel | 51 | 74.2–81.6% |
| Performance and structure | 41 | 71.0–78.6% |
| Idempotence and duplicate processing | 30 | 71.4–72.2% |
| Lifecycle cleanup and resource release | 19 | 53.8–62.5% |

The spread is the useful part. Scope generalization and lifecycle cleanup sit at the bottom because they "demand coverage beyond the immediate failure or preservation across a resource lifecycle, making them difficult to satisfy with a narrowly localized patch" ([arXiv:2609.04167v1](https://arxiv.org/abs/2609.04167v1)). One aggregate compliance number averages that shape away.

## What stating the constraint buys, and what it costs

Every number above comes from runs where the agent received the constraint in natural language before writing the patch. Telling it helps and does not close the gap: hidden failure rates under that condition still run from 29.5% for GPT-5.5 to 53.6% for GPT-4o-mini ([arXiv:2609.04167v1](https://arxiv.org/abs/2609.04167v1), Table 3).

It also costs throughput. Supplying the constraint raised compliance by 10.2 to 25.6 points and lifted joint successes from 360 to 423. Functional success fell for every model over the same ablation: 0.7 points for GPT-5.5, and 3.3 to 9.9 points for the other three ([arXiv:2609.04167v1](https://arxiv.org/abs/2609.04167v1), Table 4). The authors offer one possible explanation, that the extra requirement steers the agent "away from a simpler functionally adequate patch", and decline to call it causal, because each condition holds one generation per model and instance. Budget for the trade rather than the explanation.

## Why it works

The gap is structural. A repository-level functional suite "is typically provided with the PR and mainly assesses whether the reported issue has been functionally resolved" ([arXiv:2609.04167v1](https://arxiv.org/abs/2609.04167v1)), so it can only witness behavior the issue named. Every SWE-Gate instance ships a non-compliant patch that passes the functional test and fails the constraint test. A constraint separable from the issue is invisible to an issue-derived suite by definition. No amount of extra coverage on the functional axis reaches it, so the fix is a second oracle rather than more tests of the first kind.

Why an agent violates a constraint it was handed is a different question, and the paper does not answer it.

## When this backfires

- Functional throughput is already the binding constraint. Losing up to 9.9 points of functional success to gain compliance is the wrong trade for a team whose agent patches mostly fail on the functional side.
- Your review archive is thin. Across 654 rejected agent pull requests, 67.9% carried no explicit reviewer comment ([arXiv:2602.04226v1](https://arxiv.org/abs/2602.04226v1)), so the seam you are mining for constraints may be narrower than it looks.
- You mine the seeds from a review agent instead of trusted humans. Of closed pull requests reviewed only by code review agents, 60.2% fell in the 0–30% signal band, and 12 of 13 agents averaged below 60% signal ([arXiv:2604.03196v1](https://arxiv.org/abs/2604.03196v1)). Constraints derived from that stream encode noise as policy.

## Example

A Pydantic pull request added conditional serialization for extra fields by introducing a new core-schema representation. The behavior worked. A reviewer pointed out that changing the public interface would be breaking and asked for an `extras_ser_exclude_if` parameter instead, which the contributor adopted ([arXiv:2609.04167v1](https://arxiv.org/abs/2609.04167v1)).

The two requirements test separately. A functional test checks that qualifying extra fields are omitted from serialized output. A compatibility test checks that the existing public schema is unchanged and still usable by code written against the previous format. The first implementation passes the first test and fails the second, which is the whole shape of the problem in one patch.

## Key Takeaways

- Score constraint compliance as a separate number from functional pass rate. A single joint success rate hides which axis failed.
- Admit a constraint to the suite only if a plausible functional fix could violate it. That test is what keeps the gate honest.
- Handing the agent the constraint raises compliance by 10.2 to 25.6 points and costs up to 9.9 points of functional success, so decide which side you can afford to lose.
- Start the suite on scope generalization and lifecycle cleanup, where compliance after functional success runs at 46.3–63.0% and 53.8–62.5%.

## Related

- [Probing Unstated Constraints in Generated Code (Intent Violation Rate)](unstated-constraint-probes.md) — the same gap for constraints the prompt never stated, at single-function scale
- [Preempting Agentic PR Rejection by Failure-Mode Category](../code-review/preempting-agentic-pr-rejection.md) — writing team conventions into the instruction file, which this page prices
- [Review-Comment-Derived Benchmarks for Code Review Agents](review-comment-derived-benchmarks.md) — how to curate the review archive the constraint seeds come from
- [Non-Compensatory Readiness Gates Before Agent Release](non-compensatory-readiness-gates.md) — combining several evidence axes without letting one average away another
- [CRA-Only Review and the Merge Rate Gap](../code-review/cra-merge-rate-gap.md) — why a review agent's comment stream is a poor source of constraint seeds
