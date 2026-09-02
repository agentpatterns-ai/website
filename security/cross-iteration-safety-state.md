---
title: "Cross-Iteration Safety State for Agent Loops (LoopHarness)"
term: "Cross-Iteration Safety State"
description: "Keep grounded risk evidence across loop iterations instead of resetting it, because a per-iteration monitor is provably at chance against evidence split across runs."
tags:
  - security
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - non-decaying loop state
  - cross-iteration risk cumulant
  - loop-level safety state
last_reviewed: 2026-08-30
maturity: emerging
---

# Cross-Iteration Safety State for Agent Loops (LoopHarness)

> A safety monitor that resets each loop iteration cannot see a fragmented attack; retained cross-iteration risk state is where the evidence lives.

An unattended agent loop discovers work, plans, calls tools, verifies and persists what it learned, then decides on its own to continue. Its safety machinery does not carry over. Wu et al. call that reset a failure of composition rather than an implementation detail. Against an attack whose evidence is split across iterations, a monitor confined to one iteration performs exactly at chance, whatever its capacity ([arXiv:2608.27141v1](https://arxiv.org/abs/2608.27141v1)).

## When this applies

The impossibility result is unconditional. The fix, a retained risk value that never decays on its own, is not. Deploy it only when all four hold:

- The loop reads an open discovery channel, so an adversary controls what enters the queue. A closed queue of operator-supplied work carries no fragmentation surface.
- Some tool calls are irreversible and a budget already mediates them. Retention alone buys nothing: removing the governor raised attack success on the retention-targeted family from 0.0% to 97.0%, against the authors' own pre-registered prediction ([arXiv:2608.27141v1](https://arxiv.org/abs/2608.27141v1)).
- The risk value and its counters are integrity-protected. The guarantee assumes "no adversary action, restart or memory rollback lowers" the commit counter ([arXiv:2608.27141v1](https://arxiv.org/abs/2608.27141v1)), so without an authenticated checkpoint a memory compromise resets the state and the bound is void.
- A staffed escalation path exists. The paper is blunt about the alternative: "deploying a governor without a staffed escalation channel converts a safety mechanism into an availability failure" ([arXiv:2608.27141v1](https://arxiv.org/abs/2608.27141v1)).

## Why it works

The argument is informational rather than empirical. A trajectory-scoped monitor decides from one iteration's view alone. In an `s`-fragmented attack the adversary's contribution to each of the `s` iterations "is distributed exactly as a benign contribution, while the unauthorized capability appears only once all `s` fragments are jointly present in persistent state" ([arXiv:2608.27141v1](https://arxiv.org/abs/2608.27141v1)). Two identical distributions cannot be separated, so the monitor's true-positive rate equals its false-positive rate. A stronger model does not help, because the discriminating evidence is not in the window it sees. A monitor that reads the accumulated state reaches true-positive rate 1 at false-positive rate 0.

Carrying risk forward with a decay factor does not repair this. The gate reopens after a constant number of quiet iterations, independent of how long the loop runs, so a patient adversary waits it out once and proceeds ([arXiv:2608.27141v1](https://arxiv.org/abs/2608.27141v1)). Only a latch survives waiting: a rule-decidable violation of the loop's own admission, integrity or authorization contract pins the discount at 1, and elapsed time never releases it.

The layer sits outside the inner per-turn harness and leaves it unchanged, so it composes with whatever single-trajectory defense is already there. What crosses that boundary is narrow. Grounded attack evidence raises the retained value; action impact and verifier indecision route review inside the current iteration and never enter it or the latch, because "a legitimate authorized deletion may be high impact without indicating compromise" ([arXiv:2608.27141v1](https://arxiv.org/abs/2608.27141v1)).

## Example

A matched sweep isolates the update rule at horizon 10, over 200 attack episodes and 200 clean twins per row. A risk observation of magnitude 0.8 arrives, then 1, 2 or 4 quiet iterations pass before the gated target ([arXiv:2608.27141v1](https://arxiv.org/abs/2608.27141v1)):

| Update rule | Retained risk at the target | Attack success |
|---|---|---|
| Reset each iteration | 0.098 to 0.100 | 95.5% to 97.5% |
| Decay, no latch | 0.560, then 0.392, then 0.193 | 0.0%, then 97.0%, then 97.5% |
| Latch | 0.800 at all three intervals | 0.0% |

The decay row blocks at one quiet iteration and fails at two. That is the crossing the theory predicts, not a tuning accident. Clean-episode completion stayed between 95.5% and 97.5% across every row, so the latch cost no measured utility in this sweep.

## When this backfires

- The adversary only wants downtime. Under the availability condition, where tripping the risk latch is the sole objective, clean-episode completion for the full system fell to 0.0%, against 100.0% for the no-defense baseline ([arXiv:2608.27141v1](https://arxiv.org/abs/2608.27141v1)). A confidentiality defense becomes a reliable availability attack.
- The latch has no way out. The authors note that "the evaluated latch has no authenticated clearance transition". Persisted safety state over-generalizes: across 40 manual ChatGPT sessions, one correct copyright refusal caused 116 of 120 later unrelated benign image requests to be refused, against 0 of 40 in controls. That study covers one model and one interface, and reports behavior rather than architecture ([arXiv:2601.06049v1](https://arxiv.org/abs/2601.06049v1)).
- The guardrail is itself the target. Crafted input can trap a reasoning guardrail in long loops for 13 to 63 times the tokens and up to 148 times the latency, and one poisoned document can starve co-located agents ([arXiv:2606.14517v2](https://arxiv.org/abs/2606.14517v2)). Persistent state gives that attacker a cheaper target: trip the gate once and it stays shut.
- The horizon is short. Under the inner harness alone, compounding attack success ran 2.9% at 5 iterations and 6.2% at 10, then stayed flat out to 20 ([arXiv:2608.27141v1](https://arxiv.org/abs/2608.27141v1)). The authors decline to name a crossover point, because it depends on environment-specific compromise and detection rates.
- Stateful monitoring is not a solve on its own. In the code-review setting, [stateful cross-PR monitoring](distributed-cross-pr-attacks.md) cuts gradual-attack evasion from 93% to 47%, and a monitor more capable than the agent still misses 31% of successful attacks.

The evidence is one frozen cohort, one seed and one model-role assignment, with no multi-seed replication, on a scheduled discovery queue the authors say understates the admission problem a real deployment faces.

## Key Takeaways

- Reach for cross-iteration risk state when the loop reads an open channel and a budget already mediates irreversible calls. Below that bar, per-iteration reset is the cheaper trade.
- Do not ship a latch without an authenticated clearance transition and someone on call to use it. The evaluated system implements neither.
- Budget for the availability failure before the confidentiality one. Tripping the latch is the cheapest attack against a loop carrying this defense.
- Rule-decidable contract violations are the only signal worth latching. Model uncertainty and high action impact belong to the current iteration and must not persist.

## Related

- [Lifecycle-Integrated Security Architecture for Agent Harnesses](lifecycle-security-architecture.md) — the per-trajectory harness this composes over, and the one whose state resets.
- [Distributed Cross-PR Attacks in Persistent-State AI Control](distributed-cross-pr-attacks.md) — the same problem measured over pull requests, with an empirical ceiling on the stateful fix.
- [Context-Fractured Decomposition Attacks on Tool-Using Agents](context-fractured-decomposition-attacks.md) — the attack side: harm split across tools, modules and time.
- [Inline Safety Harness with Cascade Verification (FinHarness)](inline-lifecycle-safety-harness.md) — per-call verification routing inside a single turn.
- [Unbounded Consumption: Bounding Agent Resource Use Against DoS and Denial-of-Wallet](unbounded-consumption-resource-bounds.md) — the availability bounds this pattern makes load-bearing.
