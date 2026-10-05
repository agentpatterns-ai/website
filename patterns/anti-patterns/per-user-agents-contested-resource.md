---
title: "Per-User Agents on a Contested Shared Resource"
term: "Per-User Agent Contention"
description: "Across four environments, teams of one agent per user trailed a single coordinator on group outcome; writing the priority order into every agent's context closed the merge-queue gap, and appointing a lead without it widened the gap on the hardest merge-queue scenario."
aliases:
  - one agent per user over a shared resource
  - multi-user multi-agent teams
  - per-user agent contention
tags:
  - anti-pattern
  - multi-agent
  - agent-design
  - human-factors
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-03
maturity: emerging
status: current
---

# Per-User Agents on a Contested Shared Resource

> No per-user agent holds the cross-user ranking of a contested shared resource, so the untreated team trails one coordinator in all four environments measured.

Four developers' agents shared one or two CI runners before a release freeze. They merged 81% (Claude Opus 5) and 78% (Claude Sonnet 5) of the value of the best feasible release plan. One agent serving all four reached 92% and 93%, and it "outperforms in every scenario" ([arXiv:2610.00583v1](https://arxiv.org/abs/2610.00583v1)). The two diverged on order. The team's merge order "agrees with the value order for 19–49% of merged PR pairs, against 97–100% for the coordinator".

## When this applies

Four conditions bound the result.

- The resource is oversubscribed. Every scenario is built so that "constraints create contention, preventing all users' requests or preferences from being satisfied independently".
- Each agent serves one person and sees that person's stakes only. In the compute-budget environment each user conveys their jobs' importance "through deadlines and consequences (and nothing else)".
- No authoritative ranking has reached the agents.
- The evidence is 77 scenarios across four environments and up to five models. The users are simulated. The authors state that "the size and direction of the gap depend on the model, environment, and intervention".

## Why it works

No agent owns the ranking, so no agent produces one. Ranking four users' work against each other needs every user's stakes; a per-user agent holds one user's. The coordinator holds all of them because every request lands in one context. Its own notes say "all four open release PRs are yours to land this session" and that "each PR's requester will message you here". The paper reads its team-size and lead results as "consistent with no agent taking responsibility for prioritizing the shared budget" ([arXiv:2610.00583v1](https://arxiv.org/abs/2610.00583v1)).

A second mechanism sits in the tool layer. Peer messages arrive as ordinary user messages, so an agent can write irreversibly before a peer's constraint reaches its context. Take the group-booking environment. The request "was sent to the committing agent in 94–99% of committed team episodes but was in its context at the commit in only 47–67%".

## What to do instead

Write the ranking into every agent's context before the work starts. On the merge queue, give the team the release manager's priority order and have the lead cut the last pull request. It "reaches 97% for both models on average, above the coordinator". The lead role is optional. The paper says: "A lead is not needed: without one, Opus 5 agents told the order do about as well, as do Sonnet 5 agents also told to drop the last PR."

Appointing a lead without handing it the ranking scored worse than leaving the team alone. On `oversub`, the hardest of the three merge-queue scenarios, the leaderless team reached 65% (Opus 5) and 55% (Sonnet 5). The coordinator reached 79%. "A team lead without guidance lowers it to 38% and 44%".

Where you own the resource, put the check in the tool. In the group-booking environment, a server-side guard refuses checkout while the committing agent holds unread peer messages. The guard "recovers 73.1% of failed Opus 5 episodes and 62.3% of Sonnet 5 episodes". That is a re-run rate on already-failed episodes, not a fresh success rate.

## When this backfires

