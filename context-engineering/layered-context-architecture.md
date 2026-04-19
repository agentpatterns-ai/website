---
title: "Layered Context Architecture for AI Agent Development"
description: "Ground agents in multiple distinct context sources — schema, code, institutional knowledge, and persistent memory — rather than relying on any single signal"
aliases:
  - Agent Memory Patterns
  - Multi-Layer Context Grounding
tags:
  - context-engineering
  - agent-design
---

# Layered Context Architecture

> Ground agents in multiple distinct context sources — schema, code, institutional knowledge, and persistent memory — rather than relying on any single signal.

!!! info "Also known as"
    Agent Memory Patterns, Multi-Layer Context Grounding

## Why Schema Alone Is Insufficient

Schema is necessary but not sufficient. Tables that look similar may differ in critical ways that only the pipeline code producing them clarifies — for example, whether a table includes first-party-only traffic or all traffic.

[OpenAI's data agent](https://openai.com/index/inside-our-in-house-data-agent/) demonstrates this. For a corpus of 70,000 datasets, schema metadata alone could not distinguish tables with similar names but different inclusion criteria. The difference lived in the transformation code.

## The Six-Layer Model

OpenAI's data agent uses six context layers, aggregated offline and retrieved at runtime:

| Layer | What It Provides |
|-------|-----------------|
| Table usage and lineage | Which queries use this table, what it feeds downstream |
| Human annotations | Notes, warnings, and clarifications added by data owners |
| Code-derived enrichment | Column meanings inferred from the pipeline code that produces them |
| Institutional knowledge | Launches, incidents, canonical metric definitions from wikis and Slack |
| Persistent memory | Corrections and constraints accumulated from prior agent interactions |
| Live runtime queries | Fresh values queried at request time for volatile data |

Each layer addresses blind spots in the others. Code enrichment fills the gap schema leaves. Institutional knowledge explains anomalies neither schema nor code captures. Persistent memory surfaces corrections not documented elsewhere.

## The Coding Agent Analogue

For a coding agent, the layers map to:

| Layer | Coding agent equivalent |
|-------|------------------------|
| File structure | Directory tree, module boundaries |
| Language server symbols | Types, interfaces, function signatures, references |
| Repository history | `git log`, commit messages, PR descriptions |
| ADRs and RFCs | Architecture decision records, design documents |
| Memory | Per-repo conventions the agent has learned from corrections |
| Live queries | Current build status, open issues, recent test results |

No single layer is complete. Types express intent but not rationale. Git history records what changed but not why. ADRs record decisions but not the code that implements them.

## Offline Pipeline, Runtime RAG

Loading all six layers per request is impractical — volume exceeds any context window. The architecture separates concerns:

- **Offline**: aggregate all layers into normalized embeddings, refreshed on a schedule
- **Runtime**: retrieve the most relevant subset for the current query via retrieval-augmented generation (RAG)

Latency stays predictable regardless of corpus size. The agent receives the context most relevant to its task, not everything that might be relevant.

A [survey of Agentic RAG architectures](https://arxiv.org/abs/2501.09136) confirms production systems combine heterogeneous sources — structured queries, semantic search, graph knowledge bases, and tool APIs — with specialized agents handling each source in parallel.

## Priority of Layers

Layers are not equal. When a human annotation contradicts what the pipeline code suggests, the resolution order must be explicit. Human annotations typically take priority over code-derived enrichment, which takes priority over schema inference. Persistent memory corrections outrank general institutional knowledge.

Document the resolution order. An agent that silently favors code over an annotation will be wrong in exactly the cases the annotation exists to correct.

## Retrieval Noise Is Real

More layers do not monotonically improve accuracy. An [arxiv analysis of RAG as noisy in-context learning](https://arxiv.org/abs/2506.03100) derives bounds showing retrieval gains shrink with more examples and can flip to hurt performance past a threshold. Practitioner reports on [RAG at scale](https://www.goml.io/blog/stanford-ai-research-rag-systems) describe precision drops beyond ~10,000 documents and collapse past ~50,000. Before adding a layer, confirm the blind spot it closes causes real production errors, not a theoretical gap.

## Example

The following TypeScript snippet shows a coding agent that retrieves context from multiple layers at runtime before answering a question about a function. Each layer fills a blind spot the previous one leaves.

```typescript
// runtime RAG: assemble context from multiple layers before calling the model
async function buildContext(symbolName: string): Promise<string[]> {
  const chunks: string[] = [];

  // Layer 1 — file structure and module boundaries (always available)
  const fileTree = await getDirectoryTree("src/");
  chunks.push(`File structure:\n${fileTree}`);

  // Layer 2 — language server: type signature and references
  const signature = await lspHover("src/", symbolName);
  const refs = await lspReferences("src/", symbolName);
  chunks.push(`Type signature:\n${signature}`);
  chunks.push(`Referenced in: ${refs.join(", ")}`);

  // Layer 3 — git history: what changed and why
  const log = await execGit(`log --oneline -10 -- src/ | grep ${symbolName}`);
  chunks.push(`Recent commits:\n${log}`);

  // Layer 4 — ADR / design docs: rationale
  const adr = await searchDocs(`docs/decisions/`, symbolName);
  if (adr) chunks.push(`Architecture note:\n${adr}`);

  // Layer 5 — persistent memory: corrections from prior sessions
  const memory = await readMemory(`corrections/${symbolName}.md`);
  if (memory) chunks.push(`Prior correction:\n${memory}`);

  return chunks;
}
```

Each `chunks.push` call adds a layer. The type signature tells the agent what the function accepts; the git log tells it what recently changed and why; the ADR captures the design rationale; the memory entry surfaces a correction that isn't recorded anywhere else. No single layer would be sufficient — the type signature says nothing about the rationale, and the ADR says nothing about the current signature.

## When This Backfires

The six-layer model is optimized for large, complex corpora. It carries real engineering overhead.

- **Small corpora** — a codebase that fits in a context window gains nothing from RAG latency. Loading directly is simpler and faster.
- **Infrastructure cost** — aggregation pipelines, embedding refresh, and vector stores add operational surface. For teams without existing data infrastructure, maintenance can outweigh accuracy gain.
- **Layer staleness** — when offline pipelines and live queries diverge (e.g., an un-propagated schema change), the agent acts on contradictory context.
- **Priority rule complexity** — as layers multiply, explicit priority rules get harder to maintain. An undocumented exception silently produces wrong answers that are difficult to trace.

A two-layer approach (schema + live queries) suffices for many agents. Add layers only when each source closes a production error, not a theoretical gap.

## Key Takeaways

- Schema or file structure alone cannot ground an agent in the meaning of a dataset or codebase.
- Six context layers — usage/lineage, annotations, code enrichment, institutional knowledge, persistent memory, live queries — provide coverage no single source can match.
- Use an offline aggregation pipeline and runtime RAG to keep latency predictable across large corpora.
- Define explicit priority when layers conflict; human annotations typically override inferred context.

## Related

- [Retrieval-Augmented Agent Workflows](retrieval-augmented-agent-workflows.md)
- [Agent Memory Patterns: Learning Across Conversations](../agent-design/agent-memory-patterns.md)
- [Seeding Agent Context: Breadcrumbs in Code](seeding-agent-context.md)
- [Three Knowledge Tiers: Sourced, Unverified, Hallucinated](../instructions/three-knowledge-tiers.md)
- [Context Hub](context-hub.md)
- [Phase-Specific Context Assembly](phase-specific-context-assembly.md)
- [Semantic Context Loading](semantic-context-loading.md)
- [Context Budget Allocation: Every Token Has a Cost](context-budget-allocation.md)
- [Context Compression Strategies](context-compression-strategies.md)
- [Context Priming](context-priming.md)
- [Context Engineering: The Practice of Shaping Agent Context](context-engineering.md)
- [Discoverable vs Non-Discoverable Context](discoverable-vs-nondiscoverable-context.md)
- [Prompt Layering: How Instructions Stack and Override](prompt-layering.md)
- [Repository Map Pattern](repository-map-pattern.md)
- [Lost in the Middle: Understanding U-Shaped Attention](lost-in-the-middle.md)
- [Repository-Level Retrieval for Code Generation](repository-level-retrieval-code-generation.md)
- [Schema-Guided Graph Retrieval](schema-guided-graph-retrieval.md)
- [Structured Domain Retrieval](structured-domain-retrieval.md)
- [Environment Specification as Context](environment-specification-as-context.md)
