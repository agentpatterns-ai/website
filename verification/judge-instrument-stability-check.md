---
title: "Measure the Judge Before You Freeze a Gate on It"
term: "Judge Instrument Check"
description: "Byte-identical judge requests replayed the next day reproduced the ranking 78 times out of 100, against a threshold of 0.99 fixed in advance, while every execution-audit signal sat at ceiling."
tags:
  - testing-verification
  - evals
  - tool-agnostic
  - arxiv
aliases:
  - judge replay check
  - instrument stability gate
  - snapshot identity level
last_reviewed: 2026-09-06
maturity: emerging
---

# Measure the Judge Before You Freeze a Gate on It

> Replaying 100 byte-identical judge requests a day later reproduced the ranking 78 times. The threshold, fixed before the run, was 99.

A judge instrument check sends the same request to the same model name twice, separated by a delay, and asks whether the decision built on top of the answer survives. Zhu and Zhang ran that check as a preregistered gate on two evaluation campaigns and neither campaign got past it ([arXiv:2609.04198v1](https://arxiv.org/abs/2609.04198v1)). Run the check before you freeze a gate, not after the gate goes red.

## When this check earns its cost

Three conditions have to hold together, and the paper's headline numbers came from a run where all three did.

- The gate ranks candidates rather than reporting an aggregate. Rankings amplify small per-item flips and a mean absorbs them, which is why the audited run's scalar arm passed while its ranking arm failed ([arXiv:2609.04198v1](https://arxiv.org/abs/2609.04198v1)).
- The judge runs on a shared endpoint you do not control, so batch composition moves with load you cannot see. Replay stability holds far better on pinned self-hosted serving, and then only "while the server is quiet" ([arXiv:2609.04198v1](https://arxiv.org/abs/2609.04198v1)).
- The score gaps you are asking the judge to resolve sit near its repeat-noise floor.

Outside those conditions the check is a setup-time sanity pass rather than a standing gate.

## What the audit found

| Preregistered gate | Required | Observed |
|---|---|---|
| I-3S, same-window repeat, within-task Spearman median | 0.90 | 0.400 |
| I-5R, next-day replay, exact permutation match | 0.99 | 0.78 |

The engineering layer was clean while the measurement failed: "every request delivered, every schema valid, every request body hash-identical to its frozen plan, every recorded metadata field constant" ([arXiv:2609.04198v1](https://arxiv.org/abs/2609.04198v1)). A green execution audit only says the pipeline sent what it promised. It says nothing about whether the instrument on the far end held still.

The scalar readout underneath those rankings held, at a median repeat delta of 0.006710, and the rankings collapsed anyway ([arXiv:2609.04198v1](https://arxiv.org/abs/2609.04198v1)). The reason sits in the measurand. The median minimum gap between adjacent candidates was 3.04×10⁻¹⁰, and the authors report that "the typical gap sits four to seven orders of magnitude below the noise floor" ([arXiv:2609.04198v1](https://arxiv.org/abs/2609.04198v1)). An exact-permutation gate over gaps that small asks a question the instrument cannot answer, so the repair is to change the gate rather than to distrust the judge. Their design rules 9.3 and 9.4 name the two moves: condition ranking gates on informative pairs, and prefer continuous readouts with equivalence bands ([arXiv:2609.04198v1](https://arxiv.org/abs/2609.04198v1)).

## Running the check

1. Freeze a set of judge requests and hash the bodies. Zhu and Zhang used 100 and confirmed every replay body by SHA-256 match ([arXiv:2609.04198v1](https://arxiv.org/abs/2609.04198v1)).
2. Measure the repeat-noise floor inside one window, and record the score separations your gate has to resolve. Separations smaller than the floor mean you redesign the readout instead of replaying it.
3. Replay the frozen bodies against the same model name after at least 24 hours.
4. Compare the runs on the quantity your gate consumes, reporting scalar and ranking agreement separately.
5. Record your snapshot-identity level. L0 is a model name alone, L1 is a provider-pinned snapshot where "weights fixed; observable behaviour still not byte-stable", and L2 adds a self-hosted weights hash, batch-invariant kernels and pinned hardware ([arXiv:2609.04198v1](https://arxiv.org/abs/2609.04198v1)).

Do not treat `system_fingerprint` as certification. Across providers the field was "never populated" on some, "churning" on others, and "present, stable, and still insufficient" on the rest ([arXiv:2609.04198v1](https://arxiv.org/abs/2609.04198v1)).

## Why it works

Serving a request inside a batch changes its arithmetic. "The same request can emit different tokens when decoded alone or inside a larger batch" ([arXiv:2605.30218v1](https://arxiv.org/abs/2605.30218v1)). Zhu and Zhang name the same cause for their own replay failures, "batch-size-dependent kernel scheduling under shared load", and report it as "consistent with everything we observe" ([arXiv:2609.04198v1](https://arxiv.org/abs/2609.04198v1)). A caller on a shared endpoint cannot hold batch composition fixed, so a byte-identical body and a fixed model name do not imply a fixed instrument. The per-step flip rate is small: 0.3% to 1.3% of decode steps across five models on MATH500, GSM8K and HumanEval ([arXiv:2605.30218v1](https://arxiv.org/abs/2605.30218v1)). A gate demanding exact permutation match over near-tied scores turns that small rate into a red eval, traceable back to another tenant's traffic.

Temperature is the mitigation people reach for, and it does not close the gap. Across 690 calls spanning two providers and three model tiers, "1-2 of 7 borderline items remain non-reproducible even under forced greedy decoding", and Claude Opus 4.7/4.8 deprecated the parameter outright ([arXiv:2606.26185v1](https://arxiv.org/abs/2606.26185v1)).

## When this backfires

The three conditions above invert cleanly: an aggregate readout, or separations well clear of the noise floor, and replay disagreement changes no decision the gate makes. Three more cases:

- Self-hosted L2 serving. Replay stability there sits "far above the shared-endpoint floor" while the server is quiet ([arXiv:2609.04198v1](https://arxiv.org/abs/2609.04198v1)), so the check becomes a one-off during setup.
- The eval budget is small. Both campaigns spent theirs certifying the instrument and neither reached the questions it was built to answer ([arXiv:2609.04198v1](https://arxiv.org/abs/2609.04198v1)).
- Validity is the real risk rather than stability. Norman and colleagues found two production judges holding test-retest reliability above 0.95 alongside position bias above 0.10, across roughly 541,000 judgments ([arXiv:2606.19544v1](https://arxiv.org/abs/2606.19544v1)). Such a judge passes this check cleanly and still ranks by the wrong thing, so pair the replay with a bias audit.

## Key Takeaways

- Replay 100 byte-identical judge requests after 24 hours before a ranking gate depends on the judge.
- Gaps below the repeat-noise floor make the gate unanswerable, whatever the judge does. Measure both in one pass.
- Report scalar and ranking agreement separately. The scalar arm passed at a 0.006710 median delta while the ranking arm failed at 0.78.
- Record the snapshot-identity level beside the score, and do not accept `system_fingerprint` as a replay guarantee.

## Related

- [Audit the Noise Floor Before Trusting a Benchmark Gap](benchmark-noise-floor-audit.md) — the same discipline for AST-graded benchmarks, whose two floors explicitly exclude judge variance
- [Meta-Evaluate the LLM Judge Before Trusting Rubric Verdicts](meta-evaluate-llm-judge-rubric-verification.md) — the accuracy half, measured against human labels
- [Detecting Self-Preference in a Single LLM Judge](judge-self-preference-detection.md) — a bias a stability check passes over
- [Decomposing Agent Output Variability by Layer (Sampling vs Orchestration State)](sampling-state-agent-variability-layers.md) — attributing variance once you know the instrument moved
- [Grading Strategies](../training/eval-driven-development/grading-strategies.md) — where a judge sits among code-based and human grading
