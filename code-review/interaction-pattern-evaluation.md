---
title: "Interaction-Pattern Evaluation for Agentic PRs"
description: "Merge and rejection labels misclassify roughly two-thirds of rejected agentic PRs and one-fifth of merges — evaluate agents by interaction patterns (review loops, reviewer commits, force pushes) rather than raw outcome rates."
tags:
  - code-review
  - testing-verification
  - workflows
  - arxiv
  - tool-agnostic
last_reviewed: 2026-05-27
---

# Interaction-Pattern Evaluation for Agentic PRs

> Merge and rejection outcomes alone misrepresent agent quality: only 35.7% of rejected agentic PRs reflect clear agent failures, and 5.5% of merged ones show no visible interaction trace at all. Evaluate agents by what happened during review, not by the final label.

Outcome labels conflate three signals: whether the agent's output was viable, whether reviewers chose to engage, and whether the interaction was observable. An analysis of 11,048 closed agentic PRs — 9,799 human-reviewed, 717 manually inspected — found 31.2% of rejections driven by workflow constraints (duplicates, abandonment, policy mismatches) and 33.1% with no observable decision rationale ([MSR 2026 mining challenge entry](https://2026.msrconf.org/details/msr-2026-mining-challenge/15/Why-Are-Agentic-Pull-Requests-Merged-or-Rejected-An-Empirical-Study)). Among merged PRs, 15.4% required explicit reviewer involvement through feedback or direct commits, and 5.5% closed without visible interaction. Interaction-pattern evaluation replaces the binary outcome with a structured signal set drawn from the review trace itself.

## What to Measure

Five signals separate agent capability from workflow noise:

