---
title: "Four Reporting Levels for Agent Working Memory Evaluation"
term: "Working Memory Reporting Levels"
description: "Two memory policies at one token cap deliver different context and spend different management work; report stored state, delivered context, management work, and outcome separately."
aliases:
  - agent working memory reporting levels
  - four-level memory evaluation
  - delivered context measurement
tags:
  - context-engineering
  - evals
  - arxiv
  - tool-agnostic
last_reviewed: 2026-09-02
maturity: emerging
status: current
---

# Four Reporting Levels for Agent Working Memory Evaluation

> Two memory policies at the same token cap can deliver different context and spend different management work, so report both alongside the outcome.

Check the precondition before building any of this. The four levels exist to keep two memory-management arms honest against each other. With one policy and no comparison arm, no shared cap is being violated and the instrumentation has nothing to report.

## The token cap is not a controlled variable

A nominal budget decides which working-memory objects are admissible. It does not decide what gets assembled into the prompt on a given step. Compare arms on their median managed-state token count across steps, calling a pair matched when the larger median is at most 1.10 times the smaller: "None of the ten constrained-arm pairs matches on all eight complete tasks; FIFO–GA matches on six of eight, with a largest gap of 18.7%" ([arXiv:2608.31057v1](https://arxiv.org/abs/2608.31057v1)). The authors read that as meaning "a contrast at a common cap is therefore partly a contrast in delivered context" ([arXiv:2608.31057v1](https://arxiv.org/abs/2608.31057v1)).

## The four levels

Record all four per arm, per task, before reading any outcome number ([arXiv:2608.31057v1](https://arxiv.org/abs/2608.31057v1)).

| Level | Record | Catches |
|---|---|---|
| Stored state | Object type, size, representation, residency | A single stored-token figure that hides which type is eating the budget |
| Delivered context | Tokens actually assembled per step, per arm | Arms that share a cap and not an input |
| Management work | Auxiliary model calls by type, embeddings, wall time | The price a policy pays outside the budget it is judged on |
| Task or process outcome | Completion, repeated calls, stopping reason, paired uncertainty | The number everyone already reports |

The stored-state level is worth splitting by object type because the types are not alike. Across 55 archived coding-agent trajectories, "tool outputs account for 55.5% of pooled content volume and 40.2% of retention-weighted cost; artifacts account for 28.3% and 38.9%, respectively" ([arXiv:2608.31057v1](https://arxiv.org/abs/2608.31057v1)). Artifacts run a median 624 proxy tokens against 73 for tool outputs, and compress to a mean 0.150 of raw size against 0.673 ([arXiv:2608.31057v1](https://arxiv.org/abs/2608.31057v1)). One aggregate number over that spread tells you nothing about what your policy moved.

## Why it works

An outcome metric compounds three differences a comparison needs kept apart: what each arm stored, what it delivered, and what it spent to decide. Arms sharing a cap do not carry matched stored state, and the management cost sits outside the budget under test. The retrieval policy adds 285 importance calls and object-aware compression adds 169 summary calls; whole-run wall time rose on all eight tasks by a mean 67.45 seconds, which the authors caution "include changed tool paths and cannot isolate rating latency" ([arXiv:2608.31057v1](https://arxiv.org/abs/2608.31057v1)). None of that appears in a stored-token figure, so an outcome difference cannot be attributed to any one of the three. Weinberger and Hozez reach the same structural conclusion from [billed dollars on Claude Code](../patterns/anti-patterns/token-reduction-not-cost-reduction.md): token reduction correlated with cost reduction at only Pearson r = 0.15, because "prompt-cache creation and reads dominate the measured input-side cost" ([arXiv:2607.12161v5](https://arxiv.org/abs/2607.12161v5)).

## When this backfires

- Nothing in the working memory is large. The stored-state split pays for itself on the size and compressibility spread between artifacts and tool outputs ([arXiv:2608.31057v1](https://arxiv.org/abs/2608.31057v1)). An agent whose context is all short tool outputs has no such spread to surface.
- Your per-arm sample is thin. Four reported levels on eight held-out tasks produce four levels of noise. The same paper's object-aware policy showed a calibration contrast of −1.633 repeated calls against FIFO and a held-out contrast of −0.500, and no held-out contrast survived Holm correction ([arXiv:2608.31057v1](https://arxiv.org/abs/2608.31057v1)).
- You need one number to decide with. Weinberger and Hozez argue the opposite shape, that optimization "should therefore be evaluated at the level of cost per successful task, including cache behavior, trajectory changes, and correctness rather than token counts alone" ([arXiv:2607.12161v5](https://arxiv.org/abs/2607.12161v5)). Four tables invite picking the level that flatters the preferred arm.
- The paper gets cited for its policies. It does not support them. Its own evaluation "shows that calibration gains may not transfer to held-out tasks" ([arXiv:2608.31057v1](https://arxiv.org/abs/2608.31057v1)); the reporting shape is what the evidence carries.

## Example

An exploratory replay on an NVIDIA GB10 serving Qwen2.5-Coder-32B, under a frozen 32,768-token limit, found a constraint no nominal budget expresses. The unconstrained arm "reached 37,883 tokens on one task, so 6 of its 25 steps exceeded that limit, while every constrained arm stayed at or below 16,643 tokens: a hard feasibility boundary on delivered context, not a hardware-memory advantage for any policy" ([arXiv:2608.31057v1](https://arxiv.org/abs/2608.31057v1)). A comparison read on completion rate alone would have scored that arm on the steps that fit.

## Key Takeaways

- Log delivered tokens per step per arm. A shared cap is a label on the configuration, not a measurement of what the model received.
- Put auxiliary model calls and wall time on the policy's bill. The retrieval policy spends 285 extra importance calls to save stored tokens ([arXiv:2608.31057v1](https://arxiv.org/abs/2608.31057v1)), which moves cost rather than removing it.
- Split stored state by object type before comparing totals. Artifacts compress to a mean 0.150 of raw size and tool outputs to 0.673, and one total hides that ([arXiv:2608.31057v1](https://arxiv.org/abs/2608.31057v1)).
- Cite this work for how to report, not for which policy to run. Its held-out contrasts do not survive correction.

## Related

- [Measuring Reacquisition Cost Under Context Compaction](reacquisition-cost-measurement.md) — one process-level metric in detail: splitting tool calls into retrieval and execution.
- [Choosing a Compression Budget for Agent Control Context](control-context-compression-budget.md) — setting severity within an arm, once the arms are comparable.
- [Per-Type Retention Policy for Agent Compaction](per-type-retention-under-compaction.md) — acting on object heterogeneity instead of only measuring it.
- [Token Reduction Mistaken for Cost Reduction](../patterns/anti-patterns/token-reduction-not-cost-reduction.md) — the same proxy failure measured in billed dollars.
- [Context Compression Strategies: Offloading and Summarization](context-compression-strategies.md) — the mechanisms these arms implement.
