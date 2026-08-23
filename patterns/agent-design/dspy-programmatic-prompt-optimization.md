---
title: "DSPy: Programmatic Prompt Optimization for Compound Agent Systems"
term: "DSPy"
description: "DSPy replaces hand-written prompts with optimizable modules — signatures define input/output contracts, optimizers search the prompt and few-shot space automatically against a metric."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
aliases:
  - programmatic prompt optimization
  - DSPy prompt compiler
last_reviewed: 2026-06-12
maturity: adopted
---

# DSPy: Programmatic Prompt Optimization

> DSPy treats prompts as learnable parameters: given a metric and training examples, an optimizer searches the prompt and few-shot space automatically, replacing manual tuning.

## When to apply

Three conditions must hold before DSPy optimization pays off:

1. Measurable metric — output quality must reduce to a scalar score (exact match, F1, custom judge). Creative, open-ended tasks with subjective quality give the optimizer no score to maximize.
2. Representative training examples — at least about 30 labeled examples, though 300 is better ([DSPy optimizers](https://dspy.ai/learn/optimization/optimizers/)). Without enough data, the optimizer overfits to noise.
3. Stable pipeline structure — DSPy compiles a specific module topology. If the pipeline changes often, earlier optimization is invalidated and you pay the cost again.

## Core abstractions

Signatures, declared as a `dspy.Signature` subclass, replace raw prompt strings. A signature declares typed input and output fields:

```python
class SummarizeCode(dspy.Signature):
    """Summarize code changes for a pull request."""
    code_diff: str = dspy.InputField()
    summary: str = dspy.OutputField()
```

DSPy expands signatures into LLM-ready prompts and parses typed outputs. You never write prompt text directly.

Modules wrap signatures with a reasoning strategy. Built-in modules include:

- `dspy.Predict` — direct input→output
- `dspy.ChainOfThought` — adds step-by-step reasoning before the output field
- `dspy.ReAct` — tool-using agent loop (reason + act cycles)

Modules compose into pipelines like standard Python objects. Each module becomes an independently optimizable prompt node in the computational graph.

## Optimization loop

Given a compiled program, DSPy optimizers search the space of prompt instructions and few-shot demonstrations to maximize the metric:

```python
optimizer = dspy.MIPROv2(metric=my_metric, auto="medium")
compiled_pipeline = optimizer.compile(pipeline, trainset=train_examples)
```

[MIPROv2](https://arxiv.org/abs/2406.11695) uses Bayesian optimization. It bootstraps candidate demonstrations from high-scoring traces, generates instruction variants by inspecting the program structure and data, then searches combinations across all modules jointly. COPRO uses coordinate ascent, hill-climbing one module at a time. BootstrapFewShot adds demonstrations without changing instructions.

## Compound system advantage

The main benefit over per-prompt optimization is joint optimization. Take a pipeline of router → worker → verifier. Optimizing each prompt in isolation ignores how one module's output affects the modules downstream. DSPy optimizes all prompts at once against a single end-to-end metric. It accepts a change that hurts the router's instructions if that change improves the pipeline's final score.

The foundational paper ([Khattab et al., 2023, arxiv 2310.03714](https://arxiv.org/abs/2310.03714v1)) reports GPT-3.5 and llama2-13b-chat pipelines beating standard few-shot prompting by 25%+ and 65%+ respectively across multi-hop retrieval and question-answering benchmarks. It also reports 5–46% improvements over expert-written prompt chains.

## Limitations

- Optimization cost: MIPROv2 makes many LLM calls during the optimization run. The cost amortizes only if the compiled pipeline runs often enough in production.
- Metric quality: a poorly specified metric makes the optimizer overfit to a proxy, so gains on the training distribution may not transfer.
- Model non-transferability: prompts optimized for one model do not reliably transfer to another. This is the same coupling that makes [per-model harness tuning](per-model-harness-tuning.md) necessary. Teams that rotate underlying models must re-optimize.
- Opacity: DSPy manages prompt text automatically. To see what is sent to the LLM, you must extract it explicitly from the compiled program.

## Example

A code review pipeline: a router classifies the diff type (refactor, bug fix, feature), a worker generates review comments, and a verifier checks that all changed functions are addressed.

Without DSPy: you maintain three hand-tuned prompts independently. A wording change in the router that improves routing accuracy can quietly degrade the worker's comprehension, because the routing labels changed format.

With DSPy: each stage is a `dspy.ChainOfThought` module. A single metric — the fraction of changed functions that receive a comment — guides joint optimization. MIPROv2 finds instruction and demonstration combinations that maximize end-to-end coverage, including routing formats the worker can consume.

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

- [GEPA: Reflective Prompt Evolution with Pareto Selection](gepa-reflective-prompt-evolution.md) — sibling DSPy optimizer that uses natural-language reflection on traces instead of Bayesian search over instructions
- [Evaluator-Optimizer Pattern](evaluator-optimizer.md) — iterative refinement loop where an evaluator critiques generator output
- [Harness Hill-Climbing](harness-hill-climbing.md) — systematic improvement of agent harnesses through metric-driven iteration
- [Self-Rewriting Meta-Prompt Loop](self-rewriting-meta-prompt-loop.md) — agents that autonomously improve their own system prompts without external optimization
- [Agentic Flywheel](agentic-flywheel.md) — closed loop where agents analyze traces and metrics to generate harness improvements
- [Loop Strategy Spectrum](../../loop-engineering/loop-strategy-spectrum.md) — choosing between accumulated, compressed, and fresh-context loop strategies
- [Cost-Aware Agent Design](../../token-engineering/cost-aware-agent-design.md) — routing by complexity to match model cost to task difficulty