- **Review-loop completion** — did the PR receive at least one substantive review and converge in a bounded number of rounds? Reviewer engagement is the strongest single predictor of merge in a regression on 33,596 agent-authored PRs ([arXiv:2602.19441](https://arxiv.org/abs/2602.19441)).
- **Reviewer-commit involvement** — did a human push commits onto the PR branch? 15.4% of merged agentic PRs were rescued this way; counting them as "agent successes" overstates capability ([MSR 2026 entry](https://2026.msrconf.org/details/msr-2026-mining-challenge/15/Why-Are-Agentic-Pull-Requests-Merged-or-Rejected-An-Empirical-Study)).
- **Force-push count during review** — force pushes are the strongest negative merge predictor; they invalidate prior review context and signal instability ([arXiv:2602.19441](https://arxiv.org/abs/2602.19441)).
- **Time-to-first-review and abandonment** — workflow-driven closures dominate the 33.1% "no observable rationale" bucket. Track whether PRs reach a reviewer at all before reading the close event as a capability signal ([MSR 2026 entry](https://2026.msrconf.org/details/msr-2026-mining-challenge/15/Why-Are-Agentic-Pull-Requests-Merged-or-Rejected-An-Empirical-Study)).
- **Reviewer-mediation mode per agent** — Copilot and Devin sit more often inside reviewer-mediated workflows; Codex and Cursor PRs typically merge with minimal interaction ([MSR 2026 entry](https://2026.msrconf.org/details/msr-2026-mining-challenge/15/Why-Are-Agentic-Pull-Requests-Merged-or-Rejected-An-Empirical-Study)). Compare agents in the same mode, not on aggregate rate.

Task type confounds aggregate merge rate independently: documentation tasks accept at 82.1% versus 66.1% for new features — a 16-point gap that exceeds inter-agent variance on most categories ([arXiv:2602.08915](https://arxiv.org/abs/2602.08915)). Stratify every metric above by task type before comparing agents.

## Why It Works

The mechanism is causal pathway separation. An outcome label collapses three independent processes — agent output viability, reviewer engagement choice, and trace observability — into one binary, so any agent comparison built on that signal is contaminated by the latter two. The MSR 2026 manual inspection of 717 cases shows roughly two-thirds of rejection labels and one-fifth of merge labels carry information unrelated to agent capability ([MSR 2026 entry](https://2026.msrconf.org/details/msr-2026-mining-challenge/15/Why-Are-Agentic-Pull-Requests-Merged-or-Rejected-An-Empirical-Study)). Interaction signals — review-loop count, reviewer-commit count, force-push count, abandonment timestamp — are emitted by the three processes separately, so a metric set built on them recovers a less contaminated capability estimate. The same mechanism appears in Alam et al.'s analysis of 8,106 fix-related agentic PRs, where test failures and prior resolution of the same issue dominated non-integration — not capability defects ([arXiv:2602.00164](https://arxiv.org/abs/2602.00164)).

## When This Backfires

Interaction-pattern evaluation adds instrumentation cost and assumes enough PR volume to estimate the new metrics reliably. Five conditions favour falling back to outcome rates:

- **Homogeneous task mix and stable reviewers** — if an agent only ships documentation PRs to one team, the rationale-loss bucket collapses and merge rate becomes an acceptable proxy. The 82.1% documentation acceptance baseline is high enough that workflow noise dominates less ([arXiv:2602.08915](https://arxiv.org/abs/2602.08915)).
- **Curated, high-engagement populations** — Watanabe et al. examined 567 Claude Code PRs across 157 maintained OSS projects and found 83.8% merge with 54.9% un-modified ([arXiv:2509.14745](https://arxiv.org/abs/2509.14745)). When reviewer abandonment and missing rationale are rare by selection, outcome rates carry more signal.
- **Internal deployments with SLA-bounded review** — if every agentic PR is triaged within a fixed window and never closes as stale, the 33.1% "no observable rationale" bucket shrinks. Public-OSS pathologies do not transfer to closed teams that enforce review SLAs.
- **Low PR volume** — stable interaction-pattern statistics need enough PRs per agent and per task type to overcome variance. Small teams may not have the data to make the richer metric set more accurate than aggregate rate.
- **Agents optimised against the evaluation metric** — any metric used to gate procurement creates an optimisation target. Agents tuned to maximise reviewer engagement (chatty comments, artificial review loops) can game interaction signals the same way agents tuned to maximise merge rate can game outcomes. Audit the metric definition against gaming pressure before scaling its use.

A practitioner steelman: aggregate merge rate is the cheapest KPI for procurement and rank-orders agents directionally correctly when sample sizes are large and task mix is similar. Adopt interaction-pattern evaluation when those assumptions break, not as a blanket replacement.

## Example

A platform team evaluates four agents over a quarter and reads off aggregate merge rates: Codex 82.6%, Cursor 71%, Devin 53.8%, Copilot 43.0% ([arXiv:2602.19441](https://arxiv.org/abs/2602.19441)). The headline ranking is Codex > Cursor > Devin > Copilot.

Stratifying by interaction pattern surfaces a different story. Copilot and Devin PRs concentrate in reviewer-mediated workflows — their merges include high rates of reviewer commits and review-loop completion, both positive capability signals once isolated. Codex and Cursor PRs merge with minimal interaction, which the outcome metric rewards but which also obscures whether those merges include the 5.5% "no visible trace" bucket where review was effectively absent ([MSR 2026 entry](https://2026.msrconf.org/details/msr-2026-mining-challenge/15/Why-Are-Agentic-Pull-Requests-Merged-or-Rejected-An-Empirical-Study)). Task stratification compounds the correction: if Copilot ships proportionally more bug-fix PRs (42.2% of its mix versus 26.9% for humans) and bug-fix has a structurally lower acceptance rate than documentation, the headline gap shrinks further ([arXiv:2507.15003](https://arxiv.org/abs/2507.15003)). The team picks a tier-1 agent based on per-task, per-interaction-mode performance rather than the aggregate.

## Key Takeaways

- Treat merge and reject labels as noisy mixtures of agent capability, reviewer engagement, and trace observability — not as single capability signals
- Two-thirds of rejection labels and one-fifth of merge labels in the 717-case manual inspection encode workflow or rationale information unrelated to agent output ([MSR 2026 entry](https://2026.msrconf.org/details/msr-2026-mining-challenge/15/Why-Are-Agentic-Pull-Requests-Merged-or-Rejected-An-Empirical-Study))
- Measure review-loop completion, reviewer-commit involvement, force-push count, time-to-first-review, and per-agent reviewer-mediation mode
- Stratify by task type before comparing agents — the documentation-vs-features gap (16 points) exceeds typical inter-agent variance ([arXiv:2602.08915](https://arxiv.org/abs/2602.08915))
- Fall back to outcome rate when task mix and reviewer cohort are homogeneous, PR volume is low, or the population is curated to rule out abandonment

## Related

- [Agent PR Volume vs. Value](agent-pr-volume-vs-value.md) — the outcome-rate view this page complements; per-agent acceptance rates and the productivity paradox
- [Agent-Authored PR Integration](agent-authored-pr-integration.md) — the same interaction signals analysed via logistic regression on 33,596 PRs; reviewer engagement as the strongest positive predictor
- [CRA-Only Review and the Merge Rate Gap](cra-merge-rate-gap.md) — how reviewer composition shifts outcome rates by 23 points independent of code quality
- [PR Description Style as a Lever](pr-description-style-lever.md) — a single configurable input that moves the interaction-pattern signals
- [Tiered Code Review](tiered-code-review.md) — risk-routing framework that makes per-agent, per-task evaluation operationally useful

## Sources

- [MSR 2026 mining challenge — "Why Are Agentic Pull Requests Merged or Rejected? An Empirical Study"](https://2026.msrconf.org/details/msr-2026-mining-challenge/15/Why-Are-Agentic-Pull-Requests-Merged-or-Rejected-An-Empirical-Study) — 11,048 closed agentic PRs; 717 manual inspections; introduces interaction-pattern evaluation
- [arXiv:2602.19441](https://arxiv.org/abs/2602.19441) — Nachuma & Zibran (MSR 2026): logistic regression on 33,596 agent-authored PRs; reviewer engagement strongest positive predictor, force pushes strongest negative
- [arXiv:2602.00164](https://arxiv.org/abs/2602.00164) — Alam et al.: 8,106 fix-related agentic PRs; 12 failure reasons dominated by duplicates and CI failures
- [arXiv:2602.08915](https://arxiv.org/abs/2602.08915) — Pinna et al.: task-stratified analysis of 7,156 PRs; 16-point documentation-vs-features acceptance gap
- [arXiv:2509.14745](https://arxiv.org/abs/2509.14745) — Watanabe et al.: 567 Claude Code PRs across 157 maintained OSS projects; 83.8% merge baseline counter-evidence
- [arXiv:2507.15003](https://arxiv.org/abs/2507.15003) — Li, Zhang & Hassan: AIDev dataset of 456K agent-authored PRs; per-agent task mix
