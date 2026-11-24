---
title: "Designing Proactive Agent Check-Ins: Signal, Review, and Memory"
term: "Proactive Agent Check-In Design"
description: "How LangChain designs proactive agent check-ins: surface only what needs action, make review fast, and feed responses into memory. One vendor post, one number, no time window."
tags:
  - agent-design
  - human-factors
  - memory
  - automation
  - tool-agnostic
aliases:
  - proactive agent check-ins
  - agent check-in review design
  - attention budget for proactive agents
last_reviewed: 2026-11-24
maturity: emerging
---

# Designing Proactive Agent Check-Ins: Signal, Review, and Memory

> LangChain's post on its proactive agents treats each check-in as a cost in attention and designs it for signal, fast review, and memory.

A proactive agent responds to events from three places: real-world events, schedules the developer sets, and schedules the agent sets ([LangChain](https://www.langchain.com/blog/what-weve-learned-building-proactive-agents)). Robin's pull request reviews start from the first. GTM Agent's daily brief runs on a schedule the agent created after a user asked for one. For trigger choice, see [Loop Trigger Selection](../../loop-engineering/loop-trigger-selection.md) and [Choosing a Scheduled Agent's Firing Interval](scheduled-agent-firing-interval.md). This page starts at the check-in after the trigger fires. The post's premise, "As they take on more goals, your attention becomes the scarce resource," is an opinion with no data behind it.

## Surface only what the human acts on

"An agent should surface only what's valuable," the post says. A new email "doesn't necessarily mean the agent should do anything about it" ([LangChain](https://www.langchain.com/blog/what-weve-learned-building-proactive-agents)). Two designs from the post:

- GTM Agent's review UI sorts conversations into ones waiting on the user, ones that need a draft reply, and ones that need no reply.
- Robin uses Jev as a decision model for when to join a Slack conversation, so it joins when it has something to add rather than forcing its way in or waiting to be tagged.

The post reports no accuracy or false-start rate for either. Offline ranking quality does not guarantee in-loop value, per [Treating Offline Judgment Quality as In-Loop Controller Value](../anti-patterns/offline-judgment-quality-as-controller-value.md).

## Make review fast, because review is the feedback channel

"Every check-in should be fast to review, because review is how your feedback gets back into memory" ([LangChain](https://www.langchain.com/blog/what-weve-learned-building-proactive-agents)). Three choices from its own agents:

- GTM Agent drafts outbound emails. Working through a backlog of them in Slack was slow, so LangChain built a custom review UI.
- Robin leads with a one- or two-sentence headline and puts the detail in a thread reply.
- Robin's pull request review request carries a one-line summary, the size of the change, and a button to claim it.

These are one team's choices. The two Robin choices are Slack-specific, and the GTM Agent choice moved review out of Slack. The post measures none, including review time.

## Feed responses back as memory

The post ties check-in quality to memory: "The agent can only tell the two apart if it knows what matters to you, and that knowledge comes from memory" ([LangChain](https://www.langchain.com/blog/what-weve-learned-building-proactive-agents)). Its running example, an executive assistant that watches an inbox, is not one of the two agents LangChain runs. Treat it as illustration.

| Signal | When | Executive-assistant example |
|---|---|---|
| Seed | Past | Memory seeded from the sent folder before the first run |
| Feedback | Present | The user rewrites a draft or rejects it with a reason |
| Outcomes | Future | A drafted email gets a reply |

Keeping memory useful raises three problems, which the post states without measuring them: salience (what to save), expiry (information gone stale), and duplication (a second entry that contradicts the first). The post says many proactive agents use "dreaming," a scheduled background job that reads recent traces and updates memory before the next run. It names no agents and offers no evidence that dreaming works. [Steering Agent Memory](salience-steered-memory-with-dreaming.md) has measured results from another vendor.

## Track check-ins and extend autonomy from feedback

The post suggests judging memory by tracking outcomes it should improve, such as time to draft approval and reply rate for the executive assistant. It adds that "the share of its check-ins you actually act on is worth watching too" ([LangChain](https://www.langchain.com/blog/what-weve-learned-building-proactive-agents)). It reports no value for any of these.

The post also claims that an agent that remembers feedback "stops making the same mistakes, which earns it more autonomy." Its example is letting the assistant book meetings once the user stops changing the times it proposes. It gives no deployment result. For authority on self-created schedules, see [Whose Permissions a Self-Scheduled Agent Run Carries](../../security/self-scheduled-run-authority.md).

## Limits of the source

- It is a vendor engineering post. It ends with "You can build proactive agents today with Managed Deep Agents," a LangChain product.
- It carries one statistic. More than 70% of runs on Managed Deep Agents, the platform LangChain built both agents on, come from schedules rather than an ad hoc human prompt. The post states no time window or denominator, and does not say whether the count covers only those two agents.
- The only agents the post reports LangChain running are Robin and GTM Agent, both internal to LangChain. Its delivery advice is Slack-specific.

Related cautions: [shared-channel rollout](../anti-patterns/proactive-team-agent-tool-rollout.md), [attention across parallel agents](../../human/attention-management-parallel-agents.md), and [harness additions for goals](../../workflows/task-to-goal-agent-harness-additions.md).

## Key Takeaways

- Sort events by whether they need action before they reach the human. Robin and GTM Agent do this, and neither has a reported error rate.
- Treat each rewrite, rejection, and outcome as memory input, and plan for salience, expiry, and duplication.
- The post suggests tracking the share of check-ins acted on and widening autonomy as feedback accumulates. It reports no result for either.

## Related

- [Loop Trigger Selection: Pairing the Start with the Stop](../../loop-engineering/loop-trigger-selection.md) — pairing a trigger with its stop
- [Choosing a Scheduled Agent's Firing Interval](scheduled-agent-firing-interval.md) — interval from the job and reader capacity
- [Steering Agent Memory: Judge Salience, Then Correct with Dreaming](salience-steered-memory-with-dreaming.md) — measured dreaming results
- [Treating Offline Judgment Quality as In-Loop Controller Value](../anti-patterns/offline-judgment-quality-as-controller-value.md) — offline gate quality versus in-loop value
- [Rolling Out a Team-Embedded Agent Like a Tool](../anti-patterns/proactive-team-agent-tool-rollout.md) — proactive agents in shared channels
- [Developer as CPU Scheduler: Attention Management with Parallel Agents](../../human/attention-management-parallel-agents.md) — attention across parallel agents
- [From Task Agents to Goal Agents: Harness Additions](../../workflows/task-to-goal-agent-harness-additions.md) — harness requirements for goals
- [Whose Permissions a Self-Scheduled Agent Run Carries](../../security/self-scheduled-run-authority.md) — authority on agent-created schedules
