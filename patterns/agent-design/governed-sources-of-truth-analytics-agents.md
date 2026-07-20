---
title: "Governed Sources of Truth for Analytics Agents (Structure Over Access)"
term: "Governed Sources of Truth for Analytics Agents"
description: "Layer semantic models, lineage, and skill routers between an analytics agent and the warehouse — raw corpus access alone moved Anthropic accuracy by less than a point."
tags:
  - agent-design
  - context-engineering
  - testing-verification
  - tool-agnostic
aliases:
  - structure over access for analytics agents
  - grounding analytics agents in governed sources
last_reviewed: 2026-06-28
maturity: established
---

# Governed Sources of Truth for Analytics Agents (Structure Over Access)

> Route analytics agents through semantic layers, lineage, and skill routers — raw warehouse access alone moved Anthropic's accuracy by less than a point.

Governed sources of truth are reference surfaces — semantic layer, lineage graph, curated reference docs, business knowledge graph — that sit between an analytics agent and the raw warehouse and resolve a user's question to a single governed entity before any SQL is written. Anthropic's internal data-analytics agent reached >95% aggregate accuracy (from ≤21% without skills) after this layering, and 95% of business-analytics queries are now Claude-automated ([Anthropic blog](https://claude.com/blog/how-anthropic-enables-self-service-data-analytics-with-claude)).

## The three failure modes

Pointing an agent at the warehouse creates a false sense of precision. Three attributes account for the majority of wrong answers ([Anthropic blog](https://claude.com/blog/how-anthropic-enables-self-service-data-analytics-with-claude)):

| Failure mode | What goes wrong |
|---|---|
| Concept-to-entity ambiguity | "Active users" maps to dozens of plausible field-and-filter combinations; the agent picks one without knowing which the asker meant |
| Data staleness | Sources, definitions, and schemas change daily; cached agent knowledge returns subtly wrong answers within weeks |
| Retrieval failure | The right table is documented somewhere, but the agent doesn't find it in a million-field warehouse |

Coding agents tolerate ambiguity because tests, types, and compilers act as guardrails. Analytics has no such oracle — a syntactically valid query against the wrong entity returns a confident-looking number with no failure signal.

## The four layers

Each layer attacks one or more of the three failure modes:

1. Data foundations — canonical, governed datasets with one source-of-truth model per concept, near-duplicates aggressively deprecated, and standards enforced by tooling, CI, and mandate. Maintain metadata (column descriptions, grain documentation, ownership, model tiering) with the same rigor as the transformations ([Anthropic blog](https://claude.com/blog/how-anthropic-enables-self-service-data-analytics-with-claude)).
2. Sources of truth — reference surfaces in descending order of trust: a semantic layer (compiled metric definitions: one call, one number), a lineage and transformation graph (which upstream models feed a concept, which are deprecated, which share grain), a query corpus (raw material for curation, not direct retrieval), and business context (a knowledge graph of docs, roadmaps, and decision logs so the agent can resolve "the Q2 launch" or "the fraud question").
3. Skills — the procedural counterpart to declarative sources. A 'knowledge' skill is a thin top-level router that narrows the search space to a few dozen curated reference files before any query is written. An 'unbook' skill encodes senior-analyst process (clarify → find sources → run query → adversarial review) and bundles reusable analysis patterns. Without skills, Anthropic's accuracy ceiling was ≤21%; with them, >95% in aggregate ([Anthropic blog](https://claude.com/blog/how-anthropic-enables-self-service-data-analytics-with-claude)).
4. Validation — offline evals pinned to snapshot data, ablation at PR granularity, and online provenance footers with passive monitoring of semantic-layer hit-rate and correction language. See [Behavioral Testing for Agents](../../verification/behavioral-testing-agents.md) for the eval discipline these tiers depend on.

[Separation of Knowledge and Execution](separation-of-knowledge-and-execution.md) generalizes layers 2 and 3: declarative knowledge (sources of truth) lives separately from procedural knowledge (skills), and both are versioned independently of the agent that composes them.

## Why it works

The structural mechanism is ambiguity elimination by construction, not better retrieval. The most informative ablation in Anthropic's stack ran like this: the team gave the agent direct grep access to the entire dashboard, transformation, and analyst-notebook SQL corpus (thousands of files), verified the agent actually read them before each answer, and measured the accuracy change. Accuracy moved by less than one point in either direction — even though the answer was present in the corpus about 80% of the time for the questions the agent got wrong, and "answer present" did not predict "now gets it right" ([Anthropic blog](https://claude.com/blog/how-anthropic-enables-self-service-data-analytics-with-claude)).

The information was there. The agent saw it. The agent still did not use it. The bottleneck was not access — it was structure: mapping a question to the right entity. A semantic-layer call returns a deterministic value for a defined metric; direct SQL returns a number from one of many plausibly correct interpretations. Independent enterprise benchmarks report 85–95% accuracy when dimensions are mapped and synonyms registered through a semantic layer ([dbt: Semantic Layer vs. Text-to-SQL benchmark 2026](https://docs.getdbt.com/blog/semantic-layer-vs-text-to-sql-2026); [VentureBeat: Headless vs. native semantic layer](https://venturebeat.com/ai/headless-vs-native-semantic-layer-the-architectural-key-to-unlocking-90-text)). GitHub reaches the same conclusion independently of Anthropic: its internal plain-language analytics agent succeeded by routing questions through governed, structured data sources rather than granting broad warehouse access ([GitHub: How we built an internal data analytics agent](https://github.blog/ai-and-ml/github-copilot/how-we-built-an-internal-data-analytics-agent/)). The pattern echoes the broader [CoALA Structured Action Space](coala-structured-action-space.md): typed, governed actions surface the cost and reversibility profiles that monolithic tool lists hide.

## When this backfires

The pattern earns its complexity only when you have the platform discipline to maintain it. The layered approach is worse than direct warehouse access under these conditions:

- No semantic-layer ownership. Without a human owner per canonical metric and CI enforcement of definitions, the layer decays. Anthropic saw offline accuracy drift from ~95% at launch to ~65% over one month before they treated skill-doc maintenance as an engineering problem. A code-review hook now flags any reporting-model PR that does not touch a skill file, and ~90% of data-model PRs include a skill change in the same diff ([Anthropic blog](https://claude.com/blog/how-anthropic-enables-self-service-data-analytics-with-claude)).
- LLM-bootstrapped metric definitions. Auto-generating canonical metrics from raw tables and query logs encodes the very ambiguities the layer was meant to eliminate; Anthropic measured this net-negative on their eval set versus a smaller, human-curated layer. Generate documentation with the model; keep the definition human-owned ([Anthropic blog](https://claude.com/blog/how-anthropic-enables-self-service-data-analytics-with-claude)).
- Highly exploratory analytics outside modeled scope. Semantic layers can only answer questions inside their coverage. For long-tail exploratory queries, text-to-SQL fallback is required regardless; over-investing in semantic modeling for low-frequency questions yields negative ROI, and a hybrid surface is recommended ([dbt blog](https://docs.getdbt.com/blog/semantic-layer-vs-text-to-sql-2026)).
- Semantic debt at scale. Each new team, region, or request adds definitions and exceptions; without governance discipline the layer accumulates "semantic debt" that slows analytics, undermines confidence, and becomes increasingly expensive to untangle — eventually worse than the multi-candidate state it replaced ([Strategy.com: The hidden cost of semantic debt](https://www.strategy.com/software/blog/the-hidden-cost-of-semantic-debt-in-enterprise-data-models); [AtScale: The Costly Semantic Layer Mistake](https://www.atscale.com/blog/semantic-layer-mistakes-data-leaders/)).
- Adversarial reviewer cost ignored. The online adversarial-review skill adds +6% accuracy but costs +32% more tokens and +72% higher latency in Anthropic's measurements; swapping it for a cheaper model lost most of the accuracy wins with no real speedup. Apply it where the consequences of a silent wrong answer justify the cost; skip it for low-stakes lookups ([Anthropic blog](https://claude.com/blog/how-anthropic-enables-self-service-data-analytics-with-claude)).

## Example

The Anthropic skill template separates a domain's routing logic from its reference content. The 'knowledge' skill is the entry point — narrow, deterministic, with explicit routing rules. The reference docs it points to are written for LLM retrieval, not human onboarding.

```markdown
# [Domain] Tables

## Quick Reference
### Business Context — [what this domain means in plain words]
### Entity Grain — [what one row represents]
### Standard Hygiene Filter — [the filter every query in this domain applies]

## Dimensions
- [How key dimensions are encoded, and how the same concept is named
  differently across tables]

## Key Tables
### [table_name]
- **Grain**: [...] · **Scope/exclusions**: [...]
- **Usage**: [when to use it, when NOT to, join keys, required filters]

## Gotchas
- [The wrong-answer modes a senior analyst would warn you about]

## Best Practices / Common Query Patterns
- [Default choices, standard cuts, worked patterns where the exact query
  form is the hard part]

## Cross-References
- [Neighboring domain docs that own adjacent questions]
```

Source: [Anthropic blog appendix](https://claude.com/blog/how-anthropic-enables-self-service-data-analytics-with-claude). Routing triggers are written as explicit conditionals (`IF the question is about experiment lift... DO NOT use for raw event counts`) rather than prescriptive recipes that go stale as schemas evolve.

## Key Takeaways

- Analytics accuracy is a structure problem, not a retrieval problem — direct corpus access moved Anthropic's accuracy by less than one point even when the answer was present and demonstrably read.
- Route agents through a tiered source-of-truth surface (semantic layer → lineage → curated reference → business context) and require the structural call by skill instruction, not by hope.
- Treat skill maintenance as engineering: colocate skill markdown with transformation models, gate model PRs on skill updates, and watch for the ~95% → ~65% accuracy drift that signals maintenance neglect.
- Validate with offline eval suites pinned to snapshots, ablation at PR granularity, and online provenance footers — without these, you cannot tell which of the three failure modes is leaking.

## Related

- [Separation of Knowledge and Execution](separation-of-knowledge-and-execution.md) — the three-layer skills/agents/commands pattern this page specializes for analytics.
- [CoALA Structured Action Space: Internal vs External Actions](coala-structured-action-space.md) — typed action boundaries that surface cost and reversibility, the same discipline applied at a higher abstraction level.
- [Cognitive Reasoning vs Execution: A Two-Layer Agent Architecture](cognitive-reasoning-execution-separation.md) — typed tool interfaces enforce the reason/act boundary that semantic-layer routing relies on.
- [Layered Context Architecture](../../context-engineering/layered-context-architecture.md) — ground agents in multiple distinct context sources rather than relying on any single signal.
- [Behavioral Testing for Agents](../../verification/behavioral-testing-agents.md) — capability matrices and grading methods that the validation layer of the four-layer stack depends on.
