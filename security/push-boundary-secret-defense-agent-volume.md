---
title: "Sizing Secret Defense at the Push as Agent Volume Grows"
term: "Push-Boundary Secret Defense"
description: "Secret remediation needs a person per leak, so agent push volume grows the queue. Move work out of it with short-lived credentials, push-time blocks, and issuer revocation."
aliases:
  - push-time secret blocking
  - secret remediation capacity
tags:
  - security
  - copilot
last_reviewed: 2026-10-09
maturity: emerging
---

# Sizing Secret Defense at the Push as Agent Volume Grows

> A push-time block costs compute and scales with agent push volume. Cleanup after a leak costs a person's time and does not.

Secret defense has two halves with different cost curves. Before a push, stopping a secret is a binary decision a machine makes in milliseconds. After the push, a person must find the alert, revoke or rotate the credential, and confirm the fix. GitHub's secret scanning product lead puts it this way: "Prevention scales with compute, but remediation still scales with people." ([GitHub blog](https://github.blog/ai-and-ml/github-copilot/secret-protection-must-scale-with-software/)) The practical rule: when agents raise push volume, move as much leak handling as you can out of the human queue.

This page applies only under the conditions in the next section. It is a capacity argument, not a claim about how often agents leak.

## When this applies

- Your agents push to GitHub repositories at a volume that grows faster than your security staff.
- Your leaks are mostly provider-issued tokens, which push protection recognizes. Internal passwords and unstructured secrets fall outside its patterns.
- Your credentials are long-lived. If you already issue only short-lived credentials, there is little left to block.

## The figures, with their limits

Every number below comes from one GitHub post dated October 7, 2026. The post leaves several populations unstated, so each figure carries its qualifier.

| Figure | Qualifier |
|--------|-----------|
| One in three pull requests on GitHub involves an AI agent, against fewer than one in 10 a year earlier | GitHub's claim, linked to a Microsoft earnings page that this page did not check |
| Push protection stops about 30% of newly detected secrets before they enter history; the other 70% surface after exposure | The source states it "when including additional secret types" and gives no population or period |
| Mean time to manually revoke a secret is around 40 days; roughly one in five took more than 90 days | No population, period, or definition of "manually" |
| In Q2 2026, 0.47% of 574M public pushes carried a detected secret | Supported provider patterns only |
| Developer overrides of push-path blocks fell from 6.63% to 3.93% | The author reads this as evidence against carelessness; it is not a measured cause |

