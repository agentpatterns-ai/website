---
title: "Plan-Stage Checkpoints in Agent Code Repair"
term: "Plan-Stage Checkpoint"
description: "A planted wrong mechanism failed 1.5 to 2.4 times as often from a repair agent's implementation plan as from its hypothesis, so place a single checkpoint after the plan and have it name the obligations at risk."
tags:
  - testing-verification
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - plan-stage review
  - plan-to-code checkpoint
  - plan-stage repair gate
last_reviewed: 2026-10-18
maturity: emerging
---

# Plan-Stage Checkpoints in Agent Code Repair

> Repair attempts failed 1.5 to 2.4 times as often when the same wrong idea reached the implementation plan rather than only the hypothesis.

If a repair pipeline affords one review checkpoint, put it between the plan and the code. A controlled study planted defined but incorrect software mechanisms at chosen points in a repair agent's chain and measured what each position cost. A wrong idea sat more cheaply in the explanation.

## Four conditions before you act on this

The evidence sets the placement. It does not yet establish that a checkpoint there works.

1. The misconceptions were planted, not observed. Researchers wrote plausible but wrong accounts of the software and inserted them into the agent's hypothesis, its plan, or both ([arXiv:2610.21514v1](https://arxiv.org/abs/2610.21514v1)). Nothing here measures how often an agent reaches such a commitment unaided.
2. Two synthetic Python cases carry the whole result: atomic batch claiming on a disk-backed SQLite queue, and a source-keyed filter on NetworkX 3.6 multi-source Dijkstra. Neither is a recovered historical bug, and the authors say so: "The repeated direction across the two tasks supports the experimental method; it does not establish a universal effect size."
3. The remedy is untested. The study locates the expensive stage and stops: "Whether those checks improve a second repair remains untested." Build the checkpoint as a hypothesis you measure.
4. Model configuration moves the effect a long way. The plan-versus-hypothesis difference ranged from −3.8% to +45.1% across model and reasoning-effort settings in the queue task, and from +6.6% to +39.1% in Dijkstra.

## What the measurement found

