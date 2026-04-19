---
title: "Instruction-Guided Code Completion: Controlling What Models Generate"
description: "Code completion models that score well on benchmarks often ignore user instructions during completion; explicit implementation constraints and model selection close the gap."
tags:
  - context-engineering
  - technique
  - code-completion
  - arxiv
---

# Instruction-Guided Code Completion

> Functional correctness and instruction adherence are independent capabilities — a model that completes code correctly may still ignore your structural, algorithmic, and scope constraints.

## The Problem

Standard benchmarks measure whether generated code passes tests — HumanEval ([Chen et al., 2021](https://arxiv.org/abs/2107.03374)) scores functional correctness via unit tests and gives no signal on *how* the model implemented the solution. Developers routinely specify implementation constraints: a specific algorithm, a structural pattern, a limited completion scope. C3-Bench results show most models treat scale instructions as suggestions — open-source models score as low as 5–7% on scale-control tasks — while implementation-control adherence reaches only 50–60% even for top proprietary models.

C3-Bench (arxiv [2601.15879](https://arxiv.org/abs/2601.15879)) is the first benchmark to measure this gap directly, testing 2,195 Python tasks across two instruction categories.

## Two Types of Completion Instructions

```mermaid
graph LR
    A[Developer Instruction] --> B[Implementation Control<br/>ICC]
    A --> C[Scale Control<br/>SCC]
    B --> D[Algorithm choice<br/>Control flow<br/>Structural pattern<br/>Parameter constraints]
    C --> E[Line count<br/>Block scope<br/>Statement boundaries]
```

**Implementation-Control (ICC)** instructions specify *how* to implement: use recursion instead of iteration, follow a specific design pattern, constrain parameter types. Models handle these reasonably well — proprietary models reach 50-60% instruction-following rates.

**Scale-Control (SCC)** instructions specify *how much* to generate: complete only the next three lines, fill in just the if-block, stop at the function boundary. Even advanced models like Gemini-2.0-Flash (7.0% SCC) and GPT-4o (24.1% SCC) fail to respect scope boundaries in most cases.

## Benchmark Rankings Mislead

Open-source models that top standard leaderboards underperform on instruction adherence. Qwen2.5-Coder-32B scores 49.2% on CrossCodeEval but only 38.7% on ICC instruction-following. Claude 3.5 Sonnet reaches 60.9% ICC — a gap invisible in standard rankings.

If your workflow involves guided completions (Cursor Composer, Copilot Chat, agent-driven code generation), benchmark scores are not a reliable proxy for how well the model will follow your instructions.

## What Works

### Be Explicit About Implementation Constraints

Ablation studies show that removing instructions from prompts causes instruction-following scores to drop while functional correctness stays roughly the same — models do respond to fine-grained guidance. Specify:

- **Algorithmic approach**: "Use iterative depth-first search, not recursion"
- **Structural patterns**: "Implement as a generator that yields results"
- **Control flow**: "Handle the error case first with an early return"
- **Parameter constraints**: "Accept only keyword arguments"

### Do Not Rely on Scale Instructions

Asking a model to "complete only the next 3 lines" or "just fill in the if-block" is unreliable across most models. Instead:

- Use explicit stop markers or delimiters in context
- Post-process completions to trim to the desired scope
- Structure prompts so the completion boundary is syntactically unambiguous

### Select Models for Instruction Adherence

For workflows with heavy instruction guidance — which is the norm for agent-assisted coding — instruction-following capability matters more than raw completion accuracy. At the time of the C3-Bench evaluation (early 2025), proprietary models led on instruction-following: Claude 3.5 Sonnet reached 60.9% ICC and 50.8% SCC, while the top open-source model (Qwen2.5-Coder-32B) scored 38.7% ICC and 5.2% SCC. Model capabilities shift with each release — re-evaluate when adopting a new model version.

### Training Improves Instruction-Following

IFCoder (a fine-tuned Qwen2.5-Coder variant) improved ICC instruction-following from 38.7% to 52.5% and SCC from 5.2% to 80.7% using 200K synthetic instruction-completion pairs — while also improving functional correctness. This suggests instruction-following is a trainable capability, not an inherent limitation. Teams running local models can invest in instruction-tuning data to close the gap.

## When This Backfires

Instruction-guided completion increases prompt complexity and slows iteration velocity. These conditions reduce its value or make it counterproductive:

- **Exploratory or prototype code**: When constraints are not yet known, injecting implementation instructions prematurely locks in decisions before the design is stable. Models constrained to a specific algorithm or structural pattern resist pivoting as the solution evolves.
- **Low ICC compliance models**: If the model in use scores below ~40% on implementation-control adherence, instruction guidance produces inconsistent results. Prompts grow longer, constraint satisfaction varies run-to-run, and the overhead outweighs the benefit. Verify model ICC rates before investing in instruction-heavy workflows.
- **Scale control remains unreliable**: Even with best-practice prompting, most models ignore scope boundaries more than half the time (C3-Bench SCC median: under 25% for non-fine-tuned models). Workflows that depend on precise output length control require post-processing or syntactic delimiters — instruction guidance alone is not sufficient.

## Key Takeaways

- **Instruction adherence and functional correctness are orthogonal.** A model that writes correct code may still ignore your structural and scope constraints.
- **Implementation instructions work; scale instructions do not.** Tell models *how* to implement (algorithm, pattern, flow) but do not rely on telling them *how much* to generate.
- **Benchmark rankings do not predict instruction-following.** Evaluate models on the specific capability your workflow requires.
- **Fine-tuning on instruction-completion pairs closes the gap.** If you run local models, synthetic instruction data is an effective lever.

## Example

A developer needs a function to flatten a nested dictionary. Without instruction guidance, the model chooses its own approach:

```python
# Prompt (no instruction guidance):
# Write a function to flatten a nested dictionary

def flatten_dict(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
```

The model produces correct code but uses recursion, builds intermediate lists, and returns a new dictionary. With explicit implementation constraints:

```python
# Prompt with instruction guidance:
# Write a function to flatten a nested dictionary.
# - Use an iterative approach with an explicit stack (no recursion)
# - Yield key-value pairs as a generator
# - Use '/' as the separator
# - Handle only dict nesting (skip lists)

def flatten_dict(nested, sep='/'):
    stack = [('', nested)]
    while stack:
        prefix, current = stack.pop()
        for key, value in current.items():
            full_key = f"{prefix}{sep}{key}" if prefix else key
            if isinstance(value, dict):
                stack.append((full_key, value))
            else:
                yield full_key, value
```

The second prompt specifies algorithm (iterative with stack), output structure (generator), separator choice, and scope boundary. C3-Bench results show that models follow these implementation-control instructions roughly 50-60% of the time — better than scale instructions but still unreliable enough to require verification.

## Related

- [Context Priming](context-priming.md) — Loading relevant context before completion shapes output quality; instruction-guided completion is a specific form of this discipline
- [Prompt Layering](prompt-layering.md) — Instructions arrive from multiple sources simultaneously; understanding precedence affects whether completion instructions are followed
- [Pass@k Metrics](../verification/pass-at-k-metrics.md) — Standard evaluation metric that measures functional correctness but not instruction adherence
- [Token-Efficient Code Generation](token-efficient-code-generation.md) — Structural patterns that reduce generated code tokens; a complementary lens on controlling model output quality
- [Repository-Level Retrieval for Code Generation](repository-level-retrieval-code-generation.md) — Cross-file context improves completion accuracy; instruction adherence and retrieval quality are complementary dimensions of code generation control
