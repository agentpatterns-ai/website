---
title: "Explanation-Bound Tool Execution for Agent Gateways"
term: "Explanation-Bound Tool Execution"
description: "A tool gateway turns the agent's stated reason into typed claims and checks each one against a fact it already holds, so the prose never widens authority."
tags:
  - security
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - server-verified action claims
  - typed action claims
  - claim-carrying tool mediation
  - EBTE
last_reviewed: 2026-09-22
maturity: emerging
---

# Explanation-Bound Tool Execution for Agent Gateways

> A tool gateway checking typed action claims against its own facts allowed none of 96 authored hard contradictions; a free-form justification allowed 60.

Explanation-bound tool execution converts an agent's stated reason into a small set of typed claims and compares each claim against a fact the application already holds. The claim set carries no authority of its own. Matching claims stay eligible for execution, contradictions deny, and incomplete or uncertain claims route to a non-executing review ([Zhu & Wang, arXiv:2607.25364v3](https://arxiv.org/abs/2607.25364v3)). Free-form rationales are "neither authorization nor reliable introspection", so the verifier never scores the prose. Only fields a server can look up are enforceable: intent class, selected tool, policy rule identifiers, expected effect and its bounds, risk tier, declared uncertainty, and the provenance category of any untrusted context.

## When this is worth building

Four conditions. The first decides whether the rest matter.

