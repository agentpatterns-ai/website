---
title: "Re-Run the Original Test Suite After Every Refinement Turn"
term: "Re-Run the Original Test Suite After Every Refinement Turn"
description: "Multi-turn LLM code refinement silently breaks previously-passing code — instruction adherence does not correlate with functional correctness, so re-execute the original test suite after every refinement turn rather than trusting the diff."
aliases:
  - per-turn regression check for code refinement
  - functional-correctness preservation across refinement turns
tags:
  - testing-verification
  - tool-agnostic
  - arxiv
last_reviewed: 2026-06-28
maturity: emerging
---

# Re-Run the Original Test Suite After Every Refinement Turn

> Multi-turn LLM code refinement silently breaks previously-passing code; re-run the original test suite after every turn because instruction adherence does not predict functional correctness.

Follow-up refinement requests in a multi-turn coding dialogue — "make it more readable", "use a generator instead", "also handle the empty input" — degrade functional correctness even when the model carries out the request exactly as asked. The original test suite, executed after every turn, is the only signal available to the developer or harness that catches the silent regression.

## The silent-regression mechanism

A model optimises each refinement against the stated intent of the user's turn, not against the invariant that the original test suite encodes. The two come apart sharply. CodeChat-Eval evaluated 8 LLMs across 4 families on 542 tasks (164 HumanEval + 378 MBPP) over 10-turn dialogues (one initial generation plus nine refinement turns), grading every turn against EvalPlus extended test cases. The headline measurement: the Phi coefficient between instruction adherence and functional correctness is 0.089, a negligible correlation ([Guo et al., 2026](https://arxiv.org/abs/2606.25747)).

That single number is load-bearing. A developer reading the diff can verify the model did what was asked. They cannot, at face value, tell whether behaviour was preserved — the Phi 0.089 says the two are statistically independent for this task. Re-executing the test suite is the only externalised invariant that catches the gap.

The regression rate is monotonic across turns and scales inversely with model strength:

| Model | Functional correctness drop (turn 0 → 9) |
|---|---|
| GPT-5 Nano | 19.2 – 24.4% |
| GPT-5 | 20.3 – 27.1% |
| DeepSeek-V3 | 23.5 – 26.6% |
| Qwen 2.5 Coder 32B | 33.8 – 42.9% |
| Qwen 2.5 Coder 7B | 47.9 – 52.0% |
| Llama 3.3 70B | 50.4 – 56.4% |
| Llama 3.1 8B | 66.7 – 69.2% |

