---
title: "Cross-Vendor Competitive Routing for LLM Selection"
term: "Cross-Vendor Competitive Routing"
description: "Assign competing vendor agents to the same task in parallel and pick the best result — surfacing capability differences that static routing cannot reveal."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
  - reliability
aliases:
  - cross-vendor routing
  - competitive model routing
last_reviewed: 2026-07-28
maturity: emerging
---

# Cross-Vendor Competitive Routing

> Assign competing vendor agents to the same task, collect independent results, and let a human (or automated gate) select the winner.

## What cross-vendor routing exposes

Single-vendor routing optimizes within a known capability profile. Cross-vendor routing exposes the differences between capability profiles — visible only when you run both agents on the same task and compare.

GitHub Agent HQ (Feb 2026) made this practical: Claude and Codex can both be assigned to the same issue in the same repo. Each agent opens its own branch and PR independently. The team reviews both and picks the best output — surfacing which vendor's strengths better fit the task type. ([Announcement](https://github.blog/news-insights/company-news/pick-your-agent-use-claude-and-codex-on-agent-hq/); [Agentic Workflows changelog](https://github.blog/changelog/2026-02-13-github-agentic-workflows-are-now-in-technical-preview/))

## How it works

```mermaid
graph LR
    I[Issue assigned] --> C[Claude agent<br>branch A]
    I --> X[Codex agent<br>branch B]
    C --> R[Human review]
    X --> R
    R --> M[Merge winner]
    R --> D[Close loser]
```

1. Assign the same issue to two or more agents from different vendors
2. Each agent works independently — no shared state, no coordination
3. Each produces an independent branch and PR
4. A reviewer selects the output that better meets the acceptance criteria
5. Winning branch is merged; losing branch is closed

The selection criteria differ from within-harness model routing. Cost and latency matter less here, because both agents run in parallel. The decision rests on output quality: which agent's reasoning, code structure, or edge-case handling is better for this specific task type.

## When to use

| Situation | Rationale |
|-----------|-----------|
| Architectural decisions | Reasoning models and code-optimized models produce structurally different outputs — both worth evaluating |
| Unfamiliar task type | Competitive routing reveals which vendor's capability profile fits the domain before you commit to a routing strategy |
| High-stakes changes | Independent implementations surface issues earlier than a single agent would |
| Benchmarking new models | Systematic comparison across a task class builds routing intuition |

## Assignment patterns

- Static competitive: always assign both agents to a defined task class, for example all architectural PRs. This is expensive but thorough.
- Spot-check competitive: assign both agents to a sample of tasks, for example every 10th implementation PR. This calibrates confidence in your primary routing strategy without full duplication.
- Triage competitive: assign both agents only when the primary agent's output fails review. Running a second vendor on a failing output brings a different capability profile, rather than retrying the same failure mode.

## Trade-offs

| Approach | Pros | Cons |
|----------|------|------|
| Cross-vendor competitive | Surfaces capability differences; catches failure modes of primary agent | Doubles token consumption; requires human review of two outputs |
| Single-vendor static routing | Predictable cost; no redundant work | Blind spots in primary agent's capability profile go undetected |

## When this backfires

The pattern's hidden cost is coordination, not token consumption.

- Merge conflicts when agents touch the same files. Each agent works on its own branch, but if both vendors edit the same module the losing-branch close is not free. The winning PR may still need rebase or hand-merge work that erases the parallelism dividend.
- Coordination races on issue state. Agents act on each other's side effects. One closes an issue another agent just opened, or files a duplicate PR while the first is still in review. GitHub's own multi-agent orchestration guidance flags both failure modes and recommends [mission-control patterns to serialize touchpoints](../../tools/copilot/agent-mission-control.md) ([GitHub Blog: How to orchestrate agents using mission control](https://github.blog/ai-and-ml/github-copilot/how-to-orchestrate-agents-using-mission-control/)).
- Reviewer fatigue. Doubling agent output doubles the review surface. Cross-vendor routing only pays back when the reviewer can credibly compare both PRs. If the second gets skimmed, the loser's reasoning is wasted spend.

## Example

On GitHub Agent HQ, assign an issue to both Claude and Codex from the issue sidebar:

1. Open the issue on GitHub
2. In the right sidebar under **Assignees**, select both `claude[bot]` and `openai-codex[bot]`
3. Each agent picks up the issue independently, creates its own branch (`claude/fix-123`, `codex/fix-123`), and opens a PR against `main`
4. Review both PRs side by side — compare reasoning steps, code structure, and test coverage
5. Merge the stronger PR; close the other with a note explaining the decision

This is the simplest form of spot-check competitive routing: one issue, two independent implementations, one reviewer pick. The branch names and bot handles follow GitHub Agent HQ defaults as of Feb 2026.

## Relationship to within-harness routing

This pattern operates at the platform level, choosing which vendor agent handles the issue. [Cost-Aware Agent Design](../../token-engineering/cost-aware-agent-design.md) operates at the harness level, choosing which model tier handles which sub-task within a single agent's pipeline. The two patterns compose: use competitive routing to pick the right vendor, then within-harness routing to control cost inside that vendor's pipeline.

## Key Takeaways

- Competitive routing surfaces vendor capability differences that benchmarks cannot reveal for your specific task class
- Platform-level assignment (GitHub Agent HQ) makes parallel runs practical without custom harness integration
- Selection criteria are qualitative (output quality), not quantitative (cost/latency) — each agent runs in parallel, so latency does not compound
- Spot-check competitive routing calibrates static routing strategy without full duplication cost

## Related

- [Cost-Aware Agent Design](../../token-engineering/cost-aware-agent-design.md)
- [Copilot vs Claude Billing Semantics](../../human/copilot-vs-claude-billing-semantics.md) — GitHub AI credits vs Anthropic token rates, compared per model
- [Code-Health-Gated LLM Tier Routing](auto-model-selection.md) — pre-generation routing via file-level code health metrics
- [Evaluator-Optimizer Pattern](evaluator-optimizer.md) — selecting between candidate outputs
- [Event-Driven Agent Routing](event-driven-agent-routing.md)
- [Per-Task Agent Routing Across Coding Harnesses](per-task-agent-routing.md) — choosing one route per task instead of running rivals in parallel
- [Agent Composition Patterns](agent-composition-patterns.md) — fan-out as a composition primitive
- [Delegation Decision](delegation-decision.md)
- [Specialized Agent Roles](specialized-agent-roles.md)
