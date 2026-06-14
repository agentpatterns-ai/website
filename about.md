---
title: "About Agent Patterns"
description: "Editorial stance and inclusion criteria for the Agent Patterns site — what earns a page, what doesn't, and how to suggest one."
tags:
  - tool-agnostic
last_reviewed: 2026-05-27
status: current
---

# About Agent Patterns

> A practitioner's catalogue of patterns and primitives for engineers building with AI coding assistants.

Agent Patterns is a reference site for experienced developers using AI coding assistants daily — Claude Code, GitHub Copilot, Cursor, and the surrounding ecosystem. The principles aim to generalize across assistants; the examples are demonstrated primarily on Claude Code and GitHub Copilot, with lighter coverage of Cursor and the OpenAI Agents SDK. Pages aim for a sub-60-second read with one concept per page.

## What this site is

A practitioner resource — patterns, anti-patterns, paper summaries, and tool features — written to be understood in seconds, with no academic ceremony. Browsing the tree is the fallback; the primary access pattern is LLM-first discovery and aggressive cross-linking.

## How it's maintained

The site runs as a content pipeline. Feedback and suggestions land through GitHub issues against the public mirror at [agentpatterns-ai/website](https://github.com/agentpatterns-ai/website). Every page goes through research, drafting, review, and lint gates before publication — the inclusion criteria below are what every page is reviewed against.

## What earns a page

A topic earns a page when it meets three tests:

- **Practitioner-relevant**: it changes a decision an experienced engineer makes while shipping with AI assistants today.
- **Fast to grok**: it can be communicated as a single concept inside the length target for its category.
- **Sourceable**: every technical claim links to a primary source. Unsourceable claims are rewritten weaker, removed, or filed as a research issue — never hedged.

## What doesn't

These do not earn pages:

- **Runnable libraries or SDKs** — the site documents patterns and trade-offs, not code packages.
- **Framework tutorials** — readers already use AI assistants daily; no step-by-step onboarding.
- **Generic LLM theory** — the audience is engineers shipping with AI coding assistants, not researchers surveying the field.
- **Opinion essays or hot takes** — patterns are presented with trade-offs, not ranked or endorsed.

## How pages stay current

Pages carry optional currency frontmatter — `last_reviewed`, `applies_to`, and `status` — that surface as reader-facing badges (`current`, `aging`, `archived`). Data-driven triage runs quarterly against Google Search Console traffic and AI-citation signals, marking underperformers for consolidation, archival, or rewrite.

## How to suggest a page

Open an [issue](https://github.com/agentpatterns-ai/website/issues/new) on the public mirror with the concept, context, and any references. Ideas enter a research → drafting → review pipeline before publication.

## Key Takeaways

- The site is a practitioner reference, not a tutorial or a manifesto.
- Inclusion criteria are explicit and public — what earns a page and what doesn't.
- Every claim is sourced; the unsourced ones get rewritten, removed, or queued as research.
- Currency and triage are policy-driven, not gut-driven.

## Related

- [Tags](tags.md) — browse content by topic
- [Concept Map](concepts.md) — all content grouped by theme
