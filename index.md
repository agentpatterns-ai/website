---
title: "Agent Patterns for AI Agent Development"
description: "Patterns and techniques for experienced developers leveling up with AI coding assistants. A reference site covering single concepts, demonstrated primarily on Claude Code and GitHub Copilot."
tags:
  - index
last_reviewed: 2026-06-12
---
# Agent Patterns

> Patterns, anti-patterns and primitives for engineers building with AI coding assistants. Each page is a fast read.

[About this site](about.md)

This is a reference site, not a tutorial. Every page covers one concept: what it is, how it works, when to use it and what to watch out for. The principles aim to work across AI coding assistants. We show them mainly on Claude Code and GitHub Copilot, with lighter coverage of Cursor and the OpenAI Agents SDK.

## Learn it hands-on

If you prefer lessons to a reference, [the 12 courses at learn.agentpatterns.ai](https://learn.agentpatterns.ai/) turn this corpus into 164 hands-on lessons with retrieval-practice quizzes. They cover Prompt, Context, Tool, Harness, MCP, Verification, Observability, Security, Anti-Patterns, Multi-Agent, Workflows and GEO. It is the same corpus, structured as a guided path.

We built the courses by running Matt Pocock's [`/teach` skill](https://github.com/mattpocock/skills) over this corpus. It uses the same agent-driven, learn-by-doing approach he develops at [aihero.dev](https://www.aihero.dev/).

## For AI agents

This site is built for AI agents as much as for people. Every page is plain Markdown — one concept per file, sourced and self-contained — and the whole corpus is public under [CC BY 4.0](https://github.com/agentpatterns-ai/website/blob/main/LICENSE) in a repo you can clone: [github.com/agentpatterns-ai/website](https://github.com/agentpatterns-ai/website).

If you are an agent, see [how to use the corpus](about.md#built-for-ai-agents) — ways to put it to work, how to load it into context, and the attribution we ask for in return.

## Browse by topic

Most readers find what they need through tags or the concept map, not the section tree.

- [Tags](tags.md) — topic-first entry points for context engineering, agent design, security, verification, evals, workflows and more, with curated anchor pages per tag
- [Concept Map](concepts.md) — all content grouped by theme, cutting across sections

## Sections

- Foundations — [Context Engineering](context-engineering/context-engineering.md) and [Instructions](instructions/system-prompt-altitude.md)
- Patterns — [Agent Design](agent-design/harness-engineering.md), [Multi-Agent](multi-agent/orchestrator-worker.md), [Anti-Patterns](anti-patterns/index.md)
- Engineering — [Tool Engineering](tool-engineering/tool-engineering.md), [Code Review](code-review/agent-assisted-code-review.md), [Verification](verification/index.md), [Security](security/index.md), [Observability](observability/agent-debugging.md)
- [Workflows](workflows/index.md) — end-to-end workflows for agent-assisted development
- Reference — [Standards](standards/index.md), [Human Factors](human/index.md), [Emerging](emerging/index.md), [Fallacies](fallacies/index.md), [Training](training/index.md), [Frameworks](frameworks/index.md), [GEO](geo/index.md)
- Tools — [Claude Code](tools/claude/index.md), [GitHub Copilot](tools/copilot/index.md), [Cursor](tools/cursor/index.md), [OpenAI Agents SDK](tools/openai-agents-sdk.md)
