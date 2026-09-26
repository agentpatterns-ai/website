---
title: "Outcome Pricing as a Scope Signal"
term: "Outcome Pricing as a Scope Signal"
description: "A per-outcome price reports a vendor's bounded cost variance only when the buyer observes the outcome, which makes the billing unit evidence about how narrow the agent behind it is."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
aliases:
  - outcome-based pricing for coding agents
  - pay per merged changeset
  - billing unit as scope evidence
last_reviewed: 2026-09-17
maturity: emerging
---

# Outcome Pricing as a Scope Signal

> A per-outcome price reports bounded cost variance only when the buyer, not the vendor, records the outcome.

Check who records the outcome before you read anything into an outcome-based price. Where the buyer's own system records it, the vendor has taken delivery risk it can only carry if cost per task is bounded, and the billing unit becomes evidence about the agent. Where the vendor's system infers it, the price reports the contract instead.

Sourcegraph bills Agentic Batch Changes on merges: "You pay per changeset merged into your codebase, not per token, seat, or attempt. If it opens a pull request and your team decides not to merge it, you don't pay for it" ([Sourcegraph, Agentic Batch Changes](https://sourcegraph.com/agentic-batch-changes)). The same page says you approve every changeset before it merges, so the billing event is a git fact on your host.

## The verification test

An inferred outcome fails that test. Analyzing Zendesk, HubSpot and Salesforce, Utpal Dholakia describes a vendor that "counts an issue as resolved once there is no further communication for 72 consecutive hours, after making an automated AI-based evaluation", and observes that "neither silence nor automated checks can distinguish a satisfied shopper from a quiet defector" ([The Pricing Conundrum, 2026-06-09](https://thepricingconundrum.substack.com/p/outcome-based-pricing-in-practice)). He concludes that what counts as a resolved ticket "is often subject to different conflicting interpretations, can favor the vendor, and be difficult to verify".

Both arrangements ship as outcome pricing. A vendor bounds its exposure either by narrowing the work or by loosening the definition, and the tell is who would win a dispute about whether the outcome happened. Only the first says anything about the harness.

## Why it works

Cost per outcome is cost per attempt divided by the success rate, so a vendor pricing the outcome carries the variance in both terms. SWE-Bench+ measures that gap across its 548 instances. SWE-Agent+GPT-4 cost $3.59 per instance on average against $655.0 per issue fixed, at a 0.55% resolution rate. AutoCodeRover+GPT-4o cost $0.46 per instance against $12.61 per issue fixed, at 3.83% (Table 4, [Aleithan et al., arXiv:2410.06992v2](https://arxiv.org/abs/2410.06992v2)). Those are 2024-era models and scaffolds on a deliberately hardened benchmark, so read the ratio as arithmetic rather than as current agent economics. The numerator moves too, with the task held fixed. Over ten repetitions of a single task on a single codebase, "the most expensive trial in a group typically costs around 2.5× the cheapest, and roughly 72% of groups have a ratio above 2×" on input tokens ([arXiv:2605.20049v1](https://arxiv.org/abs/2605.20049v1)).

Narrowing the harness attacks both terms. Sourcegraph describes "a special-purpose agent, scoped deliberately in its harness, its system prompt, its permissions, and its tools, to solve one concrete problem", one that "does not immediately reach for a coding agent when a script will do, and on a migration, that's most of the time" ([Sourcegraph, Dan Adler, 2026-09-16](https://sourcegraph.com/blog/agentic-batch-changes-pricing)). Fewer reachable trajectories cut the cost of an attempt, and a task the harness was built for raises the share of attempts that finish. The post gives no figure for the saving, so the direction is sourced and the magnitude is not.

The arithmetic transfers to an agent you are not buying. Divide spend by completed units rather than runs, and both levers show up.

## When this backfires

- The outcome is inferred. Where the vendor's own system decides whether the outcome occurred, the unit price bounds nothing and the definition can move toward the vendor ([Dholakia](https://thepricingconundrum.substack.com/p/outcome-based-pricing-in-practice)).
- The outcome is observable but is not the value. A merged changeset is a git event. It can be reverted the next week, or waved through by a reviewer who did not read it.
- The per-outcome rate is not published. Sourcegraph's [pricing page](https://sourcegraph.com/pricing) gives its enterprise plan as "Starting at $16K" minimum annual contract with a "Contact sales" route, and no rate per merged changeset, so the number carrying the risk premium is negotiated.
- You cannot decline the awkward work. A vendor can refuse a contract it expects to lose money on. An internal platform team owns the repository nobody wants, so copying the pricing shape inward transfers no risk.
- Narrowing has a running cost. A special-purpose harness cannot absorb adjacent work, so each new job adds a harness, a permission set, and an eval suite to maintain.
- Buyer demand is narrower than the trend copy suggests. Futurum Research reports that in its 1H 2026 survey "43% of buyers prefer consumption-based models, while 27% favor outcome-based structures" ([Futurum Group, 2026-05-12](https://futurumgroup.com/press-release/are-outcome-based-and-hybrid-ai-pricing-models-rewriting-the-vendor-playbook/)).

## Key Takeaways

- Apply the verification test first: a priced outcome is informative when the buyer's system records it and the buyer can audit the count.
- A merged changeset passes that test; a 72-hour inactivity window does not, and both ship under the same label.
- Cost per outcome is cost per attempt divided by success rate, which is why a vendor underwriting outcomes has to bound both.
- Ask a vendor which of the two levers it pulled, then ask the same question of the internal agent whose spend you already own.
- A published outcome unit is not a published price; the risk premium sits in a rate you have to negotiate for.

## Related

- [The Harness as Product: What Listed-Rate Pricing Buys](harness-as-product.md) — what the money buys when a product prices at the model's listed API rate.
- [Minimum-Sufficient Execution: Estimate Scope Before Spending Budget](minimum-sufficient-execution.md) — the per-task version of bounding cost before spending it.
- [Cheaper-Per-Token Model Upgrades That Cost More Per Task](../anti-patterns/cheaper-per-token-costlier-per-task.md) — the same denominator error made on model choice.
- [Sizing an Agent Migration Fan-Out by Diff Uniformity](../../workflows/agent-fanout-migration-diff-uniformity.md) — how wide to fan the migration this pricing model bills for.
- [Human-Equivalent Hours for Autonomous Coding Agent Productivity](../../human/human-equivalent-hours-agent-productivity.md) — another way to put agent spend in a denominator a budget owner recognizes.
