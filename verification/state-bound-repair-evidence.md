---
title: "State-Bound Evidence and Typed Revision Contracts for Repair Loops"
term: "State-Bound Evidence"
description: "A repair loop can find a correct patch and then destroy it; bind every test result to the code state that produced it, preserve the last verified candidate, and admit only typed revision actions."
tags:
  - testing-verification
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - "state-bound repair evidence"
  - "typed revision contract for repair loops"
  - "evidence-to-state hash binding"
last_reviewed: 2026-07-28
maturity: emerging
---

# State-Bound Evidence and Typed Revision Contracts for Repair Loops

> Bind every test result to the code state that produced it, and preserve the last verified candidate, so revision cannot destroy a correct patch.

A generate-test-revise loop can find a correct patch and then throw it away. Across 900 forced-revision trajectories over 30 HumanEval repairs, current correctness fell from 0.820 after one revision to 0.673 after two while cumulative ever-correct rose to 0.847; 16.0% of trajectories held a correct patch and lost it by revision three ([Gao et al., 2026](https://arxiv.org/abs/2607.24604v1)). Finding the answer, retaining it, verifying it, and submitting it are four separate obligations. A bare loop implements only the first.

## When this earns its cost

Adopt the full apparatus only when your loop matches the regime it defends against. The source's own prospective evaluation missed its bar, so treat evidence hygiene as the default and the machinery as conditional.

- Your loop revises after a passing result, or on a fixed budget. The measured degradation comes from forced revision, which the authors call not a natural adaptive policy; an agent that halts when the suite goes green rarely enters this regime ([Gao et al., 2026](https://arxiv.org/abs/2607.24604)).
- Test output can outlive the edit that produced it. Any path that carries a trace or failure report across a code change creates the stale-evidence condition.
- You can absorb the liveness cost. In a prospective 540-rollout paired policy the guard eliminated observed correct-start harm but cut wrong-start repair from 100/135 to 93/135 and sound completion from 219/270 to 211/270, missing its five-point non-inferiority criterion ([Gao et al., 2026](https://arxiv.org/abs/2607.24604)).

If none of those hold, take the cheap half only: never carry a test result across an edit, and keep a copy of the last candidate that passed.

## The typed revision contract

The contract replaces free-form revision output with three mutually exclusive actions ([Gao et al., 2026](https://arxiv.org/abs/2607.24604)):

- `Keep` — return the current code unchanged. This absorbing state is where an agent's bare "STATUS: DONE" with no code belongs, instead of being read as a corrupt state.
- `Patch(code)` — replace the current state, admitted only when the payload parses and executes.
- `Escalate(reason)` — abstain with a stated reason instead of guessing.

Around those actions sit five obligations a bare loop conflates: admission (only a valid `Patch` replaces state), preservation (retain and exactly restore the last verified candidate), grounded certification (re-execute checks against the state you actually ship), competence (the coder's ability to use evidence), and liveness (whether the orchestrator finishes). Separating them distinguishes a loop that cannot repair from one that repaired and lost the result.

This is a different lever from its neighbors: [bounded repair-loop iterations](bounded-repair-loop-iterations.md) caps how many rounds run, [validity-estimate stopping](validity-estimate-stopping-noisy-repair-loops.md) fixes when to stop under a noisy verifier, and [re-running the original suite](test-suite-after-refinement-turn.md) detects the regression. This page is about not losing what the loop already proved.

## Why it works

A test result records the code hash, suite hash, and execution that produced it. When that code hash no longer matches the current state, the trace still reports true input and output facts — but about a different program, while reading to the model as a description of the code in front of it. The report "contains valid input/output facts, but falsely asserts that they describe the current code" ([Gao et al., 2026](https://arxiv.org/abs/2607.24604v1)). Rejecting or refreshing evidence whenever the hashes diverge removes a persuasive but wrong input, rather than asking the model to notice the mismatch. In a prespecified 14B replication over frozen common states, stale traces harmed 34 of 135 correct starts against 4 of 135 with current traces — a 22.2-point increase, task-cluster 95% confidence interval [8.9, 37.0], exact Holm p=0.0337 ([Gao et al., 2026](https://arxiv.org/abs/2607.24604v1)). Replay showed state binding intercepting every stale-condition harm at both model sizes.

## When this backfires

- Repository-scale work with a low acceptance floor. Over 24 bugs and four coder stacks, the base model produced five accepted completions and the contract produced zero; the joint intersection-union test failed ([Gao et al., 2026](https://arxiv.org/abs/2607.24604)). An admission boundary can zero out liveness before it prevents any harm.
- Small models on single-file benchmarks are where the effect was measured, and mostly not significantly: all six 7B contrasts and five of six 14B contrasts were nonsignificant after Holm correction, and the 30 HumanEval tasks may sit in training data ([Gao et al., 2026](https://arxiv.org/abs/2607.24604v1)).
- Weak oracles. Only oracle-covered properties are preserved ([Gao et al., 2026](https://arxiv.org/abs/2607.24604)), so a preserved checkpoint that passes an under-specified suite preserves an overfitted patch as faithfully as a correct one.
- Loops where iteration genuinely pays. Self-feedback refinement improves outputs by roughly 20% absolute on average across seven tasks with no evidence binding ([Madaan et al., 2023](https://arxiv.org/abs/2303.17651v2)). Repetition is not inherently destructive; stale inputs are.

The reference implementation carries the same caution: it passes 35 deterministic failure-injection cases, but the authors state it is "an executable specification and conformance artifact, not evidence of improved repair competence or calibrated verifier dependence" ([Gao et al., 2026](https://arxiv.org/abs/2607.24604v1)).

## Example

On HumanEval/89 the agent held a trace generated from code that used a Caesar shift of 12. The code had since been fixed to use a shift of 4. The trace's input and output values were accurate for the program that produced them, and the model read them as a description of the current program, so all five seeds reverted the correct shift-4 solution back to shift 12 ([Gao et al., 2026](https://arxiv.org/abs/2607.24604)). A hash comparison between the trace's recorded code state and the current one rejects that evidence before the model ever sees it.

## Key Takeaways

- Measure ever-correct alongside final correctness. A loop that reaches 0.847 ever-correct and submits 0.673 has a retention problem, not a repair problem ([Gao et al., 2026](https://arxiv.org/abs/2607.24604)).
- Never carry a test result across an edit. Stale traces cause active harm, and the fix is a state-hash comparison rather than a prompt asking the model to check freshness.
- Keep the last candidate that passed, and re-run the checks against the state you actually ship rather than the state you last tested.
- Type the revision output. `Keep`, `Patch(code)`, and `Escalate(reason)` make an unparsable response a no-op instead of a corrupted state.
- Expect the full contract to cost liveness. The source's own guarded policy failed its non-inferiority criterion and dropped repository acceptances to zero, so measure both harm avoided and work lost.

## Related

- [Re-Run the Original Test Suite After Every Refinement Turn](test-suite-after-refinement-turn.md) — detects the silent regression this page tries to prevent.
- [Validity-Estimate Stopping for Noisy Verify-Repair Loops (VRR-Stop)](validity-estimate-stopping-noisy-repair-loops.md) — the stopping-rule answer to correct-to-incorrect repair when the verifier is itself noisy.
- [Evidence-Gated Lifecycle Control for Coding Agents (Proof-or-Stop)](evidence-gated-lifecycle-control.md) — the same freshness-binding idea applied to lifecycle state rather than revision input.
- [Bounded Repair-Loop Iterations](bounded-repair-loop-iterations.md) — caps how many rounds run, which limits exposure to the degradation described here.
- [Selective Checkpoint Restore Across Code and Conversation State](../patterns/agent-design/selective-checkpoint-restore.md) — the harness affordance that makes preserving and restoring a verified candidate practical.
