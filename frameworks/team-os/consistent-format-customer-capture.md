---
title: "Consistent-Format Customer Capture"
description: "Freeze a six-section schema for customer-call summaries so agents can grep section headings across hundreds of files and synthesize findings without parsing prose."
tags:
  - agent-design
  - context-engineering
  - workflows
  - tool-agnostic
---

# Consistent-Format Customer Capture

> A frozen schema for customer-call summaries turns prose into a queryable dataset: every file shares the same headings in the same order, so an agent grep-aggregates across hundreds of calls in seconds.

## Why Shape Consistency Beats Content Richness

An agent asked "list every feature request from Q1 calls" does not read each summary end-to-end. It pattern-matches the heading hierarchy. When one summary records asks under `### Feature Requests` and the next buries them in a narrative paragraph, cross-call aggregation silently undercounts — the query returns the files that conform and skips the rest. A sparse but uniform template beats a rich but drifting one, because every query is a structural query first.

This is the same failure mode as [tool schema drift](https://medium.com/@duckweave/tool-schema-drift-11-checks-before-agents-guess-6038c1748309) and broader [document-pipeline schema drift](https://www.developer-tech.com/news/schema-drift-is-breaking-your-document-database-pipelines/): when the shape the agent expects diverges from the shape on disk, aggregation becomes a guess against the subset that still uses the heading you grep for.

## The Six-Section Schema

Hannah Stulberg's [`customer-call-summary/SKILL.md`](https://raw.githubusercontent.com/in-the-weeds-hannah-stulberg/team-os-example-repo/main/.claude/skills/customer-call-summary/SKILL.md) freezes six top-level sections, in this order, on every file:

1. **Executive Summary**
2. **Insights / Learnings**
3. **Feature Requests**
4. **Next Steps**
5. **Follow-up Email**
6. **Slack Summary**

The Executive Summary has fixed sub-structure: a status paragraph, a call-focus orientation, bold topic headers, a `How [Customer] is Using [Specific Feature/Workflow]` block, `Opportunity Areas`, an optional `[Product Strategy/Hypothesis] Validation`, and `Key Product Gaps`. Italicised inline quotes "bring the exec summary to life" per the skill file.

Persistent `## Open Action Items` and `## Completed Action Items` tables sit above the meeting content and update each call — state is tracked at the file level, not the meeting level.

## The Compression Story

A one-hour transcript runs 10,000+ tokens; a structured summary is ~500 — the 20x ratio that makes "synthesize 50 transcripts" fit in a 1M-token context where raw transcripts would not ([Gupta × Stulberg writeup](https://www.news.aakashg.com/p/claude-code-team-os)). The heading index across summaries is tier 1, the summary is tier 2, transcripts stay in tier 3 — loaded only when the summary lacks what the query needs.

## Heading-Indexed Retrieval

The schema is a hand-built inverted index. `grep -A 20 '### Feature Requests' customers/**/*.md` returns every feature request across the corpus — no embedding, no chunking, no hallucinated inclusion. Anthropic's [context-engineering guidance](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) names the same primitives: just-in-time loading, structure-first retrieval, attention-budget conservation. Stulberg on the [Aakash Gupta podcast](https://www.aakashg.com/hannah-stulberg-podcast/): *"I can say 'who did I meet with over the last two weeks and what did I learn?' because I store all my customer information inside the repository in a really structured manner"* — *"apples to apples across hundreds of calls in seconds"*. The heading is the key; the section body is the value. See [structured domain retrieval](../../context-engineering/structured-domain-retrieval.md) for the atomic pattern.

## Drift Prevention

Enforcement lives in the skill file. `SKILL.md` closes with a 17-item **Quality Checklist** — items like *`[ ] Insights use table format with quotes on separate lines`* and *`[ ] Feature requests cross-referenced with feature-requests/feature-requests.md`* — that Claude runs against each draft before finalising. A capture rule in `CLAUDE.md` routes Claude to the skill; the checklist inside the skill enforces the shape (prompt-as-spec — see [structured-output constraints](../../verification/structured-output-constraints.md)).

## Progressive Tightening

Do not freeze on day one. Start loose; ten to twenty calls reveal which sections the team actually populates, which collapse to "none", and which need sub-structure the first draft missed. Freeze once the shape stabilises — the skill file is then a [frozen spec file](../../instructions/frozen-spec-file.md), changed only through explicit PR. Tightening too early encodes guesses; tightening too late lets drift compound.

Schemas age as product strategy shifts. Review the skill file quarterly and treat changes as versioned events, not silent edits, so historical calls stay comparable to themselves.

## When This Backfires

The pattern underdelivers — or actively hurts — under three conditions:

- **Heterogeneous call types.** Support escalations, renewal negotiations, and technical deep-dives do not map cleanly onto six discovery-shaped sections. Forcing them in produces empty `## Feature Requests` blocks that pollute aggregation; fork the schema by call kind instead.
- **Small corpora.** When the team has twenty calls total, the agent can read every transcript end-to-end and the grep economics collapse. Schema overhead exceeds payoff until the corpus outgrows the context window.
- **Schemas frozen past their strategy.** A schema cut against last year's hypothesis silently distorts this quarter's discovery — the section the team needs now is the one nobody is recording. Quarterly review is a hard prerequisite, not a nice-to-have.

## Example

A PM runs a discovery call, drafts the summary under `product-development/product/customers/accounts/acme-corp/calls/summaries/2026-03-10.md` ([live example in Stulberg's reference repo](https://github.com/in-the-weeds-hannah-stulberg/team-os-example-repo/blob/main/product-development/product/customers/accounts/acme-corp/calls/summaries/2026-03-10.md)), and the skill applies the six-section schema verbatim: the **Executive Summary** opens with account status, orients on the call topic, lists `Opportunity Areas` and `Key Product Gaps`; **Insights / Learnings** goes in as a table with inline customer quotes; **Feature Requests** cross-references the team's `feature-requests.md` backlog; **Next Steps** lists owners and dates; **Follow-up Email** and **Slack Summary** are ready-to-send artifacts. Ten calls later, the PM asks: *"list every Key Product Gap across customer calls this quarter."* The aggregation is a one-liner against the corpus:

```bash
grep -A 20 '### Key Product Gaps' product-development/product/customers/accounts/**/calls/summaries/*.md
```

The agent runs the grep, returns a deduplicated list in seconds, and links back to the source files — the gaps aggregate because the heading is identical in every file.

## Key Takeaways

- Shape consistency dominates content richness — aggregation is a structural query first.
- The canonical schema is Stulberg's six ordered sections: Executive Summary, Insights / Learnings, Feature Requests, Next Steps, Follow-up Email, Slack Summary.
- The payoff is quantified: 20x token compression (~500 vs 10,000+ tokens) makes 50-transcript synthesis fit in one context window.
- Agents aggregate by grep-ing the heading hierarchy, not by parsing prose — the schema is a hand-built inverted index.
- Enforcement lives in the skill file's quality checklist, not a separate lint rule; the skill is prompt-as-spec.
- Freeze the schema only after 10–20 calls have revealed the natural fields — progressive tightening avoids encoding first-draft guesses.

## Related

- [Team OS](index.md) — the framework this page composes into
- [Cross-functional artifacts](cross-functional-artifacts.md) — the broader parent pattern on artifact types that span function folders
- [Frozen spec file](../../instructions/frozen-spec-file.md) — the general discipline the skill file embodies
- [Specification as prompt](../../instructions/specification-as-prompt.md) — why the SKILL.md functions as prompt-as-spec
- [Structured domain retrieval](../../context-engineering/structured-domain-retrieval.md) — the retrieval mechanism heading-indexed aggregation implements
- [Structured output constraints](../../verification/structured-output-constraints.md) — the verification pattern the quality checklist enforces
