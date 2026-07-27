---
title: "Local Model Viability Factors for Coding"
term: "Local Model Viability"
description: "A decision guide for when a self-hosted local model is good enough for coding — the RAM, model-size, context, tool-calling, and privacy factors that gate viability versus staying hosted."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
aliases:
  - local model viability for coding
  - self-hosted coding model viability
last_reviewed: 2026-07-08
maturity: adopted
---

# Local Model Viability Factors for Coding

> A local model is viable for coding only when RAM, model size, context length, and tool-calling reliability all clear the task's bar.

Run a local model for coding when three conditions hold at once: you have enough unified memory to fit the model plus its context, the task is small and well defined, and a privacy or offline requirement justifies the setup cost. Miss any one and a hosted frontier model is the better default. Local models became usable for some agentic coding in 2026, but the honest practitioner verdict is "hit and miss" and "not ready for a plug-and-play experience" ([Böckeler, Thoughtworks](https://martinfowler.com/articles/exploring-gen-ai/local-models-for-coding-experiences.html)).

Treat viability as a funnel, not a yes or no. A setup has to clear every stage in order: fit in RAM, respond at a bearable speed, call tools without stalling, produce functionally correct code, hold up across a longer conversation, and only then handle a larger task ([Böckeler](https://martinfowler.com/articles/exploring-gen-ai/local-models-for-coding-experiences.html)).

## The factors that gate viability

Several factors interact, which is what makes local setups tedious to evaluate — one model gave better code on a stronger machine with identical settings, and manual and automated evals disagreed on which model was best ([Böckeler](https://martinfowler.com/articles/exploring-gen-ai/local-models-for-coding-factors.html)).

| Factor | Why it gates viability |
|--------|------------------------|
| RAM / VRAM | Model weights plus the context cache must fit, or the runtime crashes or crawls. A comfortable range was 15 to 25 GB of model on a 48 GB machine; a 48 GB model on a 64 GB machine crashed once the conversation continued ([Böckeler](https://martinfowler.com/articles/exploring-gen-ai/local-models-for-coding-factors.html)). |
| Model size and architecture | More parameters mean better output but a larger footprint. Mixture-of-experts models activate only part of their weights, so a 35B MoE needs less RAM and runs faster than a 35B dense model ([Böckeler](https://martinfowler.com/articles/exploring-gen-ai/local-models-for-coding-factors.html)). |
| Quantization | Compressing weights to Q4 or Q6 shrinks the footprint at some quality cost; quantization-aware training aims to preserve quality better ([Böckeler](https://martinfowler.com/articles/exploring-gen-ai/local-models-for-coding-factors.html)). |
| Context window | Runtime defaults are far too small for agentic loops; set at least 32K, ideally 64K. Larger context consumes more RAM through the key-value cache, so context ambition is capped by memory ([Böckeler](https://martinfowler.com/articles/exploring-gen-ai/local-models-for-coding-factors.html)). |
| Tool calling | Agentic coding needs schema-valid tool calls every turn. Models not fine-tuned for tool use emit malformed calls, though they often self-recover ([Böckeler](https://martinfowler.com/articles/exploring-gen-ai/local-models-for-coding-factors.html); [XDA](https://www.xda-developers.com/biggest-local-llm-machine-useless-cant-call-single-tool-how-many-parameters/)). |
| Harness overhead | System prompt and tool schemas eat scarce local context. A lean harness such as OpenCode or Pi preserves more room than a heavier one ([Böckeler](https://martinfowler.com/articles/exploring-gen-ai/local-models-for-coding-factors.html)). |

Reasoning is not a free win. Smaller models often loop inside their chain of thought ("Wait… Actually… But wait…"); turning reasoning off ran faster and scored the same or slightly better in one automated eval ([Böckeler](https://martinfowler.com/articles/exploring-gen-ai/local-models-for-coding-factors.html)).

## Why it works

The setup is governed by a memory budget and a capability floor. Model weights plus the key-value cache, which grows with context length, must fit in physical memory; exceed it and the runtime crashes or thrashes. A fixed RAM ceiling therefore forces a three-way trade among model size, quantization, and usable context ([Böckeler](https://martinfowler.com/articles/exploring-gen-ai/local-models-for-coding-factors.html)). Separately, agentic coding needs the model to emit valid tool calls turn after turn; models not trained for that stall the loop, which is why small local models suit autocomplete far better than agentic use ([XDA](https://www.xda-developers.com/biggest-local-llm-machine-useless-cant-call-single-tool-how-many-parameters/)). Mixture-of-experts architectures relax the memory side by activating a subset of parameters per token, which is why a roughly 35B MoE model hit the best capability-per-gigabyte balance in practice ([Böckeler](https://martinfowler.com/articles/exploring-gen-ai/local-models-for-coding-factors.html)).

## When this backfires

Local inference costs more than it returns under these conditions:

- Under about 48 GB of memory, a 15 to 25 GB model plus a 32K to 64K cache will not fit comfortably, so the model crashes or crawls ([Böckeler](https://martinfowler.com/articles/exploring-gen-ai/local-models-for-coding-factors.html)).
- Complex or multi-file tasks blow up reasoning chains and context. Even a capable 80B model crashed on the next turn, and other runs stalled for 8 to 12 minutes before being abandoned ([Böckeler](https://martinfowler.com/articles/exploring-gen-ai/local-models-for-coding-experiences.html)).
- With no privacy or compliance driver, the tuning time and the quality gap against hosted frontier models make hosted the rational choice.
- A model that is not fine-tuned for tool calling derails the agentic loop with malformed calls ([XDA](https://www.xda-developers.com/biggest-local-llm-machine-useless-cant-call-single-tool-how-many-parameters/)).

The gap is narrowing, not closed. Independent evals report several local models now tool-call reliably, which reinforces that viability is a per-configuration question rather than a settled yes or no ([Böckeler](https://martinfowler.com/articles/exploring-gen-ai/local-models-for-coding-factors.html)).

## Example

After four weeks across an M3 Max (48 GB) and an M5 Pro (64 GB), Böckeler's go-to local setup was Qwen3.6 35B-A3B MoE at Q4 (about 22 GB), run in LM Studio with a 64K context window and a lean harness. It offered the best balance of capability, speed, and memory footprint among the models tried, and now handles small, well-defined day-to-day changes — while larger models either crashed or stalled ([Böckeler, factors](https://martinfowler.com/articles/exploring-gen-ai/local-models-for-coding-factors.html); [experiences](https://martinfowler.com/articles/exploring-gen-ai/local-models-for-coding-experiences.html)).

## Key Takeaways

- Local coding viability is a funnel of RAM fit, speed, tool calling, correctness, context length, and task complexity — a setup must clear every stage.
- RAM is the hard constraint: weights plus the key-value cache must fit, which forces a trade among model size, quantization, and context length.
- Mixture-of-experts models around 35B at Q4 give the best capability-per-gigabyte balance for a single developer machine today.
- Reliable tool calling, not raw parameter count, gates agentic use; small models suit autocomplete better than agentic loops.
- Choose local when a privacy or offline requirement justifies the tuning cost; otherwise a hosted frontier model is the better default.

## Related

- [Managed vs Self-Hosted Agent Harness](managed-vs-self-hosted-harness.md) — the broader deployment decision this factors guide sits inside
- [Gateway Model Routing](gateway-model-routing.md) — route the harness across a model catalog, including local providers
- [Auto Model Selection](auto-model-selection.md) — hand per-task model choice to the harness instead of pinning one model
- [Specialized SLM as an Agent Tool](specialized-slm-as-agent-tool.md) — use a small local model as a scoped tool rather than the primary agent
