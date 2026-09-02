---
title: "Per-Task Agent Routing Across Coding Harnesses"
term: "Per-Task Agent Routing"
description: "Route each coding task to a harness by its measured token cost, latency, and known failure mode instead of standardizing a whole team on one house agent."
tags:
  - agent-design
  - workflows
  - cost-performance
  - tool-agnostic
aliases:
  - per-task coding agent selection
  - routing tasks between coding harnesses
last_reviewed: 2026-08-30
maturity: adopted
---

# Per-Task Agent Routing Across Coding Harnesses

> Where per-task cost is measurable, route each task to the agent harness whose cost and failure profile fit it, not the one ranked higher.

Per-task agent routing sends each piece of work to the harness whose cost and failure profile fits it, rather than naming one house agent. The criterion that survives measurement is budget, not capability. Running two models across three open-source harnesses on a 50-task Terminal-Bench Pro subset, one study found that "paired within-model pass-rate differences remain 0-8 percentage points (95% paired-task bootstrap CIs include zero except for the largest gap)", while "harness choice induces up to a 40x difference in tokens per solved task" ([The Scaffold Effect in Coding Agents](https://arxiv.org/abs/2607.22585v1)). Quality barely moved. The bill did.

## When routing pays

The practice is conditional. Route per task only when all four conditions hold.

- You can attribute token cost and latency per task. Without those numbers you are routing on feel.
- Outcomes are test-verified. A bad routing decision has to become visible, or the table never improves.
- Tasks genuinely differ in shape. A queue of near-identical work has one right answer; find it once.
- Volume repays the deliberation. At a few tasks a day the token bill is too small to cover the attention each decision costs.

Miss any one of these and a single well-understood harness beats a routing table you cannot evaluate.

## The properties worth routing on

| Property | What to check | Why it routes |
|---|---|---|
| Loop length | How long the work would take a competent human | Success falls off with duration, and each agent falls off at its own rate |
| Context volume | Whether the task emits output nobody will read | High-volume work belongs somewhere isolated from the main thread |
| Autonomy tolerance | What one unsupervised wrong action would cost | Approval and sandbox settings are the cheapest lever available |
| Verification cost | Whether a test can decide the result is right | Cheap verification licenses a faster, less supervised route |

Name the property, never the product version. A ranking of two named tools is stale within a month.

## Why it works

The harness owns context management, tool issuance, and the stopping rule, and those three decide token cost, latency, and the shape of the failure. The Scaffold Effect study found that "failure fingerprints replicate across models (REASON for Goose, VERIFY/MAX\_TURNS for OpenHands-SDK, idle-loop/TIME for OpenCode), indicating harness-level biases that are largely model-independent" ([arXiv:2607.22585v1](https://arxiv.org/abs/2607.22585v1)). A fingerprint that survives a model swap belongs to the scaffold, not the weights. A predictable failure is one you can route around.

Task shape supplies the other half. Scoring 170 tasks against the time a human needs, the METR time-horizon study reports that "model success rates are negatively correlated with how much time it takes a human to complete the task. (y=−0.07x+0.66, R²:0.83)". Length is not the whole story: the same paper finds agents "do perform worse on messier tasks than would be predicted from the task's length alone (b=-0.081, R2 = 0.251)" ([Measuring AI Ability to Complete Long Software Tasks](https://arxiv.org/abs/2503.14499v4)). Toby Ord fits the same data with "a constant rate of failing during each minute a human would take to do the task", which gives every agent its own decay curve ([arXiv:2505.05115v1](https://arxiv.org/abs/2505.05115v1)). The routable signal is that curve meeting a known cost profile. No global better-agent term appears in it.

## When this backfires

- You route on capability. The measured within-model gap across harnesses is 0 to 8 points, with confidence intervals crossing zero for all but the largest pair ([arXiv:2607.22585v1](https://arxiv.org/abs/2607.22585v1)). Picking the smarter agent for a task is chasing noise.
- You treat cross-agent agreement as a check. Coding agents repeat one misinterpretation rather than failing randomly: silent semantic failure covers "80% of Llama 4's failing runs and 68% of GPT-5's", and "completion-based and consistency-based monitoring both look healthy exactly when the agent should not be trusted" ([Confident and Wrong](https://arxiv.org/abs/2603.25764v3)). Two agents agreeing is weaker evidence than it feels.
- The task carries long-lived context. Handing work to a second harness mid-flight discards everything the session accumulated.
- You work under audit. A second sandbox and approval model doubles the surface a security review must cover, once per audit.
- Nobody owns the second harness. Fingerprints are learned by exposure, so a team split across two recognizes neither quickly. Depth on one returns more than the gap ever will.

## Example

The first routing axis is configuration inside the harness you already run, not choice of vendor. Claude Code ships that table as documentation, keyed on task shape: `default` for "Reviewing every action yourself, sensitive work", `plan` for "Exploring a codebase before changing it", `auto` for "Long tasks, reducing prompt fatigue", and `dontAsk` for "Locked-down CI and scripts" ([Claude Code permission modes](https://code.claude.com/docs/en/permission-modes)).

Its subagent guidance routes on context volume and loop length the same way. Delegate to a subagent when the task "produces verbose output you don't need in your main context" or when "the work is self-contained and can return a summary". For breadth it says: "For independent investigations, spawn multiple subagents to work simultaneously". Stay in the main conversation when "the task needs frequent back-and-forth or iterative refinement", when "multiple phases share significant context", or when "latency matters" ([Claude Code subagents](https://code.claude.com/docs/en/sub-agents)).

Fanning out is expensive, not free. Agent teams "use approximately 7x more tokens than standard sessions when teammates run in plan mode" ([Claude Code cost management](https://code.claude.com/docs/en/costs)). Microsoft frames the same decision across deployment modes: "local when needing to steer, background or cloud when wanting isolated changes, parallel subagents when needing multiple processes" ([VS Code](https://code.visualstudio.com/blogs/2026/02/05/multi-agent-development)).

## Key Takeaways

- Route on token budget, latency, and known failure mode. Treat any capability-based routing rule you cannot back with your own measurements as noise.
- Exhaust configuration inside your current harness before adopting a second. Permission modes and subagent delegation cover most of the routing surface at no adoption cost.
- Routing compounds only where cost is attributable per task and outcomes are test-verified. Without both, a good route and a lucky one look identical.
- Two harnesses means two instruction conventions, two permission models, and two failure catalogs to keep current. Charge that against the 40x token spread before deciding.

## Related

- [Cross-Vendor Competitive Routing for LLM Selection](cross-vendor-competitive-routing.md) — running rivals on the same task instead of choosing between them
- [Auto Model Selection: Harness-Driven Routing per Task](auto-model-selection.md) — handing the per-request model choice to the harness
- [Per-Model Harness Tuning: Treating the Backing Model as a Harness Variable](per-model-harness-tuning.md) — the same coupling from the other side, tuning one harness per model
- [Benchmark-Driven Tool Selection for Code Generation](../../verification/benchmark-driven-tool-selection.md) — why leaderboard rankings overstate real capability
- [CLI-IDE-GitHub Context Ladder](../../workflows/cli-ide-github-context-ladder.md) — matching the development surface to the phase of work
