---
title: "Verify-Gated Completion as Admission Control"
description: "A read-only verifier decides whether an agent's completion claim is admitted; ambiguous cases fail closed and every decision is recorded."
tags:
  - multi-agent
  - testing-verification
  - agent-design
---

# Verify-Gated Completion as Admission Control

> Treat "done" in a multi-agent runtime as an admission-control decision — a read-only verifier separate from the producer is the canonical authority, ambiguous cases fail closed, and every decision is captured as a packetized record.

Verify-gated completion is an architecture in which the agent that produced a result is not the one that decides the work is done. A separate, read-only verifier sits on the critical path of every completion claim, admits or rejects it against deterministic checks, and writes the decision into structured admission records ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)). The pattern is worth its inter-agent protocol cost only under specific conditions — independence from the producer, access to ground truth, on-path positioning, and an honest treatment of the verifier's blocked-precision rate.

## When This Pattern Applies

Use this pattern only when all four conditions hold:

- **Verifier is independent of producer.** Different model class, different prompt context, different evidence sources. A verifier sharing the producer's training distribution admits the same hallucinations.
- **Ground truth exists.** The verifier reads deterministic signals — tests, type checks, schema validation, CI exit codes — not just another LLM's opinion.
- **Verifier is on the critical path.** Every completion claim routes through it. Sidecar advisory verifiers provide audit data, not admission control.
- **Blocked precision has been measured.** [Nguyen & Tran (2026)](https://arxiv.org/abs/2605.17998) report a shadow Policy/Governance Verifier with 1,526/1,548 = 98.58% rule agreement but only 2/518 = 0.39% blocked precision — almost every rejection was a false positive. Promoting an enforcing gate without precision evidence blocks more valid work than invalid work.

If any condition fails, prefer agent-internal verification ([pre-completion checklists](../verification/pre-completion-checklists.md)) or recording without admission control ([verification ledger](../verification/verification-ledger.md)).

## The Three Primitives

The pattern reduces to three architectural primitives that compose:

### Read-Only Verifier as Completion Authority

The verifier has no write capability over the work product — it inspects state, runs deterministic checks, and emits an admit/reject decision ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)). Read-only is structural: the verifier cannot patch or retry the producer's output, so responsibility for correctness cannot be offloaded. This complements but does not replace the [evaluator-optimizer workflow](https://www.anthropic.com/engineering/building-effective-agents) where one LLM provides feedback in a refinement loop — evaluator-optimizer keeps the loop inside one agent's responsibility; admission control externalises the authority over "done."

### Packetized Admission Records

Each admit/reject decision is written as a structured record — task identifier, evidence references, verifier identity, decision, timestamp — not prose. The records form a queryable audit surface: every completion has an admission packet, and ambiguous cases are inspectable after the fact ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)). This is the same INSERT-not-prose principle as the [verification ledger](../verification/verification-ledger.md), elevated to inter-agent boundaries.

### Fail-Closed Defaults

Ambiguous or weakly-evidenced cases resolve to reject ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)). This inverts the default behaviour of agent runtimes that optimise for completion: the producer must produce enough evidence to clear the bar, and silence is rejection. Fail-closed is what makes the gate load-bearing — without it, missing evidence collapses to admit and the verifier becomes a stamping bureau.

## Why It Works

Separating the authority to declare done from the agent doing the work removes the premature-completion incentive built into agent training: producing agents optimise for finishing tasks, not for being correct, so self-judgement collapses to the producer's bias toward closure ([Weng et al., 2022](https://arxiv.org/abs/2212.09561)). Packetized state and event traces convert the verifier's decision from prose into structured records, so the gate is inspectable, fail-closed, and auditable independent of either agent's narration ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)). Either half alone is weaker: self-verification without records is unfalsifiable, and records without an external verifier capture only the producer's chosen evidence. [Spotify's Background Coding Agents](https://engineering.atspotify.com/2025/12/feedback-loops-background-coding-agents-part-3) is a deployed precedent without the inter-agent vocabulary — deterministic verifiers (format, build, test) wired into the loop, PR creation blocked on failure — functionally an admission gate at the inter-stage handoff.

## When This Backfires

The architecture adds an inter-agent protocol, a verifier process, and a record store — none of which are free. Conditions under which verify-gated completion costs more than it returns:

- **Verifier shares the producer's failure modes.** Same model class with the same training data accepts the same hallucinations. The bounded reference does not claim independence in its conclusions ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)); without independence the gate is performative.
- **Advisory verifier treated as enforcing.** Promoting an advisory verifier without precision evidence creates a blocking gate that mostly blocks valid work — the shadow verifier had 0.39% blocked precision ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)). Measure precision before turning the gate from advisory to enforcing.
- **Short, low-stakes interactions.** Single-turn agents, one-shot completions, and exploratory work do not benefit from packetized records — bookkeeping overhead exceeds audit value, mirroring the condition under which the [verification ledger](../verification/verification-ledger.md) backfires.
- **No independent ground truth.** When the only signal of "done" is another agent's judgement (no tests, compiler, or schema), verifier and producer argue about the same uncertain claim. The 99.5% verify success in [Nguyen & Tran (2026)](https://arxiv.org/abs/2605.17998) depended on known outcomes.
- **High-cardinality bypass paths.** If agents route around the verifier through direct file writes or off-protocol egress, the gate is a suggestion. The verifier must be on the critical path for every completion claim, not a sidecar.
- **External validity is unestablished.** Evidence comes from a single high-volume reporting cluster — 1,762/1,801 rows from one source, only 17 production-classified events ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)). Applying the pattern outside the original conditions requires re-measuring, not transferring numbers.

The [Multi-Agent System Failure Taxonomy](https://arxiv.org/abs/2503.13657) identifies inter-agent misalignment as one of three primary failure categories. Adding a verifier agent adds a new misalignment surface — verifier-producer disagreement on what "done" means — rather than eliminating one. The pattern is a re-allocation of failure modes, not an elimination of them.

## Key Takeaways

- Verify-gated completion as admission control puts a separate read-only verifier on the critical path of every completion claim, with packetized records and fail-closed defaults ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998))
- The pattern is qualified — it requires independence from the producer, access to ground truth, on-path positioning, and measured blocked precision before the gate is turned from advisory to enforcing
- Published evidence supports a narrow conclusion: under observed conditions the gate made completion decisions inspectable and fail-closed; deployed operation, safety guarantees, and external validity remain outside scope ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998))
- A verifier that shares the producer's failure modes or sits off the critical path provides audit data but no admission control
- The architecture re-allocates failure modes (producer-verifier misalignment) rather than eliminating them, consistent with the [Multi-Agent System Failure Taxonomy](https://arxiv.org/abs/2503.13657)

## Related

- [Pre-Completion Checklists](../verification/pre-completion-checklists.md)
- [Verification Ledger](../verification/verification-ledger.md)
- [Agent Handoff Protocols](agent-handoff-protocols.md)
- [Deterministic Guardrails](../verification/deterministic-guardrails.md)
- [Closed-Loop Role-Based Refinement](closed-loop-role-based-refinement.md)
