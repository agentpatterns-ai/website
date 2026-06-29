---
title: "Three Knowledge Tiers: Sourced, Unverified, Hallucinated"
term: "Three Knowledge Tiers"
description: "Classify agent knowledge into three tiers — sourced, unverified, and hallucinated — to preserve useful training knowledge while maintaining accuracy standards"
tags:
  - context-engineering
  - tool-agnostic
  - instructions
last_reviewed: 2026-05-27
maturity: established
---

# Three Knowledge Tiers: Sourced, Unverified, Hallucinated

> Classify agent knowledge into three tiers — sourced, unverified, and hallucinated — to preserve useful training knowledge while maintaining accuracy standards.

## The problem with binary accuracy rules

Most anti-hallucination guidelines work on a binary: a claim either has a citation or it is rejected. This blurs two different kinds of unsourced knowledge:

- Knowledge from training that is likely accurate but cannot be traced to a specific URL
- Knowledge the model fabricated — plausible-sounding but incorrect

Treat both as "hallucination" and discard them, and you lose real signal. Treat both as acceptable, and you lose accuracy.

## The three tiers

Tier 1 — Sourced: the claim links to a primary source such as documentation, a repository, or a published blog post. Include it as fact.

Tier 2 — Unverified: the agent has this knowledge from training and believes it is correct, but cannot produce a source URL. Mark it inline with `[unverified]` and collect it in a section at the end of the document.

Tier 3 — Hallucinated: the claim is fabricated. It sounds plausible, but the agent has reason to doubt it. Reject it silently or flag it, depending on context.

The `[unverified]` marker creates a human decision point for the gray zone. The agent flags; the human decides.

## How to apply the tiers

Agents follow three rules:

1. If you can cite it, cite it.
2. If you believe it but cannot cite it, write it with `[unverified]` inline and add the claim to an Unverified Claims section at the bottom of the document.
3. If you fabricated it or have strong reason to doubt it, omit it.

Collecting unverified claims into one section makes the audit surface visible. An editor scans one section to decide what needs research, rather than hunting through the prose.

## Anti-patterns

Silent inclusion: the agent uses training knowledge as fact without sourcing it. Readers cannot tell sourced claims from unsourced ones. [Hallucination surveys](https://arxiv.org/html/2509.18970v1) consistently categorize this extrinsic hallucination type — outputs that cannot be checked against any source — as a primary failure mode in agent-generated content.

Silent omission: the agent discards all unsourced knowledge. Correct but uncitable information — conventions, tradeoffs, operational patterns — disappears from the output. The document is accurate but thinner than it should be.

Hedging instead of marking: the agent writes "the model might prefer..." or "this could possibly..." instead of `[unverified]`. Hedges are invisible to editors and do not surface the claim for review.

## Why it works

Binary sourced/rejected rules fail because model training knowledge is not uniform. It spans claims the model has seen confirmed across many sources, claims it met once, and fabrications. Collapsing them into a single "unsourced = rejected" rule discards the first category for no reason. Research on [LLM knowledge awareness](https://arxiv.org/html/2411.14257v2) shows models often hold accurate information they cannot trace to a specific document. Silent omission throws that signal away.

The second mechanism is audit-surface concentration. Inline hedges like "the model might prefer..." scatter uncertainty through the document. They force an editor to re-read the whole output to find everything that needs checking. The `[unverified]` tag plus a collection section turns that scattered uncertainty into one bounded list. The editor processes one section, not the full document. This mirrors code-review practice, where linting violations are gathered into a report rather than surfaced one by one during reading.

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

## When this backfires

The three-tier pattern adds value only when someone actually reviews the unverified claims section:

- Unactioned review backlog: if no one processes the section before publication, it ships with the document and exposes unvalidated claims to readers. The pattern needs an active triage step. It does not self-enforce.
- Tagging discipline erodes under pressure: agents working under token or time limits skip `[unverified]` tagging and fall back to silent inclusion.
- Tag volume overwhelms the reviewer: agents that lack calibration mark everything uncertain. A document with 15 unverified claims becomes noise rather than signal, and the human stops reading the section.
- Tier 2 and Tier 3 are hard to tell apart: an agent that cannot accurately judge its own confidence labels hallucinated claims as unverified rather than rejected. The review list then runs systematically optimistic.
- False confidence from the process itself: people may treat an "Unverified Claims" section as evidence of rigor even when no one researches the individual entries.
- Low-stakes contexts invert the cost and benefit: for internal drafts or brainstorming, the work of tagging and reviewing costs more than it returns. The pattern is most valuable where accuracy matters more than throughput.

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
