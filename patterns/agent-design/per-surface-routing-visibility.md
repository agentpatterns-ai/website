---
title: "Per-Surface Routing Visibility in Copilot (HydraFusion)"
term: "Per-Surface Routing Visibility"
description: "A runtime router shows a different slice of its decision in each client. HydraFusion runs in three Copilot surfaces, and only the CLI keeps an exportable record."
tags:
  - agent-design
  - cost-performance
  - copilot
  - model-routing
aliases:
  - surface-scoped routing controls
  - routing visibility per client
  - HydraFusion surface availability
last_reviewed: 2026-10-01
maturity: emerging
---

# Per-Surface Routing Visibility in Copilot (HydraFusion)

> The surface you run a routing layer in decides how much of each routing decision survives the request.

Per-surface routing visibility is the share of a routing decision a given client lets you see and keep. HydraFusion makes the gap concrete. On 30 September 2026, "The HydraFusion research preview is now available in Visual Studio Code and the GitHub Copilot app, expanding beyond Copilot CLI" ([GitHub Changelog, 2026-09-30](https://github.blog/changelog/2026-09-30-hydrafusion-in-vs-code-and-the-github-copilot-app)).

Read that availability against three limits before you switch. GitHub withholds a service level agreement and states that HydraFusion "isn't intended for production workloads". It points everyday work at Auto, which "picks one model for each request, and paid plans get a discount on model costs" that HydraFusion forgoes. The routing itself is not fixed, because "The execution patterns and models that HydraFusion uses can change during the research preview" ([GitHub Docs](https://docs.github.com/early-access/copilot/hydrafusion)).

## What each surface exposes

The docs name three clients: "HydraFusion is available in Copilot CLI, Visual Studio Code, and the GitHub Copilot app". Everything in the table comes from that page ([GitHub Docs](https://docs.github.com/early-access/copilot/hydrafusion)).

| Surface | Enablement control | After the response | Exportable record |
|---|---|---|---|
| Copilot CLI | the `--experimental` flag, then the `/model` picker | the conversation "keeps a summary of the execution pattern and its steps, including any warnings"; `/usage` reports AI credits per model | `/collect-debug-logs` archives the execution pattern and the models used for each step |
| Visual Studio Code 1.140 or later, or Insiders | the `chat.copilot.hydraFusion.enabled` setting, then the model picker | "hover over the footer of a completed response" to see which models ran | not documented |
| GitHub Copilot app, latest version | an Experimental setting named HydraFusion, then the model picker | "hover over the response" to see which models ran | not documented |

Read the enablement column as a pointer rather than a procedure, since those controls move with the preview and the docs carry the current steps. The two right-hand columns are the durable part, and `/usage` and `/collect-debug-logs` appear there as Copilot CLI commands with no equivalent named elsewhere. Live visibility is not where the record differs. The docs say "While HydraFusion works, you can follow the progress of each step". In Visual Studio Code, "The chat view shows each step of the execution pattern as HydraFusion works". In Copilot CLI, "the progress display shows which execution pattern is running and each pass in it" ([GitHub Docs](https://docs.github.com/early-access/copilot/hydrafusion)). The CLI is the only one that persists the route and hands it back as a file.

Model choice is a control on none of the three, because "You can't choose which models HydraFusion uses" ([GitHub Docs](https://docs.github.com/early-access/copilot/hydrafusion)). The opt-out is the picker. Select Auto and the routing layer is gone.

## Why it works

A router that picks a different execution pattern per prompt destroys outcome attribution unless something records the route. The route-receipts argument names the gap: "Users see a response, developers see a model name, administrators see usage totals, and the user often does not receive a compact, portable account of the service path", and closing it pays because "A receipt turns a vague complaint into an event the team can investigate" ([Model Routing as a Trust Problem, arXiv:2605.01710v1](https://arxiv.org/abs/2605.01710v1), a position paper rather than an empirical result, whose platform survey predates HydraFusion).

HydraFusion is the case that argument describes. The pattern is chosen per prompt, so two prompts in one session can take different routes, and the mix shifts as new models appear and as GitHub evaluates which perform best ([GitHub Docs](https://docs.github.com/early-access/copilot/hydrafusion)). Grading quality per shape therefore needs a per-request record, and the surface decides whether you have one. The CLI gets closest without arriving. Its record is per-session and pulled on demand, a fragment rather than the aggregatable log the argument asks for.

## When this backfires

- A discarded draft already touched your files. "If HydraFusion discards a draft, changes that the draft already made in your workspace, such as file edits, aren't undone automatically" ([GitHub Docs](https://docs.github.com/early-access/copilot/hydrafusion)). In an editor that lands in a live working tree, from a draft no reviewer saw.
- The work is routine. Auto finishes in one pass and keeps the discount, while HydraFusion's documented fit is "substantial, well-scoped coding tasks, such as fixing a complex bug or making a change across several files" ([GitHub Docs](https://docs.github.com/early-access/copilot/hydrafusion)).
- You switch part-way through a long chat. "The context window shown for HydraFusion is a conservative value based on the smallest limits among the models it uses", so a larger conversation has to be compacted first ([GitHub Docs](https://docs.github.com/early-access/copilot/hydrafusion)).
- The work runs inside subagents. "HydraFusion works separately from subagents and doesn't start them", so the routing never reaches it ([GitHub Docs](https://docs.github.com/early-access/copilot/hydrafusion)).
- You standardize on it across a team. "For Copilot Business and Enterprise, an administrator must enable preview features" ([GitHub Changelog, 2026-09-30](https://github.blog/changelog/2026-09-30-hydrafusion-in-vs-code-and-the-github-copilot-app)), and the picker hides HydraFusion when none of the models it uses are available to you ([GitHub Docs](https://docs.github.com/early-access/copilot/hydrafusion)). The same client then behaves differently per organization.

## Key Takeaways

- Pick the surface by the record you need. For a routing change you intend to grade, run it in the CLI and keep the `/collect-debug-logs` archive per run.
- A hover is not a measurement. In Visual Studio Code and the Copilot app a finished response gives you a hover that names which models ran, and nothing more.
- Budget two cost effects when moving off Auto, not one: the extra model passes, and the lost auto-selection discount.
- Review the working tree before committing after a multi-pass run in an editor. A discarded draft's file edits stay.

## Related

- [Runtime Workflow Selection Across Models (Project HydraFusion)](../multi-agent/runtime-workflow-selection-hydrafusion.md) — the pattern itself, with the published cost and quality figures.
- [Auto Model Selection](auto-model-selection.md) — the per-request model pick that sits beside HydraFusion in the same picker, and the discount it carries.
- [Cost-Driven Model Routing Without Quality Monitoring](../anti-patterns/cost-routing-without-quality-monitoring.md) — what a missing per-shape record costs over months.
- [Router-Imposed Quality Ceiling: Committing Before Output](router-imposed-quality-ceiling.md) — a routing failure that no amount of visibility fixes.
- [Copilot Auto Tiers: Weighting Cost Against Quality](copilot-auto-tier-selection.md) — the other Copilot routing control a developer can reach, and what it does not set.
