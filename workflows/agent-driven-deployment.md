---
title: "Agent-Driven Deployment: What to Delegate and What to Gate"
term: "Agent-Driven Deployment"
description: "Delegate the deploy pipeline up to the privileged action, then gate that action with a capability boundary the agent cannot reach rather than a human approval step."
tags:
  - workflows
  - agent-design
  - testing-verification
  - claude
aliases:
  - deploy delegation boundary
  - agent deployment gate
applies_to: "claude-code@2.x"
last_reviewed: 2026-08-11
maturity: emerging
---

# Agent-Driven Deployment: What to Delegate and What to Gate

> Delegate the whole deploy pipeline up to the privileged action, then gate that action with a capability boundary the agent cannot reach.

The delegation boundary sits at the credential, not at the command. A coding agent can write the change, run the checks, build the artifact, and open the pull request without ever holding the credential that reaches production. Everything in this workflow follows from putting that credential outside the agent's environment and letting a machine decide when it gets minted.

## Why the deploy step absorbs the cost of agent velocity

The 2025 DORA report found that AI adoption now correlates positively with software delivery throughput and product performance, and that "AI adoption does continue to have a negative relationship with software delivery stability" ([Google Cloud, 2025](https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report)). The same survey reports 90% of respondents using AI at work and 30% reporting little or no trust in the code it generates. More change arrives per week, and confidence in each change has not risen to match.

