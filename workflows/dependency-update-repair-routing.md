---
title: "Routing Dependency Updates to Repair Agents by Budget"
term: "Dependency-Update Repair Routing"
description: "Rank dependency-update pull requests by repair likelihood and escalate only the top slice, which cut calls per captured repair from 6.90 to 2.68."
aliases:
  - pre-agent escalation routing
  - dependency update repair triage
tags:
  - tool-agnostic
  - workflows
  - agent-design
  - token-engineering
  - arxiv
last_reviewed: 2026-09-23
maturity: emerging
---

# Routing Dependency Updates to Repair Agents by Budget

> When invoking a repair agent is expensive, score every dependency bump first and spend the budget on the top slice.

Dependency-update repair routing ranks incoming dependency pull requests by how likely each one is to need compatibility work. A repository-level repair agent then runs on a fixed top fraction of that ranking. Everything below the cut takes the review it would have had anyway. On 497 labeled GitHub dependency-update candidates, routing the top 20% captured 51.4% of the repair-requiring cases and cut calls per captured repair from 6.90 to 2.68 ([arXiv:2609.25911v1](https://arxiv.org/abs/2609.25911v1)).

## The condition that decides whether this pays

Routing is worth building when one invocation is expensive. Running an agent on every update "wastes model calls, CI time, repository context, and review attention" ([arXiv:2609.25911v1](https://arxiv.org/abs/2609.25911v1)), and those four costs are what the router is buying back. It is not worth building when escalation is a cheap metadata prompt. In the same paper's pilot, "all-agent diagnosis used 60 calls and 22,827 tokens" over 60 pull requests, roughly 380 tokens each. At that price a router saves almost nothing and still discards work.

Check the shape of your queue too. The 14.5% positive rate here is not what a real Dependabot queue produces. The authors built the candidate pool with repair-like search terms: "The collection strategy intentionally targets a repair-enriched pool rather than a natural dependency-update stream." ([arXiv:2609.25911v1](https://arxiv.org/abs/2609.25911v1)) A sparser stream moves both the precision you can reach and the point at which routing breaks even.

## The budget arithmetic

Hold the call budget fixed and the policies become comparable. At a top-20% budget the creation-time-safe model "routes 99 of 497 pull requests and captures 37 of 72 repairs. This improves precision from the 14.5% base rate to 37.4%, and reduces calls per captured repair from 6.90 under route-all or random routing to 2.68" ([arXiv:2609.25911v1](https://arxiv.org/abs/2609.25911v1)).

| Policy | Calls | Repairs captured | Recall | Calls per repair |
|---|---|---|---|---|
| Route all | 497 | 72 | 1.000 | 6.90 |
| Random 20% | 99 | 14.4 | 0.200 | 6.90 |
| Creation-time-safe top 20% | 99 | 37 | 0.514 | 2.68 |
| Full-history top 20% | 99 | 47 | 0.653 | 2.11 |

Read the recall column as the price. Half the repair cases rank below the cut, so the bottom 80% still needs whatever review it had before. The authors are explicit that a low score is not a merge signal: "Low-risk routing means skipping the repair agent, not automatic merging; normal review and CI policies still apply." ([arXiv:2609.25911v1](https://arxiv.org/abs/2609.25911v1))

## Score only on what exists at decision time

The full-history row in that table is the one to be careful with. Its extra recall comes from human follow-up commits, later commit messages, and mixed file counts — evidence that appears only after a developer has already reacted to the breakage. Feed those to an offline evaluation and the router looks 14 recall points better than it can ever be in production. The authors separate three feature regimes for exactly this reason and conclude: "We therefore interpret full-history results as diagnostic evidence for repair mining, not as live deployment savings." ([arXiv:2609.25911v1](https://arxiv.org/abs/2609.25911v1))

So fit and score the router on the fields available the moment the pull request opens. Here that was the title plus bot and dependency flags, a linear SVM that "reaches 0.488 repair F1 and 0.514 top-20% recall". Adding the initial bot commit messages made the ranking worse, not better: it "yields similar repair F1 (0.475) but lower top-20% recall (0.472)" ([arXiv:2609.25911v1](https://arxiv.org/abs/2609.25911v1)).

## Why it works

Ranking concentrates a sparse positive class into the top of the budget, so precision at that budget exceeds the base rate and the expected number of calls per captured case falls. That is the whole causal story the evidence supports, and the authors claim no more. "The central claim is not that a particular classifier is optimal, but that inexpensive pull-request signals can support selective routing" ([arXiv:2609.25911v1](https://arxiv.org/abs/2609.25911v1)). Why a bare title carries that much signal is unexplained. The general principle of paying for an expensive model only where a cheap predictor says it will return comes from the cost-cascade result in [FrugalGPT](https://arxiv.org/abs/2305.05176).

## When this backfires

- Escalation is already cheap. A percentage saving on a prompt that costs a few hundred tokens buys less than the repairs it drops.
- The score becomes a gate with nothing behind it. At 51.4% capture, a hard threshold turns half the repair cases into permanent misses rather than deferred ones.
- You believe your offline number. A study of 206,000 query-model pairs found that "These artifacts also distort router training signals: standard routers collapse to majority-class prediction", and concluded that "existing routing headroom estimates are substantially inflated" ([arXiv:2605.07395v1](https://arxiv.org/abs/2605.07395v1)).
- The workload moves. A router fitted once decays, because "both the request mix and the model frontier drift after launches, fine-tunes, quantization changes, and system updates" ([arXiv:2609.00662v1](https://arxiv.org/abs/2609.00662v1)). Keep a rolling audit sample, or refit.
- You read the pilot as end-to-end proof. Router-gated diagnosis "covered only 4 of the 12 gold repairs in the 60-case sample", and the pilot "measures diagnosis escalation cost, not repository editing or successful patch generation" ([arXiv:2609.25911v1](https://arxiv.org/abs/2609.25911v1)).
- Your queue is too small to fit a ranker. The router was fitted on 497 hand-labeled candidates: "Labels were assigned by a single annotator with a second consistency pass over ambiguous cases" ([arXiv:2609.25911v1](https://arxiv.org/abs/2609.25911v1)). The authors still call the result preliminary.

## Key Takeaways

- Fix the escalation budget first, then compare policies on calls per captured case. That number, not AUC, decides whether routing pays.
- Fit and score on fields that exist when the pull request opens; post-hoc history lifted top-20% recall from 0.514 to 0.653 and none of it is available at decision time.
- Treat the ranking as a spending order, not an admission test — the unrouted 80% keeps its normal review.
- Build this only when one invocation costs a checkout, a repair attempt, and a CI run. A cheap diagnosis prompt does not justify the pipeline.

## Related

- [Delegating Dependabot Pull Request Triage to an Agent](dependabot-pr-triage-delegation.md) — the same queue handled by a digest-only agent, with the boundary set by the tool grant rather than a score.
- [Static Difficulty Estimation for Agent Issue Triage](../verification/static-difficulty-estimation-issue-triage.md) — the repository-level counterpart, where the strongest published predictor is measured on the gold patch.
- [Per-Task Verification Budget: Size the Task to Fit the Check](per-task-verification-budget.md) — fixing the budget first and admitting work against it.
- [Oracle-Gated Delegation Beyond Your Domain Expertise](oracle-gated-delegation.md) — when a cheap decisive check lets you delegate work you cannot review yourself.
- [Auto-Triage Workflow: Bug-Monitoring Agent that Connects Related Reports and Opens Fix PRs](auto-triage-workflow.md) — the downstream stage this router decides to invoke.
