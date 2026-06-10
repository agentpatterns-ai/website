---
title: "Mermaid as Agent Output Format: When to Ask for a Diagram Instead of Prose"
term: "Mermaid as Agent Output Format"
description: "Asking the agent for a Mermaid block instead of a prose list scans faster for graph-shaped information — but only on surfaces that render Mermaid inline. The decision is surface-gated, not capability-gated."
aliases:
  - mermaid output format
  - asking agents for mermaid diagrams
  - surface-aware mermaid output
tags:
  - instructions
  - agent-design
  - tool-agnostic
last_reviewed: 2026-06-02
---

# Mermaid as Agent Output Format: When to Ask for a Diagram Instead of Prose

> Ask for a Mermaid block over prose for graph-shaped information, but only on surfaces that render it inline. The decision is surface-gated, not model-gated.

Output format value is a property of the consumer surface, not the agent. A fenced ` ```mermaid ` block renders as a diagram on GitHub, mkdocs-material, Notion, Obsidian, and — as of [VS Code 1.121](https://code.visualstudio.com/updates/v1_121) — the built-in Markdown preview, notebook cells, and chat panes. On Slack, plain email, or a terminal without ASCII fallback, the same block prints as raw markup. Make the request conditional on what the host renders.

## The Surface Shift Already Happened

Agents default to prose lists for architecture, sequence, or dependency information because Mermaid was inert noise on most surfaces in the GPT-4 era. That has flipped on the surfaces coding agents run on:

| Surface | Renders inline Mermaid | Evidence |
|---------|------------------------|----------|
| GitHub issues, PRs, README, wiki | Yes | [GitHub Blog, Feb 2022](https://github.blog/developer-skills/github/include-diagrams-markdown-files-mermaid/) |
| VS Code Markdown preview, notebooks, chat | Yes (1.121+) | [VS Code 1.121 release notes](https://code.visualstudio.com/updates/v1_121) |
| Cursor CLI (ASCII fallback) | Yes (Feb 2026+) | [Cursor changelog](https://cursor.com/changelog/cli-feb-18-2026) |
| Zed agent threads | Yes (PR #56430) | [Zed discussion #54263](https://github.com/zed-industries/zed/discussions/54263) |
| Plain Slack chat | No | [JackuB/mermaid-preview](https://github.com/JackuB/mermaid-preview) exists to work around it |
| Plain email, raw terminal | No | Renders as fenced source text |

The 1.121 release "merged Matt Bierner's Markdown Preview Mermaid Support extension into VS Code as a new built-in extension called `Mermaid Markdown Features`" ([release notes](https://code.visualstudio.com/updates/v1_121)). The agent did not change. The surface did.

## When Mermaid Wins

The pattern works when both conditions hold: the surface renders Mermaid, and the information is graph-shaped. Match diagram type to shape:

| Diagram type | Shape that benefits |
|--------------|---------------------|
| `graph TD` / `flowchart` | Branching control flow, decision trees, hierarchy |
| `sequenceDiagram` | Interactions between tools, services, agents over time |
| `stateDiagram-v2` | State machines, lifecycle transitions |
| `classDiagram` | Type relationships, domain models |
| `erDiagram` | Schema and entity relationships |

The Zed discussion motivating their renderer captures the case: "Agent responses often explain flows, architectures, and plans that are easier to understand visually than as prose or indented lists" ([Zed discussion #54263](https://github.com/zed-industries/zed/discussions/54263)).

## When This Backfires

The same fenced block fails in four specific ways:

- **Non-rendering surface.** Plain Slack, raw email, or a terminal without ASCII rendering shows ` ```mermaid graph TD A-->B ``` ` as literal text. The Slack workaround app `mermaid-preview` exists because Slack does not render Mermaid in chat — it runs Mermaid CLI server-side and posts a PNG ([JackuB/mermaid-preview](https://github.com/JackuB/mermaid-preview)).
- **Diagram too large.** Mermaid Chart's own engineering team argues flow layout is "O(n²) complex" past ~100 connections ([Mermaid Chart blog](https://docs.mermaidchart.com/blog/posts/flow-charts-are-on2-complex-so-dont-go-over-100-connections)); the third-party Mermaid-Sonar analyzer calibrates a 50-node threshold for "complex" flows ([Entropic Drift](https://entropicdrift.com/blog/mermaid-sonar-complexity-analyzer/)). Past those bounds, nested subgraphs hide structure.
- **Silent syntax failure.** LLM-generated Mermaid frequently contains parser errors that render to nothing without warning. pr-agent documents that backticks inside node labels "cause the mermaid renderer (on GitHub/GitLab) to fail silently" ([qodo-ai/pr-agent #2211](https://github.com/The-PR-Agent/pr-agent/issues/2211)). A class of repair tools exists because of this: GenAIScript's `system.diagrams` re-prompts on parse error ([Mermaids Unbroken](https://microsoft.github.io/genaiscript/blog/mermaids/)); `mermaid-validator` auto-fixes common LLM mistakes ([lvy010/mermaid-validator](https://github.com/lvy010/mermaid-validator)).
- **Information not graph-shaped.** Linear procedures, tabular comparisons, and numeric data are flattened by Mermaid. A table or ordered list communicates them faster.

## The Prompt Pattern

Make the surface explicit and pick the diagram type. The instruction belongs in the most precise scope — a [domain-specific system prompt](domain-specific-system-prompts.md), a slash command, or a per-request hint:

```
You are working in a chat surface that renders Mermaid inline (VS Code
1.121 chat, GitHub PR comment, mkdocs-material site, Notion, Obsidian).
When the answer is graph-shaped — architecture, sequence flow, decision
tree, state machine, dependency graph — reply with a single Mermaid
fenced block using the diagram type that matches the shape
(graph TD, sequenceDiagram, stateDiagram-v2). Keep diagrams under
20 nodes and avoid backticks inside node labels. For tabular or linear
information, stay with Markdown.
```

The mirror instruction matters as much: on a non-rendering surface (Slack, raw terminal, email digest), tell the agent prose is preferred. Codifying the technique as a reusable skill is viable — the [GenAIScript `system.diagrams`](https://microsoft.github.io/genaiscript/reference/scripts/diagrams/) prompt registers a parse-and-repair loop so silent-failure diagrams are caught before they reach the user.

## Why It Works

The mechanism is consumer-surface capability, not model capability. A diagram beats prose only when the surface displays it as a diagram and the information is graph-shaped enough that edges carry meaning — both properties of the deployment environment, not the model. When VS Code 1.121 added a built-in renderer, the value of asking for Mermaid changed without any model change. The companion pattern for [HTML as Agent Output Format](html-as-output-format.md) makes the same point at a different altitude — Mermaid is the inline version of the surface-conditional decision.

## Example

A reviewer asks an agent to summarise the request path through a four-service auth flow.

**Prose request** — the default:

```
Explain the request path through the auth services. List each hop and
what each service does.
```

The reply is a numbered list — readable but linear. The reviewer mentally reconstructs the graph.

**Mermaid request, rendering surface** — the technique:

```
We're in a GitHub PR comment. Explain the request path as a Mermaid
sequenceDiagram with actors for client, gateway, auth-service, and
session-store. Use arrows labelled with the call name. Stay under
15 messages.
```

The reply is a sequence diagram GitHub renders inline. The reviewer reads it in one pass.

**Same Mermaid request, non-rendering surface** — the failure mode:

The same prompt sent to an agent posting to a plain Slack channel produces a fenced ` ```mermaid ` block. Slack renders it as code text, not a diagram. The reviewer has to copy it to an external Mermaid editor to read it — strictly worse than the prose version. The fix is to either keep prose as the default on Slack or wire a Slack render-to-PNG bridge like [mermaid-preview](https://github.com/JackuB/mermaid-preview).

## Key Takeaways

- Output format value is a property of the consumer surface, not the agent. Mermaid only beats prose when the surface renders it and the information is graph-shaped.
- VS Code 1.121 added built-in Mermaid rendering to preview, notebooks, and chat ([release notes](https://code.visualstudio.com/updates/v1_121)); GitHub, mkdocs-material, Notion, Obsidian render it natively; Cursor CLI ships ASCII fallback in the terminal.
- Failure modes are concrete: non-rendering surface (Slack, plain email), diagrams past ~50 nodes or ~100 connections, silent syntax errors from LLM-generated Mermaid, and information that is not graph-shaped.
- Encode the surface as an explicit constraint in the system prompt or skill — "this surface renders Mermaid inline" or "this surface does not" — and let the diagram-type-to-information-shape mapping pick the chart.

## Related

- [HTML as Agent Output Format: When to Ask for HTML Instead of Markdown](html-as-output-format.md)
- [Domain-Specific System Prompts with Concrete Examples](domain-specific-system-prompts.md)
- [System Prompt Altitude: Specific Without Being Brittle](system-prompt-altitude.md)
- [Controlling Agent Output: Concise Answers, Not Essays](controlling-agent-output.md)
- [Event-Driven System Reminders](event-driven-system-reminders.md)
