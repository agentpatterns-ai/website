---
title: "Outcome Monitors: Recovery Affordances for Tool Failures"
term: "Outcome Monitor"
description: "A silent tool failure raises no error. An advisory receipt naming the broken property and the substitute tools the agent can call is what recovers the run."
tags:
  - agent-design
  - tool-agnostic
  - testing-verification
  - arxiv
  - reliability
aliases:
  - outcome contracts
  - recovery affordances
  - recovery-tool receipt
  - silent tool failure monitor
last_reviewed: 2026-08-23
maturity: emerging
---

# Outcome Monitors: Recovery Affordances for Tool Failures

> An outcome monitor flags a well-formed but wrong tool result and hands the agent the substitute tools it can call instead.

An outcome monitor wraps a tool call, checks the result against a contract mined from clean traces or derived from a public schema, and on a violation appends an advisory receipt naming the broken property and the public tools the agent can reach for. It never blocks the call, repairs the result, or hides it. In a frozen, prespecified ToolMaze evaluation with injected failures, completion rose from 10.9% to 28.1% (35/320 to 90/320) across four models in two provider families ([Panthi and Abdelfattah, arxiv:2608.19303v1](https://arxiv.org/abs/2608.19303v1)).

## Three conditions decide whether this pays

The headline number came from a benchmark built to make silent faults block completion. Outside that regime the same intervention measures at zero or worse, so check all three before building anything.

- Silent faults are blocking your agent today. Gains concentrate where a fault stops the baseline from finishing. The τ-bench conservation tier showed no net effect, and a held-out 32-family study on DeepSeek V4 Flash had "baseline and advisory each complete 25/32 families (p=1.0)" ([2608.19303v1](https://arxiv.org/abs/2608.19303v1)). On task distributions where the agent already succeeds, critic-model intervention has been measured at 0 to −26 points ([Vasudev et al., arxiv:2602.03338v1](https://arxiv.org/abs/2602.03338v1)).
- The violation shows up in a value, not in prose. Learned contracts reached 83% recall on structured violations against 22% on corruption hidden inside plausible strings, and on faults authored blind to the contract vocabulary "detection falls to ≈46%" ([2608.19303v1](https://arxiv.org/abs/2608.19303v1)). A fabricated summary field passes every numeric and categorical check.
- A substitute tool exists to name. The recovery-tool list is the receipt content the ablation credits with the gain ([2608.19303v1](https://arxiv.org/abs/2608.19303v1)), so on a tool surface where every capability is singular the receipt has nothing to point at.

## The receipt is the product

An outcome contract captures "expected relationships between tool calls and their results, mined from nominal executions or derived from public schemas" across invariant classes that "include per-field type constraints, echo fields (a[f]=y[f]), positivity (y[f]>0), categorical domains, affine relations, and temporal orderings" ([2608.19303v1](https://arxiv.org/abs/2608.19303v1)).

What the monitor emits on a violation matters more than how it detected one. Five matched contrasts varied a single part of the receipt over the same 114 workflow pairs:

| Receipt variant | Measured effect |
|---|---|
| Recovery-tool list restored | +11.4 points (p=.028) |
| Recovery-tool list stripped | Performs at baseline |
| Localized rather than generic witness detail | No detectable difference |
| Deferred rather than immediate timing | No detectable difference |
| Always-warn rather than detector-gated | Confounded, because it supplies recovery tools at every step |

Both nulls are power-bounded at roughly 18 points of minimum detectable effect, so read them as "not shown to matter here" rather than proven inert ([2608.19303v1](https://arxiv.org/abs/2608.19303v1)).

## Why it works

The binding constraint on recovery is affordance, not diagnosis. A cached error page or a negative price arrives in the expected format, so nothing surfaces as an error and the agent has no failure to route around. Once told what broke, it still cannot derive which other public tool covers the same need, because that mapping lives in the tool surface and never appears in the trajectory. The receipt supplies exactly that missing half, which is why stripping the tool list drops the whole effect while varying the explanation changes nothing ([2608.19303v1](https://arxiv.org/abs/2608.19303v1)).

Independent work points the same way. A binary critic with 0.94 AUROC still collapsed one model by 26 points while leaving another near zero, and the authors conclude that critic accuracy alone cannot tell you whether intervening is safe ([2602.03338v1](https://arxiv.org/abs/2602.03338v1)).

## When this backfires

- Clean traffic pays for the warnings. Advisory and baseline each completed 74 of 114 clean pairs, and the monitor emitted 16 false-trigger receipts across 14 treated pairs, producing five paired rescues and five paired harms ([2608.19303v1](https://arxiv.org/abs/2608.19303v1)). Advisory framing bounds that harm without removing it, because an agent can still overreact to a correct signal about an irrelevant field.
- The mining half may not earn its keep. A schema-only detector recovered +10.0 points on its own, and its head-to-head gap against the learned registry was +5.0 points, not distinguishable from noise (p=.42). What the learned registry bought was selectivity: 111 receipts instead of 166, with 91.9% of events listing multiple recovery actions against 12.0% ([2608.19303v1](https://arxiv.org/abs/2608.19303v1)). Start from published schemas and add mining only if the firing rate is the problem.
- A thin or skewed trace corpus gives you a registry that fires on healthy calls. Acceptance in the paper is deliberately strict: "An invariant must hold on every training sample and meet its class-specific support minimum," and the detector audit is scoped tightly: "A task-disjoint audit of the detector on the experiments' difficult C3/C4 workflow classes flags 79.6% of implicit faults at a 1.39% clean false-positive rate, with a learned contract available for 94.2% of fault outcomes; rates are per observed tool outcome, not per episode" ([2608.19303v1](https://arxiv.org/abs/2608.19303v1)). Five-fold cross-fitting then keeps every evaluated workflow out of the traces that built its registry. Relax either discipline and the false-positive rate you inherit is not the one that was measured.
- Nothing here ran against live deployment. "No episode here runs against a live deployment," and the experiments vary placement and prevalence rather than fault content ([2608.19303v1](https://arxiv.org/abs/2608.19303v1)). Read the point estimates as evidence about a mechanism, not a forecast for your traffic.

## Example

Measure the firing rate before you wire a monitor into a live loop. The authors replayed 53,078 recorded StableToolBench responses from 427 public tools with no agent and no counterfactual; the unchanged detector fired on 0.80% of them, concentrated in 54 tools ([2608.19303v1](https://arxiv.org/abs/2608.19303v1)). Run that replay over your own logged tool responses. A rate near zero means your silent-fault surface is too small to recover anything, and a rate concentrated in a few tools tells you which contracts to write first.

## Key Takeaways

- A failure signal without an affordance buys nothing. Ship the substitute-tool list before you invest in better explanations of the fault.
- Check the fault mix first. Structured violations were caught at 83% recall; corruption inside strings at 22%.
- Derive contracts from published schemas before mining them from traces. The cheaper detector was not statistically distinguishable on completion.
- Estimate the false-trigger cost on clean traffic. Five rescues and five harms is the reported balance when no fault is present.

## Related

- [Retry-Switch-Abstain: A Runtime Tool-Recovery Policy](retry-switch-abstain-recovery-policy.md) — supplies a fallback map for failures the agent can already see, and lost ground on silent corruption that this pattern is built to surface
- [Observation Contract Preservation in Tool-Augmented Agents](observation-contract-preservation.md) — the other silent-failure class, where the agent corrupts a contract-bound output rather than consuming a corrupted one
- [Exception Handling and Recovery Patterns](exception-handling-recovery-patterns.md) — the broader escalation hierarchy a monitor's receipt feeds into
- [Informed Abstention as a Tool-Boundary Runtime Gate](informed-abstention-tool-boundary-gate.md) — the pre-execution gate, where this pattern checks the result after the call returns
- [Agent Circuit Breaker](agent-circuit-breaker.md) — the blocking response to a degraded tool, against this pattern's advisory one
