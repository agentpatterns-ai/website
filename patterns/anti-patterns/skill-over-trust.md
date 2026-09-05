---
title: "Skill Over-Trust: Treating Topical Relevance as Evidence a Skill Helps"
term: "Skill Over-Trust"
description: "A topically matched skill is the usual source of skill-induced agent failures; attribute the cost by re-running the same task with the skill withheld."
aliases:
  - topically matched skill over-trust
  - skill-induced failure attribution
  - withheld-skill re-run
tags:
  - anti-pattern
  - agent-design
  - skills
  - cost-performance
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-13
maturity: emerging
---

# Skill Over-Trust: Treating Topical Relevance as Evidence a Skill Helps

> Skill-induced agent failures usually trace to a topically matched skill, so withhold the skill and re-run the same task to attribute the cost.

Skill over-trust is accepting that a loaded skill helped because its subject matched the task. A study of 307 skill-induced failures across two benchmarks, 125 functional failures and 182 efficiency regressions, reports that "skill induced functional failures are rarely caused by obviously irrelevant skills; instead, seemingly relevant skills often make the agent incorrectly implement or omit task-required implementation elements" ([Dong et al., 2026](https://arxiv.org/abs/2608.11888v1)).

## Conditions this applies under

- A skill pool wide enough to supply a semantically matched alternative for the reference run. The study built one by searching smithery.ai and skillsmp.com and keeping candidates above 0.7 cosine similarity alongside each benchmark's curated skill ([Dong et al., 2026](https://arxiv.org/abs/2608.11888v1)). Curation moves results the other way, raising average SkillsBench pass rates from 33.9% to 50.5% ([Li et al., 2026](https://arxiv.org/abs/2602.12670v4)).
- A deterministic verifier, so the skill run can fail a check the reference run passes. On tasks graded by judgement, one paired run cannot separate a skill effect from run-to-run variance.
- Tool feedback thin enough that the skill does real work. Where tools return strict, schema-validated, low-latency observations, the environment supplies the correction instead: one offensive-security study measured a gap of 8.9 percentage points between no-skill and full-skill conditions at p=0.71 ([Chacko et al., 2026](https://arxiv.org/abs/2605.20023v2)).

## What the failures look like

The 307 cases split by category ([Dong et al., 2026](https://arxiv.org/abs/2608.11888v1)):

| Failure | Cases | Shape |
|---|---|---|
| Task-implementation fault | 86 of 125 | Element implemented wrongly (46), required element omitted (36), obstructive workflow guidance (4) |
| Artifact misplacement | 24 of 125 | Right artifact, wrong path or integration point |
| Environment mismatch | 13 of 125 | Broken dependencies (5), environment-state conflicts (8) |
| Applicability mismatch | 2 of 125 | Skill did not apply to the task at all |
| Excessive procedure | 114 of 182 | Excessive verification (67), heavy pipelines (30), excessive exploration (17) |
| Context bloat | 46 of 182 | Mandatory skill-body text accounts for 43 of the 46 |
| Dependency resolution | 22 of 182 | Fragile or incompatible runtime dependencies |

The first four rows are functional failures, the last three efficiency regressions. Procedure outweighs context by more than two to one, so prompt length is the smaller half of the cost story.

## Why it works

Skill text arrives as authoritative procedure. The study names the cause: "the agent over-trusts a topically matched skill and treats its reusable defaults, examples, or templates as task-specific requirements" ([Dong et al., 2026](https://arxiv.org/abs/2608.11888v1)).

Cost has a second mechanism: skill bodies are mandatory, not optional. Context overhead is "almost entirely caused by mandatory skill-body text (43 of 46 context-overhead cases)", and procedure cost follows because "skills often turn validation checklists and construction recipes into mandatory work" ([Dong et al., 2026](https://arxiv.org/abs/2608.11888v1)). A checklist written as reference becomes work performed every run.

## Attributing a regression to a skill

Differential analysis pairs two runs of the same task ([Dong et al., 2026](https://arxiv.org/abs/2608.11888v1)):

1. Run the task with the skill loaded. Record the verifier result, token count, and wall time.
2. Run it again with the skill withheld, or with a semantically matched alternative skill.
3. Call it a functional failure when the skill run fails the verifier and the reference run passes.
4. Call it an efficiency regression when both runs pass, both metrics rise, and at least one rises by 2x.

Requiring both metrics to move filters out the token-for-time trades ordinary variance produces.

## When this backfires

- The bottleneck is retrieval, not the skill body. When agents must find their own skills in a 34,000-skill collection, gains "degrade consistently as settings become more realistic"; retrieval and refinement moved Terminal-Bench 2.0 for Claude Opus 4.6 from 57.7% to 65.5% ([Liu et al., 2026](https://arxiv.org/abs/2604.04323v1)).
- The paired run costs more than the regression it finds.
- The evidence is single-harness: all 307 cases come from Claude Opus 4.6 on OpenCode 1.15.1 ([Dong et al., 2026](https://arxiv.org/abs/2608.11888v1)). A harness that loads skill bodies on demand changes the context-bloat mechanism outright.
- The study samples failures, so it carries no denominator and says nothing about how often skills help.

## Example

A retrieval-augmented generation task required configurable model parameters. The loaded skill's example "shows retrieval parameters such as chunk size, overlap, and top-k, but does not show how to configure model parameters", and the agent followed the partial example instead of the complete task specification ([Dong et al., 2026](https://arxiv.org/abs/2608.11888v1)). This is the paper's central shape: an on-topic skill, not an obviously irrelevant one, whose example was narrower than the task.

## Key Takeaways

- Judge a skill by a paired run, not by whether its subject matches the task.
- Spend the withheld-skill re-run only where a deterministic verifier exists; elsewhere the result is variance.
- Audit skills for mandatory verification steps and construction recipes before trimming prose for length.
- Keep the reviewed skill set small. Curation is the one intervention measured here that moves pass rates upward.

## Related

- [Assuming Loaded Skills Stay Enforced in Long Contexts](assuming-loaded-skills-stay-enforced.md) — the adherence half: a correctly loaded skill's obligations drop out as the trajectory grows.
- [Agent Extension Conflicts](agent-extension-conflicts.md) — degradation from installing many extensions together, rather than from one matched skill.
- [Cost-Aware Skill Rewriting](../../instructions/cost-aware-skill-rewriting.md) — why shortening a skill can raise total cost when it strips operational anchors.
- [Skill-Use Gates: Trigger, Compliance and Boundary](../../verification/skill-use-gate-decomposition.md) — scoring which gate a skill failure came from.
- [The No-Op Test](../../instructions/behavioral-no-op-test.md) — deleting a line and rerunning the task to test whether it changes behavior.
- [Judging a Skill's Honesty by the Validity of Its Output](judging-skill-honesty-by-output-validity.md) — the same withheld-skill comparison pointed at policy integrity instead of cost and failure attribution.
