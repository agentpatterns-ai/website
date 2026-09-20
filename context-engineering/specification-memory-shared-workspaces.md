---
title: "Specification Memory: What a Shared Agent Workspace Keeps"
term: "Specification Memory"
description: "Persist the four categories of user-authored context a session established and discard the transcript: the store that kept less completed 12/12 trials at the token cost of keeping nothing."
tags:
  - context-engineering
  - memory
  - tool-agnostic
  - arxiv
aliases:
  - shared selective persistent memory
  - selective workspace memory
  - specification-carrying workspace
last_reviewed: 2026-09-19
maturity: emerging
status: current
---

# Specification Memory: What a Shared Agent Workspace Keeps

> Drop the transcript and carry only the constraints a session established; that workspace completed 12 of 12 trials where a replayed transcript completed 8.

Specification memory is a cross-session store holding four categories of user-authored context: task specifications, data schemas, tool configurations and output constraints. Everything the agent produced on its way to an answer is discarded. In a replication across four public datasets, the condition carrying that store completed 12 of 12 trials at 3.9K input tokens. An agent carrying nothing completed 0 of 12 at 3.8K, and one replaying the prior transcript completed 8 of 12 at 7.7K ([Pedada et al., 2026](https://arxiv.org/abs/2607.09493v2)). Both differences from no memory survive Bonferroni-corrected exact McNemar tests, at p=0.0005 and p=0.008.

## When this applies

The result holds under three conditions, and the third is the one people skip.

- The task recurs against a stable schema. The authors limit the zero-token refresh path to "structured tabular data with stable schemas", and put streaming data, unstructured documents and real-time API responses out of scope ([Pedada et al., 2026](https://arxiv.org/abs/2607.09493v2)).
- The user will not restate the constraint anyway. On a separate corpus of 24 enterprise tasks where the user re-specified everything, an agent with no memory still reached 79% completion, taking 4.3 turns against 1.4. The authors put it plainly: "Persisted context does not improve what an agent can do when the user will say everything again; it removes the need to." ([Pedada et al., 2026](https://arxiv.org/abs/2607.09493v2))
- The constraint is declared rather than discovered. Where the rule has to be mined from usage instead, Databricks measured the opposite result on a comparable enterprise data-agent task: memory built from uncurated user logs and filtered only by an automated judge rose "from 2.5% to over 50%, surpassing the expert-curated baseline (33.0%) after just 62 log records" ([Databricks](https://www.databricks.com/blog/memory-scaling-ai-agents)).

## What the store keeps

| Category | What it holds |
|---|---|
| Task specifications | Domain rules, output preferences and quality constraints, authored by users and refined over sessions |
| Data schemas | Column names and types, distributions for numeric columns, value catalogs for categorical ones, row counts, sample rows |
| Tool configurations | Connectors and their parameter schemas, invocation patterns, authentication requirements |
| Output constraints | The contract between the generated artifact and its runtime, above all that it reads data from an injection point rather than from hardcoded values |

Six classes are dropped: intermediate temporary files, unapproved changes, reasoning traces, tool invocation logs, error recovery paths, and the raw data itself, which the schema summary replaces ([Pedada et al., 2026](https://arxiv.org/abs/2607.09493v2)).

Transferability follows from that drop list. A workspace holds the four categories plus the latest artifact and its version history, and it "stores structured configuration, generated code, and version metadata, never conversational transcripts, reasoning traces, or tool invocation logs" ([Pedada et al., 2026](https://arxiv.org/abs/2607.09493v2)). A colleague loads it, connects their own data source and asks for refinements inside the established context, under one of three roles: owners control the workspace, stewards edit artifacts and task specifications, and viewers query without modifying the base.

## Why it works

The price half is arithmetic. Both memory conditions carry the specification, and completion tracks that one criterion: "every no-memory failure is a spec failure and nothing else" ([Pedada et al., 2026](https://arxiv.org/abs/2607.09493v2)). The typed store carries the constraint for 3.9K input tokens. The transcript carries the same constraint for 7.7K, because it also carries the reasoning, the tool logs and the error-recovery paths of one earlier execution, none of which bear on the next task. Counting input and output together, the store is the cheapest of the three at 8.2K tokens per task against 9.3K for no memory and 11.2K for full history. The condition that completed every trial cost less than the one that completed none.

Why the transcript also completes fewer trials is unsettled, and the authors decline to claim it. Their four full-history failures produced no artifact at all rather than a non-compliant one, so they record the result "as instability under transcript injection rather than as evidence of trace anchoring, which would predict a non-compliant artifact rather than none" ([Pedada et al., 2026](https://arxiv.org/abs/2607.09493v2)). Treat the cost as established and the interference as reported.

## When this backfires

- Relationships between sources vanish. The one selective-memory failure across 24 enterprise tasks was a join across two uploaded files. Schemas are profiled per source and record no cross-source keys, so the prompt described both tables without saying how they related. The authors call this "a structural limit of schema-summary-as-memory" ([Pedada et al., 2026](https://arxiv.org/abs/2607.09493v2)).
- Wide tables erase the token argument. Summary size is flat in row count and linear in columns, running 339 tokens for 4 columns and 4,486 for 44. Measured against truncation rather than raw injection, the saving falls to 2-3x, and to 2.05x on the widest table ([Pedada et al., 2026](https://arxiv.org/abs/2607.09493v2)).
- Structure buys retrieval economy, not answer quality. Zhou et al. found organized memory stores "roughly halve retrieval cost where material is large", while "no agent we measure converts organization itself into better answers" ([Zhou et al., 2026](https://arxiv.org/abs/2607.26637v1)).
- Specifications go stale with nothing to catch it. Memory decay is unimplemented in the measured system, and the user-study participants asked for it ([Pedada et al., 2026](https://arxiv.org/abs/2607.09493v2)).
- Sharing is all or nothing. Collaboration works at workspace level, and the authors record finer-grained sharing of individual components as unsupported, so a wrong task specification reaches everyone who loads the workspace ([Pedada et al., 2026](https://arxiv.org/abs/2607.09493v2)).
- The evidence has named gaps. The authors report no hand-written instructions-file baseline, which they call "the comparison a practitioner would make", no summarized-history condition, no per-category ablation, one model family, and one run per cell. The 12/12 against 8/12 gap does not reach significance at p=0.125, where roughly 21 trials per condition would be needed ([Pedada et al., 2026](https://arxiv.org/abs/2607.09493v2)).

## Example

The experiment that separates the conditions is cheap to reproduce on your own harness. Phase one generates an artifact from the full task prompt plus a formatting specification, which establishes the constraint. Phase two reuses one instruction over updated, schema-compatible data and never restates the specification. In the paper that instruction reads "Regenerate the dashboard with this updated data." Conditions differ only in what they carry across.

Score on a criterion only the constraint could satisfy. The paper's specification named a background color appearing in no task prompt, so an artifact shows that color only if the specification reached the session. Structural checks do not discriminate here: a valid render, a parser present, correct column references and no hardcoded data are satisfied by any working pipeline. The no-memory artifacts scored 7 of the 8 criteria and failed on the eighth ([Pedada et al., 2026](https://arxiv.org/abs/2607.09493v2)).

## Key Takeaways

- Audit what your store keeps by category before you tune how much it keeps; more retained context completed fewer trials in both experiments.
- Price the transcript against the specification before replaying one. The same constraint cost 3.9K input tokens as a typed spec and 7.7K as a transcript.
- Any memory experiment needs a criterion only the memory could satisfy, because structural checks pass on artifacts that never received the specification.
- Transferability comes from the discard list: a set of declared constraints can be handed to a colleague, a chat transcript cannot.
- Schema summaries describe sources one at a time, so a task spanning two tables needs the join expressed somewhere else.
- Where the rule has to be learned from usage rather than declared up front, mined logs beat a hand-written expert baseline.

## Related

- [Per-Type Retention Policy for Agent Compaction (Knowledge Triage)](per-type-retention-under-compaction.md) — type-aware retention at the compaction boundary inside one session, where this page's boundary is session to session
- [Agent Memory Patterns: Learning Across Conversations](../patterns/agent-design/agent-memory-patterns.md) — the scope-and-time model for agent-learned facts, without the cost curve this page measures
- [Persistent Teammate Workspace: Durable State for Agent Teams](../patterns/agent-design/persistent-teammate-workspace.md) — the same durability question for a Claude Code agent team, and the counter-result on curation cost
- [Stateful Iteration State-Carry: Typed Persistent State for Long Agent Loops](stateful-iteration-state-carry.md) — typed state carried turn to turn inside one loop rather than across sessions
- [Usage-Reinforced Memory Decay for Long-Running Agents](usage-reinforced-memory-decay.md) — the aging mechanism this architecture leaves unimplemented
