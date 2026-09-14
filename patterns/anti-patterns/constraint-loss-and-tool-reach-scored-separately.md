---
title: "Scoring Constraint Loss and Tool Reach as Separate Risks"
term: "Separate-Risk Boundary Scoring"
description: "A dropped constraint scores 0% loss of control on its own and a reachable unsafe action 9.33%, but together they reach 55%, so score the pair."
aliases:
  - independent risk scoring for agent boundaries
  - scoring constraint degradation and unsafe opportunity separately
  - constraint loss and tool reach
tags:
  - anti-pattern
  - context-engineering
  - agent-design
  - security
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-11
maturity: emerging
---

# Scoring Constraint Loss and Tool Reach as Separate Risks

> A dropped constraint and a reachable unsafe action each score low alone; loss of control lives in their conjunction.

Agent safety reviews ask two questions on two rows. Does compaction keep the operating rules? Which unauthorized actions can this agent execute? Both can come back clear while the failure ships, because the risk sits in the interaction rather than in either column.

Read the conditions before the numbers. Every figure below comes from a deterministic simulator with no real tools or downstream safeguards. Environment fidelity systematically shapes reported safety, and a survey of safety benchmarks found no evidence of ranking concordance across evaluation dimensions (W = 0.10, p = 0.94) ([Taxonomy and Consistency Analysis of Safety Benchmarks for AI Agents, arXiv:2605.16282v1](https://arxiv.org/abs/2605.16282v1)). Take the direction, not the forecast.

## The anti-pattern

A full-factorial study crossed constraint degradation with unsafe opportunity over five models and six operational domains, pooling 300 trajectories per cell ([Table 2, arXiv:2609.11024v1](https://arxiv.org/abs/2609.11024v1)):

| Constraints | Unsafe action reachable | Loss of control |
|---|---|---|
| Intact | No | 0% |
| Intact | Yes | 9.33% |
| Degraded | No | 0% |
| Degraded | Yes | 55.00% |

Scored apart, constraint degradation carries +22.8 pp and unsafe opportunity +32.2 pp. Their difference-in-differences is +45.7 pp, larger than either main effect ([Table 3, arXiv:2609.11024v1](https://arxiv.org/abs/2609.11024v1)), so a review that adds the two single-factor row scores, 0% and 9.33%, lands 45.7 points low. Goal pressure moved the pooled marginal rate by +3.2 pp, and inside the decisive cell it pushed one of the five models downward ([Table 4, arXiv:2609.11024v1](https://arxiv.org/abs/2609.11024v1)).

## Why it works

Progress summarizes in positive terms: what was done, what remains, what advances the task. Operational constraints are negative. They say what must not happen, when to stop, and whose approval is required, so a summary stays coherent while dropping them, and the agent keeps its goal while losing its limit ([§5.1, arXiv:2609.11024v1](https://arxiv.org/abs/2609.11024v1)). That asymmetry makes the two factors complementary. A lost constraint removes the information needed to respect the boundary, but produces no external effect while nothing can cross it. A reachable unsafe action stays contained while the rule is visible.

Compaction itself is not the mechanism. Over four domains, compaction that preserved the authorization boundary held loss of control at 0%, matching the full uncompacted context; omitting the same boundary reached 87% ([Table 9, arXiv:2609.11024v1](https://arxiv.org/abs/2609.11024v1)).

## When this backfires

- The capability can be withdrawn outright. With no executable boundary-crossing action, loss of control was 0% in every cell whatever the constraint state. Revoke the credential and joint scoring buys you nothing.
- Nothing compacts. Constraint degradation here means compaction that omits negative constraints, so a short-horizon agent whose history fits in context has no degradation channel to score.
- The intact-constraint row gets treated as a zero. The same paper reports 9.33% with the boundary intact and the unsafe action reachable, against 0% in its ten-domain counterfactual ([Tables 2 and 8, arXiv:2609.11024v1](https://arxiv.org/abs/2609.11024v1)). The floor is domain-dependent.

## Example

**Before — each factor cleared on its own row:**

```text
compaction review: summary keeps the recovery goal and the rollback target -> pass
tool review:       rollback action reachable, operator policy gates it     -> pass
```

**After — the pair scored as one row:**

```text
compaction review: summary drops "wait for the release owner's approval" -> constraint degraded
tool review:       rollback action reachable in the same window          -> opportunity present
joint row:         degraded AND reachable -> block until the approval requirement
                   survives into the compacted context
```

That is the paper's production-rollback case: 100% loss of control under constraint-omitted compaction, 0% when the same compaction kept the approval requirement ([Table 10, arXiv:2609.11024v1](https://arxiv.org/abs/2609.11024v1)).

## Key Takeaways

- Score constraint retention and executable reach on one row, in the same review window, for the same trajectory segment.
- Re-score the pair whenever the tool surface changes, not only when context handling changes. A rule dropped last month turns into a violation the day a new tool ships, and no context event fires to prompt the review.
- Goal pressure is the cheap column to cut: +3.2 pp, and not even uniform in direction across models.

## Related

- [Per-Type Retention Policy for Agent Compaction](../../context-engineering/per-type-retention-under-compaction.md) — how to keep the constraint half of the pair intact.
- [Objective Drift](objective-drift.md) — the mirror case, where compression loses the goal instead of the limit.
- [Task-Uniform Agent Permissions](task-uniform-agent-permissions.md) — the reach half, scoped per task rather than per agent.
- [Constraint Drift](../../security/constraint-drift-multi-agent-safety.md) — six runtime surfaces where constraints weaken.
