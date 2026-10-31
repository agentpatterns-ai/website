---
title: "Treating a Converter's Output as the Whole Document"
term: "Converter Output as the Document"
description: "Formatting-blind ingestion deletes the color and highlighting an author used to mark obligations, which can leave the agent guessing or omitting requirements without a parser warning."
tags:
  - anti-pattern
  - context-engineering
  - tool-agnostic
  - arxiv
aliases:
  - formatting-blind ingestion
  - silent cue loss
  - document ingestion cue loss
last_reviewed: 2026-10-26
maturity: emerging
---

# Treating a Converter's Output as the Whole Document

> A formatting-blind converter drops color and highlighting from a policy document, so an agent can miss which requirements the author marked as important.

Formatting-blind ingestion drops color and highlighting that can identify obligations. Zhao et al. tested 76 real `.docx` policy documents with Claude Opus 4.6. Each arm received the same question, with only the parsed representation changed. Micro F1 was 0.075 for plain text, 0.150 for docling, and 0.690 for the authors' cue-preserving representation. Ground truth came from OOXML run properties; scoring used a deterministic matcher ([Zhao et al., 2026, §4.1](https://arxiv.org/abs/2610.30026v1)).

## What the monitors miss

Every tested arm returned well-formed output without reporting missing content (§4.8). Docling's false-positive rate was 0.043, against 0.011 for the cue-preserving arm. The authors attribute this to guessing when cues are absent (§4.2). Two answering models instead attempted few requirements (§4.6).

## Why it works

Markdown has no native slot for font color or highlighting. The paper adds custom tags to preserve these cues (§3.1).

A span-level ablation localizes the benefit to highlight and color. Bold, italic, monospace and strikethrough each contributed within ±0.003 macro F1 of zero. The authors attribute the difference to rarity: common formatting marks many passages without identifying special obligations (§4.3).

Typing a cue added +0.085 macro F1 over the identical untyped marker on 79 documents with six repeats. The confidence interval was [+0.035, +0.145], with Holm-adjusted p = 0.049. This estimate uses only the salience roles `critical_warning`, `warning` and `deprecated`; its interval is wide (§4.4).

## When this backfires

- Few documents carry relevant cues. Of 6,462 scanned `.docx` files, 32.8% contained deliberate red text or non-white highlighting. Only 10.3% contained one on a modal obligation sentence (Appendix S1).
- Context is scarce. The representation costs roughly twice the tokens of plain text (§4.8).
- The model does not use hints. Typing replicated on three of six models, was positive on five, and showed no benefit on two sparse-attempt models (§4.6).
- The vocabulary includes structural roles. Roughly 62% of role tokens across 40 documents did not identify special attention. A weaker model over-triggered on them (§4.6).
- The PDF lacks native text. The system runs no OCR. All arms recovered zero cues for 18 of 126 ParseBench rules whose text was absent from that layer (Appendix S8).

The authors exclude medium-confidence mappings, including green text to status marker, because incorrect hints can bias the agent (§3.1).

## Example

Appendix S31 traces the pipeline over `test_doc.docx`, "an IT Password Reset Procedure SOP", whose entire Security Warning paragraph is red text. The serialized form below is the paper's own output; the plain-text form above it is the same paragraph with the markup removed.

**Before — plain-text conversion, cue dropped:**

```text
Security Warning
NEVER share temporary passwords via email
or chat messages. Email is not a secure channel and violates the
company security policy. Always use a phone call or an encrypted
messaging platform.
```

**After — the parser's hybrid serialization, cue recovered and typed:**

```text
[HEADING level=2]Security Warning[/HEADING]
[COLOR:red][CRITICAL_WARNING]NEVER share temporary passwords via email
or chat messages. Email is not a secure channel and violates the
company security policy. Always use a phone call or an encrypted
messaging platform.[/CRITICAL_WARNING][/COLOR]
```

Both inputs carry the same words. Only the second says the author marked this paragraph in red, and labels it with the parser's critical-warning interpretation. In the general case a block-level role rides on the structural tag, as `[PARAGRAPH roles="CRITICAL_WARNING"]` (Appendix S14), while inline markers such as `[COLOR:#FF0000]` and `[HIGHLIGHT:YELLOW]` carry what Markdown has no syntax for (§3.1).

## Key Takeaways

- Assert at the ingestion layer, not on the output. The paper's own parser now asserts that a recovered cue implies a located span, and that check "caught a defect we had already published in a table" (§4.8).
- Measure your corpus before paying for a richer parser. The number that decides it is the share of your documents carrying a mark on an obligation sentence, not the share carrying a mark anywhere.
- Preserve the cues your authors use sparingly and skip the rest. A cue on every heading does not distinguish exceptional obligations.
- Account for the extra context tokens. Recovery itself uses code without model calls (§4.8).
- Filter the role vocabulary down to the salience roles. Test whether structural role tokens cause over-triggering in your model.

## Related

- [Source Code Minification for State-in-Context Agents](../../context-engineering/source-code-minification-trade-off.md) — the same trade run the other way, where shrinking the input costs resolution rate.
- [Validating Token-Optimized Formats Inside Agentic Loops](../../context-engineering/validate-token-optimized-formats-in-agentic-loops.md) — a format change that looks lossless in isolation and loses accuracy end to end.
- [Typed Context Buys Addressability, Not Token Savings](../../context-engineering/typed-context-addressability.md) — typed context for harness addressability.
- [Exhaustive Retrieval for Listing Questions](../../context-engineering/exhaustive-retrieval-for-listing-questions.md) — the downstream shape of this task, where ranked retrieval gives no signal that the answer needed more.
- [Completion Summary as the Oversight Surface](completion-summary-as-oversight-surface.md) — the same mistake at the other end of the run, where a well-formed artifact stands in for what actually happened.
