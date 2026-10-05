---
title: "Configuring the Code Review Request Surface"
term: "Review Request Surface"
description: "Decide who triggers an agent code review, and on which branches, before tuning how deeply it reads. The trigger is the knob that sets volume and the only one a ruleset can target."
aliases:
  - review invocation surface
  - code review trigger configuration
  - Copilot code review configuration
tags:
  - code-review
  - copilot
  - cost-performance
last_reviewed: 2026-10-04
maturity: emerging
---

# Configuring the Code Review Request Surface

> Copilot scopes whether a review runs by branch, how deeply it reads by who set the default, and whether it can approve by file path.

Decide who triggers the review before tuning how hard it works. On GitHub Copilot code review the trigger is a branch ruleset rule, so it targets branches; the effort level is a dropdown holding one value per scope, so it targets nothing narrower ([GitHub Docs: Configuring code review by GitHub Copilot](https://docs.github.com/en/copilot/how-tos/copilot-on-github/set-up-copilot/configure-code-review)). Treat the two as one setting and you write a policy the product cannot express.

## When this is worth the effort

Two conditions have to hold. Review output must already compete with reviewer attention, because selective invocation counters [reviewer habituation](reviewer-habituation-decay.md) rather than improving review in general. And depth must cost enough to ration: GitHub estimates $0.05 to $1 in AI credits for a Lite review against $0.25 to $5 for a Balanced one, before Actions minutes ([GitHub Docs](https://docs.github.com/en/copilot/concepts/agents/code-review)). Since 2026-09-28 a repository on `Default` pays the Balanced range, because the built-in default moved from Lite to Balanced ([GitHub Changelog, 2026-10-02](https://github.blog/changelog/2026-10-02-copilot-code-review-api-support-and-new-default-effort-level)). Below both thresholds, turn automatic review on everywhere and stop.

## Three knobs, three scoping vocabularies

| Knob | Where it is set | What it can be scoped by |
|------|-----------------|--------------------------|
| Whether a review runs | Branch ruleset rule, "Automatically request Copilot code review" | Branches the ruleset targets |
| How deeply it reads | The "Review effort level" setting | One value per enterprise, organization, repository or person |
| Whether it can approve | Organization or enterprise policy, plus a repository path list | Up to 15 file globs |

The trigger is a ruleset rule at repository, organization and enterprise level, with separate options for draft pull requests and for each new push ([GitHub Docs](https://docs.github.com/en/copilot/how-tos/copilot-on-github/set-up-copilot/configure-code-review)). The effort level is a setting rather than a ruleset rule, so "Balanced on `src/auth/`" has no configuration form. The one path-scoped knob is approval authority, where the auto-approval setting counts an approval "only on pull requests where every changed file matches one of the globs" (same page). The other override is per request: whoever asks for a review "can still select a different review effort before requesting" ([GitHub Changelog, 23 September 2026](https://github.blog/changelog/2026-09-23-copilot-code-review-more-ways-to-request-and-configure-reviews)).

## Requesting a review through the API

Since 2 October 2026 a review can be requested through the REST and GraphQL APIs, with an optional effort level for that review ([GitHub Changelog, 2 October 2026](https://github.blog/changelog/2026-10-02-copilot-code-review-api-support-and-new-default-effort-level)). The REST route is the pull request reviewers endpoint, `POST /repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers`, with `copilot-pull-request-reviewer[bot]` as the reviewer ([GitHub Docs](https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/copilot-code-review)). The GraphQL route is the `requestReviewsByLogin` mutation, which takes bot logins ([GitHub GraphQL schema](https://docs.github.com/public/fpt/schema.docs.graphql)).

The changelog does not name the effort parameter, and the REST reference and GraphQL schema do not list one yet ([GitHub Docs: REST reference](https://docs.github.com/en/rest/pulls/review-requests#request-reviewers-for-a-pull-request)). Check the current reference before you write a call. A level set on the request is first in the documented precedence order, so it beats every stored default. This makes a script the one place a path rule can set depth: a CI job can read the changed paths and ask for Balanced only when `src/auth/` changed. That routing lives in your script, not in GitHub configuration.

## The tier that pays is the one you cannot see

Since 23 September 2026 every Copilot plan carries a personal code review page with an automatic-review toggle and a default effort level, and that default "applies to reviews you request, including reviews configured to automatically review your pull request" ([GitHub Changelog](https://github.blog/changelog/2026-09-23-copilot-code-review-more-ways-to-request-and-configure-reviews)). The bill lands on the same person: when a repository auto-requests review, "the AI credits consumption is attributed to the pull request author" ([GitHub Docs](https://docs.github.com/en/copilot/concepts/agents/code-review)).

GitHub now documents which level wins. Copilot checks six options in order and uses the first that applies: a level chosen when the review is requested, a level previously used on the pull request, the requester's level, the repository's, the organization's (or the repository owner's on a user-owned repository), and the built-in default, Balanced. For a new pull request the requester is the author, so the author's personal default beats the repository default ([GitHub Docs](https://docs.github.com/en/copilot/concepts/agents/code-review#review-effort-level)). The docs do not say who the requester is for a call made with a GitHub App installation token. The level that ran shows up afterwards in the pull request overview comment (same page), so the variation is auditable per pull request and not settable centrally. When a bot requests the review, usage is billed directly to the organization, not to the author ([GitHub Docs](https://docs.github.com/en/copilot/concepts/agents/code-review)).

## Why it works

Volume decides whether anyone acts on the feedback. In a study of 16 AI review actions covering "more than 22,000 review comments in 178 repositories", two of those actions supported manual triggering, and in both "manually triggered comments consistently showed higher addressing rates". The authors offer a reason rather than a proof: "This suggests that the massive feedback resulting from unconditional triggering might reduce developers' willingness to respond" ([arXiv:2508.18771v2](https://arxiv.org/abs/2508.18771v2)). Effort changes what a review says once someone has asked for it. Nothing comparable is published for effort levels.

## When this backfires

- Low pull-request volume. A repository merging a few pull requests a week has no habituation to fight, and a trigger policy costs more coordination than the noise it removes.
- Coverage loss. That trigger-mode comparison covers two actions, it is observational, and developers pick which pull requests to trigger by hand. The same study found automated actions "reviewed code changes regardless of author experience, which may help mitigate potential experience blindspots", against human review where 79% of comments went to newcomers ([arXiv:2508.18771v2](https://arxiv.org/abs/2508.18771v2)). A narrower trigger puts that blind spot back.
- Audits that demand uniform depth. A personal default "applies to reviews you request" ([GitHub Changelog](https://github.blog/changelog/2026-09-23-copilot-code-review-more-ways-to-request-and-configure-reviews)), so depth varies by author inside one repository, and proving uniform treatment means reading the per-review record.
- Enterprise cascade. An enterprise default "applies to organization-owned repositories through inheritance" and "organizations and repositories can still set their own overrides" ([GitHub Changelog](https://github.blog/changelog/2026-09-23-copilot-code-review-more-ways-to-request-and-configure-reviews)). Until an override lands, the expensive setting is the quiet one.
- Disabling below the enterprise. Copilot code review resolves across organizations by the least restrictive one: "if any of the organizations has enabled a feature, this feature is enabled for the user everywhere" ([GitHub Docs](https://docs.github.com/en/copilot/reference/enterprise-administrators/policy-conflicts)). An organization-level disable does not control a user another organization has licensed.

## Example

A service repository wants deeper review on authentication code and fast review everywhere else. Three settings are available, and none of them expresses that.

A branch ruleset with "Automatically request Copilot code review" fires the review, and it targets branches, not paths ([GitHub Docs](https://docs.github.com/en/copilot/how-tos/copilot-on-github/set-up-copilot/configure-code-review)). The "Review effort level" setting takes one value for the whole repository. The auto-approval globs do accept `src/auth/**`, but they decide whose approval counts toward merge requirements, not how hard the reviewer looks (same page).

What is left is the Reviewers menu, where the person opening the pull request picks the level for that run ([GitHub Changelog](https://github.blog/changelog/2026-09-23-copilot-code-review-more-ways-to-request-and-configure-reviews)), or an API request from your own script. Without a script the policy is a convention in `CONTRIBUTING.md`, enforced by nobody, and the effort level that actually ran is visible afterwards in the pull request overview comment ([GitHub Docs](https://docs.github.com/en/copilot/concepts/agents/code-review)). Audit it there or do not claim it.

## Key Takeaways

- Ask which object a knob lives in before asking what value to set. A ruleset rule aims at a branch; a settings dropdown holds one value for everything under it.
- The only path targeting on this feature governs whose approval counts toward merge requirements, capped at 15 globs. It does not route depth.
- Automatic review bills the pull request author, who now sets their own default depth. A budget forecast built on the repository setting will miss. The docs attribute cost to the author for automatic reviews, to the requesting user for manual ones, and to the organization when a bot requests the review. They do not say how an API request made with a user token is attributed.
- Precedence is documented: a level on the request beats the pull request's earlier level, then the requester's personal level, then the repository, organization, and built-in default. On a new pull request the author's personal default beats the repository default ([GitHub Docs](https://docs.github.com/en/copilot/concepts/agents/code-review#review-effort-level)).
- A request through the REST or GraphQL API can set depth per request, which makes a script the only place a path rule can live. The public reference does not list the effort parameter yet.
- Selective invocation trades coverage for attention. Take that trade where reviewers have stopped reading, not by default.

## Related

- [Tunable Effort Levels for Code Review Agents](tunable-review-effort.md) — what the effort dial does once a review has been requested, and why a level without a published bug-discovery curve is a hedge word
- [Reviewer Habituation in Agent PR Review](reviewer-habituation-decay.md) — the decay that selective invocation is meant to counter, and how to diagnose it
- [Signal Over Volume in AI Review](signal-over-volume-in-ai-review.md) — silence as a valid review output, the same volume argument at the comment level
- [Agent Approval Authority in Code Review](agent-approval-authority.md) — the third knob in the table, covered on its own terms
- [Team-Scoped Agent Policy Delegation](../security/team-scoped-policy-delegation.md) — the neighboring governance object: which Copilot managed-settings keys a team may override
