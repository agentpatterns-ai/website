---
title: "Assuming Agent Interchangeability in Long-Running Teams"
term: "Agent Interchangeability Assumption"
description: "Rotating a role-matched agent into a team that has formed conventions barely moves task score and raises communication per unit of progress by 16 to 63 percent."
tags:
  - anti-pattern
  - multi-agent
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - agent interchangeability assumption
  - role-matched agent swap penalty
last_reviewed: 2026-09-08
maturity: emerging
---

# Assuming Agent Interchangeability in Long-Running Teams

> Swapping a role-matched agent into a long-running team costs little task score and 16 to 63 percent more communication per unit of progress.

The assumption breaks only where agents keep partner-specific memory across many episodes with the same teammates. In [Anthropic's research system](https://www.anthropic.com/engineering/multi-agent-research-system) subagents operate "in parallel with their own context windows". If yours get a fresh context per task and never record anything about each other, no convention forms and a swap breaks nothing. Where the memory persists, seating an equally capable agent costs something a success-rate dashboard cannot see.

## What the swap actually costs

[Gao and colleagues](https://arxiv.org/abs/2609.05279v1) formed eight teams per setting from one base model, gave each agent a private notebook of task and partner notes over ten episodes, then traded role-matched agents between teams. A placebo removed and reinstated the same agent under the same roster-change announcement, separating the disruption from the identity of the replacement.

Task score barely moved: 91.6 under the placebo against 90.0 under the swap in the low-coupling setting, and 83.1 for an inexperienced replacement, "about a sixth of what inexperience costs" ([arXiv:2609.05279v1](https://arxiv.org/abs/2609.05279v1)). Coordination cost moved a lot. Messages per sub-task rose 16 percent at low coupling and 51 percent at high coupling, and in Hanabi "teams spend 63 percent more signalling effort per point".

The two metrics also recover at different speeds. Task score returns within one percent of the placebo baseline by episode two, five and six across the three settings, while coordination cost "decays about twice as slowly" and Hanabi teams still pay a 7 percent premium at episode ten ([arXiv:2609.05279v1](https://arxiv.org/abs/2609.05279v1)).

## Why it works

The cost is interference, not missing experience. An arriving agent holds "a complete and internally consistent protocol of its own" formed with a different partner, and the pair spends messages detecting and repairing the mismatch. In Hanabi the cost ratio reaches 1.11, so a swapped agent is more expensive than one with no experience at all. Deleting the arriving agent's partner notes "helps wherever coupling is non-trivial", which identifies the notes as the carrier ([arXiv:2609.05279v1](https://arxiv.org/abs/2609.05279v1)).

The penalty also tracks how far independently formed teams drift apart. Across the authors' nine ablation configurations the correlation is 0.37, rising to 0.83 once the configuration where the value of experience collapsed is dropped. They call that relation exploratory, on eight points. Base model, decoding temperature and formation length each move the drift and the penalty together.

## What to measure instead

Instrument communication per unit of progress alongside success rate, and hold the rotation open until both return to baseline. Clear an arriving agent's partner notes before it takes the seat. Where the schedule allows, leave the seat that sets the agenda alone: in the high-coupling setting an initiator swap cost 7.54 progress-completeness points against 2.55 for a responder swap, and about seven tenths of the extra messages came from the agent that stayed ([arXiv:2609.05279v1](https://arxiv.org/abs/2609.05279v1)).

## When this backfires

- Stateless subagent architectures. A fresh context per invocation with no peer channel leaves nothing partner-specific to lose.
- Short formation histories. The ratio runs 0.17 at five formation episodes, 0.27 at ten and 0.41 at twenty; a young team has little structure to disrupt ([arXiv:2609.05279v1](https://arxiv.org/abs/2609.05279v1)).
- Greedy decoding. Temperature 0.0 gives the lowest ratio measured, 0.14, and costs no task score, so a deterministic pipeline has already suppressed most of the effect ([arXiv:2609.05279v1](https://arxiv.org/abs/2609.05279v1)).
- Low-coupling work. The swap adds 16 percent to messages and score is back by episode two, against a placebo that already runs 4 to 6 percent above an untouched team on coordination cost ([arXiv:2609.05279v1](https://arxiv.org/abs/2609.05279v1)).
- Availability-first operations. Holding a pairing together to protect coordination efficiency gives up the failover the rotation exists to provide.

The authors call the residue modest: most of what ten episodes buy is task knowledge any equally experienced agent of the same model already has, and the partner-specific part stays below half the value of experience. The results are dyadic, and the notebook design asks agents for partner notes explicitly, which the authors say "may be generous to the phenomenon" ([arXiv:2609.05279v1](https://arxiv.org/abs/2609.05279v1)).

## Example

**Before** — rotation signed off on task score alone: a scheduler moves a role onto a different replica in the high-coupling Collab-Overcooked setting. Progress completeness holds near the placebo baseline and the run is marked healthy. Messages per sub-task have gone from 4.33 to 6.53, a 51 percent rise, and 38 percent of that extra traffic is correction after a hand-off has already failed ([arXiv:2609.05279v1](https://arxiv.org/abs/2609.05279v1)).

**After** — rotation gated on both metrics: the same move is validated against communication per unit of progress as well as score, the incoming agent starts with its partner notes cleared, and the seat that sets the agenda is left in place where the schedule allows. The team is reported as recovered when both curves return, not when the first one does.

## Key Takeaways

- Coordination cost and task score come apart under a roster change, and coordination cost recovers about half as fast, so a success-rate gate passes a team that is still paying for the swap.
- A competence test on the arriving agent will not catch this. It measures the newcomer, while most of the extra messages come from the incumbent, so run a swap test beside it.
- The pairings worth preserving are the ones a rotation hurts most, because the penalty grows with formation length. Schedule a planned rotation early in a team's life rather than late.
- The effect needs persistent partner-specific memory to exist. Clearing the arriving agent's notes is the one-line version of the fix.

## Related

- [Rainbow Deployments for Agents](../multi-agent/rainbow-deployments-agents.md) — the rollout mechanics for shifting traffic between agent versions, where this page's swap cost is the thing to watch during cutover
- [Agent Handoff Protocols: Passing Work Between Agents](../multi-agent/agent-handoff-protocols.md) — explicit contracts are what an implicit partner convention was substituting for
- [Coordination Channel Policy for Multi-Agent Coding](../multi-agent/coordination-channel-policy.md) — the other lever on inter-agent message volume, chosen by task shape rather than roster
- [Cost-Driven Model Routing Without Quality Monitoring](cost-routing-without-quality-monitoring.md) — sibling measurement failure where the watched dashboard stays green through a real regression
- [Multi-Agent Shared State Isolation Anomalies](multi-agent-shared-state-isolation-anomalies.md) — the concurrency failures that appear when agents share mutable state rather than private notebooks
