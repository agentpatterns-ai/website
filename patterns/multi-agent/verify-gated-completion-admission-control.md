---
title: "Verify-Gated Completion as Admission Control"
description: "A read-only verifier decides whether an agent's completion claim is admitted; ambiguous cases fail closed and every decision is recorded."
term: "Verify-Gated Completion"
tags:
  - multi-agent
  - testing-verification
  - agent-design
  - tool-agnostic
  - arxiv
last_reviewed: 2026-06-02
maturity: emerging
---

# Verify-Gated Completion as Admission Control

> Verify-gated completion makes a read-only verifier — not the producer — the admission-control authority over every "done" claim: ambiguous cases fail closed, each decision packetized.

Learn it hands-on: [Verify-Gated Completion guided lesson with quizzes](https://learn.agentpatterns.ai/multi-agent/verify-gated-completion/).

Verify-gated completion is an architecture in which the agent that produced a result is not the one that decides the work is done. A separate, read-only verifier sits on the critical path of every completion claim. It admits or rejects the claim against deterministic checks, then writes the decision into a structured admission record ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)). It earns its cost only under the four conditions below.

## When this pattern applies

All four must hold:

- Verifier independent of producer: use a different model class, prompt context, and evidence sources. A verifier that shares the producer's training distribution admits the same hallucinations.
- Ground truth exists: tests, type checks, schema validation, CI exit codes — not another LLM's opinion.
- Verifier on the critical path: every claim routes through it. Sidecar advisory verifiers yield audit data, not admission control.
- Blocked precision measured: [Nguyen & Tran (2026)](https://arxiv.org/abs/2605.17998) report 98.58% rule agreement but only 0.39% blocked precision, so almost every rejection is a false positive. Without precision evidence, an enforcing gate blocks more valid work than invalid.

If any condition fails, prefer agent-internal verification ([pre-completion checklists](../../verification/pre-completion-checklists.md)) or recording without admission control ([verification ledger](../../verification/verification-ledger.md)).

## The three primitives

### Read-only verifier as completion authority

The verifier has no write capability over the work product. It inspects state, runs deterministic checks, and emits an admit or reject decision ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)). Read-only is structural: the verifier cannot patch or retry the output, so you cannot offload correctness onto it. This inverts the [evaluator-optimizer workflow](https://www.anthropic.com/engineering/building-effective-agents), which keeps refinement authority inside one agent; admission control externalizes it.

### Packetized admission records

Each decision is written as a structured record, not prose: task identifier, evidence references, verifier identity, decision, and timestamp. The records form a queryable audit surface. Every completion has a packet, and you can inspect ambiguous cases after the fact ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)). This is the INSERT-not-prose principle of the [verification ledger](../../verification/verification-ledger.md), raised to inter-agent boundaries.

### Fail-closed defaults

Ambiguous cases resolve to reject ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)). This inverts the default of runtimes that optimize for completion: the producer must clear the evidence bar, and silence counts as rejection. Without fail-closed, missing evidence collapses to admit and the verifier becomes a stamping bureau.

## Why it works

Separating the authority to declare done from the agent doing the work removes a measured self-judgment bias. LLMs prefer their own generations when evaluating them, and self-refinement amplifies the preference rather than correcting it ([Xu et al., 2024](https://arxiv.org/abs/2402.11436)). An external verifier breaks that loop, and packetized records make the decision auditable independent of either agent's narration ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)). Either half alone is weaker: self-verification without records is unfalsifiable, and records without an external verifier capture only the producer's chosen evidence. [Spotify's background coding agents](https://engineering.atspotify.com/2025/12/feedback-loops-background-coding-agents-part-3) are a deployed precedent: deterministic verifiers (format, build, test) wired into the loop, with PR creation blocked on failure — an admission gate at the handoff.

## When this backfires

The architecture adds an inter-agent protocol, a verifier, and a record store. It costs more than it returns in these cases:

- Verifier shares the producer's failure modes: the same model class and training data admits the same hallucinations ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)).
- Advisory verifier treated as enforcing: promoted without precision evidence, it mostly blocks valid work — 0.39% blocked precision in the cited deployment ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)).
- Short, low-stakes interactions: for single-turn or exploratory work the bookkeeping exceeds the audit value, as it does for the [verification ledger](../../verification/verification-ledger.md).
- No independent ground truth: when "done" is only another agent's judgment, verifier and producer argue the same uncertain claim.
- Bypass paths: if agents route around the verifier through direct file writes, the gate is only a suggestion.
- External validity unestablished: the evidence is one reporting cluster, 17 production events ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)). Re-measure before transferring the numbers.

The [Multi-Agent System Failure Taxonomy](https://arxiv.org/abs/2503.13657) names inter-agent misalignment as a primary failure category, and a verifier adds one more: producer-verifier disagreement over what "done" means. The pattern re-allocates failure modes; it does not eliminate them.

## Key Takeaways

- Verify-gated completion puts a separate read-only verifier on the critical path of every completion claim, with packetized records and fail-closed defaults ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998))
- The pattern requires independence from the producer, access to ground truth, on-path positioning, and measured blocked precision before the gate is turned from advisory to enforcing
- Published evidence supports a narrow conclusion: under observed conditions the gate made decisions inspectable and fail-closed; deployed operation and external validity remain outside scope ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998))
- A verifier that shares the producer's failure modes or sits off the critical path provides audit data but no admission control
- The architecture re-allocates failure modes (producer-verifier misalignment) rather than eliminating them, consistent with the [Multi-Agent System Failure Taxonomy](https://arxiv.org/abs/2503.13657)

## Related

- [Pre-Completion Checklists](../../verification/pre-completion-checklists.md)
- [Verification Ledger](../../verification/verification-ledger.md)
- [Agent Handoff Protocols](agent-handoff-protocols.md)
- [Pre-Write Change Intent Admission (Claim Plane)](pre-write-change-intent-admission.md)
- [Deterministic Guardrails](../../verification/deterministic-guardrails.md)
- [Closed-Loop Role-Based Refinement](closed-loop-role-based-refinement.md)
