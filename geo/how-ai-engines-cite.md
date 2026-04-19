---
title: "How AI Engines Cite — ChatGPT, Perplexity, Claude, Gemini"
description: "Platform-by-platform breakdown of how the major AI answer engines retrieve, evaluate, and select their sources for citation."
tags:
  - geo
  - technique
  - tool-agnostic
  - workflows
aliases:
  - "AI citation behavior"
  - "how LLMs cite sources"
  - "AI engine citation mechanics"
---

# How AI Engines Cite

> The four major AI answer engines are four entirely different retrieval systems. Optimizing for one does not transfer to another.

Only **11% of cited domains appear on both ChatGPT and Perplexity** for identical queries ([Whitehat SEO, 2025](https://whitehat-seo.co.uk/blog/ai-engines-comparison-citations)). Each platform runs a different search backend, applies different freshness weights, and uses a different crawler. Understand which engine you are targeting before optimizing.

## The Crawler Split: Training vs Retrieval

Every major platform runs separate crawlers for training and real-time citation. Blocking the wrong bot has no effect on citation behavior ([Momentic AI Crawlers Guide](https://momenticmarketing.com/blog/ai-search-crawlers-bots)).

| Platform | Training bot | Retrieval bot | On-demand bot |
|----------|-------------|---------------|---------------|
| OpenAI | `GPTBot` | `OAI-SearchBot` | `ChatGPT-User` |
| Anthropic | `anthropic-ai`, `ClaudeBot` | `Claude-SearchBot` | `Claude-User` |
| Perplexity | `PerplexityBot` | `PerplexityBot` | `Perplexity-User` |
| Google | `Google-Extended` (opt-out) | `Googlebot` | — |

To appear in AI answers while blocking training crawls, allow the retrieval bot and block the training bot in `robots.txt`. Retrieval bots: `OAI-SearchBot`, `Claude-SearchBot`, `PerplexityBot`, `Googlebot`.

Most AI crawlers cannot render JavaScript — only Googlebot, Applebot, and Bingbot execute JS. OpenAI and Perplexity crawlers see raw HTML only. Server-side rendering is mandatory ([Momentic AI Crawlers Guide](https://momenticmarketing.com/blog/ai-search-crawlers-bots)).

## Platform Retrieval Architectures

### ChatGPT — Bing-backed RAG

- Routes through Bing's index when web search activates — only **31% of prompts trigger live retrieval** ([Whitehat SEO](https://whitehat-seo.co.uk/blog/ai-engines-comparison-citations))
- ChatGPT citations closely track Bing's top-10 results; pages that rank highly on Bing are far more likely to be cited ([Whitehat SEO](https://whitehat-seo.co.uk/blog/ai-engines-comparison-citations))
- **4.8% dependent on Wikipedia**; no other major platform cites Wikipedia at meaningful rates ([Qwairy Q3 2025](https://www.qwairy.co/blog/provider-citation-behavior-q3-2025))
- Citations average **7.92 per response** ([Qwairy Q3 2025](https://www.qwairy.co/blog/provider-citation-behavior-q3-2025))

### Claude — Brave Search backend

- Routes through Brave Search: **86.7% overlap** between Claude citations and Brave's top non-sponsored results ([TechCrunch, 2025](https://techcrunch.com/2025/03/21/anthropic-appears-to-be-using-brave-to-power-web-searches-for-its-claude-chatbot/))
- Prioritizes high factual density: specific data points, named sources, verifiable statistics; uses `Claude-SearchBot` for index crawling and `Claude-User` for on-demand fetches

### Perplexity — retrieval-first, always

- Runs its own large-scale index; real-time search fires on every query without exception
- **21.87 citations per response** — 2.8x more than ChatGPT ([Qwairy Q3 2025](https://www.qwairy.co/blog/provider-citation-behavior-q3-2025))
- Strongest freshness weighting of any major platform; recent content is heavily favored over older material ([Metrics Rule, 2026](https://www.metricsrule.com/research/rag-author-markup-publication-date-citations/))
- Favors niche and community-generated sources at higher rates than other platforms ([Qwairy Q3 2025](https://www.qwairy.co/blog/provider-citation-behavior-q3-2025))

### Gemini — Google AI Overviews

- Draws from Google's own index and Knowledge Graph — no external backend
- **52.15% of Gemini citations come from brand-owned websites** — highest brand preference of any platform ([Qwairy Q3 2025](https://www.qwairy.co/blog/provider-citation-behavior-q3-2025))
- Multimodal content (text + images + video) receives higher citation rates than text-only pages ([ConvertMate Gemini Visibility Study](https://www.convertmate.io/research/gemini-visibility))
- Citation placement averages later in responses than ChatGPT ([Qwairy Q3 2025](https://www.qwairy.co/blog/provider-citation-behavior-q3-2025))

## Citation Volume by Platform

| Platform | Citations per response | Unique source domains |
|----------|----------------------|-----------------------|
| Perplexity | 21.87 | 37,399 |
| Google AI Overviews | 17.93 | 25,785 |
| ChatGPT | 7.92 | 42,592 |
| Microsoft Copilot | 2.47 | 111 |

## What Drives Citation Across All Platforms

- **Brand search volume** — strongest cross-platform predictor (0.334 correlation), outperforming backlink metrics ([The Digital Bloom, 2025](https://thedigitalbloom.com/learn/2025-ai-citation-llm-visibility-report/))
- **Content freshness** — AI bots heavily target recent content; older pages drop off across all platforms
- **Embedded citations and statistics** — adding citations and quotations increases AI visibility, with mid-ranked sites seeing the largest gains ([The Digital Bloom, 2025](https://thedigitalbloom.com/learn/2025-ai-citation-llm-visibility-report/))
- **Factual density** — specific claims, named sources, verifiable data
- **Multi-platform presence** — strong cross-platform citation presence compounds ([The Digital Bloom, 2025](https://thedigitalbloom.com/learn/2025-ai-citation-llm-visibility-report/))

## Why Citation Behavior Differs

Citation profiles follow retrieval architecture. ChatGPT inherits Bing ranking signals. Claude inherits Brave's bias toward factual content and away from ad-heavy domains. Perplexity's short-TTL crawler makes freshness the primary signal. Gemini filters through Google's Knowledge Graph, where brand authority (E-E-A-T) dominates. Signals do not transfer because the ranking mechanisms differ structurally.

## When This Backfires

1. **Backend changes invalidate the tactic.** Claude's shift to Brave Search changed its citation profile overnight. Any optimization tied to a specific backend can become stale without warning.
2. **Freshness optimization conflicts with depth.** Perplexity rewards short-cycle publishing; ChatGPT and Gemini weight authority. Publishing shallow content frequently to win Perplexity citations can suppress performance elsewhere.
3. **Over-specialization reduces cross-platform citation.** The 11% domain overlap between ChatGPT and Perplexity means winning both requires different content architecture, not the same page with minor tweaks.

## Key Takeaways

- Allow retrieval bots, block training bots in `robots.txt` — each platform uses separate user-agent strings
- Four backends: Bing (ChatGPT), Brave (Claude), own index (Perplexity), Google (Gemini)
- Server-side rendering is mandatory; most AI crawlers cannot execute JavaScript ([Momentic AI Crawlers Guide](https://momenticmarketing.com/blog/ai-search-crawlers-bots))
- Brand search volume is the strongest cross-platform citation predictor

## Related

- [AI Crawler Policy](ai-crawler-policy.md)
- [Atomic Pages and Chunking](atomic-pages-and-chunking.md)
- [Answer-First Writing](answer-first-writing.md)
- [Assertion Density](assertion-density.md)
- [SEO vs GEO](seo-vs-geo.md)
- [Topical Authority](topical-authority.md)
- [llms.txt](llms-txt.md)
- [Measuring GEO Performance](measuring-geo-performance.md)
- [Schema Markup for AI Citation](schema-and-structured-data.md)
- [GEO for Technical Docs](geo-for-technical-docs.md)
- [What Is GEO](what-is-geo.md)
