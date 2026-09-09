---
title: "Pre-Execution Failure Scoring with a Draft Model (Speculative Uncertainty)"
term: "Speculative Uncertainty"
description: "A 4B draft model scores a black-box agent's emitted tokens in one forward pass to predict whether the next action executes cleanly; gating on that score cut token cost 14-19% and cut SWE-Bench Verified resolve rate from 49% to 44%."
tags:
  - testing-verification
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - "speculative uncertainty gate"
  - "draft-model failure scoring"
  - "pre-execution veto gate"
last_reviewed: 2026-09-08
maturity: emerging
status: current
---

# Pre-Execution Failure Scoring with a Draft Model (Speculative Uncertainty)

> A small draft model scores a black-box agent's emitted tokens in one forward pass and predicts whether its next action will execute cleanly.

Speculative Uncertainty runs speculative decoding backwards. Rather than a small model proposing tokens for a large one to check, a 4B open-weight draft reads the large agent's already-generated trajectory and reports how surprised it is, with no access to the agent's logits, weights, activations, or repeated samples ([Grotov and Malykh, arXiv:2609.05274v1](https://arxiv.org/abs/2609.05274v1)). Wired as a veto gate between code generation and execution on a Qwen3-Coder-480B agent, it cut per-call execution error from 21% to 15% on SWE-Bench Verified and average tokens per task by 14%. It also moved the resolved rate from 49% down to 44%. Both numbers are the result, and the second one decides whether you want the first.

## Five conditions before this pays

The authors are explicit about which axis the gate moves. The deployment value "lies in the cost and silent-failure axes, fewer wasted execute-fail-retry cycles and 14–19% lower token spend, rather than in raising the benchmark scores" ([arXiv:2609.05274v1](https://arxiv.org/abs/2609.05274v1)).

1. Your accountability is per-call error rate and token spend, not end-to-end resolve rate. If a dashboard tracks tasks completed, this gate reads as a regression.
2. You can collect and label roughly 10,000 trajectories from your own agent. Alignment is not a tuning detail, it is the method. An untrained Qwen3-4B draft scores .61 AUROC on SWE-Bench Verified against verbalized confidence's .57; distilled on 327,098 labeled action calls it reaches .76 ([arXiv:2609.05274v1](https://arxiv.org/abs/2609.05274v1), Table 1).
3. Your objective is binary and machine-checkable. The paper's oracle is exit code 0 against any error, and it claims nothing beyond that: "we provide no quantitative evidence for other settings."
4. Retries cost real money. The savings come from swapping the execute-fail-retry loop for a cheaper replan. Where a failed attempt costs a second in a local sandbox, there is nothing to recover.
5. You have a GPU on the serving path. The draft adds about 100 ms per step on a single A100, and training it cost about 50 GPU-hours on four ([arXiv:2609.05274v1](https://arxiv.org/abs/2609.05274v1), Table 7).

## Why it works

Two mechanisms carry it, and the second is easy to skip. In speculative decoding a drafted token is accepted with probability `min(1, p/q)`, and the agent's `p` is hidden. The authors' argument is that when the draft tracks the agent well, a high speculative surprisal means the agent "too would face a low acceptance rate there", so the draft's surprisal stands in for the agent's own uncertainty ([arXiv:2609.05274v1](https://arxiv.org/abs/2609.05274v1)). An aligned draft that finds the agent's tokens improbable is reporting that the agent has wandered off its own well-modeled behavior.

The second mechanism is the phase split. An agent trajectory alternates a high-entropy reasoning span with an action span "pinned down by syntax and tool-call structure", so identical surprisal carries different meaning in each. Computing the features separately "keeps the noisy reasoning signal from masking the small, failure-relevant deviations in the action span". The ablation is the evidence: pooling both phases costs 5 to 6 AUROC points, .71 against .76 on SWE-Bench Verified ([arXiv:2609.05274v1](https://arxiv.org/abs/2609.05274v1), Table 1).

## Example

The gate is a threshold on one score. The threshold is fitted on the training split and frozen for every reported evaluation ([arXiv:2609.05274v1](https://arxiv.org/abs/2609.05274v1), Algorithm 1):

```text
features  = draft.teacher_force(window)   # one forward pass, no generation
p_success = calibrator(features)          # L1 logistic regression, 50 features

if p_success >= tau:   execute the action
elif retries < K:      replan: append a failure hint, re-invoke the agent
else:                  abstain and return a low-confidence flag
```

The 50 features are eight statistics for each of three signals (surprisal, gap, entropy) across two phases, plus the two span lengths. The window covers the three most recent steps.

## When this backfires

A high AUROC does not entitle you to intervene. Vasudev and colleagues ran a binary LLM critic with an offline AUROC of 0.94 and measured a 26 percentage point performance collapse on one model while a second was affected by close to zero, naming the cause a "disruption-recovery tradeoff: interventions may recover failing trajectories but also disrupt trajectories that would have succeeded" ([arXiv:2602.03338v1](https://arxiv.org/abs/2602.03338v1)). The Speculative Uncertainty gate is a mild case of the same effect. Its false-veto rate is 0.14 on SWE-Bench Verified and 0.16 on DA-Code, so roughly one blocked action in six or seven would have run fine, and a replan is not guaranteed to recover the ones that would not.

Frozen thresholds are the second exposure. Across 19 uncertainty estimation methods, Bakman and colleagues found most "are highly sensitive to threshold selection when there is a distribution shift in the calibration dataset" ([arXiv:2506.01114v1](https://arxiv.org/abs/2506.01114v1)). Speculative Uncertainty fits its threshold once and carries it to two out-of-distribution benchmarks, which is the move that survey found fragile.

Semantic failures sit outside the objective entirely. Code that runs and computes the wrong answer earns a positive label from an exit-code oracle, so the gate is blind to it by construction. Reach for [evidence-conditioned execution](evidence-conditioned-execution.md) or a behavioral oracle for that class.

The evidence is one preprint and one run. The authors report "single-run point estimates on fixed evaluation sets" with no seed variance or confidence intervals, and say the 5 percentage point task-success change should be read with that in mind ([arXiv:2609.05274v1](https://arxiv.org/abs/2609.05274v1)).

## Key Takeaways

- Buy this for the token bill and the silent-failure rate. On resolve rate the paper's own headline experiment lost 5 points.
- An unaligned draft is close to useless at .61 AUROC. Budget for the trajectory corpus and the distillation run before budgeting for the gate.
- A draft aligned to one agent still transfers. The Qwen-distilled draft reached .69 AUROC scoring Claude 3.5 Sonnet, against .60 untrained ([arXiv:2609.05274v1](https://arxiv.org/abs/2609.05274v1), Table 4).
- The score is not a probability. The authors call it "a failure-likelihood score rather than a calibrated probability", enough for a threshold gate, not for anything that reads the number itself.
- Re-fit the threshold when your task distribution moves, and measure false vetoes, not only true ones.

## Related

- [Evidence-Conditioned Execution: Gate Edits on Observations](evidence-conditioned-execution.md) — the other pre-execution gate, conditioned on what the agent observed rather than on how it wrote
- [Deterministic Precondition Gates for Tool-Using Agents](../patterns/agent-design/deterministic-precondition-gates.md) — the deterministic counterpart, where a predicate replaces a learned score
- [Static Difficulty Estimation for Agent Issue Triage](static-difficulty-estimation-issue-triage.md) — success prediction one level up, at the task rather than the step
- [Execution Budgeting in Agentic Program Repair](execution-budgeting-program-repair.md) — the cost side of the same trade, capping executions instead of vetoing them
- [Validity-Estimate Stopping for Noisy Verify-Repair Loops (VRR-Stop)](validity-estimate-stopping-noisy-repair-loops.md) — what to do when the signal you gate on is itself unreliable
