---
title: "Copilot Adaptive Review Effort and Secret Detection"
term: "Adaptive Review Effort"
description: "Copilot code review can choose Lite, Balanced, or Max per pull request, capped by a maximum, and flag secrets in review comments. Both are in preview, and the gaps are listed."
aliases:
  - Copilot Adaptive review
  - Copilot code review secret detection
  - adaptive review effort
tags:
  - code-review
  - copilot
  - security
last_reviewed: 2026-11-23
maturity: emerging
---

# Copilot Adaptive Review Effort and Secret Detection

> Copilot code review can pick its own effort level for each pull request and flag exposed secrets in review comments, both in public preview.

Adaptive is a Copilot code review effort setting. Copilot reads each pull request's complexity and risk, then reviews it at Lite, Balanced, or Max. Secret detection is a separate review feature that flags exposed credentials in review comments. GitHub announced both on 2026-11-17, and the changelog lists them for Copilot Pro, Pro+, Max, Business, and Enterprise plans ([GitHub Changelog, 2026-11-17](https://github.blog/changelog/2026-11-17-copilot-code-review-adaptive-effort-secret-detection-and-more/)).

Adaptive sets how hard the reviewer reads. Secret detection adds one more thing it looks for. Neither replaces a check you run yourself.

## How Adaptive picks a level

