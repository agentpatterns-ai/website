---
title: "DSPy: Programmatic Prompt Optimization for Compound Agent Systems"
description: "DSPy replaces hand-written prompts with optimizable modules — signatures define input/output contracts, optimizers search the prompt and few-shot space automatically against a metric."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
aliases:
  - programmatic prompt optimization
  - DSPy prompt compiler
---

# DSPy: Programmatic Prompt Optimization

> DSPy treats prompts as learnable parameters: define a metric, supply training examples, and an optimizer searches the prompt and few-shot space automatically — eliminating manual prompt tuning for stable compound pipelines.

## When to Apply

Three conditions must hold before DSPy optimization pays off:

1. **Measurable metric** — output quality must reduce to a scalar score (exact match, F1, custom judge). Creative, open-ended tasks with subjective quality have no score for the optimizer to maximize.
2. **Representative training examples** — at minimum ~30 labeled examples; 300 is better ([DSPy optimizers](https://dspy.ai/learn/optimization/optimizers/)). Without sufficient data, the optimizer overfits to noise.
3. **Stable pipeline structure** — DSPy compiles a specific module topology. If the pipeline changes frequently, prior optimization is invalidated and the cost repeats.

## Core Abstractions

**Signatures** replace raw prompt strings. A signature declares typed input/output fields:

```python
class SummarizeCode(dspy.Signature):
    """Summarize code changes for a pull request."""
    code_diff: str = dspy.InputField()
    summary: str = dspy.OutputField()
```

DSPy expands signatures into LLM-ready prompts and parses typed outputs. The developer never writes prompt text directly.

**Modules** wrap signatures with a reasoning strategy. Built-in modules include:

- `dspy.Predict` — direct input→output
- `dspy.ChainOfThought` — adds step-by-step reasoning before the output field
- `dspy.ReAct` — tool-using agent loop (reason + act cycles)

Modules compose into pipelines like standard Python objects. Each module becomes an independently optimizable prompt node in the computational graph.

## Optimization Loop

Given a compiled program, DSPy optimizers search the space of prompt instructions and few-shot demonstrations to maximize the metric:

```python
optimizer = dspy.MIPROv2(metric=my_metric, auto="medium")
compiled_pipeline = optimizer.compile(pipeline, trainset=train_examples)
```

[MIPROv2](https://arxiv.org/abs/2406.11695) uses Bayesian Optimization: it bootstraps candidate demonstrations from high-scoring traces, generates instruction variants by inspecting the program structure and data, then searches combinations across all modules jointly. COPRO uses coordinate ascent (hill-climbing per module). BootstrapFewShot adds demonstrations without changing instructions.

## Compound System Advantage

The key benefit over per-prompt optimization is **joint optimization**. Given a pipeline of router → worker → verifier, optimizing each prompt in isolation ignores how one module's output affects downstream modules. DSPy optimizes all prompts simultaneously using a single end-to-end metric — a change that hurts the router's instructions but improves the pipeline's final score is accepted.

The foundational paper ([Khattab et al., 2023, arxiv 2310.03714](https://arxiv.org/abs/2310.03714)) reports GPT-3.5 and llama2-13b-chat pipelines outperforming standard few-shot prompting by 25%+ and 65%+ respectively across multi-hop retrieval and question-answering benchmarks, and 5–46% improvements over expert-written prompt chains.

## Limitations

- **Optimization cost**: MIPROv2 makes many LLM calls during the optimization run. Cost amortizes only if the compiled pipeline runs frequently enough in production.
- **Metric quality dependency**: a poorly specified metric causes the optimizer to overfit to a proxy — gains on the training distribution may not transfer.
- **Model non-transferability**: prompts optimized for one model do not reliably transfer to another. Teams that rotate underlying models must re-optimize.
- **Opacity**: DSPy manages prompt text automatically; inspecting what is sent to the LLM requires explicit extraction from the compiled program.

## Example

A code review pipeline: a router classifies the diff type (refactor, bug fix, feature), a worker generates review comments, and a verifier checks that all changed functions are addressed.

**Without DSPy**: three hand-tuned prompts maintained independently. A wording change in the router that improves routing accuracy may silently degrade the worker's comprehension because the routing labels changed format.

**With DSPy**: each stage is a `dspy.ChainOfThought` module. A single metric — fraction of changed functions receiving a comment — drives joint optimization. MIPROv2 finds instruction and demonstration combinations that maximize end-to-end coverage, including routing formats the worker can consume.

```python
class ReviewPipeline(dspy.Module):
    def __init__(self):
        self.router = dspy.ChainOfThought("diff -> diff_type")
        self.worker = dspy.ChainOfThought("diff, diff_type -> review_comments")
        self.verifier = dspy.ChainOfThought("diff, review_comments -> coverage_check")

    def forward(self, diff):
        diff_type = self.router(diff=diff).diff_type
        comments = self.worker(diff=diff, diff_type=diff_type).review_comments
        return self.verifier(diff=diff, review_comments=comments)
```

## Key Takeaways

- DSPy requires a measurable metric, ~30–300 training examples, and a stable pipeline structure — without all three, manual prompting is faster
- Signatures declare input/output contracts; modules attach reasoning strategies; optimizers search prompt and few-shot space against the metric
- Joint optimization of compound pipelines is the primary advantage over per-module prompt tuning
- Optimized prompts are model-specific; re-optimization is required when switching underlying models
- Open-ended and creative tasks with subjective quality are outside DSPy's applicable scope

## Related

- [Evaluator-Optimizer Pattern](evaluator-optimizer.md) — iterative refinement loop where an evaluator critiques generator output
- [Harness Hill-Climbing](harness-hill-climbing.md) — systematic improvement of agent harnesses through metric-driven iteration
- [Self-Rewriting Meta-Prompt Loop](self-rewriting-meta-prompt-loop.md) — agents that autonomously improve their own system prompts without external optimization
- [Agentic Flywheel](agentic-flywheel.md) — closed loop where agents analyze traces and metrics to generate harness improvements
- [Loop Strategy Spectrum](loop-strategy-spectrum.md) — choosing between accumulated, compressed, and fresh-context loop strategies
- [Cost-Aware Agent Design](cost-aware-agent-design.md) — routing by complexity to match model cost to task difficulty
