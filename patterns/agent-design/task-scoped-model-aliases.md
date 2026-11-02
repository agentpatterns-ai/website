---
title: "Task-Scoped Model Aliases: Name the Job, Not the Model"
term: "Task-Scoped Model Alias"
description: "Point each agent task at a named alias that a gateway resolves to a model, so a model swap becomes a configuration edit and not a redeploy. The alias abstracts the model, not the provider-specific options."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
  - model-routing
aliases:
  - model alias per task
  - virtual model ID
  - task-named model indirection
last_reviewed: 2026-10-31
maturity: emerging
---

# Task-Scoped Model Aliases: Name the Job, Not the Model

> A task-scoped model alias moves model choice from code into gateway configuration, so a model swap needs no redeploy.

A task-scoped model alias is a name for a job, such as `vmc/coding-agent`, that the caller passes where a model string would go. A gateway resolves the name to a model and its settings. The team edits that mapping in one place.

Vercel shipped this as Virtual Models on AI Gateway on 28 October 2026 ([Vercel](https://vercel.com/blog/ai-gateway-virtual-models)). This page rests on that one vendor post, so the precedence rules and swap timing below are Vercel's behavior, not a standard.

## Why a model string in code is the wrong place

Vercel counts the release rate: "In the last 90 days, 125 new models from more than 10 labs became available on AI Gateway. That adds up to about 10 a week." A gateway already reduces a switch to one changed line. What remains: "That one line still lives in your code, so switching usually means a redeploy" ([Vercel](https://vercel.com/blog/ai-gateway-virtual-models)).

An alias removes that line from the release path. The gateway changes the mapping behind `vmc/coding-agent`. Every app and agent that calls it picks up the change "within a few minutes, with no code change or deployment needed". Coding harnesses such as Claude Code and Codex select the alias in their model picker or configuration ([Vercel](https://vercel.com/blog/ai-gateway-virtual-models)).

## One alias per task, not per app

Vercel contrasts two tasks. Support ticket triage "can run hundreds of times an hour and needs to be cheap". Legal contract review "may only run a few times a day, but require a high level of reasoning" ([Vercel](https://vercel.com/blog/ai-gateway-virtual-models)).

One alias per app couples both tasks. A model change for one then moves the other and can force a cost or quality trade-off. One alias per task lets each move on its own schedule. The Virtual Models page "shows requests, spend, and success rate for each task".

## Precedence makes the alias a governance control

Settings on the alias win over the same settings in a request: "callers can't override the provider order, fallbacks, or service tier you chose". Vercel's example sets fallbacks for `vmc/storefront-assistant` once, and every app that uses the alias gets the same failover "even if a request specifies different fallbacks".

Data-handling settings follow the same rule. An alias can require Zero Data Retention or providers that do not train on request data. The gateway keeps each configured requirement "even if a request explicitly sets `zeroDataRetention` or `disallowPromptTraining` to false". Tags on the alias replace request tags, and team roles control who can edit an alias ([Vercel](https://vercel.com/blog/ai-gateway-virtual-models)).

With a model string, each caller sets its own options. An alias lets a platform or security team hold them in one place.

## Swap through a candidate alias

Vercel documents a swap procedure worth copying. "Before you switch a virtual model that serves production traffic, point a second one, like `vmc/coding-agent-candidate`, at the new model and run your evals against it. If quality drops after the switch, point the original back at the previous model" ([Vercel](https://vercel.com/blog/ai-gateway-virtual-models)).

The steps:

1. Create a second alias that targets the new model.
2. Run the eval suite against the candidate alias, not the bare model.
3. Edit the production alias to the new model.
4. Keep the previous model name on record. A rollback is the same edit in reverse.

Without evals you trust, the alias makes a bad swap faster, not safer. [Model-Neutral Agent Architecture](model-neutral-agent-architecture.md) covers that condition.

## What the alias does not abstract

The alias hides the model, not every setting. Fallbacks, Zero Data Retention, and tags "stay with the virtual model when you switch models". Provider options do not: "Provider options apply per provider, so an Anthropic-specific setting stops applying when you point the virtual model at an OpenAI model. Review your provider options whenever you switch providers" ([Vercel](https://vercel.com/blog/ai-gateway-virtual-models)).

A cross-provider swap can drop an option you expect to be active. Treat it as a configuration review and run the candidate-alias evals.

## When this backfires

- You run one model and one provider. The alias is a name to maintain for a swap you never make.
- The alias is a single point of change. A bad edit reaches every caller within minutes, so add a review step for edits.
- Alias precedence overrides a caller's intent. A request that sets its own fallbacks loses to the alias, so document which settings the alias owns.

## Key Takeaways

- Put the alias in code and the model in gateway configuration. A swap then ships as a config edit.
- Define one alias per task, so triage and contract review move independently.
- Let the alias own provider order, fallbacks, service tier, and data-retention settings. Callers cannot override them.
- Swap through a candidate alias after evals. Rollback is the same edit in reverse.
- Review provider-specific options on every cross-provider swap. They do not follow the alias.

## Related

- [Model-Neutral Agent Architecture](model-neutral-agent-architecture.md) — the portability bet and the eval condition that make a model swap safe
- [Gateway Model Routing](gateway-model-routing.md) — the gateway as model catalog, the infrastructure layer an alias resolves through
- [Routing Break-Even](routing-break-even.md) — when sending a task to a cheaper model pays, the cost question behind per-task aliases
- [Per-Model Harness Tuning](per-model-harness-tuning.md) — the per-model settings that do not follow an alias across providers
- [Tenant Model Policy](tenant-model-policy.md) — admin-tier control over which models a tenant may call, the neighbor of alias-level governance
- [Client-Keyed Gateway Controls](client-keyed-gateway-controls.md) — why a gateway control binds only where the caller cannot change the attribute it keys on