Frontier models lose a fifth of their correctness over nine turns; weaker open models lose two thirds ([Guo et al., 2026](https://arxiv.org/abs/2606.25747)).

Independent corroboration from a different benchmark and 32 additional models: MT-Sec reports a consistent 20 – 27% drop in "correct and secure" outputs from single-turn to multi-turn settings, even on state-of-the-art models, and notes that single-turn agent scaffoldings transfer poorly to the multi-turn setting ([Mishra et al., 2026](https://arxiv.org/abs/2510.13859)).

## Refinement-type signal

CodeChat-Eval decomposes the regression by the kind of refinement. The shape tells you which turns most need the gate ([Guo et al., 2026](https://arxiv.org/abs/2606.25747)):

- Scope: cosmetic refinements regress 7 – 13%; semantic (logic-changing) refinements regress 21%, the highest.
- Operation: `add` operations regress 17% (highest); `modify` is intermediate; `remove` causes the lowest damage.

A turn that touches logic or adds code is the most likely to break the suite. A turn that only changes formatting still breaks it 7 – 13% of the time — no operation is safe to skip.

The same data carries a counter-direction: roughly 12.6% of previously-failing tasks self-correct during refinement (Qwen 2.5 Coder 14B reaches the highest rate). Net regression still dominates, but the suite is the only signal that distinguishes "this turn fixed a latent bug" from "this turn broke a passing test" — both look like a working refinement in the diff.

## How to wire it

A single principle: every refinement turn produces a candidate patch, and the original test suite is the differential gate. The same primitive as [baseline-aware test evaluation](baseline-aware-test-evaluation-issue-resolution.md), applied along the turn axis rather than the patch axis.

Three components:

1. Pin the original test suite at the start of the session and treat it as the invariant. Re-running a *refined* test suite leaks behavioural drift into the gate.
2. Run the suite at every turn that lands code — not only on `add` or `semantic` operations. The 7 – 13% cosmetic regression rate is the residual that catches refactors which were not as behaviour-neutral as the model believed.
3. Surface a diff between baseline pass-set and current pass-set, not the absolute pass rate. The "I broke something I didn't" false positive and the "all green, ship it" false-green that [baseline-aware test evaluation](baseline-aware-test-evaluation-issue-resolution.md) names both apply per-turn.

This sits cleanly inside [incremental verification](incremental-verification.md), which already prescribes checkpoints between agent steps. The refinement axis is the specific instance: the step is one turn, the checkpoint is the original suite, the recovery is to reject the turn and ask again.

## Why It Works

Preserving behaviour across a refinement is not in the model's loss function for that turn. The model optimises for the user's stated request; the Phi 0.089 measurement says compliance with that request is statistically independent of whether behaviour was preserved. The original test suite is the externalised invariant the model is not optimising against, so re-executing it surfaces violations the model's self-evaluation cannot see — the same lever [baseline-aware test evaluation](baseline-aware-test-evaluation-issue-resolution.md) pulls on the patch axis. The independence finding is what keeps the gate non-redundant against diff review: a clean diff is evidence of compliance, not of preservation.

## When This Backfires

The gate is not free, and the suite has to be load-bearing for the diff to mean anything.

- The test suite is weak. SWE-bench analysis shows 7.8% of test-passing patches fail developer-written tests, and 29.6% diverge from the ground-truth patch even when tests pass ([Aleithan et al., 2025](https://arxiv.org/abs/2503.15223)). A thin suite re-run after every turn produces a stream of false-greens. Strengthen the suite first, or treat it as a filter rather than a guarantee.
- Tests are flaky. A flaky baseline corrupts the differential signal. False positives train the developer to ignore real regressions, and the gate becomes anti-signal.
- Per-turn CI cost exceeds the catch rate. For multi-minute integration or browser suites, the per-turn cost can exceed the regression-catch value in short two- or three-turn sessions. Gate at end-of-session for short interactive sessions; reserve per-turn execution for autonomous loops and longer dialogues where the Phi-0.089 gap compounds.
- The session is purely cosmetic or removal-only. The 7 – 13% cosmetic rate is non-trivial but lower than the 21% semantic rate; the marginal benefit narrows in style-only sessions and pure deletions ([Guo et al., 2026](https://arxiv.org/abs/2606.25747)).
- The harness already trusts the model. Pairing the gate with a "trust the agent's PR summary" workflow rebuilds the loop the gate is meant to break — the conjugate anti-pattern is [trust without verify](../patterns/anti-patterns/trust-without-verify.md).

## Example

A refinement session with three turns against a HumanEval-style task. The original suite has eight tests, all passing on turn 0.

```
Turn 0  (initial generation)         original tests: 8/8 pass
Turn 1  "Use a list comprehension"   original tests: 8/8 pass
Turn 2  "Also handle empty input"    original tests: 7/8 pass  -- regression
Turn 3  "Add a docstring"            original tests: 7/8 pass  -- unchanged
```

Turn 2 is the silent regression. The developer's request was a benign extension ("also handle empty input"); the model added the empty-input branch and, in doing so, changed a boundary condition that one of the original tests exercised. The diff looks clean — a guard clause added at the top of the function — and the model's stated change matches the request. Only the suite re-run catches it.

Without the per-turn re-run, the regression survives until end-of-session CI or first user complaint. With it, the rejected turn is replayed: the developer asks again with the failure surfaced ("the empty-input branch broke `test_single_element` — try again preserving the original behaviour on non-empty inputs"), and the next attempt is conditioned on the actual invariant rather than the stated intent.

## Key Takeaways

- The Phi coefficient between instruction adherence and functional correctness over multi-turn code refinement is 0.089 — the model can follow the instruction perfectly and still break previously-passing tests, because preservation is not in the per-turn loss function.
- Functional correctness drops 19 – 27% over nine refinement turns on frontier models, 50 – 69% on weaker open models; independent corroboration on 32 additional models reports the same 20 – 27% direction.
- Logic-changing (`semantic`) refinements and code-`add` operations have the highest regression rates (21% and 17% respectively); even cosmetic refinements regress 7 – 13% of the time.
- The fix is differential testing along the turn axis: pin the original suite, run it after every turn, gate on the diff between baseline pass-set and current pass-set — not the absolute pass rate.
- The gate is anti-signal when the suite is weak, flaky, or expensive enough that per-turn cost exceeds catch rate; strengthen and stabilise the suite first.

## Related

- [Baseline-Aware Test Evaluation for Multi-Agent Issue Resolution (Phoenix)](baseline-aware-test-evaluation-issue-resolution.md)
- [Multi-Turn Conversation Evaluation](multi-turn-conversation-evaluation.md)
- [Incremental Verification: Check at Each Step, Not at the End](incremental-verification.md)
- [Trust Without Verify](../patterns/anti-patterns/trust-without-verify.md)
- [Pre-Change Impact Analysis](pre-change-impact-analysis.md)
- [Generating Tests From Agent-Written Code (Code-First Oracle Bias)](../patterns/anti-patterns/code-first-test-oracle-bias.md) — a code-first test suite is not an independent oracle; the sibling ordering trap on the code-vs-spec axis
- [Validity-Estimate Stopping for Noisy Verify-Repair Loops (VRR-Stop)](validity-estimate-stopping-noisy-repair-loops.md) — when to stop a repair loop once the verifier itself is noisy and its acceptance signal no longer tracks true validity
