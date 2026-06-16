---
title: "Validating Token-Optimized Formats Inside Agentic Loops"
description: "Switching tool schemas from JSON to TOON or TRON saves tokens in isolation but loses up to 14 percentage points of accuracy inside end-to-end agentic loops — measure before you swap."
tags:
  - context-engineering
  - cost-performance
  - tool-agnostic
  - arxiv
last_reviewed: 2026-06-13
maturity: emerging
---

# Validating Token-Optimized Formats Inside Agentic Loops

> Token-optimized notations cut input tokens up to 27% but regress accuracy 9-14pp inside end-to-end agentic loops — validate before you swap.

Token-optimized formats such as Token-Oriented Object Notation (TOON) and Token Reduced Object Notation (TRON) re-encode JSON to remove repeated property names and structural overhead. Isolated comprehension benchmarks report 30-60% savings ([TOON spec](https://github.com/toon-format/toon)), but the savings measured on single-turn tasks do not survive the multi-turn, parallel tool-call patterns that make up real agentic systems ([Kutschka & Geiger, 2026](https://arxiv.org/abs/2605.29676)).

## Input-Side vs Output-Side Compression

The two compression directions behave asymmetrically:

| Direction | What the LLM does | Why behavior differs |
|-----------|------------------|----------------------|
| **Input-side** (tool schemas, retrieved context) | Reads the format only | Comprehension degrades gracefully on unfamiliar notation |
| **Output-side** (tool calls, structured responses) | Generates the format | Generation regresses sharply — LLMs were trained predominantly on JSON |

Treating "switch the wire format" as a single decision conflates two different changes. Input-only swaps (compress the schema, keep JSON tool responses) carry less accuracy risk than full bidirectional swaps.

## What the Agentic-Loop Study Found

[Kutschka & Geiger (2026)](https://arxiv.org/abs/2605.29676) benchmarked TOON, TRON, and JSON across four agentic suites (BFCL, MCPToolBenchPP, MCP-Universe, StableToolBench) on five open-weight LLMs:

| Format | Token reduction vs JSON | Accuracy delta vs JSON |
|--------|------------------------|------------------------|
| TRON | up to 27% | within 14 percentage points |
| TOON | up to 18% | ~9 percentage points |
| JSON | baseline | baseline |

The same paper documents two operational failure modes specific to multi-turn agentic loops:

- TOON exhibits **cascading parse failures** when used across multi-turn interactions — one mis-parsed turn corrupts the next.
- TOON **collapses parallel tool-call output** on most tested open-weight models, breaking concurrent tool dispatch.

An earlier benchmark on isolated structured generation found **plain JSON had the best one-shot accuracy**, and for simple structures even constrained decoding outperformed TOON ([arxiv 2603.03306](https://arxiv.org/abs/2603.03306)).

## Why It Works

Token-efficient notations save tokens by eliminating repeated property names and structural punctuation — mechanical compression of the serialized form. The accuracy cost has a separate mechanism: LLMs were trained predominantly on JSON, so unfamiliar notation forces them to spend reasoning capacity on parsing rather than the task ([InfoQ, 2025](https://www.infoq.com/news/2025/11/toon-reduce-llm-cost-tokens/)). The asymmetry between input and output compression follows from this — reading an unfamiliar format degrades less than producing it, because production requires the model to commit to a low-probability token distribution at every step.

The net effect is a Pareto frontier between tokens and accuracy, not a free lunch. The decision is whether the savings on *your* workload sit on the favorable side of the curve.

## When This Backfires

The pattern degrades or inverts in five conditions:

1. **Short, single-turn interactions** — the instructional overhead teaching the LLM the format consumes more tokens than the compression saves ([arxiv 2603.03306](https://arxiv.org/abs/2603.03306)).
2. **Multi-turn loops with parallel tool calls** — TOON collapses parallel tool-call output on most open-weight LLMs, producing cascading parse failures ([Kutschka & Geiger, 2026](https://arxiv.org/abs/2605.29676)).
3. **Nested or heterogeneous schemas** — token savings concentrate on uniform tabular data; nested objects see negligible compression while paying the full accuracy cost ([TOON spec](https://github.com/toon-format/toon)).
4. **Accuracy-critical workflows** — billing, code synthesis, or safety-critical decisions cannot absorb a 9-14pp accuracy regression for an 18-27% token win.
5. **Mixed-model fleets** — format behavior varies across the five open-weight LLMs tested; a notation that works on one model in the pipeline can regress on another.

For most production stacks the right baseline is JSON plus orthogonal levers — prompt caching, field projection at the tool boundary ([Token-Efficient Tool Design](../tool-engineering/token-efficient-tool-design.md)), and smaller models — which deliver token wins without the accuracy gamble.

## Example

A practical evaluation plan before swapping a tool schema from JSON to TOON or TRON:

**Before** — single-turn comprehension benchmark only:

```
1. Generate 100 sample tool schemas in JSON and TOON.
2. Ask the model to extract one field from each.
3. Measure token count and answer accuracy.
4. TOON wins on tokens, near-parity on accuracy. Ship the swap.
```

This is the failure mode the agentic-loop study calls out — the test does not match the production workload.

**After** — measure the swap inside the actual loop:

```
1. Replay 100 production agent sessions with three configurations:
   a. JSON in, JSON out (baseline)
   b. TOON in, JSON out (input-only compression)
   c. TOON in, TOON out (bidirectional)
2. For each, measure:
   - Total tokens (input + output, summed across all turns)
   - End-to-end task success rate
   - Parallel tool-call success rate (turns with 2+ concurrent calls)
   - Multi-turn cascade rate (failures that propagate beyond one turn)
3. Decide per workload — input-only may pass, bidirectional may regress.
```

The decoupled measurement reveals which side of the compression Pareto your workload sits on — the isolated single-turn benchmark cannot.

## Key Takeaways

- Token reductions measured on isolated single-turn benchmarks (30-60% in vendor benchmarks) shrink to 18-27% inside end-to-end agentic loops.
- The accuracy cost is real: TRON regresses up to 14 percentage points, TOON ~9 percentage points vs JSON across four agentic benchmarks.
- Input-side compression (schemas the LLM reads) and output-side compression (formats the LLM generates) carry different risk — measure them separately.
- TOON has multi-turn failure modes — cascading parse errors and collapsed parallel tool calls — that single-turn tests cannot surface ([Kutschka & Geiger, 2026](https://arxiv.org/abs/2605.29676)).
- Default to JSON. Validate any swap on replayed production traces with multi-turn and parallel-tool-call coverage before deploying.

## Related

- [Token-Efficient Tool Design](../tool-engineering/token-efficient-tool-design.md) — A different lever on the same problem: shape tool output to return only the next decision's inputs, regardless of serialization format.
- [Semantic Tool Output](../tool-engineering/semantic-tool-output.md) — Output design for agent readability, complementary to notation choice.
- [Prompt Compression](prompt-compression.md) — Compress instructions and prose for the same goal at a different layer of the prompt.
- [Semantic Density Optimization](semantic-density-optimization.md) — Why naive compression backfires: removing semantic content shifts cost to inference, paralleling the input-vs-output asymmetry seen with format swaps.
- [Tokenizer Swap Tax](tokenizer-swap-tax.md) — Another notation-layer change with hidden costs that only surface in end-to-end measurement.
