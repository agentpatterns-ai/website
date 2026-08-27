---
title: "Skill Lift: Measuring What a Skill Adds at Runtime"
term: "Skill Lift"
description: "Skill Lift is the paired difference between a run with a skill and a run without it. Static review scores do not predict it, so the two gates answer different questions."
aliases:
  - runtime skill lift measurement
  - paired with-skill and baseline trials
  - skill lift release gate
tags:
  - testing-verification
  - evals
  - skills
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-24
maturity: emerging
---

# Skill Lift: Measuring What a Skill Adds at Runtime

> Skill Lift is the paired difference between a run with a skill available and the same run with it withheld.

The baseline arm is not an empty workspace. Configured prerequisite, helper, reference, and decoy skills stay fixed and only the target skill is withheld, which is what makes the delta attributable to that skill ([arXiv:2608.20614v1](https://arxiv.org/abs/2608.20614v1)). Cost then scales with the whole registry: `N skills × K agents × C cases × A attempts × 2 conditions` needs up to 2NKCA container runs, so the measurement belongs on release candidates and high-risk skills rather than on every edit ([arXiv:2608.20614v1](https://arxiv.org/abs/2608.20614v1)).

## When the number means anything

Three conditions have to hold before a lift figure carries weight.

- Repeats per cell. The default evaluator suite combines a trace-level security metric, two deterministic skill-use metrics, and three LLM or RAGAS judges, each carrying an equal one-sixth weight in the default composite ([arXiv:2608.20614v1](https://arxiv.org/abs/2608.20614v1)). Half the composite therefore moves with model judgment. Single-trial LLM judging flips 13.6% of pairwise preferences on re-run, and recovering a 50-trial reference verdict with 95% probability took 11 repeated trials on average, rising to 15 on high-variance questions ([arXiv:2606.13685v1](https://arxiv.org/abs/2606.13685v1)). The ACES corpus itself is thinner than that: of 201 production skill-agent cells, 88 have two paired trial files and 113 have one, and among the repeated cells the median within-cell lift standard deviation is 0.0319 ([arXiv:2608.20614v1](https://arxiv.org/abs/2608.20614v1)).
- A workspace pinned at production size. Mean overall lift stays flat at 0.133 to 0.149 across 1 to 20 visible skills, while mean wall time climbs from 258 seconds to 451. At 50 visible skills the with-skill pass rate drops to 0.55 and wall time reaches 1,290 seconds ([arXiv:2608.20614v1](https://arxiv.org/abs/2608.20614v1)). Measure at a skill count you actually ship, or you are grading routing pressure.
- A comparable skill category. That corpus skews toward System Access, Deployment, Platform, and Data Infra work, and its authors decline to claim the same lift distribution for Troubleshooting, Dev-Tooling, or creative skills ([arXiv:2608.20614v1](https://arxiv.org/abs/2608.20614v1)).

## Why it works

A scan reads the artifact. The thing you want predicted is a property of the interaction between that artifact, a model, a workspace, and a task, so the file cannot carry it. Five failure classes make the gap concrete: the agent never discovers the skill, invokes the wrong script or arguments, reports correct output incorrectly, collides with a skill already in the workspace, or is silently regressed by a model update that changes how it reads the documentation ([arXiv:2608.20614v1](https://arxiv.org/abs/2608.20614v1)). None is visible in the document. The paper's analogy is compiling with `-Wall -Werror`: no warnings does not mean the program does what it should.

The paired design removes the confounds by construction, holding task, harness, model, scorer, sandbox, and every non-target skill fixed so the arms differ in one thing. On 62 production skills with matching scan metadata, structural score correlates with live lift at Spearman ρ = −0.0181 and the LLM-judge rubric score at ρ = −0.0266, and the largest process gains land in skill execution, behavior check, and skill efficiency ([arXiv:2608.20614v1](https://arxiv.org/abs/2608.20614v1)).

## When this backfires

- You read the near-zero correlation as proof that review is pointless. Those coefficients sit on 62 skills with Fisher-z intervals of [−0.2667, 0.2327] and [−0.2745, 0.2247], which the authors read as no useful monotonic proxy in those particular scores rather than a negative relationship. The same authors put it plainly — "Scanning is necessary, not sufficient" — and report that "document scanning surfaces real authoring issues, but neither scan-only axis observes discovery, tool use, workflow order, or task success" ([arXiv:2608.20614v1](https://arxiv.org/abs/2608.20614v1)).
- You set a fixed lift floor and let it retire skills. A stronger base model raises both arms, so lift shrinks while absolute task performance improves ([arXiv:2608.20614v1](https://arxiv.org/abs/2608.20614v1)). Re-baseline after a model update instead of deleting the skill.
- The skill reaches endpoints the sandbox cannot. Skills calling enterprise services behind a VPN get network errors in the container, so absolute goal-accuracy figures are a lower bound even though the paired delta survives ([arXiv:2608.20614v1](https://arxiv.org/abs/2608.20614v1)).
- You expect a portable score. Adding or removing a skill shifts routing pressure, context allocation, and competition with siblings, so the result is a marginal contribution under one declared workspace ([arXiv:2608.20614v1](https://arxiv.org/abs/2608.20614v1)). Harness means in that study ranged from 0.0896 to 0.3611 over the same skill set.

## Example

Across 145 skills from enterprise repositories and public catalogs, 94.5% cleared the default structural gate and 86.2% passed an LLM-judge rubric, yet the two scores agreed with each other at only Spearman ρ = 0.14. The same corpus showed 99.3% of skills failing to declare `tools` in frontmatter and 97.9% omitting a Limitations section, which the authors summarize as a frontmatter contract that is aspirational rather than enforced ([arXiv:2608.20614v1](https://arxiv.org/abs/2608.20614v1)).

Running the live layer on the production subset gave a different picture. Across 947 scored paired cases from 58 skills and four harnesses, mean composite Skill Lift was 0.2134 with a 95% interval of [0.1967, 0.2301], built from condition means of 0.7460 with the skill and 0.5326 at baseline. Lift was positive in 689 cases, zero in 171, and negative in 87. The authors treat those 87 as review targets rather than noise, because a paired run turns a regression into a traceable comparison between the two arms, and the cleaner negative cases show the agent finding the skill and then producing a truncated response, skipping verification, or spending extra tool calls without improving the answer ([arXiv:2608.20614v1](https://arxiv.org/abs/2608.20614v1)). An open-source implementation runs the same three tiers, where Tier 1 asks "Safe & well-formed?", Tier 2 asks "Overlap with what exists?", and Tier 3 asks "Does it help the agent?" ([NVIDIA/SkillEvaluator](https://github.com/NVIDIA/SkillEvaluator)).

## Key Takeaways

- Skill Lift is a paired delta under a fixed task, harness, model, scorer, and workspace, not a portable property of the skill file.
- A clean scan is not weak evidence of runtime value. On 62 production skills it correlated with live lift at ρ = −0.0181, which is no evidence either way.
- Budget repeats before you trust a cell. One paired trial sits inside the noise band of a model-judged metric.
- Pin the visible-skill count to what you ship; at 50 skills the with-skill pass rate falls to 0.55 and the measurement becomes a routing test.
- Keep both gates. Scans run per change and catch authoring defects; live trials run on release candidates and catch discovery, routing, and collision failures.

## Related

- [Skill Evals](skill-evals.md) — how to build the paired with-skill and baseline runner and its labeled dataset, which this page treats as given.
- [Skill Test Coverage as a Release Gate](skill-test-coverage-release-gate.md) — the adequacy floor asking which specified behaviors any test exercises, complementary to how much a skill adds.
- [Emulated APIs for Agent Skill Evals](emulated-apis-for-skill-evals.md) — keeps live-data mutation and API cost out of the paired score when the skill under test calls real endpoints.
- [Seed-Variance Reporting and Measurable-Range Eval Design](seed-variance-reporting.md) — what to report when the number moves with the run, which is the failure mode single-trial lift walks into.
- [Skill Authoring Patterns](../tool-engineering/skill-authoring-patterns.md) — the description and structure work a scan gate can actually improve.
