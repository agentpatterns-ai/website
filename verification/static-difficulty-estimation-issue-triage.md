---
title: "Static Difficulty Estimation for Agent Issue Triage"
term: "Static Difficulty Estimation"
description: "Structural task features predict coding-agent success at AUC 0.863, but the dominant features are measured on the gold patch, so only the repository half survives to triage time."
tags:
  - testing-verification
  - evals
  - tool-agnostic
  - arxiv
aliases:
  - pre-hoc task difficulty estimation
  - ex ante difficulty prediction
  - structural task triage
last_reviewed: 2026-08-20
maturity: emerging
---

# Static Difficulty Estimation for Agent Issue Triage

> Task structure predicts whether a coding agent resolves an issue, but the strongest published predictor is measured on the answer.

Static difficulty estimation forecasts a coding agent's chance of resolving an issue from deterministic properties of the task, its repository, and its issue text, without running the agent. Over CoderForge-Preview (45,769 tasks across 1,553 repositories, mean 4.8 test-verified trajectories each), an XGBoost model on 54 such features reached AUC 0.863 on whether any trajectory succeeded, and R² 0.408 regressing continuous pass rate ([Al-Haque and Johnson, 2026](https://arxiv.org/abs/2608.18280v1)).

## Read the conditions before the headline

Three limits decide how much of that result reaches a real backlog.

The largest is that the top predictors are oracle measurements. Patch fragmentation supplies the top three features, and the authors compute them on the reference solution: "Patch features are computed from the gold (oracle) patch provided with each task." At triage time no gold patch exists, so `patch_lines_deleted` (mean absolute SHAP 0.406, "2.65× larger than the fourth-ranked feature") is not a quantity you can measure.

