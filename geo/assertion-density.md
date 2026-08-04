---
title: "Assertion Density — Stats and Quotes Over Vague Claims"
description: "How replacing qualitative claims with specific statistics, attributed quotes, and cited sources increases AI citation rates by 30–41%."
term: "Assertion Density"
tags:
  - geo
  - technique
  - workflows
  - tool-agnostic
last_reviewed: 2026-05-27
maturity: adopted
---

# Assertion Density — Stats and Quotes Over Vague Claims

> Replace vague qualifiers with specific numbers, dates, sample sizes, and attributed quotes. The Princeton GEO study found this is the highest-impact single rewrite technique for AI citation rates — up to 41% improvement in source visibility.

Learn it hands-on with the [Assertion Density guided lesson and quizzes](https://learn.agentpatterns.ai/geo/assertion-density/).

## Why specificity gets cited

AI answer engines use retrieval-augmented generation: they match queries against indexed content and generate answers from retrieved passages. Specific claims improve retrieval in two ways:

1. Token-level matching — a query for "how much does X improve Y" matches numeric passages more precisely than "significantly" or "substantially"
2. Attribution confidence — attributed quotes with named credentials and dated statistics are easier to cite verbatim than generalities

## The evidence

The Princeton GEO study (Aggarwal et al., [KDD 2024](https://arxiv.org/abs/2311.09735)) tested 9 optimization techniques against a 10,000-query benchmark (GEO-bench) across 25 domains. It measured source visibility using Position-Adjusted Word Count (PAWC — word count weighted by exponential decay based on citation position):

| Technique | PAWC Improvement |
|-----------|-----------------|
| Quotation Addition | +41% |
| Statistics Addition | +30% |
| Cite Sources | +30% |
| Fluency Optimization | +15–30% |
| Keyword Stuffing | –10% |

Caveats: all three top techniques add content rather than modifying it, and PAWC rewards length, so content-addition techniques gain a structural advantage. The study permitted fabricated statistics, which limits real-world applicability (see [Sandbox SEO's critique of the methodology](https://sandboxseo.com/generative-engine-optimization-experiment/)). The directional finding (specific over vague) holds; the exact percentages are an upper bound.

## What counts

Strong assertions (retrieval-friendly):

- Specific numbers with units: "reduces latency by 23ms at p99"
- Named sources with credentials: "according to Martin Fowler, author of 'Refactoring'"
- Dated research: "a 2024 Stanford study of 1,200 developers found..."
- Sample sizes: "across 10,000 queries in 25 domains"
- Bounded ranges: "8–12 citations per 1,500 words"

Weak assertions (retrieval-unfriendly):

- Vague quantifiers: "many", "often", "most", "significantly"
- Unattributed authority: "experts say", "research shows", "it is widely known"
- Relative comparisons without anchors: "much faster", "far more accurate"
- Undated generalizations: "historically", "in recent years"

## Rewrite guide

Find vague qualifiers and replace with specifics. If no source exists for a claim, weaken it to a factually-supportable form or remove it — do not invent statistics or use hedge tags.

| Before | After |
|--------|-------|
| "Context priming significantly improves output quality." | "Context priming reduces rework — agents that read relevant files before implementing produce output that matches existing conventions, because the retrieved context constrains generation to existing patterns." |
| "Most developers use AI coding assistants." | "75% of developers surveyed by GitHub in 2024 reported using AI coding tools at least weekly." |
| "Keyword stuffing is counterproductive." | "Keyword stuffing reduced source visibility by 10% in the Princeton GEO benchmark (Aggarwal et al., KDD 2024)." |
| "Large context windows help with complex tasks." | "Claude 3.5 Sonnet supports a 200K-token context window, sufficient to load an entire mid-size codebase before implementing." |

## Unsourceable claims

If a claim cannot be backed by a real source, rewrite it in a weaker factually-supportable form or remove it entirely. Hedge tags produce a false-confidence signal without adding retrieval value — the GEO study found PAWC rewards length and attributed specificity, not vague generalities.

## Limits

- Fabrication risk: manufactured statistics are detectable, so only add specifics you can source
- Structural prerequisites: if the page buries answers (see [Answer-First Writing](answer-first-writing.md)), assertion density cannot compensate for a retrieval miss at the section level
- Diminishing returns: past a threshold, additional citations add length without citability

## Recency and assertion density

Content freshness and assertion density are independent citation signals — improving one does not substitute for the other. See [Measuring GEO Performance](measuring-geo-performance.md) for tracking both.

## FAQ

**Why do specific stats and attributed quotes get cited more often than vague claims?**

AI answer engines retrieve passages by matching queries against indexed content, so specificity helps in two ways. Token-level matching favors numeric passages over words like "significantly," and attribution confidence makes named, dated, sourced claims easier to cite verbatim than generalities. Vague qualifiers such as "many" or "often" give retrieval systems nothing precise to match.

**How much do quotations and statistics improve AI citation rates, according to the Princeton GEO study?**

The Princeton GEO study (Aggarwal et al., [KDD 2024](https://arxiv.org/abs/2311.09735)) found Quotation Addition improved source visibility by 41%, and Statistics Addition and Cite Sources each improved it by 30%. It measured these results via Position-Adjusted Word Count across a 10,000-query benchmark. Because the study permitted fabricated statistics and rewards added length, treat these percentages as an upper bound.

**What should I do if I cannot find a real source for a claim?**

Weaken the claim to a form you can factually support, or remove it entirely — do not invent statistics or add a hedge tag. Hedge tags create a false-confidence signal without adding retrieval value: the GEO study found PAWC rewards length and attributed specificity, not vague generalities dressed up with a disclaimer.

**Does adding more citations always make a page more citable?**

No — assertion density has diminishing returns and a structural prerequisite. Past a certain threshold, additional citations add length without improving citability. If a page buries its answers rather than leading with them, added specificity cannot compensate for a retrieval miss at the section level. Fix structure first, then increase density.

## Related

- [Answer-First Writing](answer-first-writing.md)
- [Atomic Pages and Chunking](atomic-pages-and-chunking.md)
- [How AI Engines Cite](how-ai-engines-cite.md)
- [Measuring GEO Performance](measuring-geo-performance.md)
- [Schema and Structured Data for GEO](schema-and-structured-data.md)
- [SEO vs GEO](seo-vs-geo.md)
- [GEO for Technical Docs](geo-for-technical-docs.md)
- [Topical Authority](topical-authority.md)
- [What is GEO](what-is-geo.md)
- [Context Priming for AI Agent Development](../context-engineering/context-priming.md)
