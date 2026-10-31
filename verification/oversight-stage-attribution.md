---
title: "Oversight Stage Attribution for Missed Agent Defects"
term: "Oversight Stage Attribution"
description: "Extra checking ran on 65 of 71 silent-defect tasks and 28 ended fixed. Grade a missed defect by which of five review stages the review reached."
tags:
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - oversight stage attribution
  - review stage attribution
  - oversight pipeline staging
last_reviewed: 2026-10-25
maturity: emerging
---

# Oversight Stage Attribution for Missed Agent Defects

> Study participants checked beyond the mandatory gate on 65 of 71 silent-defect tasks and fixed 28, so name the stage that lost the defect.

Oversight stage attribution grades a missed defect by how far the review traveled. The study models review of agent output with the five stages listed below. Each is a different thing to get right. Dissanayake and colleagues traced 71 seeded silent-defect tasks with 36 participants, and the losses spread across all four stages after the first ([arXiv:2610.27801v1](https://arxiv.org/abs/2610.27801v1)).

## When the attribution pays

Use the staging to diagnose the failure: "Our study did not evaluate specific interventions, but it identifies directions for task-calibrated re-engagement" ([arXiv:2610.27801v1](https://arxiv.org/abs/2610.27801v1)). Three conditions decide whether it earns its cost.

- A silent defect already shipped past a review, and the repair has to match the failure.
- The work is consequential. One participant described the opposite case: "These tasks felt low stakes, so I did not feel the need to put in as much effort."
- You can afford to classify what the reviewer did. The authors combined manual coding with automatically recorded actions, and a second coder on a stratified 24% sample reached only "an agreement of 75%".

## The five stages and what each loss means

The counts come from the study. The right-hand column gives possible interpretations; stage counts alone cannot establish the cause.

| Stage | Instances of 71 | A loss here reads as |
|---|---|---|
| Any evaluation past the mandatory check | 65 | Six instances stopped before additional evaluation |
| Aimed at the stated requirement | 40 | Check whether the reviewer identified the requirement at risk |
| Evidence capable of exposing the defect | 35 | Check whether the probe could expose this defect |
| Evidence read correctly | 30 | Check how the reviewer interpreted the result |
| Defect fixed | 26 | Check why recognition did not lead to repair |

Twenty-three of those 65 never got past the first stage: "In 23 instances, evaluation remained generic, such as rerunning an existing example or asking the agent to 'check' the solution without specifying what to examine" ([arXiv:2610.27801v1](https://arxiv.org/abs/2610.27801v1)). Delegating the check to the same agent is one of the two forms the paper names there. It "can create visible verification without an independent judgment about where the implementation may fail." Two further defects fell outside this path, so 28 of 71 ended resolved in total.

Do not substitute the reviewer's own account for a stage. The paper reports that participants were "often highly confident while missing silent defects" ([arXiv:2610.27801v1](https://arxiv.org/abs/2610.27801v1)). [Name the Check That Passed](named-check-over-evaluation-confidence.md) covers confidence in its own right.

## Why it works

The stage breakdown helps distinguish reviews that produced different outcomes. Between the study's two rounds the checking rate held flat: "Participants were similarly likely to initiate additional evaluation in Round 1 and Round 2 (91.7% vs. 91.4%)." The outcome nearly doubled over the same pair of rounds, as shown by "Silent-defect resolution increased from 10/36 tasks in Round 1 (27.8%) to 18/35 in Round 2 (51.4%)." In these rounds, review frequency alone did not distinguish the outcomes.

Underneath sits a decomposition of three separable capabilities. The authors state that "effective oversight required participants to identify what could fail, produce evidence capable of exposing it, and interpret that evidence correctly" ([arXiv:2610.27801v1](https://arxiv.org/abs/2610.27801v1)). Any one can be absent while the others hold. That is why their conclusion locates the failure in the shape of the actions: oversight "broke down not because people stopped acting, but because their actions didn't amount to the required evaluation."

## When this backfires

- Naming the stage does not supply a fix. A registered-report experiment tested checklist guidance, not stage naming, with 70 developers across three review tasks, weighted toward novice reviewers. It reported that "we did not identify a strong relationship between the guidance provided and code review performance" ([Wurzel Gonçalves and colleagues](https://link.springer.com/article/10.1007/s10664-022-10123-8)).
- The losing stage may sometimes reflect competence. Resolution rose with self-reported Python proficiency, "from 16.7% among beginners" upward, while "self-reported experience with agentic AI tools was not associated with defect resolution" ([arXiv:2610.27801v1](https://arxiv.org/abs/2610.27801v1)). Where generated code exceeds what the reviewer can evaluate, the attribution renames the problem.
- One task mix does not transfer. In the same study "silent-defect detectability varied substantially by task, from 8% for CONFLICTS to 75% for BILLING", so a profile measured on one change class predicts little about another.
- Sharpening the reviewer may be the wrong lever. Interviews with five practitioners describe the opposite move, shifting "human oversight" away "from line-by-line inspection toward supervisory interpretation" ([arXiv:2608.26316v1](https://arxiv.org/abs/2608.26316v1)). Generating the probe mechanically, as in [bug-discriminating validation evidence](bug-discriminating-validation-evidence.md), changes how the evidence-production stage runs.
- The study's own setting is narrow. The authors note they "used short Python tasks, seeded defects, and a controlled coding agent" ([arXiv:2610.27801v1](https://arxiv.org/abs/2610.27801v1)).

## Example

The study's Billing task shows why the third stage is separate from the second. The agent reconciled a member's charges across approved, refunded, and canceled amounts. "The seeded defect ignored refunds instead of subtracting them." A stage-one check may not expose it. The paper notes: "Generic evaluation, such as rerunning the provided example or asking the agent to check its code, would not necessarily expose this defect." Stage two can pass while stage three still fails. "Even a task-relevant test involving cancelled charges would not reveal it." One probe shape works: "In contrast, testing an approved charge together with an equal refund would expose the error because the balance should be zero" ([arXiv:2610.27801v1](https://arxiv.org/abs/2610.27801v1)).

## Key Takeaways

- Record which stage a review reached. In this study, frequent checking alone did not imply defect resolution.
- The paper suggests, without testing, three directions: "clarify what passing checks establish, highlight untested requirements, and support users in constructing and interpreting task-relevant evidence" ([arXiv:2610.27801v1](https://arxiv.org/abs/2610.27801v1)).
- A correctly built probe can still be misread. In five of 35 instances the participant produced evidence exposing the defect and did not recognize its implication.
- Use the stage record to select an intervention to test. The study ran no intervention, and the nearest guidance experiment found no strong relationship with review performance.
- A final approval step is not oversight on its own: "simply leaving final approval to the user is therefore not sufficient to establish meaningful human responsibility" ([arXiv:2610.27801v1](https://arxiv.org/abs/2610.27801v1)).

## Related

- [Name the Check That Passed Before Accepting AI Code](named-check-over-evaluation-confidence.md) — why the reviewer's confidence cannot stand in for a stage.
- [Reject on a Failing Check, Never Accept on a Passing One](asymmetric-check-evidence.md) — the same asymmetry applied to automated gates.
- [Bug-Discriminating Validation Evidence for Repair Agents](bug-discriminating-validation-evidence.md) — making a probe prove it could have failed.
- [Transcript-Measured Review Coverage](transcript-measured-review-coverage.md) — deriving what a review touched from its trace rather than its report.
- [Defect Visibility as the Unsupervised Review Boundary](defect-visibility-review-autonomy.md) — routing by whether the evidence is decidable from the diff.

## Sources

- [Looks Fine to Me: Understanding Oversight in Agentic Interactions (arXiv:2610.27801v1)](https://arxiv.org/abs/2610.27801v1)
- [Do explicit review strategies improve code review performance?](https://link.springer.com/article/10.1007/s10664-022-10123-8)
- [When Review Alone No Longer Scales (arXiv:2608.26316v1)](https://arxiv.org/abs/2608.26316v1)