Across 1,844 model requests, moving the wrong mechanism from the hypothesis into the plan raised raw failure from 21.9% to 54.7% in the queue task and from 53.4% to 83.0% in the Dijkstra task. The two conditions did not hold the same mix of families, models, and dependency settings, so the authors also compared only the combinations present in both and weighted them equally. That gave +32.2% [27.0%, 38.8%] and +28.9% [21.1%, 38.6%]: "after balancing the experimental mix, plan-only attempts failed about 2.4 and 1.5 times as often" ([arXiv:2610.21514v1](https://arxiv.org/abs/2610.21514v1)).

Adding a matching hypothesis on top of an already-poisoned plan bought little: 6.3% [0.5%, 12.2%] in the queue task and 2.2% [−4.9%, 8.5%] in Dijkstra, where the interval spans zero.

## What the review has to name

A generic "does this plan look reasonable?" pass has no target. The authors list four things a reviewer can check: whether "the plan assigns state to the right owner, preserves rollback and isolation, carries forward information needed later in execution, and retains the existing API contract" ([arXiv:2610.21514v1](https://arxiv.org/abs/2610.21514v1)).

Which obligation breaks is partly predictable from the misconception. The association between planted mechanism and failed obligation scored 0.475 [0.453, 0.556] on Cramér's V in the queue task and 0.314 [0.307, 0.434] in Dijkstra, which the authors read as structured without being one-to-one: "one family could still produce several failure patterns and different families could converge on the same violated obligation". A plan that compensates for transaction state in memory therefore points a reviewer at cross-connection isolation first, not at rollback alone.

## Why it works

A hypothesis is a claim the model can still discard. A plan is not. "A plan commits the repair to operations, owners of state, update order, error handling, and compatibility choices. When those commitments are wrong, they can pass directly into code" ([arXiv:2610.21514v1](https://arxiv.org/abs/2610.21514v1)). Writing the plan removes the freedom that kept a wrong explanation harmless, which is why the same idea costs more there. The authors do not call planning the problem: a plan "is a high-leverage boundary where a repair system should check whether the proposed operations preserve the software contract."

A second study weighs the plan heavily on a different comparison. Measuring plan compliance across 21,120 SWE-agent trajectories, it reports that "A subpar plan hurts performance even more than no plan at all" ([arXiv:2604.12147v3](https://arxiv.org/abs/2604.12147v3)). That contrast is a bad plan against no plan, not against a bad hypothesis, so it corroborates the plan's weight rather than replicating the stage result.

## Example

In the queue task, poison family A02 took this form. Its hypothesis read: "Restoring each claimed row to ready after failure is equivalent to atomic rollback." Its plan read: "Collect staged row IDs; after a SQLite error, write each status back to ready and then re-raise" ([arXiv:2610.21514v1](https://arxiv.org/abs/2610.21514v1)).

Both sentences describe recovery that a reviewer might wave through. The plan is the one that fails, because writing statuses back one at a time is not one rollback unit, and another database connection can see the intermediate state. Of 25 code-bearing plan-only attempts under A02, 8% passed every selected diagnostic axis and 92% failed on isolation alone. The paper describes the shape directly: "behavior could look correct through one connection while another observed the wrong queue state."

## When this backfires

- The agent does not follow the plan you approved. The compliance study opens by saying "it is unknown to what extent agents actually follow instructed plans" ([arXiv:2604.12147v3](https://arxiv.org/abs/2604.12147v3)), and the primary study notes that generated code "may copy, transform, compensate for, or ignore the supplied mechanism". An approved plan is weak evidence about the patch, so keep the executable checks that already run after the code exists. See [plan compliance in agents](../patterns/agent-design/plan-compliance-in-agents.md).
- Inserting the stage costs something. The same compliance study reports that "inserting additional task-relevant phases in the early stage can degrade performance, particularly when these phases do not align with the model's internal problem-solving strategy" ([arXiv:2604.12147v3](https://arxiv.org/abs/2604.12147v3)). A plan gate is such a phase.
- Nobody has written down the obligations. Rollback, isolation, record identity, route validity, weight correctness, and API compatibility were all specified in advance here. Without that contract the checkpoint has no acceptance criteria and degrades into [trust without verify](../patterns/anti-patterns/trust-without-verify.md).
- Your model configuration sits in the flat part of the range above. Measure the gate on the configuration you run rather than on the pooled average.

## Key Takeaways

- Place a single repair checkpoint after the plan and before the code. The same planted mechanism failed 1.5 to 2.4 times as often from the plan as from the hypothesis across 1,844 requests on two tasks.
- Give the reviewer a list, not a judgment call: state ownership, rollback, isolation, information the search needs later, and the existing API contract.
- Treat the gate as unvalidated. The study measures where a wrong commitment is expensive and leaves whether checking there helps as future work, so instrument it on your own model and tasks.
- Keep the post-code checks. A plan the reviewer approved can still produce code that ignores it.

## Related

- [Assumption Propagation: Compounding Agent Misunderstandings](../patterns/anti-patterns/assumption-propagation.md) — the failure this checkpoint is positioned against, with a five-level mitigation ladder
- [Plan Compliance in Agents](../patterns/agent-design/plan-compliance-in-agents.md) — why an approved plan does not guarantee the code that follows it
- [Five-Pass Blunder Hunt](five-pass-blunder-hunt.md) — how to run the critique once you have decided the plan is what gets critiqued
- [CausalFlow: Counterfactual Repair for Failed Agent Trajectories](causalflow-counterfactual-agent-repair.md) — the backward direction, working from a failure to the step responsible for it
- [The Plan-First Loop](../workflows/plan-first-loop.md) — the surrounding workflow that produces a plan worth checking
