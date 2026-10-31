---
title: "Specification-Oracle Gap Audits for Test-Graded Evals"
term: "Specification-Oracle Gap"
description: "When a scored test references a name the task text never states, the eval also grades name reproduction; a static dependency audit finds those tests in minutes, and whether it is worth running depends on how the task text was made."
tags:
  - testing-verification
  - evals
  - benchmarks
  - tool-agnostic
  - arxiv
aliases:
  - specification-oracle gap
  - hidden test dependency audit
  - unstated name dependency in benchmarks
last_reviewed: 2026-10-26
maturity: emerging
---

# Specification-Oracle Gap Audits for Test-Graded Evals

> A scored test that needs a name the task text never states grades name reproduction; dependency audits over your evals find it.

Some test-graded evals pair a prose task with tests lifted from the upstream project. The two artifacts commit to different things. An unnamed dependency is a free choice when neither the starting code nor its conventions determine it. Grading that choice measures more than the specified behavior. A static audit over your task texts and your scored tests finds those dependencies without model calls and tells you which tests to restate or waive.

## When the gap is worth auditing

The eval's construction determines where this audit is useful ([Ding, arXiv:2610.30635v1](https://arxiv.org/abs/2610.30635v1)):

- Your task text is generated rather than screened. "Prevalence follows construction." The audit flagged 17 of 48 release-note tasks in SWE-EVO and 64 of 155 LLM-summary tasks in SWE-Chain. Each share exceeds one-third. For screened SWE-bench Verified issues, it flagged 3 of 500. For test-aligned DeepSWE instructions, it flagged 7 of 113; only one survived review. Treat that comparison as exploratory: review units and sizes differ between benchmarks, and the audit ran on "four more benchmarks (Python only except DeepSWE)".
- Your tests reach into internals. Across the seven repositories of SWE-Milestone v1.0.2, go-zero carried most of the hard hidden dependencies because its "tests exercise package internals", at 15 of its 23 graded milestones. The repositories whose tests drive public interfaces, scikit-learn and ripgrep, plus nushell, had none.
- Your harness compiles a test unit as a whole and does not report the missing name back. SWE-Chain flags a larger task share than SWE-Milestone. Its flagged steps fail 1.12 times as often as unflagged steps (95% CI 1.04 to 1.28). The paper adds, without testing it as a cause, that "its harness isolates failed imports and reports them back to the agent".

## What the audit looks for

