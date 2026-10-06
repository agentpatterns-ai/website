---
title: "Pre-Execution Skill Selection: Layers Over Install Counts"
term: "Pre-Execution Skill Selection"
description: "Among agent skills that are all already popular, install counts barely predict task performance. Read four layers of the skill file instead."
aliases:
  - MCRI framework
  - skill shortlisting before execution
  - marketplace popularity as a skill signal
tags:
  - instructions
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-05
maturity: emerging
---

# Pre-Execution Skill Selection: Layers Over Install Counts

> Among skills that are all already popular, stars, downloads, and install counts barely predict how a skill performs on your task.

Pre-execution skill selection is shortlisting candidate skills by reading their contents, before you spend tokens running any of them. One study drew on 63,812 skills from the OpenClaw skill Hub. Scored against measured downstream performance, community popularity produced Spearman correlations between −0.1557 and 0.0679 on three benchmarks, none reaching p<0.05 ([arXiv:2610.01506v1](https://arxiv.org/abs/2610.01506v1)). Among candidates that have all already cleared the popularity bar, the registry counts are not a tie-breaker.

## When this applies

That null result was measured inside a pool already filtered for popularity. The authors took the top 3% of skills by average daily downloads. They matched those to benchmarks, leaving 133 candidates for BFCL-Fundamental, 83 for BigCodeBench, and 75 for Mind2Web ([arXiv:2610.01506v1](https://arxiv.org/abs/2610.01506v1)). Two conditions follow.

- Every candidate on your shortlist is already popular. Across the whole hub most community metrics are zero, and the authors found that differences among tail samples "contain substantial noise" ([arXiv:2610.01506v1](https://arxiv.org/abs/2610.01506v1)). They filtered to the top 3% for that reason. The paper does not test whether counts help on an unfiltered pool.
- A better ordering is all you are buying. The paper reads its own downstream evidence as "improved prioritization within concentrated candidate pools, rather than as a large increase in absolute task accuracy", and says the method "cannot replace execution-based evaluation" ([arXiv:2610.01506v1](https://arxiv.org/abs/2610.01506v1)). Top-1 pass rate on BFCL-Fundamental moved from 79.60% to 80.67%.

## What to read in the file

The MCRI framework names four layers, each scored 1–5 ([arXiv:2610.01506v1](https://arxiv.org/abs/2610.01506v1)):

| Layer | The question it answers |
|---|---|
| Metadata | Can the host agent tell what this does and when to invoke it? |
| Constraints | Which behaviors does it rule out: prohibitions, preconditions, invariants? |
| Resources | What task-specific information does it supply that the model lacks? |
| Instructions | How is execution organized, and what may it call? |

Score with the task in hand. The aggregate scorer received the task description alongside the four dimension scores, and reached ρ = 0.2119, 0.3355, and 0.3611 against measured performance on BFCL-Fundamental, BigCodeBench, and Mind2Web. Among the eight selectors compared it was "the only method whose positive association is significant in all three" ([arXiv:2610.01506v1](https://arxiv.org/abs/2610.01506v1)).

Two cheaper proxies failed. Character count predicted outcomes on BigCodeBench (ρ=0.2658, p=0.0152) and nowhere else, so it "does not support the general rule that longer skills are better". File count ran significantly negative on BFCL-Fundamental (ρ=−0.2237, p=0.0096), under a harness that "injects skill documents as text without executing bundled scripts" ([arXiv:2610.01506v1](https://arxiv.org/abs/2610.01506v1)).

## Why it works

Popularity and task fit measure different things. A skill helps through two mechanisms the paper names. The first is information gain, where "the skill expands the model's effective knowledge with task-relevant external information". The second is behavioral constraint, where "it increases the consistency with which a capable model selects the target path across repeated invocations" ([arXiv:2610.01506v1](https://arxiv.org/abs/2610.01506v1)). An install count sums exposure across every task anyone ever pointed the skill at, so it cannot report whether this skill carries what your task needs. Reading the layers asks that directly. The authors reconcile their two findings themselves. Their scores do track ecosystem popularity, and that does not conflict with popularity's weak downstream signal, "because popularity and task-specific post-injection performance are distinct criteria".

Splitting the judgment into four dimensions also steadies it. Averaged over the three benchmarks, the structured method "reduces the standard deviation by 67.5% relative to the Baseline and by 74.3% relative to the Full-text Holistic Baseline" ([arXiv:2610.01506v1](https://arxiv.org/abs/2610.01506v1)).

## When this backfires

- Your scorer never sees the task. A separate study scanned 62 production skills and compared two document scores against measured runtime lift. The structural score tracked it at Spearman ρ=−0.0181 and an LLM-judge rubric at ρ=−0.0266. Those authors read this as no useful monotonic runtime proxy rather than evidence of a negative relationship ([arXiv:2608.20614v1](https://arxiv.org/abs/2608.20614v1)). Both tiers read the skill document without running it. Whether task conditioning is what separates the two studies is untested.
- The harness executes bundled scripts. That negative file-count finding is attributed to text-only injection, so it does not carry over.
- Candidates are few, or their outcomes are already far apart. Percentile reporting exists because outcomes were tightly packed: on BFCL-Fundamental, pass rate "ranges from 73.33% to 83.33%, with mean 79.15% and standard deviation 2.17 percentage points" ([arXiv:2610.01506v1](https://arxiv.org/abs/2610.01506v1)). With three visibly different candidates, scoring four layers buys nothing.
- You treat the shortlist as a verdict. The paper's own reading is that "injecting an arbitrary skill is not uniformly beneficial, while selecting a task-suitable skill can improve the outcome relative to using no skill" ([arXiv:2610.01506v1](https://arxiv.org/abs/2610.01506v1)).
- Reproduction matters to you. The paper's resources directory "is not included in this preprint's source package, and no public repository URL is provided in this version" ([arXiv:2610.01506v1](https://arxiv.org/abs/2610.01506v1)).

## Example

Rank order is where the gain shows up; the raw percentages barely move. On Mind2Web the structured method's top pick scored 57.39% Step Success Rate against 56.23% for the strongest baseline, a little over one point. Converted to percentile of the candidate pool that is 99.32 against 79.73, a gap of 19.59. The corresponding gaps were 22.80 on BFCL-Fundamental and 17.68 on BigCodeBench ([arXiv:2610.01506v1](https://arxiv.org/abs/2610.01506v1)).

Keep the no-skill reference in view. With no skill injected, BFCL-Fundamental scored 80.00%, at the 54.00 percentile of the skill-injected distribution; Mind2Web scored 52.17%, at 6.05 ([arXiv:2610.01506v1](https://arxiv.org/abs/2610.01506v1)). The paper reads that spread as its case for pre-execution selection.

## Key Takeaways

- Inside an already-popular candidate pool, no community signal in the study reached significance against task performance; the range was −0.1557 to 0.0679.
- Give the scorer your task description. The two studies differ on this, though nothing tests it directly.
- Four questions to put to a skill file: can the host identify it, what does it forbid, what does it supply, and how does it execute.
- What you get is a shortlist for execution-based evaluation. Absolute top-1 gains were around one percentage point.
- Character count and file count are not shortcuts. Each reached significance on one benchmark only, and the file-count result was negative.

## Related

- [Skill Lift: Measuring What a Skill Adds at Runtime](../verification/skill-lift.md) — the execution-based measurement a shortlist feeds, and the source of the counter-evidence above.
- [Skill Packs: Registry Distribution Needs Pinning Discipline](skill-pack-registry-distribution.md) — what a team adds once a registry skill is chosen: a version pin, a review gate, a size limit.
- [Skill File Linting: Which Three Checks to Run First](skill-file-linting.md) — deterministic checks on a SKILL.md, which catch authoring defects rather than task fit.
- [Coverage-Aware Skill Selection Under a Token Budget](../context-engineering/coverage-aware-skill-selection.md) — choosing a whole loadout under a budget, where complementarity between skills decides the pick.
- [Contractual Skill Files](contractual-skill-files.md) — writing the constraints and interface that a reader of the file is looking for.
