---
title: "Absorbing Entry-Level Work into Senior-Agent Workflows"
description: "Routing entry-level tasks to a senior plus an agent is faster per task and removes the work juniors learn from. The people deciding cannot see the loss."
term: "Entry-Level Work Absorption"
aliases:
  - absorption of entry-level engineering work
  - junior development pathway erosion
tags:
  - anti-pattern
  - human-factors
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-27
maturity: emerging
---

# Absorbing Entry-Level Work into Senior-Agent Workflows

> Routing entry-level work to a senior plus an agent is faster per task, and it deletes what juniors learn from.

Absorption is the redirection of entry-level engineering work into senior-plus-agent workflows, so the tasks that used to train juniors stop arriving. [Yu and Moon (arXiv:2607.17067v3)](https://arxiv.org/abs/2607.17067v3) named the pattern from 14 interviews with juniors and senior engineers in South Korea, reporting that "the entry-level work that had historically provided learning opportunities for entry-level engineers was no longer reaching them." A senior in the study stated the routing decision outright: "What can a junior engineer do better than a 100,000-won Claude subscription? I don't think there's anything."

Every task assignment is also a training assignment. The first decision gets made every sprint, on throughput grounds, and it settles the second one by default.

## The conditions that make this bite

Three things have to hold at once. The study establishes the mechanism, not its size: its 14 participants, the authors write, "does not support claims about the prevalence or magnitude of the patterns we identified." The design is cross-sectional, and Yu and Moon recruited every participant in South Korea.

- You hire juniors. With no early-career engineers there is no pathway to erode.
- Your entry-level work is agent-sized. The absorbed tasks are the ones a senior now finishes in a single pass with an agent, the same class that used to be handed down.
- Juniors are evaluated on finished output. A junior who routes around the difficulty scores well, so nothing shows up in a review.

## Why it works

Absorption runs on two learning processes the paper names, and it removes the input to both. Legitimate peripheral participation ([Lave and Wenger 1991, cited in arXiv:2607.17067v3](https://arxiv.org/abs/2607.17067v3)) is the trajectory in which newcomers "learn by gradually moving from peripheral, lower-stakes tasks to more central roles." Route the peripheral tasks elsewhere and the trajectory loses its first step. Kapur's productive failure, cited in the same paper, holds that "generating imperfect or failed solutions enables learners to recognize critical features of knowledge that structured instruction alone does not allow." A junior who never writes the failed solution never gets the recognition, which one participant described from the inside: "I don't know what not to do. I've only seen the good examples, so I don't know what the bad ones look like."

## Why the people in charge cannot see it

Seniors read the situation as manageable because their own expertise formed before the change. S4, arguing from twenty years of experience, concluded: "The next generation won't be in that position. Therefore, we are fine." J2 described it from the other side: "The less time you invest, the less you get back — it feels like the core is hollowed out." The authors call this perceptual asymmetry. No alarm fires, because the failure mode is a task that stops arriving.

Telling juniors to opt out is a weak defense where the tool is collectively normalized. One explained the tipping point in a graded classroom: "Everyone except me was using GPT, so everyone except me was getting nearly perfect scores. I no longer had the freedom to work through assignments on my own, making mistakes as I went—so in the end, I had no choice but to use it too."

## When this backfires

Acting on this costs more than it returns in four situations.

- The reserved work teaches nothing. In the onboarding model the paper documents, newcomers fix typos and carry that change through a full release, so the release path is what the junior is exposed to. Protecting drudge on its own loses throughput and produces no expertise.
- Juniors already interact for comprehension. In the [Anthropic RCT with 52 mostly junior software engineers](https://www.anthropic.com/research/AI-assistance-coding-skills), the AI group averaged 50% on a comprehension quiz against 67% for the hand-coding group, and the AI users who scored highest "used AI assistance not just to produce code but to build comprehension while doing so." Where those habits already hold, an AI-free track buys no learning.
- AI raises novice output in other settings. Across 5,172 customer-support agents, [Brynjolfsson, Li and Raymond (arXiv:2304.11771v2)](https://arxiv.org/abs/2304.11771v2) found "less experienced and lower-skilled workers improve both the speed and quality of their output," with evidence that "AI assistance facilitates worker learning." Different occupation, and it measures output rather than expertise. It is still the strongest case that the tool carries part of the mentoring load.
- Hiring is constrained by budget. Yu and Moon concede that "broader economic shifts, post-pandemic corrections, and monetary tightening were key contributing factors" in the junior hiring decline. Redesigning a pathway does not move a headcount decision.

## Example

Both cases below are reported in [Yu and Moon (arXiv:2607.17067v3)](https://arxiv.org/abs/2607.17067v3).

**Before — entry-level work stops reaching the junior:** seniors in the study take the entry-level tasks because an agent makes each one a single-pass job for them. Every individual call is defensible on throughput, and the aggregate is the absorption quoted at the top of this page. One senior weighed the junior against a subscription price and said: "I don't think there's anything."

**After — a designed progression:** one team in the paper runs a "first step, one step, big step" model. Newcomers begin with minimal tasks such as fixing typos and carrying that change through a full release, then move on to self-directed problem-finding. The designer framed it as letting juniors "feel it by doing it themselves" rather than receiving abstract instruction.

Reserving tasks by how small they are reproduces the anti-pattern. Reserve them by what they expose, which in the second case is the release path.

## Key Takeaways

- Audit where the agent-sized tasks go before you audit which model juniors may use. The fix is in the routing, and a tool policy cannot reach it.
- Ask the juniors, not the seniors. The people with authority to notice are the ones the change did not affect, so an absence of complaints is not evidence.
- Evaluate juniors on their capacity to recognize knowledge gaps and errors while using an agent, which is what Yu and Moon recommend in place of raw problem-solving.
- The mechanism is documented and the magnitude is not. Treat this as a design prompt for your onboarding rather than a measured effect.

## Related

- [Skill Atrophy: When AI Reliance Erodes Developer Capability](../../human/skill-atrophy.md) — the same erosion measured inside one developer rather than in an organization's task routing.
- [Comprehension Debt: When Developers Understand Less of Their Own Codebase](comprehension-debt.md) — what a developer carries after accepting code they did not reason through.
- [Deliberate AI-Assisted Learning: Accelerating Skill Acquisition](../../human/deliberate-ai-learning.md) — interaction patterns that keep a junior learning while still using an agent.
- [Agentic Education: Persona Progression for Teaching AI Coding Tools](../../human/agentic-education-persona-progression.md) — a support-fading scaffold for the structured progression this page argues for.
