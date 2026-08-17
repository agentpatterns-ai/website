---
title: "Retry-Switch-Abstain: A Runtime Tool-Recovery Policy"
term: "Strategy-Aware Tool Recovery"
description: "Hand the agent a fallback map and recovery constraints in context so it can retry, switch tools, or stop — worth up to 16.8 points of robustness, and only where failures are observable."
tags:
  - agent-design
  - tool-agnostic
  - testing-verification
  - reliability
  - arxiv
aliases:
  - strategy-aware tool-use policy
  - retry, switch, or abstain
  - runtime tool recovery context
  - fallback map for tool failures
last_reviewed: 2026-08-14
maturity: emerging
---

# Retry-Switch-Abstain: A Runtime Tool-Recovery Policy

> A runtime recovery policy hands the agent a fallback map and constraints, so it retries, switches tools, or stops instead of looping.

Strategy-aware tool recovery supplies the agent, at prompt time, with two things it cannot derive from its own trajectory: which other tool is interchangeable with the one that just failed, and when to stop trying. On 402 held-out Retail tasks under injected tool failure, this context raised the pass rate from 20.1% to 36.9% with no retraining ([Chen et al., arxiv:2608.11977v1](https://arxiv.org/abs/2608.11977v1)).

## The conditions come first

Three preconditions decide whether the artifact is worth building:

- Genuine alternatives exist. A tool surface where every capability is singular gives the switch route nothing to point at.
- Failures announce themselves. Timeouts, rate limits, and malformed responses gained 18 to 25 points from the added context. On silent factual corruption the same intervention lost ground, "the only negative entry in the table" at −4.6 points ([2608.11977v1](https://arxiv.org/abs/2608.11977v1)).
- Someone owns the map. The paper supplies the fallback structure as domain-specific environment configuration and describes no automated way to build one ([2608.11977v1](https://arxiv.org/abs/2608.11977v1)), so maintaining it is your cost. An unmaintained map is the setup for [belief inertia after tool-map drift](../anti-patterns/belief-inertia-after-tool-map-drift.md).

## Three routes, one decision

The taxonomy is the reusable part. Each scenario admits exactly one correct response:

| Scenario | State of the tool surface | Correct response |
|---|---|---|
| Retry works | No path permanently blocked | Retry the original path |
| Switch needed | One side of a fallback-equivalence class is blocked for the episode | Call the equivalent tool |
| Impossible | Every viable path is blocked | Stop and escalate |

The middle row is where retry-only agents fail structurally: "task completion requires a fallback-equivalent tool" and no amount of repetition produces one ([2608.11977v1](https://arxiv.org/abs/2608.11977v1)).

## What you actually ship

The paper's ablation is the practitioner's shortcut. Static structure alone recovered 10.5 of the 14.6 points; calibrated reliability estimates added 1.7. The authors conclude that "most of this gain should be attributed to fallback structure and recovery constraints rather than to calibrated posterior values" ([2608.11977v1](https://arxiv.org/abs/2608.11977v1)). The shippable artifact is therefore a list of interchangeable tool pairs plus three constraints: retry before abandoning a path, verify before irreversible actions, escalate only after available recovery paths have been considered. Failure statistics are optional.

## Why it works

The authors read the result as knowledge supply rather than better reasoning, and are explicit that they did not measure the mechanism: they call it "an error-regime association rather than a direct mechanism measurement", supporting a functional distinction "without establishing a specific internal mechanism". Under failure the agent is missing facts about the environment that no trajectory reveals, and the context injects them directly. The per-error breakdown is what that reading rests on: the effect is largest on observable transient errors where a fallback route and a retry rule are immediately actionable, and it inverts on factual corruption, which no fallback map addresses ([2608.11977v1](https://arxiv.org/abs/2608.11977v1)). A capability story would not predict a sign flip by error type.

The gap it closes is not model-specific. Across seven models from four families, "of 70 (model, subset) pairs, 69 degrade (−1.8 to −46.7pp)" once tool failures are injected ([2608.11977v1](https://arxiv.org/abs/2608.11977v1)). A larger model does not close it.

## When this backfires

- Silent failures dominate the surface. Structurally valid but wrong data needs cross-referencing, and recovery context measurably hurt here. The authors offer one unverified explanation, that the added context raises the model's propensity to retry and a refetched value is corrupted again, and say they "did not isolate this mechanism experimentally" and cannot rule out an alternative ([2608.11977v1](https://arxiv.org/abs/2608.11977v1)).
- Long trajectories retain failure history. A retry constraint pushes against context contamination: the failed attempt stays in the window and raises the per-step error rate, with a fit implying a contaminated-to-base error ratio of about 7.1, with the independent-attempt model overestimating pass@3 by 17.4 points on SWE-bench Verified ([Yang, arxiv:2605.08563v1](https://arxiv.org/abs/2605.08563v1)). Pair the retry rule with a context-clearing policy.
- The stop route is the least validated third. Impossible episodes were used only in training, "because the underlying benchmark evaluators do not assign positive completion credit to unsolvable tasks," and the authors list an incomplete abstention reward as a limitation ([2608.11977v1](https://arxiv.org/abs/2608.11977v1)). Independent work puts the best of 17 frontier agents at 59.5% paired act-or-abstain accuracy ([AgentAbstain, arxiv:2607.10059v1](https://arxiv.org/abs/2607.10059v1)), and agents that stop too readily may fail solvable tasks and shift responsibility back to the user ([Agentic Abstention, arxiv:2606.28733v1](https://arxiv.org/abs/2606.28733v1)).
- The policy could live below the model. Retry and fallback logic in deterministic middleware costs no tokens, is testable, and cannot be argued out of its rules by a contaminated context. Since the measured gain comes from static structure, a router can enforce most of it without a model call. See [Agent Circuit Breaker](agent-circuit-breaker.md) for the blocking half of that argument.

## Example

The evidence above came from a framework that turns failure-free tool-use benchmarks into stochastic ones by injecting errors of known solvability. Its default budget leaves a 0.60 chance of a clean call and spreads the rest across nine error types, capped per tool and at two consecutive failures ([2608.11977v1](https://arxiv.org/abs/2608.11977v1)). Copy that shape before you copy the pattern: run your existing agent evals behind a proxy that fails a known fraction of calls, labeling each episode by which route should have solved it. If nothing lands in the switch row, the fallback map has nothing to earn back.

## Key Takeaways

- Classify the failure before choosing a response. Repetition cannot solve an episode whose only remaining path is a different tool.
- Skip the reliability statistics on the first pass. A tool-pair table and three constraints carried most of the measured gain.
- Check the error mix before adopting. Observable failures gained 18 to 25 points; factual corruption regressed.
- The stop route ships unmeasured. Instrument how often your agent escalates and how many of those tasks were solvable.

## Related

- [Agent Circuit Breaker](agent-circuit-breaker.md) — blocks calls to a tool once it degrades, where this pattern routes around it to a declared equivalent
- [Informed Abstention as a Tool-Boundary Runtime Gate](informed-abstention-tool-boundary-gate.md) — gates before execution on a missing precondition; this is the post-failure half of the same decision
- [Task Feasibility Awareness: Stop Before You Start](task-feasibility-awareness.md) — checks the tool manifest up front, so nothing is attempted when the capability is simply absent
- [Exception Handling and Recovery Patterns](exception-handling-recovery-patterns.md) — the broader escalation hierarchy this policy slots into
- [Belief Inertia After Tool-Map Drift](../anti-patterns/belief-inertia-after-tool-map-drift.md) — what a stale fallback map produces once the tool surface moves underneath it
