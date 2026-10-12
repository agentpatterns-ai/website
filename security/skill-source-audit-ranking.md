---
title: "Ranking Skill Sources for Review by Copy Out-Degree"
term: "Skill Source Audit Ranking"
description: "Auditing the 100 repositories a copy-network model ranks highest prevents 14.9% of later high-risk skill adoptions. The 100 most starred prevent 0.5%."
aliases:
  - skill source audit ranking
  - copy out-degree ranking
  - skill audit targeting
tags:
  - security
  - tool-agnostic
  - skills
  - supply-chain
  - arxiv
last_reviewed: 2026-10-10
maturity: emerging
---

# Ranking Skill Sources for Review by Copy Out-Degree

> Stars are nearly uninformative about which repositories spread a skill. Current copy out-degree identifies 4.0 times as many later transmissions.

Skill source audit ranking orders repositories for security review by how many skills they have passed to others, rather than by how popular they are. Seddik reconstructed a dated, directed copy network from the git history of every `SKILL.md` in GitSkills, covering 2,193,119 skill adoptions across GitHub. Reviewing the 100 repositories that network's source-choice model ranks highest "prevents 14.9% of later adoptions of high-risk skills, against 0.5% for the 100 most starred" ([Seddik, 2026](https://arxiv.org/abs/2610.11169v1)).

## When this applies

Three conditions decide whether the ranking repays the work.

- The skills arrived as copies. A [registry install that resolves to a tag](../instructions/skill-pack-registry-distribution.md) already carries a version you can bump.
- You can see who holds which skill across more than one repository. The ranking is a property of a graph, and a single checkout is not one.
- You want to reduce future adoptions rather than certify the copies you already hold. The ranking does the first job only.

