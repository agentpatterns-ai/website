---
title: "Experience Rot After Silent Tool Changes in AI Agents"
term: "Experience Rot"
description: "Agents that reuse earlier tool calls copy them after a silent tool change. Out-of-date experience scored 0.23 against 0.63 with none, under three conditions."
tags:
  - anti-pattern
  - agent-design
  - context-engineering
  - tool-agnostic
  - arxiv
aliases:
  - stale experience reuse
  - silent tool change failure
last_reviewed: 2026-11-19
maturity: emerging
---

# Experience Rot After Silent Tool Changes in AI Agents

> Agents that reuse earlier tool calls copy them after a silent tool change, and out-of-date experience scored below no experience.

Experience rot is an agent repeating an earlier successful tool call after the tool changed. The study that names it needs three conditions ([Xu et al., 2026](https://arxiv.org/abs/2611.20922v1)): the service accepts a stale call with the same response as a valid one (§3.1), the agent does not read back the stored state, and the documentation gives a range but not a meaning. Under them, final-task success was 0.63 with no experience, 1.00 with valid experience, and 0.23 with out-of-date experience (Table 16; six models, 12 task instances per change, direction, and arm, Appendix I). The incomplete-documentation arms were not preregistered; the services are synthetic (§3.3).

## Why it fails

Experienced agents stop checking. Lookups before the first write fell to 6% of runs or fewer (§1). In 135 of 144 earlier tasks with a renamed field or changed structure the agent made no lookup, and 61% of those runs repeated the old field (§5). The paper does not establish why (Appendix A).

Complete documentation did not rescue it: success was 26-49% against 88-100% with no experience (§4). Failed runs reported success in 347 of 348 cases with complete documentation and 92% with incomplete (§4). Every memory form paid, at 0.53 in the conversation and 0.20-0.30 in memory files, retrieval, and skills (§6).

## Remedies, ranked

Success with out-of-date experience (Figure 5, §7). Task-message and stored-object rows ran separately, where nothing added scored 0.45.

| Added to the final task | Complete docs | Incomplete docs |
|-------------------------|---------------|-----------------|
| Nothing | 0.46 | 0.23 |
| Version number and update notice | 0.50 | |
| Read-docs instruction, system prompt | 0.29 | |
| Read-docs instruction, task message | 0.99 | 0.25 |
| Check after writing | 0.91 (system prompt) | 0.69 (task message) |
| Write returns the stored object | 0.79 | |

Checking took 6.5 and 10.6 calls per task, against 2.9 and 3.1 with valid experience.

## When this backfires

- Qwen3.8-Flash "reads back after every write and corrects its errors". With complete documentation it scored 1.00 with out-of-date experience, the same as with none (Appendix G.4, Table 8). With incomplete documentation it scored 0.93 against 1.00 (Appendix I, Table 18).
- Forcing a docs lookup raised calls from 2.92 to 3.55 per task when nothing changed (Appendix I).
- A strict server may remove the failure. The paper did not test rejecting unknown fields (Appendix A).
- Reflection, planning, and memory modules reduced the drop under tool evolution for GPT-5.4 ([Liu et al., 2026](https://arxiv.org/abs/2607.14642v1)).

## What to do

After every state-changing call, have the harness fetch and compare the stored state, or have the write tool return the stored object, before the agent may report completion. Budget more than twice the calls. If you own the tool, put value meanings in the definition: changes it showed were copied less often than changes only the documentation described (69% against 99%, Appendix A).

## Example

The paper's earlier request states the meaning; the final request does not (§3.2):

```
(For this service, priority 4 is the highest and 1 is the lowest.)
```

In the out-of-date arm the agent gained its experience on the other version, so that stated meaning is the reverse of the running one. The service accepts the old usage with the same response as a correct request (§3.1), and the agent has no reason to look again.

## Key Takeaways

- Read back stored state after writes. Version labels and update notices did almost nothing.
- Test a memory feature with the agent's own experience. Hand-written histories that include a check step measure about a fifth of the cost, 0.11 against 0.54 (§8).
- The result covers six models in synthetic services. Test for it on your tools before treating it as a property of your agent.

## Related

- [Belief Inertia After Tool-Map Drift in AI Agents](belief-inertia-after-tool-map-drift.md)
- [Repository Skill Release Drift](repository-skill-release-drift.md)
- [Tool-Call Success as Workflow Effect Evidence](tool-call-success-as-workflow-evidence.md)
- [Budgeted Verification of Inherited Agent Constraints](../../context-engineering/budgeted-constraint-verification.md)
- [Fact Supersession Memory for Code Assistants](../../context-engineering/fact-supersession-memory.md)
- [Claim-Scoped Invalidation for Agent Memory](../../context-engineering/claim-scoped-invalidation.md)
- [Tool Description Quality](../../tool-engineering/tool-description-quality.md)
- [Truthful Error Notes for Compacted AI Agent Histories](../../context-engineering/truthful-error-notes-under-compaction.md)
