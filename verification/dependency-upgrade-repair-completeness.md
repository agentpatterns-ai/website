---
title: "Why Coding Agents Leave Dependency Upgrades Half Migrated"
term: "Incomplete Migration"
description: "On a 203-task upgrade benchmark, incomplete migration was the most common failure label, 36.5% of failed runs. A repair skill gained 15 and 6 tasks on two setups."
tags:
  - testing-verification
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - dependency upgrade repair completeness
  - old-symbol sweep
last_reviewed: 2026-11-19
maturity: emerging
---

# Why Coding Agents Leave Dependency Upgrades Half Migrated

> On breaking dependency upgrades, the most common agent failure label was an incomplete migration, at 36.5% of failed runs.

On DepBench, 203 upgrades that needed human source repair, the best of ten agent configurations solved 100 tasks (49.3%, Copilot CLI with GPT-5.5, one trial each). Across 1,262 failed runs, the most common label was incomplete migration (460, 36.5%), then wrong semantic output (397, 31.5%) and wrong root cause (361, 28.6%) ([Luo et al., 2026](https://arxiv.org/abs/2608.30300v2), §IV-E, Table V). Labels overlap. "No upgrade attempted" is 154 of 1,262 (12.2%), and 70 of those come from OpenCode with Gemini 3.5 Flash.

This page covers how completely an agent repairs a break. [Version Labels Steer How Hard Agents Check Upgrades](version-labels-steer-upgrade-checks.md) covers whether it checks at all.

Limits:

- DepBench keeps 203 of 4,660 mined pull requests (4.4%), and only upgrades where a human had to add source changes after the bot's bump (§III-D). Routine bumps are excluded.
- Each configuration ran once, with no open-weight models (§IV-A). The top two differ by one task, which the paper says "does not establish a performance advantage" (§IV-B).
- LLM annotators assigned the failure labels, with Cohen's kappa of 0.5240 before adjudication (§IV-E).
- Success means passing held-out tests (§VI-A). Python has 10 tasks (§IV-B).

## Two failure shapes

Propagation. Agents "fix the first visible compiler error but leave the migration inconsistent across the repository" (§IV-E). In the GitLab client case, a Go upgrade widened identifier types, with int becoming int64. The selected Codex and Copilot CLI trials with GPT-5.5 migrated the client wrapper but left a merge-request helper returning an int slice.

Semantics. In the Gremlin case, both selected GPT-5.5 trials added or modified a local NumberHelper override to preserve the old overflow behavior. The hidden test expects the upgraded engine to throw. The data also record 71 test-tampering labels (Table V), which [Protecting the Test Oracle From the Agent](../patterns/agent-design/protect-the-oracle-from-the-agent.md) covers.

Documentation lookup is the least used behavior. With GPT-5.5 it appears in 18 to 97 of 203 trajectories, against 151 to 178 for local API inspection and 161 to 193 for test runs (Table III).

## The skill and what it showed

The authors wrote DepUpgrader, a five-step skill: confirm the upgrade, extract version-matched migration rules, find affected code, make minimal edits, and validate. Validation includes a search for remaining old usages (§IV-E).

| Configuration | Baseline | With skill | Gain |
|---|---|---|---|
| Copilot CLI + GPT-5.5 | 100/203 (49.3%) | 115/203 (56.7%) | +15 tasks, +7.4 points |
| Codex + GPT-5.5 | 99/203 (48.8%) | 105/203 (51.7%) | +6 tasks, +2.9 points |

The abstract's 15.0% and 6.1% are relative gains (Table VII). The section is labeled preliminary. Only these two GPT-5.5 configurations were tested, against the earlier baseline run.

The Codex gain is about the size of the baseline's own drift between versions. Version 1 of the paper reported Codex with GPT-5.5 at 104 of 203 ([v1, §IV-B](https://arxiv.org/abs/2608.30300v1)). Version 2 reports 99, a 5-task shift against a 6-task gain.

## Why it works

The paper's account is that agents work mainly from local API inspection and test and build feedback, so they stop after the first visible break ([Luo et al., 2026](https://arxiv.org/abs/2608.30300v2), §IV-C, §IV-E). The skill swaps that for an explicit inventory: recorded old-to-new mappings with evidence, a repository search for old symbols, and a final sweep. No ablation shows which step does the work.

## What to do

1. Record each old-to-new API mapping with its evidence: changelog, migration guide, or installed type definitions.
2. After the last edit, search the repository for every old symbol, alias, and local wrapper. Do not finish while any remain, even when the build is green.
3. For a behavior change, quote the upgrade guide's description before editing any test expectation.
4. Measure the gain on your own harness, where it was +15 and +6 here.

## When this backfires

- Tests cover little of the dependency surface. In an earlier study, tests detected 47% of direct and 35% of indirect artificial faults on average ([Hejderup and Gousios, 2021](https://arxiv.org/abs/2109.11921v1)).
- No version-matched migration guide exists, so the "do not guess" step has nothing to cite.
- The harness already reads documentation. Codex with GPT-5.5 did so in 97 of 203 runs and gained less of the two tested.
- Skills in general: software engineering gained second least of 8 domains (+11.6 points), and 13 of 87 tasks got worse ([Li et al., 2026](https://arxiv.org/abs/2602.12670v4)).

## Key Takeaways

- A green build is where agents stop, so make the old-symbol sweep a required last step.
- Read the skill's gain as +15 and +6 tasks on two setups, not as a general effect.
- Decide which updates reach a repair agent with [Routing Dependency Updates to Repair Agents by Budget](../workflows/dependency-update-repair-routing.md).

## Related

- [Version Labels Steer How Hard Agents Check Upgrades](version-labels-steer-upgrade-checks.md)
- [Routing Dependency Updates to Repair Agents by Budget](../workflows/dependency-update-repair-routing.md)
- [Dependabot Agent Assignment for AI-Driven Vulnerability Remediation](../tools/copilot/dependabot-agent-assignment.md)
- [Verification-Gated Agent Autonomy via Automated Review](../patterns/agent-design/verification-gated-agent-autonomy.md)
- [Protecting the Test Oracle From the Agent](../patterns/agent-design/protect-the-oracle-from-the-agent.md)
- [Delegating Dependabot Pull Request Triage to an Agent](../workflows/dependabot-pr-triage-delegation.md)
