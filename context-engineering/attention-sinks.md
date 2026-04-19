---
title: "Attention Sinks: Why First Tokens Always Win"
description: "Transformer models disproportionately attend to initial tokens regardless of their semantic content — position determines attention weight, not importance."
tags:
  - context-engineering
aliases:
  - Lost in the Middle
  - Critical Instruction Repetition
  - Attention Bias and Instruction Placement
---

# Attention Sinks: Why First Tokens Always Win

> Transformer models disproportionately attend to initial tokens regardless of their semantic content — position determines attention weight, not importance.

!!! info "Also known as"
    Lost in the Middle, Critical Instruction Repetition, Attention Bias and Instruction Placement

## What Attention Sinks Are

In autoregressive transformer models, attention mechanisms exhibit a structural bias toward early tokens in the sequence. Initial tokens act as attention sinks: they absorb a disproportionate share of attention across all subsequent tokens, regardless of their semantic relevance to the current generation step — a phenomenon confirmed empirically by Xiao et al. (2023), who found that preserving just the KV cache of early tokens largely recovers the performance of full-window attention ([StreamingLLM](https://arxiv.org/abs/2309.17453)).

This is not a quirk to mitigate — it is a structural property of how causal attention masking operates. Every token the model generates is influenced more by early tokens than by semantically equivalent tokens placed later in the context.

## Practical Implications

**The role definition placed first shapes behaviour most.** Whatever role, persona, or constraint appears at the very beginning of a system prompt receives stronger model attention than the same constraint placed later. An instruction like "you are a security reviewer who never produces code without first identifying potential vulnerabilities" carries more weight at position 1 than at position 500.

**Boilerplate wastes the highest-attention real estate.** A system prompt that opens with:

```
# System Prompt v2.3 — Agent: Code Reviewer
# Created: 2025-01-01
# Last updated: 2025-03-08

You are an AI assistant designed to help developers...
```

has consumed the strongest-attention positions with metadata and generic preamble. The actual rules, constraints, and role definition follow in weaker-attention territory.

**What you ask first, the agent recalls best.** In a long conversation, restating a critical constraint at the point where you need it — rather than relying on an early-session statement — exploits the recency effect at the other end of the U-shaped attention curve.

## Applying the Pattern

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

## Relationship to the U-Shaped Curve

Attention sinks explain the strong-start portion of the U-shaped attention curve. The strong-end portion is explained by recency effects in autoregressive generation — Liu et al. (2023) demonstrated empirically that performance is highest when relevant information appears at the beginning or end of the context window, degrading significantly in the middle ([Lost in the Middle](https://arxiv.org/abs/2307.03172)). Together:

- First tokens: attention sink bias (high recall)
- Middle tokens: weakest attention (low recall)
- Last tokens: recency effect (high recall)

Content that must be reliably followed belongs at either end. Content the agent refers to passively can occupy the middle.

## Key Takeaways

- Initial tokens receive disproportionate attention — open instruction files with your most critical constraint, not context-setting prose.
- Boilerplate at the top of a system prompt wastes the highest-attention positions on low-value content.
- The role and constraints placed first shape agent behaviour most strongly across the session.
- Attention sinks and recency effects are the two mechanisms behind the U-shaped attention distribution.

## When This Backfires

- **Context compression discards early tokens.** Techniques that compress or truncate context — including some KV-cache eviction strategies — may discard early tokens, neutralizing the primacy advantage. Placing critical constraints first is only reliable when the full prompt prefix is retained.
- **Fine-tuned models with instruction following training.** RLHF and instruction-tuning can shift how models weight positional bias versus semantic relevance. A model fine-tuned to follow instructions placed anywhere in the prompt may not exhibit the same sink strength as a base model.
- **RAG pipelines with late-injected context.** In retrieval-augmented workflows, retrieved chunks are typically injected mid-prompt. If the critical constraint is buried in a static preamble before substantial retrieved content, positional advantage may be outweighed by semantic relevance of the retrieved material.
- **Very short prompts.** Attention sink effects are most pronounced in long sequences. In short prompts (under a few hundred tokens), positional placement has less observable impact on model behavior.

## Related

- [Lost in the Middle: The U-Shaped Attention Curve](lost-in-the-middle.md)
- [Critical Instruction Repetition: Exploiting Primacy and Recency Bias](../instructions/critical-instruction-repetition.md)
- [Goal Recitation](goal-recitation.md)
- [Prompt Layering](prompt-layering.md)
- [Layered Context Architecture](layered-context-architecture.md)
- [Static Content First: Maximizing Prompt Cache Hits](static-content-first-caching.md)
- [Context Compression Strategies](context-compression-strategies.md)
- [Context Engineering: The Discipline of Designing Agent Context](context-engineering.md)
