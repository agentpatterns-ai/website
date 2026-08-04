---
title: "Attention Sinks: Why First Tokens Always Win"
term: "Attention Sinks"
description: "Transformer models disproportionately attend to initial tokens regardless of their semantic content. Position determines attention weight, not importance."
tags:
  - context-engineering
  - tool-agnostic
  - arxiv
aliases:
  - Critical Instruction Repetition
  - Attention Bias and Instruction Placement
last_reviewed: 2026-06-13
maturity: emerging
---

# Attention Sinks: Why First Tokens Always Win

> Transformer models disproportionately attend to initial tokens regardless of their semantic content. Position determines attention weight, not importance.

Related lesson: [Lost in the Middle](https://learn.agentpatterns.ai/context-engineering/lost-in-the-middle/). This concept features in a hands-on lesson with quizzes.

!!! info "Also known as"
    Lost in the Middle, Critical Instruction Repetition, Attention Bias and Instruction Placement

## What attention sinks are

Attention in autoregressive transformer models is structurally biased toward early tokens. The first tokens act as attention sinks. They absorb a large share of attention from every later token, whatever their meaning at the current generation step. Xiao et al. (2023) confirmed this: keeping just the KV cache of the early tokens largely recovers the performance of full-window attention ([StreamingLLM](https://arxiv.org/abs/2309.17453)).

The attention sink is a structural property of how causal attention masking works, not a quirk to fix. Every token the model generates is shaped more by early tokens than by equivalent tokens placed later in the context.

A more precise account narrows the mechanism. Gu et al. (2024) found that the sink concentrates on the first token rather than spreading smoothly across an early-position band. It is a learned behavior that emerges during pre-training under softmax normalization. Replace softmax with sigmoid attention and the sink does not appear in models up to 1B parameters, so it is not strictly inherent to causal masking ([When Attention Sink Emerges in Language Models](https://arxiv.org/abs/2410.10781)). The practical takeaway holds: the strongest-attention position is the very start of the prompt. But treat "earlier is stronger" as a first-token-anchored, softmax-driven effect, not a uniform positional gradient.

## Practical implications

The role definition placed first shapes behavior most. Whatever role, persona, or constraint appears at the very start of a system prompt gets stronger attention than the same constraint placed later. An instruction like "you are a security reviewer who never produces code without first identifying potential vulnerabilities" carries more weight at position 1 than at position 500.

Boilerplate wastes the highest-attention positions. A system prompt that opens with:

```
# System Prompt v2.3 — Agent: Code Reviewer
# Created: 2025-01-01
# Last updated: 2025-03-08

You are an AI assistant designed to help developers...
```

has spent the strongest-attention positions on metadata and generic preamble. The actual rules, constraints, and role definition follow in weaker-attention territory.

What you ask first, the agent recalls best. In a long conversation, restate a critical constraint at the point where you need it rather than relying on an early-session statement. This uses the recency effect at the other end of the U-shaped attention curve.

## Applying the pattern

Start instruction files with the constraint or role that must be most reliably followed:

```
Never output code that modifies authentication or session state without
first identifying the downstream security impact.

You are reviewing a pull request...
```

Not:

```
You are an AI code reviewer assistant. Your goal is to provide
helpful, accurate code review feedback. When reviewing code, consider...
[10 lines later]
Never output code that modifies authentication or session state...
```

The rule comes first; the context follows. The agent's strongest recall is on the rule.

## Relationship to the U-shaped curve

Attention sinks explain the strong-start portion of the U-shaped attention curve. Recency effects in autoregressive generation explain the strong-end portion. Liu et al. (2023) showed that performance is highest when relevant information sits at the beginning or end of the context window, and drops sharply in the middle ([Lost in the Middle](https://arxiv.org/abs/2307.03172)). Together:

- First tokens: attention sink bias (high recall)
- Middle tokens: weakest attention (low recall)
- Last tokens: recency effect (high recall)

Content that must be reliably followed belongs at either end; content the agent only consults passively can occupy the middle.

## FAQ

**Is the attention sink just "earlier tokens always matter more"?**

Not quite. Gu et al. found the sink concentrates on the first token rather than spreading smoothly across an early-position band, and that it is a learned behavior emerging during pre-training under softmax normalization. Swap softmax for sigmoid attention and the sink does not appear in models up to 1B parameters. Treat it as first-token-anchored, not a uniform positional gradient.

**Where do I put a constraint when the conversation is already long?**

Restate it at the point where you need it rather than relying on an early-session statement. That exploits the recency effect at the other end of the U-shaped curve, where performance peaks when relevant information sits at the beginning or end of the window and drops sharply in the middle. Middle positions suit content the agent only consults passively.

**When does putting the constraint first stop being reliable?**

When the full prompt prefix is not preserved. Context compression and some KV-cache eviction strategies discard early tokens and neutralize the primacy advantage. In retrieval pipelines, chunks are injected mid-prompt, so a constraint buried in a static preamble can be outweighed by the semantic relevance of that material. Under a few hundred tokens, placement has little observable effect.

## Key Takeaways

- Put your single most important constraint on the first line of a system prompt or instruction file, ahead of any persona description or version header.
- Audit an existing system prompt's opening lines for version headers, dates, or generic preamble, and move a real constraint there instead.
- In a long-running conversation, do not rely on an early instruction to still carry weight. Restate a critical constraint near the turn where you need it followed.
- Before relying on first-position placement, confirm your context pipeline preserves the full prompt prefix. Compression or KV-cache eviction can silently discard it.

## When this backfires

- Context compression discards early tokens. Techniques that compress or truncate context, including some KV-cache eviction strategies, may discard early tokens and neutralize the primacy advantage. Placing critical constraints first is only reliable when the full prompt prefix is kept ([Context Compression Strategies](context-compression-strategies.md)).
- Fine-tuned models with instruction-following training. RLHF and instruction-tuning can shift how models weigh positional bias against semantic relevance. A model fine-tuned to follow instructions placed anywhere in the prompt may not show the same sink strength as a base model.
- RAG pipelines with late-injected context. In retrieval-augmented workflows, retrieved chunks are usually injected mid-prompt. If the critical constraint is buried in a static preamble before a lot of retrieved content, the semantic relevance of that material may outweigh its positional advantage.
- Very short prompts. Attention sink effects are strongest in long sequences. In short prompts (under a few hundred tokens), positional placement has less observable effect on model behavior.

## Related

- [Lost in the Middle: The U-Shaped Attention Curve](lost-in-the-middle.md)
- [Critical Instruction Repetition: Exploiting Primacy and Recency Bias](../instructions/critical-instruction-repetition.md)
- [Goal Recitation](goal-recitation.md)
- [Prompt Layering](prompt-layering.md)
- [Layered Context Architecture](layered-context-architecture.md)
- [Static Content First: Maximizing Prompt Cache Hits](static-content-first-caching.md)
- [Context Compression Strategies](context-compression-strategies.md)
- [Context Engineering: The Discipline of Designing Agent Context](context-engineering.md)
