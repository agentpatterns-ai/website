---
title: "Running an Agent's Context Step on a Smaller Model"
term: "Context-Step Model Split"
description: "A long-running agent's summarize, compress and extract calls are a different workload from its reasoning. Settle the compression policy first, then move those calls to a small model."
tags:
  - agent-design
  - cost-performance
  - arxiv
  - tool-agnostic
aliases:
  - compressor model downgrade
  - small model for context compaction
  - context-management model routing
last_reviewed: 2026-10-14
maturity: emerging
---

# Running an Agent's Context Step on a Smaller Model

> Settle the compression policy on the large model, then move the context step down; a compressor distilled from it kept over 95% of teacher performance.

A long-running agent makes two kinds of model call. Reasoning calls return arbitrary text: a plan, a patch, a reply. Context calls return a selection: a summary of old history, the relevant part of a tool result, a field copied out of a message, a label for the trajectory. Only the second kind can move to a small model, and it moves safely in one order. Optimize the compression policy on the large model, then change the model that runs it.

## Two conditions before you swap

The independent evidence for a small compressor is conditional, and the condition is the policy. ACON refines its compression guideline from failure analysis of the agent, then distills that compressor into Qwen3-14B, Qwen3-8B and Phi-4 students. Those "distilled compressors retain over 95% of the performance of the gpt-4.1 teacher", and estimated per-example compression cost falls from $0.045 to $0.0004 ([Kang et al., arXiv:2510.00615v3](https://arxiv.org/abs/2510.00615v3)). The dependency is stated directly: "small models can reliably replace large LLM-based compressors when equipped with optimized guidelines". Swap the model first and you freeze a policy you never measured. The paper's own warning covers that case: "Naive strategies like token truncation or generic summarization are insufficient, as they easily discard these critical details essential for multi-step reasoning."

The second condition is the shape of the step's answer. LangChain's ScaleDown integration keeps the boundary explicit: "Keep a general-purpose LLM for open-ended generation, like writing code, drafting replies, and planning" ([LangChain](https://www.langchain.com/blog/building-long-running-agents-with-scaledown-and-deep-agents)). Summarizing history, compressing a tool result, extracting a field and labeling a trajectory each return something bounded. Planning does not. Where the answer is a selection, the model can restrict its own output to that set: a constrained decoding model "is trained for one task and only returns answers that task allows, like a label from your list or spans of the input". On the copy-a-value steps that removes one defect, because the agent's own model "may paraphrase an error code or mistype an email address instead of copying it exactly".

## Price the step, not the vendor's average

An average tells you nothing about the step you are replacing, and this vendor publishes three of them. LangChain writes that "ScaleDown reports its models are 200x faster and 467x cheaper than frontier models on these narrow tasks". ScaleDown's own head-to-head page puts the figure against the average of GPT-5.5, GPT-5.4 Mini and GPT-5.4 Nano at "89× cheaper", then breaks that down by task.

| Task | Cost vs OpenAI average | Latency vs OpenAI average |
|---|---|---|
| Classify | 1,810x cheaper | 2.6x faster |
| Compress | 138x cheaper | 1.8x faster |
| Summarize | 41x cheaper | 2.7x faster |
| Extract | 35x cheaper | 3.3x faster |

Figures from [ScaleDown head-to-head benchmarks](https://docs.scaledown.ai/benchmarks/providers), which states the baseline: "Every figure is ScaleDown measured against that provider's average across its models on the same task." Intent classification's cost multiple is 13 to 52 times the multiple on the three steps a long-running coding agent repeats, and none of those three clears 4x on latency. The 89x aggregate sits above Summarize and Extract and below Compress, so it matches no single task.

## Why it works

The two workloads differ in the size of their output space, and that is what lets the smaller model keep up. GLiNER treats extraction "as matching entity type embeddings to textual span representations in latent space, rather than as a generation task", which is why a 50M-parameter model "outperforms general-purpose models such as ChatGPT and Vicuna" and a 90M one matches UniNER-13B at 55 F1 "despite being 140 times smaller" ([Zaratiana et al., arXiv:2311.08526v1](https://arxiv.org/abs/2311.08526v1)). The latency follows from the same change, because a generative extractor spends "several decoding steps" and has "no way to perform the prediction of multiple entity types in parallel".

Whether the step is worth attacking is measured outside any vendor. In a 65-policy sweep across three open-weight models on SWE-bench Verified and Terminal-Bench, "for five policies, total token usage remains at or above 0.94x full context despite shorter prompts, while summarization calls account for 28–46% of solved-run wall-clock time for the 4 summarization primitives" ([Satish et al., arXiv:2609.32961v1](https://arxiv.org/abs/2609.32961v1)). For those five policies the compaction call is a large share of the run, not overhead at the margin.

## When this backfires

- Your compression policy is unsettled. A hosted model arrives with a fixed one, and the policy is where ACON's gain came from: its baselines already included "LLMLingua: extractive compression with an encoder-only LM", which the guideline-optimized compressor beat ([arXiv:2510.00615v3](https://arxiv.org/abs/2510.00615v3)).
- A restricted output space is not a correctness guarantee. Constrained decoding "shapes the token stream and never consults the world those values describe" ([Semantic Validation](../../verification/semantic-validation-schema-valid-output.md)). A copied span is in range, not right.
- Compaction barely fires on your workload. The 28–46% figure covers five policies and the four summarization primitives, on solved runs only; on shared solved tasks, Qwen with TR "compresses about 9 times per run on Terminal-Bench, compared with fewer than 2 on SWE-bench" ([arXiv:2609.32961v1](https://arxiv.org/abs/2609.32961v1)).
- A local model already covers the step. Against GLiNER2.5-multi-v1, ScaleDown's own table says "GLiNER runs locally, so inference is free, and it is faster, while ScaleDown is more accurate", and on extraction that edge is 0.2 pp ([ScaleDown](https://docs.scaledown.ai/benchmarks/providers)).
- Your inputs sit outside the narrow model's trained distribution. The English-backbone GLiNER-En variant "scored only 0.89 in the F1 score" on Bengali (the multilingual variant scored 25.9) ([arXiv:2311.08526v1](https://arxiv.org/abs/2311.08526v1)). Neither source benchmarks the trajectory-drift labeling that long-running agents want.

## Example

LangChain's tool-compression middleware prepends a marker to every result it shortens, and the marker is the design worth copying:

```
[Compressed by ScaleDown for "refund policy for EU orders":
 18,402 -> 3,110 chars.
 Call this tool again without `compression_query` for the full output.]
```

The two character counts in that marker are 83% of the result gone, and LangChain says of the trace it links that "ScaleDown cut a long docs page by almost 90% before the model saw it" ([LangChain](https://www.langchain.com/blog/building-long-running-agents-with-scaledown-and-deep-agents)). The third line is what bounds the risk, because the agent can re-run the tool without `compression_query` and get the full result when the compressor dropped the part it needed.

Two operational details decide how the swap reads in production. The summarization middleware fails open: "If a ScaleDown call fails, the middleware leaves history as is and the agent keeps running." The history then stays uncompressed. And only one of the four tasks is scored on whether the compression preserved the answer, since "Compress is evaluated end to end: the compressed context is passed to a downstream LLM and the answer is scored, so the metric reflects whether the right information survived" ([ScaleDown](https://docs.scaledown.ai/benchmarks/methodology)). Summarization's ROUGE-L against QMSum meeting transcripts does not test that.

## Key Takeaways

- Order the two decisions. Optimize the compression guideline on the large model, then move execution down, because the published 95% retention belongs to a student distilled from an already-optimized teacher.
- Split the agent's calls by output space rather than by importance. Selections move; arbitrary text stays.
- Ask any vendor for the figure on your step alone. Classify's cost multiple here is 52 times Extract's, so an average across the two describes neither.
- Measure what share of wall-clock your context calls take before you shop. In the paper, one Qwen policy compressed about 9 times per run on Terminal-Bench and fewer than 2 on SWE-bench, so compaction frequency varies by workload.
- Keep an escape hatch on every compressed result. A marker that tells the agent how to re-fetch the uncompressed original turns a dropped span into a retry instead of a wrong answer.

## Related

- [Utility-Model Split](utility-model-split.md) — the same routing axis for the background harness calls an IDE makes, fixed as static configuration rather than decided per compaction.
- [Specialized Small Language Models as Agent Sub-Tools](specialized-slm-as-agent-tool.md) — the small model placed behind a tool-call boundary the agent invokes, instead of in middleware that fires on its own trigger.
- [Scoring a Compaction Policy on Latency and Billed Cost](../../context-engineering/compaction-policy-latency-and-cost.md) — how to choose the policy this page tells you to settle first.
- [Context Compression Strategies](../../context-engineering/context-compression-strategies.md) — the compaction operations themselves, offloading and summarization.
- [Semantic Validation for Schema-Valid Agent Output](../../verification/semantic-validation-schema-valid-output.md) — what a constrained output still fails to guarantee, and the checks that close the gap.
