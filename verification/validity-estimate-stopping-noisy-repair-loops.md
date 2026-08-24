---
title: "Validity-Estimate Stopping for Noisy Verify-Repair Loops (VRR-Stop)"
term: "Validity-Estimate Stopping"
description: "When a verify-repair loop's verifier is noisy, stop on an estimate of true validity — not the verifier's acceptance rate, which can rise while true validity falls as repair damages already-correct plans."
tags:
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - "validity-aware repair stopping"
  - "belief-filtered repair stopping"
last_reviewed: 2026-07-23
maturity: emerging
---

# Validity-Estimate Stopping for Noisy Verify-Repair Loops (VRR-Stop)

> When the verifier in a verify-repair loop is noisy, stop on an estimate of true validity, not on the verifier's rising acceptance signal.

Use the verifier's acceptance rate as your stop signal only when the verifier is a trustworthy oracle. When the verifier is itself noisy — an LLM-as-judge, a learned reward model, or a flaky heuristic — its reported acceptance can keep climbing while the plan's true validity falls, because a noisy repairer damages already-correct plans and the noisy verifier then accepts the damaged result ([Wu et al., 2026](https://arxiv.org/abs/2607.17641)). The fix is to stop on an estimate of true validity instead of the raw acceptance count.

VRR-Stop models the loop with four parameters: the verifier's false-acceptance rate, its false-rejection rate, the repairer's fix rate (invalid to valid), and the repairer's damage rate (valid to invalid) ([Wu et al., 2026](https://arxiv.org/abs/2607.17641)). Each round runs several independent verification votes on the current plan and feeds them through a Bayesian update — belief filtering — to estimate the probability that the plan is truly valid. The loop then repairs only while the expected gain from one more round is positive, and commits otherwise. It needs only the sign of that expected gain to be identifiable, not accurate recovery of all four parameters ([Wu et al., 2026](https://arxiv.org/abs/2607.17641)).

This targets a different failure than a round budget. [Bounded repair-loop iterations](bounded-repair-loop-iterations.md) caps rounds because gains concentrate early under a real oracle. Here the acceptance metric you would normally watch is itself corrupted, so the round count is secondary — you stop on estimated validity regardless of what acceptance reports.

## Why it works

A noisy verifier's observed acceptance rate carries a fixed false-acceptance floor: it equals that floor plus the verifier's discrimination times the true validity ([Wu et al., 2026](https://arxiv.org/abs/2607.17641v1)). When discrimination is low, the floor dominates and acceptance tracks noise, not validity. A noisy repairer then compounds the problem — it can take a valid plan that was falsely rejected, damage it, and hand the verifier a corrupted plan it falsely accepts, so true validity drops while acceptance climbs. In one stress setting 55% of instances underwent a correct-to-incorrect repair, and six of eight settings showed true validity declining monotonically as rounds continued ([Wu et al., 2026](https://arxiv.org/abs/2607.17641v1)). Estimating validity from repeated votes and stopping when expected repair gain turns negative breaks that divergence. The same balance appears independently as a feedback-control equilibrium: continue only while the error-correction rate beats the error-introduction rate by the odds factor of current accuracy ([Liu & Meng, 2026](https://arxiv.org/abs/2604.22273v2)).

## When this backfires

The apparatus earns its keep only in specific regimes.

- The verifier is a trustworthy oracle. When a compiler or a reliable test suite verifies each round and the repairer rarely corrupts correct plans, acceptance already tracks validity. Running several verification votes per round multiplies verification cost for no gain — a fixed round cap suffices.
- Verifier discrimination approaches zero. When the verifier is barely better than a coin flip, calibration itself fails and estimation error can flip the stopping decision. On one weak-verifier setting (discrimination 0.03) the method dropped 58 percentage points below its reference before the paper's estimation-free fallback, which keeps the best-seen candidate under a sufficient verification margin, recovered it ([Wu et al., 2026](https://arxiv.org/abs/2607.17641v1)).
- The loop is non-stationary or the task is graded. The model assumes repairs are conditionally independent of history given the true state, makes one-step decisions that cannot see past interior peaks, and represents validity as binary — so partial correctness and correlated verifier errors on the same plan fall outside its guarantees ([Wu et al., 2026](https://arxiv.org/abs/2607.17641)).

Without external feedback the divergence is worse, not better: intrinsic self-correction with no outside signal degrades reasoning accuracy and flips correct answers to incorrect on GSM8K ([Huang et al., 2024](https://arxiv.org/abs/2310.01798)).

## Example

On a GSM8K stress setting (Qwen2.5-3B, 500 instances, 8 verification votes per round), validity-estimate stopping reached 0.722 true validity at an average of 0.72 repair rounds, against 0.116 for fixed five-round repair — a gain of 60.6 percentage points (95% CI +56.0, +65.0) ([Wu et al., 2026](https://arxiv.org/abs/2607.17641v1)). Fixed repair kept iterating on a rising acceptance signal and destroyed most of the plans it started with; the validity estimate stopped after less than one round on average because the expected gain was already negative.

## Key Takeaways

- When the verifier is noisy, acceptance can rise while true validity falls — stop on an estimate of validity, not the acceptance rate ([Wu et al., 2026](https://arxiv.org/abs/2607.17641)).
- Estimate validity from repeated verification votes per round and repair only while the expected marginal gain is positive; you need the sign of that gain, not exact parameters ([Wu et al., 2026](https://arxiv.org/abs/2607.17641)).
- The method pays off only with a noisy verifier. With a trustworthy oracle, a plain round cap does the same job at lower cost — see [bounded repair-loop iterations](bounded-repair-loop-iterations.md).
- Near-zero verifier discrimination defeats calibration; fall back to keeping the best-seen candidate under a verification margin ([Wu et al., 2026](https://arxiv.org/abs/2607.17641)).
- The same continue-or-stop balance shows up independently as a feedback-control threshold — correction rate versus introduction rate ([Liu & Meng, 2026](https://arxiv.org/abs/2604.22273)).

## Related

- [Bounded Repair-Loop Iterations](bounded-repair-loop-iterations.md) — caps rounds under a real oracle; the complementary stopping strategy when the verifier is trustworthy rather than noisy.
- [Re-Run the Original Test Suite After Every Refinement Turn](test-suite-after-refinement-turn.md) — catches the correct-to-incorrect regressions a noisy repair loop introduces.
- [Markov-Chain Reliability for LLM Agents](markov-chain-agent-reliability.md) — audit the abstraction before you trust a metric; the same caution behind not trusting a noisy acceptance rate.
- [Evidence-Gated Lifecycle Control for Coding Agents (Proof-or-Stop)](evidence-gated-lifecycle-control.md) — advances state only on verifiable evidence, never on the agent's own acceptance claim.
- [State-Bound Evidence and Typed Revision Contracts for Repair Loops](state-bound-repair-evidence.md) — the complementary lever when the verifier is sound but its output is stale: bind evidence to a code state and preserve the last verified candidate.
