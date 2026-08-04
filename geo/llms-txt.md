---
title: "llms.txt: Full Specification, Adoption, and Limitations"
term: "llms.txt"
description: "The llms.txt specification gives AI agents a curated index of your site — it improves agentic comprehension but is not a citation or ranking signal."
tags:
  - geo
  - technique
  - tool-agnostic
  - workflows
last_reviewed: 2026-07-20
maturity: emerging
---

# llms.txt: Spec, Adoption, and Honest Limitations

> `/llms.txt` gives AI agents a curated entry point to your site at inference time — it improves agent navigation, not citation rates or search rankings.

Learn it hands-on with [Machine-Readable Corpora](https://learn.agentpatterns.ai/geo/machine-readable-corpora/) — a guided lesson with quizzes.

## What the spec specifies

The [llms.txt specification](https://llmstxt.org) (Jeremy Howard, answer.ai) defines a Markdown file published at `{site-root}/llms.txt`. LLM context windows are too small to process full websites, and HTML adds noise. The file gives agents a curated, structured index instead.

The spec defines exactly one required element:

| Element | Required? | Purpose |
|---------|-----------|---------|
| H1 heading (project/site name) | Yes | Only mandatory element |
| Blockquote summary | No | Brief description of the project |
| H2-delimited sections | No | Curated link lists by topic |
| `## Optional` section | No | Content skippable under context pressure |

```markdown
# Project Name

> One-sentence summary of what this is and who it is for.

## Documentation

- [Getting Started](/docs/start): First steps for new users
- [API Reference](/docs/api): Complete API documentation

## Optional

- [Changelog](/changelog): Version history
```

File lists use `[name](url)` with an optional colon-prefixed description. Content under `## Optional` signals material agents can skip under context pressure.

## How agents use it

Per the spec's intended usage model ([llmstxt.org](https://llmstxt.org)), an agent researching a site fetches `/llms.txt` first. The structured index replaces undirected crawling with a single fetch and a curated list:

1. Fetch `{site}/llms.txt`.
2. Identify the relevant section.
3. Fetch only the linked pages that apply to the task.

A companion convention, not in the formal spec, is to also publish `/llms-full.txt`. This file concatenates all linked pages into one, so an agent gets full site context in a single fetch. It removes the multi-step index-then-fetch pattern when an agent needs complete site context.

## Why it works

LLM context windows set a hard ceiling on how much a site can serve an agent in one request. Undirected crawling wastes tokens: agents fetch pages that turn out to be irrelevant, then discard them. `llms.txt` moves the selection step outside the inference call. A human editor curates the index once, and every agent invocation starts with a pre-filtered list. The agent then spends its context budget on content, not discovery. The `## Optional` convention extends this. Under context pressure, agents can drop entire sections without losing the core index, so the author controls what survives the cut ([llmstxt.org](https://llmstxt.org)).

## What it is not

- Not a robots.txt replacement: `robots.txt` controls crawler access; `llms.txt` guides inference-time navigation.
- Not a sitemap alternative: sitemaps cover all crawlable URLs, too many to fit in a context window with no curation. `llms.txt` is a curated editorial index.
- Not a training data submission: the spec is for inference-time use. It has no defined role in model training pipelines.

## The citation limitation

`llms.txt` is infrastructure for agentic navigation, not a GEO ranking signal. The first measurement-grade evidence confirms it: an [Ahrefs June 2026 server-log study](https://ahrefs.com/blog/llmstxt-study/) of 137,000 domains found that 97% of `llms.txt` files received zero requests in May 2026. Of the requests that did arrive, SEO audit tools led at 21.7%; among named AI agents, GPTBot accounted for 4.51% of file requests and ClaudeBot 0.80%.

- No major AI provider (Anthropic, OpenAI, Google) has published documentation confirming they read `llms.txt` at inference time. Vendor claims that Anthropic or Perplexity "confirmed `llms.txt` support" remain uncorroborated by platform docs and are contradicted by the log data ([Ahrefs](https://ahrefs.com/blog/llmstxt-study/)).
- The spec itself frames the format as inference-time tooling with no defined role in training or citation pipelines ([llmstxt.org](https://llmstxt.org))
- Citation signals are dominated by content authority, structured data, and entity recognition — not file conventions ([How AI Engines Cite](how-ai-engines-cite.md))

### The real audience is coding agents

The log data shifts the honest use case. `claude-code` was the #2 named AI fetcher of `llms.txt` in the Ahrefs study, so the file's real consumers are coding agents, not answer engines ([Ahrefs](https://ahrefs.com/blog/llmstxt-study/)). For a developer-facing site, that is a genuine audience: an agent working in a codebase can fetch your curated index to navigate your docs. That value is real, but it is separate from search ranking or citation in answer engines, and should not be confused with either.

## Real adoption examples

| Site | Implementation note |
|------|---------------------|
| [docs.github.com/llms.txt](https://docs.github.com/llms.txt) | API-first format — exposes endpoints for agents to discover pages programmatically |
| [cursor.com/llms.txt](https://cursor.com/llms.txt) | Full docs structure including 10-language internationalization |
| Anthropic platform | Developer Guide, API Reference, and SDKs — auto-generated via Mintlify hosting |

[Mintlify's November 2024 rollout](https://www.mintlify.com/blog/what-is-llms-txt) auto-generated `llms.txt` across all hosted documentation sites and spread the format quickly. Sites on Mintlify's platform, including Anthropic and Cursor, received `llms.txt` without manual effort.

Adoption keeps climbing even though the files go largely unread: publication grew 8.8x in 12 months (4,088 to 36,120 files across 3 million monitored sites), yet only 7.4% of the Fortune 500 publish one ([PPC Land](https://ppc.land/only-7-4-of-fortune-500-have-an-llms-txt-file-study-finds/)). The gap between fast adoption and near-zero consumption is the practical reason to publish for navigation utility, not for ranking.

## Example

A minimal `llms.txt` for a documentation site:

```markdown
# Acme Docs

> Developer documentation for the Acme platform — REST API, SDKs, and tutorials.

## Core Documentation

- [Quick Start](/docs/quickstart): First app in 5 minutes
- [API Reference](/docs/api): Full endpoint reference
- [Authentication](/docs/auth): API key and OAuth flows

## Optional

- [Changelog](/changelog): Release notes
- [Migration Guides](/docs/migrations): Upgrading between major versions
```

Publish an accompanying `/llms-full.txt` with the concatenated text of all linked pages. Agents can load complete site context in a single fetch instead of fetching each page individually.

## MkDocs Material implementation

This site auto-generates both files from `mkdocs.yml` via `scripts/generate-llms-txt.py`. The script:

1. Reads each page's H1 and opening blockquote for titles and descriptions.
2. Annotates sections with `git log`-sourced `lastmod` dates.
3. Places high-priority sections in the main file and lower-priority ones under `## Optional`.
4. Writes two committed files: `docs/llms.txt` and `docs/llms-full.txt`.

CI enforces freshness: `python scripts/generate-llms-txt.py --check` exits non-zero if the committed files are out of date.

For a simpler approach, a static `docs/llms.txt` with 5 to 10 hand-curated entries takes minutes to create. Keep it current — stale entries pointing to dead links are worse than no file.

## Tooling to generate llms.txt

| Tool | Purpose |
|------|---------|
| `llms_txt2ctx` CLI | Generates llms.txt from existing sites |
| VitePress / Docusaurus plugins | Framework-native generation |
| MkDocs | Manual curation or custom generation script |
| Yoast SEO (WordPress) | Weekly auto-generation prioritizing cornerstone content |

## FAQ

**What's the difference between llms.txt and robots.txt or a sitemap?**

llms.txt is not a robots.txt replacement or a sitemap alternative. robots.txt controls whether crawlers can access pages; llms.txt guides an AI agent's navigation once it's already fetching content at inference time. Sitemaps list every crawlable URL, too many to fit in a context window, while llms.txt gives a human-curated, topic-organized index sized for a single agent request.

**How does an AI agent actually use an llms.txt file when researching a site?**

Per the spec's intended usage model ([llmstxt.org](https://llmstxt.org)), an agent researching a site fetches `/llms.txt` first, scans the H2-delimited sections to find the topic that matches its task, then fetches only the specific linked pages it needs. This replaces undirected crawling — where an agent guesses at URLs and discards irrelevant pages — with one fetch and a curated shortlist.

**Why does a curated llms.txt index help agents if it is not a citation or ranking signal?**

A curated llms.txt index moves the selection step outside the inference call — a human editor picks relevant pages once, so every agent invocation starts from a pre-filtered list instead of wasting context on irrelevant fetches. The `## Optional` convention extends this: agents can drop entire sections under context pressure while keeping the core index intact ([llmstxt.org](https://llmstxt.org)).

## Key Takeaways

- The spec requires only an H1 — everything else is optional
- Publish `llms-full.txt` alongside `llms.txt` — agents can load complete site context in one fetch instead of crawling linked pages individually
- `llms.txt` improves agentic navigation; it is not a citation or ranking signal — an [Ahrefs June 2026 log study](https://ahrefs.com/blog/llmstxt-study/) of 137,000 domains measured 97% of files receiving zero requests
- No major LLM provider has published documentation confirming they read `llms.txt` at inference time
- The file's real consumers are coding agents: `claude-code` was the #2 named AI fetcher, so a developer-facing site has a genuine navigation audience
- Keep it current — stale entries pointing to dead links are worse than no file

## Related

- [AI Crawler Policy](ai-crawler-policy.md)
- [Agent-Readiness Discovery Surfaces](agent-readiness-discovery-surfaces.md)
- [Schema and Structured Data](schema-and-structured-data.md)
- [What is GEO](what-is-geo.md)
- [How AI Engines Cite](how-ai-engines-cite.md)
- [SEO vs GEO](seo-vs-geo.md)
- [GEO for Technical Docs](geo-for-technical-docs.md)
- [Assertion Density](assertion-density.md)
- [Topical Authority](topical-authority.md)
- [Answer-First Writing](answer-first-writing.md)
- [Atomic Pages and Chunking](atomic-pages-and-chunking.md)
- [Measuring GEO Performance](measuring-geo-performance.md)
