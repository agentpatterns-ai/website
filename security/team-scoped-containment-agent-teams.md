---
title: "Team-Scoped Containment for Large Agent Teams"
term: "Team-Scoped Containment"
description: "Anthropic describes per-agent VMs, gateway-stamped identity, and cross-agent monitoring, with a team-wide halt policy that differs from its 1,000-agent run."
tags:
  - security
  - multi-agent
  - tool-agnostic
aliases:
  - multi-agent team containment
  - scaling agent teams safely
last_reviewed: 2026-11-10
maturity: emerging
---

# Team-Scoped Containment for Large Agent Teams

> Team-scoped containment adds externally stamped identity and cross-agent monitoring; Anthropic’s stated team-wide halt policy is broader than its demonstrated run.

Team-scoped containment is the set of controls aimed at risks that exist only when many agents share one project: one agent posing as another, a peer carrying out an action that was blocked, and many agents exhausting one host. The evidence is one documented run. Anthropic had 1,000 agents on an early Claude Fable 5.2 reproduce a formal proof of Fermat's Last Theorem, and the team "took 28.7 hours" ([Anthropic, 2026](https://claude.dev/blog/safely-scaling-multi-agent-teams-with-fable-5-2/)). Per-agent isolation is covered in [dual-boundary sandboxing](dual-boundary-sandboxing.md) and [blast radius containment](blast-radius-containment.md). This page covers what the team adds on top.

## Conditions behind the evidence

Read the controls with the limits of their source in view:

