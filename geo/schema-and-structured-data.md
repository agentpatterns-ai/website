---
title: "Schema and Structured Data for GEO — AI Citation Guide"
description: "FAQPage JSON-LD yields a 2.7x citation lift in AI responses. Implementation guide for FAQPage, HowTo, and DefinedTerm schema in MkDocs Material."
tags:
  - geo
  - workflows
aliases:
  - Schema Markup
  - Structured Data for GEO
  - JSON-LD for AI
---

# Schema Markup for AI Citation

> FAQPage schema yields a 2.7x citation lift in AI responses (41% vs. 15% without markup) [unverified]. Structured data pre-packages content in the same Q&A and step formats AI uses to generate answers, reducing extraction effort during indexing.

Schema markup's primary value has shifted from SEO to AI search citation — ChatGPT, Perplexity, Gemini, and Claude all process schema during indexing. This site auto-injects FAQPage, HowTo, and Article schemas via the `docs/hooks/structured_data.py` hook.

## What Changed: Google vs. AI Search

| Channel | FAQPage / HowTo Rich Results | Schema Citation Value |
|---------|------------------------------|-----------------------|
| Google Search (classic) | Restricted to government/health sites since Aug 2023 | Low for most dev docs |
| Google AI Overviews | Processed at index time | High — 3.2x appearance lift (Frase.io) |
| ChatGPT | Not rendered live; indexed content used | High — favours Q&A format |
| Perplexity | Indexed schema aids entity disambiguation | High — citation footnotes |
| Gemini | Renders JavaScript; processes schema | High |

**Key nuance**: AI chatbots do not read JSON-LD during live page fetches — the citation benefit comes from schema's role in the indexing and training pipeline.

## The Three Schema Types

### FAQPage

Structures Q&A blocks for direct AI extraction. Answers should be 40–80 words — standalone, citable length for AI response units.

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "What is an agent harness?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "An agent harness is scaffolding that surrounds an AI agent loop — managing context, tool calls, error recovery, and output formatting. It separates infrastructure concerns from reasoning logic."
    }
  }]
}
```

The `structured_data.py` hook detects `## FAQ` or `## Frequently Asked Questions` followed by `**Question**` / answer pairs and auto-generates this schema.

### HowTo

Converts numbered step lists into extractable content blocks. Each step becomes a quotable unit.

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How to configure prompt caching",
  "step": [
    { "@type": "HowToStep", "position": 1, "text": "Enable the caching header in your API request." },
    { "@type": "HowToStep", "position": 2, "text": "Place stable content at the top of the context window." }
  ]
}
```

The hook auto-detects ordered lists (`<ol>`) with three or more items, but only on pages under `patterns/` or `techniques/` paths. To enable HowTo on `geo/` pages, extend `_HOWTO_PATHS` in `docs/hooks/structured_data.py`.

### DefinedTerm

Establishes machine-readable definitions for named concepts — useful where terms like "agent" and "context window" are ambiguous across tools.

```json
{
  "@context": "https://schema.org",
  "@type": "DefinedTermSet",
  "@id": "https://agentpatterns.ai/concepts#",
  "name": "Agent Patterns Glossary",
  "hasDefinedTerm": [
    {
      "@type": "DefinedTerm",
      "@id": "https://agentpatterns.ai/concepts#agent-harness",
      "termCode": "AP-001",
      "name": "Agent Harness",
      "description": "Scaffolding that surrounds an agent loop, managing context, tool calls, error recovery, and output formatting.",
      "inDefinedTermSet": "https://agentpatterns.ai/concepts#"
    }
  ]
}
```

Each term's `@id` fragment is directly linkable — AI knowledge graphs can reference it as an authoritative definition.

## How This Site Generates Schema

The `docs/hooks/structured_data.py` MkDocs hook runs at `on_post_page` and injects JSON-LD into every page's `<head>`:

```mermaid
graph LR
    A[MkDocs builds page] --> B[on_post_page hook fires]
    B --> C[Organization schema]
    B --> D{Is homepage?}
    D -- yes --> E[WebSite schema]
    B --> F[Article schema]
    B --> G[BreadcrumbList schema]
    B --> H{FAQ heading detected?}
    H -- yes --> I[FAQPage schema]
    B --> J{Ordered list 3+ steps and patterns/ or techniques/ path?}
    J -- yes --> K[HowTo schema]
    C & E & F & G & I & K --> L[Inject before head close]
