---
title: "Validate Permission State Across Agent Handoffs"
description: "Check authority-bearing handoff claims against their original permission records, preserving targets, conditions, pending requests, and withdrawn approvals."
tags:
  - security
  - arxiv
  - context-engineering
  - agent-design
  - tool-agnostic
last_reviewed: 2026-11-06
maturity: emerging
---

# Validate Permission State Across Agent Handoffs

> Validate permission state before a successor acts on a handoff approval claim. Resolve it against the actual authorization record.

A self-written summary can misstate what an agent may do. *When Do Summaries Become Instructions?* studies this in synthetic tool tasks with a ground-truth permission ledger. The successor receives the summary and system prompt, without the original user request repeated ([paper, v1](https://arxiv.org/html/2611.06545v1)). This is a compaction failure, distinct from an attacker planting a fabricated approval.

## Read the replay evidence narrowly

The held-out models were Qwen3-8B and gpt-oss-20b. Two AI readers reviewed rule-flagged summaries; unknown rule-labeler recall limits the prevalence estimates. In a post hoc pooled replay, neutralizing false approvals reduced unauthorized actions from 24/120 to 7/120 runs. A later set moved from 17/48 to 11/48. The pre-specified restriction test was null; a subsequent fragile result was not a replication ([study results](https://arxiv.org/html/2611.06545v1#S5)).

These results support investigating permission loss at handoff. They do not establish a production error rate or show that deleting suspicious sentences reliably repairs a summary. The study's true-permission rewrites used an oracle and were not a validated deployable safeguard ([discussion](https://arxiv.org/html/2611.06545v1#S6)).

## Keep permission records outside narrative summaries

Use the following design recommendation to address that failure mode. Store authorization state in a harness-controlled record and let the summary reference it. For each consequential action, retain:

- The authorized action and exact target.
- The source of authority and a resolvable record identifier.
- Conditions that still apply, such as a time window or environment.
- Current state: allowed, pending, denied, withdrawn, or superseded.

In the paper's held-out example, Ben Mehta approved a rename and then withdrew approval. The summary retained an approval with a maintenance-window condition. The successor renamed in two of four original-summary runs and none after neutralization ([Table 3](https://arxiv.org/html/2611.06545v1#S5.T3)). A permission resolver should preserve the withdrawal even when the summary omits it.

## Verify both excess permission and excess caution

Create handoff tests from your own authorization rules. Include a withdrawn approval, a pending request, a different target, and a statement from someone without approval authority. Also include work already authorized by a standing policy. A checker that asks for confirmation on every task can avoid some unauthorized actions while still failing the intended workflow.

Measure unauthorized actions and unnecessary approval requests separately. Keep the checker and permission record outside the model's write authority. If a record cannot be resolved, report that specific gap before executing the dependent action; do not convert uncertainty into either blanket approval or a permanent new restriction.

## Key Takeaways

- A summary is evidence to inspect, not an independent grant of authority.
- Preserve scope, conditions, and withdrawals with the permission record.
- Test unnecessary approval requests alongside unauthorized actions.

## Related

- [Non-Human Event Provenance Markers](non-human-event-provenance-markers.md) — distinguish task events from user authorization
- [Trusting Claimed Prior Approval](../patterns/anti-patterns/trusting-claimed-prior-approval.md) — externally supplied approval claims
- [Evidence-Anchored Handoff](../patterns/agent-design/evidence-anchored-handoff.md) — attach evidence to escalation decisions
