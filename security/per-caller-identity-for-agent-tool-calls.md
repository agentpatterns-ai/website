---
title: "Per-Caller Identity: Who an Agent's Tool Call Acts As"
term: "Per-Caller Identity"
description: "A tool call reaches an external system as the deployment or as the person who asked. That token decides visible data, the logged actor, and whose quota it spends."
tags:
  - security
  - agent-design
  - tool-agnostic
aliases:
  - on-behalf-of identity for agents
  - user-owned agent credentials
  - caller identity for tool calls
last_reviewed: 2026-09-10
maturity: emerging
---

# Per-Caller Identity: Who an Agent's Tool Call Acts As

> The identity a tool call carries decides what the agent sees, what the audit log records, and whose rate limit drains.

Every tool call arrives at the external system carrying one identity, and that system decides authorization, attribution, and quota from it. LangChain's Connections splits the decision into two independent axes: "A connection has an owner and a credential type, and they are independent." The owner is either the deployment or the caller, and the credential is either a static secret or an OAuth grant ([Moreira, LangChain, 2026-09-09](https://www.langchain.com/blog/connections-managed-credentials-and-per-caller-identity-for-managed-deep-agents)). Where you keep the key is a different question: "A key in `.env` answers what the agent may do. It has no way to answer who asked."

## When per-caller identity earns its cost

Use the caller's own credential when the result depends on who is asking. A search across private repositories or a personal Notion workspace returns different rows for different people, so a shared credential returns the wrong rows rather than fewer of them. LangChain describes the effect on reads, before any write happens: private repositories "one person can see and another cannot change the results — same query, same deployment, different answers" ([Moreira, 2026](https://www.langchain.com/blog/connections-managed-credentials-and-per-caller-identity-for-managed-deep-agents)). Use it again when a write has to be attributable to a person, so the issue carries their handle in `user.login` instead of a bot's.

