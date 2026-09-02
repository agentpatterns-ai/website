---
title: "Repository Skill Release Drift"
term: "Repository Skill Release Drift"
description: "A skill distilled from one release keeps giving obsolete guidance once a release moves what it pins, and the agent executes it rather than reading it. Six frontier models score 29.9% to 69.7% F1 at bringing one back up to date."
aliases:
  - repository skill staleness
  - silent skill decay
  - release-coupled skill drift
tags:
  - anti-pattern
  - instructions
  - skills
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-25
maturity: emerging
---

# Repository Skill Release Drift

> A skill that pins release-specific APIs and paths goes obsolete when a release moves them, with no signal, and the agent executes it anyway.

Two conditions have to hold before a skill decays without warning. The skill pins release-specific detail — an API signature, a script path, a config key — and nothing checks those references against the current release ([Duan et al., 2026](https://arxiv.org/abs/2608.21964v1)). Meet both and the skill keeps handing the agent confident, obsolete guidance after the repository moves on.

## The pattern

Distilling repository knowledge into a skill pays. On the five weakest-baseline repositories in one 2026 study, the skill alone raised mean utility from 4.48 to 8.46 ([Duan et al., 2026](https://arxiv.org/abs/2608.21964v1)). The skill then sits in the repo with no record of the release it was distilled from. A later release renames a function or moves a script, and nobody edits the skill, because nothing asked them to. Duan et al. prescribe the missing piece: repository skills "should be treated as versioned knowledge assets that carry the release they were distilled from" ([arxiv 2608.21964v1](https://arxiv.org/abs/2608.21964v1)).

## Why it works

An agent executes a skill rather than reading it. A wrong path in a README makes a human pause. The same line in a skill drives an action against the repository, so the failure arrives as a plausible wrong result instead of an error. The authors name the causal shape: "the same version specificity that makes a skill useful also makes it fragile: after a release, it may become stale without raising any explicit signal, while continuing to provide obsolete guidance" ([Duan et al., 2026](https://arxiv.org/abs/2608.21964v1)).

The counter-move with evidence behind it is a contract, not a review ritual. Fan et al. extract executable environment contracts from skill documents and check only the assumptions carrying an operational role: "a version string in a comment is noise; the same string in a pinned dependency is an operational obligation". That precision buys zero false alarms over 599 no-drift and hard-negative cases, against 40% false positives from contract-free CI probes ([Fan et al., 2026](https://arxiv.org/abs/2605.10990v1)).

## Repair is the expensive half

Six frontier models were asked to bring a stale skill set up to a new release. They scored between 29.9% and 69.7% avg@3 macro removal F1, across 105 release transitions from 57 public GitHub repositories. Locating the affected files accounts for most of that gap: coverage correlates with F1 at r=0.650, and full-coverage runs average 67.3% F1 against 41.0% for partial coverage. Handed the gold file paths, the best model still reaches only 62.3% F1 on that subset ([Duan et al., 2026](https://arxiv.org/abs/2608.21964v1)).

## When this backfires

- Stable repositories. The corpus excluded every transition whose obsolete set was empty ([Duan et al., 2026](https://arxiv.org/abs/2608.21964v1)), so it says nothing about how often a release breaks a skill. Where APIs and scripts hold steady, a per-release review returns nothing for real reviewer time.
- Skills that anchor procedure rather than pin versions. Procedural anchoring accounts for 65.7% of skill cases against 4.5% for explicit knowledge injection ([Jiang et al., 2026](https://arxiv.org/abs/2608.14036v1)). "Run the suite before opening a PR" carries nothing a release can invalidate.
- Unreviewed automated updating. GPT-5.4 pairs high file coverage with a removal load of 2.84, stripping guidance outside the stale set, and three of the six models sit below 50% F1 ([Duan et al., 2026](https://arxiv.org/abs/2608.21964v1)).
- Large skill pools, where retrieval is a separate bottleneck. Actual-use precision falls from 29.6% to 3.3% as the pool grows from 5 skills to 100, while downstream success moves only from 36.4% to 39.3% ([Jiang et al., 2026](https://arxiv.org/abs/2608.14036v1)). Per-release review does not touch retrieval, and retrieval work does not make a stale skill correct. Budget both rather than trading one against the other.

## Key Takeaways

- Record the release each skill was distilled from. That one line turns "is this stale?" into a diff you can run over the release range.
- Check role-bearing assumptions, not every value the skill mentions. Contract-free CI probes produce 40% false positives ([Fan et al., 2026](https://arxiv.org/abs/2605.10990v1)).
- Do not let a model rewrite a stale skill unsupervised. Removal F1 tops out at 69.7%, and the model with the best file coverage over-edits at a removal load of 2.84 ([Duan et al., 2026](https://arxiv.org/abs/2608.21964v1)).
- Retrieval and freshness are separate bottlenecks, not a priority order. Precision collapses as the pool grows while downstream success barely moves, and the authors conclude that "exact ground-truth skill invocation is neither sufficient nor strictly necessary for success" ([Jiang et al., 2026](https://arxiv.org/abs/2608.14036v1)).
- Treat the maintenance difficulty as measured and the base rate as open. The benchmark excluded every release transition that broke no skill ([Duan et al., 2026](https://arxiv.org/abs/2608.21964v1)).

## Related

- [Stale AI Configuration Artifacts (Context Rot)](stale-ai-configuration-artifacts.md) — the adjacent failure, measured between a config file and the code it describes rather than across a release boundary
- [Skill Reuse as Vendored Forking](../../tool-engineering/skill-reuse-as-vendored-forking.md) — the third drift axis: a copied skill diverging from its upstream source
- [Plugin Component Co-Change](../../instructions/plugin-component-co-change.md) — the fourth axis: a skill diverging from the script bundled beside it in the same plugin
- [Skill Library Technical Debt](../../tool-engineering/skill-library-technical-debt.md) — library-level defects that no single-skill eval catches, including stale clones
- [Skill Over-Trust](skill-over-trust.md) — a topically matched skill is not evidence the skill helps, stale or fresh
- [Belief Inertia After Tool-Map Drift](belief-inertia-after-tool-map-drift.md) — what an agent does when the surface it memorized changes underneath it
