---
title: "Proof of Presence: Re-Authenticating for Agent Actions"
term: "Proof of Presence"
description: "A session or token proves a credential was issued, not presence. Proof of presence re-checks the IdP first, but only over the browser channel it covers."
tags:
  - security
  - agent-design
  - human-factors
  - tool-agnostic
  - arxiv
aliases:
  - step-up authentication
  - IdP re-authentication challenge
last_reviewed: 2026-09-26
maturity: emerging
---

# Proof of Presence: Re-Authenticating for Agent Actions

> A session or token proves issuance, not presence. Proof of presence re-checks the person at the IdP, then opens a sliding two-hour window.

Proof of presence stops an agent under three conditions only: the action runs through the channel the identity provider (IdP) actually checks, no live re-authentication window already covers it, and the IdP demands a factor the agent cannot reach. GitHub shipped a feature by this name as a public preview on 24 September 2026. It extends sudo mode so a member is redirected to their IdP and the action waits until they return having satisfied a named policy. GitHub names the agent threat directly: the redirect blocks "the use of compromised or hijacked credentials or agents going an extra step without your knowledge" ([GitHub Changelog](https://github.blog/changelog/2026-09-24-require-proof-of-presence-for-high-impact-actions)). Treat GitHub's feature as one dated implementation of a broader pattern: bind a high-impact action to a factor the requester does not already hold, and check the mechanism against those three conditions before trusting it against an agent.

## How the challenge works

The redirect asks the IdP for one of two things. "Re-authentication" may accept a password, depending on IdP policy; "MFA" adds a second-factor challenge on top ([Configuring Proof of Presence](https://docs.github.com/en/enterprise-cloud@latest/admin/configuring-settings/hardening-security-for-your-enterprise/configuring-proof-of-presence)). Concretely, satisfying the redirect "might mean performing multi-factor authentication, checking for device compliance, or just signing in again to prove freshness" ([GitHub Changelog](https://github.blog/changelog/2026-09-24-require-proof-of-presence-for-high-impact-actions)). The preview supports Microsoft Entra ID via SAML or OIDC only, scoped to managed-user (EMU) enterprises on github.com and to GHEC-DR ([GitHub Changelog](https://github.blog/changelog/2026-09-24-require-proof-of-presence-for-high-impact-actions)).

It reuses the sudo-mode action list, so "the same protected actions that trigger sudo mode will trigger a PoP challenge" ([Configuring Proof of Presence](https://docs.github.com/en/enterprise-cloud@latest/admin/configuring-settings/hardening-security-for-your-enterprise/configuring-proof-of-presence)): creating a token, editing webhooks, changing organization security settings, and viewing recovery codes ([GitHub Changelog](https://github.blog/changelog/2026-09-24-require-proof-of-presence-for-high-impact-actions)). It also closes a gap sudo mode left open. Before this feature, "only the setup user will receive prompts to enter sudo mode, as managed user accounts don't have credentials stored on GitHub" ([Sudo mode](https://docs.github.com/en/enterprise-cloud@latest/authentication/keeping-your-account-and-data-secure/sudo-mode)), which meant most EMU members had no fresh-auth check on these actions at all. "PoP uses the same session and timeout model as sudo mode" ([Configuring Proof of Presence](https://docs.github.com/en/enterprise-cloud@latest/admin/configuring-settings/hardening-security-for-your-enterprise/configuring-proof-of-presence)). One passed challenge covers further high-impact actions "in that browser session for two hours" ([GitHub Changelog](https://github.blog/changelog/2026-09-24-require-proof-of-presence-for-high-impact-actions)), and "any sensitive action that you perform will reset the timer" ([Sudo mode](https://docs.github.com/en/enterprise-cloud@latest/authentication/keeping-your-account-and-data-secure/sudo-mode)) — so the window slides rather than expiring on a fixed schedule.

## What it does not cover

| Action path | Covered today |
|---|---|
| Web-session actions on the sudo-mode list (webhooks, org security settings, recovery codes) | Yes |
| Minting a new personal access token in the browser | Yes |
| A call made with a PAT or GitHub App token an agent already holds | Not described in either proof-of-presence document; the REST reference for creating a webhook names no re-authentication step ([REST webhooks](https://docs.github.com/en/rest/repos/webhooks)) |
| Merging a pull request | Not yet — GitHub states "support for proof of presence before pull request merges is coming soon" ([GitHub Changelog](https://github.blog/changelog/2026-09-24-require-proof-of-presence-for-high-impact-actions)), a request that traces to FDA 21 CFR Part 11 e-signature needs for PR approvals ([GitHub Community #64212](https://github.com/orgs/community/discussions/64212)) |

A CLI or cloud agent that calls the REST API with a PAT or App token sits on the row the documentation is silent on.

## Why it works

The mechanism moves the authorization decision to a factor the requester does not hold. A session cookie or bearer token proves someone authenticated at some earlier time; a fresh IdP challenge proves the account holder authenticated just now, with a factor the IdP controls. RFC 9470 standardizes this exact gap: a resource server may need "a more recent user authentication" than the token reflects, based on "its own risk evaluation of the API request" ([RFC 9470](https://datatracker.ietf.org/doc/html/rfc9470)). OWASP names the threat that a fresh-credential check removes: without it, "an attacker may be able to execute sensitive transactions through a CSRF or XSS attack without needing to know the user's current credentials" ([OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)).

## When this backfires

- The agent never touches the browser. The challenge fires "when an enterprise member attempts a high-impact action" ([GitHub Changelog](https://github.blog/changelog/2026-09-24-require-proof-of-presence-for-high-impact-actions)). An injected CLI tool, a cloud agent, or a headless run calling the REST or GraphQL API with a PAT or App token it already holds is not on that channel, so it edits a webhook or a ruleset with no redirect at all.
- A browser-driving agent inherits an open window. After a human passes one challenge, the sliding two-hour timer covers every high-impact action in that session, and each one resets the clock rather than closing it ([Sudo mode](https://docs.github.com/en/enterprise-cloud@latest/authentication/keeping-your-account-and-data-secure/sudo-mode)).
- The policy accepts a password. GitHub's own weaker option means a member "may be able to satisfy the challenge with password-based authentication" ([Configuring Proof of Presence](https://docs.github.com/en/enterprise-cloud@latest/admin/configuring-settings/hardening-security-for-your-enterprise/configuring-proof-of-presence)). Only FIDO or WebAuthn resists phishing; a password-grade check does not ([CISA](https://www.cisa.gov/mfa)).
- The action is frequent. If a repository merges many pull requests a day, the planned PR-merge coverage fires on each one. Microsoft warns that setting sign-in frequency to "Every time" "can increase security friction to a point that it causes users to experience MFA fatigue and open the door to phishing." It also warns that "users who habitually enter credentials without thinking might unintentionally provide them to malicious prompts" ([Microsoft Entra](https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-session-lifetime)). Anthropic reports the same reflex elsewhere: Claude Code users approve 93% of permission prompts, with approval fatigue named as the cost ([Anthropic](https://www.anthropic.com/engineering/claude-code-auto-mode)).
- The enterprise runs a different IdP. Outside Entra ID on EMU or GHEC-DR, the preview does not apply, and the same argument needs a different mechanism.

## The token-path equivalent

For an agent that never opens a browser, GitLab already runs the same idea over a different channel: "Require user re-authentication (password or SAML) to approve" forces "potential approvers to first authenticate with SAML or a password" before an approval counts ([GitLab MR approval settings](https://docs.gitlab.com/user/project/merge_requests/approvals/settings/)). RFC 9470 gives the token-path version a name — a resource server returns `insufficient_user_authentication` with `acr_values` and `max_age` to demand a fresher or stronger login than the token carries ([RFC 9470](https://datatracker.ietf.org/doc/html/rfc9470)). Research on agent identity proposes the same shape for anomalous tool calls: low-risk requests pass, and "an anomalous request would dynamically trigger a Client Initiated Backchannel Authentication (CIBA) flow to request explicit, out-of-band human approval" ([arXiv:2510.25819v1](https://arxiv.org/abs/2510.25819v1)). None of this ships in GitHub's current preview. Together they show where the equivalent control has to sit for a token-authenticated agent: per request, not per browser session.

## Example

GitLab's own API shows where a password-grade re-authentication check leaks to automation. The merge request approval endpoint accepts an `approval_password` parameter: "Current user's password. Required if Require user re-authentication to approve is enabled" ([GitLab MR approvals API](https://docs.gitlab.com/api/merge_request_approvals/)). Anything holding that password in its environment, including a script or an agent, satisfies the re-authentication check over the API exactly as a human would in the browser. The same reference states the parameter "always fails if the group or GitLab Self-Managed instance is configured to force SAML authentication" ([GitLab MR approvals API](https://docs.gitlab.com/api/merge_request_approvals/)) — the SAML setting is what turns the check back into one only a person can pass, because the agent has no SAML session to present.

## Key Takeaways

- Check whether the acting principal is on the channel the IdP guards. A token-authenticated API call is outside proof of presence today; only a web-session action is inside it.
- Set the IdP policy to phishing-resistant MFA, not password-based re-authentication — a password in reach of an agent's environment satisfies a weaker policy the same way it satisfies GitLab's `approval_password`.
- Treat the sliding sudo-mode window as something a browser-driving agent inherits from the human who opened it, not as a check that runs fresh on every action.
- Keep agent credentials on scoped tokens that cannot mint new tokens or edit webhooks, since those are exactly the actions this control does not reach once a token already exists.
- Reserve the pattern for rare, high-blast-radius actions. Gating something frequent (a planned PR-merge check, for instance) trains reflex approval instead of scrutiny.

## Related

- [Non-Retirable Approval Rules for Agent Operations](non-retirable-approval-rules.md) — an admin-set rule that also refuses any bypass, but enforced inside the agent host rather than at the IdP
- [Human-in-the-Loop Confirmation Gates for Consequential Agent Actions](human-in-the-loop-confirmation-gates.md) — the in-host confirmation checkpoint this pattern complements from outside the host
- [Per-Caller Identity: Who an Agent's Tool Call Acts As](per-caller-identity-for-agent-tool-calls.md) — deciding which identity a tool call carries, the question a token-path step-up challenge has to answer
- [Enforced Versus Advisory Controls in LLM-Native IDEs](enforced-versus-advisory-controls.md) — sorting safeguards by where they are evaluated, the same test this pattern needs applied to it
- [Ask-Everything Permission Policies Protect Less than Per-Action Approval](../patterns/anti-patterns/ask-everything-permission-policies.md) — the fatigue mechanism behind why a frequent IdP prompt degrades the same way a frequent local one does
