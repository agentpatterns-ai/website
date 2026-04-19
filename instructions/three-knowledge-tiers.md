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

Most anti-hallucination guidelines operate on a binary: a claim either has a citation or it is rejected. This conflates two different categories of unsourced knowledge:

- Knowledge from training that is likely accurate but cannot be traced to a specific URL
- Knowledge the model fabricated — plausible-sounding but incorrect

Treating both as "hallucination" and discarding them loses real signal. Treating both as acceptable loses accuracy.

## The Three Tiers

**Tier 1 — Sourced**: The claim links to a primary source — documentation, a repository, a published blog post. Include as fact.

**Tier 2 — Unverified**: The agent has this knowledge from training and believes it is correct but cannot produce a source URL. Mark inline with `[unverified]` and collect in a dedicated section at the end of the document.

**Tier 3 — Hallucinated**: The claim is fabricated — plausible-sounding but the agent has reason to doubt it. Reject silently or flag explicitly depending on context.

The `[unverified]` marker creates a human decision point for the grey zone. The agent flags; the human decides.

## How to Apply the Tiers

Agents follow three rules:

1. If you can cite it, cite it.
2. If you believe it but cannot cite it, write it with `[unverified]` inline and add the claim to an **Unverified Claims** section at the bottom of the document.
3. If you fabricated it or have strong reason to doubt it, omit it.

Collecting unverified claims into a dedicated section makes the audit surface visible — an editor scans one section to decide what needs research instead of hunting through prose.

## Anti-Patterns

**Silent inclusion**: The agent uses training knowledge as fact without sourcing it. Readers cannot distinguish sourced from unsourced claims. [Hallucination surveys](https://arxiv.org/html/2509.18970v1) consistently categorize this extrinsic hallucination type — outputs unverifiable against any source — as a primary failure mode in agent-generated content.

**Silent omission**: The agent discards all unsourced knowledge. Correct-but-uncitable information — conventions, tradeoffs, operational patterns — disappears from the output. The document is accurate but thinner than it should be.

**Hedging instead of marking**: The agent writes "the model might prefer..." or "this could possibly..." instead of `[unverified]`. Hedges are invisible to editors and do not surface the claim for review.

## Why It Works

Binary sourced/rejected rules fail because model training knowledge is not uniform — it spans claims the model has seen confirmed across many sources, claims encountered once, and fabrications. Collapsing them into a single "unsourced = rejected" rule discards the first category unnecessarily. Research on [LLM knowledge awareness](https://arxiv.org/html/2411.14257v2) shows models often hold accurate information they cannot trace to a specific document; silent omission throws that signal away.

The second mechanism is audit-surface concentration. Inline hedges like "the model might prefer..." scatter uncertainty throughout the document, forcing an editor to re-read the entire output to find everything requiring verification. The `[unverified]` tag plus a dedicated collection section converts that scattered uncertainty into a single bounded list — the editor processes one section, not the full document. This mirrors established code-review practice, where linting violations are aggregated into a report rather than surfaced one-by-one during reading.

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

## When This Backfires

The three-tier pattern adds value only when the unverified claims section is actually reviewed:

- **Unactioned review backlog**: If the section is never processed before publication, it ships with the document and exposes unvalidated assertions to readers. The pattern requires an active triage step — it does not self-enforce.
- **Tagging discipline erodes under pressure**: Agents operating under token or time constraints skip `[unverified]` tagging, collapsing back to silent inclusion.
- **Tag volume overwhelms the reviewer**: Agents that lack calibration mark everything uncertain. A document with 15 unverified claims becomes noise rather than signal; the human stops reading the section.
- **Tier 2 and Tier 3 are hard to distinguish**: An agent that cannot accurately introspect on its own confidence classifies hallucinated claims as unverified rather than rejected, producing a review list that is systematically optimistic.
- **False confidence from the process itself**: Stakeholders may treat the existence of an "Unverified Claims" section as evidence of rigor even when individual entries are never researched.
- **Low-stakes contexts invert the cost/benefit**: For internal drafts or brainstorming outputs, the overhead of tagging and reviewing exceeds the benefit. The pattern is most valuable where accuracy matters more than throughput.

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
