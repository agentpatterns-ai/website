---
title: "Serving-Stack Confounds in Tool-Call Evaluation"
term: "Serving-Stack Confound"
description: "A local server decides whether a tools= request is honored before the model runs, so a 0% tool-call rate can be a template flag rather than a measurement of the model."
tags:
  - anti-pattern
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - serving stack as evaluation confound
  - tool-call rate as a model property
  - measuring the serving stack instead of the model
last_reviewed: 2026-09-23
maturity: emerging
---

# Serving-Stack Confounds in Tool-Call Evaluation

> A local server can refuse a tool-call request before the model runs, and the harness records that refusal as the model declining.

A tool-call failure rate measured through a local serving stack describes the model, the server, and the server's launch flags together. On Ollama 0.30.8, Phi-3 and Gemma-3 have the request rejected with HTTP 400 "does not support tools" before inference, so a per-turn analysis reports both at 0% when "100% of their turns are rejected requests, so the model never ran and the rate is properly undefined" ([arXiv:2609.26693v1](https://arxiv.org/abs/2609.26693v1)).

## When the reading goes wrong

Three conditions hold together: a self-hosted serving layer, a harness that keeps only the assistant message stream, and an unpinned stack version. A rejection then collapses into a generic error string whose type never reaches the trajectory. Four stacks handle the identical request four ways on the same weights ([arXiv:2609.26693v1](https://arxiv.org/abs/2609.26693v1)):

| Model | Ollama | llama.cpp | vLLM (default) | SGLang (default) |
|---|---|---|---|---|
| Qwen2.5-Coder-0.5B | 200 text | 200 text | 400 rejected | 200 text |
| Phi-3-mini | 400 rejected | 200 text | 400 rejected | 200 text |
| Gemma-3-270m | 400 rejected | 200 text | not probed | not probed |

vLLM refuses every model's request until launched with `--enable-auto-tool-choice` and a `--tool-call-parser`; SGLang returns the call as text until given a parser. Both were probed on Qwen-0.5B and Phi-3 only.

## Diagnosing a zero tool-call rate

Attribute to the model last. First check whether the serving layer refused or emptied the request, because on HTTP 4xx or retry exhaustion the model never ran and the rate is undefined. Then check that a tool-call parser is configured for this stack and model, since an accepted request can still surface the call as prose nothing extracts.

Two reporting habits keep that ladder usable. Log a serving failure as its own outcome category, and report per-seed rates with intervals beside any pooled number: Qwen-0.5B under a uniform text protocol reads 85% pooled and 34% per-seed, because one 41-turn episode dominates the pool ([arXiv:2609.26693v1](https://arxiv.org/abs/2609.26693v1)).

## Why it works

The tool schemas never reach the weights. "The model never receives that array directly": the serving layer renders the specifications into the prompt with the model's chat template, then parses the generated text back into a structured `tool_call`. Both steps happen outside the weights, so whether a server performs them is "determined by the model's template and the server's launch configuration rather than by what the model can do" ([arXiv:2609.26693v1](https://arxiv.org/abs/2609.26693v1)).

A refusal decided before dispatch carries no information about the model, and the same GGUF weights Ollama rejects return a text response under llama.cpp. The backend confounds more than tool calls: with weights, decoding parameters, and hardware held constant, it alone shifts benchmark scores by up to 16.6 percentage points ([arXiv:2605.19537v2](https://arxiv.org/abs/2605.19537v2)). Across 5,194 execution trajectories, Harness-Bench reaches the matching conclusion, that capability "should be reported at the model–harness configuration level rather than attributed to the base model alone" ([Yao et al., arXiv:2605.27922v1](https://arxiv.org/abs/2605.27922v1)).

## When this backfires

The authors scope the fixed-interface rule to standardized model comparisons. Four cases fall outside it.

- You are evaluating a deployable model-server system. The parser and template are part of the product, and such evaluations "should instead report the full model–server configuration as part of the system being evaluated" ([arXiv:2609.26693v1](https://arxiv.org/abs/2609.26693v1)).
- A uniform protocol destroys a real capability. Llama-3.2 reaches 82% per-seed fidelity on the native channel with a text hint and 44% under the uniform text protocol, which discards its native `tool_calls` support ([arXiv:2609.26693v1](https://arxiv.org/abs/2609.26693v1)).
- The denominators are too thin to decide anything. Over 8 seeds the intervals reach 34% [9,59] for Qwen-0.5B and 38% [12,75] for Phi-3, "far too wide to rank these models against each other" ([arXiv:2609.26693v1](https://arxiv.org/abs/2609.26693v1)).
- You stop at the stack and the cause was model-side. Small models hallucinate tool names absent from the schema, and pretraining-aligned renaming cut those errors by 80% ([arXiv:2510.07248v3](https://arxiv.org/abs/2510.07248v3)).

## Key Takeaways

- Report the serving stack, its version, and the tool-call parser alongside the model identity, the way decoding parameters and hardware already are.
- A refused or empty request is its own evaluation outcome. Recording it as a model non-call is what turns a capable model into a 0%.
- Pin which question you are answering. A fixed interface serves model comparison; a system evaluation reports the whole model-server configuration.
- Per-seed and turn-pooled rates can differ by roughly 50 points on the same runs, so publishing one alone hides which you got.
- Ollama's gate is a release-level policy, so a result that survives one upgrade of the stack is not the same measurement.

## Related

- [Blaming the Model for Scaffolding-Driven Quality Regressions](blaming-the-model-for-scaffolding-regressions.md) — the same misattribution one layer up, where the scaffold version moved and the model took the blame.
- [Constraint Tax in Open-Weight LLMs](constraint-tax-tool-suppression.md) — grammar-constrained decoding masking the tool-call tokens while schema compliance stays near 100%.
- [Seed-Variance Reporting](../../verification/seed-variance-reporting.md) — what to publish when a result moves with the seed.
- [Perceived Model Degradation](perceived-model-degradation.md) — the competing explanations for a model that seems to have got worse, and how to pin versions before choosing one.
- [Benchmark Noise-Floor Audit](../../verification/benchmark-noise-floor-audit.md) — measuring how much of an eval gap the instrument itself produces.
