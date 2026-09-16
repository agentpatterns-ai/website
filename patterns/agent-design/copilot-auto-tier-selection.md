---
title: "Copilot Auto Tiers: Weighting Cost Against Quality"
term: "Auto Tier Selection"
description: "Copilot's efficiency, balance, and intelligence tiers reweight which model auto prefers per prompt. They set no price, no quality floor, and no org policy."
tags:
  - agent-design
  - cost-performance
  - copilot
aliases:
  - copilot auto tier
  - efficiency balance intelligence tier
  - auto model selection cost quality setting
last_reviewed: 2026-09-15
maturity: emerging
---

# Copilot Auto Tiers: Weighting Cost Against Quality

> Copilot's auto tiers reweight which model auto prefers per prompt. They do not cap spend, pin quality, or reach every surface.

GitHub added three tiers to Copilot auto model selection on 2026-09-14: efficiency, balance, and intelligence ([GitHub Changelog, 2026-09-14](https://github.blog/changelog/2026-09-14-configure-cost-and-quality-in-copilot-auto-model-selection)). Pick one and auto weighs cost, quality, and response time differently on every prompt. That is all of it. The tier reorders preference inside a router that was already choosing for you, and changes nothing about which models are reachable, what a response costs, or who can hold the team to the choice.

## What the tier moves

| Tier | Priority | Typical use |
|---|---|---|
| Efficiency | Cost | Fast, straightforward tasks |
| Balance | Cost, quality, and latency together | Everyday work |
| Intelligence | Quality | Complex tasks |

Source: [GitHub Docs: about Copilot auto model selection](https://docs.github.com/en/copilot/concepts/models/auto-model-selection).

The same docs draw the limit: "The same models remain available in each tier, but tiered routing changes how preferred models are selected for each task." The changelog states the consequence, and it is the line teams will get wrong: a docstring prompt "may use a small, efficient model even when auto is optimizing for intelligence" ([GitHub Changelog, 2026-09-14](https://github.blog/changelog/2026-09-14-configure-cost-and-quality-in-copilot-auto-model-selection)). Intelligence expresses a preference, not a floor under model capability.

Billing does not move with the tier either. Usage "is still charged based on the model auto selects, regardless of tier", alongside the 10% discount paid plans already receive on auto usage ([GitHub Docs](https://docs.github.com/en/copilot/concepts/models/auto-model-selection)). Efficiency buys a cheaper model mix, not a cheaper rate, so nobody can put a figure on the saving until they have measured one.

## Who owns the setting

GitHub addresses the choice to the individual developer: "Choose the tier that reflects how you want auto to weigh cost, quality, and response time for each prompt" ([GitHub Changelog, 2026-09-14](https://github.blog/changelog/2026-09-14-configure-cost-and-quality-in-copilot-auto-model-selection)). The docs then draw the boundary around where that choice exists: "Auto tiers are only available on VS Code, Copilot CLI, and GitHub Copilot app" ([GitHub Docs](https://docs.github.com/en/copilot/concepts/models/auto-model-selection)). Auto itself runs in more places, including Copilot Chat on the GitHub website, JetBrains, Eclipse, Xcode, Visual Studio, and the cloud agent. None of those take a tier.

Administrators govern the pool, not the dial. Auto will not select models excluded by administrator policies, by plan, by data-residency or FedRAMP restrictions, or by the evaluation-model policy ([GitHub Docs](https://docs.github.com/en/copilot/concepts/models/auto-model-selection)). Neither the announcement nor the docs place the tier under an org or repository setting, so "we run efficiency" is a convention any developer can drop without leaving a trace.

## The acceptance signal you need first

GitHub calls the release "the first step" toward "more visibility into the tradeoffs you're making" ([GitHub Changelog, 2026-09-14](https://github.blog/changelog/2026-09-14-configure-cost-and-quality-in-copilot-auto-model-selection)). Until that visibility lands, the signal in hand is per response: Copilot shows which model answered, on hover in Chat, in the terminal in CLI, and beside Auto in the app ([GitHub Docs](https://docs.github.com/en/copilot/concepts/models/auto-model-selection)).

A per-response label is enough to compare two runs of a fixed task set. It is not enough to watch a team drift over a quarter. The independent case for caring comes from work on routing transparency: "Without clear rationale, developers cannot distinguish between intelligent efficiency -- using specialized models for appropriate tasks -- and latent failures caused by budget-driven model selection" ([Explainable Model Routing for Agentic Workflows, arXiv:2604.03527v1](https://arxiv.org/abs/2604.03527v1)). Move the dial down on a workload you already score, or you will not learn which of the two you got.

## Why it works

The tier reweights an objective inside a scorer that already runs. GitHub describes auto with task optimization as two systems: "One system tracks real-time system health and availability, while the other evaluates task complexity" ([GitHub Docs](https://docs.github.com/en/copilot/concepts/models/auto-model-selection)). A tier tells the second system which of cost, quality, and latency to favor and leaves the candidate set untouched, which is why the same model can answer under any tier. The payoff comes from deciding per prompt across a wide capability spread. GitHub states the aim as "reserving higher-cost reasoning models for problems that truly need it, while routing straightforward tasks to faster, lower-cost models".

The decision also fires where it is cheap. GitHub reports that "Routing occurs along natural cache boundaries to avoid additional cache related costs. Switching models mid-session has shown increased cost without ample improvements in quality." That is GitHub's measurement of its own product, published without its numbers, so read it as design rationale rather than a result.

## When this backfires

- Mixed surfaces. A tier set in VS Code does not travel to a cloud-agent session, to Chat on github.com, or to JetBrains, so a team spanning those clients has a standard covering part of its work.
- No enforcement. Nothing records that a developer switched back, so the setting holds only while each one remembers it.
- Reproducibility. Eval-gated CI and compliance attestation need the same model twice, and a preference cannot supply that. Pin instead, as [Auto Model Selection](auto-model-selection.md) sets out, then budget for the pin going stale: "Available models may change over time" ([GitHub Docs](https://docs.github.com/en/copilot/concepts/models/auto-model-selection)).
- Moving the dial with no per-model quality signal. That is the [Cost-Driven Model Routing Without Quality Monitoring](../anti-patterns/cost-routing-without-quality-monitoring.md) failure arriving through a vendor setting rather than a router you built.

## Example

A team on Copilot CLI wants the cheaper end for a backlog of dependency bumps and changelog edits. Score the current tier on twenty representative tasks, recording the model the terminal shows for each response. Switch to efficiency, rerun the same twenty, and compare review rejections and retries rather than spend. Rejections holding means the mix moved and quality did not. Rejections rising means the dial caught a task class that needed the capable end, which individual results will hide: auto evaluates each prompt on its own, so a tier change shows up as a distribution rather than one swapped model.

## Key Takeaways

- Treat the tier as an intent, not a guarantee. Nothing about it is enforceable: the model set is identical across all three, the rate is identical, and no admin scope sets it.
- Reach for balance as the standing default and move to efficiency per workload, once you can score that workload. Efficiency on unscored work is the dial doing damage you will not see.
- Reach for a pin, not intelligence, whenever you need the same model twice. Budget for the pin going stale.
- If your team works across the cloud agent, JetBrains, or Chat on github.com, write the standard per surface. Tiers reach VS Code, Copilot CLI, and the GitHub Copilot app, and nothing else.

## Related

- [Auto Model Selection: Harness-Driven Routing per Task](auto-model-selection.md) — the routing policy the tiers configure, including the pool, the billing history, and when to pin instead.
- [Dispatch-Time Reasoning Level for Delegated Agents](dispatch-time-reasoning-level.md) — the cloud agent's own effort control, on a surface the tiers do not reach.
- [Cost-Driven Model Routing Without Quality Monitoring](../anti-patterns/cost-routing-without-quality-monitoring.md) — what an unmeasured move to the cheap end costs, and the per-tier observability that prevents it.
- [Routing Break-Even: When a Cheaper Model Actually Pays](routing-break-even.md) — the arithmetic for a router you control, useful for sizing whether the mix shift is worth chasing.
- [Routing Decision Framework](../../token-engineering/routing-decision-framework.md) — the tool-agnostic map of routing patterns this vendor control sits inside.
