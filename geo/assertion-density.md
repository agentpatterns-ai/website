---
title: "Assertion Density — Stats and Quotes Over Vague Claims"
description: "How replacing qualitative claims with specific statistics, attributed quotes, and cited sources increases AI citation rates by 30–41%."
tags:
  - geo
  - technique
  - workflows
---

# Assertion Density

> Replace vague qualifiers with specific numbers, dates, sample sizes, and attributed quotes. The Princeton GEO study found this is the highest-impact single rewrite technique for AI citation rates — up to 40–41% improvement in source visibility.

## Why Specificity Gets Cited

AI answer engines use retrieval-augmented generation: they match queries against indexed content and generate answers from retrieved passages. Specific claims improve retrieval in two ways:

1. **Token-level matching** — a query for "how much does X improve Y" matches numeric passages more precisely than "significantly" or "substantially"
2. **Attribution confidence** — attributed quotes with named credentials and dated statistics are easier to cite verbatim than generalities

## The Evidence

The Princeton GEO study (Aggarwal et al., [KDD 2024](https://arxiv.org/abs/2311.09735)) tested 9 optimization techniques against a 10,000-query benchmark (GEO-bench) across 25 domains, measuring source visibility using Position-Adjusted Word Count (PAWC — word count weighted by exponential decay based on citation position):

| Technique | PAWC Improvement |
|-----------|-----------------|
| Quotation Addition | +41% |
| Statistics Addition | +40% |
| Cite Sources | +30% |
| Fluency Optimization | +15–30% |
| Keyword Stuffing | –10% |

**Caveats**: All three top techniques add content rather than modifying it — PAWC rewards length, giving content-addition techniques a structural advantage. The study permitted fabricated statistics, limiting real-world applicability. The directional finding — specific over vague — is robust; exact percentages are an upper bound.

## What Counts

**Strong assertions** (retrieval-friendly):

- Specific numbers with units: "reduces latency by 23ms at p99"
- Named sources with credentials: "according to Martin Fowler, author of *Refactoring*"
- Dated research: "a 2024 Stanford study of 1,200 developers found..."
- Sample sizes: "across 10,000 queries in 25 domains"
- Bounded ranges: "8–12 citations per 1,500 words"

**Weak assertions** (retrieval-unfriendly):

- Vague quantifiers: "many", "often", "most", "significantly"
- Unattributed authority: "experts say", "research shows", "it is widely known"
- Relative comparisons without anchors: "much faster", "far more accurate"
- Undated generalizations: "historically", "in recent years"

## Rewrite Guide

Find vague qualifiers and replace with specifics. If you don't have a source, tag with `[unverified]` rather than inventing one.

| Before | After |
|--------|-------|
| "Context priming significantly improves output quality." | "Context priming reduces rework — agents that read relevant files before implementing produce output that matches existing conventions without manual correction. `[unverified]`" |
| "Most developers use AI coding assistants." | "75% of developers surveyed by GitHub in 2024 reported using AI coding tools at least weekly." |
| "Keyword stuffing is counterproductive." | "Keyword stuffing reduced source visibility by 10% in the Princeton GEO benchmark (Aggarwal et al., KDD 2024)." |
| "Large context windows help with complex tasks." | "Claude 3.5 Sonnet supports a 200K-token context window, sufficient to load an entire mid-size codebase before implementing." |

## The `[unverified]` Convention

- `[unverified]` claims are retrieval liabilities — the GEO study found that PAWC rewards length and attributed specificity, not vague generalities; unverifiable assertions offer neither
- Find a source and cite it, or keep the tag to signal the gap
- Removing the tag without adding a source creates a worse false confidence signal

## Limits

- **Fabrication risk**: manufactured statistics are detectable; only add specifics you can source
- **Structural prerequisites**: if the page buries answers (see [Answer-First Writing](answer-first-writing.md)), assertion density won't compensate for a retrieval miss at the section level
- **Diminishing returns**: past a threshold, additional citations add length without citability

## Recency and Assertion Density

Content freshness and assertion density are independent citation signals — improving one does not substitute for the other. See [Measuring GEO Performance](measuring-geo-performance.md) for tracking both.

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
