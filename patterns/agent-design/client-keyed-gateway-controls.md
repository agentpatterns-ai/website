---
title: "Client-Keyed Gateway Controls: Where a Spend Cap's Trust Comes From"
term: "Client-Keyed Gateway Control"
description: "A gateway spend cap or rate limit keyed on a request header is enforced server-side but selected client-side, so it binds only where the caller does not hold the gateway credential."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
aliases:
  - header-keyed spend cap
  - per-customer gateway policy
  - client-supplied policy subject
last_reviewed: 2026-10-25
maturity: emerging
---

# Client-Keyed Gateway Controls: Where a Spend Cap's Trust Comes From

> The attribute a gateway policy keys on decides whether its spend cap binds the caller or merely bills them.

A client-keyed gateway control is a spend cap or rate limit whose subject comes from the request rather than from the credential that authenticated it. The gateway still enforces it: the counter lives at the proxy and the call gets a 402 when the cap is hit. What the caller picks is which counter the call lands against.

## What the gateway stamps, and what it takes from you

LangSmith's LLM Gateway draws this line inside its own matcher namespace. A policy's subject can name an organization, workspace, user, or API key, and both spend caps and rate limits attach at all four. The launch post says the gateway "is available now in public beta for Plus and Enterprise plans" ([LangChain, July 30, 2026](https://www.langchain.com/blog/langsmith-llm-gateway-runtime-controls-for-production-agents)). Treat the knobs as moving and the split as the durable part. The gateway fills in those four itself: "The gateway stamps caller identity itself and ignores client attempts to override it", and any header resolving to `organization_id`, `workspace_id`, `user_id`, `user_email`, `api_key_id`, `auth_mode` or the rest are discarded ([per-customer policies](https://docs.langchain.com/langsmith/llm-gateway-header-policies)).

Everything else in the subject space is yours to supply. "The gateway matches on request headers prefixed with `X-Gateway-`, and on keys inside the `X-Gateway-Metadata` JSON header. No other request header is matchable" ([per-customer policies](https://docs.langchain.com/langsmith/llm-gateway-header-policies)).

On trust the docs are explicit: "The gateway trusts the `X-Gateway-*` headers on an incoming request". It warns that "A caller that controls both the key and the header can choose which limit to use" ([per-customer policies](https://docs.langchain.com/langsmith/llm-gateway-header-policies)). Their instruction is to set the header in your own backend, after you authenticate the end user. Keep the gateway API key away from end users.

## Why it works

A gateway policy is a function from request attributes to a decision, and its integrity stops at the least trustworthy attribute it reads. Moving the check from the agent to the proxy takes away the client's ability to skip it. The client can still choose which check applies, because it writes the attribute that selects one. LiteLLM gives the causal reason in its JWT documentation: a verified JWT claim "takes precedence over all headers and body fields listed above", and because "the claim comes from a token LiteLLM has already validated, callers cannot override it" ([Customers / End-Users](https://docs.litellm.ai/docs/proxy/customers)). The attribute must come from a source the limited caller cannot change.

Each vendor builds the distinction into a mechanism rather than leaving it as advice, which is what makes it checkable. LiteLLM puts the validated claim above the eight request-supplied places it otherwise reads a customer id from: four headers, then four body fields, first match wins ([Customers / End-Users](https://docs.litellm.ai/docs/proxy/customers)).

## Picking the key

Key a control you need to bind on something the caller cannot set. Where the limited party holds the gateway credential, a header-keyed cap is attribution with a 402 attached: "When a cap is hit, the agent receives a 402 response with a clear error" ([LangChain, July 30, 2026](https://www.langchain.com/blog/langsmith-llm-gateway-runtime-controls-for-production-agents)).

Two documented mechanisms close the gap. Neither source frames them as a fix for client-selected keying; this page draws that inference. Promote the subject into a verified token claim, the way LiteLLM's JWT precedence does. LiteLLM still reads request-supplied fields when the JWT yields no end-user ID ([Customers / End-Users](https://docs.litellm.ai/docs/proxy/customers)). Require that claim on every capped request. Or put a credential-keyed policy behind the header-keyed one, because "A request that matches both a plain subject policy and a policy with a header condition counts against both, and either one can block it" ([per-customer policies](https://docs.langchain.com/langsmith/llm-gateway-header-policies)).

Header keying is the right design in the topology these docs assume, where "A reseller or multi-tenant application usually calls the gateway from its own backend, using one workspace-scoped API key on behalf of many end customers" ([per-customer policies](https://docs.langchain.com/langsmith/llm-gateway-header-policies)). That backend holds the key and sets the header after authenticating its own user. The header inherits an authentication step the end customer never touches, and no gateway API key is issued per customer. Check whether the party you are capping can write the header.

## When this backfires

- The limited party holds the credential. The documented setup for a coding harness is to authenticate with your LangSmith API key and "Update your `base_url`" ([LangChain, July 30, 2026](https://www.langchain.com/blog/langsmith-llm-gateway-runtime-controls-for-production-agents)), which leaves the agent holding both the key and the header, so its own cap is self-selected. A developer fleet is not the reseller backend these docs describe.
- The client's identifier has unbounded cardinality. LiteLLM upserts every distinct customer id it sees, and uses Claude Code as its example of a client that breaks this: it "puts a JSON blob in `metadata.user_id`". Where a default customer budget is configured, "each session gets its own copy of that budget, so a monthly cap meant for real customers turns into a per-session cap on that traffic" ([Customers / End-Users](https://docs.litellm.ai/docs/proxy/customers)).
- Unlabeled traffic lands somewhere you did not pick, and where depends on which mechanism you chose. Under an explicit header condition, "A request without the configured header does not match the policy". Under a default limit separated by header, "Requests without the configured header share a fallback limit for their subject" ([per-customer policies](https://docs.langchain.com/langsmith/llm-gateway-header-policies)).
- The hardening fails open. LiteLLM's `validate_end_user_id_in_db`, available in v1.87.0 and above, drops an unrecognized id when used alone, and "Dropping is not an error: the request still succeeds, it just carries no customer, and its spend is attributed to the virtual key, team and internal user as usual" ([Customers / End-Users](https://docs.litellm.ai/docs/proxy/customers)). Pairing it with `max_end_user_budget_id` preserves unregistered plain-string IDs under the default budget. JSON-shaped IDs, including Claude Code session blobs, are still dropped ([LiteLLM](https://docs.litellm.ai/docs/proxy/customers)).
- One key, one team. A credential-keyed cap already covers the fleet, and explicit per-customer policies add a sync job, since "each end customer needs its own policy" ([per-customer policies](https://docs.langchain.com/langsmith/llm-gateway-header-policies)). A default spend limit separated by header requires no policy per value.
- The readback can be absent. Per-customer spend arrives as `current_spend_usd`, and "The field is omitted when the spend lookup fails, so treat a missing value as unknown rather than as zero" ([per-customer policies](https://docs.langchain.com/langsmith/llm-gateway-header-policies)).

## Key Takeaways

- A gateway control depends on the provenance of the attribute it keys on.
- LangSmith discards client-supplied values for organization, workspace, user, and API key, and matches only `X-Gateway-*` headers and `X-Gateway-Metadata` keys for everything else.
- Ask whether the party you are capping can write the attribute the cap selects on. For a coding harness configured by base URL the answer is yes, so use a credential-keyed cap to bound that caller.
- Use a verified token claim as the subject on every capped request, or a credential-keyed policy behind the header-keyed one. LiteLLM falls back to request fields when the JWT has no end-user ID ([Customers / End-Users](https://docs.litellm.ai/docs/proxy/customers)).
- A client-supplied key with per-session cardinality turns one monthly cap into one cap per session.

## Related

- [Gateway Hint Headers for Routing and Budgeting Agent Calls](gateway-hint-headers.md) — the client half of the same contract, where the agent declares request class and subagent type for a gateway to route on
- [Centralized LLM Gateway for Per-Dimension Agent Budgets](../../observability/llm-gateway-per-dimension-budgets.md) — the credential-keyed budget dimensions this page sits beside, and the chokepoint that enforces them
- [Gateway Model Routing](gateway-model-routing.md) — the same proxy as a model catalog, and the harness contract it has to honor
- [Prompt-Only Tool Access Control](../anti-patterns/prompt-only-tool-access-control.md) — why the proxy is the right place for the check, which is the half this page takes as given before asking what the check keys on
- [Tenant Model Policy](tenant-model-policy.md) — per-tenant model entitlements, which need the same question asked about where tenant identity comes from