One owner, one repository, five skills: skip it. A consistent change moves every copy of a skill to the same next version. A single owner raises the odds of one 3.32-fold, controlling for group size, platform and content ([Seddik, 2026](https://arxiv.org/abs/2610.11169v1)). With one repository there is no copy network to rank.

## What the ranking buys, and where it stops

Ranked before the 1 April 2026 split, "current copy out-degree identifies 4.0 times as many later transmissions as stars, and PageRank and the number of skills held perform comparably" ([Seddik, 2026](https://arxiv.org/abs/2610.11169v1)). The ordering survives moving the split to 1 March or 1 May.

The same paper bounds what that buys.

- The ceiling is low. "Even a ranking chosen in hindsight prevents only about a quarter of them, because roughly half arrive as new skills" ([Seddik, 2026](https://arxiv.org/abs/2610.11169v1)). No ranking of repositories reaches a skill that does not exist yet.
- Flagged skills are not the ones spreading fastest. They "reach fewer repositories than a uniform permutation null predicts (28.6% against 41.1%)" ([Seddik, 2026](https://arxiv.org/abs/2610.11169v1)).
- The ranking names distributors. Its rule credits the earlier adopter of the most lineages, usually a catalog, and matches the source an installer recorded in only 26.7% of cases. "Source-level measures therefore describe distribution rather than authorship" ([Seddik, 2026](https://arxiv.org/abs/2610.11169v1)).

## Why it works

Copying delivers a snapshot with no return channel. Skills "form a software supply chain built from copies, lacking a registry that records provenance, a version that can be pinned and a channel that delivers fixes" ([Seddik, 2026](https://arxiv.org/abs/2610.11169v1)). An edit at the source has no path to the copy. "Copied code files adopt upstream security fixes in 47% to 84% of cases"; skill copies manage 20.9% ([Seddik, 2026](https://arxiv.org/abs/2610.11169v1)). [Skill Reuse as Vendored Forking](../tool-engineering/skill-reuse-as-vendored-forking.md) covers what that costs a copy you already hold.

Stars fail for a separate reason. Skills do not spread one at a time: repositories "copy entire catalogs in bulk or in bundles far more often than they adopt a single skill" ([Seddik, 2026](https://arxiv.org/abs/2610.11169v1)). A bundle copy then prefers a source already copied, at a coefficient of 1.64 on the logarithm of past copies. Preferential attachment runs on catalogs, so being a distributor is what makes a repository a source. Stars measure attention instead, and the star count "is also at risk of being artificially inflated (i.e., faked), decreasing its value as a decision-making signal" ([He et al., StarScout study](https://arxiv.org/abs/2412.13459v2)). An audit of 2,500 ClawHub skills found the same decoupling from the other direction: "download volume is not a reliable proxy for security quality" ([Guo et al., 2026](https://arxiv.org/abs/2603.21019v1)).

## What a review has to cover

Reviewers "have weeks rather than hours, because a new skill reaches few of its eventual adopters in its first week" ([Seddik, 2026](https://arxiv.org/abs/2610.11169v1)). A weekly pass over a ranked list keeps up. The pass has to span agent folders, because "a third of copies between agent folders now cross platforms" ([Seddik, 2026](https://arxiv.org/abs/2610.11169v1)). Checking only `.claude/skills/` misses the copies that landed elsewhere, some of which still name tools only Claude Code provides.

## When this backfires

- A flag read as a verdict misleads. The flags "mark capability rather than malice", and against a 200-skill labeled sample the strict flag measured 98.3% precision and 80.9% recall ([Seddik, 2026](https://arxiv.org/abs/2610.11169v1)). Removing every flagged skill removes working ones.
- Out-degree used to find who introduced a defect fails. It ranks catalogs, so the audit lands on a distributor and the author stays unexamined.
- You stop reading popular skills because stars rank poorly for prevention. Over 90% of high-popularity skills failed the SkillProbe audit ([Guo et al., 2026](https://arxiv.org/abs/2603.21019v1)). Popularity selects a set worth reading; it does not predict spread.
- A 14.9% cut is not the whole defense. It cuts future adoptions, and says nothing about the skills already on your disk, which need the [closure read](skill-closure-declaration-gap.md).
- You extrapolate past the measurement. The data "cover the first ten months of the format on public GitHub" ([Seddik, 2026](https://arxiv.org/abs/2610.11169v1)).

## Key Takeaways

- Credit a repository only for skills it held first. Only 7 of the 20 highest static out-degree repositories survive that correction ([Seddik, 2026](https://arxiv.org/abs/2610.11169v1)).
- Budget for about a quarter of high-risk adoptions at best. Half arrive as skills nobody could have ranked.
- The top of the list is a catalog, not an author. Use it to stop spread, and something else for attribution.
- Schedule the pass weekly and run it across every agent folder, not only the one your team uses.
- Keep reading popular skills anyway. Stars failing as a prevention ranking is a different claim from popular skills being clean ([Guo et al., 2026](https://arxiv.org/abs/2603.21019v1)).

## Related

- [Skill Reuse as Vendored Forking](../tool-engineering/skill-reuse-as-vendored-forking.md) — owns the argument that a copy is a fork and what to bind at adoption; this page is the upstream-selection half
- [Skill Supply-Chain Poisoning](skill-supply-chain-poisoning.md) — what a top-ranked distributor can be spreading, and why the capability flags miss some of it
- [The Skill Closure Declaration Gap](skill-closure-declaration-gap.md) — the per-skill read a reviewer does once the ranking has chosen a repository
- [Skill Packs: Registry Distribution Needs Pinning Discipline](../instructions/skill-pack-registry-distribution.md) — the distribution channel that removes the need for this ranking, where a team can adopt it
- [Tool Cloning and Provenance Assessment](../tool-engineering/tool-cloning-provenance-assessment.md) — recovering provenance from a snapshot, which cannot give direction or dates
- [Repository Skill Release Drift](../patterns/anti-patterns/repository-skill-release-drift.md) — what a copy that never followed its source does to the agent reading it
