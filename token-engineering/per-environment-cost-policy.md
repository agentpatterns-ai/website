---
title: "Per-Environment Cost Policy from Agent Traces"
term: "Per-Environment Cost Policy"
description: "A cost-control strategy applied uniformly cut spend in some repositories and raised it in others; deriving the policy from each environment's own completed traces held in all 30 repository-setting cells measured."
tags:
  - token-engineering
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - environment-derived cost policy
  - trace-derived cost control
last_reviewed: 2026-10-19
maturity: emerging
---

# Per-Environment Cost Policy from Agent Traces

> A fixed cost plugin cut spend in some repositories and raised it in others; a per-repository policy cut cost in all 30 cells.

Use this when the agent returns to one environment, runs several tasks there, and receives a success signal for each task. Derive the policy from completed traces in that environment.

## Why a uniform cost plugin is unreliable

Three strategies taken from popular plugins turned out to have no stable sign. Profiling 60 SWE-Bench tasks across 6 repositories with Claude Code and Opus 4.8, researchers compared Rust Token Killer, Serena, and Aider's RepoMap against unmodified runs, each strategy configured identically in every repository. "Every strategy lowers cost in some repositories and raises it in others" ([TokenEconomizer, arXiv:2610.22732v1](https://arxiv.org/abs/2610.22732v1)). The seeded main experiment repeats it across 30 repository-setting cells: "RTK alone increases cost in 12 cells and RepoMap alone in 15."

A controller that learned its policy per repository from completed traces instead "reduces cost in all 30, by 5.2-40.1%". Charging its own LLM calls to the task that triggered them, it "reduces mean per-task cost on SWE-Bench by 18.4-30.9%, while improving Pass@1 over default execution in 4 of 5 agent-model settings". In the fifth setting Pass@1 fell 1.0 percentage point.

Payback is not immediate. Averaged over two Claude Code settings, five of six repositories cost more at first, and "all become cheaper by the sixth task and remain cheaper thereafter, ending with cumulative savings of 16.9-32.0%."

## The three levers, ranked by what they bill

| Lever | Headroom in the 60 profiled tasks | Cost change when run alone, two Claude Code settings |
|---|---|---|
| Prune tools that no task calls | 23 schemas shown every turn, no repository invoking more than 7; 16 never called | -13.2% and -17.7% |
| Inject one-line operational facts | Actions recurring in at least half a repository's tasks carry 12-28% of tool-call bytes | -11.8% and -14.3% |
| Interrupt unproductive loops | 10 failed runs were 17% of tasks and 32% of total spend | single digits |

The middle column is the profiling run; the right column is the ablation over the 277-task experiment ([arXiv:2610.22732v1](https://arxiv.org/abs/2610.22732v1)). The part worth copying is that each decision carries a reversal path: "a stale skill is retired once a trace contradicts it, a wrongly pruned tool returns at the next re-audit, and the failure-loop intervention redirects before it stops". A forced stop can also end a run after its scaled turn budget. It requires edit churn, dense errors and a repeated failure signature together; the judge cannot veto it.

## Why it works

Every turn bills the persistent instruction and tool prefix plus the whole interaction history, "causing earlier content to be charged repeatedly across the trajectory" ([arXiv:2610.22732v1](https://arxiv.org/abs/2610.22732v1)). Anything cut from that prefix is saved once per turn, which is why tool pruning led the ablation: it "acts on every turn of every task". The policy has to be local because the removable content is local. Matched against a different repository's complete history, only 7% of a repository's tool calls recur, mostly generic setup and test commands.

## When this backfires

- Few tasks per environment. Payback is slow: "All repositories except xarray initially cost more", so five of six did. The study ran fresh-checkout streams, the paper's "conservative test of experience reuse", and still crossed over by task six, with 18.4-30.9% savings on SWE-Bench. A short run in one environment can end before the crossover, and six tasks is not a universal threshold.
- No per-task success signal. The turn budget is a percentile of prior successful trajectories; the study took success from the benchmark grader, and without an equivalent the loop guard has no calibration.
- Fast-moving environments. The stored operational facts are what goes stale. Agents tend to follow retrieved experience closely, so inaccurate records compound as "error propagation" and seemingly correct ones can offer "limited or even misleading value" through "misaligned experience replay" ([arXiv:2505.16067v2](https://arxiv.org/abs/2505.16067v2)). Retirement on contradiction addresses this risk; it does not establish safety.
- Short trajectories or an already-thin tool interface. On the ReposVul security benchmark, savings fell to 6.4-9.3% "where shorter trajectories leave less removable cost" ([arXiv:2610.22732v1](https://arxiv.org/abs/2610.22732v1)).
- Stacking on a fixed strategy you already run. RepoMap bills its map every turn, so the controller paired with RepoMap "saves less than TokenEconomizer alone in four of five settings".

One paper carries most of this, at v1, with no independent replication, and its SWE-Bench streams are "related but independent fixes rather than actual user sessions" ([arXiv:2610.22732v1](https://arxiv.org/abs/2610.22732v1)). The paper treats those streams as the conservative case: "Continuous sessions should offer more reusable experience". Its Web-Bench streams do inherit the workspace, which is nearer to how a developer works. Treat the three measured levers as the finding and the percentages as someone else's environment.

## Key Takeaways

- Measure a cost strategy per repository before adopting it globally; its sign flipped between repositories in both the profiling and the seeded experiment.
- Spend attention on the levers that bill every turn. In the two Claude Code settings ablated, the tool-schema prefix beat trace-derived instructions, which beat loop interruption.
- Set the retirement threshold asymmetrically. One contradiction should outweigh one confirmation, because "a skill that should have been retired is re-billed on every later prefix, whereas a skill retired too eagerly can be proposed again under a new identifier" ([arXiv:2610.22732v1](https://arxiv.org/abs/2610.22732v1)).
- Measure the cumulative crossover in your environment. The six-task crossover came from six repositories averaged over two Claude Code settings.

## Related

- [Harness-Controlled Token Economics (The Harness Effect)](harness-token-economics.md) — the orchestration layer sets both token volume and effective price
- [Token-Cost Profiling and Reduction for Always-On Agentic Workflows](token-cost-profiling-always-on-workflows.md) — the human-run instrument, attribute, fix, verify loop for high-frequency workflows
- [The Four Terms That Decide What an Agent Task Costs](four-term-agent-cost-model.md) — why a per-turn prefix cut multiplies through the bill
- [Mask Tools Instead of Removing Them](../context-engineering/mask-tools-instead-of-removing.md) — the cache cost of changing a tool array, and when removal is still cheaper
- [Usage-Reinforced Memory Decay for Long-Running Agents](../context-engineering/usage-reinforced-memory-decay.md) — retention scoring for the stored facts this technique accumulates
