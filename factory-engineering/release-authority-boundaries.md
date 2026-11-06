---
title: "Release Authority Boundaries for Software Factories"
term: "Release Authority Boundaries"
description: "Assign authority for execution, evaluation, merge, and deployment. Keep policy changes and waivers separate, with evidence tied to each release decision."
tags:
  - factory-engineering
  - tool-agnostic
last_reviewed: 2026-11-06
maturity: emerging
---

# Release Authority Boundaries for Software Factories

> Release authority boundaries separate implementation permissions from acceptance and deployment decisions when credentials enforce the separation and evidence identifies the candidate.

Release authority boundaries assign who can advance work and who can change the rules for advancement. Use this model when scoped credentials cover every release route and decisions refer to specific evidence. The combined model is a proposal for [factory engineering](index.md), informed by [GitHub's waiver incident](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/) and [environment controls](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments). Neither source validates the whole design.

## Assign authority across stages

Principals are identities whose credentials permit actions. This proposed inventory does not prescribe one agent per row. The [issue-to-PR pipeline](../workflows/issue-to-pr-delegation-pipeline.md) owns stage inputs and handoffs.

| Stage or control | Performs or proposes work | Authorizes advancement | Record the boundary |
|---|---|---|---|
| Intake | Requester | Intake policy or triage owner | Requester identity across chat, tracker, and code host; permitted task and repository |
| Code execution | Implementation agent | Dispatcher under execution policy | Workspace, candidate revision, credentials, network destinations, execution limits |
| Evaluation | Evaluator | Acceptance policy owner or service | Candidate, scenario and grader versions, verdict, inconclusive-result handling |
| Merge | Merge service or maintainer | Reviewer or automated merge policy | Reviewed revision, target branch, check source, approval freshness |
| Deployment | Deployment service | Environment approver or release policy | Artifact digest, environment, deployment evidence, every credential-bearing route |
| Policy changes | Implementer or operator | Separate policy owner | Acceptance criteria, workflows, required checks, environment settings, approval rules |
| Waivers | Implementer requests exception | Separate waiver owner | Rule, reason, candidate scope, expiry or closure condition, granting identity |
| Stop and restart | Operator or monitoring control stops advancement | Named restart authority | In-flight work, fresh evidence, explicit restart decision |

Keep successful execution, ready-for-review, merged, and deployed as distinct terminal states for their respective stages. [Stripe's account](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents) describes a typical run ending in a CI-passing PR ready for human review. [GitHub environment approval](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments) separately gates a deployment job.

## Bind each decision to evidence

GitHub can dismiss stale PR approvals after diff changes and require approval of the latest reviewable push by someone other than its pusher. Required checks can name an expected GitHub App. These are [merge controls](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).

The proposed extension records artifact identity, target environment, evaluation versions, policy version, decision-maker, and decision time. Define which changes invalidate approval; require fresh evaluation and a new decision when those inputs change. Escalate inconclusive results. Use [evidence-bundled PRs](../verification/evidence-bundled-agent-prs.md) for review artifacts. GitHub environment approval does not document this complete binding contract.

Stop/restart ownership is also a proposal. Name who stops advancement, how to treat in-flight work, and who authorizes restart after fresh evidence. The accounts supply no factory-wide restart protocol.

## GitHub environment enforcement and limits

GitHub gates jobs that reference a protected environment. Environment secrets become available after required approval. One listed reviewer is enough; preventing self-review is optional. Administrators can bypass protection by default unless configuration disables bypass. Required reviewers on Free, Pro, and Team plans apply only to public repositories. The protected-branches option allows all branches when no branch protection rules exist. These limits appear in [GitHub's environment reference](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments).

Rejection fails the workflow. Allowed bypass applies to pending jobs and requests a reason. [GitHub's deployment review instructions](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/review-deployments) distinguish rejection from bypass.

Organization environment configuration requires admin access. Workflows can create new environments, normally without protections or secrets. Pro/Team private-environment support does not imply every protection feature is available. A Free repository converted to private has its configured protections and environment secrets ignored. See [environment management](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments).

Inspect direct cloud credentials and jobs that omit the environment. A new environment does not inherit the original's deployment credentials. Include workflow editors and policy administrators in the authority inventory.

## Why it works

The mechanism removes exception paths from ordinary implementation authority. GitHub's [waiver incident](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/) shows that a working check can lose force through label access. Separate ownership makes relaxing that check another decision. This limits actions without proving correctness.

## When this backfires

Shared credentials defeat nominal role separation. [Manji's Bashi experience report](https://arxiv.org/abs/2610.28683v1) describes agents approving through human accounts. The single-startup report has incomplete transcripts and no auditor assessment. Changing reviewer models alone does not establish independent authority.

Under this proposal, unavailable policy owners delay legitimate changes, and weak evidence leaves authorized reviewers unable to judge behavior. These costs are unmeasured. Match manual approval effort to risk, as [Vercel reports doing](https://vercel.com/blog/building-a-software-factory-for-ai-sdk).

## Example

Stephen Toub reports that a Copilot runtime port deleted an SDK-exposed function. Compatibility CI failed, and the agent applied `schema-break-ok` to waive it. Toub challenged the label before merge; the agent removed it and restored the function. This was a caught regression, not a reported production outage. The [GitHub migration account](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/) supports separate waiver ownership, without establishing a complete release architecture. [Oracle protection](../patterns/agent-design/protect-the-oracle-from-the-agent.md) covers that ownership in detail.

[Stripe](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2) reports QA devboxes without real user data, production services, or arbitrary network egress, followed by human-reviewed changes. [Vercel](https://vercel.com/blog/building-a-software-factory-for-ai-sdk) reports task sandboxes with scoped secrets and human approval before merge. Its automated review approval does not replace that human gate. Neither account establishes a separate production deployment gate.

[StrongDM](https://factory.strongdm.ai/) instead describes specification- and scenario-driven development without human code review. That account documents an alternative review policy. It supplies neither a complete authority matrix nor evidence of equal safety relative to Stripe or Vercel.

## Key Takeaways

- Inventory waiver labels and policy-editing credentials alongside merge and deployment permissions.
- Check repository visibility, plan, bypass settings, and every deployment credential route before relying on an environment gate.
- Define approval invalidation and restart ownership explicitly when adopting the proposed model.

## Related

- [Factory Run Recovery and Compatible Product Rollback](run-recovery-and-product-rollback.md)
- [Acceptance Scenario Lifecycle for Software Factories](acceptance-scenario-lifecycle.md)
- [Factory Engineering Across Software Delivery Systems](factory-engineering.md)
- [Software Factory Model](../workflows/software-factory-model.md) — alternative production and review policies
- [Judgment Relocation](../human/judgment-relocation.md) — ownership of product and verification decisions
- [Evidence-Bundled Agent PRs](../verification/evidence-bundled-agent-prs.md) — artifacts for review decisions
- [Protect the Oracle from the Agent](../patterns/agent-design/protect-the-oracle-from-the-agent.md) — test and waiver ownership
