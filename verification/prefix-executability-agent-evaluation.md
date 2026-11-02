---
title: "Prefix Executability as a Tool-Agent Reliability Axis"
term: "Prefix Executability"
description: "Replay an agent's tool calls in order and record where the first one stops being legal. Final success is the sum of uninterrupted execution and recovery."
tags:
  - testing-verification
  - evals
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - prefix executability
  - trajectory executability rate
  - first-error depth
  - executable-prefix survival
last_reviewed: 2026-11-01
maturity: emerging
---

# Prefix Executability as a Tool-Agent Reliability Axis

> Prefix executability checks whether every tool call was legal when made, so final success splits into uninterrupted execution and recovery after an invalid call.

Prefix executability replays an agent's emitted tool calls in order and records the depth at which the first one stops being executable. The test is the tool schema, argument validators, referenced values and state preconditions in force at that moment. Rezaeian and colleagues build four metrics on that one predicate ([Rezaeian et al., arXiv:2610.40444v1](https://arxiv.org/abs/2610.40444v1)):

- First-error depth (FED): the depth at which the first call stops being executable.
- Trajectory executability rate (TER): the share of rollouts executable end to end.
- AUC-PEC: a horizon-normalized area under the executable-prefix profile.
- Recovery rate (RR): final success among the rollouts that broke.

