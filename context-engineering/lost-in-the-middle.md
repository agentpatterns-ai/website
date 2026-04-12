---
title: "Lost in the Middle: Understanding U-Shaped Attention"
description: "Model attention is strongest at the start and end of a context window; content in the middle receives significantly less focus regardless of its importance"
tags:
  - context-engineering
aliases:
  - Attention Sinks
  - Critical Instruction Repetition
  - Attention Bias
  - Instruction Placement
---

# Lost in the Middle: The U-Shaped Attention Curve

> Model attention is strongest at the start and end of a context window; content in the middle receives significantly less focus regardless of its importance.

!!! info "Also known as"
    Attention Sinks, Critical Instruction Repetition, Attention Bias and Instruction Placement

## The Attention Distribution

Transformer models do not process a context window uniformly. Research has consistently shown that attention is distributed in a U-shape: content near the beginning and end of the context receives the strongest attention; content in the middle zone receives substantially less ([Liu et al., 2023](https://arxiv.org/abs/2307.03172)). The precise magnitude varies by model, but the positional bias is consistent across architectures tested.

This is a structural property of how transformer attention mechanisms weight earlier and later tokens, not a quirk of any particular model or instruction format.

## What This Means in Practice

**Instruction position determines instruction effectiveness.** An instruction placed in section 5 of a 10-section system prompt is in the weak attention zone. The instruction may be well-written and clearly stated, but the model is statistically less likely to follow it than an identical instruction placed at the top or bottom — position affects retrieval accuracy even when content is identical ([Liu et al., 2023](https://arxiv.org/abs/2307.03172)).

**Adding content degrades surrounding content.** Each instruction added in the middle does not merely dilute attention — it pushes existing instructions further from the high-attention edges. A long AGENTS.md file buries most of its instructions in the zone where they are least likely to be followed.

**The middle is for reference, not rules.** Content that must be reliably followed belongs at the edges. Content that the agent retrieves and refers to — schemas, examples, lookup information — can tolerate mid-context placement because the agent is actively pulling it, not relying on passive attention.

## Structural Implications

For instruction files (system prompts, AGENTS.md, skill instructions):

- Place the most critical rules first — before any background context or preamble
- Place the next most critical rules last — as a closing section or summary
- Minimise the total number of instructions to reduce the size of the middle zone
- Reserve the middle for reference material the agent will actively read, not rules the agent must remember

For conversation context:

- If a constraint was stated early in a long conversation and the agent appears to have forgotten it, restate it at the end rather than assuming the agent will scroll back
- After [context compression](context-compression-strategies.md), restate the objective explicitly so it appears near the current end of context

## Example

The following `AGENTS.md` structure places the most critical rules at the edges and relegates reference material to the middle — directly applying the U-shape attention pattern.

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

The opening section carries the rules the agent must reliably follow. The middle holds project structure and conventions — content the agent actively retrieves when needed, not rules it must remember passively. The closing section restates the most critical constraint so it sits in the high-attention tail of the context.

## When This Backfires

- **Short contexts**: When the full input fits within a few hundred tokens, there is no meaningful middle zone. Placement optimisation has negligible effect and adds unnecessary structural overhead.
- **Retrieval-augmented flows**: If the model is explicitly instructed to retrieve a specific document section, positional bias is largely overridden by the retrieval directive. Passive attention is not the bottleneck.
- **Long-context models with position-aware training**: Some models (e.g., those trained with specific long-context fine-tuning or instruction-following reinforcement) exhibit reduced middle-degradation. Treat placement as a default safeguard, not a universal guarantee.
- **Frequently refreshed context**: In agent loops that compact or re-inject context at each step, the "middle" shifts continuously. Optimising static layout matters less than ensuring critical state survives each compaction cycle.

## Key Takeaways

- Model attention follows a U-shape: strongest at the start and end, weakest in the middle.
- Critical rules belong at the beginning and end of instruction files; reference material can occupy the middle.
- Adding instructions in the middle of a long file pushes existing instructions further into the low-attention zone.
- Keep instruction files short enough to minimise the size of the weak-attention middle zone.

## Related

- [Context Engineering: The Discipline of Designing Agent Context](context-engineering.md)
- [Attention Sinks: Why First Tokens Always Win](attention-sinks.md)
- [Critical Instruction Repetition: Exploiting Primacy and Recency Bias](../instructions/critical-instruction-repetition.md)
- [The Infinite Context](../anti-patterns/infinite-context.md)
- [Context Priming: Pre-Loading Files for AI Agent Tasks](context-priming.md)
- [Goal Recitation: Countering Drift in Long Sessions](goal-recitation.md)
- [Prompt Layering: How Instructions Stack and Override](prompt-layering.md)
- [Context Window Management: The Dumb Zone](context-window-dumb-zone.md)
- [Dynamic System Prompt Composition](dynamic-system-prompt-composition.md)
- [Context Budget Allocation](context-budget-allocation.md)
- [KV Cache Invalidation in Local Inference](kv-cache-invalidation-local-inference.md)
- [Discoverable vs Non-Discoverable Context](discoverable-vs-nondiscoverable-context.md)
- [Manual Compaction Strategy for Dumb Zone Mitigation](manual-compaction-dumb-zone-mitigation.md)
- [Prompt Compression: Maximizing Signal Per Token](prompt-compression.md)
- [Layered Context Architecture](layered-context-architecture.md)
- [Observation Masking: Filter Tool Outputs from Context](observation-masking.md)
- [Phase-Specific Context Assembly](phase-specific-context-assembly.md)
- [Retrieval-Augmented Agent Workflows: On-Demand Context](retrieval-augmented-agent-workflows.md)
- [Context Hub: On-Demand Versioned API Docs for Coding Agents](context-hub.md)