```

No per-page config required — add an FAQ section and the schema appears automatically.

## Writing for Schema Auto-Detection

### FAQ Section

The hook matches `## FAQ` or `## Frequently Asked Questions` followed by `**Question text**` / paragraph pairs:

```markdown
## FAQ

**What is an agent harness?**

An agent harness is the scaffolding that surrounds an AI agent loop — managing
context, tool calls, error recovery, and output formatting. It separates
infrastructure concerns from the agent's reasoning logic.

**When should I use HowTo schema?**

Use HowTo schema for step-by-step instructional content where each step is a
discrete, independently meaningful action. Avoid it for conceptual explanations
that happen to have numbered sections.
```

### HowTo Steps

Steps should be self-contained sentences — each is extracted as a standalone `HowToStep.text`. Auto-injection applies only to `patterns/` or `techniques/` paths.

## Testing Schema

| Tool | Purpose | URL |
|------|---------|-----|
| Google Rich Results Test | Validates Google-supported rich results (Article, BreadcrumbList) | https://search.google.com/test/rich-results |
| Schema Markup Validator | Validates all schema.org types without Google restrictions | https://validator.schema.org/ |
| [Google Search Console](../workflows/gsc-search-console-monitoring.md) | Monitors rich result impressions and errors post-deployment | https://search.google.com/search-console |

Run locally:

```bash
mkdocs build --strict
# Copy a built page's head block into the Schema Markup Validator
```

## Sources

- [FAQPage Structured Data — Google Search Central](https://developers.google.com/search/docs/appearance/structured-data/faqpage) — required properties, content guidelines, eligibility restrictions
- [DefinedTerm — Schema.org](https://schema.org/DefinedTerm) — official spec: name, termCode, description, inDefinedTermSet
- [Using Schema.org's DefinedTermSet for Industry Terminology — DEV Community](https://dev.to/mark_mcneece_365i/using-schemaorgs-definedtermset-for-industry-terminology-a-case-study-1mm2) — fragment @id, bidirectional TermSet linking
- [Schema.org Is Your Secret Weapon for AI Citations — DEV Community](https://dev.to/wilow445/schemaorg-is-your-secret-weapon-for-ai-citations-heres-the-data-1if3) — citation rate data: FAQPage +45%, HowTo +38%
- [FAQ Schema for AI Search, GEO and AEO — Frase.io](https://www.frase.io/blog/faq-schema-ai-search-geo-aeo) — 3.2x AI Overview appearance lift, platform citation patterns
- [Schema Markup and AI in 2025 — Searchviu](https://www.searchviu.com/en/schema-markup-and-ai-in-2025-what-chatgpt-claude-perplexity-gemini-really-see/) — JSON-LD ignored during direct chatbot fetch; benefits accrue at indexing
- [How to Use Structured Data in MkDocs](https://v-schipka.github.io/posts/schema-in-mkdocs/) — MkDocs Material extrahead block and frontmatter template approach
- [Structured Data for SEO and GEO — Digidop](https://www.digidop.com/blog/structured-data-secret-weapon-seo) — GPT-4 accuracy: 16% to 54% on structured-data-backed content

## Related

- [GEO for Technical Docs](geo-for-technical-docs.md) — schema type selection checklist and per-format GEO priorities
- [How AI Engines Cite](how-ai-engines-cite.md) — citation mechanisms schema markup targets
- [Answer-First Writing](answer-first-writing.md) — content structure that complements schema auto-detection
- [SEO vs GEO](seo-vs-geo.md) — how structured data signals differ between traditional SEO and AI citation optimization
- [llms.txt](llms-txt.md) — complementary machine-readable format for AI discoverability
- [AI Crawler Policy](ai-crawler-policy.md) — controlling which crawlers index your structured data
- [Measuring GEO Performance](measuring-geo-performance.md) — tracking schema citation lift
- [What Is GEO](what-is-geo.md) — foundational concepts behind generative engine optimization

## Unverified Claims

- The 41% vs. 15% citation rate numbers originate from the referenced GEO research sources; the primary source (eseospace.com) returned 403 during research. The figure is corroborated at similar magnitudes by multiple independent studies. `[unverified]`
