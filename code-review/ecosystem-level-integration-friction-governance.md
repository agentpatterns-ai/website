---
title: "Ecosystem-Level Integration Friction Governance"
term: "Ecosystem-Level Integration Friction Governance"
description: "Govern AI coding agents at the repository level — integration friction concentrates roughly twice as much for agent PRs as for human PRs, so per-agent benchmarks underweight the risk that actually accumulates."
aliases:
  - Repository-Level Agent Governance
  - Ecosystem-Level Risk Governance
tags:
  - code-review
  - human-factors
  - workflows
  - tool-agnostic
last_reviewed: 2026-06-29
maturity: emerging
---

# Ecosystem-Level Integration Friction Governance

> Integration friction is half a repository property, and agent PRs concentrate it twice as much as human PRs — govern the repository, not the agent.

## When the repository lens wins

The repository-level governance lens is the right primary unit when all three of these conditions hold:

- The repo absorbs autonomous-agent contributions from more than one agent or operator account.
- Concurrent contributions land at a rate fast enough to interact (roughly ≥50 agent PRs/month, the threshold below which repo-specific friction estimates lack statistical power).
- Reviewer and CI capacity, not generation, is the bottleneck.

Outside these conditions — single-agent repos, low PR volume, regulated codebases with mandatory human review — fall back to per-agent assessment and PR-level signals ([Agent-Authored PR Integration](agent-authored-pr-integration.md)).

## The finding

A multi-level analysis of 33,596 agent-authored PRs across 2,807 repositories (≥100 stars) covering Claude Code, OpenAI Codex, Devin, GitHub Copilot, and Cursor finds that the repository intraclass-correlation coefficient (ICC) for agent contributions is 0.30 versus 0.16 for matched human contributions on resolution latency. Other friction constructs widen the asymmetry: deliberation latency 0.43 vs. 0.21 and changes-requested 0.54 vs. 0.41 ([arXiv:2606.28235](https://arxiv.org/abs/2606.28235)).

The full population is 930,292 agent PRs across 116,211 repositories, joining the [AIDev](https://arxiv.org/abs/2507.15003) and [AgenticFlict](https://arxiv.org/abs/2604.03551) datasets. Integration friction is defined as the effort of integrating a contribution into a codebase that other contributors are concurrently changing, measured across seven constructs grouped into timing, effort, contention, and outcome.

## Why it works

Repository attributes — base-branch churn, branch protection, test-suite latency, conventions density, reviewer availability — set the cost floor for every PR. Agents amplify this concentration because they generate contributions faster than humans, increasing concurrency density per unit time, and because they lack the ambient project context that lets human contributors self-route around hot areas. So the same repo-level attributes that mildly shape human friction strongly shape agent friction — a variance-decomposition effect that Russo (2026) quantifies as roughly half of agent-PR friction sitting in the repository, not in the agent ([arXiv:2606.28235](https://arxiv.org/abs/2606.28235)).

## The four governance levers

Russo's framework names four interventions that follow from the variance decomposition:

1. Assess agents in the target repository, not on isolated benchmarks. SWE-bench-class evaluations face contamination, single-language bias, and confounded scaffold-model effects ([arXiv:2509.16941](https://arxiv.org/abs/2509.16941)), so the in-repo signal dominates.
2. Govern change tempo via merge queues and batch-size caps, not by capping agent headcount. Practitioner reports converge — when generation is cheap, the throughput lever is the merge queue, not the agent count ([Why Coding Agents Need a Merge Queue](https://ctx.rs/blog/merge-queue-for-agents/)).
3. Route review effort to high-friction paths using base-branch churn indicators rather than treating every diff as equivalent — the same principle as [Tiered Code Review](tiered-code-review.md), applied at the repository level.
4. Track a repository-level dashboard: base-branch churn, conflict-replay rate, reviewer engagement, and resolution-latency ICC trends — the four signals that index when the floor is rising.

## When this backfires

- Low PR volume: repos with under 50 agent PRs/month lack power to estimate repo-specific friction reliably; the dashboard becomes vanity.
- Single-agent repos: when only one agent operates, "govern the repo, not the agent" collapses into "govern the agent" with extra dashboarding overhead.
- Mandatory per-PR human review: the merge-queue tempo lever has no slack to give — every PR already gates on a human reviewer.
- Greenfield repos: with no concurrent contributors, integration friction by definition cannot accumulate; the thesis applies only to repos with active concurrent change.
- As a vendor lock-in justification: treating the ICC as license to standardize on one agent inverts the recommendation.

Per-agent assessment remains a complementary signal — agent merge rates range 43% (Copilot) to 82.6% (Codex) in the same population ([arXiv:2602.19441](https://arxiv.org/abs/2602.19441)) — so layer repo-level tempo and routing on top of per-agent quality choices. Repository rules are also bypassable when text-based ([arXiv:2603.26487](https://arxiv.org/abs/2603.26487)); pair the dashboard with mechanically enforceable controls (CI gates, merge-queue policy, branch protection).

## Key Takeaways

- The repository, not the agent, is the unit of governance when multiple agents contribute concurrently at volume.
- Agent contributions concentrate repository-level friction roughly twice as much as human contributions (ICC 0.30 vs. 0.16).
- The four levers are in-repo assessment, tempo governance, friction-aware review routing, and a repo-level dashboard — not agent-headcount caps.
- The lens is complementary to per-agent merge-rate analysis, not a replacement for it.
- Below ~50 agent PRs/month, the variance decomposition lacks power and the per-agent lens is cheaper.

## Related

- [Agent PR Volume vs. Value](agent-pr-volume-vs-value.md) — per-agent merge-rate gaps the repo-level lens complements
- [Agent-Authored PR Integration](agent-authored-pr-integration.md) — PR-level collaboration signals (the within-repo variance)
- [CRA-Only Review and the Merge Rate Gap](cra-merge-rate-gap.md) — reviewer composition as a per-repo policy variable
- [Tiered Code Review](tiered-code-review.md) — risk-aware review routing applied at the PR level
- [Agent-Generated Code Maintenance Asymmetry](agent-code-maintenance-asymmetry.md) — downstream repo-level cost of agent-authored files

## Sources

- [arXiv:2606.28235](https://arxiv.org/abs/2606.28235) — Russo (2026): "Govern the Repository, Not the Agent: Measuring Ecosystem-Level Risk in AI-Native Software" — ICC + integration-friction methodology
- [arXiv:2507.15003](https://arxiv.org/abs/2507.15003) — AIDev dataset (456K agent-authored PRs)
- [arXiv:2604.03551](https://arxiv.org/abs/2604.03551) — AgenticFlict: 27.67% merge-conflict rate across 142K agent PRs
- [arXiv:2602.19441](https://arxiv.org/abs/2602.19441) — Nachuma & Zibran (MSR 2026): per-agent merge-rate variation in the same population
- [arXiv:2509.16941](https://arxiv.org/abs/2509.16941) — SWE-Bench Pro: documented limits of per-agent benchmarks
- [arXiv:2603.26487](https://arxiv.org/abs/2603.26487) — Beyond Banning AI: enforcement-gap limits of repository-level governance
- [Why Coding Agents Need a Merge Queue](https://ctx.rs/blog/merge-queue-for-agents/) — practitioner argument for tempo governance
