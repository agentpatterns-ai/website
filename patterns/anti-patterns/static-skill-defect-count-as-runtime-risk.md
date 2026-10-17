---
title: "Counting Static Skill Defects as a Runtime Risk Ranking"
term: "Defect Count as Risk Ranking"
description: "Repairing one validated skill-contract defect per task moved verifier pass rate by +0.136, +0.085 and +0.023 across three models, so one audit report is a six-fold different risk depending on who executes the skill."
aliases:
  - static skill defect count as risk
  - skill audit findings count as runtime risk
  - inconsistency count as skill risk ranking
tags:
  - anti-pattern
  - testing-verification
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-16
maturity: emerging
---

# Counting Static Skill Defects as a Runtime Risk Ranking

> A skill audit's defect count ranks artifacts rather than runtime risk, and the same repair list moves one model six times as much as another.

A static audit of 575 agent skills produced 1,182 manually validated contract inconsistencies, present in 67.4% of the 488 GitHub skills and 64.4% of the 87 SkillBench skills ([arXiv:2610.18927v1](https://arxiv.org/abs/2610.18927v1)). That total is what a skill linter prints. It is not a risk ranking, because how much a given inconsistency costs depends on the model that executes the skill. The authors state it plainly: "Static inconsistency counts are thus poor proxies for runtime risk and motivate runtime-aware Skill quality assessment."

## What the paired experiment measured

Forty-nine executable tasks were each built around one confirmed inconsistency and scored by a deterministic verifier, with no LLM judge. Each ran under three conditions and three replicates: no skill, the shipped skill, and a minimally repaired skill ([arXiv:2610.18927v1](https://arxiv.org/abs/2610.18927v1)).

| Model | No skill | Shipped | Repaired | Gain from the repair |
|---|---|---|---|---|
| Claude Haiku 4.5 | 0.534 | 0.741 | 0.877 | +0.136 |
| Qwen3.6-35B | 0.498 | 0.707 | 0.792 | +0.085 |
| DeepSeek-V4-Flash | 0.689 | 0.870 | 0.893 | +0.023 |

Supplying any skill was worth +0.18 to +0.21 for all three models. The gain from repairing the defect ran almost six times higher for Haiku than for DeepSeek ([arXiv:2610.18927v1](https://arxiv.org/abs/2610.18927v1)). One audit report, three risk profiles.

## Why it works

Seeing the defect is not the variable. Across 441 paired executions the agent read the skill in 97.1% of runs, and the per-model rates of 100%, 98% and 93% do not track the repair gains ([arXiv:2610.18927v1](https://arxiv.org/abs/2610.18927v1)). The authors' coding rule names the gap in four words: "contact is not use".

What does line up is adoption. The count of runs where the agent followed the inconsistency into a failed verifier check was 44 for Haiku, 35 for Qwen and 18 for DeepSeek, reproducing the repair-gain ordering exactly. The whole benefit sits in that one class, at +0.366 score points per incident, while every other response class lands within ±0.05 of zero ([arXiv:2610.18927v1](https://arxiv.org/abs/2610.18927v1)). "Fixing a skill pays off exactly when it stops the agent from delivering the inconsistency to the final artifact." A static audit counts files. Runtime harm is a count of executions in which a particular model adopted what it read, and no file carries that number.

## What predicts harm instead

Defect type does. Of the 97 follow-into-failure cases, 41 came from over-promised documentation, where the docs commit to a capability the implementation never provides. Semantic contradictions recovered in 13 of 18 cases: "A contradiction in meaning is noticed and worked around far more often than a promised but absent capability" ([arXiv:2610.18927v1](https://arxiv.org/abs/2610.18927v1)). Where audit effort is rationed, the authors tell skill authors to "prioritize the Document Code boundary, especially cases where documentation promises behavior not supported by the implementation" ([arXiv:2610.18927v1](https://arxiv.org/abs/2610.18927v1)).

## When this backfires

- You already know your model and it recovers well. DeepSeek-V4-Flash gained +0.023 from the whole repair effort, so a runtime triage rig built to rank defects for it costs more than the defects do.
- Your triage harness is built to trigger the defect, as this one was. The authors withdraw the exposure figure themselves: "The high exposure rate observed in RQ3 should therefore be interpreted as a property of controlled defect-exposing tasks rather than as a general exposure rate in practical Skill use."
- You expect the ranking to survive a model swap. The effect is a joint property of the contract and the executing model, so a routing change invalidates the order.
- You expect the repair to pay for itself in tokens. For DeepSeek the inconsistent skill was the cheapest condition at 316k median tokens and 69 seconds, and the repair added 55k tokens and 20 seconds ([arXiv:2610.18927v1](https://arxiv.org/abs/2610.18927v1)). "A fix buys correctness, not compute savings."
- You treat the top-ranked repair as safe. In the 103-run control class where both arms failed, 38 runs improved by +0.352, 37 were unchanged, and 28 got worse by −0.380 ([arXiv:2610.18927v1](https://arxiv.org/abs/2610.18927v1)). "Removing one inconsistency can still mislead the agent by altering the execution path in an unexpected direction."
- Counting is defensible in conventional code, and someone on your team will say so. On Windows Server 2003, Nagappan and Ball report "a strong positive correlation between the static analysis defect density and the pre-release defect density determined by testing" ([Microsoft Research, May 2005](https://www.microsoft.com/en-us/research/publication/static-analysis-tools-as-early-indicators-of-pre-release-defect-density/)). What that predicts is defects found by testing, not task outcomes under an executing model.

## Key Takeaways

- Report the defect count as inventory. Attach a model before you call any part of it risk.
- Exposure does not discriminate between models and adoption does, so a triage signal built on reachability ranks nothing useful.
- Over-promised documentation is the class worth fixing without measuring, at 41 of 97 observed follow-into-failure cases.
- A targeted repair made 28 of 103 control-class runs worse. Re-run the task after fixing, not just the linter.
- Weaker models carry more of the cost, so cheap-model routing raises the price of an unrepaired skill library.

## Related

- [Skill Lift: Measuring What a Skill Adds at Runtime](../../verification/skill-lift.md) — the paired with-skill and without-skill measurement, where this page's comparison is repaired against shipped.
- [Skill File Linting: Which Three Checks to Run First](../../instructions/skill-file-linting.md) — the static gate whose output this page tells you how to read.
- [Treating a Clean Static Scan as Security Evidence](static-clean-as-security-evidence.md) — the same gap on the security axis, where a cleared file is not a cleared behavior.
- [Repository Skill Release Drift](repository-skill-release-drift.md) — how a skill acquires these inconsistencies over time as the release it was distilled from moves.
- [Skill Over-Trust](skill-over-trust.md) — what the agent does with a skill it should have questioned, which is the adoption step this page measures.
