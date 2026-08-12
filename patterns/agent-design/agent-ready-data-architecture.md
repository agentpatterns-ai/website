---
title: "Agent-Ready Data Architecture for Analytics Agents"
term: "Agent-Ready Data Architecture"
description: "Publish grain, join semantics, authoritative markers, and completeness windows in the warehouse. dbt measured a schema-only change: 64.5% to 90% text-to-SQL."
tags:
  - agent-design
  - context-engineering
  - tool-agnostic
aliases:
  - agent-ready data warehouse
  - warehouse design for analytics agents
last_reviewed: 2026-08-12
maturity: adopted
---

# Agent-Ready Data Architecture for Analytics Agents

> Publish grain, join semantics, authoritative markers, and completeness windows in the warehouse itself, since an analytics agent cannot infer them from a schema.

An agent-ready data warehouse publishes the facts an analytics agent would otherwise guess: what one row represents, how tables join, which of several candidate tables is authoritative, and how complete each one is. Three conditions decide whether the work pays back. The facts have to be human-authored, because machine-generated database descriptions lifted SQL accuracy by only 0.93% over no descriptions at all ([arXiv:2502.20657v1](https://arxiv.org/abs/2502.20657v1)). The errors you are attacking have to be schema-linking errors rather than analytical ones. And every change needs per-domain validation, because the same transformation that helps most domains measurably hurts others ([arXiv:2606.03145v1](https://arxiv.org/abs/2606.03145v1)).

This is the layer beneath [Governed Sources of Truth for Analytics Agents](governed-sources-of-truth-analytics-agents.md), which covers which source wins and how a semantic layer routes a question. This page covers what the warehouse must state before anyone can define a governed metric on top of it.

## What the warehouse must publish

Schema metadata gives an agent data types. It does not give business rules, so a field named `campaign_costs` never says whether agency fees are included, currencies normalized, or refunds deducted. The four gaps below come from that same account ([Towards Data Science](https://towardsdatascience.com/building-an-agent-ready-data-warehouse-what-traditional-architectures-do-wrong/)).

| Fact | What breaks when it is missing |
|---|---|
| Grain | The agent picks a table whose name matches the question and aggregates at the wrong level of detail |
| Join semantics | Join relationships are frequently implicit in enterprise schemas, so the agent infers joinable columns with no declared key to check against ([arXiv:2409.02038v3](https://arxiv.org/abs/2409.02038v3)) |
| Authoritative marker | Several valid sources exist; the agent chooses the raw table whose naming matches best, while reconciliation lives in a dashboard it never sees |
| Completeness and restatement window | Partial load history, pre-cancellation revenue, and differing time zones produce a correct calculation over unsuitable data |

Three schema-side moves make these facts legible, all of them semantics-preserving: expose recurring join paths as logical views, restrict the model-facing schema to the tables a workload actually uses, and rename cryptic identifiers descriptively. Across four text-to-SQL pipelines and three model backbones they gained up to 4.2 percentage points of execution accuracy ([arXiv:2606.03145v1](https://arxiv.org/abs/2606.03145v1)).

Access control does not substitute: traditional governance answers who may read a table, never whether it supports a reliable decision ([Towards Data Science](https://towardsdatascience.com/building-an-agent-ready-data-warehouse-what-traditional-architectures-do-wrong/)).

## Why it works

LLM SQL failures concentrate at schema linking, the step that maps a question onto the right tables, columns, and join paths. BEAVER isolates that step by grading five subtasks separately on a benchmark built from private warehouse query logs. Supplying oracle schema-linking annotations raises the ReFoRCE framework from 11.4% to 18.9% accuracy, and oracle annotations for all five subtasks reach 30.1% ([arXiv:2409.02038v3](https://arxiv.org/abs/2409.02038v3)). The model, the questions, and the framework are held constant across those three conditions, so only the supplied facts differ, which places a large share of the failure in the platform rather than in model reasoning. Renaming shows the same effect directly at the linking step, where table-set match on Spider-Union rose from 64.7% to 94.1% ([arXiv:2606.03145v1](https://arxiv.org/abs/2606.03145v1)). A prompt cannot supply a fact nobody wrote down, which is why this is architecture work. It is [harness engineering](harness-engineering.md) applied to the data platform: the environment determines the output.

## When this backfires

- Machine-generated metadata. Generating the descriptions from the tables themselves re-encodes the ambiguity they were meant to remove. Hand-written context is what moves the number: a 4 KB human-authored semantic document took three frontier models from 45.5–50.5% to 67.7–68.7% ([arXiv:2604.25149v1](https://arxiv.org/abs/2604.25149v1)).
- Analytical failures rather than linking failures. Window functions, multi-CTE decomposition, and subtle predicates survive oracle annotation; 46.8% of BEAVER residual errors are analytical-construct failures ([arXiv:2409.02038v3](https://arxiv.org/abs/2409.02038v3)).
- Global rollout without per-domain checks. The schema transformations are non-monotonic. One BIRD domain regressed 5.4%, 42 queries got worse against 74 improved, and aggressive partitioning pruned tables the question needed ([arXiv:2606.03145v1](https://arxiv.org/abs/2606.03145v1)).
- Small, already-legible schemas. The payoff tracks schema size and opacity. Spider and BIRD databases average 6.8 tables and 72.5 columns, against 101.5 tables and 869.4 columns in BEAVER's private warehouses, and ReFoRCE drops from 62.9% on Spider 2.0 to 11.4% on BEAVER ([arXiv:2409.02038v3](https://arxiv.org/abs/2409.02038v3)). A compact, well-named schema leaves much less to recover.
- Waiting it out is a real alternative. On an unchanged schema, model progress alone took text-to-SQL from 32.7% in 2023 to 64.5% in 2026, and a bounded semantic layer already reaches 98.2–100% on the queries it covers while refusing the rest instead of returning a confident wrong number ([dbt Labs](https://docs.getdbt.com/blog/semantic-layer-vs-text-to-sql-2026)).

## Example

dbt Labs ran 11 questions 20 times each against a heavily normalized third-normal-form schema. Text-to-SQL scored 64.5% for both Claude Sonnet 4.6 and GPT-5.3 Codex. They then had an LLM add the minimum modeling needed, which came to three dbt models joining a few tables, and reran the identical benchmark ([dbt Labs](https://docs.getdbt.com/blog/semantic-layer-vs-text-to-sql-2026)).

| Configuration | Sonnet 4.6 | GPT-5.3 Codex |
|---|---|---|
| Text-to-SQL, original 3NF schema | 64.5% | 64.5% |
| Text-to-SQL, three added models | 90.0% | 84.1% |

Nothing about the model, the prompt, or the questions changed between the two rows. dbt's own summary is that better modeling helps both approaches. One caveat they state: to make text-to-SQL work they loaded the entire schema into context, which is not practical for larger datasets.

## Key Takeaways

- Budget the work against your error mix. Warehouse metadata recovers schema-linking errors and leaves analytical-construct errors untouched, so measure which class dominates before funding a redesign.
- Human-author the four facts and give each an owner. Grain, join keys, the authoritative marker, and the completeness window are the inputs a semantic layer's authors need too, so publishing them once serves both surfaces.
- Roll schema transformations out per domain against a held-out query set, since the measured effect includes regressions.
- On real private warehouses, frontier agents score around 11% and cap near 30% even with perfect human annotation ([arXiv:2409.02038v3](https://arxiv.org/abs/2409.02038v3)). Scope the agent to a covered surface rather than promising warehouse-wide question answering.

## Related

- [Governed Sources of Truth for Analytics Agents (Structure Over Access)](governed-sources-of-truth-analytics-agents.md) — the semantic-layer and skill-routing tier that sits above the warehouse facts this page covers.
- [Harness Engineering for Building Reliable AI Agents](harness-engineering.md) — the general form of the argument that environment design outranks prompting.
- [Codebase Readiness for Agents: Agent-Friendly Code](codebase-readiness.md) — the same legibility discipline applied to a code repository instead of a data platform.
- [Separation of Knowledge and Execution](separation-of-knowledge-and-execution.md) — versioning declarative knowledge apart from the agent that consumes it.
- [Layered Context Architecture](../../context-engineering/layered-context-architecture.md) — grounding an agent in several distinct context sources rather than one.
