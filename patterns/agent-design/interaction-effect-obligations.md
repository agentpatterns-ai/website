---
title: "Binding an Agent's Effect to the Approval It Claims"
term: "Interaction-Effect Obligation"
description: "A per-call permission check passes on a send to the recipient a user just removed. Bind each effect to the task revision its approval named."
tags:
  - agent-design
  - security
  - tool-agnostic
  - arxiv
aliases:
  - interaction-effect obligation
  - endorsement binding
  - stale approval binding
last_reviewed: 2026-09-13
maturity: emerging
---

# Binding an Agent's Effect to the Approval It Claims

> A per-call permission check passes on a send to the recipient a user just removed, because no component can see the approval's task revision.

An interaction-effect obligation is a record attached to an agent-initiated effect that names what authorized it. Yu, Fang and Chen define it as "the relation Ψₑ=⟨κ,r,βₑ,γₑ,ℓₑ,ϵₑ⟩, linking the task and revision to reviewed payload/object bindings βₑ, role-specific authority γₑ, controller identity and epoch ℓₑ, and available outcome evidence ϵₑ" ([arXiv:2609.11381v1](https://arxiv.org/abs/2609.11381v1)). Written down, it gives the release path something to compare against the task record. Nothing else in the call carries that.

## Where the per-call check runs out

Two authorization layers sit above this failure and neither catches it. Capability gating decides which tools are exposed. An audit of LangChain/LangGraph, LlamaIndex and the Stripe Agent Toolkit found that "all three provide capability gating by default, but none provides a deterministic fail-closed per-call value authorization gate by default" ([arXiv:2606.28679v1](https://arxiv.org/abs/2606.28679v1)). That second gate is right, and it still does not cover this case.

A user endorses sending a document to recipients a and b. Before the agent reaches the send, a GUI revision removes b. "A send operation for b can still satisfy its API schema and the caller's ordinary resource permission" ([arXiv:2609.11381v1](https://arxiv.org/abs/2609.11381v1)). Schema valid, permission valid, arguments exactly the ones a human approved. The one fact that changed is one no component can read.

The paper states it as Proposition 2.3: "Valid component calls and authenticated permissions are insufficient to establish [interaction conformance] under a contract requiring current endorsement bindings when task-relevant state can change before effect admission" ([arXiv:2609.11381v1](https://arxiv.org/abs/2609.11381v1)).

## What the effect carries

| Field | What it pins |
|---|---|
| Task identity and revision | Which task, and which revision of it the human endorsed |
| Reviewed bindings | The concrete objects and payload the endorsement covered |
| Role-specific authority | Which role's authority the effect relies on |
| Controller identity and epoch | Who held the task, and under which lease |
| Outcome evidence | What the effect must return to count as done |

The fields are the components of Ψₑ, glossed ([arXiv:2609.11381v1](https://arxiv.org/abs/2609.11381v1)). Row one does the work.

## Why it works

The component check and the contract check read different state. A tool call carries its arguments and its caller's permissions, and nothing about the task. It cannot ask whether the endorsement behind those arguments still refers to the current revision. Attaching the obligation moves that state to where the effect is released. A revision counter then turns staleness into an equality test instead of a re-derivation of intent: "Material revision increments r and invalidates prior task endorsements" ([arXiv:2609.11381v1](https://arxiv.org/abs/2609.11381v1)). Two clauses of the worked disclosure contract are worth copying ahead of the formalism. Endorsements get recorded "through a non-delegated channel", so the agent cannot forge its own approval, and each one expires "no later than ten minutes after recording" ([arXiv:2609.11381v1](https://arxiv.org/abs/2609.11381v1)).

## When this backfires

- Nothing has been built. The authors say the work "does not claim an implemented runtime, demonstrated productivity gains, or cross-domain validation" ([arXiv:2609.11381v1](https://arxiv.org/abs/2609.11381v1)). You would be implementing a definition.
- This is time-of-check to time-of-use, and countermeasures in the class measure badly. On TOCTOU-Bench's 66 tasks, three combined countermeasures moved vulnerabilities in executed trajectories from 12% to 8%, and automated detection topped out at 25% accuracy ([Lilienthal and Hong, arXiv:2508.17155v1](https://arxiv.org/abs/2508.17155v1)).
- Invalidation manufactures prompts. Every material revision voids the endorsement, so a user who keeps editing re-endorses repeatedly. Claude Code users approve 93% of permission prompts, and Anthropic names the result: "Over time that leads to approval fatigue, where people stop paying close attention to what they're approving" ([auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)). A ten-minute endorsement lifetime against an hour-long task makes that reflex certain.
- The commit point has to do the checking. Validate in your process, commit in someone else's, and the race stays open. Against a third-party API with no conditional write, you get an audit trail rather than a guarantee.
- Clauses drift away from code. Across 21 projects and more than 7,700 revisions, "contracts are quite stable compared to implementations" ([Estler, Furia, Nordio, Piccioni and Meyer, arXiv:1211.4775v6](https://arxiv.org/abs/1211.4775v6)). Hand-written binding clauses age the same way while the admission code moves under them.

Replanning is the competitor to beat. Discard the endorsement, re-decide from current state, and record nothing that can go stale. Where pending effects are rare and a model call is cheap, it wins on everything but the audit trail.

## Key Takeaways

- Per-call value authorization on the exact approved arguments still admits an effect whose approval has expired. That is a proposition with a counter-example, not a measurement.
- The cheap half of the pattern is a revision counter on the task plus an equality test before release. Skip the formalism and keep that.
- Record endorsements on a channel the agent cannot drive, or the obligation records the agent's own say-so.
- Validation without a conditional write at the target narrows the window and does not close it.
- Budget for the prompts. An endorsement that dies on every edit is one a user learns to click through.

## Related

- [Deterministic Precondition Gates for Tool-Using Agents](deterministic-precondition-gates.md) — the same write-path check, evaluated against live state rather than against a recorded human endorsement
- [Capability Declarations for Agents That Act on Data](capability-declarations-for-agent-actions.md) — the per-action metadata this obligation gets compared against
- [Approval Gate Granularity in Agent Pipelines](approval-gate-granularity.md) — where the pause that opens the stale-endorsement window comes from, and what re-prompting costs
- [Trusting Claimed Prior Approval in Agent Review Gates](../anti-patterns/trusting-claimed-prior-approval.md) — the fabricated-approval failure, which a non-delegated endorsement channel also closes
- [The Post-Authorization Execution Trust Gap in Remote MCP](../../security/post-authorization-execution-trust-gap.md) — the same interval measured against the workload that executes rather than the human who approved
