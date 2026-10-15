---
title: "Revising Code Against Its Own Tests (Interpretive Lock-In)"
term: "Interpretive Lock-In"
description: "Across 30 DataFrame tasks, revision raised test passes from 22/30 to 30/30 while reference agreement stayed at 0/30."
tags:
  - testing-verification
  - tool-agnostic
  - anti-pattern
  - arxiv
aliases:
  - interpretive lock-in
  - self-confirming revision loop
  - revision loop oracle drift
last_reviewed: 2026-10-14
maturity: emerging
status: current
---

# Revising Code Against Its Own Tests (Interpretive Lock-In)

> One wrong reading of the task survives plan, code and tests, so revising against them turns the suite green and leaves the code unchecked.

Interpretive lock-in is a mistaken reading of the task that persists through the plan, the implementation and the self-generated tests. The suite then agrees with the code while neither agrees with the task. Three conditions held in the study. The output contract covers more than a return value, reaching column names, numeric widths, grouping grain and null handling. An authoritative reference exists but the agent never sees it. And the loop's feedback comes from the agent's own suite, plus, in the third pipeline, an audit against prompt-derived obligations. All three held across 30 DataFrame tasks derived from TPC Benchmark DS, where "No candidate matched the reference (0/30 per condition), although test-pass rates rose from 22/30 to 29/30 and 30/30" ([Liu et al., 2026](https://arxiv.org/abs/2610.15797v1)).

## The anti-pattern

Let the agent write the plan, the implementation and the tests, hand it the pytest failures, and ship on green. Reference agreement never moves. Test-guided revision "gained 23.3 percentage points in test passing", and the matching code-semantics gain was 2.33 points, "entirely through q2's recovery from execution failure to 70% obligation satisfaction" ([Liu et al., 2026](https://arxiv.org/abs/2610.15797v1)). Every suite that went green disagreed with the reference: "Every passing suite was therefore a false pass: the conditional false-pass proportion was 100% in each condition." In the PlanAudit pipeline, two mismatches turned out to be cosmetic, and "Normalization recovered only q13 and q17 as genuine alias-only mismatches" while "27/30 outputs failed full normalization".

Auditing the plan did not rescue it. A third pipeline extracted obligations from the prompt, scored the three artifacts against them, and could revise them all. It reached 30/30 passing, improved code scores on 3 of 30 tasks and test coverage on 11 of 30, with a median paired change of zero on both ([Liu et al., 2026](https://arxiv.org/abs/2610.15797v1)).

## Why it works

A suite measures agreement between the implementation and the assertions, and one interpretation produced both. The reference never enters the loop, so the only thing the loop can converge on is itself. Their paper states the limit directly: "Separate generation alone does not ensure independence when specifications or expected values share an ambiguity" ([Liu et al., 2026](https://arxiv.org/abs/2610.15797v1)).

The protocol shows the channel. Test-guided revision let the model "make syntax, import, or fixture additions to test_solution.py", and the plan-audit condition could rewrite the test file outright, so the oracle moved with the candidate. The defects that result have names: "Inadequate checks include coarse aggregates, candidate-defined schemas, nondiscriminating fixtures, and assertions repeating incorrect logic." The candidate-schema category alone accounted for 9 of 39 violated obligations in the one-pass false passes and 11 of 52 in the plan-audit ones ([Liu et al., 2026](https://arxiv.org/abs/2610.15797v1)).

Coverage does not stand in for the contract either. Among runs scoring at least 90% test coverage, 11, 12 and 17 still failed reference agreement ([Liu et al., 2026](https://arxiv.org/abs/2610.15797v1)).

## When this backfires

The first limit is in the evidence. Reference agreement was already 0/30 in the no-revision baseline, so the design cannot separate a loop that fails to improve semantics from a task set this model does not solve under any condition. The authors say as much: "These findings are diagnostic rather than causal". It is one model, 30 tasks, one generation each, and "the targeted replication establishes recurrence, not population robustness" ([Liu et al., 2026](https://arxiv.org/abs/2610.15797v1)).

Three conditions put a task outside the finding:

- Thin output contracts leave nothing for the tests to miss. Where the prompt fixes the signature and enumerates the cases, self-generated tests are a useful ranking signal. CodeT "improves the pass@1 metric on HumanEval to 65.8%, which represents an absolute improvement of 18.8% over the code-davinci-002 model" ([Chen et al., 2022](https://arxiv.org/abs/2207.10397v2)). That gain is scored against hidden tests, not against the generated ones.
- No independent reference exists. The study's check is a set of reference outputs frozen before generation and used only after it. Without an equivalent artifact, the authors say shared errors "require independent implementations or hand-checked assertions to resolve".
- The contract is what you are discovering. On exploratory work the interpretation should move, and an assertion frozen before any candidate exists pins whichever reading you had first.

Keep the loop for what it does catch. In the primary study "Execution succeeded in 28/30, 29/30, and 29/30 runs", and the one code-score gain under test-guided revision came from a task recovering from execution failure ([Liu et al., 2026](https://arxiv.org/abs/2610.15797v1)). The failure is reading the pass count as semantic progress.

## What to do instead

The paper's proposed first step is "deriving acceptance assertions from explicit task contracts before candidate inspection and holding them fixed during revision". It also splits the contract: "Contracts should distinguish stated from hidden requirements and separate schema, null behavior, grouping, channel labels, and ordering from value assertions" ([Liu et al., 2026](https://arxiv.org/abs/2610.15797v1)).

Then make the fixtures discriminate. "Fixtures should discriminate alternatives: unmatched keys for joins, unequal price fields for metric substitutions, and multiple groups for aggregation grain" ([Liu et al., 2026](https://arxiv.org/abs/2610.15797v1)). A fixture that cannot tell two candidate readings apart certifies both.

## Example

In the primary study, "In q4, all 10 PlanAudit-revised tests passed despite using ss_list_price rather than ss_ext_list_price". In the targeted fresh-generation replication of q4, "PlanAudit repaired a join fixture but retained the wrong price formula; small fixture values made the alternatives yield equal relative ratios" ([Liu et al., 2026](https://arxiv.org/abs/2610.15797v1)).

**Before — the fixture cannot separate the two price fields:**

```text
fixture:  list_price and ext_list_price carry small values
          so the two readings give the same relative ratio
check:    the ratio between two segments
outcome:  passes whichever column the code used; the wrong metric ships
```

**After — the fixture is built to separate them:**

```text
fixture:  list_price and ext_list_price carry unequal values
check:    the same ratio, frozen from the contract before the code was read
outcome:  the column substitution moves the ratio and the check fails
```

The loop is the same in both. What changes is whether the fixture values can tell the reading under test apart from the reading in the contract.

## Key Takeaways

- Across three pipelines on 30 TPC-DS DataFrame tasks, test passes went 22/30, 29/30, 30/30 while reference agreement stayed at 0/30, and all 77 passing suites on the 28 reproducible tasks were false passes ([Liu et al., 2026](https://arxiv.org/abs/2610.15797v1)).
- Auditing the plan against prompt-derived obligations improved a minority of tasks with a zero median, so a review stage inside the loop is not an outside check.
- An editable test file lets the oracle change with the candidate, though the study did not isolate that effect, since the frozen one-pass baseline also had 22 false passes. Freeze contract-derived assertions before the first candidate and keep the loop out of them, as the authors propose.
- Fixture values decide whether an assertion carries information: "small fixture values made the alternatives yield equal relative ratios" in the fresh-generation replication of q4, where PlanAudit "retained the wrong price formula".
- The evidence is one model, 30 contract-dense tasks, and a zero baseline, and findings the authors call diagnostic rather than causal. On thin contracts, generated tests still work as a selection signal.

## Related

- [Generating Tests From Agent-Written Code (Code-First Oracle Bias)](code-first-test-oracle-bias.md) — the ordering fix this page is the limit case of: separating the stages still leaves the shared interpretation when the loop can edit the tests
- [When Your Agent's Verifier Reads the Same False Premise](verifier-reads-the-same-premise.md) — the selection counterpart, where a false premise in the task description reaches generator and verifier together
- [Test Oracles That Read Their Expectation From the Code](state-anchored-test-oracles.md) — the single-assertion version of the same cancellation, with the expected value flowing out of the code under test
- [Specification-Grounded Test Writing](../../verification/specification-grounded-test-generation.md) — how to supply the contract as enumerated rules so the assertions have somewhere to come from
- [Mutation Testing as a Quality Gate for AI-Generated Test Suites](../../verification/mutation-testing-quality-gate.md) — the mechanical way to find out whether a fixture discriminates, by checking which planted faults the suite catches
