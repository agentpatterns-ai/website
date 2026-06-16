---
title: "llms.txt: Making Your Project Discoverable to AI Agents"
description: "Publish a standardized /llms.txt file so AI agents can navigate your project or site efficiently without crawling every page."
tags:
  - workflows
  - context-engineering
  - tool-agnostic
  - standards
last_reviewed: 2026-05-27
maturity: emerging
---

# llms.txt: Making Your Project Discoverable to AI Agents

> llms.txt is a plain-text file at `/.well-known/llms.txt` or `/llms.txt` that tells AI agents and language models what your project does and how to navigate its content efficiently.

The [llms.txt specification](https://llmstxt.org) (Jeremy Howard, answer.ai) defines a Markdown file published at `{site-root}/llms.txt`. LLM context windows are too small to process full websites, and HTML adds noise; `llms.txt` gives agents a curated, structured index instead — one fetch replaces undirected crawling, and the agent spends its context budget on content rather than discovery.

A companion convention is `/llms-full.txt`: all linked pages concatenated for complete site context in a single fetch.

## When This Backfires

- **Static sites with infrequent updates** benefit most; high-churn sites risk serving stale link lists that mislead agents
- **No major LLM provider has published documentation confirming they read `llms.txt` at inference time** — Google's John Mueller stated in June 2025 that "no AI system currently uses llms.txt" and that server logs show AI bots are not fetching it ([Search Engine Roundtable](https://www.seroundtable.com/google-ai-llms-txt-39607.html)); treat adoption as forward-compatible infrastructure, not a guaranteed citation signal
- **Empirical 2026 data shows no citation uplift**: an analysis of 300,000 domains found no measurable effect of `llms.txt` presence on AI citation likelihood, and adoption remains ~10% even among tech-forward publishers ([Search Engine Journal](https://www.searchenginejournal.com/llms-txt-shows-no-clear-effect-on-ai-citations-based-on-300k-domains/561542/); [ALLMO analysis of 94k cited URLs](https://www.allmo.ai/articles/llms-txt))
- A poorly curated `llms.txt` pointing to dead links is worse than none — agents that follow broken links waste context and may return errors

See [llms.txt: Spec, Adoption, and Honest Limitations](../geo/llms-txt.md) for full adoption landscape and known limitations.

## Example

A minimal `llms.txt` for a documentation site:

```markdown
# Acme Docs

> Developer documentation for the Acme platform — REST API, SDKs, and tutorials.

## Core Documentation

- [Quick Start](/docs/quickstart): First app in 5 minutes
- [API Reference](/docs/api): Full endpoint reference

## Optional

- [Changelog](/changelog): Release notes
```

The H1 is the only required element per the [spec](https://llmstxt.org); sections and the `## Optional` block are conventions that help agents budget context. Publish `/llms-full.txt` alongside it to give agents the full concatenated content in one fetch.

## Key Takeaways

- `llms.txt` is a curated Markdown index at `/llms.txt` that tells agents where your content lives without forcing them to crawl HTML pages.
- The spec requires only an H1; blockquote summaries, H2 sections, and an `## Optional` block are conventions that help agents budget context.
- Publishing `/llms-full.txt` alongside it lets agents fetch all linked content in a single request, eliminating multi-step navigation.
- Treat `llms.txt` as forward-compatible agent infrastructure — empirical 2026 data shows no measurable citation uplift, so do not invest in it as an SEO or ranking signal.
- A stale or broken `llms.txt` is worse than none; only publish if you can keep the link list current.

## Related

- [llms.txt: Full Specification, Adoption, and Limitations](../geo/llms-txt.md)
- [Agent Cards: Capability Discovery Standard for AI Agents](agent-cards.md)
- [agents.md Convention](agents-md.md)
