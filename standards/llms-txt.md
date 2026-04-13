---
title: "llms.txt: Making Your Project Discoverable to AI Agents"
description: "Publish a standardized /llms.txt file so AI agents can navigate your project or site efficiently without crawling every page."
tags:
  - workflows
  - context-engineering
---

# llms.txt: Making Your Project Discoverable to AI Agents

> llms.txt is a plain-text file at `/.well-known/llms.txt` or `/llms.txt` that tells AI agents and language models what your project does and how to navigate its content efficiently.

The [llms.txt specification](https://llmstxt.org) (Jeremy Howard, answer.ai) defines a Markdown file published at `{site-root}/llms.txt`. LLM context windows are too small to process full websites, and HTML adds noise; `llms.txt` gives agents a curated, structured index instead — one fetch replaces undirected crawling, and the agent spends its context budget on content rather than discovery.

A companion convention is `/llms-full.txt`: all linked pages concatenated for complete site context in a single fetch.

## When This Backfires

- **Static sites with infrequent updates** benefit most; high-churn sites risk serving stale link lists that mislead agents
- **No major LLM provider has published documentation confirming they read `llms.txt` at inference time** — treat adoption as forward-compatible infrastructure, not a guaranteed citation signal
- A poorly curated `llms.txt` pointing to dead links is worse than none — agents that follow broken links waste context and may return errors

See [llms.txt: Spec, Adoption, and Honest Limitations](../geo/llms-txt.md) for full adoption landscape and known limitations.

## Related

- [llms.txt: Full Specification, Adoption, and Limitations](../geo/llms-txt.md)
- [Agent Cards: Capability Discovery Standard for AI Agents](agent-cards.md)
- [agents.md Convention](agents-md.md)
