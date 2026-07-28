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
last_reviewed: 2026-07-28
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

Cascade routing queries cheaper models first and escalates only when confidence is low. [FrugalGPT](https://arxiv.org/abs/2305.05176) showed up to 98% cost reduction this way. No coding tool implements it natively, so the cascade pattern stays a manual or custom build. Approximate it with a two-pass pattern: fast model first, deterministic gate (tests, linter, type checker), then escalate to the capable model on failure. [Within-Task Model Cascade](../loop-engineering/within-task-model-cascade.md) covers the part that decides whether this pays — how to design the gate, and what a shape-only check lets through.

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

## Token economics in GitHub Copilot

On 2026-06-01 GitHub replaced premium requests with GitHub AI Credits: one credit is $0.01, and an interaction bills on the model's input, cached-input, and output tokens at that model's published rates ([GitHub — Copilot is moving to usage-based billing](https://github.blog/news-insights/company-news/github-copilot-is-moving-to-usage-based-billing/), [GitHub Docs — models and pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing)). The multipliers and per-seat request quotas of the [retired request-based model](https://docs.github.com/en/copilot/concepts/billing/copilot-requests) no longer apply ([GitHub Docs — what changed with billing](https://docs.github.com/en/copilot/reference/copilot-billing/request-based-billing-legacy/what-changed-with-billing)).

Copilot rates, USD per million tokens ([GitHub Docs — models and pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing)):

| Model | Input | Cached Input | Output |
|-------|-------|--------------|--------|
| GPT-5 mini | $0.25 | $0.025 | $2.00 |
| Claude Haiku 4.5 | $1.00 | $0.10 | $5.00 |
| Gemini 2.5 Pro | $1.25 | $0.125 | $10.00 |
| Claude Sonnet 5 | $2.00 | $0.20 | $10.00 |
| Claude Opus 5 | $5.00 | $0.50 | $25.00 |
| GPT-5.5 | $5.00 | $0.50 | $30.00 |

Tier still drives cost — Sonnet 5 bills twice Haiku 4.5 per token, Opus 5 five times — but tier is now one term in a product rather than a fixed charge per request. A verbose session on a cheap model can outspend a compact one on an expensive model, so token volume belongs in the routing calculation alongside tier. Cached input bills at a tenth of fresh input on every Claude model listed, which makes a stable prompt prefix worth as much as a tier downgrade. Code completions and next edit suggestions consume no credits and stay unlimited on paid plans ([GitHub Docs — models and pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing)), so this decision applies to chat and agent work only.

Included credits are denominated at the seat price — Copilot Business is $19 per user per month for 1,900 credits per user, promotionally 3,000 through 2026-09-01 — so a paid seat is a floor on spend, not a discount on token rates. Organization credits pool at the billing entity and reset unused at the start of each month ([GitHub Docs — usage-based billing for organizations and enterprises](https://docs.github.com/en/copilot/concepts/billing/usage-based-billing-for-organizations-and-enterprises)). Auto model selection gives a 10% discount on model costs on individual plans and lets you override the selected model at any time ([GitHub Docs — usage-based billing for individuals](https://docs.github.com/en/copilot/concepts/billing/usage-based-billing-for-individuals), [GitHub Changelog: Auto Model Selection](https://github.blog/changelog/2025-11-11-auto-model-selection-for-copilot-in-visual-studio-in-public-preview/)).

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

Single-task pipelines suffer too. A three-tier routing system — whether by task type or by [code health](../patterns/agent-design/auto-model-selection.md) — adds configuration and coordination overhead. For pipelines with one task type and low invocation volume, a single capable model at a fixed tier is simpler and often cheaper once you amortize setup and maintenance cost.

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

## FAQ

**How much cost reduction does big.LITTLE multi-model orchestration deliver in practice?**

A community analysis of Claude Code's Explore subagent pattern found 2 to 2.5x cost reduction at 85 to 95% quality on mixed workloads ([community analysis](https://claudelog.com/mechanics/agent-engineering)). Cognition's Devin Fusion pairs a frontier reasoning core with cheaper sidekick agents, claiming frontier-level performance at roughly 35% lower cost ([Cognition — Devin Fusion](https://cognition.ai/blog/devin-fusion)). Both results come from pairing a capable model with cheaper delegates rather than routing by task type alone.

**When does cascade routing make agents slower or more expensive instead of cheaper?**

Cascade routing only saves money when the validation gate (tests, linters, type checkers) is cheap and deterministic. If validation takes longer than the cost difference between tiers, the cascade adds latency without saving money ([Braintrust — testing agent cost-efficiency](https://braintrust.dev/blog/test-agent-cost-efficiency)). Measure gate cost before committing to escalation-based routing, and treat cost-per-task as an eval metric alongside correctness.

**How is role-based routing different from complexity-based routing?**

Complexity routing decides which model tier handles a task (fast, balanced, powerful); role routing decides which capability handles it, regardless of tier. The OPENDEV paper defines five independently configurable roles — action, thinking, critique, vision, and compact — each with its own fallback chain for graceful degradation ([Bui, 2026 §2.2.5](https://arxiv.org/abs/2603.05344)). The two axes compose: a role can still be assigned a lightweight or powerful model.

## Key Takeaways

- Route tasks to models by complexity — exploration to fast, implementation to balanced, architecture to powerful.
- Assign models by role (action, thinking, critique, vision, compact) with independent fallback chains for graceful degradation.
- Classify agents by initialization token weight: lightweight (<3k), medium (10–15k), heavy (25k+). Prefer lightweight.
- Craft agent descriptions with activation keywords to improve orchestrator delegation accuracy.
- Use display names (`haiku`, `sonnet`, `opus`) rather than pinned model IDs to avoid silent breakage at model retirement.
- Cascade routing (cheap model first, escalate on validation failure) approximates FrugalGPT-style savings without native tooling support.

## Related

- [Reasoning Budget Allocation](../patterns/agent-design/reasoning-budget-allocation.md) — budget reasoning effort the same way you budget tier choice
- [Heuristic-Based Effort Scaling](../patterns/agent-design/heuristic-effort-scaling.md) — heuristics that scale model effort by task signals
- [Cross-Vendor Competitive Routing](../patterns/agent-design/cross-vendor-competitive-routing.md) — extend tier routing across providers
- [Code-Health-Gated LLM Tier Routing](../patterns/agent-design/auto-model-selection.md) — route by file-level code health metrics rather than task type
- [Cognitive Reasoning vs Execution: A Two-Layer Agent Architecture](../patterns/agent-design/cognitive-reasoning-execution-separation.md) — role split that complements tier routing
- [Claude Code Sub-Agents](../tools/claude/sub-agents.md) — per-agent model selection mechanic
- [Token-Efficient Tool Design](token-efficient-tool-design.md) — pair tier routing with lean tool surfaces
- [Copilot vs Claude Billing Semantics](../human/copilot-vs-claude-billing-semantics.md) — AI credits, seat-included credits, per-model token rates, and budget controls compared
- [Minimum-Sufficient Control Ladder](../patterns/agent-design/minimum-sufficient-control-ladder.md) — orthogonal axis: this page escalates *model tier* by task complexity; the ladder escalates *control mechanism* by named failure mode
- [Harness-Controlled Token Economics (The Harness Effect)](harness-token-economics.md) — the complementary lever: the orchestration layer sets token volume and effective price, model routing sets the tier