List, per scored test, the artifacts the solution must supply: identifiers the test references, module or file paths it imports or mocks, and literals it compares output against. Subtract what the starting code base defines, what the task text names, and what a convention already present in the code base determines. The remainder is the gap. The audit uses one extractor per language for Go, Python, Rust, TypeScript and Java. Over seven repositories from a cold cache, it "takes 28.1 minutes on a 16-core workstation, with at most 1,333 MiB of memory and no model calls" ([Ding, arXiv:2610.30635v1](https://arxiv.org/abs/2610.30635v1)). Across two held-out rounds, precision was 58 of 65 flagged build units (89.2%; 95% Wilson interval 79.4 to 94.7%). The source states that "on the second set its recall is 13/14". A hired software expert labeled the final 103-case round blind. An author labeled the held-out cases independently. Agreement was 92 of 94 and 101 of 103 cases (Cohen's kappa 0.92 and 0.96).

Then repair in the direction that keeps evidence. Waiving the affected tests costs information, because "Removing tests changes what a benchmark measures". Stating the interface keeps the test and removes the guessing. The paper generated an addendum for each of the 25 affected milestones. Together, the 25 addenda state 153 interface conventions that the reference tests require, without describing their implementation. One reads: "the package rest/handler must declare valueSSE (relied on by 84 required tests)".

## Why it works

"The specification describes behaviour; the oracle is code that calls helpers, references constants, imports modules at fixed paths and compares exact messages" ([Ding, arXiv:2610.30635v1](https://arxiv.org/abs/2610.30635v1)). A name is free when neither the task text nor the starting code and its conventions determine it. Scoring that choice rewards reproduction of upstream detail. A missing name or path can fail every test in its build unit. The language compiles or collects those tests together.

A counterfactual on the reference solution isolates that mechanism with no agent involved. The experiment renames one hidden identifier in the reference's non-test code. This "stops the unit's tests from compiling in 126 of 128 Go cases". The tests that then failed were 99.5% of those the audit predicted. That check covers Go only.

Across 35 published SWE-Milestone v1.0.2 runs, "units blocked by a hard hidden dependency fail in 80.6% of (unit, run) pairs and all other units in 15.1%". Most unflagged units only hold tests an agent passes by breaking nothing. The matched comparison uses units inside the same milestones that also carry new tests and no new dependency. Those units "fail in 48.4%". Blocked units fail 1.67 times as often (95% CI 1.32 to 2.04). Units whose new names the specification states show no such penalty (1.08, CI 0.83 to 1.41). This observational comparison associates the omission with failures; difficulty can still differ.

## When this backfires

- The effect is rare in aggregate and may not touch what you report. Only 0.6% of SWE-Milestone's required tests sat at risk. In the full re-scoring variant, the 28 leaderboard runs gained 0.84 score points on average, ranging from −0.26 to +2.89. Over all 35 runs the ranking moved "within what chance produces" against removing as many tests from randomly chosen units of matched size ([Ding, arXiv:2610.30635v1](https://arxiv.org/abs/2610.30635v1)).
- A flag is not a lost task. "A flag means that the specification withholds a dependency, not that every agent misses it". Runs reproduced 45% of the hard dependencies for which the evaluation gives evidence.
- Writing the names into the task can turn an engineering task into instruction-following. Inferring an unstated interface from surrounding code is part of the job. The addendum route is untested: its "effect we have not yet measured with new agent runs".
- The audit is name-level, so its counts run low. Its extractors "do not type-check", and matching against the specification is lexical. A separate text heuristic covers required behavior that introduces no new name. Thus "the audit's counts are a lower bound on how often tests demand what the task does not say" ([Ding, arXiv:2610.30635v1](https://arxiv.org/abs/2610.30635v1)). On SWE-bench Verified, behavioral gaps explained most of the persistent failures the paper reviewed.
- The failure-rate comparison is observational. Blocked units were matched to units that also test new code inside the same milestones, yet "the groups can still differ in difficulty".

## Example

The paper's motivating case ([Ding, arXiv:2610.30635v1](https://arxiv.org/abs/2610.30635v1)): milestone M019 of go-zero adds Server-Sent Events support, and its generated specification states the behavior down to detecting the `Accept: text/event-stream` header. It never names the two constants the reference tests use, `headerAccept` and `valueSSE`. Go compiles a package's tests together. An agent using its own names loses every required test of `rest/handler`: 84 in M019. Each of five later milestones inherits 88 to 108 affected tests. Of the 34 runs counted, 32 implemented the bypass the specification asks for. Nine also named the value `valueSSE`; four of those passed all 84 required tests. The 23 that named it differently or wrote the string inline passed none.

## Key Takeaways

- List what each scored test references, subtract what the base code and the task text already supply, and check the remainder for an eval defect.
- Run it where the task text was mined or summarized and the tests touch internals. Screened or test-first task text showed almost no hidden names.
- Prefer an addendum that names the interface over waiving the test. Neither repair has been measured against fresh agent runs.
- Fix the harness too. The authors associate SWE-Chain's smaller flagged-step failure ratio (1.12) with reporting failed imports back to the agent; this comparison does not isolate a causal effect.
- Expect a small aggregate effect and a large local one. A quarter of SWE-Milestone's graded milestones were affected while the leaderboard ranking held, and per-repository scores shifted.

## Related

- [LLM-Driven Benchmark Auditing](llm-benchmark-auditing.md) — audits the benchmark's own artifacts with a frontier model, where this audit is static and name-level
- [Probing Unstated Constraints in Generated Code (Intent Violation Rate)](unstated-constraint-probes.md) — the mirror case, where the tests check less than the prompt asked for rather than more
- [Ambiguity Stability as a Model-Selection Criterion](ambiguity-stability-model-selection.md) — what to do with the ambiguity you cannot remove from your own task text
- [Specification-Path Testing: Same Contract, Different History](specification-path-testing.md) — the same requirement restated through a different revision history flips which tasks pass
- [Benchmark Contamination as Eval Risk](benchmark-contamination-eval-risk.md) — the other way a test-graded score drifts away from capability
