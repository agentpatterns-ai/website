---
title: "Rolling Out a Team-Embedded Agent Like a Tool"
term: "Tool-Style Rollout of a Team Agent"
description: "Provisioning a proactive agent into shared team channels the way a tool is provisioned leaves the renegotiation of unwritten norms to whoever is in the channel."
aliases:
  - shared-channel agent rollout
  - team agent provisioning
  - proactive agent onboarding
tags:
  - anti-pattern
  - human-factors
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-28
maturity: emerging
status: current
---

# Rolling Out a Team-Embedded Agent Like a Tool

> Interviews with 17 people at one large technology company found them individually working out what a proactive agent in shared channels could do.

An agent that "integrates natively into workspaces via a dedicated service account, functioning as a peer in team chats, code repositories, and shared documents" acts in front of people who did not ask it to ([Qadri et al., arXiv:2609.29901v1](https://arxiv.org/abs/2609.29901v1)). Provisioning it the way a tool is provisioned, with access and an announcement, leaves the rest to whoever is in the channel: deciding when it may speak, what it may surface, and who is allowed to tell it to stop.

## What the evidence is, and is not

One interview study supplies everything this page reports about the deployment, and its shape bounds those claims. Qadri and co-authors interviewed 17 participants across 11 teams who had adopted "Team Agent", a persistent proactive agent deployed "across over 20 teams" inside "a single large distributed technology company", where it generated "over 41,000 conversational turns (both user and agent) and over 11,000 agent responses over a period of 5 months" ([Qadri et al., arXiv:2609.29901v1](https://arxiv.org/abs/2609.29901v1)).

Those turn counts are telemetry, not an outcome. The authors state the methodological limit themselves: the study "relies on users self-reported experiences, not observed metrics of change". Nothing this page takes from that study is an effect size, because no effect was measured. Three further limits, in their words: the site "reflects a highly technology-forward workplace where employees are already invested in experimenting with cutting-edge AI"; the data "represents a snapshot of this specific moment in time rather than following users over a longitudinal trajectory"; and the agent's design choices "are not intended to serve as a prescriptive blueprint for an AI teammate". The paper says the first three authors ran the interviews, and that participants were told the researchers had no involvement in developing Team Agent and that its developers would not see raw study data.

## The conditions that produce the breakdowns

All four held in this deployment. Remove any one and you are outside the deployment this study describes.

- The agent sits in a space several people share, so its mistakes are visible to colleagues who never invoked it.
- It acts without being addressed. Every breakdown quoted below followed an action nobody asked for.
- It can write to shared artifacts. In this deployment that covered comments on documents, bug filings and calendar invitations.
- The norms it steps on are tacit. Nobody wrote down which document is authoritative or which disagreement is healthy.

## What participants described

Stale files read as current. The agent "treated every file in a shared repository as equally current, authoritative, and relevant", citing old notes in a way P4 called "overconfidently talking about it like it's the law of the land". P1 recounted the cleanup: "Team Agent added a bunch of comments, this needs to be updated, this needs to be updated, this is wrong, this doesn't match this. So the next day people come in and they got these pings that there's all these comments, they go to them, it's taken them out of the regular workflow…it stole time away from a lot of developers that morning."

The org chart read as a workflow graph. "the agent proactively tagged P14's team's VP in 16 separate engineering bugs", because it "conflated organizational presence with workflow participation".

A consent control in the design that did not produce felt consent. The agent "was explicitly designed to have direct messaging be opt-in and configurable through a team-defined 'allow' list", and P2 still said: "First of all, I don't remember anyone on the team saying we accept being DM'd by it." The mechanism existed in the design; P2 did not remember the agreement.

Agent presence misread as a human response. P4 described a bystander effect: "people don't actually say anything now because they assume someone is handling it, but really it's the agent and they're not helping me at all."

None of this trended one way. The study reports that "the resulting experiences were deeply polarized", ranging from an indispensable "lifesaver" (P1) to a liability that had to be managed or ignored.

## Why it works

The paper's Discussion gives the authors' interpretation of the self-reported accounts, not a measured result: the misfirings occurred "because high proactivity requires an operational understanding of the tacit knowledge, situational stakes, and unwritten cultural rules that dictate when to act and when to wait" ([Qadri et al., arXiv:2609.29901v1](https://arxiv.org/abs/2609.29901v1)). It then separates what the agent could read from what it could not. The agent "could parse the technical metadata of interactions (e.g., response latencies) to enforce basic etiquette" but "could not parse their sociological meaning".

The second half is that a misfire does not vanish the way a rejected autocomplete does. When the agent erred, "the technical stack lacked the affordances for humans to easily isolate, audit, or roll back the non-human actor's behavior", so each wrong call converted into someone else's remedial work. The same capability is what produced the wins: "unbounded proactivity drove the agent's greatest successes—like surfacing obscure bugs and executing rote administration—yet triggered its most costly breakdowns."

A lab study points the same direction with measured data and a different population. In a randomized study of 16 two-student teams with an AI teammate against 17 all-human teams of three, "Students in AI teams responded to and built on one another less than students in all-human teams, reported lower belonging and status, and felt less valued when the AI dominated more of the conversation" ([Nixon et al., arXiv:2607.27179v1](https://arxiv.org/abs/2607.27179v1)). Read that as corroboration of direction only. Its authors scope it to "a single AI persona, a text-based interface, a single-session design, and a morally framed decision task".

## What the authors recommend

These are the paper's proposals, from its Discussion. The authors ran no intervention to test them and the study measures no outcome, so each is a hypothesis with a rationale attached, not a validated fix. Some teams reached the first one on their own: "some teams created their own constraints to build trust incrementally with Team Agent".

Release proactivity in stages. The authors "suggest a paradigm shift toward systems of progressive, adaptive autonomy—where an agent's proactive capabilities are initially tightly bounded by the team, and only gradually released as trust is organically earned through demonstrated competence". P13 gave the participant version: "It hasn't earned its space, it has asserted its space…I actually might be more okay with agency if it's earned agency."

Let the adopting team decide, not the org. The paper argues organizations "can ensure the initial deployment of these agents is driven by localized team consent rather than top-down enterprise mandates".

Write the boundaries down before the agent arrives. The recommendation is for "explicit, team-negotiated protocols" that say which actions stay human-only and which spaces stay agent-free. P12 suggested a code of conduct for agents comparable to the one employees have.

## When this backfires

Drop any of the four conditions and this page costs you more than it saves. A single-user session has no bystanders, a tag-to-invoke agent takes no unrequested action, and a read-only scope cannot pollute a document.

Three cases where the advice is wrong even with all four present:

- Regulated or safety-critical work. The answer there is an access-control decision, and local per-team tuning is the wrong governance model for it.
- Teams that wanted more assertion, not less. P10 wanted an agent that would "call you on your BS", and P16 wanted proactive nudges on open tasks. Turning proactivity down costs those teams the thing they came for.
- Reaching for a consent checkbox. The agent's design already had one and P2 did not remember the team agreeing to it.

## Key Takeaways

- Interview evidence, one company, 17 people, no measured outcome. Use it to recognize failure shapes, never to forecast a result.
- Check all four conditions before borrowing any of this. Three of the four, and you are reading about a different deployment.
- This agent could read interaction metadata such as response latencies and not their social meaning. The authors name that gap as a cause of its misfires.
- A misfire in a shared channel becomes a colleague's remedial work, because this deployment's stack had no way to isolate, audit or roll back the agent's actions.
- An opt-in control in the design is not agreement. The agent shipped with one and P2 did not remember the team agreeing to it.
- Budget the rollout for the argument about when the agent may act. The study records that argument happening and gives no estimate of how long it runs.

## Related

- [The Anthropomorphized Agent](anthropomorphized-agent.md) — the single-user version of the mental-model problem, where the mistaken expectations stay inside one head
- [The Implicit Knowledge Problem for AI Coding Agents](implicit-knowledge-problem.md) — why the norms an agent steps on are invisible to it in the first place
- [Progressive Autonomy: Scaling Trust with Model Evolution](../../human/progressive-autonomy-model-evolution.md) — the staged-release idea the paper recommends, written as an engineering practice
- [Proactive Idle-Time Anticipation (ProAct)](../agent-design/proactive-idle-time-anticipation.md) — the capability side of proactivity, and the conditions under which it pays
- [AI Adoption Footprint](../../human/ai-adoption-footprint.md) — the segmented adoption shape that the polarized reactions here are consistent with
