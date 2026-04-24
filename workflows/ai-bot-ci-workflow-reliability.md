---
title: "AI Bot CI/CD Workflow Reliability by Agent"
description: "Per-agent GitHub Actions success rates from 61,837 workflow runs range from 65% to 94% — CI reliability is agent-dependent, with sample-size and selection caveats that constrain how the numbers should be used."
tags:
  - workflows
  - github-actions
  - arxiv
aliases:
  - Agent CI Success Rate
  - AI Bot Workflow Reliability
---

# AI Bot CI/CD Workflow Reliability by Agent

> GitHub Actions workflow success rates for PRs authored by five AI coding agents vary from 64.86% (Claude) to 94.44% (Codex) — a 29-point spread whose interpretation is bounded by uneven sample sizes and public-repo selection effects.

## The Measurement

A 2026 MSR Mining Challenge study analysed 61,837 GitHub Actions workflow runs from 2,355 public repositories, linking each run to a pull request authored by one of five agents: Claude, Devin, Cursor, Copilot, or Codex ([arXiv:2604.18334](https://arxiv.org/abs/2604.18334)). Runs come from the AIDev dataset ([arXiv:2602.09185](https://arxiv.org/abs/2602.09185)), which aggregates 932,791 agentic PRs across 116,211 repositories.

| Agent | Workflow Runs | Success Rate |
|-------|--------------:|-------------:|
| Codex | 180 | 94.44% |
| Copilot | 14,179 | 93.28% |
| Devin | 43,852 | 77.43% |
| Cursor | 3,031 | 72.39% |
| Claude | 37 | 64.86% |

Differences across agents are statistically significant (p<0.01). Copilot shows 7.53x higher odds of workflow success than Claude and 4.05x higher odds than Devin ([arXiv:2604.18334](https://arxiv.org/abs/2604.18334)).

## What the Spread Means — and Does Not

The 29-point gap between Codex (94.44%) and Claude (64.86%) is real in the dataset, but three properties of the measurement constrain how far it generalises.

**Sample-size asymmetry.** Devin and Copilot contribute 94% of the runs; Claude contributes 37 and Codex contributes 180. A success rate computed on 37 runs is indicative, not authoritative — the confidence interval is wide enough that Claude's "true" rate could overlap with Cursor's.

**Public-repo selection.** The dataset is restricted to public GitHub repositories. The paper explicitly notes findings may not generalise to "private or enterprise CI/CD environments, which typically involve more complex workflows" ([arXiv:2604.18334](https://arxiv.org/abs/2604.18334)). Enterprise CI uses self-hosted runners, stricter gates, and custom orchestration not represented here.

**Attribution noise for low-volume agents.** A separate fingerprinting study of the same five agents achieved 97.2% overall F1, but Claude Code alone scored 0.67 F1 with 57% recall ([arXiv:2601.17406](https://arxiv.org/html/2601.17406)). Some PRs labelled "Claude" in the reliability study may be misattributed, and misattribution dominates more heavily where the labelled population is smallest.

## Repository-Level Correlation

At the repository level, agent contribution frequency correlates negatively with workflow success rate — repos receiving more agentic PRs tend to show lower aggregate CI reliability ([arXiv:2604.18334](https://arxiv.org/abs/2604.18334)). The direction of causation is not established by the study. Two readings are consistent with the data:

- Agent PRs introduce more failures, dragging repository CI success rates down as volume grows.
- Repositories with less mature CI attract more agent experimentation (reverse causality).

The practical implication is the same either way: repositories planning to absorb high agentic PR volume should expect CI reliability to become a first-class operational concern, not a background assumption.

## Failure Category Distribution

Across 3,067 failed agentic PRs the paper classifies failures into 13 categories. The largest slices:

- Bug Fixes — 17.57%
- UI/UX — 11.64%
- New Features — 10.26%
- Refactoring — 10.04%
- Config/Infrastructure — 8.04%
- Security — 3.59%
- CI/CD — 3.42%
- Tools/CLI — 1.95%

Testing/QA, APIs/SDKs, Docs/Examples, Performance, and Maintenance make up the remainder ([arXiv:2604.18334](https://arxiv.org/abs/2604.18334)). The paper classifies PR categories with GPT-5.0; inter-rater agreement is Cohen's κ=0.88.

## How CI/CD-Specific Edits Compare

A complementary study (99,930 workflow runs, 8,031 PRs that touch CI/CD files) found that when the scope is narrowed to CI/CD configuration changes, build success rates are statistically indistinguishable between CI/CD and non-CI/CD edits (75.59% vs 74.87%, p=0.138) ([arXiv:2601.17413](https://arxiv.org/html/2601.17413v1)). The per-agent reliability gap in the primary paper is therefore not driven by config-file edits specifically — it reflects PR work as a whole, not a CI-file handling deficit.

## Practical Implications

**Monitor CI reliability per agent, not in aggregate.** A 30-point spread across agents in the same repository will be invisible if CI success is tracked only at the repo level. Attribute runs to the agent that authored the triggering PR.

**Weight sample size when ranking.** Codex's 94.44% comes from 180 runs. Treat the Codex/Copilot ordering as a tie within the observed data, and treat Claude's rate as "unresolved" until more runs accumulate.

**Anticipate a reliability tax on agent PR volume.** The repo-level negative correlation holds regardless of direction of causation — higher agentic volume tracks with lower CI success. Capacity planning for CI infrastructure should scale with agent deployment, not with human contributor counts.

**Do not port these numbers into private-repo decisions.** The selection bias is large enough that internal or enterprise CI reliability must be measured in-place.

## When This Data Doesn't Apply

- **Low-volume agents in-sample** — Claude (37 runs) and Codex (180 runs) carry confidence intervals too wide for tool-selection decisions. A practitioner choosing between Claude and Copilot on these numbers over-reads 37 observations.
- **Private / enterprise environments** — public-GitHub CI patterns are simpler than enterprise stacks with self-hosted runners, stricter gating, and custom orchestration.
- **Non-representative task mix** — 3.42% of failures are CI/CD-specific. A repository whose agent workload is dominated by bug fixes (17.57% failure share) will show a different reliability profile from the aggregate.
- **Single-agent deployments** — the cross-agent ranking is irrelevant when only one agent is in use; in that case, absolute success rate trending over time is the signal.

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
- [arXiv:2602.09185](https://arxiv.org/abs/2602.09185) — Li et al.: AIDev dataset (932,791 agentic PRs, 116,211 repos) — underlying dataset
- [arXiv:2601.17413](https://arxiv.org/html/2601.17413v1) — "When AI Agents Touch CI/CD Configurations" — CI/CD-specific edits compare equally to non-CI/CD edits
- [arXiv:2601.17406](https://arxiv.org/html/2601.17406) — "Fingerprinting AI Coding Agents on GitHub" — per-agent attribution F1 scores
