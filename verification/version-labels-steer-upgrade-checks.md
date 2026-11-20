---
title: "Version Labels Steer How Hard Agents Check Upgrades"
term: "Version Label Steering"
description: "In one vendor experiment a patch label led some models to skip checks on a breaking upgrade; three models checked every time. A required CI check removes the dependence."
tags:
  - testing-verification
  - agent-design
  - tool-agnostic
last_reviewed: 2026-11-19
maturity: emerging
---

# Version Labels Steer How Hard Agents Check Upgrades

> In one vendor test, the version label changed how hard some agents checked a breaking upgrade; others checked every time.

Some models let the version label set how hard they check a dependency upgrade. Microsoft ran one breaking change under a patch label and a major label with byte-identical library code ([Mastykarz, 2026](https://devblogs.microsoft.com/blog/do-ai-coding-agents-care-about-semver/), "Same code, different version number"). Claude Sonnet 5.5 ran the tests or read the new code in 2 of 10 runs under the patch label and 10 of 10 under the major label. That is n=10 per label. In the post's second experiment the same model's gap, 4 of 30 unchecked merges against 0 of 30, is rated "Inconclusive, leaning toward an effect". The evidence is one vendor blog post: a made-up library, a deliberately mislabeled break, small apps, no release notes, and no published fixtures or trajectories. The page cites no independent replication of the label result.

## What the two experiments found

Experiment 1 counted a run as checked if the agent ran the tests or app, or read the updated library code. Experiment 2 asked the agent to review an update branch and merge it if good: six scenarios, three breaking, 30 runs per label per model, 540 runs. The post set its effect threshold at 25 percentage points before running ([Mastykarz, 2026](https://devblogs.microsoft.com/blog/do-ai-coding-agents-care-about-semver/)).

| Model | Experiment 1: checked, patch / major | Experiment 2: unchecked merges, patch / major |
|-------|-------|-------|
| Claude Sonnet 5.5 | 2/10, 10/10 (effect) | 4/30, 0/30 (inconclusive) |
| Claude Haiku 5.5 | not run | 11/30, 2/30 (effect) |
| GPT-6 Luna | not run | 9/30, 5/30 (inconclusive) |
| Claude Opus 5.5, GPT-6.1 Sol, GPT-6.1 Terra | 70/70, 70/70 | 0/30, 0/30 |

The aggregate rate fell from 13% to 9% to 4% across patch, minor, and major labels (180 runs per label). Three of the six models contributed no unchecked merges, so three models produce the whole gradient. Within Claude 5.5 the smaller model was swayed more. Agents merged breaking updates in 13 of 270 runs, and 4 of those 13 left main broken: two by Haiku 5.5 and two by GPT-6 Luna, all under a patch or minor label.

## Why it might happen

The post offers a hypothesis, not a test: models trained on SemVer-saturated repositories may have absorbed the habit that a major release deserves a careful look. Every model, including the three that always checked, talked about compatibility more often under a major label. A related study finds the same class of effect in security review, where presentation overrides content ([Alexopoulos et al., 2026](https://arxiv.org/abs/2603.18740v5)). It tests framing in pull request metadata and not version labels, so it supports the mechanism and does not replicate this result.

## When this backfires

- A required CI gate already covers the branch. The agent's own check is then redundant, and the damage in the post was small (4 broken-main merges across 270 runs of breaking updates).
- The reviewing model ignores the label. Opus 5.5, Sol, and Terra checked under every label. The post warns that the next model you switch to might not.
- Real releases usually come with release notes, which the experiments left out, and most patch releases are what they claim to be.
- The break is behavioral. The fixture renamed a function, which a test that calls it catches. A required check helps only if the tests exercise the changed code.

## Why the label is a weak signal

In an npm study, about 14% of dependent releases were hit by a breaking change in non-major updates of their dependencies, and 44% of manifesting breaking changes came in minor and patch releases ([Venturini et al., 2023](https://arxiv.org/abs/2301.04563v1)). [Delegating Dependabot Pull Request Triage to an Agent](../workflows/dependabot-pr-triage-delegation.md) covers the semver delta as a publisher claim; this page adds the measured effect on the agent's verification.

## What to do

1. Make a CI status check required on every dependency-update branch, whatever the semver delta, before any agent or bot may merge. In GitHub, put the test job in the branch ruleset's required checks.
2. If you scope auto-merge by update type, keep the label as a candidate filter only.
3. In evals, run each dependency scenario under a patch and a major label on the models your developers use, and read the trajectories. A run that bumped a patch and got lucky passes like a run that checked.

## Key Takeaways

- The label changed behavior for some models and not for others, so the model that reviews your dependency branches decides the risk.
- Read each figure with its denominator: n=10, n=30, and three models at zero.
- A required check makes verification depth a property of the workflow instead of the model's reading of a version string.

## Related

- [Delegating Dependabot Pull Request Triage to an Agent](../workflows/dependabot-pr-triage-delegation.md)
- [Routing Dependency Updates to Repair Agents by Budget](../workflows/dependency-update-repair-routing.md)
- [Enforced Versus Advisory Controls in LLM-Native IDEs](../security/enforced-versus-advisory-controls.md)
- [Verification-Gated Agent Autonomy via Automated Review](../patterns/agent-design/verification-gated-agent-autonomy.md)
- [Eval Blind Spots: Structural Gaps in Measurement Methodology](eval-blind-spots.md)
- [Pressuring a Coding Agent Degrades the Code It Writes](../patterns/anti-patterns/pressured-prompt-framing.md)
- [Risk-Based Shipping: Review by Risk Matrix, Not by Default](risk-based-shipping.md)
- [Why Coding Agents Leave Dependency Upgrades Half Migrated](dependency-upgrade-repair-completeness.md)