- Your application already owns the facts. The verifier resolves an intent certificate, a canonical tool registry, a policy snapshot, an authorized route record, and a context-risk snapshot. The layer "does not create those facts and should not be placed inside the same untrusted planner that generated the proposal" ([§XIII-D, arXiv:2607.25364v3](https://arxiv.org/abs/2607.25364v3)). With nothing independent to compare against, every claim resolves unknown and you have built a review queue.
- The action is not already gated on risk tier. Where the tool is high-impact enough to demand review whatever the claim says, this layer changes the recorded reason rather than the outcome, which is what the paper's own external transfer tier found ([§XII-B, arXiv:2607.25364v3](https://arxiv.org/abs/2607.25364v3)).
- The model can emit the object. One of the four hosted families in the paper's pilot parsed 7 of 24 initial attempts and passed schema validation on 2 of 24 ([Table V, arXiv:2607.25364v3](https://arxiv.org/abs/2607.25364v3)).
- Every effectful call meets the gateway. The check "provides no guarantee for effects that bypass its gateway" ([§II-B, arXiv:2607.25364v3](https://arxiv.org/abs/2607.25364v3)), the same mediation assumption that bounds [intent-governed tool authorization](intent-governed-tool-authorization.md).

## What each rung actually blocks

The paper ablates its own profile across 136 authored tasks, 96 carrying a designated hard contradiction.

| What the gateway requires | Hard contradictions allowed |
|---|---|
| A non-empty free-form justification | 0.6250 |
| A schema-valid object, values unchecked | 0.5729 |
| Tool, operation, resource and numeric bounds compared to the payload | 0.3646 |
| Every contract dimension compared to server facts | 0.0000 |

Source: [Table III, arXiv:2607.25364v3](https://arxiv.org/abs/2607.25364v3). The full profile "denies all 96 designated hard cases and routes all 32 soft cases to review". Composed against a reference draft endpoint over 68 tasks it "forwards none of 48 designated hard cases, while all 16 soft and 4 aligned cases create governed drafts", where the justification-only configuration forwarded every one.

The third rung is what a team that will never build the reference profile can still use, because it needs no new fact store. Compare what the explanation declares against the payload the agent is actually sending, and the allow rate falls from 0.5729 to 0.3646. Closing the remaining 0.3646 is what costs an intent certificate, a policy snapshot, a route record and a context snapshot.

## Why it works

The mechanism replaces a persuasion judgement with a lookup. Each enforceable field names a value the gateway can resolve in a store it already trusts, so "each enforceable statement becomes a proposition that the application can independently accept, reject, or mark unresolved" ([§XIII-D, arXiv:2607.25364v3](https://arxiv.org/abs/2607.25364v3)). Fluency contributes nothing because nothing reads it.

The second half is the composition order. Baseline authorization, the claim disposition, and the effect controls combine by their most restrictive outcome, and declared uncertainty is "one-way escalation only; a low declaration cannot establish certainty" ([Table I, arXiv:2607.25364v3](https://arxiv.org/abs/2607.25364v3)). A claim can tighten a decision and can never widen one, which is what makes the layer safe to attach to a system whose planner and explanation generator are the same untrusted model.

The premise has independent support. On the τ²-bench airline domain, 78% of a budget agent's observed failures were silent wrong states that "neither the tool nor the agent's self-report exposes" ([Reddy, Challaram & Basu, arXiv:2607.07405v2](https://arxiv.org/abs/2607.07405v2)). The self-report is where the evidence is missing, not where it is wrong.

## When this backfires

- The action was already review-gated, so you gain a reason and no blocking. On the pinned AgentDojo banking adaptation every configuration held all 12 cross-task attack proposals non-allow, because the banking tools are high risk. The full profile "changes the diagnostic disposition of the 12/12 task–proposal contradictions from review to deny; the immediate non-allow rate remains 12/12 under every ablation" ([§XII-B, arXiv:2607.25364v3](https://arxiv.org/abs/2607.25364v3)).
- The headline number is conformance, not external validity. "Expected outcomes are defined by the same profile implemented by the evaluator, so profile-disposition agreement measures conformance within that profile" ([§XVI, arXiv:2607.25364v3](https://arxiv.org/abs/2607.25364v3)). The suite is "small, authored, and partially generated from 8 base tasks".
- Unavailable state turns into review volume. More predicates "increase integration cost, fact freshness requirements, and the probability of review when state is unavailable" ([§XIII-C, arXiv:2607.25364v3](https://arxiv.org/abs/2607.25364v3)). A flaky policy store converts into operator work.
- Repair loops do not converge. Among 96 paired initial and post-feedback attempts, 8 moved from agreement to disagreement against 3 moving the other way, and feedback was "not monotonically associated with recorded profile agreement" ([§XI-B, arXiv:2607.25364v3](https://arxiv.org/abs/2607.25364v3)). Budget the retries.
- Detailed rejection reasons teach the attacker, since reason codes "can become an adaptive oracle" ([§XIII-C, arXiv:2607.25364v3](https://arxiv.org/abs/2607.25364v3)). Keep what the model sees coarser than what the audit record keeps.
- The packet is neither a correctness certificate nor a leak control. It "may increase operator confidence even when upstream facts are wrong" ([§XIV-E, arXiv:2607.25364v3](https://arxiv.org/abs/2607.25364v3)), and its summary field stays free text, where "the fixed-marker test does not detect novel encoding" ([§XIV-D, arXiv:2607.25364v3](https://arxiv.org/abs/2607.25364v3)).
- Typing the explanation throws away whatever signal lived in the prose. The 41 authors of a 2025 paper on chain-of-thought monitorability argue that models acting in a misaligned way "often explicitly say so in their reasoning traces", which makes the trace worth monitoring for "the intent to misbehave" ([Korbak et al., arXiv:2507.11473v2](https://arxiv.org/abs/2507.11473v2)). A schema has no field for an intention nobody anticipated. Run both.

## Example

The paper publishes its contract object as `ebte-0.1`, a compatibility identifier it is careful to call "not a name for the mechanism described in this paper" ([Appendix A, arXiv:2607.25364v3](https://arxiv.org/abs/2607.25364v3)). Below is that schema carrying a claim a user's summarize request does not justify:

```json
{
  "schemaVersion": "ebte-0.1",
  "intentClasses": ["read", "summarize"],
  "intentSummary": "Summarize Q1 revenue for the requested ledger.",
  "selectedTool": "records.export",
  "toolReasonCode": "tool.effect_matches_intent",
  "policyBasis": {
    "requiredScopes": ["record.read"],
    "policyRuleIds": ["policy.export.review"],
    "decision": "allow"
  },
  "expectedEffect": {
    "operation": "export",
    "resourceType": "record",
    "resourceIds": ["collection_a"],
    "maxRecords": 50000,
    "destination": "external_bucket"
  },
  "riskTier": "low",
  "uncertainty": {"level": "low", "reasonCodes": []},
  "untrustedContextDependencies": [],
  "evidenceRefs": [
    {"type": "intent_certificate", "digest": "sha256:0000"},
    {"type": "policy_snapshot", "digest": "sha256:1111"},
    {"type": "payload", "digest": "sha256:2222"}
  ]
}
```

The verifier reads no word of `intentSummary` or `toolReasonCode`, which are "operator-facing only" and "never used to widen a decision" ([Table II, arXiv:2607.25364v3](https://arxiv.org/abs/2607.25364v3)). Three typed fields settle it instead.

`expectedEffect.operation` is `export` where the certificate covers read and summarize, and the payload operation "checked against the certified operation set" fails hard. `untrustedContextDependencies` is empty while the current context snapshot holds an untrusted source, and omitting a material untrusted dependency is a hard category too. `riskTier` of `low` sits under the registry's risk for `records.export`, which escalates only: "declared risk never lowers server risk". The first two deny, the third would review on its own, and the most restrictive outcome wins. What returns to the model is a stable reason code naming the failed dimension, carrying no source content.

## Key Takeaways

- Collect a rationale only if you will check it. An unchecked justification requirement is close to collecting nothing, and it reads like a control on the architecture diagram.
- Pick the enforceable fields your application can already resolve, and let them tighten a decision but never widen one. Declared confidence escalates upward only.
- Where the tool already demands review on risk, expect a better audit reason rather than a blocked attack.
- Keep model-facing rejections coarse and the audit record detailed. The same text does both jobs badly.

## Related

- [Intent-Governed Tool Authorization for AI Agents (IGAC)](intent-governed-tool-authorization.md) — the same authors' upstream layer, narrowing the visible manifest from a server-issued certificate. This page covers the explanation object IGAC's consistency check never reads.
- [Deterministic Precondition Gates](../patterns/agent-design/deterministic-precondition-gates.md) — a pure predicate over the proposed call and live state, with no explanation as input. The cheaper control, and the one to build first.
- [Chain-of-Thought Reasoning Fallacy](../fallacies/chain-of-thought-reasoning-fallacy.md) — why the trace is post-hoc rationalization. This page is what a server can check once you accept that.
- [Hybrid Deterministic + Semantic Authorization for Agent Tool Calls](hybrid-deterministic-semantic-tool-authorization.md) — CASA checks the call's form; the claim layer checks the reason attached to it.
- [Enforced Versus Advisory Controls in LLM-Native IDEs](enforced-versus-advisory-controls.md) — the sorting rule underneath: a control the runtime evaluates binds, a control resolved inside the model's context does not.
