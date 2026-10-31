---
title: "Label Prompt Intent Before Comparing Prompt Counts"
term: "Prompt Intent Mix"
description: "Across two three-person groups in one shadowing study, artifact requests ran 78% of prompts against 18%, so a prompt total carries no fixed amount of delegated work."
tags:
  - human-factors
  - workflows
  - tool-agnostic
  - arxiv
aliases:
  - prompt intent mix
  - prompt intent classification
  - prompt count composition
last_reviewed: 2026-10-28
maturity: emerging
---

# Label Prompt Intent Before Comparing Prompt Counts

> Artifact requests ran 78% of prompts for one group of three developers and 18% for another, so equal prompt counts can mean unequal work.

A prompt total counts how many turns someone took, not how much work they handed to an agent. Shadowing 11 professional developers, Chou and colleagues classified 255 submitted prompts by intent and found the share asking for an artifact varied widely between groups of participants ([arXiv:2610.33588v1](https://arxiv.org/abs/2610.33588v1)). Label the turns before you compare totals across people.

## When this reading rule applies

The rule is conditional, and two conditions decide whether it is worth anything to you.

- You can label intent at all. The labels came from researchers reading prompts by hand. "For each prompt, we coded three aspects: (1) its intent (inquiry, request, or reply)", after they "analyzed each prompt's content and reviewed the coded activities during the ten minutes before the developer began formulating it" ([arXiv:2610.33588v1](https://arxiv.org/abs/2610.33588v1)). The paper validated no automated classifier, so the breakdown is unavailable wherever only a prompt total was recorded.
- You compare prompt streams whose intent mix can differ. The study does not test within-person changes over time.

## What the study coded

Chou and colleagues shadowed 11 professional developers recruited from a multinational enterprise software company and a foundation that organizes an open-source project with more than 1,000 developers. Each reserved about 90 minutes free of meetings and worked on their own tasks. Sessions were recorded with 13 developers and 11 were included, for about 15 hours of observation. Nine participants used Claude Code; P7 and P8 used Codex ([arXiv:2610.33588v1](https://arxiv.org/abs/2610.33588v1)).

From 280 prompt-formulation episodes the authors "excluded eight unsent or interrupted episodes and 17 agent commands unrelated to development or information seeking", retaining 255 submitted prompts. Those 255 were coded into three intents. Requests "ask the agent to produce or modify an artifact". Inquiries "ask the agent to retrieve or explain information, even when doing so requires tool use". Replies "respond to an agent's question or proposal". One prompt could carry more than one label.

Read every percentage below as the study reports it: a mean of each participant's own percentages, rather than a share of the 255-prompt pool. Table 4 averages "across all eleven participants, including zeros"; Table 6 averages within each group. Participant volume differs enough for that to matter, because "P5 had five retained prompts, whereas P6 had 43."

### The mix by participant group

The authors sorted the 11 participants into three recurring management patterns plus two mixed cases, then reported each group's intent mix ([arXiv:2610.33588v1](https://arxiv.org/abs/2610.33588v1), Table 6).

| Group (participants) | Requests | Inquiries | Replies |
|---|---|---|---|
| Supervisors (P1, P2, P5) | 78% | 18% | 7% |
| Delegators (P6, P7, P8) | 35% | 39% | 30% |
| Learners (P3, P4, P9) | 18% | 76% | 12% |
| Mixed (P10, P11) | 36% | 45% | 18% |

The authors note that "Categories can overlap, so percentages need not sum to 100%." The groups hold three, three, three and two participants, so each figure averages a handful of sessions.

Turns about the agent itself sit in the same stream. For Delegators, "23% of their prompts concerned agent information or configuration", against 0% for Supervisors in the study's Table 6. Across all 11 participants, "Agent-information inquiries accounted for 8% of prompts on average (29 prompts across six participants), while eight prompts requested changes to agent configuration" ([arXiv:2610.33588v1](https://arxiv.org/abs/2610.33588v1)). Directing agents to implement features reached 21% of participants' sent prompts on average, and seeking explanations of code 17%.

## Why it works

A submitted prompt is a conversational turn, not a unit of delegated work, and the two separate as soon as the turn mix changes. One prompt stream in this study carried artifact requests, information inquiries, replies that continued an existing goal, and turns about the agent's own status. The intent label is what ties a turn to artifact production, and the request share ran from 78% among P1, P2 and P5 to 18% among P3, P4 and P9, so two equal totals can sit on very different amounts of production ([arXiv:2610.33588v1](https://arxiv.org/abs/2610.33588v1)). That rests on the study's coding of observed sessions; the paper ran no causal test of it. The authors read the patterns as "recurring patterns of agent management that can shift with the task and context, rather than as fixed developer types", which makes the mix a property of the work in front of someone rather than of the person.

## When this backfires

- You have no classifier, so demanding the breakdown leaves you with nothing. The activity coding the intent analysis sits on cost a full pass over every recording: "Each recording was coded in full by one researcher. A second researcher then watched the entire recording and reviewed all segment boundaries and assigned codes" ([arXiv:2610.33588v1](https://arxiv.org/abs/2610.33588v1)). A rough count you already hold can beat a decomposition you cannot produce.
- A coarse measure sometimes outperforms a finer one. Studying GitHub Copilot, Ziegler and colleagues report that "the rate with which shown suggestions are accepted, rather than more specific metrics regarding the persistence of completions in the code over time, drives developers' perception of productivity" ([arXiv:2205.06537v1](https://arxiv.org/abs/2205.06537v1)). That covers code completion and perceived productivity rather than agent prompt streams, and it is still a case where the blunt number held up better.
- The evidence behind the sharpest contrast is thin. The 78% against 18% gap compares two groups of three participants in sessions of about 90 minutes. The authors "present the findings as practices observed in these work contexts, not as an exhaustive account or estimates of their prevalence among professional developers."
- The labels do not partition the count. Because "Prompts could receive multiple intent labels" and the shares need not total 100%, an intent breakdown will not cleanly divide a prompt total into disjoint parts.
- Inline completion has no stream of this shape. Nine of the 11 participants used Claude Code and two used Codex. A completion product produces accepted and rejected suggestions rather than intent-bearing turns, and the acceptance-rate measure fits it better.

## Example

Two participants in the study sit at opposite ends of prompt volume. "P5 had five retained prompts, whereas P6 had 43" ([arXiv:2610.33588v1](https://arxiv.org/abs/2610.33588v1)). A dashboard counting prompts would put P6 roughly nine times above P5.

The groups they fall into point the other way on composition. P5 is one of the Supervisors, whose requests averaged 78% of prompts. P6 is one of the Delegators, whose requests averaged 35%, whose prompts were 30% replies, and 23% of whose prompts concerned agent information or configuration.

The study reports those shares per group rather than per participant, so the artifact-request count for P5 and for P6 is not available. That is the gap. The total is easy to read off, and the composition that gives it meaning is not recorded.

## Key Takeaways

- Treat a prompt total as a turn count. In this study the artifact-request share ran from 78% to 18% between two three-person groups.
- Agent housekeeping sits in the same stream: 23% of Delegators' prompts concerned agent information or configuration, against 0% for Supervisors in the study's Table 6.
- The percentages are participant-weighted means including zeros, not shares of the 255 prompts, and the intent labels can overlap.
- Nothing here is a tested intervention. The paper coded observed sessions and disclaims prevalence estimates.
- Where no intent labels are available, report that alongside the count instead of treating the total as delegated output.

## Related

- [Developer Control Strategies for AI Coding Agents](developer-control-strategies-ai-agents.md) — the checking practices behind the same management patterns.
- [Cohort Segmentation in the Copilot Usage Metrics API](cohort-segmentation-copilot-usage-metrics.md) — recovering a segmented shape that an aggregate usage number hides.
- [Intervention Rate as a Diagnostic North Star, Not a Target](intervention-rate-diagnostic-north-star.md) — why an interaction rate needs its categories surfaced before anyone acts on it.
- [Reading a Vendor-Computed AI Coding ROI Dashboard](vendor-computed-roi-copilot-impact-dashboard.md) — checking what a supplied metric actually counted.
- [Adapting AI Assistants to Developer Interaction Style](developer-interaction-style-adaptation.md) — per-developer differences in how people drive the same tool.
