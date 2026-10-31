---
title: "Inference-Option Adoption Rates Are Not Configuration Guidance"
term: "Inference-Option Adoption Rate"
description: "Across 5,398 repositories, 78.9% of documented inference options are set in at most 10% of the repositories using that backend, which measures what developers make explicit rather than what affects cost or quality."
tags:
  - token-engineering
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - inference configuration prevalence
  - reading an option adoption rate
last_reviewed: 2026-10-26
maturity: emerging
---

# Inference-Option Adoption Rates Are Not Configuration Guidance

> Repository adoption rates show which inference options developers make explicit, not which ones change latency, cost, or output quality.

An adoption rate mined from open-source code is a visibility measurement. It ranks options by how often they appear in other people's repositories. That ranking tracks how visible an option is, not what it does to your bill.

## What the adoption numbers measure

A mining study of 5,398 public GitHub repositories using Hugging Face Transformers, vLLM, or the OpenAI API found 345,117 explicitly configured option occurrences. Of the 331 documented backend-specific options in its scope, 327 (98.8%) appear at least once, yet 78.9% are configured in at most 10% of the repositories that use the corresponding backend ([Zine et al., arXiv:2610.27945v1](https://arxiv.org/abs/2610.27945v1)).

Individual configurations are small and barely shared. The repository-level median is 2 distinct options for Transformers and 4 for both vLLM and OpenAI. Among repositories holding at least one multi-option configuration, 56.8% to 61.6% of the distinct option combinations occur in exactly one repository, counting per backend ([arXiv:2610.27945v1](https://arxiv.org/abs/2610.27945v1)).

The authors are explicit about what this does not support: "How often an option is configured, or how often a particular value is selected, should therefore not be interpreted as a measure of its importance or impact on inference behavior" ([arXiv:2610.27945v1](https://arxiv.org/abs/2610.27945v1)). They add that "rarely configured options may still matter because developers can rely on defaults, may be unaware of the option or its effect, or may need it only in specific situations".

## Why it works

Adoption frequency and measured effect come from different processes, so one cannot rank the other. The study names the process behind frequency: "Frequently configured options may simply be more visible because they are more commonly documented, discussed, or studied", and recurring combinations "may also result from shared examples, documentation, reused code, or common configuration practices" ([arXiv:2610.27945v1](https://arxiv.org/abs/2610.27945v1)). Neither documentation prominence nor copied code touches the hardware the option runs on.

Measured effect depends on the model and the workload. One controlled study varied three vLLM options across 5 open-weight models and 5 tasks in 9,000 runs. It found that "Attention type and prefix caching show the most frequent effects on energy and performance", and its recommendation is to evaluate both "jointly across energy, performance, and accuracy" ([Zine et al., arXiv:2607.09172v2](https://arxiv.org/abs/2607.09172v2)). Its summary of the trade-off space: "These effects are highly model- and workload-dependent, and no configuration is universally optimal".

## What the data supports

Common options show which parts of each backend developers configure explicitly. Model and loading options appear in 85.7% of the study's Transformers repositories, 87.6% of its vLLM repositories, and 98.0% of its OpenAI repositories ([arXiv:2610.27945v1](https://arxiv.org/abs/2610.27945v1)).

Where an over-represented option matches the application's own function, prevalence and relevance coincide. For vLLM the study retained exactly one context difference: `limit_mm_per_prompt` runs +30.7 percentage points in multimodal and vision repositories. For the OpenAI API, `tools` runs +14.3 points in agent repositories and `reasoning_effort` +6.5 points in code and software engineering repositories. All three are measured over the 1,850 repositories the study maps to at least one application context ([arXiv:2610.27945v1](https://arxiv.org/abs/2610.27945v1)).

A common configuration supplies a comparison point, without evidence that it beats another configuration. The paper offers the observed configurations as "descriptive reference points", with the caveat that "they should not be interpreted as recommended or optimal configurations" ([arXiv:2610.27945v1](https://arxiv.org/abs/2610.27945v1)).

## When this backfires

- You cannot run a controlled comparison. The mining study supplies examples to inspect, but it cannot establish which configuration fits your workload.
- The option is a fixture of the interface. `messages` and `model` lead the OpenAI list at 32,022 and 30,571 occurrences, and the study notes that "The prominence of model also differs across backends because model selection is exposed differently" ([arXiv:2610.27945v1](https://arxiv.org/abs/2610.27945v1)), so interface shape can affect the rate.
- Your regime sits outside the sample. The dataset is public, Python, active since January 2025 and at least 50 stars, and the authors note these repositories "may not represent smaller, older, non-Python, private, or industrial projects".
- Low adoption reflects a correct default. An option almost nobody sets may be one almost nobody needs to set, which is not a gap to close.
- You copy a popular value across workloads. Recurring values do exist, with `top_p=1` at 40.4% of that option's resolved observations in OpenAI repositories ([arXiv:2610.27945v1](https://arxiv.org/abs/2610.27945v1)), but decoding performance is "notably task-dependent and influenced by factors such as alignment, model size, and quantization" ([Shi et al., arXiv:2402.06925v3](https://arxiv.org/abs/2402.06925v3), abstract).

## Example

The vLLM case shows why the two studies cannot be read against each other. The frequently configured vLLM options the mining study names are generation settings and serving settings: "In vLLM, generation options such as `max_tokens`, `temperature`, and `top_p` appear alongside serving-related options such as `tensor_parallel_size`, `gpu_memory_utilization`, and `max_model_len`" ([arXiv:2610.27945v1](https://arxiv.org/abs/2610.27945v1)).

The mining paper's examples of frequently configured vLLM options do not include attention kernel type or prefix caching, and the paper's text reports no adoption rate for either. Both carried the controlled study's most frequent energy and performance effects, and both moved measured accuracy for some model and benchmark pairs: "These findings are unexpected, as the parameters in question are intended solely for computational optimization and have no bearing on model outputs." Prefix caching alone "significantly altered measured accuracy for six model–benchmark combinations" ([arXiv:2607.09172v2](https://arxiv.org/abs/2607.09172v2)). Chunked prefill, the third option varied, showed limited observable effects on energy under the workloads studied.

## Key Takeaways

- Use an adoption rate to order your reading and your measurement queue, then price each option on your own workload.
- Do not copy a popular option combination as a unit. Most combinations in the data were used by one project, so the combination carries no second opinion ([arXiv:2610.27945v1](https://arxiv.org/abs/2610.27945v1)).
- Put attention kernel type and prefix caching on your measurement list whether or not many projects set them. A controlled study of vLLM found energy effects and, for some model and benchmark pairs, accuracy movement ([arXiv:2607.09172v2](https://arxiv.org/abs/2607.09172v2)).
- Treat an option's absence as no evidence about its effect. The sample stops at public Python projects with at least 50 stars.

## Related

- [What an Agent's Own Token Cost Estimate Is Good For](agent-cost-self-prediction.md) — the same question asked of a different weak signal
- [Cost-Quality Pareto Measurement for Agent Configurations](cost-quality-pareto-measurement.md) — how to compare two configurations once you measure them yourself
- [Probe-Run Calibration for Predicting Agent Token Spend](probe-run-cost-calibration.md) — getting one measured number instead of a borrowed one
- [Serving-Stack Confounds in Tool-Call Evaluation](../patterns/anti-patterns/serving-stack-confound-tool-call-evaluation.md) — a rarely-configured serving flag deciding a measurement outcome
- [Decomposing Agent Output Variability by Layer (Sampling vs Orchestration State)](../verification/sampling-state-agent-variability-layers.md) — separating sampling settings from the rest of the variability budget
