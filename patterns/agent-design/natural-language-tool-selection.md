---
title: "Natural Language Tool Selection (NLT)"
term: "Natural Language Tools"
description: "Describe tools in prose and parse the model's plain-language choice instead of forcing JSON tool calls — it lifts accuracy on weaker models, but frontier models optimized for structured calling gain little or regress."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - natural language tools
  - natural language tool calling
last_reviewed: 2026-07-07
maturity: emerging
---

# Natural Language Tool Selection (NLT)

> Describe tools in prose and parse the model's plain-language choice instead of forcing JSON tool calls — a large accuracy win on weaker models.

Natural Language Tools (NLT) present the available tools as a prose list and ask the model to pick in plain language — for example a `YES`/`NO` per tool — then a regex extracts the selection. Structured tool calling instead forces the model to emit a valid JSON function call. A 14-model replication study found NLT reached 62.3% tool-calling accuracy versus 47.4% for structured calling, a 14.9 percentage-point gain, and cut critical errors by 93% (51 versus 755) across 8,560 trials ([Somma et al., 2026](https://arxiv.org/abs/2607.03953v1)).

## When to reach for it

The gain is not uniform — it tracks model capability, so lead with the condition. Choose NLT when your agent runs on models that are weak at structured output:

- Small or open-weight models. Mistral 7B gained 39.4pp; it and Qwen3-VL "collapsed completely with structured outputs: 0% accuracy," mostly from failing to emit valid JSON ([Somma et al., 2026](https://arxiv.org/html/2607.03953)).
- Reasoning models. DeepSeek-R1 gained 24.0pp (55.0% versus 31.0%) ([Somma et al., 2026](https://arxiv.org/html/2607.03953)).
- Models without strong native tool calling. Claude Sonnet 4 gained 43.1pp (61.9% versus 18.8%) in this single-turn selection setting ([Somma et al., 2026](https://arxiv.org/html/2607.03953)).

NLT also cut token usage 25.2% and won on 11 of the 14 models tested ([Somma et al., 2026](https://arxiv.org/abs/2607.03953v1)).

## Why it works

Forcing schema compliance draws on a different part of the model's learned distribution than the task itself. The authors attribute the gap to cognitive-resource competition: JSON generation patterns are "primarily acquired from coding corpora, whereas tasks such as customer service or mental wellness originate from different domains," so producing a schema engages deliberate format compliance "at the expense of System 1's intuitive task understanding," diverting capacity from the actual decision ([Somma et al., 2026](https://arxiv.org/html/2607.03953)). The effect is corroborated independently: strict JSON-mode generation degrades accuracy on reasoning-heavy tasks compared with free-form generation converted to structure afterward ([Tam et al., 2024](https://arxiv.org/abs/2408.02442)), and structured-output constraints measurably suppress correct tool calling in open-weight models ([Constraint Tax, 2026](https://arxiv.org/abs/2606.25605v1)).

## When this backfires

- Frontier models optimized for structured calling. GPT-5 gained only 1.6pp (both near 81%) and Gemini 2.5 Pro regressed 33.7pp under NLT (82.1% structured versus 48.3%) — the prose-parsing overhead buys nothing and can hurt ([Somma et al., 2026](https://arxiv.org/html/2607.03953)). The study notes reinforcement-learning optimization is narrowing the NLT advantage on these models over time.
- Parameterized or multi-turn tool calls. The study validates only single-turn, parameterless tool selection across two domains. A `YES`/`NO` regex parse does not extract typed arguments the way a JSON schema does, so NLT does not obviously carry to tools that take structured inputs ([Somma et al., 2026](https://arxiv.org/html/2607.03953)).
- Systems needing a guaranteed machine-readable contract. Replacing schema-validated JSON with regex-parsed prose adds a parse-failure surface that structured calling eliminates by construction. See the trade-off in [Structured Output Constraints](../../verification/structured-output-constraints.md).

## Example

The NLT prompt lists each tool as one prose line asking for a per-tool decision, wraps it in a reasoning slot and an end marker, then a regex reads the answers:

```
Thinking: <the model's reasoning about the request>
Website information – YES/NO
<one line per available tool> – YES/NO
Assessment finished
```

The model replies in prose (`Website information – YES`) and the harness extracts the selection by exact match — no JSON, no schema validation, no failed-parse retries ([Somma et al., 2026](https://arxiv.org/html/2607.03953)). The structured equivalent passes OpenAI-compatible function schemas and requires the model to return a valid `tool_calls` JSON object, which the weakest models fail to produce at all.

## Key Takeaways

- NLT lifts single-turn tool-selection accuracy 14.9pp on average and cuts critical errors 93% across 14 models ([Somma et al., 2026](https://arxiv.org/abs/2607.03953v1)).
- The gain is capability-dependent — large on small, reasoning, and non-native-tool-calling models; near-zero or negative on frontier models optimized for structured calling.
- The mechanism is distributional: schema formatting pulls from coding-corpus patterns and competes with task reasoning.
- Keep structured calling for frontier models, parameterized tools, and multi-turn flows that need typed arguments or a machine-guaranteed contract.
- Decide per model, not once for the whole system — pair it with [Per-Model Harness Tuning](per-model-harness-tuning.md).

## Related

- [Structured Output Constraints: Reducing Hallucination](../../verification/structured-output-constraints.md)
- [Tools as Typed Code Stubs (Programmatic Tool Calling)](programmatic-tool-calling.md) — the other alternative to JSON tool calls, which needs strong code generation rather than weak structured output
- [Per-Model Harness Tuning](per-model-harness-tuning.md)
- [The Think Tool](think-tool.md)
- [Auto Model Selection](auto-model-selection.md)
- [Asynchronous Agent I/O and Speculative Tools](asynchronous-agent-io-and-speculative-tools.md)
