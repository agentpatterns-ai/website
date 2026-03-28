---
title: "Three Knowledge Tiers: Sourced, Unverified, Hallucinated"
description: "Classify agent knowledge into three tiers — sourced, unverified, and hallucinated — to preserve useful training knowledge while maintaining accuracy standards"
tags:
  - context-engineering
  - tool-agnostic
---

# Three Knowledge Tiers: Sourced, Unverified, Hallucinated

> Classify agent knowledge into three tiers — sourced, unverified, and hallucinated — to preserve useful training knowledge while maintaining accuracy standards.

## The Problem with Binary Accuracy Rules

Most anti-hallucination guidelines operate on a binary: either a claim has a citation or it is rejected. This conflates two fundamentally different categories of unsourced knowledge:

- Knowledge the model has from training that is likely accurate but cannot be traced to a specific URL
- Knowledge the model fabricated — plausible-sounding but incorrect

Treating both categories as "hallucination" and silently discarding them loses real signal. Treating both as acceptable loses accuracy.

## The Three Tiers

**Tier 1 — Sourced**: The claim links to a primary source — documentation, a repository, a published blog post. Include as fact.

**Tier 2 — Unverified**: The agent has this knowledge from training and believes it is correct, but cannot produce a specific source URL. Mark inline with `[unverified]` and collect in a dedicated section at the end of the document. The human decides: keep it, research it, or remove it.

**Tier 3 — Hallucinated**: The claim is fabricated — it sounds plausible but the agent cannot verify it and has reason to doubt it. Reject silently or flag explicitly depending on context.

The [unverified] marker creates a human decision point for the grey zone. The agent flags; the human decides.

## How to Apply the Tiers

In practice, agents operating under this pattern follow three rules:

1. If you can cite it, cite it.
2. If you believe it but cannot cite it, write it with `[unverified]` inline and add the claim to an **Unverified Claims** section at the bottom of the document.
3. If you fabricated it or have strong reason to doubt it, omit it.

The collection of unverified claims into a dedicated section is intentional. It makes the audit surface visible — an editor can scan one section to decide what requires further research rather than hunting through the document.

## Anti-Patterns

**Silent inclusion**: The agent uses training knowledge as fact without sourcing it. Readers cannot distinguish sourced from unsourced claims. This is the dominant failure mode in agent-generated content.

**Silent omission**: The agent discards all unsourced knowledge. Correct-but-uncitable information — conventions, tradeoffs, operational patterns — disappears from the output. The document is accurate but thinner than it should be.

**Hedging instead of marking**: The agent writes "the model might prefer..." or "this could possibly..." instead of `[unverified]`. Hedges are invisible to editors and do not surface the claim for review.

## Example

An agent writing a technical summary applies the three tiers inline. The passage below shows Tier 1 (cited), Tier 2 (marked `[unverified]`), and the resulting Unverified Claims section that an editor audits separately.

```markdown
## Summary

Claude 3.5 Sonnet achieves a 49% solve rate on SWE-bench Verified
([source](https://www.anthropic.com/news/claude-3-5-sonnet)), making it
the top-performing publicly available model on that benchmark as of June 2024.

The model uses a 200k token context window, which allows it to process
entire large codebases in a single pass [unverified].

Constitutional AI training reduces refusal rates on benign requests
compared to RLHF-only baselines [unverified].

---

## Unverified Claims

- The model uses a 200k token context window, allowing entire large codebases
  in a single pass. [needs citation — check Anthropic docs]
- Constitutional AI training reduces refusal rates on benign requests compared
  to RLHF-only baselines. [needs citation — may be from research paper]
```

The editor can process the Unverified Claims section in one pass — verifying, citing, or removing each claim — rather than re-reading the full document to find unsourced statements.

## Key Takeaways

- Binary sourced/rejected rules conflate unverified knowledge with hallucination — the distinction matters.
- Mark unverified claims inline with `[unverified]` rather than omitting or silently including them.
- Collect unverified claims in a dedicated section so the audit surface is visible.
- [Human-in-the-loop](../workflows/human-in-the-loop.md) for Tier 2: the agent flags, the human decides.

## Related

- [Context Priming](../context-engineering/context-priming.md)
- [Discoverable vs Non-Discoverable Context](../context-engineering/discoverable-vs-nondiscoverable-context.md)
- [Layered Accuracy Defense](../verification/layered-accuracy-defense.md)
- [Instruction Compliance Ceiling](instruction-compliance-ceiling.md)
- [AGENTS.md as a Table of Contents, Not an Encyclopedia](agents-md-as-table-of-contents.md)
