---
title: "Pooled Tool Usage Can Hide Tools Without Past Examples"
description: "Folding shared usage examples into a tool index can lower retrieval of unused tools. Score evidence separately and test tools without shared usage."
term: "Pooled Tool Usage Retrieval"
tags:
  - tool-engineering
  - anti-pattern
  - cost-performance
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-31
maturity: emerging
---

# Pooled Tool Usage Can Hide Tools Without Past Examples

> Folding usage examples into a tool index can push tools without shared usage out of the retrieved candidates.

Folding adds past requests as extra searchable entries for their tools, alongside documentation. The best entry sets the score. Tools with usage gain extra chances to match a request, while tools without usage must compete through their documentation alone ([Chakraborty, v2, Setup](https://arxiv.org/html/2610.30867v2#Sx2)).

## Where retrieval drops

The paper measures Hit@5, the share of queries with a correct tool among five distinct candidates. Held-out tools keep documentation but receive no shared usage. This split concerns the usage pool; it does not establish that embedding models never saw these tools during training ([Introduction](https://arxiv.org/html/2610.30867v2#Sx1)).

With Jina-v2 embeddings and three usage-pool seeds, Table 2 reports these held-out results ([v2, Table 2](https://arxiv.org/html/2610.30867v2#Sx4.T2)):

| Catalog | Documentation only | Folded usage | Separate scoring with ZoE |
|---|---|---|---|
| StableToolBench | 73.3% | 40.0% | 78.5% |
| ToolRet | 30.6% | 29.0% | 29.4% |
| TOUCAN | 48.6% | 20.3% | 50.6% |

Folding raises StableToolBench's labeled-query Hit@5 from 65.8% to 80.1%. Labeled tools can receive usage, although some lack examples in a given seed. Report both groups separately; their results move in opposite directions ([v2, Table 2 and Introduction](https://arxiv.org/html/2610.30867v2#Sx4.T2)).

Adding entries gives used tools more chances, but entry count alone does not explain the observed loss. On StableToolBench, appending one usage example to each used tool's documentation already causes most of the loss at equal entry counts. Text-type controls leave content and writing style as possible explanations ([RQ1](https://arxiv.org/html/2610.30867v2#Sx3)).

## Separate evidence before combining scores

ZoE, or Z-scores over Evidence, computes separate documentation and best-usage similarities. It standardizes each score across tools for the query, then mixes them with a development-tuned weight. A tool without usage keeps its standardized documentation score. Used tools can still outrank it, so this preserves a score without guaranteeing rank ([Setup](https://arxiv.org/html/2610.30867v2#Sx2)).

Keep the documentation-only baseline. On ToolRet, ZoE fails to improve held-out retrieval over documentation-only. Its difference is -1.18 percentage points, with a paired 95% interval of -2.85 to +0.24. The study detects no difference; it does not establish equivalence ([RQ2](https://arxiv.org/html/2610.30867v2#Sx4)).

The authors saw test sets during earlier development. Some baseline settings were tuned on development data after that exposure. Their frozen settings describe the final scoring run, not an untouched test set. These are retrieval results. The experiments do not test task success or live agent behavior ([Settings](https://arxiv.org/html/2610.30867v2#Sx2), [Limitations](https://arxiv.org/html/2610.30867v2#Sx8)).

For your evaluation, hold out usage for selected tools while keeping their documentation searchable. Compare those queries separately from queries about tools eligible for usage. Test documentation-only, folding, and separate scoring at the same candidate budget. These checks follow the paper's evaluation design ([Setup](https://arxiv.org/html/2610.30867v2#Sx2)).

## Example

The paper selects a Shopify request for a store's products and one item's full record. Documentation-only retrieval finds the scraper among five candidates; folding misses it. The authors choose this example to show the failure, not estimate its frequency ([Introduction](https://arxiv.org/html/2610.30867v2#Sx1)).

## Key Takeaways

- Report tools without shared usage separately from tools eligible for usage.
- Keep a documentation-only baseline when adding usage evidence.
- Separate scoring preserves an unused tool's documentation score, without guaranteeing its rank.
- Treat ZoE as an emerging option with prior test-set exposure and no ToolRet improvement over documentation-only.

## Related

- [Tool Discovery Architecture by Query Shape](../patterns/agent-design/tool-discovery-architecture-by-query-shape.md) — candidate-budget comparisons for discovery architectures
- [Lexical-First Retrieval for Agentic Search](lexical-first-retrieval-for-agentic-search.md) — retriever choice and evaluation conditions
- [MCP Eager vs JIT Loading](mcp-eager-vs-jit-loading.md) — when tool definitions enter context
