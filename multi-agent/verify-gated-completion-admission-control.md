---
title: "Verify-Gated Completion as Admission Control"
description: "A read-only verifier decides whether an agent's completion claim is admitted; ambiguous cases fail closed and every decision is recorded."
tags:
  - multi-agent
  - testing-verification
  - agent-design
  - tool-agnostic
  - arxiv
last_reviewed: 2026-06-02
---

# Verify-Gated Completion as Admission Control

> Verify-gated completion makes a read-only verifier — not the producer — the admission-control authority over every "done" claim: ambiguous cases fail closed, each decision packetized.

Verify-gated completion is an architecture in which the agent that produced a result is not the one that decides the work is done. A separate, read-only verifier sits on the critical path of every completion claim, admits or rejects it against deterministic checks, and writes the decision into a structured admission record ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)). It earns its cost only under the four conditions below.

## When This Pattern Applies

All four must hold:

- **Verifier independent of producer.** Different model class, prompt context, and evidence sources; a verifier sharing the producer's training distribution admits the same hallucinations.
- **Ground truth exists.** Tests, type checks, schema validation, CI exit codes — not another LLM's opinion.
- **Verifier on the critical path.** Every claim routes through it; sidecar advisory verifiers yield audit data, not admission control.
- **Blocked precision measured.** [Nguyen & Tran (2026)](https://arxiv.org/abs/2605.17998) report 98.58% rule agreement but only 0.39% blocked precision — almost every rejection a false positive. Without precision evidence an enforcing gate blocks more valid work than invalid.

If any fails, prefer agent-internal verification ([pre-completion checklists](../verification/pre-completion-checklists.md)) or recording without admission control ([verification ledger](../verification/verification-ledger.md)).

## The Three Primitives

### Read-Only Verifier as Completion Authority

The verifier has no write capability over the work product — it inspects state, runs deterministic checks, and emits an admit/reject decision ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)). Read-only is structural: it cannot patch or retry the output, so correctness cannot be offloaded onto it. This inverts the [evaluator-optimizer workflow](https://www.anthropic.com/engineering/building-effective-agents), which keeps refinement authority inside one agent; admission control externalises it.

### Packetized Admission Records

Each decision is written as a structured record — task identifier, evidence references, verifier identity, decision, timestamp — not prose. The records form a queryable audit surface; every completion has a packet, and ambiguous cases are inspectable after the fact ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)). This is the INSERT-not-prose principle of the [verification ledger](../verification/verification-ledger.md), elevated to inter-agent boundaries.

### Fail-Closed Defaults

Ambiguous cases resolve to reject ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)). This inverts the default of runtimes that optimise for completion: the producer must clear the evidence bar, and silence is rejection. Without fail-closed, missing evidence collapses to admit and the verifier becomes a stamping bureau.

## Why It Works

Separating the authority to declare done from the agent doing the work removes a measured self-judgement bias: LLMs prefer their own generations when evaluating them, and self-refinement amplifies the preference rather than correcting it ([Xu et al., 2024](https://arxiv.org/abs/2402.11436)). An external verifier breaks that loop, and packetized records make the decision auditable independent of either agent's narration ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)). Either half alone is weaker: self-verification without records is unfalsifiable; records without an external verifier capture only the producer's chosen evidence. [Spotify's Background Coding Agents](https://engineering.atspotify.com/2025/12/feedback-loops-background-coding-agents-part-3) is a deployed precedent — deterministic verifiers (format, build, test) wired into the loop, PR creation blocked on failure — functionally an admission gate at the handoff.

## When This Backfires

The architecture adds an inter-agent protocol, a verifier, and a record store. Where it costs more than it returns:

- **Verifier shares the producer's failure modes.** Same model class and training data admits the same hallucinations ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)).
- **Advisory verifier treated as enforcing.** Promoted without precision evidence, it mostly blocks valid work — 0.39% blocked precision in the cited deployment ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)).
- **Short, low-stakes interactions.** For single-turn or exploratory work the bookkeeping exceeds the audit value, as it does for the [verification ledger](../verification/verification-ledger.md).
- **No independent ground truth.** When "done" is only another agent's judgement, verifier and producer argue the same uncertain claim.
- **Bypass paths.** If agents route around the verifier via direct file writes, the gate is a suggestion.
- **External validity unestablished.** Evidence is one reporting cluster, 17 production events ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)). Re-measure before transferring numbers.

The [Multi-Agent System Failure Taxonomy](https://arxiv.org/abs/2503.13657) names inter-agent misalignment as a primary failure category, and a verifier adds one: producer-verifier disagreement over what "done" means. The pattern re-allocates failure modes; it does not eliminate them.

## Key Takeaways

- Verify-gated completion puts a separate read-only verifier on the critical path of every completion claim, with packetized records and fail-closed defaults ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998))
- The pattern requires independence from the producer, access to ground truth, on-path positioning, and measured blocked precision before the gate is turned from advisory to enforcing
- Published evidence supports a narrow conclusion: under observed conditions the gate made decisions inspectable and fail-closed; deployed operation and external validity remain outside scope ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998))
- A verifier that shares the producer's failure modes or sits off the critical path provides audit data but no admission control
- The architecture re-allocates failure modes (producer-verifier misalignment) rather than eliminating them, consistent with the [Multi-Agent System Failure Taxonomy](https://arxiv.org/abs/2503.13657)

## Related

- [Pre-Completion Checklists](../verification/pre-completion-checklists.md)
- [Verification Ledger](../verification/verification-ledger.md)
- [Agent Handoff Protocols](agent-handoff-protocols.md)
- [Deterministic Guardrails](../verification/deterministic-guardrails.md)
- [Closed-Loop Role-Based Refinement](closed-loop-role-based-refinement.md)
