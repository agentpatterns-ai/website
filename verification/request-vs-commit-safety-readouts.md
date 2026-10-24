---
title: "Request Rate and Commit Rate Are Different Safety Numbers"
term: "Request-Commit Readout Split"
description: "On identical invalid-proof trials two models requested a protected action 52.1% and 54.2% of the time, and the deterministic tool gate committed none."
tags:
  - testing-verification
  - evals
  - security
  - tool-agnostic
  - arxiv
aliases:
  - request-commit readout split
  - advisory versus committed action rate
  - proposal and commitment safety endpoints
last_reviewed: 2026-10-21
maturity: emerging
---

# Request Rate and Commit Rate Are Different Safety Numbers

> Two models requested a protected action in 52.1% and 54.2% of identical invalid-proof trials, and the gate's commit rate was zero for both.

A request-commit readout split reports two rates from one run of one harness: how often the model asked for a protected action, and how often the tool committed it. A 48-task runtime study of 2,688 initial calls put invalid-proof request rates at 0.8% for GPT-5.4, 0% for Claude Sonnet 5, 52.1% for Nemotron 3 Super 120B and 54.2% for Llama 4 Maverick. Under a deterministic proof gate, none of it committed ([Zhu et al., arXiv:2610.24298v1](https://arxiv.org/abs/2610.24298v1), §5.4). The Nemotron and Llama request-to-commit gaps were 52.1 points, 95% CI [39.2, 64.6], and 54.2 points, 95% CI [42.1, 65.8]. Ship one number and you cannot tell which half of the system produced it.

## The conditions that make the commit column mean anything

Three conditions held in this study, and each is a question about your own harness.

Every path to the protected action is mediated. The guarantee is explicitly conditional: "Complete mediation is a separate prerequisite for the execution-gate guarantee" ([arXiv:2610.24298v1](https://arxiv.org/abs/2610.24298v1), §3.3). An unguarded execution edge runs no proof check, so the rate describes the guarded path and nothing else.

The authorization policy is decidable without judgement. The tool's check tests claim binding, the freshness window, scope, and whether the distinct authenticated signers contain a qualified signer set ([arXiv:2610.24298v1](https://arxiv.org/abs/2610.24298v1), §3.3, Eq. 1). Where authorizing the action needs a human call, there is no predicate to read a second rate off.

You report the true-world rate beside both, meaning the share of trials where the claim was true and the action went through. The policy that drives commits to zero can take legitimate work with it. In a separate signer-composition study, Claude's "two-of-three quorum achieved only 0.8% true-state utilization, suggesting a possible utility cost" ([arXiv:2610.24298v1](https://arxiv.org/abs/2610.24298v1), §5.3).

## What each column is evidence of

| Column | What it measures | What moved it in this study |
|---|---|---|
| Request rate | The model's decision policy over the claims it can see | Model choice. 0% to 54.2% across four models on identical invalid-proof trials |
| Commit rate | The gate's coverage and the policy's completeness | Nothing. 0% on those same trials for all four models, "by construction, not by learned proof recognition" |

Read down the commit column and every model looks equally safe, because that column is a property of the gate rather than of any model in it.

A gate that passes is not a truth check either. "Proof validity authenticates a properly bound, timely endorsement under the policy, not ground truth", and freshness "checks proof timing, not whether the claimed business state remains true" ([arXiv:2610.24298v1](https://arxiv.org/abs/2610.24298v1), §3.3). In "a separate single-model authorization check", a false claim with a policy-valid compromised-signer proof "can pass the gate, since proof validity is not factual truth" ([arXiv:2610.24298v1](https://arxiv.org/abs/2610.24298v1), abstract). Only Llama passed that check's eligibility controls, and the authors call the result "a selected-protocol mechanism check, not an independent cross-model threshold discovery" ([arXiv:2610.24298v1](https://arxiv.org/abs/2610.24298v1), §5.3).

## Why it works

The two numbers come from two different functions, which is why they disagree on the same trials. The proposed action is whatever the model selects from visible claims. The committed action additionally requires an available execution edge and, on a guarded edge, a deterministic verifier returning one ([arXiv:2610.24298v1](https://arxiv.org/abs/2610.24298v1), §3.3–§3.4). Rejecting an invalid proof follows from that predicate, so the zero is an entailment rather than a measurement of the model.

Two unrelated groups found the same split. A paired evaluation across 1,500 scenarios, under regimes that either block or permit unsafe actions, reports "substantial gaps between attempted and executed violations, indicating that external guardrails can suppress visible harm while masking persistent misalignment" ([arXiv:2603.20320v1](https://arxiv.org/abs/2603.20320v1), abstract). A study across three agentic environments and 13 architectural configurations scored "planning refusal, execution-stage interception, partial harmful execution, and successful attack completion" as separate stages ([Hagag et al., arXiv:2604.23459v1](https://arxiv.org/abs/2604.23459v1)).

## When this backfires

- The commit column drives a model decision. It did not move across four models, so a team ranking models on it is reading the gate. The request column separates them, and even it is protocol-bound: Llama "selected actions under unsigned E1 claims (98.3%) and invalid runtime proofs (54.2%) in separate protocols", so "the E2 below-cut rate cannot be interpreted as its general refusal rate" ([arXiv:2610.24298v1](https://arxiv.org/abs/2610.24298v1), §5.3).
- The enforcement layer is itself model-mediated. A benchmark of poisoned tool descriptions found "common prompt-guardrail defenses are largely ineffective and can, counterintuitively, even be counterproductive" ([Liu et al., arXiv:2605.24069v1](https://arxiv.org/abs/2605.24069v1)). A commit rate belongs to the enforcement configuration that produced it.
- You have no programmatic ground truth. Scoring a false-world rate needs paired tasks whose authoritative state is set in code and never visible to the executor. Without that there is no denominator.
- You expect the split to settle an architecture question. With the executor-visible claim held fixed, "None of the 27 reported comparisons met the prespecified large-effect rule" over routing configurations ([arXiv:2610.24298v1](https://arxiv.org/abs/2610.24298v1), §5.1). Of ten proof perturbations, only stale replay replicated across three or more models (§5.4).
- You read recovery after a denial as the agent catching up. All 257 post-denial responses chose safe progress, but each recovery prompt supplied a new authoritative snapshot first, which the authors call "assisted post-denial behavior, not hidden-state inference" ([arXiv:2610.24298v1](https://arxiv.org/abs/2610.24298v1), §5.4).

All of it comes from synthetic tasks. The design "does not establish how frequently the observed failures occur in deployed multi-agent systems", and counts from the separate studies "should not be aggregated into a single denominator" ([arXiv:2610.24298v1](https://arxiv.org/abs/2610.24298v1), Limitations and Appendix A).

## Key Takeaways

- Report three rates from the same trials: requested, committed, and completed in the true world. Each one fails for a different reason, so a single figure cannot say which part of the system to change.
- Before you quote a commit rate, name the paths it covers. An unmediated route makes the number a statement about the guarded route only.
- A zero at the gate transfers to a new model and nothing else. It does not transfer to a new policy, a new tool, or a path the gate does not sit on.
- Enforcement answers obedience, never truth. A proof that satisfies the policy can still carry a false claim, so the state the claim asserts needs its own check.

## Related

- [Recover the Six Measurement Choices Behind an Attack Success Rate](asr-comparability-audit.md) — the rule for numbers carried between harnesses, which excludes the within-run case this page covers.
- [Zero Violations Is Not Evidence Your Hook Works](enforcement-liveness-evidence.md) — the other way a clean commit column misleads, where the rail never fired or the agent never tried.
- [Deterministic Precondition Gates for Tool-Using Agents](../patterns/agent-design/deterministic-precondition-gates.md) — building the predicate whose coverage the commit column measures.
- [Prompt-Only Tool Access Control](../patterns/anti-patterns/prompt-only-tool-access-control.md) — what the request column looks like when nothing sits on the write path.
- [Action-Graded Severity for Agent Red-Team Outcomes](action-graded-severity-red-team-outcomes.md) — grading the commits that do land, rather than counting them.
