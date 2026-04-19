---
title: "Interactive Canvases: Agent-Generated Visual Artifacts as Outputs"
description: "Agents increasingly return interactive canvases — tables, charts, diagrams, dashboards — instead of text. A decision framework for when that shape earns its overhead and what it does to review."
tags:
  - agent-design
  - code-review
aliases:
  - agent canvas output
  - interactive artifact output
---

# Interactive Canvases: Agent-Generated Visual Artifacts as Outputs

> Canvases are an output-shape choice, not a new pattern. They earn their overhead when output is irreducibly multi-dimensional and lose it when a sentence would have done — and they change what "reviewing the answer" means.

Claude Artifacts (Claude 3.5 Sonnet, June 2024) introduced a dedicated window for generated content "alongside their conversation" for code snippets, text documents, and website designs ([Anthropic](https://www.anthropic.com/news/claude-3-5-sonnet)). Cursor 3.1 extended the primitive to agent-built visualizations: "Cursor can now respond by creating interactive canvases" with first-party components — tables, boxes, diagrams, charts — plus diffs and to-do lists ([Cursor changelog](https://cursor.com/changelog)). The shape is now available across mainstream tools; the question is when to produce one.

This page covers the **output-shape decision**: when a canvas beats text or a Git-tracked file, and what changes about review once one exists.

## When a Canvas Earns Its Overhead

A canvas costs render time, an extra surface the reader must interact with, and a verification gap (see below). It pays that cost back only when the output has structure a sentence cannot carry. The Cursor blog describes canvases as combining "data from multiple sources into single visualizations" with "logic and interactivity tailored to user requests" ([Cursor](https://cursor.com/blog/canvas)) — which is the real criterion: irreducible multi-dimensionality.

Use a canvas when:

- The answer is a comparison across rows, columns, or time
- The reader will filter, sort, or drill in rather than read top-to-bottom
- Multiple data sources merge into one view
- A diagram or chart communicates faster than the equivalent prose

Do not use a canvas when:

- The answer is a scalar, a short list, or a single file path
- The output already lives in Git (a diff, a config file) — review belongs in the PR, not an ephemeral side panel
- The reader will copy the result elsewhere — plain text travels better than a rendered component

## The Source-Traceability Gap

A rendered dashboard looks authoritative. The query behind it may be wrong. A canvas presents the synthesis — the chart, the aggregation, the filter — without automatically surfacing the inputs. This is the same failure mode as any LLM output that hides its intermediate reasoning, amplified by the visual confidence the rendering provides.

Mitigations belong in the canvas itself:

- A visible "source" affordance that shows the query, tool call, or data slice that produced each panel
- A way to expand any aggregate into its constituent rows
- Timestamps and data versioning so a stale canvas is recognisable as stale

Without these, reviewing a canvas means trusting the render. With them, the canvas becomes auditable — which is the condition under which it is worth producing at all.

## Review and Handoff Implications

Canvases live in the agent window, not the Git tree. For a pull-request-centric team, this splits the review surface: the code diff is in GitHub, the canvas that motivated it is in the agent. Reviewers cannot inspect the canvas unless they re-run the prompt, and re-runs may produce a different canvas.

Two practical consequences:

1. **Canvas outputs are not review artifacts on their own.** If a decision hinges on what the canvas showed, export the canvas (or its underlying data and query) into the PR description, an issue comment, or a committed file. The canvas is a working surface; the PR is the record.
2. **Canvases do not replace written answers in async review.** A reviewer reading the PR at 2 a.m. cannot interact with a live Cursor canvas. Any claim the canvas was meant to communicate needs a prose or screenshot version in the durable channel.

## Why This Is an Output-Shape Pattern, Not an Architectural One

Anthropic's canonical list of agent patterns — prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer — does not include artifacts or canvases ([Anthropic](https://www.anthropic.com/engineering/building-effective-agents)). That is deliberate. The underlying agent architecture is unchanged whether the output ships as Markdown, JSON, a chart, or a dashboard. Canvases are a UI affordance that changes what the human does with the result; they do not change what the agent did to produce it.

Treating canvases as an architectural pattern conflates tooling with design. Treating them as an output-shape decision — one of several ways to package the same underlying work — keeps the focus on the real question: does this output have enough structure that rendering it beats describing it, and is the verification gap small enough to accept?

## Example

An agent is asked to audit dependency versions across five services in a monorepo and recommend upgrades.

**Without a canvas** — prose output:

```
service-a: express 4.18.2 (latest 4.21.1, 3 minor versions behind, 2 CVEs)
service-b: express 4.19.0 (latest 4.21.1, 2 minor versions behind, 1 CVE)
... (5 services x 6 dependencies = 30 lines of text)
```

A reviewer scans 30 lines, trying to remember which services had CVEs.

**With a canvas** — table output in Cursor 3.1:

| Service | Package | Current | Latest | Severity |
|---------|---------|---------|--------|----------|
| service-a | express | 4.18.2 | 4.21.1 | 2 CVEs |
| service-b | express | 4.19.0 | 4.21.1 | 1 CVE |

The canvas pays off: the reviewer sorts by severity, filters to CVEs only, decides which services to upgrade this sprint. The multi-dimensional comparison across services and packages is exactly the shape a canvas handles better than prose.

The source-traceability requirement still applies. A "Show query" affordance on each row — revealing the `npm outdated` call, the advisory database query, and the timestamp — is what makes the canvas auditable rather than just pretty. Without it, the reviewer is trusting that the advisory list is current and the version parsing was correct, on faith.

## Key Takeaways

- Canvases earn their overhead only when output has irreducible multi-dimensionality — comparisons, drill-ins, merged data
- For scalars, short lists, and Git-tracked outputs, a canvas adds cost without value
- Rendered canvases carry source-traceability risk: the visual confidence exceeds the audit trail unless sources are explicitly surfaced
- Canvases are a working surface, not a review artifact; exporting key state into the PR is what makes them reviewable
- The pattern is an output-shape decision, not a change in agent architecture

## Related

- [Controlling Agent Output](../agent-design/controlling-agent-output.md)
- [Diff-Based Review](../code-review/diff-based-review.md)
- [Visible Thinking in AI Development](../observability/visible-thinking-ai-development.md)
- [Product-as-IDE](product-as-ide.md)
