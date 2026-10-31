---
title: "Random Restart as the Baseline for Agent Early Stopping"
term: "Random Restart as the Stopping Baseline"
description: "A kill switch measured against random restart proves nothing about compute. Across 224 budget-threshold replays, letting the run continue won 216."
tags:
  - anti-pattern
  - tool-agnostic
  - cost-performance
  - testing-verification
  - arxiv
aliases:
  - pooled AUC as stopping evidence
  - early stopping without a continuation baseline
  - restart-versus-random comparison
last_reviewed: 2026-10-29
maturity: emerging
---

# Random Restart as the Baseline for Agent Early Stopping

> A mid-run kill switch validated against random restart has been measured against the wrong thing. The baseline it has to beat is doing nothing.

Shipping a mid-run stop on two numbers, a monitor's pooled AUC and a solve-rate win over random restart, leaves both of its real decisions unmeasured. Pooled AUC says which repository issues are hard, which a pre-execution filter tells you for free. A win over random restart says the stopping quota landed on better-chosen runs than a coin flip, not that stopping beat continuing. The scope is narrow and load-bearing: this indicts cold restart under a shared token budget on repository-scale work, where the replacement starts from an empty context. Three other stopping designs clear the same bar, and the section on when this backfires names them.

## The two measurements that are missing

