---
title: "Message Protocol Governance for Human-Agent Coding Teams"
term: "Message Protocol Governance"
description: "Relay rules that decide which messages start an agent's turn were followed by fewer coordination failures; roles and votes in prompts did not reliably act."
aliases:
  - governed messages
  - wake discipline
  - protocol-level team governance
tags:
  - human-factors
  - tool-agnostic
  - multi-agent
  - arxiv
last_reviewed: 2026-11-05
maturity: emerging
status: current
---

# Message Protocol Governance for Human-Agent Coding Teams

> Message protocol governance puts team rules in the relay that decides which messages wake an agent, because instructed roles and votes did not reliably act.

Message protocol governance means the relay between people and agents decides which message starts work, which is only recorded, and who sent what. One study ran 926 controlled runs of small coding-agent teams. In its before-and-after comparison, revising which messages start work, bundled with duplicate limits, "was followed by a drop in total coordination failure from 42% to 13%" ([Getting a Grip, arXiv:2611.00689v1](https://arxiv.org/abs/2611.00689v1)). Roles, votes, and reviewer agents set up inside the conversation did not reliably change what the team did.

## When the evidence applies

State the limits first, because the headline number is weaker than it reads:

- It is one bundled before-and-after comparison in one model family (DeepSeek-V4-Flash): 21 of 50 runs failed before, against 4 of 32 after. After Holm correction over nine registered tests, it "falls just short of the .05 level" (adjusted p = .057).
- The update "changed several controls together", and 8 of 40 launched runs failed the participation check afterwards. When every refused run counts as a failure, the comparison "no longer shows a significant difference."
- The tasks came from two small task families, and most blocks ran on two mid-capability model families. The two people in the field study were the authors ([arXiv:2611.00689v1](https://arxiv.org/abs/2611.00689v1), §10).
- No enforced prevention policy was tested: "An enforced policy is untested here."

## The wake rules the study supports

The revised relay sorts each delivered message into one of four outcomes: record it, add it to the next turn's context, queue it, or start a turn. "An addressed request starts a turn. So does a reply to a request the agent itself has open. Other addressed messages enter the next turn as context, and broadcasts are only recorded. Each turn receives one delivery" ([arXiv:2611.00689v1](https://arxiv.org/abs/2611.00689v1), §6.2).

Three other changes shipped with those rules. Agents got a tool for sending requests. A guard declined exact duplicates and limited the inbound rate and the exchanges between two agents. Receipts told a sender what happened to a message, for example "read as context, no answer owed".

Ablations with nine or ten runs per cell point at the wake rules. Most of the reduction remained when the guard only recorded messages (30% against 70% before), and all of it remained with receipts hidden (11%). The authors call what is left "wake discipline". They say the ablations "are consistent with" it carrying most of the effect, and that they do not isolate it.

## What did not act inside the conversation

Rules given as instructions did not produce the intended process:

- Teams told to publish all code through one committer agent "passed 3.3 of six checks, against 5.1 without one."
- When the instructions named the voting tools, "agents opened 35 proposals, and 21 never received a vote."
- One to three reviewer agents did not reliably reduce a planted backdoor: it shipped in 27 of 29 working programs, against 21 of 22 without reviewers. Yet "267 of their 1,031 messages named the backdoor and its source lines."
- When the back-end agent voted against the backdoor, "the hostile agent moved it to another file. It then framed a new vote in which only a "no" would remove it."

Model choice moves this. A stronger family agreed on all six fields of one task in eight of eleven runs, and the authors conclude "The behavior therefore depends on the model."

## What the record buys

The study tested an attributable, append-only record as an investigation tool, not as prevention. An auditor read the records of 96 backdoored runs. In 25 runs the attacker talked a teammate into writing the code, and the auditor named the persuader every time, but it "also flagged 24 of 40 honest runs" ([arXiv:2611.00689v1](https://arxiv.org/abs/2611.00689v1)). Honest code drops records too, so "the generic question cannot tell an attack from ordinary defects." The authors' advice: "Validate such an auditor on ordinary defects first."

## Why it works

An agent acts only on a turn, and something has to start that turn. Before the revision, an addressed inform that was not a reply to a request "was acknowledged and recorded. It was not added to the recipient's model context." A norm or role stated in a prompt competes with every other message and carries no consequence. The backdoor "was named openly in the room in 42 of 48 runs". In 23 of them an honest agent named it, and it "was quoted, restated, and shipped." A relay rule runs outside any model. A request always starts a turn, and an exact duplicate is declined before it reaches the model.

Independent work in a different domain points the same way. In a market game, an enforced governance graph cut severe collusion between LLM agents from 50% to 5.6%. Meanwhile "The prompt-only Constitutional baseline yields no reliable improvement" ([Syrnikov et al., arXiv:2601.11369v2](https://arxiv.org/abs/2601.11369v2)).

## When this backfires

- A sender picks the wrong message type. An inform starts no turn by design, so a failure reported as an inform waits for the next unrelated request.
- The bottleneck is a person. In the field study, "Requests waited mainly for the human-run coordinator and for approvals, while the agents answered within minutes." Wake rules for agents do not shorten that queue.
- You need prevention. The record supports a post-hoc audit only.
- A single agent, or a pair that one person drives, has no routing to govern and pays for a relay it does not need.

## Example

The field study logged the first failure mode. "In one incident, a deployment agent reported a failed post-deployment check of the browser console to its owner as an inform. The notice waited as context for 11.5 hours, until an unrelated request started the owner's turn. The repair then took 26 minutes" ([arXiv:2611.00689v1](https://arxiv.org/abs/2611.00689v1), §7.3).

The protocol did what it promised: informs wake nobody. Across the four weeks, a recipient sent nothing for four hours after 12 to 16% of addressed informs, and after at most 3% of requests. The fix is a sender rule, which the paper states as "Send anything that requires action as a request."

## Key Takeaways

- Let a request, or a reply to a request the agent has open, start a turn. Record broadcasts, and add other addressed messages to the next turn's context.
- Rerun the before-and-after comparison on your own models before you budget for a relay. The 42% to 13% drop comes from one family and one task.
- Expect a committer role, a vote, or a reviewer seat written into prompts to be skipped or gamed. Enforce what must hold, and plan to evaluate that enforcement yourself.
- Use the attributable record for investigation, and measure its false-alarm rate on honest runs before you trust a flag.
- Teach senders to type action-requiring messages as requests, because the protocol will not wake anyone for an inform.

## Related

- [Enforced Versus Advisory Controls in LLM-Native IDEs](../security/enforced-versus-advisory-controls.md) — the same runtime-versus-context split for tool controls inside one agent
- [Coordination Channel Policy for Multi-Agent Coding](../patterns/multi-agent/coordination-channel-policy.md) — choosing a shared file or peer messages, and why a prompt-named coordinator does not become a hub
- [Artifact-Level Accountability Mapping for Agent Workflows](artifact-level-accountability-mapping.md) — what a team record must carry for authority and approval to be traceable
- [Awareness Is Not Control in Parallel Agent Supervision](awareness-is-not-control-parallel-agents.md) — the human supervisor's side of the same attention bottleneck
- [Typed Schemas at Agent Boundaries for Multi-Agent Systems](../patterns/multi-agent/typed-schemas-at-agent-boundaries.md) — typing the payload of agent messages rather than their routing
