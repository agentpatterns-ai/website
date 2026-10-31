---
title: "Copilot Server-to-Server Authentication: What the Workload Identity Covers"
term: "Copilot Server-to-Server Authentication"
description: "A GitHub App installation token lets a service make Copilot SDK requests billed to an organization with no user seat. The agent tasks API still refuses it."
tags:
  - agent-design
  - copilot
  - security
applies_to: "copilot@1.x"
last_reviewed: 2026-10-28
status: current
aliases:
  - Copilot organization installation token
  - Copilot Requests permission
  - workload identity for Copilot
---

# Copilot Server-to-Server Authentication: What the Workload Identity Covers

> A Copilot installation token makes model requests for an organization and spends its AI credits. The agent tasks API still refuses the same token.

A GitHub App installed on an organization can make Copilot SDK requests using its own installation access token, with no signed-in user and no Copilot seat. The capability is in public preview ([GitHub Changelog, 2026-10-27](https://github.blog/changelog/2026-10-27-github-copilot-supports-server-to-server-authentication)), and it reaches requests made through the [Copilot SDK](copilot-sdk.md) rather than GitHub as a whole. Separately, the controls for approving and auditing such an app are documented for organization owners on Copilot Enterprise or Copilot Business ([GitHub Docs: managing app Copilot access](https://docs.github.com/en/copilot/how-tos/administer-copilot/manage-for-organization/manage-app-copilot-access)).

## What the credential is

Create a GitHub App with the organization `Copilot Requests` permission set to `Read-only`, install it on the organization that should pay, then mint an installation access token carrying `{"permissions": {"organization_copilot_requests": "read"}}` and pass the resulting `ghs_` token to the SDK's explicit token option. "Installation tokens expire after one hour" ([GitHub Docs: server-to-server authentication](https://docs.github.com/en/copilot/how-tos/copilot-sdk/auth/server-to-server-tokens)), and refresh means minting a new one and restarting the SDK client or the host runtime rather than a rotation callback.

The permission name understates what it grants. GitHub says so on its own admin page: "In this context, **Read-only** does not mean that the app cannot incur costs. The permission authorizes the app to make requests that consume your organization's AI credits" ([GitHub Docs: managing app Copilot access](https://docs.github.com/en/copilot/how-tos/administer-copilot/manage-for-organization/manage-app-copilot-access)). The read grant is a spend grant.

## Three paths, three prerequisites

GitHub documents three authentication paths for Copilot requests, and they do not share a policy switch.

| Path | Credential | What the organization must enable | Attribution |
|---|---|---|---|
| GitHub Actions | built-in `GITHUB_TOKEN` with `copilot-requests: write` | `Allow use of Copilot CLI billed to the organization` | the organization, under Actions-specific policies and budgets |
| App installation | `ghs_` installation access token, organization `Copilot Requests` set to Read-only | support for GitHub App installation authentication for Copilot | the organization that owns the installation |
| User authorization | a user-to-server token | the user's own Copilot access | "attributed according to that user's Copilot access" |

The first two rows disagree about the same setting. For the App route GitHub writes: "You do not need to enable the **Allow use of Copilot CLI billed to the organization** policy. That policy applies to a different authentication path" ([GitHub Docs: managing app Copilot access](https://docs.github.com/en/copilot/how-tos/administer-copilot/manage-for-organization/manage-app-copilot-access)). Enable the wrong one and the documented symptom is a `403` saying Copilot requests with GitHub App installation access tokens are not enabled, which points at the organization rather than at the policy you touched.

## What it does not cover

The Copilot cloud agent's tasks API rejects this credential. "The agent tasks API only supports user-to-server tokens", and "Server-to-server tokens, such as GitHub App installation access tokens, are not supported" ([GitHub Docs: cloud agent via the API](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/use-cloud-agent-via-the-api)). A service that calls models and also dispatches cloud-agent tasks needs two credentials, and the second still belongs to a person. [Programmatic cloud-agent dispatch](../../workflows/programmatic-cloud-agent-dispatch.md) covers that half.

Neither the changelog nor the organization admin page mentions commit or review authorship. Attribution here means billing and usage attribution, and it lands in a CSV: "App attribution is available in CSV exports, not in the **AI usage** view on GitHub" ([GitHub Docs: managing app Copilot access](https://docs.github.com/en/copilot/how-tos/administer-copilot/manage-for-organization/manage-app-copilot-access)). Finding which app spent what means downloading an AI usage report, reading `app_client_id`, and matching it to `client_id` from the organization's app installations endpoint.

## Why it works

The receiving system derives the policy set and the billing account from the credential's owner, so swapping the credential type changes whose rules apply without touching agent logic. "Usage is attributed and billed to the organization that owns the GitHub App installation" ([GitHub Docs: server-to-server authentication](https://docs.github.com/en/copilot/how-tos/copilot-sdk/auth/server-to-server-tokens)), and that organization's "model policies, budgets, and spending controls apply" ([GitHub Changelog, 2026-10-27](https://github.blog/changelog/2026-10-27-github-copilot-supports-server-to-server-authentication)).

What drops away is a person-shaped dependency. A credential tied to a person inherits that person's account state and seat. GitHub frames the gain as helping services "operate reliably at larger scale without tying their authentication or usage to individual users" (same changelog) and prices it as "No user subscription; organization policy required" ([GitHub Docs: SDK authentication](https://docs.github.com/en/copilot/how-tos/copilot-sdk/auth/authenticate)). The same premise caps it, because authorization is decided per surface from the token type. [Per-caller identity](../../security/per-caller-identity-for-agent-tool-calls.md) sets out the general version of this trade.

## When this backfires

- `useLoggedInUser` is left at its default. The SDK's priority runs from an explicit token through environment variables to stored `copilot` CLI credentials and then `gh auth` ([GitHub Docs: SDK authentication](https://docs.github.com/en/copilot/how-tos/copilot-sdk/auth/authenticate)), so the service quietly bills a developer and leaves `app_client_id` empty. Setting "`useLoggedInUser: false` turns off automatic credential discovery" ([GitHub Docs: server-to-server authentication](https://docs.github.com/en/copilot/how-tos/copilot-sdk/auth/server-to-server-tokens)).
- One app needs its own spending ceiling. "You cannot create a budget for one app or installation", and "A budget that only sends alerts does not stop spending" ([GitHub Docs: managing app Copilot access](https://docs.github.com/en/copilot/how-tos/administer-copilot/manage-for-organization/manage-app-copilot-access)). A looping app drains the pool every other consumer shares unless `Stop usage when budget limit is reached` is on.
- The app also does useful non-Copilot work. Stopping its requests means suspending or uninstalling the installation, which "also blocks the installation's access to other organization resources" (same page). The kill switch is not surgical.
- The installation sits on a personal account or at enterprise level. "Personal account and enterprise installations cannot use this authentication method" (same page).
- A dedicated machine user would do. The SDK's supported token types include fine-grained personal access tokens (`github_pat_`) and exclude classic `ghp_` ones ([GitHub Docs: SDK authentication](https://docs.github.com/en/copilot/how-tos/copilot-sdk/auth/authenticate)), while the agent tasks API takes "a personal access token, a OAuth app token or a GitHub App user-to-server token" ([GitHub Docs: cloud agent via the API](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/use-cloud-agent-via-the-api)), so one user credential reaches surfaces this installation token cannot. In Actions the built-in token "needs no GitHub App or stored authentication secret" ([GitHub Docs: server-to-server authentication](https://docs.github.com/en/copilot/how-tos/copilot-sdk/auth/server-to-server-tokens)), so a private key and an hourly mint-and-restart loop buy nothing there.
- The permission name or the attribution field moves. GitHub marks this authentication "in public preview and subject to change" ([GitHub Docs: managing app Copilot access](https://docs.github.com/en/copilot/how-tos/administer-copilot/manage-for-organization/manage-app-copilot-access)).

## Key Takeaways

- The credential is a GitHub App installation access token with the organization `Copilot Requests` permission at Read-only, valid for one hour, and it serves Copilot SDK requests in public preview; the controls for approving and auditing such an app are documented for organization owners on Copilot Enterprise or Copilot Business
- Read-only authorizes spending rather than reading alone, so review an app's expected volume before approving the permission
- The agent tasks API still rejects installation tokens, so dispatching cloud-agent work keeps needing a user-to-server credential
- Governance is organization-grained: no per-app budget, attribution only in CSV exports, and revocation that removes the installation's other access with it
- Set `useLoggedInUser: false`, because the SDK's fallback chain ends at a developer's own credentials

## Related

- [GitHub Copilot SDK](copilot-sdk.md) — the surface this credential authenticates against
- [Bounding an Embedded Copilot SDK Agent's Tool Set](copilot-sdk-tool-scoping.md) — what the authenticated session may then call
- [Copilot Cloud Agent Organization Controls](cloud-agent-org-controls.md) — the org-scope governance this path inherits
- [Programmatic Cloud-Agent Dispatch via REST API and Webhooks](../../workflows/programmatic-cloud-agent-dispatch.md) — the adjacent surface that refuses installation tokens
- [Per-Caller Identity: Who an Agent's Tool Call Acts As](../../security/per-caller-identity-for-agent-tool-calls.md) — the tool-agnostic choice between a deployment-owned and a caller-owned credential