Before Adaptive, someone chose the level in settings or when requesting the review. The changelog gives two examples: a documentation update may need only Lite, and a change to authentication logic benefits from Max. Adaptive makes that choice, and each review shows which level it picked ([GitHub Changelog](https://github.blog/changelog/2026-11-17-copilot-code-review-adaptive-effort-secret-detection-and-more/)).

| Level | What GitHub says it does | Typical range per review | Approximate average |
|-------|--------------------------|--------------------------|---------------------|
| Lite | Standard review, fast and targeted | $0.05 to $1 | $0.25 |
| Balanced | Higher-reasoning model for complex logic, security-sensitive code, and cross-service changes | $0.25 to $5 | $1.50 |
| Max | Multiple high-reasoning models, for the pull requests that need the most scrutiny | $1.50 to $25 | $10 |

Source: [GitHub Docs: GitHub Copilot code review](https://docs.github.com/en/copilot/concepts/agents/code-review). The figures are GitHub's estimates in USD, and they exclude GitHub Actions minutes.

You pick Adaptive for one pull request from the Reviewers bar, or set it as the default in personal, repository, organization, or enterprise settings. Balanced remains the default ([GitHub Changelog](https://github.blog/changelog/2026-11-17-copilot-code-review-adaptive-effort-secret-detection-and-more/)). The docs say the same: "the review effort level defaults to Balanced, not Adaptive" ([GitHub Docs](https://docs.github.com/en/copilot/concepts/agents/code-review)). The pull request overview comment shows the level used for each review run (same page).

## The maximum caps Adaptive

Adaptive "never picks a level above the maximum review effort level set for your enterprise, organization, or repository" ([GitHub Changelog](https://github.blog/changelog/2026-11-17-copilot-code-review-adaptive-effort-secret-detection-and-more/)). The "Maximum review effort" setting takes No limit, Lite, Balanced, or Max. At organization and enterprise scope, lower scopes cannot exceed it ([GitHub Docs: Configuring code review](https://docs.github.com/en/copilot/how-tos/copilot-on-github/set-up-copilot/configure-code-review)).

Two consequences follow, and both are inference from those statements. The maximum is also the most expensive tier an Adaptive default can bill at. A maximum of Lite makes Adaptive behave as Lite on every pull request.

## What GitHub leaves unstated about Adaptive

The changelog and the two Docs pages cited here name "complexity and risk" as the inputs. They give no signals, thresholds, or per-level bug-discovery rates. They show which level ran, not why. Both Adaptive and Max are marked "in public preview and subject to change" ([GitHub Docs](https://docs.github.com/en/copilot/concepts/agents/code-review)).

You therefore cannot predict a level from a diff. You can audit after the fact by reading the overview comments. [Tunable Effort Levels for Code Review Agents](tunable-review-effort.md) covers why a level without a published curve is a weak basis for routing.

## Secret detection in reviews

Copilot code review "points out exposed credentials in review comments, so you can remove them before you merge" ([GitHub Changelog](https://github.blog/changelog/2026-11-17-copilot-code-review-adaptive-effort-secret-detection-and-more/)). GitHub describes two detection types:

- Known formats. 500+ secret types, built with 150+ partners in the secret scanning partnership program, found by deterministic methods such as regex.
- AI/ML-detected secrets. Secrets with no recognizable format, found with LLMs and GitHub's purpose-built secret model.

To turn it on, open repository or organization settings, then Copilot, then Code review (same changelog).

### Where it sits next to push protection

Push protection acts before the push, and a person must handle everything after it ([Push-Boundary Secret Defense](../security/push-boundary-secret-defense-agent-volume.md)). A review comment arrives later, on a pull request that already holds the commit. That ordering is an inference: the changelog does not say when in the flow the check runs.

The inference changes what the finding means. GitHub's secret scanning docs say to rotate an exposed credential immediately, and that removing it from Git history is time-intensive and often unnecessary once it is revoked ([GitHub Docs: Secret scanning](https://docs.github.com/en/code-security/concepts/secret-security/secret-scanning)). Treat a review finding as an exposure to rotate. Deleting the line does not undo it.

### What the changelog does not say

- It gives no precision or recall figures, for either detection type.
- It does not say whether a finding creates a secret scanning alert, notifies the provider, or blocks a merge. Copilot's reviews "do not count toward required approvals" by default ([GitHub Docs](https://docs.github.com/en/copilot/concepts/agents/code-review)), and nothing cited here makes a flagged secret a merge gate.
- It calls part of the approach "non-deterministic". An inference follows: the same diff may not yield the same finding on every run, so a clean review does not clear a pull request.
- It lists Copilot plans and does not mention GitHub Secret Protection. The secret scanning docs say private and internal organization repositories get secret scanning with Secret Protection enabled ([GitHub Docs: Secret scanning](https://docs.github.com/en/code-security/concepts/secret-security/secret-scanning)). Check which applies to your plan.

## What your own checks still cover

- A deterministic secret scan before commit or in CI. [Deterministic Guardrails](../verification/deterministic-guardrails.md) lists secret detection as a pre-commit check.
- Push protection, which acts before the push.
- Path-based human escalation for high-risk code. Adaptive's idea of risk is undocumented, so [tiered code review](tiered-code-review.md) rules on auth and payment paths stay yours.
- A rotation runbook for the finding that does land in a review comment.

## Example

An organization owner sets "Default review effort level" to Adaptive and "Maximum review effort" to Balanced, both settings named in GitHub's configuration docs. Copilot now chooses between Lite and Balanced for each pull request and never picks Max. If Adaptive picks Lite for a documentation fix, its cost falls in the $0.05 to $1 range. The cap has a cost: the changelog's own example says an authentication change benefits from Max, and under this cap it gets Balanced at most. The owner raises the maximum, or adds a human reviewer on the auth paths.

## When this backfires

- The cap sits below what the risky code needs. The example above shows it.
- The preview moves. Both features are "subject to change", so a policy written around today's behavior can break silently.
- Cost becomes variable. A fixed Balanced default has one cost range. An Adaptive default spreads across up to three.
- A quiet secret check reads as clearance. Without published recall, silence in a review proves nothing about the diff.

## Key Takeaways

- Set the maximum review effort before turning on Adaptive. It caps the level Adaptive can pick, and by inference the cost tier it can bill at.
- Adaptive shows which level ran and gives no reason, so audit by sampling overview comments.
- Treat a secret finding in a review as an exposure to rotate. The finding most likely arrives after the commit is on the pull request branch, though the changelog does not say when the check runs.
- Keep a pre-commit scan and push protection. The changelog publishes no recall figure for review-time detection.

## Related

- [Tunable Effort Levels for Code Review Agents](tunable-review-effort.md) — the per-PR dial, Cursor's and Copilot's earlier effort levels
- [Configuring the Code Review Request Surface](review-request-surface.md) — where the effort level is set and who pays for it
- [Tiered Code Review](tiered-code-review.md) — risk-based escalation to human review
- [Signal Over Volume in AI Review](signal-over-volume-in-ai-review.md) — why a quiet reviewer can mislead
- [Push-Boundary Secret Defense](../security/push-boundary-secret-defense-agent-volume.md) — the push-time block and rotation queue
