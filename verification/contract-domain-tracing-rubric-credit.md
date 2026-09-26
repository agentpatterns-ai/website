---
title: "Contract-Domain Tracing for Rubric Credit"
term: "Contract-Domain Tracing"
description: "A rubric domain scoring full credit on every decision is not a verified domain: label each criterion with the contract requirement it tests, then run that requirement on its boundary value."
tags:
  - testing-verification
  - evals
  - tool-agnostic
  - arxiv
aliases:
  - contract-stratified rubric analysis
  - criterion-to-contract mapping
  - tracing eval reward to contract domains
last_reviewed: 2026-09-25
maturity: emerging
---

# Contract-Domain Tracing for Rubric Credit

> Every decision in the rubric's safety and boundary domain took full credit. A containment guard inside it accepts the parent directory.

Contract-domain tracing labels each rubric criterion with the version-contract requirement it claims to check, then tests that requirement instead of reading the score built from it. Liu and colleagues traced a shipped plugin-upgrade skill across 64 archived reports and 328 criterion decisions. The defect they found sat in a domain the original judge had scored at full credit in both arms ([Liu et al., 2026, §5.2](https://arxiv.org/abs/2609.30120v1)).

## When tracing earns its cost

Four conditions have to hold together.

- The eval grades advice, not an executed repair. Describing a test can satisfy a static diagnosis task without establishing that the test ran ([Liu et al., 2026, §4.1](https://arxiv.org/abs/2609.30120v1)). Where the harness runs the repair in a version-pinned environment, the tests already answer the contract question.
- The scores sit near a ceiling. The original judge gave full credit to 300 of 328 decisions, and eight of 16 task pairs scored 100 in both arms ([Liu et al., 2026, §5.1, §5.3](https://arxiv.org/abs/2609.30120v1)). A score with that little room cannot record a defect by moving.
- You will re-grade both arms. Corrections here pull in opposite directions. Replacing the S11 with-skill decision alone drops the gain from 4.92 to 4.61 points and moves its interval across zero; adding the S6 no-skill correction lifts it to 5.39 with a lower endpoint at zero ([Liu et al., 2026, §5.1, §5.3](https://arxiv.org/abs/2609.30120v1)).
- The criterion names something you can run. A containment predicate, a timer, a version range: all executable. "Explains the migration clearly" is not.

## What the trace found

Every criterion took one primary contract domain, assigned before the counts were produced ([Liu et al., 2026, §4.4](https://arxiv.org/abs/2609.30120v1)).

| Primary domain | Criteria per arm | Full credit, no skill | Full credit, with skill |
|---|---|---|---|
| Version and release applicability | 12 | 8 | 12 |
| API, data and ownership contracts | 46 | 35 | 45 |
| Lifecycle, ordering and deployment | 26 | 24 | 25 |
| Safety and boundary handling | 10 | 10 | 10 |
| Failure attribution | 32 | 32 | 32 |
| Evidence, verification and provenance | 38 | 31 | 36 |

Safety and boundary handling reads as settled at 10 of 10 in both arms. Inside it, a with-skill answer proposed a relative-path check that rejects any path prefixed by two dots and a separator. The exact path `..` passes that test, and it denotes the parent directory ([Liu et al., 2026, §5.2](https://arxiv.org/abs/2609.30120v1)). The original judge awarded full containment credit anyway. Reviewers then extracted the predicate, removed only its TypeScript annotations, and ran seven declared lexical inputs under each of Node's POSIX and Windows path algorithms. It contradicted the declared containment expectation in 2 of 14 diagnostic inputs, with the other 12 controls behaving as expected ([Liu et al., 2026, §4.5](https://arxiv.org/abs/2609.30120v1)).

Some findings indict the rubric instead. On task S18 the with-skill answer proposed explicit host teardown and kept partial credit, because the rubric required timers that do not hold a still-mounted probe host alive. A reconstruction in separate Node child processes showed that explicit unmount with cancellation also exits naturally, so the partial credit measured noncompliance with a narrower rubric rather than a broken repair ([Liu et al., 2026, §5.2](https://arxiv.org/abs/2609.30120v1)). Confusing that with a bad predicate sends you to rewrite advice that already worked.

## Running the trace

1. Map every criterion to one primary contract domain before you look at any counts, one label each so credit is not counted twice ([Liu et al., 2026, §4.4](https://arxiv.org/abs/2609.30120v1)).
2. Count full-credit decisions per domain per arm with the denominator beside each count. A domain sitting at its denominator is where to look next.
3. Extract the artifact proposed under the criteria whose requirement is executable. Strip type annotations, not logic.
4. Run it on the boundary value, plus ordinary cases as controls. The parent path is the counterexample a containment check needs; descendants confirm the probe works.
5. Re-grade both arms and keep the original decisions beside the replacements ([Liu et al., 2026, §4.2](https://arxiv.org/abs/2609.30120v1)).
6. State which endpoint the eval measures: locating knowledge, giving contract-consistent advice, or completing a verified repair ([Liu et al., 2026, §6.3](https://arxiv.org/abs/2609.30120v1)).

## Why it works

Recorded reward is a weighted sum over judge decisions. A pass takes a criterion's full weight, a partial takes half, and a deterministic scorer turns the decisions into a 0-100 number ([Liu et al., 2026, §4.1](https://arxiv.org/abs/2609.30120v1)). Each decision is a text-level call about whether a report satisfies a criterion, so a defect that survives a careful reading of the report enters the sum at full weight. Naming the contract requirement behind a criterion converts that call into something runnable, which is how the parent-directory escape became observable.

Re-judging cannot substitute, because a panel inherits the rubric. Three judges here returned gains of 4.92, 10.63 and 6.09 points, agreeing with the original judge on 91.8% and 95.7% of decisions at linearly weighted kappa of 0.64 and 0.72. The study reads that as sensitivity to judge configuration, and says the shared rubric's validity is not established by their agreement ([Liu et al., 2026, §5.3](https://arxiv.org/abs/2609.30120v1)). Judges often fail to update when the criterion itself is reversed, and classifiers trained on rubric text alone, with no access to any response, predict judge outputs to a nontrivial degree ([arXiv:2609.02942v1](https://arxiv.org/abs/2609.02942v1)). Agreement measures whether judges read the rubric the same way. It says nothing about a requirement the rubric never asks about.

## When this backfires

- You need an error rate. The bounded review found three criterion disagreements in two of ten answers, from a purposive sample. The authors read those as weaknesses in the measurement rather than a rate ([Liu et al., 2026, §5.2](https://arxiv.org/abs/2609.30120v1)).
- A judge panel answers your actual question for less. A panel of smaller diverse models outperformed a single large judge with less intra-model bias at over seven times less cost ([arXiv:2404.18796v2](https://arxiv.org/abs/2404.18796v2)). Both blinded re-judgments here kept positive intervals where the manual replacements touched or crossed zero, so the expensive pass produced the weaker conclusion.
- Your reviewers are not independent. This study's review was AI-assisted, non-blind, seeded by the decisions it was auditing, and done by contributing plugin authors ([Liu et al., 2026, §4.2](https://arxiv.org/abs/2609.30120v1)).
- One task carries the result, which is cheaper to check than a trace. S1 alone gained 42.5 points, and removing it left 2.42 points across the other 15 tasks ([Liu et al., 2026, §5.1](https://arxiv.org/abs/2609.30120v1)).

## Key Takeaways

- A domain at 100% full credit tells you only that the judge found nothing. Treat its denominator as a place to look.
- Read a criterion as a claim about a runnable requirement, and run it. Anything you cannot run yields another opinion.
- Re-grade both arms, or the correction is a direction you chose.
- Skip the trace when the harness executes the repair, or when a judge panel settles the direction for less.

## Related

- [Skill Lift: Measuring What a Skill Adds at Runtime](skill-lift.md) — how to get the paired with-versus-without delta this page then reads against the contract.
- [Meta-Evaluate the LLM Judge Before Trusting Rubric Verdicts](meta-evaluate-llm-judge-rubric-verification.md) — measuring a judge's error rate against human labels, the sibling control to tracing its decisions.
- [Choosing the Judge Model That Grades Your Agent Evals](judge-model-bake-off.md) — what a cross-judge comparison can and cannot settle when every judge shares one rubric.
- [Audit the Noise Floor Before Trusting a Benchmark Gap](benchmark-noise-floor-audit.md) — the prior check on whether a gap of a few points is readable at all.
- [Spec-Derived Execution-Correctness Judging](spec-derived-execution-correctness-judging.md) — grounding the oracle in execution traces when the eval can run the artifact end to end.
