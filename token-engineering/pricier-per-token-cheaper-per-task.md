---
title: "Pricier-Per-Token Models That Cost Less Per Task"
term: "Inverse Token-Price Effect"
description: "A model priced twice as high per token can finish an agentic task for less total cost, but only under a harness that lets the lead model delegate."
tags:
  - token-engineering
  - cost-performance
  - agent-design
  - tool-agnostic
aliases:
  - inverse token-price effect
  - harness-conditional cost ordering
last_reviewed: 2026-07-28
maturity: emerging
---

# Pricier-Per-Token Models That Cost Less Per Task

> A model priced twice as high per token can finish a task for less total cost — but only when the harness lets it delegate.

What you are pricing is the model and the harness together. Per-token price orders models correctly inside a plain agent loop, and can order them backwards once the harness gives the lead model somewhere cheaper to send work. The bill then follows what the lead declines to do itself.

## The condition that decides it

Cognition ran 3,000 evaluation sessions on the FrontierCode 1.1 benchmark with Fable 5 and Opus 4.8 in the lead seat, each with and without the same cheap sidekick agent. Fable 5 costs twice as much per token as Opus 4.8. The two arms landed on opposite sides ([Cognition, "Making Fable Cheaper Than Opus"](https://cognition.com/blog/making-fable-cheaper-than-opus)):

| Configuration | Score | Cost per run |
|---|---|---|
| Fable 5 (low) + sidekick | 60.7 | $1.86 |
| Opus 4.8 (medium) + sidekick | 54.6 | $2.04 |
| Fable 5 (low) alone | 60.8 | $4.03 |
| Opus 4.8 (medium) alone | 55.4 | $3.06 |

Read the bottom two rows first. Without a sidekick, the 2x per-token premium lands as a 32% higher bill, exactly as the price table predicts. The inversion appears only in the top two rows, where each lead can hand work to a cheaper model. So the finding is not that expensive models are secretly cheap. It is that a delegating harness moves the cost ordering far enough to cross over, and a plain loop does not.

Treat these as vendor-reported figures. Cognition sells Devin and the [Fusion architecture](https://cognition.com/blog/devin-fusion) credited for the result, no public harness reproduces the run, and a separate study measured a 23.8 percentage-point score spread across six harnesses on identical tasks and model backends ([Harness-Bench, arXiv:2605.27922](https://arxiv.org/abs/2605.27922v1)). Carry the method across to your own setup, not the numbers.

## Why it works

Effective cost per task is unit price multiplied by tokens consumed, and on agentic work the lead model's behavior sets the second factor. Cognition parsed every model call across the 3,000 sessions and found cost "dominated by how many turns the lead model takes, how much context it drags along, and above all, what it decides not to do itself". Fable's lead took 11.5 turns per run against Opus's 26.5, wrote 6.1k output tokens against 19.0k, and consumed roughly a third of the input tokens. It spent $0.27 more per run on its sidekick and $0.45 less on itself. In 81% of Fable-led runs the lead never made a single code edit, against 24% for Opus ([Cognition](https://cognition.com/blog/making-fable-cheaper-than-opus)).

Both leads handed off about three times per run, so delegation volume is not the driver. Timing and content are. Fable delegated the implement-test-lint loop early with a constraint-level brief, while Opus explored and implemented solo and delegated the mechanical tail, then pulled the sidekick's files back into its own context twice as often and made four times as many corrective edits at lead prices ([Cognition](https://cognition.com/blog/making-fable-cheaper-than-opus)). That judgment is a model property no price table reports, which is why agentic capability is better reported per model-harness configuration than per model ([Harness-Bench, arXiv:2605.27922](https://arxiv.org/abs/2605.27922)).

## When this backfires

Per-token price stays the better guide under three conditions:

- You have no delegating harness. A single-agent loop gives the lead nowhere cheaper to send work, so judgment cannot convert into fewer expensive tokens. Cognition's own no-sidekick arm is this case, and the price ordering held.
- The tasks have nothing worth handing off. Cognition names short tasks with a handful of lead turns, and serial debugging where the root-cause hunt is one chain of judgments and "the accumulated context is the work" ([Cognition](https://cognition.com/blog/making-fable-cheaper-than-opus)).
- The model sits below the delegation-capability floor. You cannot instruct the effect into existence: "a model coerced into delegating doesn't gain that judgment; it just delegates the wrong things" ([Cognition](https://cognition.com/blog/making-fable-cheaper-than-opus)). Sub-agent delegation is reliable only on the strongest models ([Harness-Controlled Token Economics](harness-token-economics.md)).

The finding also inverts into a bad rule if you read it as "pricier is cheaper". On the independent AA-Briefcase benchmark, cost per task spans more than 800x across models, the leader is also the most expensive per task at over $31, and no low-cost-per-task model reaches frontier quality ([Artificial Analysis](https://artificialanalysis.ai/articles/aa-briefcase)). Price and per-task cost are not reliably related in either direction, which is why the measurement below is the deliverable rather than the ordering.

## Example

The design that settles the question is a four-cell matrix, not a two-model comparison. Vary the model and the harness independently, and price each cell on your own tasks:

```text
                  no sidekick      with sidekick
  cheaper model   cost / score     cost / score
  pricier model   cost / score     cost / score
```

That is the shape Cognition ran, and it is what makes the result interpretable: the no-sidekick column is the control showing the per-token premium behaving normally, so the crossover in the sidekick column is attributable to delegation rather than to the model alone ([Cognition](https://cognition.com/blog/making-fable-cheaper-than-opus)). Running only the sidekick column would have produced the same headline with no way to tell which factor caused it.

## Key Takeaways

- Compare model-harness pairs, not models. Per-token price ordered these two models correctly in a plain loop and backwards once a cheap sidekick was available.
- The mechanism is what the lead model declines to do: 11.5 lead turns against 26.5, and a lead that never touched the code in 81% of runs.
- The figures are vendor-reported by the company selling the harness, and a 23.8 percentage-point cross-harness spread means single-harness numbers transfer poorly. Reuse the method, re-measure the numbers.
- Keep using per-token price when you have no delegating harness, the tasks have nothing to hand off, or the model lacks delegation judgment.

## Related

- [Cheaper-Per-Token Model Upgrades That Cost More Per Task](../patterns/anti-patterns/cheaper-per-token-costlier-per-task.md) — the other direction of the same unit mismatch, driven by token inflation rather than delegation
- [Harness-Controlled Token Economics (The Harness Effect)](harness-token-economics.md) — the third axis: hold the model fixed and swap the orchestration layer
- [Cost-Quality Pareto Measurement for Agent Configurations](cost-quality-pareto-measurement.md) — the standing frame for plotting each configuration on the cost-quality frontier
- [Utility-Model Split: Background Tasks on a Cheaper Model](../patterns/agent-design/utility-model-split.md) — the sidekick architecture this result depends on
- [Cost-Aware Agent Design: Route by Complexity, Not Habit](cost-aware-agent-design.md) — matching model tier to task complexity once the per-task numbers exist
