---
title: "Cost-Aware Agent Design: Route by Complexity, Not Habit"
description: "Match model capability to task complexity: fast models for exploration, capable models for implementation, powerful models for architecture."
tags:
  - agent-design
  - cost-performance
  - source:opendev-paper
  - long-form
---

# Cost-Aware Agent Design: Route by Complexity, Not Habit

> Cost-aware agent design matches model capability to task complexity, classifies agents by initialization token weight, assigns specialized roles (action, thinking, critique, vision, compact) with independent fallback chains, and applies cascade routing and economic multiplier logic to minimize cost without sacrificing output quality.

## The Routing Principle

Model cost scales with token volume and tier. Top-tier models on every task waste compute; cheap models on complex tasks produce rework [unverified].

[Claude Code supports per-agent model selection](https://code.claude.com/docs/en/sub-agents) via the `model` field, routing each task type to the appropriate tier.

| Task Type | Characteristics | Model Tier |
|-----------|-----------------|------------|
| File search, exploration | High volume, low reasoning | Fast (e.g., Haiku) |
| Code implementation | Balanced capability and speed | Balanced (e.g., Sonnet) |
| Architecture, complex refactoring | Deep reasoning required | Powerful (e.g., Opus) |

## Agent Weight Taxonomy

Agent initialization cost — tokens consumed by system prompt, tool definitions, and loaded skills — directly affects composability. A [community analysis](https://claudelog.com/mechanics/agent-engineering) classifies agents by initialization weight:

| Weight Class | Token Budget | Composability |
|-------------|-------------|---------------|
| Lightweight | <3k tokens | High — fast startup, frequent delegation viable |
| Medium | 10–15k tokens | Moderate — noticeable context cost per invocation |
| Heavy | 25k+ tokens | Low — bottleneck in multi-agent workflows |

**Treat initialization cost as a performance budget.** Lightweight agents get composed more because they fit within context constraints. Heavy agents are justified only when the task requires specialization that cannot be decomposed [unverified].

## big.LITTLE Multi-Model Orchestration

Borrowed from [CPU architecture](https://en.wikipedia.org/wiki/Big.LITTLE): powerful cores for demanding work, efficient cores for background tasks. [Claude Code's Explore subagent](https://code.claude.com/docs/en/sub-agents) implements this — Haiku handles read-only exploration while the main model reasons. A [community analysis](https://claudelog.com/mechanics/agent-engineering) suggests 2-2.5x cost reduction at 85-95% quality [unverified].

**Model rotation**: start with the cheaper model, escalate only on validation failure. This works when validation is cheap and deterministic — test suites, linters, type checkers.

**Cascade routing**: [FrugalGPT](https://arxiv.org/abs/2305.05176) demonstrated up to 98% cost reduction by querying cheaper models first and escalating only when confidence is low. No coding tool implements this natively — the cascade pattern remains a manual or custom implementation. Approximate it with a two-pass pattern: fast model first, deterministic gate (tests, linter, type checker), escalate to capable model on failure.

## Roo Code: Mode-Level Routing

Roo Code assigns [different models to different modes](https://docs.roocode.com/features/custom-modes) — Architect, Code, Ask, and Orchestrator. When the mode switches, the model switches automatically. The recommended pattern: strong reasoning models for Architect mode, cheaper models for Code mode. This achieves similar cost segmentation to per-subagent assignment, at the mode level rather than the skill level.

## Role-Based Multi-Model Routing

Complexity routing decides *which tier*; role routing decides *which capability*. The OPENDEV paper defines five model roles, each independently configurable with fallback chains for graceful degradation ([Bui, 2026 §2.2.5](https://arxiv.org/abs/2603.05344)):

| Role | Purpose | Fallback |
|------|---------|----------|
| Action | Primary execution model for tool-based reasoning | Default for all workloads |
| Thinking | Extended reasoning without tool access | Action model |
| Critique | Self-evaluation of output (selective, not every turn) | Thinking model, then Action model |
| Vision | Vision-language model for screenshots and images | Action model (if vision-capable) |
| Compact | Fast summarization during context compaction | Action model |

Provider abstraction separates role assignment from model identity — swap providers without modifying agent code ([Bui, 2026 §2.2.5](https://arxiv.org/abs/2603.05344)). HTTP client slots initialize lazily; only models actually used in a session are initialized. Model capabilities (context length, vision support, reasoning features) are cached locally with time-to-live refresh, enabling offline startup and background updates.

## Premium Request Economics

In GitHub Copilot, [premium request multipliers](https://docs.github.com/en/copilot/concepts/billing/copilot-requests) make model choice a direct economic decision:

| Model Tier | Examples | Multiplier |
|-----------|----------|------------|
| Budget | Claude Haiku 4.5, Grok Code Fast 1 | 0.25x–0.33x |
| Included | GPT-5 mini, GPT-4.1, GPT-4o | 0x (no premium cost) |
| Standard | Claude Sonnet 4/4.5/4.6, Gemini 2.5 Pro | 1x |
| Premium | Claude Opus 4.5/4.6 | 3x |
| Ultra | Claude Opus 4.6 (fast) | 30x |

Using a 1x model for tasks that a 0.33x model handles equally well consumes three times the premium request budget for no quality gain. GitHub Copilot's Auto mode provides a [10% multiplier discount](https://docs.github.com/en/copilot/concepts/billing/copilot-requests) and lets users override the selected model at any time ([GitHub Changelog: Auto Model Selection](https://github.blog/changelog/2025-11-11-auto-model-selection-for-copilot-in-visual-studio-in-public-preview/)).

## Model Deprecation Awareness

Model IDs have finite lifespans — `claude-3-haiku-20240307` is deprecated and retires April 19, 2026, with Haiku 4.5 as the migration path ([Anthropic models page](https://docs.anthropic.com/en/docs/about-claude/models)). Hardcoded IDs break silently at retirement; the API returns an error rather than routing to a successor. Use display names (`haiku`, `sonnet`, `opus`) where possible, and pin full IDs only when reproducibility requires it.

## Tool SEO: Optimizing Agent Descriptions

[Claude Code uses the `description` field for delegation decisions](https://code.claude.com/docs/en/sub-agents). A [community analysis](https://claudelog.com/mechanics/agent-engineering) terms this "Tool SEO."

Activation keywords that improve delegation reliability:

- "use PROACTIVELY" — triggers delegation without explicit request
- "Use immediately after [action]" — ties delegation to workflow events
- "[domain] specialist" — narrows matching to relevant tasks

Effective descriptions combine activation triggers, domain scope, and temporal context — features that help the orchestrator match tasks to agents.

## Anti-Patterns

**Default everything to the top tier.** Safe but wasteful at scale.

**Heavy agents for simple tasks.** Decompose into lightweight agents.

**Vague agent descriptions.** "Helps with code" gives no delegation signal.

## Example

The following Claude Code sub-agent configuration routes file exploration to a fast model while reserving the balanced model for implementation tasks. The agent descriptions use activation keywords to guide orchestrator delegation.

```json
{
  "agents": [
    {
      "name": "explorer",
      "model": "claude-haiku-4-5",
      "description": "Use PROACTIVELY for any read-only codebase exploration: searching files, reading source, tracing call paths, listing directories. Use immediately after receiving a new task to understand the codebase before implementing.",
      "tools": ["Read", "Glob", "Grep"],
      "system": "You are a read-only exploration agent. Never write or modify files. Return findings as structured summaries."
    },
    {
      "name": "implementer",
      "model": "claude-sonnet-4-5",
      "description": "Use for writing, editing, or refactoring code once exploration is complete. Implementation specialist — invoke after the explorer agent has mapped relevant files.",
      "tools": ["Read", "Edit", "Write", "Bash"]
    },
    {
      "name": "architect",
      "model": "claude-opus-4-5",
      "description": "Use for architectural decisions, complex refactors spanning more than 5 files, or tasks requiring deep cross-cutting reasoning. Invoke sparingly.",
      "tools": ["Read", "Edit", "Write", "Bash"]
    }
  ]
}
```

The `explorer` agent's description combines "Use PROACTIVELY" with "Use immediately after receiving a new task" — two activation keywords that instruct the orchestrator to delegate exploration automatically, keeping Haiku handling the high-volume read-only work while Sonnet and Opus are reserved for tasks where their reasoning capability justifies the cost.

## Key Takeaways

- Route tasks to models by complexity — exploration to fast, implementation to balanced, architecture to powerful.
- Assign models by role (action, thinking, critique, vision, compact) with independent fallback chains for graceful degradation.
- Classify agents by initialization token weight: lightweight (<3k), medium (10–15k), heavy (25k+). Prefer lightweight.
- Craft agent descriptions with activation keywords to improve orchestrator delegation accuracy.
- Use display names (`haiku`, `sonnet`, `opus`) rather than pinned model IDs to avoid silent breakage at model retirement.
- Cascade routing (cheap model first, escalate on validation failure) approximates FrugalGPT-style savings without native tooling support.

## Unverified Claims

- Cheap models on complex tasks produce rework [unverified]
- Heavy agents are justified only when the task requires specialization that cannot be decomposed [unverified]
- big.LITTLE multi-model orchestration suggests 2-2.5x cost reduction at 85-95% quality [unverified]

## Related

- [Token-Efficient Tool Design](../tool-engineering/token-efficient-tool-design.md)
- [Separation of Knowledge and Execution](separation-of-knowledge-and-execution.md)
- [Tool Description Quality](../tool-engineering/tool-description-quality.md)
- [Agent Backpressure](agent-backpressure.md)
- [Reasoning Budget Allocation](reasoning-budget-allocation.md)
- [Heuristic-Based Effort Scaling](heuristic-effort-scaling.md)
- [Cross-Vendor Competitive Routing](cross-vendor-competitive-routing.md)
- [Cognitive Reasoning vs Execution: A Two-Layer Agent Architecture](cognitive-reasoning-execution-separation.md)
- [Agent Composition Patterns](agent-composition-patterns.md)
- [Agent Loop Middleware](agent-loop-middleware.md)
- [Event-Driven Agent Routing](event-driven-agent-routing.md)
- [The Delegation Decision](delegation-decision.md)
- [Copilot vs Claude Billing Semantics](../human/copilot-vs-claude-billing-semantics.md)
- [Claude Code Sub-Agents](../tools/claude/sub-agents.md)
- [Agentic AI Architecture: From Prompt-Response to Goal-Directed Systems](agentic-ai-architecture-evolution.md)
- [Model a Single Agent Turn as Many Inference and Tool-Call Iterations](agent-turn-model.md)
- [Agentic Flywheel: Self-Improving Agent Systems](agentic-flywheel.md)