Source: [GitHub blog](https://github.blog/ai-and-ml/github-copilot/secret-protection-must-scale-with-software/).

The post also offers a forecast: "If that pace holds, within the next two years, most of the code pushed to GitHub could be written by an agent." That is a conditional projection, not a measurement.

The post does not split secret prevalence by human or agent authorship. Do not read these figures as saying agent-authored commits leak more or less often.

## Why it works

The load argument is linear. In the source's words: "At a fixed rate, doubling activity doubles expected exposures. If each exposure requires the same human response, the workload doubles too." ([GitHub blog](https://github.blog/ai-and-ml/github-copilot/secret-protection-must-scale-with-software/)) The source reports no statistically detectable trend in per-push prevalence across nine quarters, while screened pushes grew 2.84 times and pushes carrying credentials grew 2.59 times. Volume, not a rising rate, drives the queue.

Cleanup stays human for a technical reason. GitHub's documentation says a leaked secret first needs revoking or rotating, and that "You cannot remove sensitive data from other users' clones of your repository" ([GitHub docs](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)). A history rewrite does not undo the exposure.

A second dataset points the same way. GitGuardian found that the validity rate of credentials confirmed valid in 2022 was still above 64% in January 2026, and that new public secrets grew 34% against 43% growth in public commits in 2025 ([GitGuardian](https://blog.gitguardian.com/the-state-of-secrets-sprawl-2026/)). Leaks roughly track volume, and the backlog does not clear.

## Three levers that remove human work

Rank the levers by where they act.

1. Short-lived credentials. With OpenID Connect, "your cloud provider issues a short-lived access token that is only valid for a single job, and then automatically expires." ([GitHub docs](https://docs.github.com/en/actions/concepts/security/openid-connect)) A token that expires has little left to leak.
2. A push-time block. A coding agent can act on this lever inside its own loop. GitHub is adding its new classifier to the `/security-review` command in Copilot CLI and Copilot App, "so Copilot users can address secrets before a push even without needing an organization's GitHub Secret Protection plan." ([GitHub blog](https://github.blog/ai-and-ml/github-copilot/secret-protection-must-scale-with-software/))
3. Issuer revocation. Once GitHub notifies partners, "a large number of these partners immediately revoke the token," so revocation can happen "without waiting for a developer to find and process a GitHub alert." ([GitHub blog](https://github.blog/ai-and-ml/github-copilot/secret-protection-must-scale-with-software/))

Auto-revocation also removes people from the queue, but only for partner secret types.

## Setting up the push-time block for agents

1. Turn on push protection for repositories where agents push. It covers only a subset of the most identifiable patterns ([GitHub docs](https://docs.github.com/en/code-security/reference/secret-security/secret-scanning-detection-scope)).
2. Delegate bypass. By default, "anyone with write access to the repository can bypass push protection by specifying a bypass reason," and choosing "false positive" creates a closed alert ([GitHub docs](https://docs.github.com/en/code-security/concepts/secret-security/about-push-protection)). An agent that can pick its own bypass reason can clear its own block, so route bypass requests to a reviewer.
3. Run `/security-review` in Copilot CLI or Copilot App before the agent pushes, so it sees the finding in its own session.

## When this backfires

- Your leaks are internal or unstructured. Standard push protection blocks only the lowest-false-positive patterns, so a database password an agent copies from a config file passes through unless the new classifier is enabled ([GitHub docs](https://docs.github.com/en/code-security/reference/secret-security/secret-scanning-detection-scope)). The post-push share of 70% exists partly for this reason.
- You already use short-lived credentials. The classifier consumes AI credits and was in private preview at publication, with availability to organizations with GitHub Secret Protection promised later that month ([GitHub blog](https://github.blog/ai-and-ml/github-copilot/secret-protection-must-scale-with-software/)). The post also notes that a false positive interrupts a developer and makes the next block harder to trust.
- Bypass is not delegated. The block then moves the human decision to a moment with less review instead of removing it.
- The push is large or the history is complex. GitHub documents that a bypass request without commit or file path details means push protection ran out of time ([GitHub docs](https://docs.github.com/en/code-security/reference/secret-security/secret-scanning-detection-scope)). Bulk agent refactors and monorepo imports are the likely cases.
- Your secret types sit outside the partner program. Issuer revocation does not apply, so alerts still land on a person, and the 40-day figure may not describe your case.

A practitioner can fairly argue that money spent on a faster classifier buys less than money spent making credentials short-lived. The sources here do not settle it. The order matters if you can fund only one.

## Conflicting evidence on agent leak rates

GitHub reads its falling override rate as a challenge to "the common claim that agents are causing developers to become more careless." GitGuardian reports a different picture: "Claude Code-assisted commits showed a 3.2% secret-leak rate , versus a 1.5% baseline across all public GitHub commits ." It adds that the gap "should not be read as a simple tool failure." ([GitGuardian](https://blog.gitguardian.com/the-state-of-secrets-sprawl-2026/))

The two figures use different units, commits against pushes, and the sources do not say whether they control for repository type. This page does not resolve the conflict. The capacity argument holds either way, because it depends on volume and not on who writes the code.

## Key Takeaways

- Remediation work scales with push volume at a fixed per-push exposure rate, so a growing agent share of pushes grows the queue.
- Size defenses by how much human work they remove, using short-lived credentials, push-time blocks, and issuer revocation together.
- Carry each number with its qualifier. The 30% split, the 40-day figure, and the authorship question all lack a stated population.
- Delegate bypass so an agent cannot clear its own block.
- Push protection misses internal and unstructured secrets, so it does not replace rotation or short-lived credentials.

## Related

- [Credential Hygiene for Agent Skill Authorship](credential-hygiene-agent-skills.md)
- [Secrets Management for Agent Workflows](secrets-management-for-agents.md)
- [Supply-Chain Security Debt in Agent Pull Requests](supply-chain-security-debt-agent-prs.md)
- [Scoped Credentials via Proxy Outside the Agent Sandbox](scoped-credentials-proxy.md)
- [Scanner-as-MCP-Server: Secret and Dependency Scans as Typed Agent Tools](scanner-as-mcp-server.md)
