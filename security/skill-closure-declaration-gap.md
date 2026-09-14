---
title: "The Skill Closure Declaration Gap"
term: "Skill Closure Declaration Gap"
description: "Of 526 published Agent Skills that bundle files, 21 name every one of them in SKILL.md and none declares a dependency. Approving a skill root is not approving what runs."
aliases:
  - undeclared skill dependencies
  - agent skill dependency closure
  - skill closure binding
tags:
  - security
  - tool-agnostic
  - skills
  - supply-chain
  - arxiv
last_reviewed: 2026-09-09
maturity: emerging
---

# The Skill Closure Declaration Gap

> A skill root names less than a run of that skill loads, so approving the root approves an incomplete statement.

The skill closure declaration gap is the distance between what a `SKILL.md` names and the files, packages, and services one run of that skill can reach. Zhu and Wang measured it across 549 public Agent Skills holding 4,872 unique local files at two fixed commits. Of the 526 roots bundling at least one file besides `SKILL.md`, 21 name every one of those paths verbatim in the manifest ([Zhu and Wang, 2026](https://arxiv.org/abs/2609.05920v1)).

## When this applies

The review practices below repay their cost under three conditions.

- The skill arrives from outside the repository you review. A registry CLI that installs by [symlink to a canonical copy](../instructions/skill-pack-registry-distribution.md) puts bytes on disk that no pull request diff showed you.
- The skill ships executable helpers. A `scripts/` directory makes the closure a question about packages and services, not just markdown.
- Anything you pin has an update path behind it, for the reason [pinned library versions](llm-pinned-vulnerable-versions.md) carry their own exposure.

If none of those holds, skip this. Markdown files living in your own repository, installed by copy, already reach code review byte by byte.

## What the audit measured

Two frozen public commits, walked by a repository adapter that follows no symlinks ([Zhu and Wang, 2026](https://arxiv.org/abs/2609.05920v1)).

| Snapshot | Skills | Unique files | Roots with bundled files | Roots naming every path | Roots with cross-root links |
|---|--:|--:|--:|--:|--:|
| Anthropic Skills, commit `3b3fad96` | 19 | 411 | 18 | 6 | 0 |
| OpenAI plugin Skills, commit `1e285826` | 530 | 4,461 | 508 | 15 | 67 |
| Total | 549 | 4,872 | 526 | 21 | 67 |

Two results sit behind that table. Of 1,341 unique Markdown link targets, 208 links across 67 skills resolve inside the same repository but outside the skill's own root. And no frontmatter among the 549 declares a dependency, which is a fact about the format rather than about the authors: Claude Code's `SKILL.md` field reference lists twenty-odd optional fields and no `dependencies` field ([Claude Code documentation](https://code.claude.com/docs/en/skills)).

Read 21 of 526 as a ceiling on what a reviewer can rebuild from the manifest, not as a defect rate. The count is "a strict lexical measure, not semantic dependency recall", and a path the audit flags may be "documentation-rooted, generated at use time, or intentionally external" ([Zhu and Wang, 2026](https://arxiv.org/abs/2609.05920v1)).

## Why it works

Evidence gathered at the root authenticates an incomplete statement, because the operational dependency set need not exist when that evidence is collected. The format asks for a name and a description, treats its conventional directories as non-exhaustive, and expects scripts to document or resolve their own dependencies. Clients load catalog metadata first, instructions on activation, and referenced resources only when a task needs them, so "the complete operational dependency set need not exist at discovery or even at activation" ([Zhu and Wang, 2026](https://arxiv.org/abs/2609.05920v1)). Three gaps follow, and a root hash closes none of them. Completeness: a nested skill, a lazy package, or a service deployment the manifest never lists does not disappear by going unlisted. Topology: "an unordered inventory cannot distinguish 'Skill A invokes package P only through sandboxed helper B' from 'A invokes P directly'". Time: "loading precedes lazy resolution and the real effect".

An independent study of over 1.43 million skills reaches the same recommendation from a different corpus, reporting that skill metadata is "activation-ready but governance-poor" and that "inspecting only the root skill misses security-relevant signals that appear in transitive dependencies" ([Jia et al., 2026](https://arxiv.org/abs/2607.01136v1)).

## What to do before installing one

Enumerate the root yourself and diff that listing against what `SKILL.md` names. The gap is the part nobody reviewed. Read every helper for what it installs or calls at run time, and pin those versions inside the helper, since the manifest has nowhere to record them. Then resolve every relative link and flag the ones leaving the root, `${CLAUDE_PROJECT_DIR}` and `${CLAUDE_PLUGIN_ROOT}` paths included, which are the supported route to a file the skill does not ship ([Claude Code documentation](https://code.claude.com/docs/en/skills)). A leaving link is a question for the author, not a finding.

## When this backfires

- The skill lives in your repository and installs by copy. Every byte is in the diff, so a declared closure becomes a second artifact that drifts, with nothing checking the two agree.
- The helpers generate paths at use time or fetch at run time. A static declaration is wrong by construction, and repository enumeration "excludes packages, services, tools, generated paths, and runtime effects" ([Zhu and Wang, 2026](https://arxiv.org/abs/2609.05920v1)).
- You gate on the cross-root link count. The audit reports its 208 links without calling them defects, so a blocking check fails intentional shared references and teaches reviewers to wave the rule through.
- You add pins with no bump path. Model-specified versions carry a known CVE in 36.70% to 55.70% of tasks, and an unmaintained pin only sits still ([Wang et al., 2026](https://arxiv.org/abs/2605.06279v1)).

## Key Takeaways

- The manifest is not an inventory. 21 of 526 published skills that bundle files name all of them, so read the directory rather than the document.
- No `dependencies` field exists to declare, so pins have to live in the helper scripts that resolve them.
- A root hash answers "did these bytes change", never "is this the set that runs". Completeness, topology, and timing all sit outside it.
- Apply this to skills you did not write and cannot see in a diff. In-repo skills already get review from git.
- Ask the author where a leaving link goes. Some are deliberate, so a blocking check on them buys noise and a habit of overriding it.

## Related

- [Skill Packs: Registry Distribution Needs Pinning Discipline](../instructions/skill-pack-registry-distribution.md) — pins the bundle through a registry channel, where this page argues the bundle boundary is not the closure boundary
- [Skill Supply-Chain Poisoning](skill-supply-chain-poisoning.md) — what a publisher can put inside the part of the closure nobody enumerated
- [Skill Composition Risk in Agent Ecosystems](skill-composition-risk.md) — the runtime counterpart, where individually vetted skills compose into an effect neither one authorizes
- [Agent Config as a Managed Supply Chain](../instructions/agent-config-as-managed-supply-chain.md) — the same hashing and pinning discipline applied to `CLAUDE.md` and `AGENTS.md`
- [LLM-Pinned Library Versions Carry Systemic CVE Exposure](llm-pinned-vulnerable-versions.md) — why the pin you add to a helper script needs a bump path behind it
- [Authorization Continuity Across Agent Mutation](authorization-continuity-across-agent-mutation.md) — the general principle this page is one instance of: a grant names a subject that can change after the grant is issued
