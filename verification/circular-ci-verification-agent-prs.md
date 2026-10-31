---
title: "Circular CI Verification in Dual-Scope Agent PRs"
term: "Circular CI Verification"
description: "When an agent pull request edits the CI workflow that validates it, the passing check is self-referential, so require one non-author human approval on those paths."
tags:
  - testing-verification
  - code-review
  - security
  - tool-agnostic
  - arxiv
aliases:
  - dual-scope agent pull request
  - non-author approval on infrastructure paths
  - circular verification paradox
last_reviewed: 2026-10-12
maturity: emerging
status: current
---

# Circular CI Verification in Dual-Scope Agent PRs

> Circular CI verification supplies no independent assurance when an agent PR edits its own workflow; require non-author human approval on those paths.

Require one explicit non-author human approval when an agent pull request touches the deployment paths your own verification runs on, such as `.github/workflows/**`, `terraform/**`, or `k8s/**`. The key is the path intersection, not the rest of the diff. Soualhi and Suleiman recommend path-based CODEOWNERS entries "coupled with repository rulesets that categorically disable auto-merge capabilities whenever a PR intersects with sensitive infrastructure directories" ([arXiv:2610.12849v1](https://arxiv.org/abs/2610.12849v1)). Application-only PRs stay ungated.

The rule gates a small share of agent PRs, about 9% to 10% once infrastructure-only PRs count. Across 26,999 pull requests in two datasets, dual-scope PRs were 4.48% of agent PRs in AIDev v5 and 4.55% in MOSAIC-3M. Infrastructure-only PRs were 4.43% in AIDev v5 and 5.29% in MOSAIC-3M. The paper's merge-latency figures cover dual-scope PRs only, so the cost of gating infrastructure-only PRs is unmeasured. Where an agent touched a single infrastructure file, it was a CI/CD manifest in 74.1% of AIDev v5 cases ([arXiv:2610.12849v1](https://arxiv.org/abs/2610.12849v1)).

## Why it works

A passing status check on a PR that changed the checker carries no independent information. The paper states the mechanism plainly: "Because the patch altered the validation logic tasked with verifying it, the passing automated check provides zero independent assurance of build integrity" ([arXiv:2610.12849v1](https://arxiv.org/abs/2610.12849v1)). Industry threat models name the attack this opens as Poisoned Pipeline Execution. A contribution manipulates workflow definitions to reach arbitrary code execution inside build runners. The paper takes the name from Krivelevich and Gil (2022) and the code-execution risk from Koishybayev et al. (2022) and Muralee et al. (2023) ([arXiv:2610.12849v1](https://arxiv.org/abs/2610.12849v1)). The paper recommends non-author human sign-off on those paths. Automated checks derived from the edited workflow cannot supply independent assurance. That makes this the pipeline case of [keeping the oracle out of the agent's reach](../patterns/agent-design/protect-the-oracle-from-the-agent.md): the workflow decides whether the change is correct, so the change must not own it. The property comes from the diff, whoever wrote it, so it does not depend on the statistics below.

## Why the review deficit is the weaker half

The paper's most quotable result is that "the agent's identity reduces the odds of human review by 63.7% compared to human contributors" ([arXiv:2610.12849v1](https://arxiv.org/abs/2610.12849v1)). Check its scope first. The figure comes from one stratum of one dataset: 2,232 MOSAIC-3M PRs by external contributors with zero repository write access, where humans drew review 82.7% of the time and agents 63.6%. AIDev v5 could not support the analysis, because it "lacks explicit author permission metadata".

The silent-merge result reverses sign between the two cohorts. In MOSAIC-3M, dual-scope agent PRs merged with no review 56.2% of the time against 42.5% for application-only (matched OR 2.38, p=0.052). In AIDev v5, the larger matched sample at 687 pairs, oversight went up instead: 43.1% silent for dual-scope against 47.2% application-only (matched OR 0.63, p=0.015). The abstract's "43.1% to 56.2%" is two datasets' endpoints, not a range inside one. The human baseline is flat on the same comparison, because "the external review rate remains statistically flat, shifting from 72.2% to 73.4%" when human developers co-modify infrastructure ([arXiv:2610.12849v1](https://arxiv.org/abs/2610.12849v1)). Author identity is what the deficit tracks, and a path rule keys on paths. Gate on the pair, author identity and path, or the control misses the variable the statistic measured.

## What the gate costs

The study measures merge-time differences between PR types, not the causal cost of adding an approval gate. In AIDev v5, dual-scope PRs merged in a median of 16.60 hours against 3.47 hours for matched application-only controls, a +13.13-hour difference and a 3.237x time ratio ([arXiv:2610.12849v1](https://arxiv.org/abs/2610.12849v1)). In MOSAIC-3M the same paired comparison was 2.21 against 2.93 hours and not statistically significant (p=0.803).

Two of four infrastructure subdomains produced the AIDev v5 delay: CI/CD manifests at a 3.827x time ratio (p<0.001) and system provisioning at 2.727x (p=0.0070). Automation scripts and containerization showed no significant penalty ([arXiv:2610.12849v1](https://arxiv.org/abs/2610.12849v1)). The split inside dual-scope says where that cost lands. Core source code alongside infrastructure reached a 19.64-hour median; application configuration alongside infrastructure merged in 1.13 hours, faster than the application-only baseline. The second shape shows no delay in the data, which is a reason to apply the rule to every path match.

## When this backfires

- A CI-enforced path allowlist already denies those paths to the agent. The approval then reviews a diff that cannot exist.
- Review capacity is already the binding constraint. A creation-time triage model over 33,707 agent PRs reports: "At a 20% review budget, this approach captures 69% of the high-effort PRs" ([arXiv:2601.00753v2](https://arxiv.org/abs/2601.00753v2)). That result concerns review triage; it does not establish whether adding this approval gate improves review quality.
- A case-control study of 516 Chromium OS reviews that caught a security defect against 374 that missed one found "opposite effects are observed from the number of directories under review" ([arXiv:2102.06909v1](https://arxiv.org/abs/2102.06909v1)). In that study, which predates agent PRs, more directories under review is associated with fewer security defects caught.
- Your repository sits outside the study's support. It covers merged PRs only, repositories over 100 stars, and June to July 2025 agent versions, and the authors state the findings "may not generalize to personal hobby projects nor to proprietary enterprise monorepos employing dedicated Site Reliability Engineering teams, custom distributed build systems, and automated canary deployment gates" ([arXiv:2610.12849v1](https://arxiv.org/abs/2610.12849v1)).

Two measures may offset the review load. A CODEOWNERS study across more than 844,000 pull requests reports: "While roughly 65% of changes were not statistically significant, the consistent direction suggests that CODEOWNERS contributes to smoother and faster PR workflows over time" ([arXiv:2512.05551v2](https://arxiv.org/abs/2512.05551v2)). The Soualhi and Suleiman paper also asks agent runtimes to verify before submitting by "executing local containerized dry-runs (using tools like act to simulate continuous integration workflows locally)". It adds that proactively resolving pipeline incompatibilities "mitigates the protracted integration stalls (spanning 15.59 to 49.80 hours) driven by CI/CD modifications" ([arXiv:2610.12849v1](https://arxiv.org/abs/2610.12849v1)).

## Example

Cilium maintainer André Martins and security-team member Feroz Salam describe a path-based review gate for CI configuration. Their June 2026 report assigns `.github/` to the `github-sec` and `ci-structure` teams. It assigns `auto-approve.yaml` to `cilium-maintainers`. They report that CI changes require explicit review from the responsible team ([Cilium CI/CD security post](https://www.cncf.io/blog/2026/06/04/securing-ci-cd-for-an-open-source-project-controlling-who-runs-what/)).

This illustrates infrastructure-path ownership in a public project. The report does not measure an agent-specific approval gate. To require the review on GitHub, enable code-owner approval in branch protection or the corresponding ruleset. A CODEOWNERS file alone assigns reviewers; the repository rule makes their approval mandatory ([GitHub code-owner documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)).

## Key Takeaways

- Gate on the pair, author identity and infrastructure path. Diff scope alone predicts no change in review: human authors drew 72.2% review without infrastructure and 73.4% with it.
- Justify the gate by the self-referential check. The 63.7% figure comes from one MOSAIC-3M stratum that AIDev v5 cannot test, and the silent-merge result reverses between the datasets.
- Key the gate on the path intersection. A workflow edit with no source change beside it is still self-verifying.
- In AIDev v5, dual-scope PRs merged 13.13 hours later at the median than matched application-only PRs. Dual-scope PRs comprised about 4.5% of agent PRs. MOSAIC-3M showed no significant change. Containers and automation scripts carried no measured penalty, so the cost sits in CI/CD and provisioning.
- Ask the agent to run its workflow locally before it opens the PR. The paper expects this to cut the integration stalls that CI/CD changes cause.

## Related

- [Supply-Chain Security Debt in Agent Pull Requests](../security/supply-chain-security-debt-agent-prs.md) — where the hardening gaps concentrate once you decide to review infrastructure paths.
- [Diff-Coverage Gating for Agent-Authored Pull Requests](diff-coverage-gate-agent-prs.md) — a sibling gate keyed on changed-line coverage rather than on path.
- [Post-Merge Fix Signals for Agent Merges](post-merge-fix-signals-agent-merges.md) — what an unreviewed agent merge costs after it lands.
- [Layered Oracle Stack for Agent IaC Security Repair (TerraProbe)](layered-oracle-iac-security-repair.md) — independent oracles for infrastructure changes a single scanner pass clears.
- [Task Category as the Security Review Routing Key](task-category-security-review-routing.md) — routing review depth by what the change does.
