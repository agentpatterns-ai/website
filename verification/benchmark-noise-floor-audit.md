---
title: "Audit the Noise Floor Before Trusting a Benchmark Gap"
term: "Noise-Floor Audit"
description: "Under greedy, single-turn tool calling the prompt-rewording noise floor measured 11 to 58 times the rerun floor, so repeat runs capture only the smaller one."
tags:
  - testing-verification
  - evals
  - tool-agnostic
  - arxiv
aliases:
  - prompt-perturbation floor
  - eval noise floor
  - rerun versus perturbation variance
last_reviewed: 2026-08-25
maturity: emerging
---

# Audit the Noise Floor Before Trusting a Benchmark Gap

> Two noise floors sit under a benchmark score. On greedy single-turn tool calling the rewording floor ran 11 to 58 times the rerun floor.

A noise-floor audit measures two variance arms before you spend on either: repeated runs at a frozen decoding setting, and matched runs across semantics-preserving rewrites of the same prompt. Chen et al. ran both arms over 150 frozen BFCL instances on three native tool-calling endpoints and found the perturbation arm 11 to 58 times wider than the rerun arm ([arXiv:2608.22331v1](https://arxiv.org/abs/2608.22331v1)). A reported gap has to clear the wider floor.

## The conditions this holds under

The ordering is not a general property of evals. Four conditions held during the audit, and each one bounds the result.

- Temperature 0 with greedy decoding.
- Hosted endpoints whose serving configuration the audit never changed.
- Single-turn native tool calling, graded by AST matching rather than by a judge.
- A frozen list of 150 instances. The authors warn that "a rerun-SD estimate is more trustworthy only once enough matched instances are included to stabilize the resampling curve" ([arXiv:2608.22331v1](https://arxiv.org/abs/2608.22331v1)).

Change one and measure again.

## The two floors, measured

| Endpoint | Ever-flip across reruns | Rerun paired SD | Median perturbation paired SD | Ratio |
|---|---|---|---|---|
| Groq llama-3.1-8b-instant | 0.7% | 0.28pp | 16pp | ~58x |
| Groq llama-3.3-70b-versatile | 2.0% | 0.91pp | 10pp | ~11x |
| Gemini 3.5 Flash, thinking low | 2.7% | 1.1pp | 19pp | ~16x |

The rerun arm ran ten times per endpoint. The perturbation arm ran four semantics-preserving variants at five runs each: collapsed whitespace, a tool-instruction prefix, a request-label wrapper, and a call-only suffix ([arXiv:2608.22331v1](https://arxiv.org/abs/2608.22331v1)).

Failure character moved with endpoint strength too. Malformed outputs (unparseable, truncated, or degenerate) made up 30% of task failures on the 8B endpoint, 7% on the 70B, and under 1% on Gemini ([arXiv:2608.22331v1](https://arxiv.org/abs/2608.22331v1)). Two endpoints can post one accuracy number and need different repairs: malformed calls point at the call surface, wrong arguments at tool-use semantics.

## Spend the next dollar on variants

Run a small rerun check, then stop buying reruns. The authors put the remaining compute into "matched prompt perturbations, grader audits, or broader instance coverage". Their rule for a gap you want to act on: below the perturbation floor, prompt wording and call-surface robustness are the actionable targets, not another batch of identical reruns ([arXiv:2608.22331v1](https://arxiv.org/abs/2608.22331v1)).

Publish enough for a reader to reproduce the floor: the frozen instance list, the prompt-template family, paired perturbation SDs, and a small failure-character table beside each headline score ([arXiv:2608.22331v1](https://arxiv.org/abs/2608.22331v1)).

## Why it works

Greedy decoding takes the argmax at every step. Re-running an identical prompt against an identically configured server changes the answer only where the top-two logit margin is narrower than the numerical drift in the forward pass. That drift traces to non-associative floating-point arithmetic under limited precision ([Yuan et al., arXiv:2506.09501v2](https://arxiv.org/abs/2506.09501v2)). Rewording the prompt changes the input tokens instead, so every logit differs and the decision boundary can move across many instances at once. Meaning-preserving format changes alone shift few-shot accuracy by up to 76 points on LLaMA-2-13B ([Sclar et al., arXiv:2310.11324v2](https://arxiv.org/abs/2310.11324v2)). Chen et al. call their own analysis descriptive rather than causal and leave the mechanism open, so this explanation is assembled from adjacent work.

## When this backfires

- Sampling above temperature 0 in production. A 0.28pp to 1.1pp rerun floor is a greedy-decoding measurement and does not carry over.
- Self-hosted or configuration-varying inference. Changing GPU count, GPU type, or evaluation batch size moves greedy accuracy by up to 9% and response length by 9,000 tokens on DeepSeek-R1-Distill-Qwen-7B ([Yuan et al., arXiv:2506.09501v2](https://arxiv.org/abs/2506.09501v2)). That is roughly ten times the rerun floor here and comparable to the perturbation floor. The two arms stop being an order of magnitude apart, and the budgeting rule no longer follows.
- Multi-turn or environment-coupled agents. The authors exclude them, and per-step variance compounds through accumulated state. Attribute it by [variability layer](sampling-state-agent-variability-layers.md) first.
- A prompt template already frozen in production. The perturbation SD then describes how sensitive the model is to wording, not how uncertain your own number is, and the extra runs buy something you cannot act on.
- LLM-judge grading. AST matching has no judge arm, so neither floor covers judge variance.

The audit carries one confound of its own: its Gemini endpoint differs from the Groq pair on provider and thinking configuration at once, so that row cannot separate the two ([arXiv:2608.22331v1](https://arxiv.org/abs/2608.22331v1)).

## Key Takeaways

- Measure both arms once. On these endpoints the rerun floor was 0.28pp to 1.1pp and the perturbation floor 10pp to 19pp ([arXiv:2608.22331v1](https://arxiv.org/abs/2608.22331v1)).
- Compare a reported gap against the perturbation floor, and treat a smaller gap as a question about prompt wording rather than about capability.
- Report the failure-character split beside accuracy. A 30% malformed-output share and a sub-1% share need different repairs.
- Re-measure both floors whenever decoding, serving configuration, turn count, or the grader changes.

## Related

- [Seed-Variance Reporting and Measurable-Range Eval Design](seed-variance-reporting.md) — how to report a spread once you have one, and when a cell sits too near a bound to carry a verdict.
- [Decomposing Agent Output Variability by Layer](sampling-state-agent-variability-layers.md) — attributing run-to-run spread to sampling, infrastructure, or orchestration state.
- [Tool-Use Sim-to-Real Perturbation Taxonomy](tool-use-sim-to-real-perturbation-taxonomy.md) — perturbations that change the environment rather than the wording, and where robustness collapses under each.
- [Eval Blind Spots: Structural Gaps in Measurement Methodology](eval-blind-spots.md) — measurement gaps a stronger model cannot close.
- [Use pass@k and pass^k to Separate Agent Capability from Consistency](pass-at-k-metrics.md) — reporting capability and consistency as two numbers.