Everywhere else, prefer an identity that belongs to the software. The vendor that shipped the per-caller machinery says so on its own reference page: where the provider issues an application credential of its own, such as a Slack bot token or a GitHub App installation token, "prefer that credential stored as an agent-owned secret. An application credential is scoped to the application, is revocable on its own, and does not depend on any person's account" ([Connections, LangChain docs](https://docs.langchain.com/langsmith/python/managed-deep-agents-connections)). Reach for per-person identity when the provider authenticates only as a person, or when attribution to a human is the point.

## The four cells

Owner and credential type are orthogonal, which gives four combinations rather than a spectrum.

| Owner | Static secret | OAuth grant |
|---|---|---|
| Deployment | One API key for a capability that does not vary by person: web search, a geocoder, a pricing feed | One grant collected with `--authorize`, so "every caller acts as a single shared account" |
| Caller | Per-person API keys | The caller's own grant, resolved at run time by `connections.get(slug, {"type": "user"})` |

Per-caller identity is the bottom-right cell. Teams that want a shared team account land top-right, which LangChain calls "the right answer when you want a dedicated team account rather than per-person identity" ([Moreira, 2026](https://www.langchain.com/blog/connections-managed-credentials-and-per-caller-identity-for-managed-deep-agents)). Bottom-left is the cell the product does not fill yet: Connections is in public beta, and "Slack and Studio do not collect a per-caller API key, and the CLI does not create an empty slot for one" ([Connections docs](https://docs.langchain.com/langsmith/python/managed-deep-agents-connections)), so read the flag names below as a moving surface.

## Why it works

The receiving system reads one token and derives everything from it, which is what makes this a single decision instead of several knobs. LangChain spells out the consequences for an agent backed by a person's account: "The agent gets your full access at that provider. The provider's audit log shows your name for what the agent did. The agent stops working when your own access changes" ([Connections docs](https://docs.langchain.com/langsmith/python/managed-deep-agents-connections)).

Quota moves with those three. On GitHub, requests an app makes on a person's behalf "count towards your personal rate limit of 5,000 requests per hour", shared with that person's own personal access tokens; an installation access token draws on a separate pool that scales with the organization ([Rate limits for the REST API, GitHub Docs](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api)). Choose the caller and a busy agent competes with that caller's own tooling.

Picking the identity does not authorize the call. An audit of LangChain/LangGraph, LlamaIndex, and the Stripe Agent Toolkit found all three "provide capability gating by default, but none provides a deterministic fail-closed per-call value authorization gate by default" ([Mellafe Zuvic, 2026](https://arxiv.org/abs/2606.28679v1)). Identity picks the principal; a separate gate still checks the arguments.

## When this backfires

- The run has no caller. "User-owned connections require an authenticated caller. Anonymous or agent-only runs cannot complete the credential gate" ([Connections docs](https://docs.langchain.com/langsmith/python/managed-deep-agents-connections)). A missing grant raises a `credential_authorization_required` interrupt before the first model turn, and a scheduled run has nobody to answer it. Any agent with both a schedule and user-owned connections needs a second identity path.
- The default resolves everyone to one person. The default identity declaration "authenticates the calling client, not an individual person, so every caller who presents it resolves to the same identity" ([Connections docs](https://docs.langchain.com/langsmith/python/managed-deep-agents-connections)). Code reading `{"type": "user"}` can behave as a shared account until you declare a real identity provider.
- A privileged caller widens the blast radius. The agent inherits the caller's standing access at that provider, so an injected run reaches whatever the most privileged person can reach. Scope caps are the mitigation: `--allowed-scope` sets a ceiling on what any later authorization may request ([Connections docs](https://docs.langchain.com/langsmith/python/managed-deep-agents-connections)).
- A human account becomes production infrastructure. A grant "stays tied to the account that authorized it, even a dedicated one. A password reset, a revoked session, or a deactivated account ends the grant" ([Connections docs](https://docs.langchain.com/langsmith/python/managed-deep-agents-connections)). Routine account hygiene turns into an outage.
- Retrofitting leaves history unattributed. "Adding Supabase identity to an existing deployment does not add owner metadata to existing threads" ([Identity, LangChain docs](https://docs.langchain.com/langsmith/python/managed-deep-agents-identity)). Switching on per-caller identity later does not backfill what ran before it.

## Example

A GitHub connection that files issues under the caller's own account registers an OAuth app and stores no credential value:

```bash
uv run mda connections create github-issues \
  --oauth github \
  --client-id "$GITHUB_CLIENT_ID" \
  --secret-from-env GITHUB_CLIENT_SECRET \
  --scope repo
```

The scope line matters more than it looks. GitHub's catalog default is `read:user`, "which cannot open an issue, so whatever you pass becomes the whole list" ([Moreira, 2026](https://www.langchain.com/blog/connections-managed-credentials-and-per-caller-identity-for-managed-deep-agents)).

One line inside the tool selects the owner, and every tool sharing that helper inherits the choice:

```python
access_token = await connections.get("github-issues", {"type": "user"})
```

Swapping `"user"` for `"agent"` moves the call to a different cell of the table with no other code change. One argument is the whole decision surface, which is why it is easy to leave on its default.

## Key Takeaways

- Owner and credential type are separate choices. Deciding where the secret lives says nothing about which principal the call presents.
- Per-caller identity is the exception. Prefer an application credential wherever the provider issues one.
- Reads diverge before writes do. If two people running the same query should see different rows, a shared credential is already wrong.
- On GitHub, an agent acting for a person spends that person's 5,000 requests per hour; an installation token has its own pool.
- No unattended run can answer a per-caller authorization prompt, so schedules and retries need their own identity path.

## Related

- [Secrets Management for AI Agents: Credential Injection](secrets-management-for-agents.md) — keeping the credential out of context, the other half of the problem, which does not answer who the call acts as
- [Workload Identity Federation for Agent Runtimes](workload-identity-federation-for-agents.md) — short-lived tokens minted from a runtime's existing identity, the machine-to-machine end of the same question
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md) — why inheriting a privileged caller's access is the cost of per-caller identity
- [Authorization Continuity Across Agent Mutation](authorization-continuity-across-agent-mutation.md) — what happens to a grant when the subject it names changes
- [Deep Agent Runtime: The Layer Beneath the Harness](../patterns/agent-design/deep-agent-runtime.md) — the runtime layer that attaches caller identity to a run
