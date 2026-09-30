---
title: "Action-Class Decomposition for Tool-Calling Evals"
term: "Action-Class Decomposition"
description: "Split a multi-turn tool-calling score into call, ask, refuse, and confirm. An end-state grader passes trajectories that picked the wrong class, and the split is what finds them."
tags:
  - testing-verification
  - evals
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - gold action recall
  - action-class diagnostic
  - per-class tool-calling evaluation
last_reviewed: 2026-09-28
maturity: emerging
---

# Action-Class Decomposition for Tool-Calling Evals

> An end-state grader passes a trajectory that called a tool where it should have asked. Action-class recall beside that score shows the miss.

Action-class decomposition scores each turn against the kind of action its context called for. Zhao et al. use four classes: call, ask, refuse, and confirm. They report Gold Action Recall, the share of cases emitting the required class at any turn, beside the aggregate pass rate ([arXiv:2609.00949v2](https://arxiv.org/abs/2609.00949v2)).

## What you need before the numbers mean anything

Three preconditions. Without them the columns return noise.

- A gold class per scenario category. Recall scores against a label the benchmark supplies, and the authors say the same of their probes: "they need the category-level gold action class to choose which seam to monitor" ([arXiv:2609.00949v2](https://arxiv.org/abs/2609.00949v2)). Nobody has written that label for your production traces.
- Scenarios that withhold something. Two classes appear only when a task omits a required argument or removes a needed tool, so well-specified tasks leave two columns empty ([arXiv:2609.00949v2](https://arxiv.org/abs/2609.00949v2)).
- A variance figure for your harness. An audit of four benchmark families reviewed 496 tasks and found "an 18.5% misalignment rate" between evaluator and human, with 23 repeats of one setup spanning "18.9 percentage points" ([arXiv:2607.02577v1](https://arxiv.org/abs/2607.02577v1)). A gap under your rerun spread is not a finding.

## Read the two columns against each other

Where passing requires the gold class, accuracy cannot exceed recall, so the pair is a bound that checks itself ([arXiv:2609.00949v2](https://arxiv.org/abs/2609.00949v2)).

| Signature | Reading | Where the fix goes |
|---|---|---|
| Accuracy above recall | The grader passed trajectories that chose the wrong class | The eval, before the model |
| Recall far above accuracy | Right class, then wrong tool, arguments, or state tracking | Execution downstream of the decision |

On a 26-checkpoint BFCL v3 multi-turn panel, every row emitted the gold call class on both call-required categories at 77% recall or above ([arXiv:2609.00949v2](https://arxiv.org/abs/2609.00949v2)). Accuracy trailed by 17 points or more, so the whole gap is execution. "Without the GAR column this is indistinguishable from never emitting the call, and the two failures call for different fixes" ([arXiv:2609.00949v2](https://arxiv.org/abs/2609.00949v2)).

The missing-input categories split the other way, and unevenly. General-purpose families ask readily and refuse rarely. The tool-call-specialized cluster shows negative gaps on both missing-input categories. On the ask-required category, Hammer-2.1-7B reached 0.5% recall against Qwen3-8B's 84.0% in the same 7-to-8-billion band, because "Calibration is family-mediated, not size-mediated" ([arXiv:2609.00949v2](https://arxiv.org/abs/2609.00949v2)). xLAM-2-70b topped the open-weight accuracy panel at 77.5% while posting negative gaps on both missing-input categories, with masking accounting for up to 66 points of apparent accuracy across that cluster ([arXiv:2609.00949v2](https://arxiv.org/abs/2609.00949v2)).

Run the confirm class first if your agent writes anything. Against a written policy the benchmark's reward never checks, Qwen3-14B obtained consent on 28.8% of its airline database writes, while 36.4% of those writes sat in passing trajectories. "Unconfirmed writes therefore pass routinely" ([arXiv:2609.00949v2](https://arxiv.org/abs/2609.00949v2)).

Listing the available tools in the prompt does not substitute for measuring the refuse column. Of 78 audited refusal misses on xLAM-2-8b, 92.3% called the held-out function outright: "the prompt-level toolset constraint does not block emission of a held-out function" ([arXiv:2609.00949v2](https://arxiv.org/abs/2609.00949v2)).

## Why it works

The grader compares runtime state against a gold reference trajectory and skips turns whose reference is empty. It scores where a run ended, not what it decided ([arXiv:2609.00949v2](https://arxiv.org/abs/2609.00949v2)). When a scenario withholds an argument, the benchmark hands it over on the next turn. A model that fabricated a placeholder rather than asking still reaches the gold end state. The authors name the property: "Acc tracks state outcomes regardless of action-class emission" ([arXiv:2609.00949v2](https://arxiv.org/abs/2609.00949v2)). That masks under-refusal on the refuse-required category and exposes post-ask execution failure on the ask-required one ([arXiv:2609.00949v2](https://arxiv.org/abs/2609.00949v2)). Scoring each emission against the class its context required restores what the end state erased. The benchmark audit above reaches the same prescription independently, arguing "for decomposed metrics that separately measure tool invocation, task completion, and outcome verification" ([arXiv:2607.02577v1](https://arxiv.org/abs/2607.02577v1)).

## When this backfires

- You treat the diagnosis as a fix. The framework "diagnoses rather than corrects". One context-only perturbation raised Qwen3-8B accuracy 11.5 points on the scenario where it cost ToolACE-2-8B 21.0 points. Two variants of a second probe pulled apart: "Retry shifts emission policy at the cost of trajectory completability; bypass preserves completability and leaves emission policy unchanged" ([arXiv:2609.00949v2](https://arxiv.org/abs/2609.00949v2)). Both probes run on 6 of the 26 checkpoints, on BFCL v3. Only an adapted variant of the first probe is replicated on tau^2-retail, across 3 families.
- Your agent's wording does not match the cue list. The three non-call classes are read from textual cues, under a priority that puts a parsed call first ([arXiv:2609.00949v2](https://arxiv.org/abs/2609.00949v2)). An agent explaining a refusal in the turn it also calls scores as calling.
- You read high call recall as recognition. "High emission on the tool-call categories does not prove context-sensitive recognition: a model that blindly calls tools scores the same" ([arXiv:2609.00949v2](https://arxiv.org/abs/2609.00949v2)).
- You conclude the deficit is universal. Another group calls over-calling "a consistent tendency" traced to an activation-level offset, correctable in closed form ([arXiv:2605.18882v1](https://arxiv.org/abs/2605.18882v1)). If one steering fix generalizes, a per-scenario profile earns less than a single global correction.

## Key Takeaways

- Report per-class recall next to the aggregate score. Accuracy above recall can only mean the grader passed a wrong-class trajectory ([arXiv:2609.00949v2](https://arxiv.org/abs/2609.00949v2)).
- Run the confirm class first if the agent writes. On the same benchmark the closed anchors confirmed 89.2% to 100% of their writes and Qwen3-14B confirmed 28.8% ([arXiv:2609.00949v2](https://arxiv.org/abs/2609.00949v2)).
- Treat asking and refusing as separate capabilities. Refusal "contradicts a function-calling recipe that optimizes for emitting a call, while ask sits closer to natural dialogue" ([arXiv:2609.00949v2](https://arxiv.org/abs/2609.00949v2)).
- Measure your rerun spread first. One audited suite moved 18.9 points across repeats of the same setup ([arXiv:2607.02577v1](https://arxiv.org/abs/2607.02577v1)).
- Pick the next model on its class profile, not its parameter count. Scaling inside one family barely moved class choice on this panel ([arXiv:2609.00949v2](https://arxiv.org/abs/2609.00949v2)).

## Related

- [Trajectory Decomposition: Diagnose Where Coding Agents Fail](trajectory-decomposition-diagnosis.md) — the same split taken along the stage axis, scoring search, read, and edit separately.
- [Audit the Noise Floor Before Trusting a Benchmark Gap](benchmark-noise-floor-audit.md) — how to get the rerun and perturbation floors a per-class gap has to clear.
- [Canary Tools for Diagnosing Tool-Selection Reasoning](canary-tools-tool-selection-diagnosis.md) — planted decoy tools that name the cause once the wrong tool is picked.
- [Informed Abstention as a Tool-Boundary Runtime Gate](../patterns/agent-design/informed-abstention-tool-boundary-gate.md) — the runtime counterpart, enforcing the ask, refuse, and confirm decisions this technique measures.
- [Task Feasibility Awareness: Stop Before You Start](../patterns/agent-design/task-feasibility-awareness.md) — checking the tool manifest up front, the behavior a low refusal recall predicts is missing.
