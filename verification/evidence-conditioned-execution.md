---
title: "Evidence-Conditioned Execution: Gate Edits on Observations"
term: "Evidence-Conditioned Execution"
description: "Hold a coding agent's edit until its trajectory shows the repository observations that edit depends on, tracked as machine-checked conditions rather than prose advice."
tags:
  - testing-verification
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - "evidence-conditioned execution layer"
  - "premature commitment gating"
  - "pre-edit evidence conditions"
last_reviewed: 2026-08-03
maturity: emerging
---

# Evidence-Conditioned Execution: Gate Edits on Observations

> Hold an agent's edit until its trajectory shows the repository observations that edit depends on, tracked as machine-checked conditions.

Evidence-conditioned execution interposes a layer between a coding agent and the repository. Per task, the layer compiles conditions describing what the agent should observe before each type of code modification or patch submission, tracks which the runtime trajectory has satisfied, and postpones any proposed action whose conditions remain unmet. A named implementation is ECLoop, which raised Pass@1 by 4.8 to 11.8 percentage points across two models and two agent scaffolds on all 500 instances of SWE-bench Verified, with no retraining and no scaffold change ([arxiv:2607.28815v1](https://arxiv.org/abs/2607.28815v1)). It gates the edit itself, which places it upstream of every gate that inspects work the agent has already produced.

## When this earns its cost

The effect is statistically strong and also bounded. Check these conditions before building the layer.

- Your models sit below the frontier. The weaker model gained 10.4 and 11.8 points across two scaffolds; the stronger one gained 5.0 and 4.8, with token savings of 12.1% at the weakest pairing and 1.4% at the strongest ([arxiv:2607.28815v1](https://arxiv.org/abs/2607.28815v1)).
- Your issues describe the problem well. The specification is compiled from the issue text plus repository structure, so its completeness is bounded by how well the issue characterizes the underlying problem. Conditions that resolve to no concrete repository entity are dropped outright ([arxiv:2607.28815v1](https://arxiv.org/abs/2607.28815v1)). A tracker of one-line bug reports yields a thin gate.
- The work is bug fixing against an existing codebase. The authors state the evaluation does not cover other languages, task types such as feature addition, or benchmarks beyond SWE-bench ([arxiv:2607.28815v1](https://arxiv.org/abs/2607.28815v1)).
- You can express the conditions as tracked state. The same expectations written into the prompt as prose lose most of the benefit, as the [example](#example) prices.

## How it works

Before execution, the system analyzes the issue and the repository to build the conditions a commitment action must satisfy. Each condition is a tuple of the action type it guards, the concrete program entity it names, the event pattern required, and a satisfaction predicate over the trajectory so far. Entity resolution uses AST traversal, call graphs, and class hierarchies ([arxiv:2607.28815v1](https://arxiv.org/abs/2607.28815v1)).

Three operations then run during execution:

1. Guidance converts the remaining global evidence gap into text added to the model's context, so the agent sees what investigation is outstanding.
2. Commitment gating derives an action-specific gap when the agent proposes an edit or a submission, holding only the unsatisfied conditions that apply to that action. The action is postponed while that gap is nonempty.
3. State update refreshes the trajectory and the evidence state after each executed action, so the gate reads live state instead of a static instruction.

All three carry measurable weight. Removing any one costs solved instances on the paper's ablation subset, priced in the [example](#example) below ([arxiv:2607.28815v1](https://arxiv.org/abs/2607.28815v1)).

## Why it works

Agents carry a measurable bias toward acting. On FixedBench, 200 human-verified tasks requiring no code change, five recent models across four agent harnesses proposed undesirable changes in 35 to 65% of cases, which the authors name an action bias ([arxiv:2605.07769v1](https://arxiv.org/abs/2605.07769v1)). A gate acts on that bias by removing the option to act: the action-specific gap is a predicate over recorded trajectory events, so the agent does not re-decide each turn whether it has looked hard enough.

The structure of the conditions carries much of the effect. Replacing the specification with an equivalent natural-language summary costs as much as removing the commitment check entirely ([arxiv:2607.28815v1](https://arxiv.org/abs/2607.28815v1)). The ablation establishes the outcome, not the mechanism: tracked conditions outperform the same expectations written as prose.

What improves is less settled than the headline number suggests. The closest controlled study of a comparable intervention found the gain landed on coverage: better repository guidance produced evaluable patches for 14.5 percentage points more instances while per-patch precision stayed statistically constant at roughly 59% ([arxiv:2606.20512v2](https://arxiv.org/abs/2606.20512v2)). That result comes from a different system, and ECLoop reports no measurement separating the two, so the same reading stays open here: the conditions may improve where the agent looks and when it stops looking without improving the edit it then writes.

## When this backfires

- The gate holds work it should release. In the documented regression path the agent keeps proposing an action the gate holds and exhausts the hold limit of three. The fallback release then permits an under-supported action and an incorrect patch. ECLoop newly resolved 33 and 68 previously-failing instances per model while regressing 9 successes in each case ([arxiv:2607.28815v1](https://arxiv.org/abs/2607.28815v1)).
- Forcing evidence trades one bias for another. Instructing agents to reproduce the issue before patching partially fixed over-editing and then produced a new failure: on partially-fixed issues the agents abstained even though a patch was still needed ([arxiv:2605.07769v1](https://arxiv.org/abs/2605.07769v1)).
- Strictness carries a false-positive price. An adjacent pre-action authorization layer blocked 0 of 50 legitimate actions under its default configuration and 18 of 50 under maximum security, at roughly 1.9 seconds of added latency per action ([arxiv:2604.12986v1](https://arxiv.org/abs/2604.12986v1)).
- The gate is the agent grading itself. Specification, gap assessment, and guidance all come from the same model that drives the agent, so a blind spot it has at action-selection time it may also have when assessing evidence sufficiency ([arxiv:2607.28815v1](https://arxiv.org/abs/2607.28815v1)).
- The numbers rest on a single benchmark. A mutation-based re-evaluation reports that existing benchmarks overestimate agent capabilities by more than 50% over baseline for public benchmarks, against roughly 10 to 16% on an internal one ([arxiv:2510.08996v2](https://arxiv.org/abs/2510.08996v2)). Treat 4.8 to 11.8 points as an upper bound on what transfers.

Post-hoc revision does not substitute for the gate. Self-Refine, the study's revision comparison, degraded Pass@1 by 1.4 and 1.8 points ([arxiv:2607.28815v1](https://arxiv.org/abs/2607.28815v1)).

## Example

The ablation prices each operation separately on the same 100-instance subset. Every variant runs GPT-5-mini in mini-swe-agent v2 with the same prompt and tools, and only the execution layer changes ([arxiv:2607.28815v1](https://arxiv.org/abs/2607.28815v1)).

| Variant | Instances solved |
|---|---|
| Full specification, all three operations | 68 |
| Without guidance | 63 |
| Without state update | 59 |
| Without the commitment check | 58 |
| Specification replaced by a natural-language summary | 58 |
| Baseline agent, no layer | 47 |

The last two rows are the ones to act on. Writing the expectations as prose costs exactly what deleting the commitment check costs, so a team that ships this as an `AGENTS.md` paragraph has built the 58-instance variant rather than the 68-instance one.

## Key Takeaways

- Condition the edit on recorded trajectory events, so the agent gets no turn in which to relitigate the check. ECLoop's gains came at no additional inference cost and lowered average token consumption by up to 12.1% ([arxiv:2607.28815v1](https://arxiv.org/abs/2607.28815v1)).
- Price the layer against your weakest model. The measured benefit roughly halves between the two models tested, and the token saving nearly vanishes on the stronger one ([arxiv:2607.28815v1](https://arxiv.org/abs/2607.28815v1)).
- If you build one part, build the machine-checked condition list. Prose in an instructions file bought about as much as having no commitment check at all.
- Set a hold limit and decide what happens when it expires. The fallback release is where the paper's 9 regressions per model come from ([arxiv:2607.28815v1](https://arxiv.org/abs/2607.28815v1)).
- Pair the gate with a verifier the driving model did not write. It catches process failures rather than reasoning failures, because the agent's own model produced the conditions it is being held to.

## Related

- [Evidence-Gated Lifecycle Control for Coding Agents (Proof-or-Stop)](evidence-gated-lifecycle-control.md) — gates state advancement on verified receipts, downstream of where this pattern fires.
- [Staged Evidence Gates for Agentic Program Repair](staged-evidence-gates-program-repair.md) — orders cheap gates ahead of expensive ones over candidate patches that already exist.
- [State-Bound Evidence and Typed Revision Contracts for Repair Loops](state-bound-repair-evidence.md) — binds each test result to the code state that produced it so revision cannot discard a correct patch.
- [Pre-Change Impact Analysis: Dependency Maps That Prevent Agent Regressions](pre-change-impact-analysis.md) — supplies the code-to-test dependency evidence an edit-time gate can condition on.
- [Deterministic Guardrails Around Probabilistic Agents](deterministic-guardrails.md) — the hard, deterministic checks a gate's satisfaction predicates are built from.
