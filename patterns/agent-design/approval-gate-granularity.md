---
title: "Approval Gate Granularity in Agent Pipelines"
term: "Approval Gate Granularity"
description: "Bundling agent approvals helps only on the axis that removes decisions; batching the approval queue moves wait time and leaves reviewer load unchanged."
tags:
  - agent-design
  - human-factors
  - tool-agnostic
aliases:
  - batching agent approvals
  - approval bundling axis
last_reviewed: 2026-08-30
maturity: emerging
status: current
---

# Approval Gate Granularity in Agent Pipelines

> Bundling agent approvals cuts reviewer load only when the bundle removes decisions; batching the queue moves wait time and leaves the count unchanged.

An approval gate spends two quantities that teams routinely conflate. Wait time is how long the agent idles before a human answers. Decision count is how many judgments the reviewer makes per hour. Only the second one saturates, so a granularity change that leaves it alone will not move the bottleneck. Anthropic reports that Claude Code users approve 93% of permission prompts ([auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)), which puts a real decision behind roughly 7 prompts in 100. Re-timing when those 100 prompts arrive does not change that ratio.

## Where the bundle can sit

| Axis | What gets bundled | Decisions removed |
|---|---|---|
| Queue | Pending requests pile up and are reviewed together | None |
| Task | The gate moves to a task boundary such as one pull request | The per-action gates inside the task |
| Class | A rule pre-authorizes every future action of one kind | Every later action the rule covers |

Queue bundling is the one teams reach for and the one with a documented failure. In a text-to-SQL deployment that gated every non-SELECT write, analysts were "waiting twenty, sometimes forty minutes for a human to glance at a query and click approve". Once the median wait passed fifteen minutes, "the reviewers started approving the requests in batches, skimming five or six queries at once, dropping the review quality" ([Towards Data Science](https://towardsdatascience.com/human-in-the-loop-without-killing-throughput/)). Nobody designed that batch. Queue pressure produced it, and it spent scrutiny without buying throughput.

Class bundling is what the same team shipped instead ([Towards Data Science](https://towardsdatascience.com/human-in-the-loop-without-killing-throughput/)). A risk score combined blast radius (an actual row count capped at 50,000, rather than a query-planner estimate), a sensitivity allowlist covering billing and auth tables, semantic distance from approved queries, and disagreement across resamples. Low scores execute immediately. The human sees the residue, which is where the reviewers had proved useful: "requests where the agent's interpretation of intent was plausible but wrong".

Task bundling sits between the two and ships as a mode rather than a queue. Claude Code's `acceptEdits` "automatically accepts file edits and common filesystem commands such as `mkdir`, `touch`, `mv`, and `cp` for paths in the working directory or `additionalDirectories`" ([Configure permissions](https://code.claude.com/docs/en/permissions)). The mode, not the task, is what bounds it: the gate stays off every edit until someone changes the mode back.

## Why it works

Reviewer output is bounded by decisions attended to, not by elapsed wait, so only a move that deletes decisions relieves the reviewer. Anthropic names the causal chain: "Constantly clicking 'approve' slows down development cycles and can lead to 'approval fatigue', where users might not pay close attention to what they're approving, and in turn making development less safe" ([Claude Code sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing)). Acting on the count is measurable. Sandboxing "safely reduces permission prompts by 84%" in Anthropic's internal usage, because a boundary answers a whole class of actions once. Shortening the approval interval answers nothing in advance and removes zero prompts.

Gaube et al. reach the same result from the oversight side. Badly designed oversight "can create the illusion of human control, when oversight structures give humans the responsibility, but not the agency, to prevent harm", and humans are "poorly suited" to "prolonged periods of passive monitoring" ([arXiv:2605.16278v1](https://arxiv.org/abs/2605.16278v1)). A queue bundle hands the reviewer the same stream in lumps. It does not hand back agency over any individual item.

## When this backfires

- Heterogeneous bundles. Evaluation cost spreads across members only when they share a rule and a fix shape, the condition [batched suggestion application](../../code-review/batched-suggestion-application.md) depends on. Mix an irreversible action into forty reversible ones and it collects the bundle's average scrutiny.
- Class signals that do not track risk. Anthropic's two-stage classifier reaches a 0.4% false-positive rate on real traffic, and on genuinely overeager actions it still shows a 17% false-negative rate ([auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)). Roughly one dangerous action in six passes, and an under-escalation stays invisible until an audit.
- Scopes wider than the instance reviewed. Claude Code saves a Bash approval "Permanently per repository and command" ([Configure permissions](https://code.claude.com/docs/en/permissions)). A command approved once on a benign invocation is approved for every later one.
- Volume below saturation. Where the reviewer clears the queue as fast as it arrives, bundling adds latency to every waiting item and buys nothing back. Measure arrival rate against service rate before assuming the gate is the constraint.
- A long but stable queue. That is a batch-size and variability problem, not the state [verification capacity saturation](../../verification/verification-capacity-saturation.md) describes. Letting more items pile up raises wait-time variance while removing no decisions.

The strongest counter-position is to skip granularity entirely. If 93 of every 100 prompts get a reflex, most of them should not exist, and an engineering hour buys more safety spent on reversibility and audit trails than on bundle size.

## Example

Claude Code's approval scopes are class bundling with the class width written down per tool type. Selecting "Yes, and don't ask again" saves a different breadth of pre-authorization depending on what was approved ([Configure permissions](https://code.claude.com/docs/en/permissions)).

| Tool type | What the saved rule covers |
|---|---|
| Bash commands | Permanently per repository and command |
| File modification | Until session end |
| Web fetch | Permanently per repository and domain |

Only the file-modification row expires. Edits are frequent and the class is broad, so that approval is capped at the session rather than written to a settings file. A reviewer who approves a Bash command sets durable policy; a reviewer who approves an edit sets policy that ends with the session. Read the width before deciding whether one click is enough scrutiny for it.

## Key Takeaways

- Measure decisions per hour before wait time. A gate that never saturates the reviewer has no granularity problem to solve.
- Queue bundling is a symptom of an overloaded gate rather than a treatment for one. Reviewers arrive at it on their own and lose scrutiny getting there.
- Write down the escape rate of every class rule before you ship it. If nobody can name the number, the rule has not been evaluated, only assumed.
- Audit your own gate by asking which axis each existing bundle sits on. A team that cannot answer is usually running queue bundling by accident.
- Check how long an approval lasts, not only what it approves. A rule saved permanently per repository outlives the instance the reviewer actually looked at.

## Related

- [Human-in-the-Loop Placement: Where and How to Supervise](../../workflows/human-in-the-loop.md) — decides which actions get a gate at all; this page decides how many decisions each gate carries
- [Human-in-the-Loop Checkpoints as Loop Control](../../loop-engineering/human-in-the-loop-checkpoints.md) — the loop-internal placement and the four decision verbs a checkpoint exposes
- [Classifier-Gated Auto-Permission for Cloud-IDE Coding Agents](classifier-gated-auto-permission.md) — the mechanism that implements class bundling when a static rule cannot express the class
- [Tool Confirmation Carousel: Batched UI for Per-Call Approvals](tool-confirmation-carousel.md) — the last-mile surface for the residual approvals no bundle absorbs
- [Verification Capacity Saturation: Three Levers, One Default](../../verification/verification-capacity-saturation.md) — what remains once the gate is already past its service rate
- [Fleet-Level Irreversibility Budgets for Agent Effects](fleet-irreversibility-budget.md) — the aggregate a per-action gate cannot see, whatever granularity you set it at