The reported metric is the second limit. A study of ex ante difficulty prediction across 17 agentic benchmarks reports that "AUC can remain high even when the predictor contains no task-specific difficulty information", and measured 0.715 AUC from a predictor that assigns every task the same constant difficulty ([Krsteski and Meyer, 2026](https://arxiv.org/abs/2608.05797v1)). That baseline is pooled across their own suite rather than computed on CoderForge, so the figures are not directly comparable, but an AUC in the mid-0.80s carries a smaller informative margin than it appears to. The R² of 0.408 is the more honest summary: roughly 60% of pass-rate variance stays unexplained.

Generalization closes the list. Every trajectory came from Qwen3-Coder-480B under OpenHands v0.52.1 over Python-centric repositories drawn from SWE-Smith and SWE-Rebench, and the authors state that features predicting difficulty for this agent "may not generalize to agents with different architectures" ([Al-Haque and Johnson, 2026](https://arxiv.org/abs/2608.18280v1)).

## What survives to triage time

The repository feature group. It reaches AUC 0.839 and R² 0.350 on its own, against 0.863 and 0.408 for the full model, and every feature in it is computable before dispatch: `repo_top_level_dir_count`, `repo_file_count`, `repo_total_known_size`, and `repo_max_depth` ([Al-Haque and Johnson, 2026](https://arxiv.org/abs/2608.18280v1)). The deployable signal is a property of the codebase you point the agent at, not of the individual ticket.

Issue wording is the weakest lever. Prompt features alone reach AUC 0.599 and explain "almost none of the continuous variance (R²=0.025)", surfacing only near the pass/fail boundary: at least one ranked in the top five contributors for 70.3% of the 575 near-baseline tasks, against 6.8% of hard ones. Rewriting an issue description pays off for borderline work and close to nothing for the hard tail.

## Why it works

The study measures correlation and offers only a partial causal account, so read the mechanism as the authors' interpretation. Repository scale features "reflect the size of the search space the agent must traverse", standing in for the group-level construct of "navigation difficulty: how hard it is to locate the relevant code before making any edit". Patch features borrow the diffusion result from defect prediction, where what separates defect-inducing commits from clean ones is "how scattered a change is across files and hunks" rather than raw edit volume; "tasks with unusually large inter-hunk distances are especially penalized". Across the top three patch features the pattern is monotone: "high feature values push predictions toward failure". The repository group contributes separately — "ranks 4-14 are occupied entirely by repository structural and patch features, all showing negative directional effects", which the authors read as evidence that "the navigational complexity of the repository the agent must traverse matters beyond the properties of the edit itself" ([Al-Haque and Johnson, 2026](https://arxiv.org/abs/2608.18280v1)).

The account has a hole the authors name. Gold-patch features "do not capture all sources of task complexity", and "a task could have a simple gold patch but require complex agent reasoning, or vice versa". Trajectory evidence sharpens the caveat: examining all 12 never-solved simple-patch tasks, one study found the agent "correctly localizes the bug, finding the gold-patch file in 12 of 12 tasks and editing it in 10 of 12", failing instead by patching "the symptom (the caller, the consumer, the display layer) while the gold patch fixes the root cause" ([Mehtiyev and Assunção, 2026](https://arxiv.org/abs/2604.02547v1)). Structure predicts where difficulty concentrates. It does not tell you what the agent got wrong.

## When this backfires

- Ranking issues inside one repository. The deployable features are repository-level constants, so every ticket shares its file count and directory depth. The surviving signal separates codebases, not backlog items within one.
- Substituting the agent's own patch for the missing gold patch. A scattered patch from a confused run then reads as a hard task instead of a bad run, and the feature becomes an output of the run it was meant to predict.
- Calibrating on a small backlog. Pass rate came from a mean of 4.8 nonzero-temperature trajectories per task, and outcomes "conflate genuine task difficulty with sampling variance" ([Al-Haque and Johnson, 2026](https://arxiv.org/abs/2608.18280v1)), so a score fitted on a few dozen of your own issues mostly measures noise. See [seed variance reporting](seed-variance-reporting.md).
- Using the score as a gate. With most pass-rate variance unexplained, an auto-reject threshold discards issues the agent would have solved. Treat the estimate as a prior over verification depth, not an admission test.
- Transferring a threshold from public repositories to private code, since pretraining on public code may elevate the solve rates it was fitted on. See [benchmark contamination as eval risk](benchmark-contamination-eval-risk.md).

For a single issue the agent run is itself the measurement, and it is cheap next to standing up a feature pipeline and keeping it calibrated as the agent changes underneath it. [Krsteski and Meyer](https://arxiv.org/abs/2608.05797v1) locate the actionable signal in the residual between expected and observed difficulty, which "can expose hidden environment flaws such as contamination and infeasibility", and residuals require rollouts.

## Key Takeaways

- Difficulty is substantially encoded in static structure, but the published headline rests on features derived from the reference solution, which triage does not have.
- The repository feature group is the part you can compute before dispatch, and it gives up only 0.024 AUC against the full model.
- Report Spearman rank correlation or pairwise accuracy within a benchmark alongside AUC, so a predictor carrying no task-specific signal cannot hide behind a strong-looking curve.
- Use the estimate to decide how much verification a class of work deserves, and calibrate on your own outcomes rather than importing published coefficients.

## Related

- [Trajectory Decomposition: Diagnose Where Coding Agents Fail](trajectory-decomposition-diagnosis.md) — the post-hoc counterpart, decomposing a run into search, read, and edit stages once it exists.
- [Repository Perturbation as Context-Reasoning Diagnosis (RepoMirage)](repository-perturbation-context-reasoning-diagnosis.md) — isolates repository navigation from issue resolution by perturbing the codebase before the agent runs.
- [Benchmark Contamination as Eval Risk](benchmark-contamination-eval-risk.md) — why solve rates on public repositories overstate performance on private code.
- [Risk-Based Task Sizing for Agent Verification Depth](risk-based-task-sizing.md) — how to spend a difficulty prior once you have one.
- [Use pass@k and pass^k to Separate Agent Capability from Consistency](pass-at-k-metrics.md) — the metric pair that separates the mixed-outcome band from genuinely hard tasks.
