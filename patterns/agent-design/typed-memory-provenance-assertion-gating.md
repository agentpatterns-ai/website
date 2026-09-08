---
title: "Typed Memory Provenance and Assertion Release Gating"
term: "Assertion Release Gating"
description: "Tag each stored claim with its epistemic role, validity window, and disclosure scope, then check candidate output against that record before release — because tagging origin alone stopped 1 of 19 unsafe releases."
tags:
  - agent-design
  - memory
  - context-engineering
  - tool-agnostic
  - arxiv
aliases:
  - typed provenance for agent memory
  - assertion release gating
  - autobiographical assertion boundedness
last_reviewed: 2026-09-05
maturity: emerging
---

# Typed Memory Provenance and Assertion Release Gating

> Typed provenance records each stored claim's role and validity window, and a release gate checks output against it before the agent asserts anything.

Three conditions decide whether this pattern is worth building. Your agent makes statements about itself, the user, or a named relationship, so there is something to govern. Some of what reaches its store arrives from a channel you do not control. And you can name the output channels the check has to sit on. Outside those conditions, persisting less and regenerating more is the cheaper answer.

The framing comes from [He and Yu (2026)](https://arxiv.org/abs/2609.02127v1): "Storing or retrieving an unverified string or model inference does not authorize its presentation as an authentic part of the agent's autobiographical history."

## What the type carries

The paper's baselines separate two designs. A source-tag rule carries origin alone. The full type carries four values per node:

| Value | What it holds |
|---|---|
| Epistemic role | "Model priors, raw retrieved inputs, admitted evidence, derived interpretations, and recorded beliefs" stay "distinct persisted objects" |
| Proposition | "The structured proposition carried by" the node, or a null for non-propositional evidence |
| Validity interval | "Its validity interval over the extended time domain" |
| Authorization scope | "The authorization scope across principals, purposes, and tasks" |

In the paper's suite, a source-tag rule "prevents one unsafe release but admits the other 18 (94.7% UOR, 78.3% RC over |R|=23)", while typed mediation "passed none of 19 unsafe opportunities unqualified and passed all five supported controls" ([He and Yu, 2026](https://arxiv.org/abs/2609.02127v1)).

## Three enforcement points

The paper names three surfaces:

- State admission "regulates which epistemic entities enter the accepted state graph".
- Context projection "filters accepted state into an authorized projection".
- Assertion mediation "intercepts candidate responses at governed output channels to verify content support and disclosure safety before release" ([He and Yu, 2026](https://arxiv.org/abs/2609.02127v1)).

Write-path filtering and retrieval scoring are the first two. The mediation gate is the check on the way out, comparing a candidate statement against what was admitted.

## Why it works

A release condition cannot be outvoted by similarity; a score penalty can. [Karunanidhi (2026)](https://arxiv.org/abs/2608.21230v1) measured the arithmetic on a retrieval-path provenance defense: "An untrusted memory takes a fixed score penalty of 0.245, while the entire semantic term contributes at most 0.45", so a poisoned entry that looks relevant enough still wins retrieval. At shipped weights the defense was "statistically indistinguishable from no defense (p=0.80)". Raising the weight until poison loses removes legitimate untrusted evidence with it: at the corrected weight, "Not one answer-bearing memory survived ranking for any of the 120 questions" and accuracy fell to 0.0417.

Moving the check to the output path escapes that trade. The gate does not rank a claim against competitors; it asks whether the statement is supported by admitted evidence and refuses or qualifies it if not. Origin is the weak signal in both studies. As a ranking penalty it loses to similarity, and as a release rule on its own it stopped 1 of 19.

## When this backfires

- The type says origin, not truth. A false claim entering through a correctly-typed channel passes. A four-stage content screener reaching "0.832 recall on indirect prompt injection" nonetheless "refuses 0 of 360 poisoned memories", because the attack carried "no instruction, no override, no role manipulation, and no exfiltration construct — nothing beyond a false assertion" ([Karunanidhi, 2026](https://arxiv.org/abs/2608.21230v1)). Separating a false statement from a true one needs grounding the store does not hold.
- The step you have to build is the one that was not tested. The paper's artifact "does not implement natural-language semantic extraction", so every conformance result assumes the mapping from free text to a typed proposition already happened correctly. In production that mapping is the whole system.
- The evidence is a specification test. Twenty-four hand-authored cases exercise obligations the same authors encoded, and they "do not constitute an end-to-end evaluation of language models or retrieval systems" ([He and Yu, 2026](https://arxiv.org/abs/2609.02127v1)). Read the 19-of-19 as the specification behaving as written.
- Compaction erases lineage. Taint-based methods "remain difficult to apply when information is transformed through summarization, paraphrasing, memory consolidation, or multi-step reasoning" ([Wang et al., 2026](https://arxiv.org/abs/2606.04990v3)), and a long agent session does all four continuously.
- One gate is not a gate. The mechanism does not "audit unmediated out-of-band channels" ([He and Yu, 2026](https://arxiv.org/abs/2609.02127v1)). A tool call, a log line, or a side channel that skips the mediated path skips the property with it.
- The scope is narrow. The property covers governed statements about the agent, the user, or named relationships. An agent that mostly emits diffs and test output gives the gate almost nothing to mediate.
- Model-swap invariance is argued, not measured. The paper reasons that replacing the model under a fixed state head leaves the accepted claim set unchanged ([He and Yu, 2026](https://arxiv.org/abs/2609.02127v1)), which follows from how the formalism separates the two. No such experiment is reported.

## Key Takeaways

- A source tag carries origin alone, and in this suite it stopped 1 unsafe release in 19. Adding role, validity, and scope is what changed the number.
- Put the check on the output path. Ranking penalties lose to similarity at usable weights and destroy recall at weights that win.
- Typing certifies where a claim came from. Nothing here decides whether it is true, so a legitimate channel carrying a falsehood still gets through.
- The published evidence is a hand-authored conformance suite with the natural-language extraction step stubbed out. Budget for that step being where your failures live.

## Related

- [Self-Correcting Memory: Evidence-Backed Claim Repair](self-correcting-memory-evidence-backed-claims.md) — the freshness half, deciding whether a stored claim is still true rather than whether it may be asserted
- [Knowledge Graphs as Provenance-Carrying Agent Memory](knowledge-graph-shared-memory.md) — source attribution as a retrieval property, which is the one-field design this pattern measures itself against
- [Memory Retrieval as a Control Decision](memory-retrieval-as-control.md) — the read-path gate, governing what reaches the model where this pattern governs what leaves it
- [Layered Mutability: Governing Persistent Self-Modifying Agents](layered-mutability.md) — where governance attaches across a persistent agent's layers, of which memory is one
- [Detecting Memory-Poisoning Exfiltration by Tool-Call Order](../../security/recall-before-send-memory-poisoning-detection.md) — the adversarial case this gate is sized against
