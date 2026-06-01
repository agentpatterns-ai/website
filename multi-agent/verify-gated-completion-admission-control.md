---
title: "Verify-Gated Completion as Admission Control"
description: "A read-only verifier decides whether an agent's completion claim is admitted; ambiguous cases fail closed and every decision is recorded."
tags:
  - multi-agent
  - testing-verification
  - agent-design
  - tool-agnostic
  - arxiv
last_reviewed: 2026-05-27
---

# Verify-Gated Completion as Admission Control

> Treat "done" in a multi-agent runtime as an admission-control decision — a read-only verifier separate from the producer is the canonical authority, ambiguous cases fail closed, and every decision is captured as a packetized record.

Verify-gated completion is an architecture in which the agent that produced a result is not the one that decides the work is done. A separate, read-only verifier sits on the critical path of every completion claim, admits or rejects it against deterministic checks, and writes the decision into a structured admission record ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)). The pattern is worth its cost only under four conditions: independence from the producer, ground truth, on-path positioning, and a measured blocked-precision rate.

## When This Pattern Applies

All four conditions must hold:

- **Verifier is independent of producer.** Different model class, prompt context, evidence sources. A verifier sharing the producer's training distribution admits the same hallucinations.
- **Ground truth exists.** Tests, type checks, schema validation, CI exit codes — not another LLM's opinion.
- **Verifier is on the critical path.** Every claim routes through it; sidecar advisory verifiers provide audit data, not admission control.
- **Blocked precision has been measured.** [Nguyen & Tran (2026)](https://arxiv.org/abs/2605.17998) report a shadow verifier with 98.58% rule agreement but only 0.39% blocked precision — almost every rejection was a false positive. An enforcing gate without precision evidence blocks more valid work than invalid.

If any condition fails, prefer agent-internal verification ([pre-completion checklists](../verification/pre-completion-checklists.md)) or recording without admission control ([verification ledger](../verification/verification-ledger.md)).

## The Three Primitives

### Read-Only Verifier as Completion Authority

The verifier has no write capability over the work product — it inspects state, runs deterministic checks, and emits an admit/reject decision ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)). Read-only is structural: it cannot patch or retry the output, so correctness cannot be offloaded. This complements the [evaluator-optimizer workflow](https://www.anthropic.com/engineering/building-effective-agents), which keeps refinement authority inside one agent; admission control externalises it.

### Packetized Admission Records

Each decision is written as a structured record — task identifier, evidence references, verifier identity, decision, timestamp — not prose. The records form a queryable audit surface; every completion has a packet, and ambiguous cases are inspectable after the fact ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)). This is the INSERT-not-prose principle of the [verification ledger](../verification/verification-ledger.md), elevated to inter-agent boundaries.

### Fail-Closed Defaults

Ambiguous cases resolve to reject ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)). This inverts the default of runtimes that optimise for completion: the producer must clear the evidence bar, and silence is rejection. Without fail-closed, missing evidence collapses to admit and the verifier becomes a stamping bureau.

## Why It Works

Separating the authority to declare done from the agent doing the work removes a measured self-judgement bias: LLMs prefer their own generations when evaluating them, and self-refinement amplifies the preference rather than correcting for it ([Xu et al., 2024](https://arxiv.org/abs/2402.11436)). An external verifier breaks that loop. Packetized records then convert the decision into structured evidence, so the gate is auditable independent of either agent's narration ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)). Either half alone is weaker: self-verification without records is unfalsifiable; records without an external verifier capture only the producer's chosen evidence. [Spotify's Background Coding Agents](https://engineering.atspotify.com/2025/12/feedback-loops-background-coding-agents-part-3) is a deployed precedent — deterministic verifiers (format, build, test) wired into the loop, PR creation blocked on failure — functionally an admission gate at the handoff.

## When This Backfires

The architecture adds an inter-agent protocol, a verifier, and a record store. Conditions where it costs more than it returns:

- **Verifier shares the producer's failure modes.** Same model class, same training data, same hallucinations admitted ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)).
- **Advisory verifier treated as enforcing.** Promoting an advisory verifier without precision evidence creates a blocking gate that mostly blocks valid work — 0.39% blocked precision in the cited deployment ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)).
- **Short, low-stakes interactions.** Single-turn or exploratory work — bookkeeping exceeds audit value, mirroring when the [verification ledger](../verification/verification-ledger.md) backfires.
- **No independent ground truth.** When the only "done" signal is another agent's judgement, verifier and producer argue about the same uncertain claim.
- **Bypass paths.** If agents route around the verifier through direct file writes, the gate is a suggestion.
- **External validity unestablished.** Evidence comes from one reporting cluster with only 17 production-classified events ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)). Re-measure before transferring numbers.

The [Multi-Agent System Failure Taxonomy](https://arxiv.org/abs/2503.13657) identifies inter-agent misalignment as a primary failure category. Adding a verifier creates a new misalignment surface — verifier-producer disagreement on what "done" means. The pattern re-allocates failure modes; it does not eliminate them.

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
