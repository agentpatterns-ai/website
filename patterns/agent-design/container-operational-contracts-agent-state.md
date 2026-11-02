---
title: "Container Operational Contracts for Durable Agent State"
term: "Operational Contract"
description: "A container platform treats the container as disposable while an agent framework saves conversations and resumes runs. Fourteen contracts a deployment must meet to keep that state, with violation rates from 433 public repositories where the repository shows a verdict."
tags:
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - agent deployment operational contracts
  - framework-platform deployment contracts
  - LangGraph container deployment failures
last_reviewed: 2026-10-31
maturity: emerging
status: current
---

# Container Operational Contracts for Durable Agent State

> A container platform treats the container as disposable. An agent framework saves state in it. The deployment must close that gap.

Docker, Compose, and Kubernetes assume you can stop and replace a container at any time. Agent frameworks assume the opposite: they carry conversations across requests, pause a run until a person approves, and resume interrupted work from saved state. Each side documents only its own behavior. Mastouri, Ksontini, and Barrak call the obligations that the combination creates "operational contracts". They test 14 of them against 433 public LangGraph deployments ([Mastouri et al., 2026](https://arxiv.org/abs/2610.34620v1)).

## What the study covers

The study takes one framework (LangGraph) and three platforms (Docker, Compose, Kubernetes). It reads public Python repositories with at least 10 stars that ship a Dockerfile ([Mastouri et al., 2026](https://arxiv.org/abs/2610.34620v1)). The authors mark a contract broken only on positive evidence in the repository, so every violation rate below is a lower bound. Behavior hidden inside a built image escapes the analysis. A runtime sub-study injected seven platform events into 12 systems chosen to cover the contracts. It shows how violations appear, not how often.

## The contracts

The 14 contracts fall into three groups. This table paraphrases the paper's catalog and gives the share of applicable systems that violated each contract. Contracts marked "runtime" need execution evidence, so the repository analysis gives no verdict.

| Group | Contract | Violation rate |
|---|---|---|
| Saved state | Threads, paused runs, and memories survive a process restart | 99 of 265 (37.4%) |
| Saved state | The same state survives container replacement | 110 of 265 (41.5%) |
| Saved state | Every replica sees the same state for a thread | 3 of 19 |
| Saved state | The database accepts connections before startup migrations run | 6 of 46 |
| Running work | The stop grace period covers the drain of in-flight runs | 8 of 8 decidable |
| Running work | SIGTERM reaches the application, not only PID 1 | 3 of 15 |
| Running work | Progress is saved during a multi-step run | 1 of 9 |
| Running work | The server restarts after a crash | 6 of 7 decidable |
| Running work | An update keeps a worker listening | 7 of 8 decidable |
| Running work | Re-executed side effects after a mid-step kill are harmless | runtime |
| Running work | Interrupted runs resume after a kill, restart, or replacement | runtime; 54 of 61 systems ship no resume mechanism |
| Running work | The memory limit fits all concurrent runs | runtime |
| Clients and resources | External resources are released without relying on shutdown code | 14 of 22 |
| Clients and resources | Streaming clients resume after a redeploy | runtime |

Rows with fewer than 50 applicable systems are indicative only.

All figures come from the paper's repository analysis ([Mastouri et al., 2026](https://arxiv.org/abs/2610.34620v1)). The drain contract is the clearest case. LangGraph's production server allows up to 180 seconds to drain running work. Docker sends SIGKILL after a 10-second grace period by default. All eight decidable production-server deployments kept the 10-second default, 170 seconds short of the drain window.

## Most lost state never had a store

Of the 99 systems that lose state on restart, 77 ship no persistent store at all. The other 22 ship one that agent state never reaches ([Mastouri et al., 2026](https://arxiv.org/abs/2610.34620v1)). A persistent database in the Compose file does not show that the checkpointer uses it. The paper found 16 of 76 systems with an in-memory checkpointer that deployed a persistent store beside it and never routed agent state there.

## Fault injection

Under induced events, 14 of 16 predicted violations became runtime failures. The two that did not were cases where the deployed image carried safeguards the repository did not show ([Mastouri et al., 2026](https://arxiv.org/abs/2610.34620v1)).

On the predicted holds, the abstract and the body disagree. The abstract says "all seven predicted holds pass". The runtime results section describes eight systems predicted to satisfy their contract: seven passed and one was inconclusive because it had a single valid repetition. This page uses the body count, 7 of 8, with one inconclusive.

## How developers repair these failures

The authors mined 39,261 commits, pull requests, and issues and validated 122 repairs. Three results matter for a team planning its own fix ([Mastouri et al., 2026](https://arxiv.org/abs/2610.34620v1)):

- Failures start in deployment but get fixed in code. 95 of 122 repairs (78%) change application code only, and 22 change only deployment files.
- Two in three repairs fully restore the contract: 80 of 122. Saved-state repairs fare best at 32 of 39.
- Draining is the weak spot. Only 2 of 13 drain repairs lengthened the grace period. The other 11 started a drain but kept the 10-second default. 11 of 23 resume repairs were partial. Eight of those only reported interrupted runs instead of resuming them.

## Applying the contracts to a deployment

1. Check that agent state reaches a store that outlives the container. Run both a restart test and a replacement test. Eleven systems survived restart and lost state on redeployment.
2. Raise the stop grace period above the framework's drain window.
3. Confirm SIGTERM reaches the application process, not only PID 1.
4. Decide what happens to a run killed mid-step. Requeueing it or marking it failed is the most common repair.

## Limits

The numbers describe LangGraph projects on GitHub. They do not show that other frameworks, including Claude Agent SDK runtimes, share these rates. For those runtimes, see [Production Hosting Topology](agent-sdk-hosting-topology.md).

## Key Takeaways

- Treat framework-versus-platform obligations as a checklist you test, not an assumption. 37.4% of systems that need durable state lost it on a plain restart.
- Look for the store the state actually reaches. Shipping a database does not mean the checkpointer writes to it.
- Align the stop grace period with the framework's drain window. All eight decidable production-server deployments left a 170-second shortfall.
- Expect to fix deployment failures in application code. 78% of mined repairs changed code only.
- Expect predicted violations to fail at runtime. Fault injection turned 14 of 16 of them into runtime failures.
- Read every rate as a lower bound for one framework and public repositories.

## Related

- [Production Hosting Topology for Self-Hosted Agent SDK Runtimes](agent-sdk-hosting-topology.md) — what a container restart loses in a Claude Agent SDK runtime
- [Durable Turn Log for Agent Crash Recovery](durable-turn-log-crash-recovery.md) — recording intent and outcome so a replacement process resumes the turn
- [Cloud-Agent Three-Layer State Decoupling](cloud-agent-state-layer-decoupling.md) — which agent state is persistent and which is ephemeral
- [Agent Workspace Persistence Boundary](agent-workspace-persistence-boundary.md) — where workspace state must live to outlive the container
