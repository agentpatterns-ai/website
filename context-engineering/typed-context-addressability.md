---
title: "Typed Context Buys Addressability, Not Token Savings"
term: "Typed Context"
description: "Schema-bearing context records cost more tokens than the prose they replace. The payoff is a harness that can prune, validate, and gate what reaches the model."
tags:
  - context-engineering
  - agent-design
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - context type system
  - schema-bearing context
last_reviewed: 2026-08-25
maturity: emerging
---

# Typed Context Buys Addressability, Not Token Savings

> Typed context spends more tokens than the prose it replaces. What you buy is a harness that can prune, validate, and gate the payload.

Typed context stores every item the agent will see as a discrete record carrying a declared type and schema, rather than appending it to one growing string. A tool result enters as `TOOL_OUTPUT` and a retrieved fact as `EVIDENCE`, labels drawn from one practitioner implementation ([Towards Data Science, 2026](https://towardsdatascience.com/ai-agents-dont-need-more-context-they-need-typed-context/)). The harness serializes those records into a prompt at the end of the turn. The usual pitch says this saves tokens. It spends them, and the reason to adopt it anyway is that a program can act on the context before the model ever reads it.

## The token premium is real

Schema-bearing serialization is the expensive direction, because every record restates its own field names. Deekeswar finds that "key repetition accounts for the majority of JSON overhead," with indentation in nested structures explaining a further 4-percentage-point gap between flat and hierarchical payloads ([Deekeswar, 2026](https://arxiv.org/abs/2604.17512v1)). The same work measures 46 to 51% token reduction when moving away from JSON to a columnar notation, and puts 1,000 IoT sensor readings serialized as JSON at roughly 80,000 tokens.

The per-turn re-reading cost that typing is supposed to remove is already priced, too. Prefix caching bills a repeated prompt prefix at 10% of the base input rate, and the discount requires an exact byte-level match ([Anthropic prompt caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)). An append-only transcript satisfies that by construction. A typed store that re-orders or re-serializes its fields each turn writes a fresh prefix instead, forfeiting the cheap reads and paying a 125 to 200% write premium on top.

## Why it works

The payoff lands outside the transformer. Once each item is a separate record with a type and a source, a program can drop it, summarize it, validate it, or refuse to move it between channels. None of those operations is expressible over an undifferentiated string, and that gap is the mechanism.

The lever is large enough to measure. On a 50-task hotel expense benchmark with GPT-5, keeping the full conversation history scored 71.0% completion at 1,480,996 tokens. Pruning to the last five tool interactions and adding automated summarization scored 91.6% at 553,374 tokens ([Lodha et al., 2026](https://arxiv.org/abs/2606.10209v1)). That rule is only writable because tool interactions were separable units. The saving comes from the deletion; the schema is what makes the deletion expressible.

The second payoff is integrity. A ledger holding each item's original type can reject a transition, so that "content that enters the system as tool output cannot silently become an instruction" ([Towards Data Science, 2026](https://towardsdatascience.com/ai-agents-dont-need-more-context-they-need-typed-context/)). That check runs before a prompt exists. It enforces the boundary [CaMeL](../security/camel-control-data-flow-injection.md) draws at the harness level, and the one [authority confusion](../security/authority-confusion-untrusted-context.md) names from the dispatch side.

## Type the input, watch the output

Typing what the model reads and typing what it writes carry different risks, and conflating them is how teams get surprised. Constrained generation costs reasoning accuracy, and the cost tracks how tight the constraint is. On GSM8K, GPT-3.5-Turbo scores 75.99% in natural language and 74.70% asked for JSON, but 49.25% once a schema restriction is added on top, and 29.87% under JSON-mode. On Last Letter Concatenation the same model falls from 56.7% in prose to 25.2% in JSON, and to 1.78% under JSON-mode ([Tam et al., 2024](https://arxiv.org/abs/2408.02442v3)). Asking for JSON is nearly free on GSM8K; pinning the shape is what costs 26 points.

The same paper shows where the constraint pays. On the DDXPlus classification task, Gemini-1.5-Flash rises from 41.6% in natural language to 60.3% asked for JSON, and to 84.92% under JSON-mode ([Tam et al., 2024](https://arxiv.org/abs/2408.02442v3)), because narrowing the answer space is the point there rather than a side effect. Type the output when the step picks among known options. On multi-step reasoning, let the model deliberate in prose, then parse what it wrote.

## When this backfires

- The schema is not settled yet. Exploratory work has no stable field set, so every schema change rewrites every stored record, and that cost lands on you rather than the model.
- Your prefix is byte-stable today. If an append-only transcript already hits the cache, a typed store that re-serializes each turn converts 10%-priced reads into full-rate recomputation.
- The content is narrative. Tone guidance, rationale, and procedures have no natural field decomposition. Typing them yields one giant free-text field, paying the schema premium for no addressability.
- The context is small. Below the size where pruning or retrieval matters, there is nothing to address into and the premium is pure cost.
- You swap notation to claw the premium back. Token-optimized formats cut 18 to 27% but regress accuracy by 9 to 14 percentage points inside end-to-end agentic loops ([Kutschka & Geiger, 2026](https://arxiv.org/abs/2605.29676v2)).

## Key Takeaways

- Budget for a token increase, not a saving. Key repetition dominates the overhead, and a schema-once, data-many layout that eliminates per-record key repetition recovers 46 to 51% ([Deekeswar, 2026](https://arxiv.org/abs/2604.17512v1)).
- Adopt it when a program needs to prune, validate, or gate the context before the model sees it. Leave it as prose when nothing but the model will ever read it.
- The measured win comes from deleting context. Pruning to five recent tool interactions moved one benchmark from 71.0% to 91.6% completion at a third of the tokens ([Lodha et al., 2026](https://arxiv.org/abs/2606.10209v1)).
- Typed input is low risk. Typed output cost 26.7 percentage points on GSM8K in one study, so keep deliberation and formatting apart on reasoning steps ([Tam et al., 2024](https://arxiv.org/abs/2408.02442v3)).
- Check your cache before restructuring. Re-serializing a stable prefix every turn is the most expensive way to adopt this.

## Related

- [Validating Token-Optimized Formats Inside Agentic Loops](validate-token-optimized-formats-in-agentic-loops.md) — What happens when you try to win the schema premium back by changing notation.
- [Prompt Caching Architectural Discipline](prompt-caching-architectural-discipline.md) — Why a byte-stable prefix is worth more than a tidier context store.
- [Structured Domain Retrieval](structured-domain-retrieval.md) — Structure applied to what you fetch, rather than to the payload you assemble.
- [Schema-Guided Graph Retrieval](schema-guided-graph-retrieval.md) — One shared schema across construction and query, on the retrieval side of the same idea.
- [Semantic Density Optimization](semantic-density-optimization.md) — The parallel finding that stripping content to save tokens shifts the cost to inference.