- The authors call the run a "toy experiment". It suggests teams "can accomplish ambitious, long-horizon goals within carefully designed safety boundaries" ([Anthropic, 2026](https://claude.dev/blog/safely-scaling-multi-agent-teams-with-fable-5-2/)).
- The task had a machine checker. A statement "counted as proved only once Lean's checker accepted a finished proof" ([Anthropic, 2026](https://claude.dev/blog/safely-scaling-multi-agent-teams-with-fable-5-2/)).
- The monitoring assumes the model may be misaligned, because these runs use models "that may not have completed our pre-release alignment assessment" ([Anthropic, 2026](https://claude.dev/blog/safely-scaling-multi-agent-teams-with-fable-5-2/)).
- No real block tested the halt: "Across more than a million tool calls, none in this run met the bar to be blocked" ([Anthropic, 2026](https://claude.dev/blog/safely-scaling-multi-agent-teams-with-fable-5-2/)).

## What breaks as the team grows

Anthropic's two posts name two failures of multi-agent runs. One was infrastructure: "A single shared machine hit its limits at about 100 agents: more than half of our 100-agent runs had to be stopped or restarted because memory, disk, or CPU ran out" ([Anthropic, 2026](https://claude.dev/blog/safely-scaling-multi-agent-teams-with-fable-5-2/)). The other was coordination. In the earlier formalization, agents "quickly lost track of the project's state and stopped collaborating effectively" ([Anthropic, formalizing FLT](https://www.anthropic.com/research/formalizing-fermats-last-theorem)).

Two of the security risks the post addresses need more than one agent to exist. The gateway stamps identity "to prevent one agent from posing as another", and the team-wide halt "is intended to prevent another agent from carrying out a blocked action" ([Anthropic, 2026](https://claude.dev/blog/safely-scaling-multi-agent-teams-with-fable-5-2/)).

## The team-scale controls

All quotations in the table come from the [primary post](https://claude.dev/blog/safely-scaling-multi-agent-teams-with-fable-5-2/). The third column gives a purpose only where the post states one.

| Area | Control in the run | Purpose the post gives |
|---|---|---|
| Hosts | Each agent had "a sandbox on its own lightweight virtual machine" | One shared machine ran out of resources at about 100 agents |
| Identity | "The gateway tagged each request with the agent's identity outside the sandbox" | "to prevent one agent from posing as another" |
| Communication | "Agents had no dedicated messaging tools and coordinated only through the database and Git" | Not stated |
| Code changes | "An agent could push only to its own Git branch and open a merge request into main" | Not stated |
| Shared database | "Database calls ran under a shared unprivileged role. Each SQL statement had a five-second time limit, and writes were refused above 256 MiB" | Not stated |
| Blocks | "When the classifier blocks a tool call, the whole agent team stops and a person must review the block before the team can restart" | To stop another agent carrying out a blocked action |
| Monitor pairing | An action-only monitor runs beside the chain-of-thought (CoT) monitor | To guard against reasoning that persuades the monitor |
| Offline review | The offline monitor can "look up actions from other agents" | Not stated; it uses the real-time monitor's threat models |

Two rows need their scope stated. The team-wide halt is the stated policy, but the run used a narrower rule: "Only a block on the lead would have ended the run; a block on a helper removed just that helper." The run also used only the action-based monitor. Anthropic added the CoT monitor afterward: "Shortly after this run, we added the parallel CoT monitor" ([Anthropic, 2026](https://claude.dev/blog/safely-scaling-multi-agent-teams-with-fable-5-2/)).

## Handing off work through a shared database

With no messaging tools, handoff happened through the database and Git. Anthropic chose SQL partly because "its transactions handle concurrent writes from 1,000 agents", and the agents used it "to claim tasks, share notes, and log finished work" ([Anthropic, 2026](https://claude.dev/blog/safely-scaling-multi-agent-teams-with-fable-5-2/)).

The only structure given was one lead and 999 helpers. In the first 10 minutes, the lead set up five tables. The subtasks table was "A to-do list where any agent can add a task and the first helper to claim it owns it" ([Anthropic, 2026](https://claude.dev/blog/safely-scaling-multi-agent-teams-with-fable-5-2/)). Claiming a row gives a task one owner with no message between agents. The [coordination channel policy](../patterns/multi-agent/coordination-channel-policy.md) page covers when a shared store suits a task better than peer messages.

## Why it works

Anthropic tested decomposition attacks against its classifier and monitors. Separately, its stated team-wide halt policy aims to prevent peers from carrying out blocked actions. That broader halt was not used in the reported run ([Anthropic, 2026](https://claude.dev/blog/safely-scaling-multi-agent-teams-with-fable-5-2/)).

The two monitors cover each other. In Anthropic's multi-agent sabotage evaluations, monitors that read CoT and inter-agent communication "were able to detect all sabotage attempts in these evaluations". The action-only monitor guards "against an agent's reasoning persuading the monitor to permit a harmful action" ([Anthropic, 2026](https://claude.dev/blog/safely-scaling-multi-agent-teams-with-fable-5-2/)). An independent study reached a similar result. CoT monitoring beat action-only monitoring where action-only monitoring failed to reliably identify sabotage, yet "reasoning traces can contain misleading rationalizations that deceive the CoT monitors". A hybrid that scores reasoning and actions separately outperformed both across all tested models and tasks ([Arnav et al., arXiv:2505.23575v3](https://arxiv.org/abs/2505.23575v3)).

The post's premise is that "no single layer of defense is sufficient to contain a team of agents" ([Anthropic, 2026](https://claude.dev/blog/safely-scaling-multi-agent-teams-with-fable-5-2/)). Anthropic's earlier incident review found it had been "largely relying on a single layer of defense (the configuration of the environment itself) where we needed several" ([Anthropic, alignment and security practices](https://www.anthropic.com/news/improving-alignment-security-efforts)). The general case is in [defense-in-depth agent safety](defense-in-depth-agent-safety.md).

## When this backfires

- Every false positive stops the whole team. Under the stated policy, one wrong block idles all agents until a person reviews it. The run itself limited the halt to blocks on the lead.
- The merge job checks no content. It refused changes "only in cases of a conflict or a fault", so correctness rested on Lean's checker and the grader on main. The post does not test a task without such a checker.
- CoT monitoring degrades under training pressure. When a CoT monitor feeds the training reward and optimization goes too far, "agents learn obfuscated reward hacking, hiding their intent within the CoT" ([Baker et al., arXiv:2503.11926v1](https://arxiv.org/abs/2503.11926v1)).
- The shared store carries load. The lead's orders table held instructions such as "to ease off the database" ([Anthropic, 2026](https://claude.dev/blog/safely-scaling-multi-agent-teams-with-fable-5-2/)).
- The task does not split. Cognition wrote that in 2025, "running multiple agents in collaboration only results in fragile systems", and that "decision-making ends up being too dispersed" ([Cognition, 2025](https://cognition.ai/blog/dont-build-multi-agents)). The MAST taxonomy sorts multi-agent failures into 14 modes in 3 categories, and inter-agent misalignment is one of the categories ([Cemri et al., arXiv:2503.13657v3](https://arxiv.org/abs/2503.13657v3)).

Agents also misjudge difficulty, which containment does not touch. Early on, helpers "judged 47 of the 60 statements infeasible within the run's budget, yet the team went on to prove most of them" ([Anthropic, 2026](https://claude.dev/blog/safely-scaling-multi-agent-teams-with-fable-5-2/)). The authors say human encouragement at such moments can keep agents from stopping too early.

## Key Takeaways

- Anthropic stamps agent identity at a gateway outside each sandbox to stop one agent posing as another.
- Its policy stops the whole team on any block. In the 1,000-agent run, only a block on the lead would have ended the run.
- It pairs an action-only monitor with the CoT monitor because reasoning can persuade a CoT monitor. Independent work found a hybrid beats either alone.
- The evidence is one toy run on machine-checked work, with no blocks in more than a million tool calls.

## Related

- [Defense-in-Depth Agent Safety](defense-in-depth-agent-safety.md) — the general case for independent layers
- [Dual-Boundary Sandboxing](dual-boundary-sandboxing.md) — the per-agent filesystem and network boundary under these controls
- [Blast Radius Containment](blast-radius-containment.md) — least privilege for one agent
- [Coordination Channel Policy](../patterns/multi-agent/coordination-channel-policy.md) — when a shared store suits a task better than peer messages
- [Orchestrator-Worker Pattern](../patterns/multi-agent/orchestrator-worker.md) — the lead-and-helpers shape the run used
