---
title: "Bounded Repair-Loop Iterations"
term: "Bounded Repair-Loop Iterations"
description: "Cap generate-validate-repair loops near three to four rounds — most achievable gains land in the first iterations and later rounds mostly burn tokens for marginal return."
tags:
  - testing-verification
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - "repair-loop iteration budget"
  - "repair iteration cap"
last_reviewed: 2026-07-07
maturity: emerging
---

# Bounded Repair-Loop Iterations

> Cap generate-validate-repair loops near three to four rounds — the first iterations capture most of the achievable gains and later rounds mostly burn tokens.

Treat the iteration count in a generate-validate-repair loop as an explicit budget, not an arbitrary constant. An empirical study across five software-engineering workflows — code generation, test generation, and code translation — and three models finds that most achievable gains concentrate in the first three to four repair rounds, with sharp diminishing returns after ([Kiecker et al., 2026](https://arxiv.org/abs/2607.05197)). The completion curves are consistently concave across every model-and-tool pairing, so a fixed budget of three to four rounds captures nearly the full benefit at a fraction of the token cost.

Independent work on different benchmarks and model scales lands in the same place: gains concentrate in the first two rounds, with pass-rate lifts of +4.9 to +17.1 pp on HumanEval and +16.0 to +30.0 pp on MBPP fading fast across five attempts ([Arimbur, 2026](https://arxiv.org/abs/2604.10508v1)). The practical default is a low cap plus a stop-on-plateau check — end the loop when a round produces no measurable improvement rather than running a long fixed budget.

This budgets a different resource than [execution budgeting](execution-budgeting-program-repair.md). That page caps how often a repair agent runs the test suite within one attempt; this page caps how many repair rounds the loop runs at all. The two compose: bound the rounds, then bound the executions inside each round.

## Why it works

The early-gain concentration follows from the asymmetry between generating a fix and verifying one. Verification is discriminative and generation is creative, so the first feedback rounds cheaply catch errors that are easy to detect even though they were hard to avoid — compile failures and shallow test breaks resolve first. By the third round the model has consumed the high-signal feedback the oracle can supply, so later rounds mostly re-attempt variations of the same fix. The study reports this as a consistently concave completion curve across all tools and models, and attributes the shape more to workflow orchestration and feedback design than to the underlying model ([Kiecker et al., 2026](https://arxiv.org/abs/2607.05197)). The cap is therefore a property of the loop, not of any one model.

## When this backfires

A fixed cap of three is a lossy proxy for "stop when gains plateau," and the proxy breaks in four cases.

- Strong models on hard error classes keep improving past round three. Frontier models still make progress on logic and assertion errors — the class that stays around 45% unresolved even late in the search — so a hard cap abandons instances that were still yielding ([Arimbur, 2026](https://arxiv.org/abs/2604.10508v1)). Prefer plateau detection over a constant here.
- A weak or thin oracle inverts the aim of extra rounds. Systems that iteratively refine code against a limited visible test suite can worsen test overfitting on SWE-bench, so higher visible pass rates need not mean better held-out correctness ([Ahmed et al., 2025](https://arxiv.org/abs/2511.16858)). The cap then protects correctness, not just cost — but the right number tracks oracle quality rather than a universal constant.
- No external signal in the loop voids the finding. The diminishing-returns curve assumes a real oracle — tests or a compiler — feeding each round. Intrinsic self-critique with no external feedback does not follow the same early-gain shape and can degrade from the first round, so this result does not license capping a self-critique loop "for the same reason" ([Kiecker et al., 2026](https://arxiv.org/abs/2607.05197)).
- Free execution removes the point of the cap. When each round costs near-zero — sub-second local tests, no metered API — the token argument loses force and a hard cap saves little worth the harness complexity.

## Example

A plateau-aware loop keeps the low default but does not abandon a run that is still improving:

```python
def repair_loop(candidate, oracle, max_rounds=4, plateau_patience=1):
    best_score = oracle.score(candidate)
    stale = 0
    for _ in range(max_rounds):
        if oracle.passes(candidate):
            return candidate                     # done — no further rounds
        candidate = model.repair(candidate, oracle.feedback(candidate))
        score = oracle.score(candidate)
        if score <= best_score:
            stale += 1
            if stale > plateau_patience:
                break                            # no gain — stop early
        else:
            best_score, stale = score, 0
    return candidate
```

The load-bearing parts are the low `max_rounds` default and the plateau break. The exact ceiling is a calibration knob tuned to the oracle and model, not a constant to hard-code.

## Key Takeaways

- Most achievable gains in a generate-validate-repair loop land in the first three to four rounds; later rounds mostly burn tokens for marginal return ([Kiecker et al., 2026](https://arxiv.org/abs/2607.05197)).
- Two independent studies across different tools, benchmarks, and model scales report the same concave curve, so a low default cap is a safe starting point ([Arimbur, 2026](https://arxiv.org/abs/2604.10508)).
- Prefer stop-on-plateau over a fixed constant — strong models on hard bugs keep improving past round three.
- With a thin test oracle, iterative refinement can worsen test overfitting on SWE-bench, so the cap guards correctness as well as cost ([Ahmed et al., 2025](https://arxiv.org/abs/2511.16858)).
- This caps repair rounds; [execution budgeting](execution-budgeting-program-repair.md) caps test runs within a round. Use both.

## Related

- [Execution Budgeting in Agentic Program Repair](execution-budgeting-program-repair.md) — caps how often tests run within an attempt; this page caps how many attempts run.
- [Staged Evidence Gates for Agentic Program Repair](staged-evidence-gates-program-repair.md) — orders which evidence gates fire inside each repair round; pairs with a round budget.
- [Re-Run the Original Test Suite After Every Refinement Turn](test-suite-after-refinement-turn.md) — catches the correctness regressions that extra repair rounds can silently introduce.
- [Baseline-Aware Test Evaluation for Multi-Agent Issue Resolution (Phoenix)](baseline-aware-test-evaluation-issue-resolution.md) — strengthens what each round's test signal actually tells you.
- [Use pass@k and pass^k to Separate Agent Capability from Consistency](pass-at-k-metrics.md) — the metrics that show whether extra rounds add capability or just retries.
- [Validity-Estimate Stopping for Noisy Verify-Repair Loops (VRR-Stop)](validity-estimate-stopping-noisy-repair-loops.md) — the complementary stop rule for when the verifier is noisy rather than a real oracle; stop on estimated validity, not a fixed round count.
- [Profiler-Guided Optimization Loops for Coding Agents](profiler-guided-optimization-loop.md) — changes what signal each round acts on rather than how many rounds run, for the performance-optimization case.
- [Blind Resampling Over Self-Repair in Small Code Models](../loop-engineering/blind-resampling-over-self-repair.md) — asks whether a round should carry the failed attempt at all; below 7B it should not.
- [Behavior-Partitioned Security Tests as Executable Specs](behavior-partitioned-security-tests.md) — why some rounds are inert rather than low-yield: the visible oracle is silent on whole security behavior families.
- [Specification-First Convergence Without a Test Oracle](../workflows/specification-first-convergence.md) — a reported audit loop whose per-cycle findings rose again at round 15, so this cap did not transfer.
