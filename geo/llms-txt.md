---
title: "llms.txt: Full Specification, Adoption, and Limitations"
description: "The llms.txt specification gives AI agents a curated index of your site — it improves agentic comprehension but is not a citation or ranking signal."
tags:
  - geo
  - technique
  - tool-agnostic
  - workflows
---

# llms.txt: Spec, Adoption, and Honest Limitations

> `/llms.txt` gives AI agents a curated entry point to your site at inference time — it improves agent navigation, not citation rates or search rankings.

## What the Spec Actually Specifies

The [llms.txt specification](https://llmstxt.org) (Jeremy Howard, answer.ai) defines a Markdown file published at `{site-root}/llms.txt`. LLM context windows are too small to process full websites, and HTML adds noise. The file gives agents a curated, structured index instead.

The spec defines exactly one required element:

| Element | Required? | Purpose |
|---------|-----------|---------|
| H1 heading (project/site name) | **Yes** | Only mandatory element |
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

## How Agents Use It

When an agent needs to research a site, it checks `/llms.txt` first — a structured index replacing undirected crawling with a single fetch and curated list:

1. Fetch `{site}/llms.txt`
2. Identify the relevant section
3. Fetch only the linked pages that apply to the task

A companion convention (not in the formal spec) is to also publish `/llms-full.txt`: all linked pages concatenated into one file for full site context in a single fetch. Profound data shows agents visit `llms-full.txt` at 2x the rate of `llms.txt` [unverified].

## What It Is Not

- **Not a robots.txt replacement**: `robots.txt` controls crawler access; `llms.txt` guides inference-time navigation.
- **Not a sitemap alternative**: Sitemaps cover all crawlable URLs — too many to fit in a context window with no curation. `llms.txt` is a curated editorial index.
- **Not a training data submission**: The spec is for inference-time use. It has no defined role in model training pipelines.

## The Citation Limitation

`llms.txt` is infrastructure for agentic navigation, not a GEO ranking signal:

- No major AI provider (Anthropic, OpenAI, Google) has documented reading `llms.txt` at inference time [unverified]
- Studies find no correlation between `llms.txt` presence and AI citation rates [unverified]
- Citation signals are dominated by content authority, structured data, and entity recognition [unverified]

## Real Adoption Examples

| Site | Implementation note |
|------|---------------------|
| [docs.github.com/llms.txt](https://docs.github.com/llms.txt) | API-first format — exposes endpoints for agents to discover pages programmatically |
| [cursor.com/llms.txt](https://cursor.com/llms.txt) | Full docs structure including 10-language internationalization |
| Anthropic platform | 651 pages across Developer Guide, API Reference, and SDKs [unverified] |

[Mintlify's November 2024 rollout](https://www.mintlify.com/blog/what-is-llms-txt) of auto-generated `llms.txt` across all hosted documentation sites drove mass adoption: sites including Anthropic and Cursor adopted overnight via their hosting platform [unverified].

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

Publish an accompanying `/llms-full.txt` with the concatenated text of all linked pages. Agents use it to load complete site context in a single fetch [unverified].

## MkDocs Material Implementation

This site auto-generates both files from `mkdocs.yml` via `scripts/generate-llms-txt.py`. It:

1. Reads each page's H1 and opening blockquote for titles and descriptions
2. Annotates sections with `git log`-sourced `lastmod` dates
3. Places high-priority sections in the main file; lower-priority under `## Optional`
4. Writes two committed files: `docs/llms.txt` and `docs/llms-full.txt`

CI enforces freshness: `python scripts/generate-llms-txt.py --check` exits non-zero if committed files are out of date.

For a simpler approach: a static `docs/llms.txt` with 5-10 manually curated entries takes minutes to create. Keep it current — stale entries pointing to dead links are worse than no file.

## Tooling Ecosystem

| Tool | Purpose |
|------|---------|
| `llms_txt2ctx` CLI | Generates llms.txt from existing sites |
| VitePress / Docusaurus plugins | Framework-native generation |
| MkDocs | Manual curation or custom generation script |
| Yoast SEO (WordPress) | Weekly auto-generation prioritizing cornerstone content |

## Key Takeaways

- The spec requires only an H1 — everything else is optional
- Publish `llms-full.txt` alongside `llms.txt` — agents use it for full-site context in a single fetch [unverified]
- `llms.txt` improves agentic navigation; it is not a citation or ranking signal
- No major LLM provider has documented reading `llms.txt` at inference time [unverified]
- Keep it current — stale entries pointing to dead links are worse than no file

## Related

- [AI Crawler Policy](ai-crawler-policy.md)
- [Schema and Structured Data](schema-and-structured-data.md)
- [What is GEO](what-is-geo.md)
- [How AI Engines Cite](how-ai-engines-cite.md)
- [SEO vs GEO](seo-vs-geo.md)
- [GEO for Technical Docs](geo-for-technical-docs.md)
