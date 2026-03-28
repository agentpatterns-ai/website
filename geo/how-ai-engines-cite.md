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

Every major platform runs separate crawlers for model training and real-time citation. Blocking the wrong bot has no effect on citation behavior ([Momentic AI Crawlers Guide](https://momenticmarketing.com/blog/ai-search-crawlers-bots)).

| Platform | Training bot | Retrieval bot | On-demand bot |
|----------|-------------|---------------|---------------|
| OpenAI | `GPTBot` | `OAI-SearchBot` | `ChatGPT-User` |
| Anthropic | `anthropic-ai`, `ClaudeBot` | `Claude-SearchBot` | `Claude-User` |
| Perplexity | `PerplexityBot` | `PerplexityBot` | `Perplexity-User` |
| Google | `Google-Extended` (opt-out) | `Googlebot` | — |

To appear in AI-generated answers while blocking training crawls, allow the retrieval bot and block the training bot in `robots.txt`. Retrieval bots: `OAI-SearchBot`, `Claude-SearchBot`, `PerplexityBot`, `Googlebot`.

69% of AI crawlers cannot render JavaScript — only Googlebot, Applebot, and Bingbot execute JS. All OpenAI and Perplexity crawlers see raw HTML only. Server-side rendering is mandatory for indexing by these platforms. [unverified]

## Platform Retrieval Architectures

### ChatGPT — Bing-backed RAG

- Routes through Bing's index when web search activates — only **31% of prompts trigger live retrieval** ([Whitehat SEO](https://whitehat-seo.co.uk/blog/ai-engines-comparison-citations))
- ChatGPT citations match Bing's top-10 results **87% of the time** [unverified]
- **90% of ChatGPT-cited pages rank position 21 or lower on Google** [unverified]
- **4.8% dependent on Wikipedia**; no other major platform cites Wikipedia at meaningful rates ([Qwairy Q3 2025](https://www.qwairy.co/blog/provider-citation-behavior-q3-2025))
- Citations average **7.92 per response** [unverified]

### Claude — Brave Search backend

- Routes through Brave Search: **86.7% overlap** between Claude citations and Brave's top non-sponsored results ([TechCrunch, 2025](https://techcrunch.com/2025/03/21/anthropic-appears-to-be-using-brave-to-power-web-searches-for-its-claude-chatbot/))
- Prioritizes high factual density: specific data points, named sources, verifiable statistics [unverified]
- Uses `Claude-SearchBot` for index crawling; `Claude-User` for on-demand fetches

### Perplexity — retrieval-first, always

- Runs its own index of **200+ billion URLs** [unverified]; real-time search fires on every query without exception
- **21.87 citations per response** — 2.8x more than ChatGPT ([Qwairy Q3 2025](https://www.qwairy.co/blog/provider-citation-behavior-q3-2025))
- Strongest freshness weighting: **82% citation rate for content under 30 days old**, 37% for older content [unverified]
- Favors specialized vertical content; niche sources: 24% of citations on subjective queries [unverified]
- Reddit is a top domain (46.7%); community-generated content is a primary signal [unverified]

### Gemini — Google AI Overviews

- Draws from Google's own index and Knowledge Graph (500 billion facts) — no external backend [unverified]
- **52.15% of Gemini citations come from brand-owned websites** — highest brand preference of any platform [unverified]
- Multimodal content (text + images + video) gets **156% higher citation rates** than text-only pages [unverified]
- Google AI Overviews now appear in more than 60% of searches [unverified]
- Citation placement averages later in responses (position 10.08 vs ChatGPT's 2.82) [unverified]

## Citation Volume by Platform

| Platform | Citations per response | Unique source domains |
|----------|----------------------|-----------------------|
| Perplexity | 21.87 | 37,399 |
| Google AI Overviews | 17.93 | 25,785 |
| ChatGPT | 7.92 | 42,592 |
| Microsoft Copilot | 2.47 | 111 |

## What Drives Citation Across All Platforms

- **Brand search volume** — strongest cross-platform predictor (0.334 correlation), outperforming backlink metrics ([The Digital Bloom, 2025](https://thedigitalbloom.com/learn/2025-ai-citation-llm-visibility-report/))
- **Content freshness** — 65% of AI bot traffic targets content under one year old; 79% under two years [unverified]
- **Embedded citations and statistics** — adding citations to content produced a 115.1% visibility increase for rank-5 sites; statistics +22%, quotations +37% [unverified]
- **Factual density** — specific claims, named sources, verifiable data [unverified]
- **Multi-platform presence** — sites cited on 4 or more platforms are 2.8x more likely to appear in ChatGPT responses [unverified]

## Key Takeaways

- Allow retrieval bots, block training bots in `robots.txt` — each platform uses separate user-agent strings
- Four backends: Bing (ChatGPT), Brave (Claude), own index (Perplexity), Google (Gemini)
- Server-side rendering is mandatory; 69% of AI crawlers cannot execute JavaScript [unverified]
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