You need declared schemas, explicit preconditions and readable state before you can measure any of it. The scorer replays rather than judges, so there is nothing to fall back on where the environment cannot answer. "The benchmark-side scorer is deterministic and uses no LLM judge" ([§2.1](https://arxiv.org/abs/2610.40444v1)). The authors name where that stops working: "Partially observed web or GUI environments may require state estimation or learned preconditions, and executability does not certify semantic correctness" ([Limitations](https://arxiv.org/abs/2610.40444v1)). The paper names state estimation and learned preconditions as the options and does not evaluate them. My own reading is that a learned model supplying the missing preconditions gives up the determinism that made the scorer worth having. Treat the gap as a reason not to measure rather than a modeling problem.

## What the second axis shows that one score cannot

Final success and prefix reliability rank methods differently on the same runs. Both samples below are 200 stratified tasks under GPT-5.4 at high reasoning effort ([Table 2](https://arxiv.org/abs/2610.40444v1)).

| Dataset | Method | Final success | TER | AUC-PEC |
|---|---|---|---|---|
| BFCL v3 | Plan-Conditioned ReAct | 0.94 | 0.47 | 0.54 |
| BFCL v3 | Dual-Loop | 0.94 | 0.94 | 0.96 |
| ToolSandbox | Plan-Conditioned ReAct | 0.69 | 0.48 | 0.52 |
| ToolSandbox | Dual-Loop | 0.63 | 0.94 | 0.95 |

These are point estimates with marginal 95% intervals, and the paper refuses the paired reading: "Marginal-interval overlap does not establish paired significance, and we do not infer paired effects from it" ([§2.6](https://arxiv.org/abs/2610.40444v1)).

The extreme case is BFCL v3 with Llama-4 Maverick under Plan-Conditioned ReAct, at 0.74 final success and TER 0.05. Of 200 episodes, 10 were fully executable and all 10 succeeded; 138 of the 190 carrying a prefix failure also succeeded. So 93.2% "of successful episodes reached the objective after an earlier invalid prefix" ([§3.1](https://arxiv.org/abs/2610.40444v1)). The authors call that "high terminal utility with low uninterrupted-execution reliability, rather than a contradiction between metrics". A leaderboard sorted on final success calls that agent reliable.

Read RR beside its denominator. Dual-Loop records RR 0.00 on BFCL across all three models, with only 12, 7 and 25 eligible episodes. Plan-Conditioned ReAct has 106, 130 and 190. The paper calls the estimates imprecise: "the small eligible sets make these conditional estimates imprecise" ([§3.1](https://arxiv.org/abs/2610.40444v1)). It adds that "the size of the eligible set does not itself determine the recovery rate". The Table 2 caption adds: "RR is better only conditional on entering the failure regime and should be interpreted with RR-Eligible" ([Table 2 caption](https://arxiv.org/abs/2610.40444v1)).

## Why this is not path matching

[Outcome grading](grade-agent-outcomes.md) is this site's default because path-based graders punish an agent for solving the task a way the eval author did not anticipate. Prefix executability does not reopen that case, because the predicate holds no reference trajectory: "It credits alternative executable action sequences without requiring one gold path and records first failure, survival, and recovery" ([§1](https://arxiv.org/abs/2610.40444v1)). An unanticipated but legal sequence scores 1.0. What the check rejects is a call that was not legal when issued, a validity question rather than a preferred-path question. The real difference is scope. That page retains the trace for debugging and lets the end state decide correctness. This paper asks you to publish the number. "Evaluations should therefore report uninterrupted executability, recovery, terminal success, and agent-side cost together" ([Conclusion](https://arxiv.org/abs/2610.40444v1)).

## Why it works

Final success is a mixture of two capabilities, and the proof is arithmetic rather than empirical. Partition rollouts by whether the whole trajectory was executable. Define three terms:

- `q`: the executable share (TER).
- `s`: the success rate inside that share.
- `r`: the recovery rate.

Proposition 3 gives `Pr(Y=1) = qs + (1−q)r` for any rollout distribution with `0 < q < 1`. Holding `s` and `r` fixed, the slope with respect to TER is `s−r`. Across methods both conditional rates can also change. So "the decomposition does not imply a universal monotone relationship between TER and final success" ([Appendix B](https://arxiv.org/abs/2610.40444v1)).

Prefix validity is also a product of per-action validity, so one rejected call zeroes every longer prefix of that rollout: "Once an action fails, every subsequent prefix still contains that failure. Consequently, later successful execution can contribute to recovery while never restoring executable-prefix survival for that rollout" ([Appendix C.1](https://arxiv.org/abs/2610.40444v1)). TER and RR therefore measure different things, and an agent can post high terminal success on an almost entirely invalid execution history.

## When this backfires

- You read a falling PEC curve as an error count. The main curve is fixed-cohort, so a rollout that stopped early leaves it too: "Fixed-cohort PEC reflects both reaching a depth and retaining validity, so its decline is not an error-only statistic" ([Limitations](https://arxiv.org/abs/2610.40444v1)). Pair it with the eligible-depth variant, which conditions on reaching the depth and is not a survival curve.
- You treat TER as a safety or correctness gate. The authors rule that out: "Moreover, an executable trajectory can still be unsafe, biased, privacy-violating, or misaligned with user intent" ([Broader impacts](https://arxiv.org/abs/2610.40444v1)). Unsafe-path detection is a different instrument, covered by the [trajectory-opaque gap](eval-blind-spots.md).
- You buy the plan-verification intervention expecting the benchmark result. Dual-Loop raised TER and AUC-PEC across three models on BFCL v3 and ToolSandbox. The transfer audit did not establish the same advantage: "The Airline/Retail audit does not establish the consistent validation advantage observed on BFCL-v3 and ToolSandbox." The explanation about stale advance plans is marked "a testable interpretation, not an identified causal mechanism". A paired study varying the verifier model and budget returned a null: "All paired 95% intervals for TER and AUC-PEC changes include zero" ([§3.3](https://arxiv.org/abs/2610.40444v1)).
- You price that intervention at zero. Against Plan-Conditioned ReAct in the same audit, mean tokens moved by roughly −3% to +12% across the three models. Cumulative agent-call latency moved by −1% to +22% ([§3.3](https://arxiv.org/abs/2610.40444v1)).
- You make the new number a target. A trajectory-level scorer is gameable the way a static benchmark is memorizable. Agents "may exploit simulator quirks, avoid meaningful exploration, optimize for superficial trajectory signals, or discover shortcuts that satisfy the scorer without demonstrating the intended competence" ([arXiv:2605.17829v1, §6.1](https://arxiv.org/abs/2605.17829v1)).

## Example

The paper's illustrative contact-removal task under ToolSandbox semantics shows what the axis separates. The agent first tries to delete a contact using its phone number where the stored identifier belongs. Both values have string type, but the requested identifier is absent from the current state, so the transition is rejected without changing it. The agent then searches by phone number, gets the stored identifier back, and removes the contact ([Appendix C.2](https://arxiv.org/abs/2610.40444v1)).

| Step | Action | Outcome |
|---|---|---|
| 1 | Remove the contact by phone number | Rejected, no matching identifier, state unchanged |
| 2 | Search for the contact by phone number | Returns the stored identifier |
| 3 | Remove the contact by that identifier | Accepted |

Per-action validity is `(0, 1, 1)` and prefix validity is `(0, 0, 0)`. With `T = 3` the trajectory scores FED 1, contributes zero to TER and AUC-PEC, counts as RR-eligible, and can still carry final success. A two-step trajectory that searches first and then removes is executable throughout and takes full credit. A terminal milestone check could credit both, which is what the prefix record distinguishes: the repaired run from the clean one.

When the first-failure replay stops, the paper labels the offending action with one primary cause by fixed precedence, for diagnosis only. The authors "annotate the action at the first invalid prefix with one primary cause: schema failure, dependency failure, precondition failure, state-consistency failure, or information failure" ([§2.4](https://arxiv.org/abs/2610.40444v1)). The label routes the engineering work. No metric consumes it.

## Key Takeaways

- Report TER beside final success, because a tie on final success is not a tie on reliability.
- Publish the recovery rate as the other half of the identity, always beside its RR-Eligible count. Small eligible counts make RR imprecise.
- Route the work from the first-failure label, not from the scalar. Schema, dependency, precondition, state-consistency and information failures each send you somewhere different.
- Check you have declared schemas, explicit preconditions and readable state before committing to any of this. Partially observed web and GUI environments are the authors' named gap.
- Keep it off your safety and correctness gates. Executability says a call was legal, not that it was wise.
- Treat pre-execution plan checking as environment-dependent until you measure it on your own environment. Price its token and latency cost in the same table.

## Related

- [Grade Agent Outcomes, Not Execution Paths](grade-agent-outcomes.md) — the position this page engages; prefix executability is reference-free, so it is not the path grading that page rejects
- [Valid Completion Rate as a Second Scoring Axis](valid-completion-rate-second-axis.md) — a different second axis over the same runs, scoring normal termination and evaluator handoff rather than call legality
- [Recovery as a Separate Eval Axis](recovery-as-separate-eval-axis.md) — recovery measured under deliberately injected faults, against the organically observed prefix failures here
- [Learned Prefix Monitors for Agent Traces](learned-prefix-monitors-agent-traces.md) — a learned risk score over partial traces, where this predicate is deterministic
- [Action-Class Decomposition for Tool-Calling Evals](action-class-decomposition-tool-calling-evals.md) — scores whether the turn called for a different kind of action, not whether the call it made was legal