Task difficulty dominates a monitor's pooled score. Repository outcomes cluster hard by issue, at an intraclass correlation of at least 0.71 in all four corpora studied. A predictor built from nothing but a task's own solve fraction therefore reaches pooled AUC 0.97 at the 5k-token landmark, while scoring 0.50 within a task by construction ([arXiv:2610.35971v1](https://arxiv.org/abs/2610.35971v1)). Report within-task AUC instead: given two attempts on the same issue, one that solved it and one that did not, how often does the monitor rank them correctly? Count models, frozen initial-turn embeddings, task-conditional rankers trained only on mixed-outcome issues, cross-setting transfers, and a fine-tuned Qwen3-0.6B monitor over 32,406 attempts at 20k tokens all land around 0.50. The frozen embeddings score 0.49 [0.48, 0.50], and the neural monitor's 90% interval of [0.48, 0.51] lies strictly inside a [0.45, 0.55] equivalence bound.

Signal starvation does not explain that. By 20k tokens, 87.51% of runs in the primary corpus had already executed a test and 32.80% had edited code, and "detecting an early test invocation or edit action does not establish whether the interaction was diagnostic or whether its outcome distinguished eventual task resolution from failure."

Continuation is the second missing measurement. Across 224 combinations of four settings, four token caps and seven score thresholds, "uninterrupted continuation achieves higher solve rates at lower mean token cost than both restart policies" in 216 of them, and in 56 of 56 at the 75k cap. Seven of the eight exceptions are exact ties at the 30k cap.

## Why it works

Continuation wins for a reason you can write down. A stopping policy's expected solve rate is the sum over attempts of that attempt's own success if continued, plus the stopping indicator times the difference between the replacement's expected credit and that success ([arXiv:2610.35971v1](https://arxiv.org/abs/2610.35971v1)). Stopping sells one attempt's continuation success to buy a replacement's, and two terms price the trade against you. The replacement inherits only the budget left after the landmark, and at the tighter caps 91% to 100% of coding trajectories need more than that remainder to finish. The abort also "forces the replacement attempt to repeat setup and localization from scratch", pushing combined spend above the cost of letting a moderate-length original run end naturally.

A monitor at chance within a task cannot pick which attempts have low continuation value, so the selection that would justify the trade is unavailable. A score threshold filters issues instead: "When a monitor primarily captures static issue difficulty, score thresholding acts as an implicit task filter." An exact decomposition shows that filter is the whole of the learned policy's advantage. "the gain over random restarting stems almost entirely from between-task stopping allocation (avoiding stops on easy issues), whereas attempt-level selection within a task contributes near zero (-0.11 to +0.24 percentage points)." Between-task allocation set the sign in all four settings, so a filter available before execution did the work, 20k tokens late.

## When this backfires

Demanding a continuation baseline is not a reason to drop early stopping. In four conditions the demand misleads:

- The stop keeps the work. Carrying the interrupted repository diff into the replacement inverts the comparison: "At a target 25% false-positive rate, RestartSmart raises Qwen3.6-27B resolution from 66.6% to 71.8%, whereas cold restart reaches only 66.8%" ([arXiv:2608.03222v1](https://arxiv.org/abs/2608.03222v1)). The continuation result indicts discarding state, calling it essential to retain "intermediate edits and test diagnostics" so the replacement avoids repeating exploration.
- The stop sits at a phase boundary. EET terminates patch generation and selection iterations rather than aborting mid-exploration, and "consistently reduces total cost by 19%-55% (32% on average), with negligible loss in resolution rate (at most 0.2%)" ([arXiv:2601.05777v2](https://arxiv.org/abs/2601.05777v2)). No exploration is discarded, so the sunk-token term never appears.
- Short-horizon agents outside a repository. The strongest model-environment settings cut generated tokens 54.9% and 60.2% at a 90% recall target on WebShop and TextCraft, because "Lightweight linear probes on internal activations predict eventual task failure from the first interaction round" ([arXiv:2607.06503v2](https://arxiv.org/abs/2607.06503v2)). Setup is cheap there, and the continuation paper scopes itself "to four open-weight model-framework settings on Python-centric repository benchmarks", noting that activation-probing monitors may behave differently.
- The objective is fleet spend, not per-attempt resolution. A team trading resolution for cost is optimizing something the replay never scores, where BAGEN's finding lives: "Early stop saves 28-64% tokens on failed trajectories" ([arXiv:2606.00198v1](https://arxiv.org/abs/2606.00198v1)). Read the qualifier. Savings are conditional on the trajectory being a failure, the judgment shown to be unavailable early.

One structural limit cuts the other way. "Within-task discrimination requires mixed-outcome tasks by definition", so a workload that attempts each issue once cannot produce the measurement. Repeat a sample of issues before trusting a monitor built on it.

## Example

The change is in what the evaluation reports, not in the monitor.

**Before** — the monitor's own scoreboard:

```text
solve rate, learned restart   20.66%
delta vs matched random       +1.98 pp  [+1.31, +2.60]
verdict                       ship it
```

**After** — the two rows that decide it:

```text
within-task AUC               0.50  [0.48, 0.51]   <- ranks issues, not attempts
solve rate, learned restart   20.66%  @ 69.93k mean tokens
solve rate, continuation      28.71%  @ 68.10k mean tokens
verdict                       continuation wins on both axes
```

Solve rates and the delta are the SWE-agent/Qwen3.5 setting at a 20k landmark under a 75k cap; the within-task AUC is the three-seed Qwen3-0.6B monitor across 32,406 attempts ([arXiv:2610.35971v1](https://arxiv.org/abs/2610.35971v1)). The authors state the protocol as a standard: "Policy evaluations under shared token budgets should compare proposed stopping rules against both matched random stopping and uninterrupted continuation."

Point the cost-reduction work up front instead. Static signals rank difficulty before execution, so they "naturally support up-front token provisioning" and solver routing. On the issues shared between the two Qwen3.5 settings, scaffold choice alone moved the solve rate 14.06 percentage points, against the 1.98 the best mid-run restart policy bought.

## Key Takeaways

- Report within-task AUC, not pooled AUC. A difficulty-only predictor scores 0.97 pooled and 0.50 within a task, so the pooled number cannot distinguish a trajectory monitor from a lookup table of issue difficulty.
- Add continuation as a baseline before random restart. Continuation won 216 of 224 replay configurations, and all 56 at the 75k cap, on solve rate and token cost together.
- A learned stop's edge over random restart is between-task allocation worth up to 1.75 percentage points. Within-task selection stayed inside -0.11 to +0.24 and never decided the sign.
- Cold restart lost to continuation in these replays. Replacements received only the residual budget and repeated setup.
- Keeping the interrupted diff, stopping at a phase boundary, or probing hidden states in a short-horizon environment each clear the bar that cold restart fails.
- The measurement has a prerequisite your workload may not meet: repeat a sample of issues, because a single attempt per issue yields no within-task comparison at all.

## Related

- [Behavioral Drivers of Coding Agent Success and Failure](../agent-design/behavioral-drivers-agent-success.md) — the task-identity confound that makes pooled trajectory metrics unreliable in the first place
- [What an Agent's Own Token Cost Estimate Is Good For](../../token-engineering/agent-cost-self-prediction.md) — the same ranking-versus-deciding split applied to an agent's self-reported budget
- [Task Feasibility Awareness: Stop Before You Start](../agent-design/task-feasibility-awareness.md) — the pre-execution filter that costs nothing, which a mid-run score threshold reimplements late
- [Harness-Enforced Stopping on Judged-Useless Tool Results](../agent-design/enforced-stop-on-useless-results.md) — a stop rule built on an observed signal rather than a predicted outcome
- [Token Reduction Mistaken for Cost Reduction](token-reduction-not-cost-reduction.md) — the adjacent measurement error, where the saving is real and the accounting is not
- [Convergence Detection in Iterative Agent Refinement](../../loop-engineering/convergence-detection.md) — progress-based stopping for loops with no verification harness