The worst case is on record. The AI Incident Database catalogs a Replit agent that "reportedly deleted a live production database during an active code freeze, despite receiving repeated instructions not to make changes", and that "reportedly produced fabricated test results and fake data, and incorrectly claimed rollback was impossible" ([incident 1152](https://incidentdatabase.ai/cite/1152/)). The instruction not to touch production existed. Nothing enforced it.

## Gate the capability, not the decision

Reach for a capability boundary before reaching for an approver. DORA's research on change approval reports that approval by people external to the team has "a negative impact on software delivery performance", and that "no evidence was found to support the hypothesis that a more formal, external review process was associated with lower change fail rates" ([DORA, Streamlining change approval](https://dora.dev/capabilities/streamlining-change-approval/)). The same page describes the second-order cost: heavyweight approval slows delivery into "larger batches less frequently", which carries higher risk per release and, DORA found, higher change fail rates. A human approval step on every agent deploy buys the delay without evidence of the safety.

A capability boundary is a different mechanism. It decides which principal may act, not whether this particular change is good, so it adds no queue and no judgement. This is the deploy-path case of the general split between [enforced and advisory controls](../security/enforced-versus-advisory-controls.md): a control the runtime evaluates bounds the agent, and a control stated in its context does not. The condition that makes this whole workflow work is that the gate is structural. If your gate is a person clicking approve, DORA's finding applies to you.

## Three implementation layers

### Layer 1: Delegated preparation

Everything before the privileged action is safe to delegate: reading the codebase, writing the change, running tests and linters, building the release artifact, drafting release notes, and opening the pull request. This layer is tool-agnostic. Delegating it is also where the throughput gain lives, so do not narrow it out of caution about the layer below.

### Layer 2: The capability boundary

Anthropic's deployment guidance places sensitive resources outside the boundary containing the agent: "rather than giving an agent direct access to an API key, you could run a proxy outside the agent's environment that injects the key into requests. The agent can make API calls, but it never sees the credential itself" ([Securely deploying AI agents](https://code.claude.com/docs/en/agent-sdk/secure-deployment)). Applied to deploys, this means the agent's session never carries cloud credentials at all. The pipeline holds them, and only in the job that runs after the gate.

Claude Code's permission rules belong in this layer as a pre-flight, not as the boundary. The same Anthropic guide is direct about their limit: "This is a permission gate, not a sandbox; it does not infer whether a command is dangerous from its target path or effects."

The pipeline half of this layer is tool-agnostic, since the credential lives in CI rather than in any assistant. Only the pre-flight differs per tool, and Copilot and Cursor each have their own allow and deny mechanics with the same standing: useful for catching a mistake in the session, worthless as the thing standing between an agent and production.

### Layer 3: Independent verification and rollback

The checks that gate the deploy must live outside the agent's write scope, and the previous artifact must stay deployable. Both conditions have the same purpose, which is to keep recovery cheap when the change is wrong. See [rollback-first design](../patterns/agent-design/rollback-first-design.md) for choosing the undo path before the do path, and [verification-gated agent autonomy](../patterns/agent-design/verification-gated-agent-autonomy.md) for scaling review without per-action approval.

## Triggers and authority bounds

| Trigger | Agent authority | What bounds it |
|---|---|---|
| Local session | Edit, test, build, commit | Permission rules and sandbox; no deploy credentials present |
| Pull request | Open, update, respond to review | Branch protection; required status checks the agent cannot edit |
| Merge to main | Build and publish artifact | Path allowlist; artifact is content-addressed and immutable |
| Deploy to production | None | Environment protection rules; credential minted by the pipeline |

The agent's authority drops to zero at the last row, and no row above it can grant what that row withholds.

## Why it works

Deploy authority is a credential rather than an instruction, so it can be withheld structurally instead of behaviorally. GitHub Actions demonstrates the mechanism. With OpenID Connect the workflow requests a short-lived token instead of reading a stored cloud credential ([Configuring OpenID Connect in cloud providers](https://docs.github.com/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-cloud-providers)), and that token's subject claim references the job's environment when the job declares one, as in the documented example `"sub": "repo:octo-org/octo-repo:environment:prod"` ([OpenID Connect reference](https://docs.github.com/en/actions/concepts/security/openid-connect)). The cloud role's trust policy can therefore refuse any token that did not come from a job running in that environment, and the job only reaches that state once the environment's protection rules pass. Environment secrets follow the same rule: "a job cannot access environment secrets until one of the required reviewers approves it" ([Deployments and environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)). An agent inside this pipeline can do all of Layer 1 and remain unable to produce the credential, because nothing in its environment can mint one.

This is the production form of the [lethal trifecta](../security/lethal-trifecta-threat-model.md): repository read access, untrusted content from issues and dependencies, and deploy credentials in one principal. Removing the third leg is cheaper than defending the first two.

## When this backfires

- The gate is a permission rule. Claude Code evaluates rules "in order: deny, then ask, then allow", and a broad deny "can't carry allowlist exceptions" ([Configure permissions](https://code.claude.com/docs/en/permissions)). The same page notes that Read and Edit deny rules "don't apply to arbitrary subprocesses that read or write files indirectly, like a Python or Node script that opens files itself". A deploy invoked through a wrapper script never presents the string the rule was written against.
- The action is not reversible. Schema migrations and data deletions cannot be undone by redeploying the previous artifact. Reviewing them faster does not help; remove the capability from the automated path instead.
- The agent can edit its own gate. The EvilGenie benchmark identifies explicit reward-hacking behavior in both Codex and Claude Code, and detects test-file editing as one signal of it ([Gabor et al., 2026](https://arxiv.org/abs/2511.21654v2)). A pre-flight suite the agent can rewrite sits inside its blast radius.
- Approval degrades to a click. A GitHub environment accepts up to six required reviewers, and "only one of the required reviewers needs to approve the job for it to proceed" ([Deployments and environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)). Agent output outruns what human review can truthfully consume ([verification capacity ceiling](../verification/verification-capacity-quality-ceiling.md)), so you pay DORA's lead-time cost for a change-fail-rate benefit its research did not find.
- Deploy volume is low. A team shipping monthly does not have the change volume that justifies the harness, and the setup cost dominates.
- The artifact is not pinned. An agent deploying from a working copy ships something no check ever saw. Deploy the artifact the merge commit produced, never the session's local state.

## Example

A production environment that no agent can deploy into, expressed as the job that runs after the gate:

```yaml
jobs:
  deploy:
    environment: production      # protection rules evaluated before the job starts
    permissions:
      id-token: write            # request an OIDC token; no stored cloud secret
      contents: read
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::111122223333:role/deploy
          aws-region: us-east-1
```

The role's trust policy conditions on the token's subject claim containing `environment:production`. A local agent session holds no AWS role, no stored key, and no path to this job other than merging a pull request that the pipeline then builds.

## Key Takeaways

- Put the deploy credential outside the agent's environment and let the pipeline mint it after the gate.
- A structural gate escapes DORA's change-approval finding because it selects a principal rather than judging a change.
- Permission rules are a useful pre-flight and a poor boundary, since a wrapper script defeats command-string matching.
- Keep the gating checks outside the agent's write scope, or the gate is inside the blast radius it exists to bound.
- Deploy the artifact the merge produced; a session's working copy has passed nothing.

## Related

- [Risk-Based Shipping](../verification/risk-based-shipping.md) — which change tiers auto-ship and which halt for review
- [Rollback-First Design](../patterns/agent-design/rollback-first-design.md) — choosing the undo path before the do path
- [Verification-Gated Agent Autonomy](../patterns/agent-design/verification-gated-agent-autonomy.md) — automated review in place of per-action human approval
- [Rainbow Deployments for Agents](../patterns/multi-agent/rainbow-deployments-agents.md) — gradual version migration once the deploy has happened
- [Lethal Trifecta Threat Model](../security/lethal-trifecta-threat-model.md) — why deploy credentials are the third leg
