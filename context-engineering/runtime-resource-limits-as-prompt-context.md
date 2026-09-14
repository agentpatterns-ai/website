---
title: "Runtime Resource Limits as Prompt Context"
term: "Runtime Resource Limit Disclosure"
description: "State the memory ceiling and time budget the generated code must run under, so the model picks a bounded implementation on its first attempt instead of after an out-of-memory kill."
tags:
  - context-engineering
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - execution contract disclosure
  - substrate-aware agent planning
  - resource budget in the prompt
last_reviewed: 2026-09-08
maturity: emerging
---

# Runtime Resource Limits as Prompt Context

> Stating the memory ceiling and time budget in the prompt changes which implementation a model writes, before any execution feedback exists.

Your container has a memory limit and the model writing code for it usually does not know the number. Adding a RAM ceiling and a wall-time target to the prompt moved measured peak memory down in 13 of 14 comparisons across three frontier models, and cut mean wall time in every cohort by up to 3.09x ([Agrawal, 2026](https://arxiv.org/abs/2609.05232v1)). No algorithm was prescribed and no failed run was needed first.

## When this applies

The evidence is one task, five generations per cell, and an unreviewed preprint. Four conditions have to hold before the technique earns its prompt tokens.

1. The task admits several correct implementations with different allocation profiles. Agrawal's benchmark sums all pairwise Euclidean distances over an 8,000 by 1,024 float32 matrix, where a full distance matrix needs 244.14 MiB and a blocked traversal is equally correct at a fraction of it ([Agrawal, 2026](https://arxiv.org/abs/2609.05232v1)). Where correctness pins the shape, disclosure has nothing to choose between.
2. The limit binds. Under a generous ceiling the contract changes nothing you can measure.
3. You want the budget approached rather than guaranteed. Compliance is not what disclosure buys.
4. Something in the harness knows the number. Kubernetes schedules on requests and enforces limits at runtime ([Kubernetes documentation](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)), so a deployment config or job spec usually holds the figure the prompt should carry.

## What to state, and what moves

The intervention is the task specification plus the disclosed envelope ([Agrawal, 2026](https://arxiv.org/abs/2609.05232v1)):

```text
Execution environment:
RAM limit: 128 MB.
Execution time limit: 10.0 seconds.
```

No block size, no data type, no algorithm. Implementation choice is what changed: block sizing, keeping intermediates in float32 instead of promoting them, traversing only the upper triangle, and reusing in-place or memory-mapped buffers. Mean peak memory fell from 256.48 to 107.82 MiB for Claude Opus 5, 118.63 to 64.61 MiB for GPT-5.6-Sol, and 452.36 to 158.16 MiB for Gemini 3.7 Flash ([Agrawal, 2026](https://arxiv.org/abs/2609.05232v1)).

The paper records a distribution shift. Some unaware programs already blocked, and aware ones picked differing block geometries instead of converging on a single answer.

## Why it works

Nothing in a bare task specification distinguishes two correct programs whose peak memory differs by 4x, so the model writes the most idiomatic one. That default is measurable. Across 30 models, ENAMEL attributes the shortfall against expert-level efficient code partly to models being "barely aware of implementation optimization" ([Qiu et al., 2025](https://arxiv.org/abs/2406.06647v4)). EffiBench measures GPT-4 code averaging 3.12x the execution time of human canonical solutions ([Huang et al., 2025](https://arxiv.org/abs/2402.02037v6)). Stating the envelope turns it into a selection criterion at generation time. The harness already held the number; only the model's context lacked it, which is the gap [environment specification](environment-specification-as-context.md) closes on the dependency-version axis.

## When this backfires

Disclosure is not enforcement. Gemini 3.7 Flash cut mean peak memory 65% under the 128 MB contract and still landed only 2 of 5 programs inside it, against 0 of 5 without ([Agrawal, 2026](https://arxiv.org/abs/2609.05232v1)). If the ceiling must hold, the runtime has to hold it.

Tighter contracts buy memory with time. Moving the stated limit from 128 MB to 96 MB raised mean wall time 5.3% for Claude, 9.1% for GPT, and 11.9% for Gemini inside each aware cohort, though all three stayed faster than their unaware references ([Agrawal, 2026](https://arxiv.org/abs/2609.05232v1)).

A prompt line does not fix an algorithmic gap. ENAMEL finds models struggle at designing advanced algorithms, separately from implementation choice ([Qiu et al., 2025](https://arxiv.org/abs/2406.06647v4)). In code translation, Zhang et al. found the runtime-efficiency gap "cannot be remedied through prompt engineering alone" and reached for multi-candidate generation with explicit selection instead ([Zhang et al., 2026](https://arxiv.org/abs/2606.17683v1)).

Efficiency-flavored instructions have a history of backfiring, which is why [token-efficient code generation](../token-engineering/token-efficient-code-generation.md) argues for structural rules over prompt-level pressure. A resource contract is narrower than a general instruction to be efficient, and the narrowness is doing the work. Keep it to numbers.

A stale number is worse than no number. A ceiling pinned into an instruction file keeps steering generation toward a budget the deployment target no longer has, and nothing reports the drift.

## Example

**Before** — the task alone:

```text
Write a self-contained, executable Python script to process 'vectors.npy'
(containing an 8,000 x 1,024 float32 matrix). Compute the total sum of all
pairwise Euclidean distances between rows: sum_{i,j} ||v_i - v_j||_2 and print:
'TOTAL_DIST:<value>'. Constraint: Use ONLY numpy and standard library modules.
Do NOT import scipy or external packages.
```

**After** — the identical task with the operating envelope appended:

```text
Write a self-contained, executable Python script to process 'vectors.npy'
(containing an 8,000 x 1,024 float32 matrix). Compute the total sum of all
pairwise Euclidean distances between rows: sum_{i,j} ||v_i - v_j||_2 and print:
'TOTAL_DIST:<value>'. Constraint: Use ONLY numpy and standard library modules.
Do NOT import scipy or external packages.

Execution environment:
RAM limit: 128 MB.
Execution time limit: 10.0 seconds.
```

These are the frozen prompts from Agrawal's reproducibility appendix ([Agrawal, 2026](https://arxiv.org/abs/2609.05232v1)). Correct-and-under-128-MiB outcomes moved from 0 of 5 to 5 of 5 for Claude Opus 5 under this change, and from 0 of 5 to 2 of 5 for Gemini 3.7 Flash.

## Key Takeaways

- Put the deployment limit in the prompt when your harness already knows it, and keep it to a number rather than an instruction to be efficient.
- Expect the memory distribution to move and expect misses. A 65% mean reduction still left 3 of 5 Gemini programs over the stated ceiling ([Agrawal, 2026](https://arxiv.org/abs/2609.05232v1)).
- Keep runtime enforcement and execution-feedback repair. Disclosure acts on the first generation, a different moment in the loop, and substitutes for neither.
- Tightening the stated budget trades wall time for memory, so state the limit you actually have rather than the smallest one you can imagine.
- Treat the effect size as provisional: one numerical task, five generations per cell, single-turn generation, and a v1 preprint with no significance testing.

## Sources

- [Agrawal, "Substrate-Aware AI Agents," 2026](https://arxiv.org/abs/2609.05232v1) — the two-condition study, prompts, and resource profiles.
- [Qiu et al., "ENAMEL," 2025](https://arxiv.org/abs/2406.06647v4) — 30 models short of expert-level efficient code.
- [Huang et al., "EffiBench," 2025](https://arxiv.org/abs/2402.02037v6) — GPT-4 code averages 3.12x canonical execution time.
- [Zhang et al., "Code Translation Efficiency Gaps," 2026](https://arxiv.org/abs/2606.17683v1) — the gap prompt engineering alone did not close.

## Related

- [Environment Specification as Context](environment-specification-as-context.md) — the dependency-version axis of the same execution context.
- [Execution Budgeting in Agentic Program Repair](../verification/execution-budgeting-program-repair.md) — budgets how often a repair agent runs tests, rather than what the generated code may consume.
- [Token-Efficient Code Generation](../token-engineering/token-efficient-code-generation.md) — the opposing evidence on prompt-level efficiency pressure, and the structural alternative.
- [Profiler-Guided Optimization Loops for Coding Agents](../verification/profiler-guided-optimization-loop.md) — the after-execution half, where measured hotspots drive the rewrite.
- [Cost-Aware Agent Design](../token-engineering/cost-aware-agent-design.md) — routing by cost at the model layer rather than the generated-code layer.