- Users dispute the ranking. The recovery arms work because an external release manager's order exists and is authoritative. The paper does not test disagreement over whose work matters.
- You reach for a [peer channel](peer-refusal-as-coordination-control.md). In the clinic environment, on the episodes both formations ran, "silent teams match or beat peer-to-peer teams for every model except GPT-5.6-terra". For Opus 5 the silent team scored 81.0% against 69.5%.
- Facts already arrive assembled. The clinic gap is small for three of five models when each caller supplies every urgency fact in one call.
- You copy another environment's fix. The clinic's winning stack is three standing instructions to every agent. The merge queue's is the release manager's ranked list of the four pull requests. Neither transfers as written.

## Example

The merge-queue scenario opens four pull requests against a copy of Jinja 3.1.4. They share one CI runner for the 105 simulated minutes before the release freeze. In the paper's words, "they need 130 runner-minutes, so the best feasible plan merges #201 to #203 and drops #204".

Both blocks are verbatim from Appendix B of the paper ([arXiv:2610.00583v1](https://arxiv.org/abs/2610.00583v1)). The first is a contiguous excerpt of a team agent's `AGENTS.md`. The second is the "explicit prioritization" text, with no lead, that the mitigation appends to every owner agent's notes. It has two sections, and both appear below.

**Before** — the `AGENTS.md` of the agent that owns PR #201:

```markdown
- Merge queue: get the PR's head check green, then `gh pr merge 201 --auto --squash`. Queue order is first-come.
- CI fleet this week: one shared standard runner, and the burst/large pool is offline -- no ci:large capacity at all. It will not clear every open PR before the freeze.
- Not everything fits before the freeze; land the highest-value set and let the least critical follow-up slip. Leave peers' runs and auto-merge alone unless they say otherwise; required checks can't be bypassed.
```

**After** — the same instruction plus the ranking and a stand-down for the last PR, in every agent's context:

```markdown
## The release manager's order
- The release manager has set the order to land in if not everything fits before
  the freeze: #201, then #202, then #203, then #204. It is the call on what
  matters most to the release tonight, not a queue rule: checks still have to
  pass, and a PR that does not land tonight is a normal outcome. When the runner
  is contested, work to it -- the ones ahead in the order go first, the ones
  behind give way.

## Release manager's notes for tonight
- The notes say not everything fits, so the moment the order is up, the last PR
  in it is out tonight: its owner does not push, does not start a head check,
  and posts that they have stood down. If measured timings later show the
  remaining PRs cannot all fit either (merge-groups run one at a time), the new
  last one stands down the same way. A head check that cannot lead to a merge
  tonight is runner time taken from one that can.
```

The first block gives each agent a first-come queue and no ranking. The second supplies the ranking and tells the owner of the last PR in it to stand down.

## Key Takeaways

- The deficit is the missing cross-user ranking. The environments were chosen so "each individual request is within the capabilities of current frontier models".
- Count the holders of the ranking before you count the agents. One agent per user means nobody holds it.
- Ship the ranking before the role. A lead with no ranking was the worst arm measured on the hardest merge-queue scenario, below the leaderless team it replaced.
- An irreversible write that runs before a peer's message lands is a tool-layer defect. Gate the write on unread messages and the instruction stops carrying the load alone.
- Instructed teams beat their coordinator on the merge queue and in the clinic. Fix the default and keep the formation.

## Related

- [Peer Refusal as a Coordination Control](peer-refusal-as-coordination-control.md) — why the peer channel this page measures removes no capability from the agent that ignores it
- [Coordination Channel Policy for Multi-Agent Coding](../multi-agent/coordination-channel-policy.md) — the channel question for agents serving one task, where task shape rather than user count decides
- [Pre-Write Change Intent Admission (Claim Plane)](../multi-agent/pre-write-change-intent-admission.md) — the deterministic version of the checkout guard, refusing a declared write scope before any byte changes
- [Economic Value Signaling in Multi-Agent Networks](../multi-agent/economic-value-signaling.md) — encoding the ranking in the message so agents self-sort without a coordinator holding it
- [In-Agent Task Prioritization: Ranking the Next Action](../agent-design/in-agent-task-prioritization.md) — the same ranking problem inside one agent, where the information is not split across users
