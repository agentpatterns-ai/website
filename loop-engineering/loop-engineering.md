---
title: "Stacking Outer Loops Around the Agent"
term: "Loop Engineering"
description: "Loop engineering names the discipline of stacking outer loops — verification, scheduling, hill-climbing — around the agent loop so the human stops being the throughput ceiling."
tags:
  - loop-engineering
  - workflows
  - long-form
  - tool-agnostic
aliases:
  - Loop Engineering
  - loopcraft
  - stacking loops
  - designing loops that prompt agents
last_reviewed: 2026-08-27
maturity: emerging
---

# Stacking Outer Loops Around the Agent

> Loop engineering stacks outer loops — verification, scheduling, hill-climbing — around the inner agent loop so the human stops being the throughput ceiling.

## The discipline

Loop engineering is the practice of replacing the human as the agent's prompter with a system of stacked outer loops. The inner-most loop is the familiar [agent loop](../patterns/agent-design/anthropic-effective-agents-framework.md) — a model calling tools until a task is complete. The outer loops add automated grading, automated initiation, and automated harness improvement. Each layer removes one place where a human used to sit between the agent and its next action.

Three primary-source descriptions of the discipline converged inside an eight-day window in June 2026. Addy Osmani's ["Loop Engineering"](https://addyo.substack.com/p/loop-engineering) names the term on 2026-06-08, framing it as "replacing yourself as the person who prompts the agent." swyx's ["Loopcraft: The Art of Stacking Loops"](https://www.latent.space/p/ainews-loopcraft-the-art-of-stacking) follows on 2026-06-12, framing it as a stacked-loops design space where reliability comes from going *down* a loop and leverage from going *up*. LangChain's Sydney Runkle publishes ["The Art of Loop Engineering"](https://blog.langchain.com/the-art-of-loop-engineering/) on 2026-06-16, structuring the stack as four named loops. Three independent practitioners arriving at the same term inside one week marks loop engineering as a recognized discipline, not one author's coinage.

Lulla et al. put a number on the uptake. Their August 2026 survey *Loop Engineering: Building Blocks, Adoption, and Impact* dates the term to that same June — "In June 2026, practitioners began to describe a further level called loop engineering" — and mines 36,710 repositories for it, confirming autonomous agent loops in 217 of 256 matched repositories ([arXiv:2608.21884v2](https://arxiv.org/abs/2608.21884v2)). Its framing matches the one here: prompting, then context engineering, then harness configuration, then loop engineering. The June essays describe the practice; the survey measures how far it has spread.

## When loop engineering pays off

Loop engineering carries real setup cost — a verifier sub-agent, a scheduler, a state file, project-knowledge skills, and at least one connector to an issue tracker or notification channel. The stack pays back only when all four conditions from the [Agent Loop Go/No-Go gate](agent-loop-go-no-go-gate.md) hold simultaneously: task cadence at least weekly, objective verification that grades "done" without an LLM's opinion, absorbable token budget for retries, and real tooling that lets the verifier see ground truth. Fail any one and a single prompt-driven session is cheaper than a four-loop stack forever.

Go/No-Go decides whether to loop at all; loop engineering decides which outer layers to stack once you commit. Read the gate first.

## The four-loop stack

LangChain's framing gives the cleanest decomposition. Each layer is named below with the existing site pages that go deep on its mechanics.

| Loop | What it does | Where to go deep |
|---|---|---|
| 1. Agent loop | Model calls tools until a task is complete | [Anthropic's Effective Agents framework](../patterns/agent-design/anthropic-effective-agents-framework.md), [ReAct pattern](../patterns/agent-design/react-pattern.md) |
| 2. Verification loop | A grader scores output against a rubric; failing output is fed back with feedback | [Evaluator-Optimizer](../patterns/agent-design/evaluator-optimizer.md), [LLM-as-Judge Evaluation](../workflows/llm-as-judge-evaluation.md) |
| 3. Event-driven loop | An event — schedule, webhook, repo push — triggers the agent | [Event-Driven Agent Routing](../patterns/agent-design/event-driven-agent-routing.md), [Goal-Driven Autonomous Loop](goal-driven-autonomous-loop.md) |
| 4. Hill-climbing loop | An analysis agent reads production traces and rewrites the harness | [Harness Hill-Climbing](../patterns/agent-design/harness-hill-climbing.md), [Agentic Flywheel](../patterns/agent-design/agentic-flywheel.md) |

LangChain's article ([Runkle, 2026](https://blog.langchain.com/the-art-of-loop-engineering/)) calls Loop 4 "arguably most important": "the return arrow doesn't just loop back to the top — it reaches inside and updates the agent loop directly. Each cycle of the outer loop makes the inner loops more effective."

Osmani's parallel framing lists five building blocks rather than loops — automations, worktrees, skills, plugins and connectors, sub-agents — plus disk-resident memory as the sixth element that sits outside the five ([Osmani, 2026](https://addyo.substack.com/p/loop-engineering)). The block list and the loop list overlap heavily: automations supply Loop 3's trigger; sub-agents supply Loop 2's verifier; memory survives Loop 1's context resets. The two framings agree on the underlying mechanism even when their carving differs.

Osmani's August follow-up reports the loops arriving as first-class tool primitives rather than hand-rolled bash: `/goal` in Claude Code drives a bounded task to a measurable finish line while an evaluator model checks each attempted stop, and `/loop` reruns work on a timer. He also relays the Claude Code team's taxonomy of four loop types, classified by how each loop is triggered and how it stops, which is a different carving from the layer stack above ([Osmani, 2026-08-14](https://addyo.substack.com/p/practical-loop-engineering)).

## Why it works

The causal mechanism is bottleneck migration. The inner agent loop produces output faster than a human can prompt the next task, so the human becomes the throughput ceiling. Each outer loop removes one place the human used to sit. Loop 2 replaces human grading with an automated rubric. Loop 3 replaces human initiation with an event trigger. Loop 4 replaces human harness-tweaking with trace-driven analysis.

Karpathy states the underlying claim directly in his [autoresearch talk](https://www.latent.space/p/ainews-loopcraft-the-art-of-stacking): "the goal is to maximise your token throughput and not be in the loop." Boris Cherny, head of Claude Code at Anthropic, [reports the same shift](https://www.latent.space/p/ainews-loopcraft-the-art-of-stacking): "I don't prompt Claude anymore. I write loops, the loops do the work."

The empirical anchor for the broader "environment dominates the model" claim comes from LangChain's [harness engineering work](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/): Terminal Bench 2.0 moved from 52.8% to 66.5% through harness changes alone, no model swap. Loop engineering extends that result outward — if the environment around a single agent run dominates the model, then the environment around many agent runs dominates the run.

## When this backfires

The four conditions from the [Go/No-Go gate](agent-loop-go-no-go-gate.md) name the upstream cost gate. Past it, four failure modes specific to loop engineering remain.

Low-cadence tasks: the four-loop stack carries fixed setup cost — a verifier, a scheduler, a state schema, the skill files that hold project conventions. For tasks that run weekly or less, the setup never amortizes. A single prompt-driven session ships faster and cheaper.

Subjective verification: Loop 2 demands a rubric that grades output without a human. Tasks where "done" is taste — design review, writing quality, naming conventions — cannot be wrapped in a verification loop. The loop stops on vibes, the maker grades its own homework, and quality drifts down across iterations. The [Evaluator-Optimizer pattern](../patterns/agent-design/evaluator-optimizer.md) covers when an LLM judge can stand in; outside that envelope, Loop 2 silently fails.

Reviewer-bottlenecked teams: Osmani is explicit on this in ["Loop Engineering"](https://addyo.substack.com/p/loop-engineering) — "the worktrees take away the mechanical collision but YOU are still the ceiling, your review bandwidth decides how many you can actually run, not the tool." When the human reviewer is already saturated, a loop multiplies output by N but effective throughput is capped at reviewer capacity. The queue gets longer, not the team faster. The parent throughput argument runs through Osmani's earlier [Orchestration Tax](https://addyosmani.com/blog/orchestration-tax/) piece; the [WIP=1 and Little's Law page](../patterns/agent-design/wip-1-littles-law-agent-throughput.md) makes the consequence quantitative.

Drifting harness assumptions: Loop 4 optimizes the harness against historical traces. If the underlying task distribution shifts — new framework, new team, new feature — the optimized harness encodes stale assumptions and silently degrades. Bui et al. (2025) measured the symptom across 567 Claude Code PRs: 83.8% merged but only 54.9% merged without modification ([arxiv:2509.14745](https://arxiv.org/abs/2509.14745v3)). About 45% of "automated" output still consumed reviewer time. A hill-climbing loop trained on yesterday's traces will not catch tomorrow's distribution shift.

## Loop engineering vs context engineering

Loop engineering does not name per-turn loop mechanics; that is a separate discipline. The choice of how much context survives between iterations of the inner agent loop (accumulated, compressed, or fresh) is covered at the [Loop Strategy Spectrum](loop-strategy-spectrum.md). Within-session compaction is covered at [Context Compression Strategies](../context-engineering/context-compression-strategies.md). Loop engineering operates one layer up: it composes the outer loops around whichever inner-loop strategy you chose. The two disciplines stack; they do not replace one another. A Towards Data Science experiment makes the layering concrete by running loop engineering with "no LLM inside the loop" — the outer loops carry the work even when the inner step is not a model call, illustrating loop engineering as a layer beyond context engineering ([Towards Data Science, 2026](https://towardsdatascience.com/context-engineering-isnt-enough-a-loop-engineering-experiment-with-no-llm-inside-the-loop/)).

The same disambiguation applies to harness engineering. [Harness engineering](../patterns/agent-design/harness-engineering.md) is the discipline of designing the environment a single agent runs inside — the legibility, the constraints, the mechanical enforcement. Loop engineering is the discipline of stacking control loops around many agent runs. Osmani positions loop engineering as "one floor above the harness" in his ["Loop Engineering" piece](https://addyo.substack.com/p/loop-engineering); LangChain's hill-climbing loop is what closes the feedback between the two layers.

## Key Takeaways

- Loop engineering names the discipline of stacking outer loops — verification, scheduling, hill-climbing — around the inner agent loop.
- The published framings (LangChain four-loop stack, Osmani five building blocks, swyx loopcraft) agree the discipline replaces the human as the agent's prompter, not the agent's per-turn context strategy.
- The stack pays back only when the [Go/No-Go gate's](agent-loop-go-no-go-gate.md) four conditions hold; below that bar a single prompt session is cheaper.
- Subjective verification, reviewer bottlenecks, and harness drift each break one specific loop in the stack — diagnose by which layer's invariants fail.

## Related

- [Agent Loop Go/No-Go: When Looping Earns Its Cost](agent-loop-go-no-go-gate.md)
- [Loop Strategy Spectrum: Accumulated vs Fresh Context](loop-strategy-spectrum.md)
- [Harness Engineering](../patterns/agent-design/harness-engineering.md)
- [Evaluator-Optimizer Pattern](../patterns/agent-design/evaluator-optimizer.md)
- [Harness Hill-Climbing](../patterns/agent-design/harness-hill-climbing.md)
- [The Three Loops of Agentic Coding](three-loops-agentic-coding.md)
