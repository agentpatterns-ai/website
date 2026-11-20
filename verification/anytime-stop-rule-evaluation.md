---
title: "Anytime Evaluation of Stop Rules for Coding Agents"
term: "Anytime Stop Evaluation"
description: "Replay recorded coding-agent runs to score a stop rule offline. In one study the deployable rule saved 22.8% of cost, with non-inferiority not established."
tags:
  - testing-verification
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - anytime evaluation
  - replay-based stop rule evaluation
last_reviewed: 2026-11-19
maturity: emerging
---

# Anytime Evaluation of Stop Rules for Coding Agents

> Replaying recorded coding-agent runs scores a stop rule offline; in one study the deployable rule saved 22.8% without establishing non-inferiority.

Anytime evaluation replays recorded runs, scores every intermediate patch with hidden tests, and prices each step, so a rule that only ends a run or picks an earlier patch is tested on runs you already have. In the primary study the hindsight saving at passing self-tests ran from under 1% to 57% of cost across eight open models in two scaffolds on SWE-bench Verified: 57% for Qwen3.6-27B in SWE-agent, 25% in mini-SWE-agent ([Yang et al., 2026](https://arxiv.org/abs/2611.22901v1), Abstract, §4.3). Those bounds read the hidden tests, so no deployable rule reaches them. The deployable rule, stop when the same patch passes a self-test twice, saved 22.8% at -1.0 points on 386 new Qwen3.6-27B runs in mini-SWE-agent, but the preregistered test did not establish non-inferiority (Table 2, §4.3). Tasks are limited to those whose gold patch passes, and no closed-API model was run (§3, §7).

## Why the quality effect varies

A rule changes nothing before it fires, so its quality change is ΔQ = −r·u·δ (§2, Equation 3). The terms are r, the share of runs where it fires; u, the share of those whose final patch differs from the patch at the stop; and δ, the net repair per change. Only δ needs hidden tests.

- The twice-passed rule lost 2.8 points in SWE-agent and 0.3 in mini-SWE-agent, with similar δ (0.08 and 0.07). The difference was u: 40% of runs changed the patch after the stop point in SWE-agent, 10% in mini-SWE-agent (§4.4).
- DeepSeek-V4-Flash has δ of -0.18. Its later changes break more patches than they repair, so stopping raised resolution 0.9 points (§4.4).
- For Qwen3-Coder, Gemma-4, and GLM-4.7-Flash, r was 6% or less. They seldom see the repository's tests pass, so the rule never fires (§4.4).

## What replay can and cannot test

The identity holds for rules that read the observed prefix and only end the run or choose among its patches. A different prompt, a question to the agent, or a fine-tuned model changes the prefix and needs new runs (§2, Proposition 1). Final-patch reconstruction matched 4,009 of 4,012 runs; intermediate states are unchecked (§4.2). On 178 tasks, detecting a 2-point change at 80% power took 56 tasks offline and 1,184 online (Appendix O).

These did not work as stop rules (§4.5 unless noted):

- An instruction to submit once the relevant tests pass saved 8.4% (preregistered).
- Asked at its first passing self-test, the agent said submit in 6-7% of 439 cases.
- A fresh judge of the same model saved 14.0%, against 20.8% for the twice-passed rule on the same runs.
- A turn cap at the 75th percentile of run length saved 13-21% and lost 8-16 points under the paper's older scoring convention (Appendix F).

## A second source on the tail

A second paper ([Cim et al., 2026](https://arxiv.org/abs/2611.14960v1)) measures the same tail in steps, with each task run once. In runs that reach a correct patch, the first source edit was already correct in 38-82% (Table 2). Post-solution steps were a median of 35-37% for Qwen3-Coder and 54-60% for Laguna-XS.2 in successful runs on Verified and Multilingual. Verification took 48-63% of steps after the first correct patch, and 1-8% of runs broke a correct patch (§1, RQ3, RQ4). These are step shares against a hidden-test oracle, not comparable with the primary paper's cost shares.

## When this backfires

- In SWE-agent the twice-passed rule fired in 88% of runs, saved 54.2%, and lost 2.8 points, failing the quality criterion. Between the first pass and the end, 24 failing patches became passing and 3 passing ones failed (Appendix J).
- A self-test pass is a weak signal: hidden tests failed in about 30% of runs where it fired (§7).
- Hidden tests are an imperfect oracle. 7.8% of SWE-bench patches count as correct while failing the developer-written suite ([Wang et al., 2025](https://arxiv.org/abs/2503.15223v2)).
- First-pass stopping saves 24-31% and loses up to 3.9 points (§4.3), which is [premature completion](../patterns/anti-patterns/premature-completion.md) adopted as policy.

## What to do

1. Log per-step patches and token counts for a sample of your agent's runs.
2. Replay the rule offline and measure r, u, and the cost saved. None needs labels.
3. Check δ on fired-and-changed runs against your strongest test oracle.
4. Adopt the rule only if r is large enough to matter and u is small.

## Example

Twice-passed against first-pass stopping on Qwen3.6-27B in mini-SWE-agent. Each cell is the change in resolution in points, then the change in cost, relative to running to the end (Table 2, §4.3). Run counts are in the headers.

| Rule | Derivation (712) | Fresh tasks (230) | New repos (156) | New runs (386) |
|------|------------------|-------------------|-----------------|----------------|
| Self-test passed | +0.4 / -23.9% | -3.9 / -31.1% | -1.3 / -27.3% | -1.8 / -30.5% |
| Passed twice on one patch | +0.7 / -17.5% | -1.7 / -23.1% | -1.3 / -17.6% | -1.0 / -22.8% |

The rule was designed on the derivation runs, so that column is in-sample.

## Key Takeaways

- Treat a stop rule's saving and its quality cost as two measurements. The saving comes from unlabeled runs, and the cost needs δ.
- A hindsight bound shows what is available, and a preregistered replication shows what a deployable rule keeps.
- The result covers open models, two scaffolds, and tasks whose gold patch passes. Replay your own runs before adopting a rule.

## Related

- [Cut-Point Replay: Test a Fix Against a Recorded Agent Run](cut-point-replay-agent-regression-tests.md)
- [Random Restart as the Baseline for Agent Early Stopping](../patterns/anti-patterns/random-restart-as-the-stopping-baseline.md)
- [Observed-Pass Token Accounting for Post-Success Agent Spend](../token-engineering/observed-pass-token-accounting.md)
- [Re-Run the Original Test Suite After Every Refinement Turn](test-suite-after-refinement-turn.md)
- [Trajectory Decomposition: Diagnose Where Coding Agents Fail](trajectory-decomposition-diagnosis.md)
- [Circuit Breakers for Agent Loops](../observability/circuit-breakers.md)
- [Harness-Enforced Stopping on Judged-Useless Tool Results](../patterns/agent-design/enforced-stop-on-useless-results.md)
- [Pass-Only Grading Treats Luck and Judgment the Same](../patterns/anti-patterns/pass-only-grading-lucky-pass.md)
