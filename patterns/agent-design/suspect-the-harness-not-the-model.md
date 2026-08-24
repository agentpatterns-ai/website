---
title: "Suspect the Harness Before the Model on a Regression"
description: "When a released coding agent's quality shifts after an update at a fixed model, suspect the harness before the model and confirm with a pinned eval slice."
term: "Harness-First Regression Diagnosis"
tags:
  - agent-design
  - tool-agnostic
  - arxiv
  - observability
  - harness-engineering
aliases:
  - don't blame the model
  - harness evolution regression
  - harness-first triage
last_reviewed: 2026-07-23
maturity: emerging
---

# Suspect the Harness Before the Model on a Regression

> When a released coding agent regresses after an update at a fixed model, suspect the harness, not the model.

When a coding agent gets slower, more expensive, or less reliable after an update, the harness is the more likely cause than the model. The harness is the middleware around the model — system prompts, tool execution, context management, and the reasoning loop — and it changes far more often than the model does. A longitudinal study of 35 sequential Qwen Code CLI releases, run against 50 SWE-bench Verified tasks with the backing model held fixed, found no statistically significant improvement in resolve rate across the releases (Spearman ρ=0.208, p=0.231) while token consumption rose more than 70%, from 391K to 668K, a strong upward trend (ρ=0.743, p<0.0001) ([Ben Sghaier et al., 2026](https://arxiv.org/abs/2607.03691v2)).

## The diagnostic

Practitioners routinely blame the model for a post-update regression, but the same study shows the harness is where the change actually lands. Agent harnesses ship 13 to 28 times more often than traditional projects — 10 to 18 releases a week against 0.6 to 0.8 for VS Code or GitHub CLI — so between two agent updates the harness has almost always changed and the model usually has not ([Ben Sghaier et al., 2026](https://arxiv.org/abs/2607.03691)). Base your first suspicion on that base rate.

Three steps turn the suspicion into an answer:

- Confirm the model is fixed. Check the release notes or provider for a model change. Hosted APIs rotate models silently, so if you cannot confirm a fixed model ID, the regression could genuinely be the model.
- Measure against a pinned eval slice. Run a small graded task set — your own held-out eval or a SWE-bench slice — on the old and new versions. Without a fixed slice you cannot separate a real regression from a harder task mix.
- Watch tokens and tool calls, not just resolve rate. Cost often moves before quality does, and failed tasks in the study burned 2.7 times more tokens and 1.8 times more tool calls than successful ones — an efficiency regression the resolve rate hides.

If the slice confirms a drop at a fixed model, pinning the harness version is a rational response rather than an admission of defeat.

## Why it works

Token inflation with flat quality traces to a compounding structure in the harness, not to model change. Later releases shipped roughly 8% larger system prompts, from expanded tool schemas and instructions, and needed about 18% more conversation turns. Because the full conversation history is prepended on every API call, the enlarged per-turn overhead repeats across every turn — turns and total tokens correlate at ρ=0.941 ([Ben Sghaier et al., 2026](https://arxiv.org/abs/2607.03691v2)). A harness edit that adds prompt or tooling weight multiplies through the loop, raising cost without raising the resolve rate.

The attribution is credible because the study isolated the harness. It held a single self-hosted model constant so the provider could not swap it, fixed the compute, timeout, and evaluation environment, saw 87.7% run-to-run agreement on task outcomes, and mapped specific git commits to quality shifts by code inspection. The highest-risk components were the LLM-provider and context-management modules — the same layers that [harness token economics](../../token-engineering/harness-token-economics.md) shows control the token bill.

## When this backfires

The diagnostic mis-fires or goes unactionable under specific conditions:

- Managed or consumer-tier agents. When both the harness and the model are vendor-controlled and opaque, you cannot pin or inspect either, so the question is moot — see [managed vs self-hosted harness](managed-vs-self-hosted-harness.md).
- Genuine model swaps. If the provider rotated the backing model, the regression really is the model, and the diagnostic misleads unless you have confirmed a fixed model ID.
- Disciplined, eval-gated harness teams. Where each release is gated on a held-out eval, version drift is a weak regression signal and pinning forfeits real gains — [observability-driven harness evolution](observability-driven-harness-evolution.md) shows harness evolution lifting pass@1 from 69.7% to 77.0% when edits are verified against outcomes ([Lin et al., 2026](https://arxiv.org/abs/2604.25850v4)).
- Task-mix drift. A resolve-rate drop can come from your own workload shifting toward harder tasks. Without a fixed graded slice you cannot attribute the change to either layer.

## Example

A team's agent starts costing about 40% more per pull request over a month, with no obvious drop in merged-PR rate. The instinct is that the model got worse. Instead they apply the diagnostic. The provider confirms the same model ID across the month, so the model is fixed. They replay a 30-task held-out slice on last month's pinned harness build and this month's: resolve rate is flat at 61%, but median input tokens per task rose from 410K to 690K. The efficiency regression is real and the quality is not moving. They pin the harness at last month's version, file an issue with the token trace, and upgrade only once a later release passes the same slice at equal or lower token cost. This mirrors [fleet harness attribution](fleet-harness-attribution.md), applied across time rather than across models.

## Key Takeaways

- Between two agent updates the harness has almost always changed and the model usually has not — suspect the harness first ([Ben Sghaier et al., 2026](https://arxiv.org/abs/2607.03691)).
- Confirm the model is fixed, measure on a pinned eval slice, and track tokens and tool calls, not just resolve rate.
- The mechanism is structural: larger prompts and more turns compound through prepended history (turns-to-tokens ρ=0.941), inflating cost at flat quality.
- Pinning a harness version is a rational response to a confirmed regression, not a failure to keep up.
- The diagnostic does not apply to managed agents, genuine model swaps, or eval-gated harness teams, where disciplined evolution improves quality.

## Related

- [Fleet Harness Attribution](fleet-harness-attribution.md) — pin the model and swap whole harnesses to attribute an outcome to the harness layer; this page applies the same logic across time
- [Observability-Driven Harness Evolution](observability-driven-harness-evolution.md) — the eval-gated discipline whose absence produces the mis-attributed regressions this page diagnoses
- [Harness Impermanence](harness-impermanence.md) — why harness scaffolding churns so fast, the base rate behind suspecting it first
- [Harness-Controlled Token Economics](../../token-engineering/harness-token-economics.md) — why the orchestration layer, not the model, sets the token bill that inflates here
- [Managed vs Self-Hosted Agent Harness](managed-vs-self-hosted-harness.md) — the boundary condition where you cannot pin or inspect the harness at all
