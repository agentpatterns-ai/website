---
title: "Tools as Typed Code Stubs (Programmatic Tool Calling)"
term: "Programmatic Tool Calling"
description: "Expose tools as typed Python stubs the model calls from a script. It matched or beat JSON tool calling on 11 of 14 models, but only pays off past two gates."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - programmatic tool calling
  - tools as code stubs
  - code-mode tool calling
last_reviewed: 2026-08-09
maturity: emerging
---

# Tools as Typed Code Stubs (Programmatic Tool Calling)

> Expose tools as typed Python stubs the model calls from a script, so chaining and fan-out become ordinary control flow.

Programmatic tool calling compiles your tool schemas into typed Python stubs and lets the model write a sandboxed script that imports and calls them, with execution and results inside one agent turn. Across 14 models on 309 BFCL v4 entries it matched or exceeded native JSON tool calling on 11 ([Patel et al., 2026](https://arxiv.org/abs/2608.06370v1)). That headline does not make it a default. It pays off past two gates, and below them it costs more and buys nothing.

## Two gates before you switch

### Gate one: does the model emit valid multiline Python?

Three of the 14 models wrote literal `\n` escape sequences instead of real newlines, so their scripts died on a syntax error. GPT-4o fell from 81.9% to 55.0%, GPT-4.1 from 81.9% to 62.1%, and GPT-5.4-mini from 79.3% to 55.0% ([Patel et al., 2026](https://arxiv.org/abs/2608.06370v1)).

Viability tracks model generation, not vendor family: "programmatic tool calling viability divides along model generation lines rather than model family" ([Patel et al., 2026](https://arxiv.org/abs/2608.06370v1)). It is not a clean ordering, though. GPT-5.4-mini is later and larger than GPT-5-nano, which handled the same system prompt correctly, and the authors use that pair to rule out prompt configuration as the cause. Measure the models you run, then keep the result as a per-model harness setting (see [Per-Model Harness Tuning](per-model-harness-tuning.md)).

### Gate two: is the workload shaped for it?

Anthropic names the strong fits as fan-out across many items, large tool results you can filter before they reach context, and agentic search. The weak fits are the common case. Each call depends on the model reasoning over the last, or there are few calls with small responses, or the tools need user feedback between steps. On τ²-bench, where each turn makes one or two sequential calls, programmatic calling "left scores unchanged and cost roughly 8% more" ([Anthropic](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling)).

## What the evidence shows

Fan-out is where the difference stops being a matter of degree, for some models. JSON tool calling has to enumerate every parallel call in a single response, and above a model-specific threshold it begins dropping calls without raising an error. Claude Sonnet 5 held 100% enumeration accuracy to N=70, fell to 75% at N=72, and reached 0% at N=100, while the programmatic path held 100% at both points ([Patel et al., 2026](https://arxiv.org/abs/2608.06370v1)). GPT-5 rose from 71.9% to 96.9% under the same ablation.

That ceiling is not universal, and the paper says so: "This asymmetry does not appear in GPT-5.6-Sol, which holds 100% baseline enumeration accuracy through N=100, suggesting the structural limit is specific to how Anthropic models serialize parallel tool-call blocks rather than a universal property of JSON tool calling" ([Patel et al., 2026](https://arxiv.org/abs/2608.06370v1)). Measure the drop on your own model rather than assuming the paradigm has it.

Chaining gains scale with depth: the accuracy gap reaches 18.8 percentage points at chains of 12 or more calls, at 0.32 to 0.96 of baseline per-entry latency ([Patel et al., 2026](https://arxiv.org/abs/2608.06370v1)). That range covers 13 of the 14 models; GPT-5 is the exception at 2.8x baseline latency, so a budget set from the range alone gets it wrong there. Under schema flooding with 128 schemas and decoys, mean accuracy moved +5.5% for the programmatic path against −2.3% for JSON and −32.0% for filesystem-based tool discovery ([Patel et al., 2026](https://arxiv.org/abs/2608.06370v1)).

Token cost inverts at scale. Below roughly 26 parallel calls the programmatic path is the expensive one, running 1.5× the input tokens on the chaining ablation. The overhead is the instruction template, which sits in the system prompt as prose instead of the API `tools` parameter. At a fan-out of 48 it needs 3,535 input tokens against 5,097 for JSON ([Patel et al., 2026](https://arxiv.org/abs/2608.06370v1)). Anthropic measured roughly 38% fewer billed input tokens on a 75-tool agent benchmark, with no change in accuracy ([Anthropic](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling)).

## Why it works

Two of the causes are structural and one is statistical. Chaining collapses turns: under JSON the model emits the first call, waits for its return value, then emits the second in a fresh inference turn, whereas a script computes the intermediate value inline. Fan-out has no ceiling in code, because a loop imposes no limit on call count where a parallel JSON block must list every call explicitly ([Patel et al., 2026](https://arxiv.org/abs/2608.06370v1)). Whether that second cause binds depends on the vendor's serialization, as the GPT-5.6-Sol result above shows. The statistical cause is training distribution. Anthropic states that "Claude is trained on large amounts of code, so presenting tools as callable Python functions lets it use that strength" ([Anthropic](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling)).

## When this backfires

- Any workload that fails gate two. The script cannot skip a round trip the model's own judgment gates, and on small first-turn interactions container startup and script generation cost more than they save ([Anthropic](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling)).
- Toolsets that rely on schema-level guarantees. Anthropic's implementation does not support tools with `strict: true` structured outputs, forcing a programmatic tool through `tool_choice`, `disable_parallel_tool_use: true`, or input schemas containing a recursive `$ref` ([Anthropic](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling)). Our own coverage of how it sits alongside deferred loading and tool search is [Advanced Tool Use](../../tool-engineering/advanced-tool-use.md).
- No sandbox in the path. Running the model's script client-side "executes untrusted code outside of a sandbox," where "tool invocations can be vectors for code injection" ([Anthropic](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling)). A validated call surface becomes an arbitrary-code surface, which raises the containment question covered in [Restrict the Coding Agent to Executing Code](../../tool-engineering/restrict-coding-agent-to-execute-code.md).
- Reading the benchmark as end-to-end evidence. BFCL v4 stubs return their arguments verbatim, so the study measures argument serialization accuracy rather than tool-use correctness, and its ablations run 31 to 52 entries per condition ([Patel et al., 2026](https://arxiv.org/abs/2608.06370v1)).

## Example

Checking budget compliance across 20 employees, the case Anthropic uses to document the feature, written in the typed-stub import form the paper's harness compiles ([Anthropic](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling); [Patel et al., 2026](https://arxiv.org/abs/2608.06370v1)). Each vendor exposes the stubs differently, so treat the import line as the shape rather than a literal API.

**Before** — JSON tool calling:

```text
model → get_expenses(employee="E001") → 400 line items into context
model → get_expenses(employee="E002") → 380 line items into context
…  20 model round trips, every line item in the context window
```

**After** — one script, one turn:

```python
from tools import get_expenses, get_budget

over = []
for eid in employee_ids:
    spent = sum(e["amount"] for e in get_expenses(employee=eid))
    if spent > get_budget(employee=eid):
        over.append((eid, spent))
print(over)
```

Only the contents of `over` reach the context window. Anthropic describes the same workload shrinking from hundreds of kilobytes of expense line items "down to a handful of lines" ([Anthropic](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling)).

## Key Takeaways

- Verify that your model emits syntactically valid multiline Python before switching. Viability tracks generation rather than vendor family, but not as a clean ordering, and a failure costs an absolute 19.7% to 26.9%.
- Fan-out above roughly 26 calls, large filterable results, and chains of 12 or more steps are where the paradigm pays. One or two sequential calls per turn are where it does not.
- Silent call-dropping at high fan-out is model-specific, not a property of JSON tool calling: Claude Sonnet 5 fell to 0% enumeration at N=100 while GPT-5.6-Sol held 100%. Measure enumeration counts on your own model.
- Switching trades a validated schema surface for a code-execution surface, which makes a sandbox a precondition rather than an optimization.

## Related

- [Natural Language Tool Selection (NLT)](natural-language-tool-selection.md) — the other way to drop JSON tool calls, aimed at weak models rather than high fan-out
- [Per-Model Harness Tuning](per-model-harness-tuning.md) — how to express the gate-one result as a declarative model-keyed override
- [Filter and Aggregate Data in the Execution Environment](../../context-engineering/filter-aggregate-execution-env.md) — the context-savings half of the same sandbox
- [Code Interpreter as a Primary Agent Tool](../../tool-engineering/code-interpreter-as-agent-tool.md) — when to give the agent an interpreter in the first place
- [Advanced Tool Use: Scaling Agent Tool Libraries](../../tool-engineering/advanced-tool-use.md) — programmatic calling alongside deferred tool loading and tool search
