---
title: "Cost-Aware Agent Design: Route by Complexity, Not Habit"
term: "Cost-Aware Agent Design"
description: "Match model capability to task complexity: fast models for exploration, capable models for implementation, powerful models for architecture."
tags:
  - token-engineering
  - cost-performance
  - source:opendev-paper
  - long-form
  - tool-agnostic
last_reviewed: 2026-06-30
maturity: established
---

# Cost-Aware Agent Design: Route by Complexity, Not Habit

> Cost-aware agent design routes each task to the cheapest model that meets its complexity, escalating tier only when validation fails.

Learn it hands-on with the [Cost Controls and Circuit Breakers lesson](https://learn.agentpatterns.ai/harness-engineering/cost-controls-and-circuit-breakers/), a guided lesson with quizzes.

## The routing principle

Model cost scales with token volume and tier. Top-tier models on every task waste compute. Cheap models on complex tasks produce rework. [FrugalGPT](https://arxiv.org/abs/2305.05176) measures this as higher error rates when under-powered models handle tasks that need multi-step reasoning.

[Claude Code supports per-agent model selection](https://code.claude.com/docs/en/sub-agents) through the `model` field, so you route each task type to the right tier.

| Task Type | Characteristics | Model Tier |
|-----------|-----------------|------------|
| File search, exploration | High volume, low reasoning | Fast (e.g., Haiku) |
| Code implementation | Balanced capability and speed | Balanced (e.g., Sonnet) |
| Architecture, complex refactoring | Deep reasoning required | Powerful (e.g., Opus) |

## Agent weight taxonomy

Agent initialization cost — the tokens spent on system prompt, tool definitions, and loaded skills — directly affects composability. A [community analysis](https://claudelog.com/mechanics/agent-engineering) classifies agents by initialization weight:

| Weight Class | Token Budget | Composability |
|-------------|-------------|---------------|
| Lightweight | <3k tokens | High — fast startup, frequent delegation viable |
| Medium | 10–15k tokens | Moderate — noticeable context cost per invocation |
| Heavy | 25k+ tokens | Low — bottleneck in multi-agent workflows |

Treat initialization cost as a performance budget. Lightweight agents get composed more often because they fit within context limits. Heavy agents are justified only when the task needs specialization that you cannot decompose. Otherwise, splitting into lighter sub-agents is cheaper and more composable.

## big.LITTLE multi-model orchestration

This pattern comes from [CPU architecture](https://en.wikipedia.org/wiki/Big.LITTLE): powerful cores for demanding work, efficient cores for background tasks. [Claude Code's Explore subagent](https://code.claude.com/docs/en/sub-agents) applies it — Haiku handles read-only exploration while the main model reasons. A [community analysis](https://claudelog.com/mechanics/agent-engineering) reports 2 to 2.5x cost reduction at 85 to 95% quality on mixed workloads.

Cognition applies this pattern in production through Devin Fusion — a hybrid harness pairing a frontier model as the reasoning core with cheaper sidekick agents for delegated subtasks and dynamic routing between them, claiming frontier-level performance at roughly 35% lower cost ([Cognition — Devin Fusion](https://cognition.ai/blog/devin-fusion)).

Model rotation starts with the cheaper model and escalates only on validation failure. This works when validation is cheap and deterministic — test suites, linters, type checkers.

Retrieval augmentation is a second lever on the same trade-off: a cheaper model with good context can beat a bigger model used alone. On a CodeScaleBench evaluation, Claude Sonnet 4.6 paired with code-search MCP beat Fable 5 alone on 6 of 9 large-codebase tasks at roughly half the cost per quality point ([Sourcegraph — MCP and a cheaper model beat a bigger model alone](https://sourcegraph.com/blog/sourcegraph-mcp-and-a-cheaper-model-beat-a-mythos-class-model-alone)). Pairing a lower tier with targeted retrieval can beat a single high-tier call before you reach for escalation.

Cascade routing queries cheaper models first and escalates only when confidence is low. [FrugalGPT](https://arxiv.org/abs/2305.05176) showed up to 98% cost reduction this way. No coding tool implements it natively, so the cascade pattern stays a manual or custom build. Approximate it with a two-pass pattern: fast model first, deterministic gate (tests, linter, type checker), then escalate to the capable model on failure.

Routing also affects how predictable your spend is, not just the average. Escalation paths make per-task cost vary. LangChain describes techniques for making a coding agent's token spend predictable, treating bounded cost as an explicit design goal rather than a side effect of tier choice ([LangChain — making coding-agent spend predictable](https://blog.langchain.com/how-we-made-coding-agent-spend-predictable)).

## Roo Code: mode-level routing

Roo Code assigns [different models to different modes](https://docs.roocode.com/features/custom-modes) — Architect, Code, Ask, Orchestrator — and switches the model automatically when the mode switches. The recommended pattern pairs strong reasoning models with Architect mode and cheaper models with Code mode. This is the same cost segmentation as per-subagent assignment, but at the mode level.

## Role-based multi-model routing

Complexity routing decides which tier to use. Role routing decides which capability to use. The OPENDEV paper defines five model roles, each independently configurable with fallback chains for graceful degradation ([Bui, 2026 §2.2.5](https://arxiv.org/abs/2603.05344)):

| Role | Purpose | Fallback |
|------|---------|----------|
| Action | Primary execution model for tool-based reasoning | Default for all workloads |
| Thinking | Extended reasoning without tool access | Action model |
| Critique | Self-evaluation of output (selective, not every turn) | Thinking model, then Action model |
| Vision | Vision-language model for screenshots and images | Action model (if vision-capable) |
| Compact | Fast summarization during [context compaction](../context-engineering/context-compression-strategies.md) | Action model |

Provider abstraction separates role assignment from model identity, so you can swap providers without touching agent code ([Bui, 2026 §2.2.5](https://arxiv.org/abs/2603.05344)). Clients initialize lazily — only the models a session uses — and capabilities are cached locally with TTL refresh for offline startup.

## Premium request economics

In GitHub Copilot, [premium request multipliers](https://docs.github.com/en/copilot/concepts/billing/copilot-requests) make model choice a direct economic decision:

| Model Tier | Examples | Multiplier |
|-----------|----------|------------|
| Budget | Claude Haiku 4.5, Grok Code Fast 1 | 0.25x–0.33x |
| Included | GPT-5 mini, GPT-4.1, GPT-4o | 0x (no premium cost) |
| Standard | Claude Sonnet 4/4.5/4.6, Gemini 2.5 Pro | 1x |
| Premium | Claude Opus 4.5/4.6 | 3x |
| Ultra | Claude Opus 4.6 (fast) | 30x |

Using a 1x model for tasks that a 0.33x model handles just as well spends three times the premium request budget for no quality gain. GitHub Copilot's Auto mode gives a [10% multiplier discount](https://docs.github.com/en/copilot/concepts/billing/copilot-requests) and lets you override the selected model at any time ([GitHub Changelog: Auto Model Selection](https://github.blog/changelog/2025-11-11-auto-model-selection-for-copilot-in-visual-studio-in-public-preview/)).

## Model deprecation awareness

Model IDs have finite lifespans. `claude-3-haiku-20240307` is deprecated and retires on April 19, 2026, with Haiku 4.5 as the migration path ([Anthropic models page](https://docs.anthropic.com/en/docs/about-claude/models)). Hardcoded IDs break silently at retirement: the API returns an error rather than routing to a successor. Use display names (`haiku`, `sonnet`, `opus`) where you can, and pin full IDs only when reproducibility requires it.

## Tool SEO: optimizing agent descriptions

[Claude Code uses the `description` field for delegation decisions](https://code.claude.com/docs/en/sub-agents). A [community analysis](https://claudelog.com/mechanics/agent-engineering) calls this "Tool SEO."

Activation keywords that improve delegation reliability:

- "use PROACTIVELY" — triggers delegation without explicit request
- "Use immediately after [action]" — ties delegation to workflow events
- "[domain] specialist" — narrows matching to relevant tasks

Effective descriptions combine activation triggers, domain scope, and temporal context — features that help the orchestrator match tasks to agents.

## When this backfires

Validation gates are slow or absent. Cascade routing depends on cheap, deterministic validators (tests, linters, type checkers). If the validation step takes longer than the cost difference between tiers, the cascade adds latency without saving money. Measure gate cost before you commit to escalation-based routing. Routing is a design-time cost control, so pair it with a runtime measurement. Braintrust treats cost-efficiency (tokens or dollars per task at fixed quality) as a first-class eval scoring axis alongside correctness, so a routing change that quietly raises spend without improving quality shows up as a regression ([Braintrust — testing agent cost-efficiency](https://braintrust.dev/blog/test-agent-cost-efficiency)).

Single-task pipelines suffer too. A three-tier routing system — whether by task type or by [code health](../agent-design/auto-model-selection.md) — adds configuration and coordination overhead. For pipelines with one task type and low invocation volume, a single capable model at a fixed tier is simpler and often cheaper once you amortize setup and maintenance cost.

Frequently updated model rosters break role-based routing. Routing fails when a provider deprecates or renames a model tier. Teams without automated model-ID management (display names like `haiku`, capability caching with TTL) spend engineering time on breakage rather than shipping features.

High task interdependency adds friction. Some tasks cannot be cleanly separated by complexity — for example, a refactor that needs reasoning at every file edit. Routing exploration to a fast model and implementation to a capable one then backfires: the capable model must re-ingest the fast model's findings, which adds tokens and latency.

## Anti-patterns

Default everything to the top tier. Safe but wasteful at scale.

Heavy agents for simple tasks. Decompose into lightweight agents.

Vague agent descriptions. "Helps with code" gives no delegation signal.

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

The `explorer` description combines "Use PROACTIVELY" with "Use immediately after receiving a new task" — activation keywords that push the orchestrator to delegate exploration automatically, keeping Haiku on high-volume read-only work while Sonnet and Opus stay reserved for tasks that justify their cost.

## Key Takeaways

- Route tasks to models by complexity — exploration to fast, implementation to balanced, architecture to powerful.
- Assign models by role (action, thinking, critique, vision, compact) with independent fallback chains for graceful degradation.
- Classify agents by initialization token weight: lightweight (<3k), medium (10–15k), heavy (25k+). Prefer lightweight.
- Craft agent descriptions with activation keywords to improve orchestrator delegation accuracy.
- Use display names (`haiku`, `sonnet`, `opus`) rather than pinned model IDs to avoid silent breakage at model retirement.
- Cascade routing (cheap model first, escalate on validation failure) approximates FrugalGPT-style savings without native tooling support.

## Related

- [Reasoning Budget Allocation](../agent-design/reasoning-budget-allocation.md) — budget reasoning effort the same way you budget tier choice
- [Heuristic-Based Effort Scaling](../agent-design/heuristic-effort-scaling.md) — heuristics that scale model effort by task signals
- [Cross-Vendor Competitive Routing](../agent-design/cross-vendor-competitive-routing.md) — extend tier routing across providers
- [Code-Health-Gated LLM Tier Routing](../agent-design/auto-model-selection.md) — route by file-level code health metrics rather than task type
- [Cognitive Reasoning vs Execution: A Two-Layer Agent Architecture](../agent-design/cognitive-reasoning-execution-separation.md) — role split that complements tier routing
- [Claude Code Sub-Agents](../tools/claude/sub-agents.md) — per-agent model selection mechanic
- [Token-Efficient Tool Design](token-efficient-tool-design.md) — pair tier routing with lean tool surfaces
- [Minimum-Sufficient Control Ladder](../agent-design/minimum-sufficient-control-ladder.md) — orthogonal axis: this page escalates *model tier* by task complexity; the ladder escalates *control mechanism* by named failure mode
