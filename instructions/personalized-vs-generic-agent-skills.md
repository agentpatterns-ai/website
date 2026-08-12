---
title: "Personalized vs Generic Agent Skills: Where Effort Pays"
term: "Personalized Skill Files"
description: "Per-developer skill files distilled from interaction history tie with a random colleague's file below about six relevant prior sessions. Pool instead."
aliases:
  - per-developer skill files
  - developer-specific skills
  - personalized coding agent skills
tags:
  - instructions
  - skills
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-12
maturity: emerging
---

# Personalized vs Generic Agent Skills: Where Effort Pays

> Personalized agent skills pay off only where a developer's history holds several sessions relevant to the task at hand.

A personalized skill file distills one developer's recurring preferences from their past agent sessions into reusable guidance. A replay study measured what that buys. Across 42 held-out test sessions from 13 developers, personalized skills scored 65.99 on a 100-point rubric against a 65.02 no-skill baseline. A single skill file pooled from all 13 developers scored 68.80 ([Huang, Du and Lan, arXiv:2608.10319v1](https://arxiv.org/abs/2608.10319v1)). Handing a developer a random colleague's skill file instead scored 65.94, a gain of +0.92 against the personalized file's +0.97.

## When personalization pays

The study breaks its results down by how many of a developer's prior sessions an LLM reviewer judged semantically relevant to the held-out task ([arXiv:2608.10319v1](https://arxiv.org/abs/2608.10319v1)):

| Relevant prior sessions | Personalized skill minus no-skill baseline |
|---|---|
| 0 | −6.33 |
| 1–5 | minimal or negative |
| ≥6 | +10.17 |

The +10.17 in the bottom row is the largest single effect the paper reports, and it is personalization working. Settle one question before building per-person files: how many logged sessions each developer has that resemble the work coming in. A team that started capturing agent transcripts this quarter sits in the top row.

## What the numbers do and do not support

Four caveats bound how far the comparison travels ([arXiv:2608.10319v1](https://arxiv.org/abs/2608.10319v1)):

- No condition reached statistical significance. Generic skills gained +3.78 (p=.063), personalized skills +0.97 (p=.399), and a random developer's skills +0.92 (p=.451).
- The sample is 13 developers and 206 sessions, filtered down from 8,866, with a simulated developer rather than a real one issuing follow-ups.
- The generic skill was pooled from every developer's evolution sessions "including those of the target developer", so it is a superset of the personal data rather than a competing alternative to it.
- Skills raised the follow-up rate in every condition, from 24.76% at baseline to 30.95% personalized and 30.00% generic. The authors read this as more implementation and validation work, not faster execution.

The comparison is strong enough to set where you spend first and too weak to settle the question.

## Why it works

Coverage explains the gap. A skill file changes behavior only when one of its rules matches the task in front of the agent. In this study 64.7% of personalized rules were unique to a single developer, so those rules had "limited opportunities to influence held-out tasks" ([arXiv:2608.10319v1](https://arxiv.org/abs/2608.10319v1)). Sparse histories compound the problem: the 164 evolution sessions used for distillation work out to about a dozen per developer, too few to separate a stable preference from one-off feedback on a single task, so some rules encode noise. Pooling across people raises the hit rate because it captures procedural practice that recurs across both tasks and developers, such as validation steps and review conventions. The dose-response curve above is the direct evidence for that reading, since hit rate is what more relevant sessions increases.

## When this backfires

- Zero relevant history. With no semantically related prior sessions, the personalized file made results worse (−6.33). Early in a logging program it is a net cost.
- Wide task diversity. Rules unique to one developer never fire when the next task resembles nothing in their history, and you still pay the tokens to load them.
- Team conventions filed as personal preferences. Distilling a shared convention per person writes the same rule into every file and multiplies maintenance for no measured gain.
- Preferences that must never be violated. Advisory prose is the wrong container. TRACE mines user corrections into atomic rules and compiles them into runtime checks. That cut preference violations on coding tasks from 100.0% to 37.6% in-distribution and to 2.0% out-of-distribution ([Zhou et al., arXiv:2606.13174v1](https://arxiv.org/abs/2606.13174v1)). Enforcement closes that gap where loaded context does not.
- Restructuring tooling on one study. Thirteen developers and a simulated user are thin ground for a policy change, and the authors expect richer interaction-trace datasets to change the picture ([arXiv:2608.10319v1](https://arxiv.org/abs/2608.10319v1)).

## Key Takeaways

- Measure relevant-session density before building per-developer skill files. Below roughly six relevant prior sessions per task, the personalized file added nothing measurable ([arXiv:2608.10319v1](https://arxiv.org/abs/2608.10319v1)).
- Put shared procedural conventions in one team-wide skill file first. It is the option that does not depend on any single developer's history being deep enough.
- Run your own before-and-after on a handful of representative tasks before adopting either shape. Neither result here cleared p<.05, so the study sets a prior rather than a decision.
- Route hard requirements to enforcement rather than a preference file. Compiled runtime checks cut violations far further than distilled prose ([arXiv:2606.13174v1](https://arxiv.org/abs/2606.13174v1)).
- Re-test as history accumulates. The finding is about data density, and personalization may pay once per-developer histories deepen.

## Related

- [Adapting AI Assistants to Developer Interaction Style](../human/developer-interaction-style-adaptation.md) — independent evidence that per-developer configuration pays back only under specific team conditions
- [Skill Loadout Curation for Coding Agents](../context-engineering/skill-loadout-curation.md) — which skills to load once you have decided what to write
- [Example-Driven vs Rule-Driven Instructions](example-driven-vs-rule-driven-instructions.md) — the other sourcing choice for instruction content
- [Restraint Rules Need External Enforcement](restraint-rules-need-external-enforcement.md) — why preferences that stop work belong in CI rather than a context file
- [Cost-Aware Skill Rewriting: Preserve Operational Anchors, Not Skill Tokens](cost-aware-skill-rewriting.md) — the token economics of what stays in a skill file
