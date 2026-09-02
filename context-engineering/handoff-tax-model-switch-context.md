---
title: "The Handoff Tax: What a Receiving Model Should Inherit"
term: "Handoff Tax"
description: "A mid-task model switch costs quality and money, and the trajectory the receiver should inherit reverses with direction: drop the cheap model's on escalation, keep the strong model's on downshift."
tags:
  - context-engineering
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - handoff tax
  - non-native trajectory continuation
  - mid-task model switch interface
last_reviewed: 2026-08-26
maturity: emerging
---

# The Handoff Tax: What a Receiving Model Should Inherit

> A mid-task model switch charges a handoff tax, and what the receiving model should inherit reverses with the direction of the switch.

Two conditions decide this, in order. A mid-task escalation only pays on hard tasks: "For Claude, all escalation interfaces are unfavorable on easy and medium tasks", and in aggregate "every Claude escalation interface costs more than HC-only". Downshifting is a different story — the authors report it "offers a favorable intermediate cost-quality point" ([Ganz et al., arXiv:2608.24358v1](https://arxiv.org/abs/2608.24358v1)). Once you are switching, the interface that helps depends on direction. Escalating to a stronger model goes better when you drop the cheap model's trajectory. Downshifting goes better when you keep the strong model's.

## What crosses the boundary

The study compared four interfaces on a Claude pair (Haiku 4.5 to Opus 4.7) and a GPT pair, across 500 SWE-bench Verified tasks and 58,000 agent runs ([arXiv:2608.24358v1](https://arxiv.org/abs/2608.24358v1)):

| Interface | What the receiver gets |
|---|---|
| Raw | The sender's full trajectory, verbatim |
| Compact-pre | A summary the sender writes before handing over |
| Compact-suf | A summary the receiver writes from the full trajectory |
| Traj-drop | Nothing but the edited files on disk |

Traj-drop sounds worse than it is. "All strategies preserve [the working tree (edited files on disk)]; they differ only in the trajectory information passed to the suffix model" ([arXiv:2608.24358v1](https://arxiv.org/abs/2608.24358v1)). Dropping the trajectory does not throw away the work. It throws away the reasoning about the work.

## The direction decides the interface

Quality recovery (QRec) is the fraction of the strong model's quality advantage a handoff recovers, so 100% would mean the switch matched running the strong model throughout ([arXiv:2608.24358v1](https://arxiv.org/abs/2608.24358v1)).

| Interface | Escalation, Claude | Escalation, GPT | Downshift, Claude | Downshift, GPT |
|---|---|---|---|---|
| Raw | 47% | 36% | 50% | 79% |
| Compact-pre | 60% | 40% | 56% | 72% |
| Traj-drop | 64% | 84% | 28% | 53% |

Traj-drop is the best escalation interface in both families and the worst downshift interface. Raw transfer, which hands over the session unchanged, recovers less than half the quality gap on escalation and costs the most: "For Claude, Raw costs more than twice as much as starting with HC ($1.61 vs. $0.72)". The authors put the consequence plainly — "even after paying for the LC prefix, abandoning the attempt and restarting with HC is cheaper and more accurate than Raw continuation" ([arXiv:2608.24358v1](https://arxiv.org/abs/2608.24358v1)).

## Why it works

The receiver's capability decides whether inherited reasoning is a burden or a prerequisite. A strong model handed a weak model's transcript inherits context that "may contain reasoning the receiver would not have generated and mistakes it would not have made", and carrying that text inflates every subsequent call: raw escalation, relative to compact-pre, "raises the average post-handoff cost per HC step by 2.2x for Claude and 1.6x for GPT" ([arXiv:2608.24358v1](https://arxiv.org/abs/2608.24358v1)). A weak model handed only the repository state cannot reconstruct the strong model's reasoning and rebuilds it by trial, taking 1.6x the post-handoff steps for Claude and 2.0x for GPT. The authors state the asymmetry directly: "Full LC context inflates HC calls, whereas missing HC context forces LC rework."

Independent work supports the mechanism rather than the specific rule. Cross-model reuse of stored trajectories degrades performance "because stored memories often entangle task-relevant knowledge with model-specific biases" ([Chang et al., arXiv:2603.23234v2](https://arxiv.org/abs/2603.23234v2)). Transferring a trajectory helps only when the receiver can separate the knowledge from the bias, and a strong receiver is better placed to do that.

## When this backfires

- The task is easy or medium and you are escalating. Every Claude escalation interface cost more than the strong model alone on those strata. Only the hard subset showed reduced-context escalation recovering 65-74% of quality below strong-model-only cost, and the authors call that pattern exploratory at roughly 24 tasks per cell ([arXiv:2608.24358v1](https://arxiv.org/abs/2608.24358v1)).
- Your pair is not one of the two studied. A conversational benchmark of the same phenomenon found switch effects swinging "-8 to +13 percentage points in Multi-IF strict success rate", and that "some suffix models degrade under nearly any non-self dialogue history, while others improve under nearly any foreign prefix" ([Khraishi et al., arXiv:2603.03111v1](https://arxiv.org/abs/2603.03111v1)). The sign is a property of the pair, so measure yours.
- Progress does not live on disk. Traj-drop survives only because the working tree carries the edits. In research or planning work it drops the result itself.
- You reach for traj-drop on a downshift because it worked on the escalation. That is the 28% cell, plus 1.6-2.0x the post-handoff steps against compact-pre.
- The evidence is thinner than the table looks: one episode per configuration, no variability estimates, one primary coding benchmark ([arXiv:2608.24358v1](https://arxiv.org/abs/2608.24358v1)).

## Key Takeaways

- Ask whether to switch before asking how. On easy and medium tasks no Claude escalation interface repaid its cost in this study; downshifting is where the favorable middle point sits.
- Escalating: hand the strong model the repository state and a fresh problem statement, not the cheap model's transcript. That choice moved quality recovery from 47% to 64% on Claude and 36% to 84% on GPT.
- Downshifting: keep the strong model's trajectory. Removing it drops recovery to 28% and, relative to compact-pre, takes 1.6-2.0x the post-handoff steps.
- Handing over the session unchanged is the worst escalation interface in both families. On the Claude pair, restarting the strong model from scratch is cheaper and more accurate than Raw continuation.
- Two model pairs, one primary benchmark, single runs. Treat the direction rule as a hypothesis to test on your own pair, not a setting to ship.

## Related

- [Within-Task Model Cascade: Designing the Escalation Gate](../loop-engineering/within-task-model-cascade.md) — decides when to escalate; this page decides what the receiver inherits once you do
- [Trajectory-Conditioned Model Escalation (SWE-Router)](../patterns/agent-design/trajectory-conditioned-model-escalation.md) — reads the cheap model's partial trajectory to make the escalation call, then this page governs whether that trajectory travels with it
- [Context Compression Strategies](context-compression-strategies.md) — the compaction machinery the compact-pre and compact-suf interfaces are built from
- [Reasoning Retention and Compaction as Harness Settings](reasoning-retention-and-compaction.md) — the same question one level down: what the harness passes back across tool calls within a single model
- [Cost-Quality Pareto Measurement](../token-engineering/cost-quality-pareto-measurement.md) — how to run the pair-specific comparison this page says you need
