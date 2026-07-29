---
title: "Supply-Chain Security Debt in Agent Pull Requests"
term: "Supply-Chain Security Debt"
description: "In a study of 4,022 agent-authored PRs, 82.3% of security smells were supply-chain integrity issues concentrated in CI and Docker files — target review at high-impact infra paths."
tags:
  - security
  - code-review
  - arxiv
  - tool-agnostic
aliases:
  - agent PR supply-chain debt
  - agent-authored PR security smells
last_reviewed: 2026-07-29
maturity: emerging
---

# Supply-Chain Security Debt in Agent Pull Requests

> Most agent-PR security smells are unpinned CI and Docker supply-chain references — target review at high-impact infra paths, not every diff.

This applies when your agent PRs touch GitHub Actions workflows, Dockerfiles, or dependency manifests. If your agents only edit application code and docs, the finding below does not describe your risk.

An empirical study of the AIDev dataset classified security smells across 16,112 file changes in 4,022 agent-authored pull requests and found that 38.9% of those PRs carry at least one security smell, of which 82.3% are supply-chain integrity issues ([arXiv:2607.12428](https://arxiv.org/abs/2607.12428)). GitHub Actions workflows and Docker files together held 87.6% of all detected smells. So review of agent PRs pays off most where the debt concentrates — the infrastructure paths — not spread evenly across every changed line.

## Read the 82.3% as scoped, not absolute

The study restricted its corpus to high-risk file paths and to added lines only ([arXiv:2607.12428](https://arxiv.org/abs/2607.12428)). Scoping to CI and container files over-represents supply-chain smells by construction, so 82.3% describes the smell mix inside those paths, not the share of all agent security problems. Two more limits keep the number honest: the LLM-as-a-judge detector recovered 77.5% of smells against a manually-labeled gold standard (precision 0.908, F1 0.836), so real prevalence is higher than reported; and a "smell" is a hardening gap such as a mutable tag, not a confirmed exploit. Treat the finding as a signal about where to look, not a severity score.

## The credential leaks are a collaboration problem

The critical-severity slice tells a sharper story. Of 253 critical smells, 99.6% were hard-coded credentials, and of the 74 confirmed genuine secrets, 67.6% were introduced by human collaborators rather than the agents ([arXiv:2607.12428](https://arxiv.org/abs/2607.12428)). Worse, 81.1% of those secrets reached integration with no review comment from any bot or human. So the target is not distrust of agents specifically — humans leaked more secrets than the agents did. Agent-driven velocity outpaces human-in-the-loop review, and the same gap swallows secrets from either author. The fix belongs in CI, applied to every PR regardless of author: secret scanning with push protection, SHA-pinning policy, and pinned base images.

## Why it works

Supply-chain smells cluster because agents and humans reference GitHub Actions and Docker images by mutable tags such as `@v4` or `:latest` instead of immutable commit SHAs or digests. A mutable tag is a pointer the upstream owner can move: if that account is compromised, the tag silently resolves to malicious code on the next CI run. The tj-actions/changed-files compromise of March 2025 is the realized case — an attacker repointed more than 350 tags to a commit that dumped runner secrets into build logs, affecting over 23,000 repositories ([Unit 42](https://unit42.paloaltonetworks.com/github-actions-supply-chain-attack/)). Pinning to a full commit SHA removes the mutable pointer, which is why GitHub added policy-level SHA-pinning enforcement ([GitHub Changelog](https://github.blog/changelog/2025-08-15-github-actions-policy-now-supports-blocking-and-sha-pinning-actions/)). GitHub reports it now holds workflows it flags as potentially malicious for human approval before they run, a further platform-side, CI-layer control for the same agent-authored-workflow risk ([GitHub Changelog](https://github.blog/changelog/2026-07-28-github-actions-holds-potentially-malicious-workflows-for-approval)). An independent study of agentic PRs found agents concentrate their security-relevant work in configuration and CI surfaces, which is exactly where this debt accrues ([arXiv:2601.00477](https://arxiv.org/abs/2601.00477)).

## When this backfires

- Agent PRs dominated by docs and refactors that never touch CI, Dockerfiles, or manifests: a supply-chain-focused gate adds friction with almost nothing to catch.
- Repos that already enforce SHA-pinning policy, secret push protection, and pinned base images: the counted smells are blocked deterministically, so extra manual review is redundant.
- Teams with no security-triage capacity: turning on scanners without a responder produces noise that trains reviewers to dismiss alerts — the review-fatigue mode the authors explicitly warn against ([arXiv:2607.12428](https://arxiv.org/abs/2607.12428)).
- Single-agent or single-platform shops: the AIDev distribution aggregates many agents and may not match one tool's mix — measure your own before wiring policy to the 82% figure.

## Example

An agent opens a PR adding a workflow step that references a popular action by tag:

**Before — mutable tag, repointable by the upstream owner:**
```yaml
- uses: tj-actions/changed-files@v44
```

**After — pinned to a full commit SHA, with the tag kept as a comment:**
```yaml
- uses: tj-actions/changed-files@<full-40-char-commit-sha>  # v44
```

The pinned form is what survived the March 2025 compromise: workflows referencing `@v44` picked up the malicious commit, while workflows pinned to a known-good SHA never resolved to it ([Unit 42](https://unit42.paloaltonetworks.com/github-actions-supply-chain-attack/)). Enforce the pin as a CI check so the gate does not depend on a reviewer spotting the tag.

## Key takeaways

- In-scope agent PRs carry security debt concentrated in supply-chain integrity — unpinned CI and Docker references — with 87.6% of smells in workflow and Docker files ([arXiv:2607.12428](https://arxiv.org/abs/2607.12428)).
- Read 82.3% as the smell mix inside high-risk paths, not the share of all agent security issues; the corpus was scoped to those paths and detector recall was 77.5%.
- Hard-coded credentials were the critical failure, but humans introduced most of them — put secret scanning and SHA-pinning in CI for every author, not as author-conditional distrust of agents.
- Agent velocity outpaces human review: 81.1% of confirmed secrets reached integration unreviewed, so deterministic CI gates beat manual inspection here.
- Route review effort to the paths that hold the debt; skip the gate on agent populations that never touch infra files.

## Related

- [Agent-Emitted Dependency Version Ranges Widen the Supply-Chain Attack Surface](agent-emitted-dependency-ranges.md) — the manifest-level sibling of the unpinned-tag problem
- [The Security Review Gap in AI-Authored PRs](../code-review/security-review-gap-in-ai-prs.md) — the complementary code-level view: six CWEs that survive review
- [Reviewer's Playbook for Agent-Authored Pull Requests](../code-review/reviewers-playbook-agent-authored-prs.md) — the inspection order that puts CI and security boundaries early
- [Always-On Agentic PR Security Review](always-on-pr-security-review.md) — the operational pattern for running the gate at PR time
- [Secrets Management for Agents](secrets-management-for-agents.md) — closing the hard-coded-credential leg with proper secret handling

## Sources

- [arXiv:2607.12428](https://arxiv.org/abs/2607.12428) — Sakib, Banik, Jadliwala, "Trust but Verify? Uncovering the Security Debt of Autonomous Coding Agents" (KDD 2026 AgenticSE workshop): primary study
- [arXiv:2601.00477](https://arxiv.org/abs/2601.00477) — "Security in the Age of AI Teammates": agent security work concentrates in config/CI surfaces
- [Unit 42 (Palo Alto Networks)](https://unit42.paloaltonetworks.com/github-actions-supply-chain-attack/) — tj-actions/changed-files supply-chain compromise, March 2025
- [GitHub Changelog, 15 Aug 2025](https://github.blog/changelog/2025-08-15-github-actions-policy-now-supports-blocking-and-sha-pinning-actions/) — policy-level SHA-pinning enforcement
- [GitHub Changelog, 28 Jul 2026](https://github.blog/changelog/2026-07-28-github-actions-holds-potentially-malicious-workflows-for-approval) — GitHub Actions holds flagged workflows for human approval
