---
title: "Bottom-Up Harness Construction for a Self-Hosted Model"
term: "Bottom-Up Harness Construction"
description: "Start a fixed self-hosted model on a near-empty harness and admit a component only when it clears a score margin and a justification check. Parity at about 3k lines."
tags:
  - agent-design
  - tool-agnostic
  - pattern
  - arxiv
  - harness-engineering
aliases:
  - CLEO harness optimization
  - grow-only harness construction
  - justification-gated harness
last_reviewed: 2026-11-05
maturity: emerging
---

# Bottom-Up Harness Construction for a Self-Hosted Model

> Start a fixed self-hosted model on a near-empty harness and keep a component only when it beats a score margin and passes a justification check.

Build the harness up from almost nothing when the model is fixed and self-hosted, a security review prices every tool and line of harness code, and you have an expert-labeled question set to score against. Two more conditions apply. The base model must already handle multi-step tool use, and a frontier supervisor must be allowed to read run traces (see [When this backfires](#when-this-backfires)). On a held-out investigative-analysis benchmark, the bottom-up harness reached an 83.8% pass rate at about 3k lines of code. A bare Claude Code SDK on the same model scored 85.0% ([arXiv:2611.03434v1](https://arxiv.org/abs/2611.03434v1)). The win is size at near parity, not accuracy.

## The conditions

Harness size is a cost where "every new tool and every line of harness code must be inspected, justified, and often certified before deployment" ([arXiv:2611.03434v1](https://arxiv.org/abs/2611.03434v1)). 
The model stays fixed. The team works with "self-hostable (on-premises), open-weights LLMs", changes only the harness, and reports results with GLM-5.1 ([arXiv:2611.03434v1](https://arxiv.org/abs/2611.03434v1)). A model swap reopens the fit, as [per-model harness tuning](per-model-harness-tuning.md) describes.

## How the loop runs

1. Start near empty. The first agent is a ReAct-style loop "with a short list of terminal tools—ls, read, grep, a sandboxed non-persistent Python—and nothing else" ([arXiv:2611.03434v1](https://arxiv.org/abs/2611.03434v1)).
2. A frontier supervisor model (Opus-4.8 in the paper) proposes one change at a time: a tool, a guardrail, or a loop tweak ([arXiv:2611.03434v1](https://arxiv.org/abs/2611.03434v1), Algorithm 1).
3. Keep the change only if it clears two gates. It must raise the pass-rate and soft-score objective by a set margin. It must also survive "a justification check that asks whether the edit is generic, auditable, and as lean as possible" ([arXiv:2611.03434v1](https://arxiv.org/abs/2611.03434v1)).
4. Score each candidate on 44 questions: a fixed core of 32 plus 12 drawn fresh each iteration. Swap in an out-of-distribution pool from time to time. Keep a 240-question held-out set that the supervisor loop never sees ([arXiv:2611.03434v1](https://arxiv.org/abs/2611.03434v1)).

The second gate does work the first cannot. A `cite()` helper was proposed after error analysis showed the judge penalizing answers with missing evidence. It "was reverted: the agent rarely used it, so the change failed the justification gate". The changes that stayed included read/write memory tools and "a non-answer safety net with a retry loop" ([arXiv:2611.03434v1](https://arxiv.org/abs/2611.03434v1)).

## What the results show

All four harnesses ran GLM-5.1 against the same 240 held-out questions ([arXiv:2611.03434v1](https://arxiv.org/abs/2611.03434v1), Table 1):

| Harness | Lines of code | Pass rate | Latency |
|---|---|---|---|
| Claude Code SDK, bare | about 512k | 85.0% | 76s |
| PI, generic prompt | about 75k | 80.8% | 126s |
| PI, CLEO's optimized prompt | about 75k | 83.8% | 121s |
| CLEO | about 3k | 83.8% | 114s |

The authors put the 1.2-point gap at "roughly three questions" and "read this as practical parity rather than a ranking". The 512k figure is a reported estimate they "could not independently verify", because the SDK ships minified ([arXiv:2611.03434v1](https://arxiv.org/abs/2611.03434v1)).

The optimized prompt alone moved the lean PI harness from 80.8% to 83.8%, which equals CLEO. In this table the prompt work accounts for the gain over bare PI, and the bottom-up harness accounts for the size: about 3k lines against about 75k.

## Why it works

Pruning a large harness is the slow path. The authors build up "rather than pruning a large off-the-shelf harness: in a broad harness much must be removed, and deciding which capabilities are unnecessary is itself a slow security and engineering exercise" ([arXiv:2611.03434v1](https://arxiv.org/abs/2611.03434v1)). A grow-only loop never has to make that call, and each component it keeps arrives with the justification a reviewer would ask for. One control supports the direction. A top-down loop from PI that encouraged removals "matched bottom-up on accuracy while barely shrinking the harness" ([arXiv:2611.03434v1](https://arxiv.org/abs/2611.03434v1)).

## When this backfires

- No review cost. If nobody audits tools and code one by one, the size win buys little: the bare large harness scored higher and ran fastest.
- No trusted ground truth. The margin gate scores against expert answers through an LLM judge that the authors "did not validate systematically" ([arXiv:2611.03434v1](https://arxiv.org/abs/2611.03434v1)). A gain smaller than judge noise can pass.
- Small per-iteration sets. On 44 questions, one answer moves the pass rate by about 2.3 points. The held-out set and the out-of-distribution swaps catch a fit to the optimization pool, so keep both.
- A weak base model. The stated scope is "a base model already capable of multi-step tool use, one investigative domain" ([arXiv:2611.03434v1](https://arxiv.org/abs/2611.03434v1)).
- Automated search may not beat simpler compute. One study on Terminal-Bench 2.1 found "that automatic harness evolution fails to outperform simple test-time scaling methods both with and without test cases, and exhibits limited generalization" ([arXiv:2607.12227v4](https://arxiv.org/abs/2607.12227v4)).
- Traces that cannot leave the enclave. The supervisor that judges each change reads run traces, and the paper used a frontier model (Opus-4.8) for it ([arXiv:2611.03434v1](https://arxiv.org/abs/2611.03434v1)). It reports no run with a self-hosted supervisor.

## Key Takeaways

- Choose bottom-up construction to cut the audit bill, not to gain accuracy.
- Put the justification gate next to the score gate. A component the agent rarely calls can still pass on score, and only the second gate removes it.
- Run the optimized prompt on a lean off-the-shelf harness as a control. If it matches, your harness code buys size and no extra accuracy.
- Never show the held-out set to the supervisor loop. A 44-question set is too small to trust alone.

## Related

- [Deletion and Cost Rules for an Evolving Agent Harness](harness-deletion-and-cost-rules.md) — acceptance rules for a search that edits a large harness, where this page starts from an empty one
- [Isometric Harness Ablation](isometric-harness-ablation.md) — removes one subsystem at a time to rank investment, the top-down counterpart
- [Prompt-Only Baseline Before a Specialized Agent Subsystem](prompt-only-baseline-before-specialized-subsystem.md) — measure the bare loop before adding a subsystem
- [Local Model Viability Factors for Coding](local-model-viability-for-coding.md) — when a self-hosted model is good enough to fit a harness to at all
- [Harness Hill-Climbing](harness-hill-climbing.md) — eval-driven harness iteration, the general loop this page constrains
