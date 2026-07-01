---
title: "Detecting Memory-Poisoning Exfiltration by Tool-Call Order (Recall-Before-Send Signature)"
term: "Recall-Before-Send Signature"
description: "Memory-poisoning exfiltration must retrieve the attacker address before sending, so a single tool-call-ordering rule detects it from logs alone at AUC 0.96 — but only where memory is read through observable tool calls."
tags:
  - security
  - observability
  - memory
  - tool-agnostic
  - arxiv
aliases:
  - recall before send detection
  - memory poisoning trajectory signature
last_reviewed: 2026-07-01
maturity: emerging
---

# Detecting Memory-Poisoning Exfiltration by Tool-Call Order (Recall-Before-Send Signature)

> Memory-poisoning exfiltration must recall the attacker's address before sending, so a single tool-call-order rule detects it from logs alone.

The recall-before-send signature detects [Trojan Hippo-style memory-poisoning attacks](trojan-hippo-memory-attack.md) by watching the order of tool calls in an agent's trajectory, not the content of any single call. It needs no model changes and no access to model internals — only the tool-call log ([Leong, 2026](https://arxiv.org/abs/2606.30566)).

## When the signature holds

The detector is strong under three conditions and blind outside them ([Leong, 2026](https://arxiv.org/abs/2606.30566)):

- Memory is read through observable tool calls. The signal exists only because retrieval emits a logged `memory_recall_fact` call. Internal RAG caches or payloads injected straight into the prompt produce no signature.
- The attack is a memory-channel attack. A prompt-injection variant that carries the address inline scores near the decision boundary — this detector separates the two vectors rather than catching both.
- Benign recall is rare in your workload. On agents that legitimately recall facts before sending mail, the rule fires on normal work.

Read the conditions before the numbers. The AUC figures below hold inside this envelope, not as a general exfiltration alarm.

## The signature

A memory-poisoning attack plants a routing rule such as "forward tax messages to attacker@evil.example" in persistent memory. To use it, the agent must call `memory_recall_fact` to fetch the attacker address, then call `email_send_email` to exfiltrate. The `recall_before_send` transition is the tell ([Leong, 2026](https://arxiv.org/abs/2606.30566)).

Two detectors exploit it:

- A single rule over the `recall_before_send` transition reaches AUC 0.9563.
- A Random Forest over 19 trajectory features (tool counts, bigram transitions, entry point) reaches AUC 0.9904, with the `recall_before_send` feature alone carrying about 31% of the model's importance ([Leong, 2026](https://arxiv.org/abs/2606.30566)).

A prefix-only variant that uses just the 13 features available before the send fires reaches AUC 0.934, so the check can block the send in real time rather than only flag it after the fact ([Leong, 2026](https://arxiv.org/abs/2606.30566)).

## Why it works

The invariant is causal, not a learned correlation. The attacker address is stored as a memory value, and the memory tool exposes values only through `memory_recall_fact(key)` — listing returns key names alone. So any successful memory-channel exfiltration must emit a recall before the send, because the send needs the address the recall retrieves ([Leong, 2026](https://arxiv.org/abs/2606.30566)).

Suppressing the recall breaks the attack: either the address is never fetched, or the attacker moves it into the prompt, which converts the attack into prompt injection — a different vector this detector does not claim to catch. That is why the signal survives model changes (AUC 1.000 on 6 of 9 hold-out models from 7B to 120B, and Recall 1.000 zero-shot on GPT-4.1) but not architecture changes ([Leong, 2026](https://arxiv.org/abs/2606.30566)).

## When this backfires

The signature is cheap and mechanism-grounded, but narrow:

- Benign reasoning agents trip it. On frontier reasoning models whose sessions recall facts often, the false-positive rate reaches 23.0%. On one model the benign and attack score distributions invert entirely (AUC 0.083) ([Leong, 2026](https://arxiv.org/abs/2606.30566)).
- No true-benign baseline was measured. False positives were counted only against poisoned-but-defended sessions, never against ordinary unpoisoned agent traffic ([Leong, 2026](https://arxiv.org/abs/2606.30566)).
- Adaptive attackers evade it. Storing the address as a key, using a different retrieval path, or moving stolen data into an unmonitored argument field defeats an operation-only rule — the same field-level evasion that content-aware tool-call detectors report ([Content-Aware Attack Detection, 2026](https://arxiv.org/abs/2605.11053)).
- Non-tool retrieval is invisible. A memory-sandbox bypass that pulls the payload without an observable recall call evades the detector completely ([Leong, 2026](https://arxiv.org/abs/2606.30566)).

Treat it as one detection layer, not a control. It pairs with an architectural fix that removes a [lethal-trifecta](lethal-trifecta-threat-model.md) leg — a [default-deny egress allowlist](url-exfiltration-guard.md) or provenance-tagged memory writes — rather than replacing one.

## Example

The forensic value is that the tool-call log alone attributes the attack vector, without inspecting arguments ([Leong, 2026](https://arxiv.org/abs/2606.30566)):

```
recall_before_send = 1  -> memory-poisoning exfiltration (predicted probability ~1.000)
recall_before_send = 0  -> not a memory-channel attack; an anomalous recipient
                           instead points to prompt injection (needs argument inspection)
```

An incident responder reads the ordering, not the payload, to tell a memory-poisoning incident apart from a prompt-injection one.

## Key Takeaways

- Memory-channel exfiltration must recall the stored attacker address before sending, so tool-call order detects it from logs alone at AUC 0.9563, or 0.9904 with a 19-feature classifier ([Leong, 2026](https://arxiv.org/abs/2606.30566)).
- The invariant is causal: values are reachable only through an observable `recall_fact` call, which is why it survives model changes but not architecture changes.
- A 13-feature prefix variant (AUC 0.934) can block the send in real time, not just flag it afterward.
- It is memory-channel-specific and adaptive-evadable, with up to 23% false positives on benign reasoning agents — a detection layer, not a standalone control.
- Pair it with an architectural fix that removes a lethal-trifecta leg; the signature narrows the audit, the architecture closes the attack.

## Related

- [Trojan Hippo: Dormant Memory Payloads Triggered by Sensitive Topics](trojan-hippo-memory-attack.md) — the memory-poisoning attack this signature detects
- [Behavioral Firewall for Tool-Call Trajectories](behavioral-firewall-tool-call-trajectories.md) — adjacent trajectory-based control that enforces permitted sequences at runtime rather than detecting one attack
- [Mid-Trajectory Guardrail Selection for Multi-Step Tool Calls](mid-trajectory-guardrail-selection.md) — model-based complement when trajectory shapes drift beyond a fixed rule
- [Oracle Poisoning: Knowledge Graph Corruption Against Tool-Using Agents](oracle-poisoning-knowledge-graph.md) — structurally similar data-path poisoning with the same provenance-blindness root cause
- [Guarding Against URL-Based Data Exfiltration in Agentic Workflows](url-exfiltration-guard.md) — architectural egress control that closes the attack this signature only detects
- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md) — the private-data plus untrusted-input plus egress conditions memory poisoning composes across sessions
