---
title: "Frozen Playbook Reuse Without Target-Side Validation"
term: "Frozen Playbook Reuse Without Target-Side Validation"
description: "Copying a distilled playbook to a new model, domain, or runtime and certifying it on pass rate alone, which hides the termination and cost damage."
tags:
  - anti-pattern
  - cost-performance
  - instructions
  - arxiv
  - tool-agnostic
aliases:
  - frozen playbook transfer
  - prompt-side playbook portability
  - reusing a distilled playbook on a new target
last_reviewed: 2026-08-07
maturity: emerging
---

# Frozen Playbook Reuse Without Target-Side Validation

> A frozen playbook can hold its single-attempt pass rate on a new target while tool calls climb 2.4x, so an accuracy-only gate passes it.

The anti-pattern is treating a distilled playbook as portable knowledge: validate it on the source setting, freeze it, drop it into a new model or runtime, check the pass rate held, and ship. A prompt-side playbook is a deployment artifact carrying the assumptions of the setting it came from ([Lin, Sun & Zhang, arXiv:2608.05778v1](https://arxiv.org/abs/2608.05778v1)).

## When reuse without measurement is defensible

Four assumptions decide whether reuse holds: workflow structure, target capability, decoding regime, and runtime budget. Skipping fresh measurement is defensible when all four match the source. On ALFWorld under greedy decoding, transfer was positive at every scale tested, gaining +4.9 pp to +12.2 pp on Qwen2.5-32B and +12.6 pp to +23.6 pp on Qwen3-32B and Llama3.1-70B, and it shortened traces ([arXiv:2608.05778v1](https://arxiv.org/abs/2608.05778v1)).

Change one assumption and that evidence stops applying. Raising temperature from zero to 0.3 on Qwen2.5-7B flipped one artifact from helpful to harmful, its 50-step exhaustion rate rising from 58.1% to 79.8%. Across 135 route-level transfers on the TAU2-Bench service-agent suite, global Holm correction retained exactly one positive route ([arXiv:2608.05778v1](https://arxiv.org/abs/2608.05778v1)).

## The cost the pass rate hides

An artifact distilled from 32K-context trajectories, deployed under a 128K-context runtime, kept working and got much more expensive. Total tool calls rose from 10.4 to 24.7 per task, roughly 2.4x. Pass@1 moved between 0 and +6 pp, so a gate reading single-attempt accuracy alone would have passed it, while Pass@3 fell by 16 pp ([arXiv:2608.05778v1](https://arxiv.org/abs/2608.05778v1)).

## Why it works

A distilled playbook encodes two kinds of guidance with different portability. First-try heuristics are about the domain: which tool to reach for, what to search first, how to recover from a known error. Termination heuristics are calibrated against the source runtime budget. Move that budget and the stopping rule no longer fires at the right point, so the agent re-queries and defers submission. In the 128K case, trajectories containing an identical repeated query rose from 17.3% to 39.3% and submissions within ten tool calls fell from 78% to 30% ([arXiv:2608.05778v1](https://arxiv.org/abs/2608.05778v1)). Single-attempt pass rate is blind here because the half of the playbook that transfers is the half it measures.

## When this backfires

A target-side validation grid before every reuse is not always worth its cost.

- Near-identical target: with the same model family, domain, decoding, and budget, the grid confirms what the source study already establishes.
- Genuine cold start: validation needs target-side failure data, which is exactly what a cold-start deployment lacks.
- Low-volume or supervised runs: a 2.4x tool-call increase across a few daily invocations costs less than the audit that finds it.
- Many artifacts times many targets: per-route tests go under-powered, which the authors report of their own grid, and unadjusted route-level results then pick winners from noise ([arXiv:2608.05778v1](https://arxiv.org/abs/2608.05778v1)).
- Screening instead of measurement: the same authors' model-judged cost pre-screen raised no alert on a case carrying 347.1% held-out cost inflation ([arXiv:2608.05778v1](https://arxiv.org/abs/2608.05778v1)).

Transfer also succeeds outside those conditions. A self-evolving security-auditing playbook needed "only minor adaptation to run under a different LLM or harness", lifting Qwen3.6-27B from 2.4% to 6.5% ([EvoHunt, arXiv:2606.16420v1](https://arxiv.org/abs/2606.16420v1)). Portability is unproven until measured on the target, not impossible.

## Example

Both blocks describe the same real transfer run, differing only in which metrics the gate reads.

**Before — certifying on single-attempt accuracy alone:**

```text
Pass@1:  0 to +6 pp across conditions    -> no regression, ship it
```

**After — certifying on accuracy, termination, protocol, and cost:**

```text
Pass@1:                     0 to +6 pp     -> no regression
Pass@3:                     -16 pp         -> regression
total tool calls:           10.4 -> 24.7   -> ~2.4x cost
identical repeated query:   17.3% -> 39.3% -> termination broken
submitted <=10 tool calls:  78% -> 30%     -> stopping deferred
                                           -> hold, redistill on target
```

## Key Takeaways

- Certify a transferred playbook on accuracy, termination behavior, protocol compatibility, and cost. Pass@1 was the one metric of those that stayed clean.
- Add tool-call volume and early-submission rate to the gate, since both moved on the 128K target while Pass@1 held.
- Treat a context-window, tool-budget, or decoding change as a new target, not a configuration tweak.
- The authors offer no selector or threshold for deciding when transfer is safe, so freeze your decision criteria before you measure and keep a rollback path.
- Prefer a domain-matched candidate playbook: matched-domain transfer averaged +1.72 pp over mismatched (CI95 +0.25 to +2.97) on TAU2-Bench ([arXiv:2608.05778v1](https://arxiv.org/abs/2608.05778v1)).

## Related

- [Token Reduction Mistaken for Cost Reduction](token-reduction-not-cost-reduction.md) — the same measurement error, where a proxy metric certifies a cost regression
- [Stale AI Configuration Artifacts (Context Rot)](stale-ai-configuration-artifacts.md) — config that was correct for a setting that no longer exists
- [Cargo Cult Agent Setup: Copying Without Understanding](cargo-cult-agent-setup.md) — adopting a configuration whose assumptions you have not checked
- [Prompt-Rewrite Discipline on Cross-Generation Model Migration](../../instructions/prompt-rewrite-on-cross-generation-migration.md) — what to rebuild when the target model generation changes
- [Evolving Playbooks: Incremental Context That Preserves Knowledge](../../context-engineering/evolving-playbooks.md) — how the playbooks being transferred get built in the first place
