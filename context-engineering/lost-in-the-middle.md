---
title: "Lost in the Middle: The U-Shaped Attention Curve"
term: "Lost in the Middle"
description: "Model attention is strongest at the start and end of a context window; content in the middle receives significantly less focus regardless of its importance."
tags:
  - context-engineering
  - tool-agnostic
aliases:
  - Critical Instruction Repetition
  - Attention Bias
  - Instruction Placement
last_reviewed: 2026-06-13
maturity: established
---

# Lost in the Middle: The U-Shaped Attention Curve

> Model attention is strongest at the start and end of a context window; content in the middle receives significantly less focus regardless of its importance.

Learn it hands-on: [Lost in the Middle guided lesson with quizzes](https://learn.agentpatterns.ai/context-engineering/lost-in-the-middle/).

!!! info "Also known as"
    Attention Sinks, Critical Instruction Repetition, Attention Bias and Instruction Placement

## The attention distribution

Transformer models do not read a context window evenly. Research shows attention follows a U-shape. Content near the beginning and end of the context gets the strongest attention, and content in the middle gets much less ([Liu et al., 2023](https://arxiv.org/abs/2307.03172); [Hsieh et al., 2024](https://arxiv.org/abs/2406.16008)). The size of the gap varies by model, but the positional bias holds across the architectures tested.

This is a structural property of how transformer attention weights earlier and later tokens. It is not a quirk of any particular model or instruction format. Later theoretical work traces the pattern to how causal masking and relative positional encodings such as RoPE interact, which together bias attention toward the edges of the sequence ([Wu et al., 2025](https://arxiv.org/abs/2502.01951)).

## What this means in practice

Position decides how well an instruction works. An instruction placed in section 5 of a 10-section system prompt sits in the weak attention zone. The instruction may be well written and clear, but the model is statistically less likely to follow it than the same instruction placed at the top or bottom. Position affects retrieval accuracy even when the content is identical ([Liu et al., 2023](https://arxiv.org/abs/2307.03172)).

Adding content degrades the content around it. Each instruction added in the middle does more than dilute attention. It pushes existing instructions further from the high-attention edges. A long AGENTS.md file buries most of its instructions in the zone where they are least likely to be followed.

Use the middle for reference, not rules. Content that must be followed reliably belongs at the edges. Content that the agent retrieves and refers to, such as schemas, examples, and lookup information, can sit mid-context because the agent is actively pulling it rather than relying on passive attention.

## Structural implications

For instruction files such as system prompts, AGENTS.md, and skill instructions:

- Place the most critical rules first, before any background context or preamble
- Place the next most critical rules last, as a closing section or summary
- Keep the total number of instructions low to shrink the middle zone
- Reserve the middle for reference material the agent will actively read, not rules the agent must remember

For conversation context:

- If you stated a constraint early in a long conversation and the agent seems to have forgotten it, restate it at the end rather than expecting the agent to scroll back
- After [context compression](context-compression-strategies.md), restate the objective so it sits near the current end of context

## Example

The following `AGENTS.md` structure places the most critical rules at the edges and moves reference material to the middle, applying the U-shape attention pattern directly.

````markdown
# AGENTS.md

## Critical Rules (read first)
- Never commit directly to `main`; always open a pull request
- All secrets must use environment variables — never hardcode credentials

## Reference: Project Structure
```
src/
  api/        # Express routes
  services/   # Business logic
  models/     # Prisma schema
tests/        # Jest test suites
```

## Reference: Coding Conventions
- Use `camelCase` for variables, `PascalCase` for classes
- Prefer `async/await` over `.then()` chains
- Add JSDoc comments to all exported functions

## Closing Reminders (read last)
- Run `npm test` before marking any task complete
- Never commit directly to `main`
````

The opening section carries the rules the agent must follow reliably. The middle holds project structure and conventions, which the agent retrieves when needed rather than remembers passively. The closing section restates the most critical constraint so it sits in the high-attention tail of the context.

## When this backfires

- Short contexts: when the full input fits within a few hundred tokens, there is no meaningful middle zone. Placement tuning has little effect and adds structural overhead you do not need.
- [Retrieval-augmented flows](retrieval-augmented-agent-workflows.md): when you tell the model to retrieve a specific document section, the retrieval directive largely overrides positional bias. Passive attention is not the bottleneck.
- Long-context models with position-aware training: some models, such as those trained with long-context fine-tuning or instruction-following reinforcement, show less middle-degradation. Treat placement as a default safeguard, not a guarantee.
- Frequently refreshed context: in agent loops that [compact](manual-compaction-dumb-zone-mitigation.md) or re-inject context at each step, the middle shifts continuously. Tuning static layout matters less than making sure critical state survives each compaction cycle.

## FAQ

**What causes the U-shaped attention curve?**

It is a structural property of how transformer attention weights earlier and later tokens, not a quirk of a particular model or instruction format. Later theoretical work traces the pattern to how causal masking and relative positional encodings such as RoPE interact, biasing attention toward the edges of the sequence ([Wu et al., 2025](https://arxiv.org/abs/2502.01951)). The size of the gap varies by model, but the bias holds across architectures tested.

**Does position matter even when the wording is good?**

Yes. An instruction placed in section 5 of a 10-section system prompt sits in the weak-attention zone; it may be well written and perfectly clear, yet the model is statistically less likely to follow it than the same instruction placed at the top or bottom. Position affects retrieval accuracy even when the content is identical ([Liu et al., 2023](https://arxiv.org/abs/2307.03172)).

**What belongs in the middle of an instruction file?**

Reference material the agent actively pulls — schemas, examples, and lookup information — rather than rules it must remember. Content that must be followed reliably belongs at the edges, because the middle relies on passive attention. Retrieval behaves differently: when you direct the model to a specific document section, the retrieval directive largely overrides positional bias.

**When is placement tuning not worth the effort?**

When the whole input fits in a few hundred tokens, there is no meaningful middle zone, so tuning adds structural overhead for no gain. Models trained with long-context fine-tuning or instruction-following reinforcement show less middle-degradation, making placement a default safeguard rather than a guarantee. In loops that compact or re-inject context each step, the middle shifts continuously anyway.

## Key Takeaways

- Model attention follows a U-shape: strongest at the start and end, weakest in the middle.
- Critical rules belong at the beginning and end of instruction files like `AGENTS.md`; reference material can occupy the middle.
- Adding instructions in the middle of a long file pushes existing instructions further into the low-attention zone.
- Keep instruction files short enough to minimize the size of the weak-attention middle zone.

## Related

- [Context Engineering: The Discipline of Designing Agent Context](context-engineering.md)
- [Attention Sinks: Why First Tokens Always Win](attention-sinks.md)
- [Critical Instruction Repetition: Exploiting Primacy and Recency Bias](../instructions/critical-instruction-repetition.md)
- [The Infinite Context](../patterns/anti-patterns/infinite-context.md)
- [Goal Recitation: Countering Drift in Long Sessions](goal-recitation.md)
- [Prompt Layering: How Instructions Stack and Override](prompt-layering.md)
- [Context Window Management: The Dumb Zone](context-window-dumb-zone.md)
- [Context Compression Strategies](context-compression-strategies.md)
