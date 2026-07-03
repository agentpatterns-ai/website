---
title: "Compositional Skill Routing for Large Skill Libraries"
term: "Compositional Skill Routing"
description: "Decompose a query into atomic sub-tasks, retrieve one skill per sub-task, then compose the plan — earns its cost only above hundreds of skills."
aliases:
  - skill routing
  - decompose-retrieve-compose
  - SkillWeaver
  - skill-aware decomposition
tags:
  - context-engineering
  - agent-design
  - tool-agnostic
  - arxiv
  - rag
  - skills
last_reviewed: 2026-06-20
maturity: emerging
---

# Compositional Skill Routing for Large Skill Libraries

> Decompose a query into atomic sub-tasks, retrieve one skill per sub-task, then compose the plan — earns its cost only above hundreds of skills.

Compositional skill routing replaces single-shot tool selection with a three-stage pipeline — a task decomposer breaks the query into atomic sub-tasks, a bi-encoder retriever fetches the best-matching skill for each, and a DAG planner composes the executable plan ([Gao 2026](https://arxiv.org/abs/2606.18051)). It earns its engineering cost only at MCP-scale skill libraries; below the threshold, the simpler preload-or-rerank baselines dominate.

## When the conditions hold

The pattern is qualified, not unconditional. Four conditions must hold before decompose-retrieve-compose beats single-shot retrieval or preload-and-route:

| Condition | Why it matters |
|----------|----------------|
| Library holds hundreds to thousands of skills | The headline >99% context-window reduction in [Gao (2026)](https://arxiv.org/abs/2606.18051) is measured against 2,209 MCP server skills. At 50 skills, prompt caching and preloading remove most of the pressure; the extra LLM call to decompose costs more than it saves |
| Queries span multiple skills per turn | Decomposition only earns its keep when the typical query is compositional. A library of 2,000 skills serving one-skill-at-a-time queries is the SkillRouter case — single-shot retrieve-and-rerank reaches [74.0% Hit@1 at ~80K skills](https://arxiv.org/abs/2603.22455) without any decomposition |
| Sub-tasks are loosely coupled | The composer is a dependency-aware DAG. If sub-tasks need feedback between steps (output of step 2 changes what step 3 should look like), a pre-committed DAG cannot recover. Dynamic re-decomposition mid-flight is a separate, harder problem ([TDAG, 2402.10178](https://arxiv.org/abs/2402.10178)) |
| Skill descriptions are unambiguous | The bi-encoder retriever tells skills apart by their description text. If two skills overlap functionally, no amount of decomposition rescues retrieval — Anthropic's [guidance is that "if a human engineer can't pick, the agent can't either"](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) |

Outside these conditions, the pattern adds a decoder call, a retriever round-trip, and a new cascading-error surface for negligible context savings.

## The three stages

Decompose. An LLM task decomposer breaks the user query into atomic sub-tasks — each sub-task should map to roughly one skill. Standard decomposition reaches only [34.2% category recall at the step level](https://arxiv.org/abs/2606.18051) because the decomposer chunks by linguistic structure, not by what skills exist.

Retrieve. A bi-encoder embedding model with FAISS indexing returns the top-k skills for each atomic sub-task. Retrieval over atomic sub-tasks works because each query now aligns roughly 1:1 with one skill, instead of carrying the mixed semantics of a compositional query ([Gao 2026](https://arxiv.org/abs/2606.18051)). Hiding skill implementation details to save tokens [drops routing accuracy 31–44 percentage points](https://arxiv.org/abs/2603.22455) — the full skill text matters at retrieval time.

Compose. A dependency-aware planner assembles the retrieved skills into an executable DAG. It resolves step ordering and data dependencies before execution begins ([Gao 2026](https://arxiv.org/abs/2606.18051)).

## Iterative skill-aware decomposition (SAD)

Plain decomposition is not enough. The paper's central contribution is the feedback loop that aligns decomposition with the skills actually available: after a first decomposition, retrieve candidates for each sub-task, feed the retrieval results back to the decomposer, and re-chunk. One iteration of SAD lifts decomposition accuracy from [51.0% to 67.7% (p < 10⁻⁶)](https://arxiv.org/abs/2606.18051). When decomposition accuracy reaches 1, category recall jumps from 34% to 41% — which confirms that decomposition quality, not retriever quality, is the bottleneck.

## Why it works

The mechanism is granularity alignment — the same principle that drives [retrieval-augmented agent workflows](retrieval-augmented-agent-workflows.md). A monolithic query like "book a flight to Tokyo and email my team the itinerary" hits a bi-encoder retriever with mixed semantics. No skill matches, because the query contains two skill-shaped sub-intents. Decomposing into atomic sub-tasks restores 1:1 semantic alignment, which is why category recall jumps once decomposition is correct ([Gao 2026](https://arxiv.org/abs/2606.18051)). The SAD loop adds a second alignment: feeding retriever hits back to the decomposer lets it re-chunk along the catalog's actual seams rather than linguistic structure.

The broader pattern already ships in products. Anthropic's [Tool Search Tool](https://www.anthropic.com/engineering/advanced-tool-use) reports an 85% token reduction on large libraries and lifts Opus 4 accuracy from 49% to 74% (Opus 4.5: 79.5% → 88.1%) by deferring tool definitions and retrieving on demand.

## When this backfires

- Small libraries (under 50 skills). The >99% context-saving headline measures against a 2,209-skill baseline. With 50 skills and prompt caching, preloading every schema is cheap; adding a decomposer call costs more than the savings and adds decomposition-error risk for no gain.
- Failed decomposition cascades. SAD reaches 67.7% accuracy, so roughly one in three queries still decomposes incorrectly. On those, every downstream retrieval and compose step is wasted. [Survey work on agent failures](https://arxiv.org/abs/2509.25370) finds early decomposition mistakes "rarely remain confined" — they propagate through the trajectory.
- Tightly-coupled sub-tasks. A pre-committed DAG cannot recover when step 2's output should change step 3's plan. [TDAG (2402.10178)](https://arxiv.org/abs/2402.10178) formalizes this as Cascading Task Failure and argues for dynamic re-decomposition; one-iteration SAD does not fully address it.
- Ambiguous or overlapping skills. The bi-encoder cannot tell functionally overlapping skills apart from descriptions alone. Decomposition does not fix a poorly-curated catalog — [Anthropic's guidance applies](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents): if a human engineer cannot pick the right skill, the agent cannot either.
- Latency-sensitive paths. Decompose, retrieve, and plan adds at least one extra LLM round-trip before any real work begins. For sub-second interactive paths this overhead is dead weight that preload-and-route avoids.

## Example

Anthropic's Tool Search Tool is the closest practitioner-ready expression of this pattern. The startup prompt declares tools with `defer_loading: true`; only the search tool is loaded by default, and the model retrieves skills at runtime:

```json
{
  "type": "tool_search_tool_20251119",
  "name": "tool_search_tool"
}
```

Individual tools are marked deferred:

```json
{
  "name": "jira_create_issue",
  "description": "Create a Jira issue",
  "defer_loading": true
}
```

At inference, the agent issues a tool-search call, retrieves the small subset of skills the current sub-task actually needs, and then calls them. The compositional layer — a decomposer that breaks `"file a Jira issue and post the link to Slack"` into two atomic searches — sits above this API. Anthropic reports [average usage dropping from 43,588 to 27,297 tokens (37% reduction)](https://www.anthropic.com/engineering/advanced-tool-use) when this is combined with programmatic tool calling, with intermediate results stripped from the model's context.

## Key Takeaways

- The pattern is for libraries in the hundreds-to-thousands of skills — under 50 skills, preload with caching wins on simplicity.
- Decomposition quality, not retrieval quality, is the bottleneck — Iterative Skill-Aware Decomposition closes the gap by feeding retrieval hits back to the decomposer.
- A failed decomposition wastes every downstream step; expect ~30% of queries to still mis-decompose even with SAD.
- Pre-committed DAGs cannot recover from mid-execution evidence — use dynamic re-decomposition for tightly-coupled tasks.
- Hiding skill implementation text to save tokens at retrieval time drops accuracy sharply — the retriever needs the full description.

## Related

- [Retrieval-Augmented Agent Workflows: On-Demand Context](retrieval-augmented-agent-workflows.md)
- [Semantic Context Loading: Language Server Plugins for Agents](semantic-context-loading.md)
- [Context Budget Allocation: Every Token Has a Cost](context-budget-allocation.md)
- [Prompt Chaining: Sequential LLM Calls for Agent Workflows](prompt-chaining.md)
- [Schema-Guided Graph Retrieval](schema-guided-graph-retrieval.md)
