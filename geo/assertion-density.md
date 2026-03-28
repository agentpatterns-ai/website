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

AI answer engines use retrieval-augmented generation: they match queries against indexed content and generate answers from retrieved passages. Specific, verifiable claims improve retrieval in two ways:

1. **Token-level matching** — a query for “how much does X improve Y” matches numeric passages more precisely than passages with “significantly” or “substantially”
2. **Attribution confidence** — attributed quotes with named credentials and dated statistics are easier to cite verbatim than paraphrased generalities

## The Evidence

The Princeton GEO study (Aggarwal et al., [KDD 2024](https://arxiv.org/abs/2311.09735)) tested 9 optimization techniques against a 10,000-query benchmark (GEO-bench) across 25 content domains, measuring source visibility using Position-Adjusted Word Count (PAWC — word count weighted by exponential decay based on citation position):

| Technique | PAWC Improvement |
|-----------|-----------------|
| Quotation Addition | +41% |
| Statistics Addition | +40% |
| Cite Sources | +30% |
| Fluency Optimization | +15–30% |
| Keyword Stuffing | –10% |

**Caveats**: All three top techniques add content, not just modify it — the PAWC metric rewards length, giving content-addition techniques a structural advantage. The study permitted fabricated statistics, limiting real-world applicability. The directional finding — specific over vague — is robust; exact percentages are an upper bound. Domain variation is real: no single technique dominates universally.

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

## Relationship to This Site's `[unverified]` Convention

- A claim tagged `[unverified]` is a retrieval liability — AI engines are less likely to cite it because they cannot verify attribution `[unverified]`
- Find a source and cite it, or keep the `[unverified]` tag to signal the gap explicitly
- Removing the tag without adding a source creates a false confidence signal that is worse than the original

## Limits

- **Freshness**: content recency is a separate citation signal. High assertion density on a stale page may still underperform a fresher page with weaker assertions. `[unverified — secondary GEO guides cite a recency majority-of-citations claim without a confirmed primary source]`
- **Fabrication risk**: manufactured statistics are detectable; only add specifics you can source
- **Structural prerequisites**: if the page buries answers (see [Answer-First Writing](answer-first-writing.md)), assertion density in the body won't compensate for a retrieval miss at the section level
- **Diminishing returns**: beyond a threshold, additional citations add length without adding citability; keep the page scannable

## Unverified Claims

- Content recency is a dominant signal for AI citation — secondary GEO practitioner guides cite a "majority from recently updated content" finding without a confirmed primary source `[unverified]`
- LLMs increasingly detect hallucinated citations and may penalise sources that use them — directionally plausible but no primary study confirmed `[unverified]`

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
