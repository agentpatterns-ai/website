---
title: "AI Bot CI/CD Workflow Reliability by Agent"
description: "Per-agent GitHub Actions success rates from 61,837 workflow runs range from 65% to 94% — CI reliability is agent-dependent, with sample-size and selection caveats that constrain how the numbers should be used."
term: "AI Bot CI/CD Workflow Reliability"
tags:
  - workflows
  - github-actions
  - arxiv
  - tool-agnostic
  - agent-design
aliases:
  - Agent CI Success Rate
  - AI Bot Workflow Reliability
last_reviewed: 2026-06-12
maturity: emerging
---

# AI Bot CI/CD Workflow Reliability by Agent

> Per-agent GitHub Actions workflow success rates span 29 points — 64.86% (Claude) to 94.44% (Codex) — but uneven samples and public-repo selection bound the reading.

## The measurement

A 2026 MSR Mining Challenge study analyzed 61,837 GitHub Actions workflow runs from 2,355 public repositories. It linked each run to a pull request authored by one of five agents: Claude, Devin, Cursor, Copilot, or Codex ([arXiv:2604.18334](https://arxiv.org/abs/2604.18334v1)). The runs come from the AIDev dataset ([arXiv:2602.09185](https://arxiv.org/abs/2602.09185v1)), which aggregates 932,791 agentic PRs across 116,211 repositories.

| Agent | Workflow Runs | Success Rate |
|-------|--------------:|-------------:|
| Codex | 180 | 94.44% |
| Copilot | 14,179 | 93.28% |
| Devin | 43,852 | 77.43% |
| Cursor | 3,031 | 72.39% |
| Claude | 37 | 64.86% |

Differences across agents are statistically significant (p<0.01). Copilot shows 7.53x higher odds of workflow success than Claude and 4.05x higher odds than Devin ([arXiv:2604.18334](https://arxiv.org/abs/2604.18334v1)).

## What the spread means and does not

The 29-point gap between Codex (94.44%) and Claude (64.86%) is real in the dataset. But three properties of the measurement constrain how far it generalizes.

Sample-size asymmetry. Devin and Copilot contribute 94% of the runs; Claude contributes 37 and Codex contributes 180. A success rate computed on 37 runs is indicative, not authoritative. The confidence interval is wide enough that Claude's "true" rate could overlap with Cursor's.

Public-repo selection. The dataset covers only public GitHub repositories. The paper notes that findings may not generalize to "private or enterprise CI/CD environments, which typically involve more complex workflows" ([arXiv:2604.18334](https://arxiv.org/abs/2604.18334v1)). Enterprise CI uses self-hosted runners, stricter gates, and custom orchestration not represented here.

Attribution noise for low-volume agents. A separate fingerprinting study of the same five agents achieved 97.2% overall F1, but Claude Code alone scored 0.67 F1 with 57% recall ([arXiv:2601.17406](https://arxiv.org/html/2601.17406v1)). Some PRs labeled "Claude" in the reliability study may be misattributed. Misattribution dominates more heavily where the labeled population is smallest.

## Repository-level correlation

At the repository level, agent contribution frequency correlates negatively with workflow success rate. Repos that receive more agentic PRs tend to show lower aggregate CI reliability ([arXiv:2604.18334](https://arxiv.org/abs/2604.18334)). The [MSR 2026 study](https://arxiv.org/abs/2604.18334) does not establish the direction of causation. Two readings fit the data:

- Agent PRs introduce more failures, dragging repository CI success rates down as volume grows.
- Repositories with less mature CI attract more agent experimentation (reverse causality).

The practical implication is the same either way: a repository that plans to absorb high agentic PR volume should expect CI reliability to become a first-order operational concern, not a background assumption.

## Failure category distribution

Across 3,067 failed agentic PRs the paper sorts failures into 13 categories. The largest slices:

- Bug Fixes — 17.57%
- UI/UX — 11.64%
- New Features — 10.26%
- Refactoring — 10.04%
- Config/Infrastructure — 8.04%
- Security — 3.59%
- CI/CD — 3.42%
- Tools/CLI — 1.95%

Testing/QA, APIs/SDKs, Docs/Examples, Performance, and Maintenance make up the remainder ([arXiv:2604.18334](https://arxiv.org/abs/2604.18334)). The paper classifies PR categories with GPT-5.0; inter-rater agreement is Cohen's κ=0.88.

## How CI/CD-specific edits compare

A complementary study (99,930 workflow runs, 8,031 PRs that touch CI/CD files) narrowed the scope to CI/CD configuration changes. It found build success rates statistically indistinguishable between CI/CD and non-CI/CD edits (75.59% vs 74.87%, p=0.138) ([arXiv:2601.17413](https://arxiv.org/html/2601.17413v1)). So config-file edits do not drive the per-agent reliability gap in the primary paper. The gap reflects PR work as a whole, not a CI-file handling deficit.

## Practical implications

Monitor CI reliability per agent, not in aggregate. A 30-point spread across agents in the same repository stays invisible if you track CI success only at the repo level. Attribute each run to the agent that authored the triggering PR.

Weight sample size when ranking. Codex's 94.44% comes from 180 runs. Treat the Codex/Copilot ordering as a tie within the observed data, and treat Claude's rate as "unresolved" until more runs accumulate.

Anticipate a reliability tax on agent PR volume. The repo-level negative correlation holds whichever way causation runs: higher agentic volume tracks with lower CI success. Plan CI infrastructure capacity to scale with agent deployment, not with human contributor counts.

Do not port these numbers into private-repo decisions. The selection bias is large enough that you must measure internal or enterprise CI reliability in place.

## When this data does not apply

- Low-volume agents in-sample: Claude (37 runs) and Codex (180 runs) carry confidence intervals too wide for tool-selection decisions. Choosing between Claude and Copilot on these numbers over-reads 37 observations.
- Private or enterprise environments: public-GitHub CI patterns are simpler than enterprise stacks with self-hosted runners, stricter gating, and custom orchestration.
- Non-representative task mix: 3.42% of failures are CI/CD-specific. A repository whose agent workload centers on bug fixes (17.57% failure share) will show a different reliability profile from the aggregate.
- Single-agent deployments: the cross-agent ranking does not matter when only one agent is in use. In that case, the signal is the absolute success rate trending over time.

## Key Takeaways

- Workflow success rates across five agents span 29 points: Codex 94.44%, Copilot 93.28%, Devin 77.43%, Cursor 72.39%, Claude 64.86%
- Sample sizes are uneven — Devin and Copilot dominate; Claude (37 runs) and Codex (180 runs) carry wide confidence intervals
- Repository-level agent contribution frequency correlates negatively with workflow success rate; direction of causation is not established
- Narrowing to CI/CD configuration edits alone erases the gap (75.59% vs 74.87%) — the per-agent spread is a PR-wide effect, not a CI-file-specific one
- Findings come from public GitHub only; private and enterprise CI reliability must be measured in-place

## Related

- [Continuous AI (Agentic CI/CD)](continuous-ai-agentic-cicd.md) — design pattern for running agents inside CI infrastructure with read-only defaults
- [Agent PR Volume vs. Value](../code-review/agent-pr-volume-vs-value.md) — merge-rate data from the same AIDev dataset
- [CRA-Only Review and the Merge Rate Gap](../code-review/cra-merge-rate-gap.md) — another MSR 2026 Mining Challenge finding on the same dataset
- [Headless Claude in CI](headless-claude-ci.md) — tool-specific CI integration for Claude Code

## Sources

- [arXiv:2604.18334](https://arxiv.org/abs/2604.18334) — Shah, Habib, Hussain, Ghafoor, Bangash (LUMS, 2026): "Reliability of AI Bots Footprints in GitHub Actions CI/CD Workflows" — MSR 2026 Mining Challenge
- [arXiv:2602.09185](https://arxiv.org/abs/2602.09185v1) — Li et al.: AIDev dataset (932,791 agentic PRs, 116,211 repos) — underlying dataset
- [arXiv:2601.17413](https://arxiv.org/html/2601.17413v1) — "When AI Agents Touch CI/CD Configurations" — CI/CD-specific edits compare equally to non-CI/CD edits
- [arXiv:2601.17406](https://arxiv.org/html/2601.17406) — "Fingerprinting AI Coding Agents on GitHub" — per-agent attribution F1 scores
