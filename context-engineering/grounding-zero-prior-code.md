---
title: "Grounding Agents in Code the Model Has Never Seen"
term: "Zero-Prior Grounding"
description: "A model with no training data for your proprietary SDK writes code for the closest public API it does know, and never flags the guess. Retrieving the internal docs leaves most of that gap open. An identity layer that names the wrong API and forbids it closes it."
aliases:
  - zero-prior provisioning
  - closest-match grounding
  - proprietary SDK grounding
tags:
  - context-engineering
  - instructions
  - tool-agnostic
last_reviewed: 2026-06-25
maturity: adopted
---

# Grounding Agents in Code the Model Has Never Seen

> A model with no training data for your SDK writes the closest public API instead, and never flags the guess. Grounding has to override it.

## The zero-prior case

The familiar version of this problem is a stale prior: the model knows an old release of a public API and writes against it with confidence ([Training-Data Gravity](../patterns/anti-patterns/training-data-gravity.md)).

Zero-prior is a different problem. For internal SDKs, proprietary codebases, and custom frameworks, the correct API is not in the training data at all. The model does not pause, ask for documentation, or flag uncertainty. It "finds the closest match in its training data and generates code as if that match were your technology" ([Mastykarz, "When the model has never seen your code", Microsoft for Developers, 2026](https://developer.microsoft.com/blog/when-the-model-has-never-seen-your-code)), mapping an unknown `SessionManager.initialize()` onto whichever public SDK sits nearest by name and shape.

The code compiles often enough to reach review looking fine. It still violates the requirements of the technology you actually run.

Three neighboring failures are not this one:

- [Training-Data Gravity](../patterns/anti-patterns/training-data-gravity.md) — stale-prior bias on a public API. The model knows X, and X is deprecated.
- [Unversioned Scaffolding](../patterns/anti-patterns/unversioned-scaffolding-stale-templates.md) — a resolver picking an old template at scaffold time.
- [Seeding Agent Context](seeding-agent-context.md) — the general technique of leaving context in the code.

Zero-prior bites at generation time, on every call, against code no model has indexed. That last part is why the breadcrumbs need an identity layer. There is no correct prior underneath for them to anchor to.

## Retrieving the docs is not enough

The obvious fix is to pull the internal API reference into context at inference time. It closes less of the gap than you would expect. PriCoder tested exactly this across three mainstream LLMs on private-library benchmarks: "even given accurate required knowledge, LLMs still struggle to invoke private-library APIs effectively." Their training-side intervention adds "over 20% gains in pass@1 in many settings" on top of doc retrieval ([Zhang et al., "To See is Not to Master", arxiv 2603.15159, 2026](https://arxiv.org/abs/2603.15159)).

The reason is mechanical. Context can only shift weight toward APIs the model already assigns some probability to, and a proprietary API has none. So the nearest public API keeps winning every decision the documentation does not explicitly forbid.

ExploraCoder shows the same thing from the other direction: force the agent to call the real API at intermediate steps and it beats retrieval-based approaches by 11.99% and pretraining-based methods by 17.28% on unseen APIs ([Wang et al., "ExploraCoder", arxiv 2412.05366, 2024](https://arxiv.org/abs/2412.05366)). Documentation gives the agent somewhere to look things up. Overriding the wrong guess takes a model of the technology sitting in context at the moment of the decision.

## The five-layer bootstrap

Mastykarz's teaching strategy has five layers, and the order carries weight. Skip layer 1 and the wrong mental model survives everything after it ([Mastykarz, 2026](https://developer.microsoft.com/blog/when-the-model-has-never-seen-your-code)):

1. Identity and purpose. What the technology does, and explicitly what it is not. "Contoso Identity uses mutual TLS with short-lived certificates, NOT OAuth." This is the layer that overrides the wrong guess.
2. Core concepts. Three to five ideas that replace the model's wrong picture.
3. API shape and conventions. Naming patterns, initialization flow, common signatures. Not an exhaustive reference.
4. Common patterns and workflows. A handful of typical use cases with annotated examples. In retrieval studies, example code outweighs parameter lists ([Chen et al., "When LLMs Meet API Documentation", arxiv 2503.15231, 2025](https://arxiv.org/abs/2503.15231)).
5. Edge cases and gotchas. Useful only once the basics have landed.

Where each layer lives depends on when it needs to be readable:

| Layer | Surface | Why there |
|-------|---------|-----------|
| Identity, concepts | [AGENTS.md / CLAUDE.md](../instructions/agents-md-as-table-of-contents.md) | Loads every session, which is what it takes to override the wrong guess |
| API shape, examples | Skills (on demand) | Pulled in when the agent asks, so the always-loaded context stays lean |
| Lookup detail | MCP server | Returns only what the model asks for, maintained in one place |
| Reference implementations | Workspace code | Agents pattern-match the code they can see, so it has to show the right shape |
| Diagnostics | Error messages | "Received: { clientId, scope } which appears to be an OAuth configuration" teaches at the point of failure |

Loading all five every session costs more than it returns. A controlled evaluation found context files often reduce task success against no context file at all, while raising inference cost over 20% when they carry structural overviews ([Gloaguen et al., "Evaluating AGENTS.md", arxiv 2602.11988](https://arxiv.org/abs/2602.11988)). Layer 1 is a few lines and belongs in the always-loaded file. Layers 3 and 4 are long and belong behind an on-demand call.

## Start with the baseline run

Run the task with no extensions and watch which public technology the model reaches for. "The baseline reveals the model's closest match, and that match is what your extensions need to override" ([Mastykarz, 2026](https://developer.microsoft.com/blog/when-the-model-has-never-seen-your-code)).

Then write the identity layer against that specific answer. "Uses our internal auth" does nothing. The version that works names the wrong API and forbids it: "uses mutual TLS with short-lived certificates, not OAuth. Do not generate `OAuth2Client`, `authorization_code` flows, or `Bearer` headers."

## Why it works

Every generation samples from the pretrained distribution. When the correct API carries no probability under that distribution, the nearest public API is the best answer available, so that is what comes out. The model has nothing to be uncertain about.

The behavior is stubborn. In one study, models accepted fabricated library names under plausible prompts in up to 99% of cases ([Twist et al., "Library Hallucinations in LLM-Generated Code", arxiv 2509.22202, 2026](https://arxiv.org/abs/2509.22202)).

Documentation adds weight where the correct API should be. The wrong one still wins wherever the docs are silent, which is most places. An identity layer changes the question the model is answering. Instead of "complete this code against the most likely API," it reads "this is technology X, X is not Y, treat Y patterns as errors," and that constraint holds across the whole generation rather than one call at a time.

## When this backfires

The five-layer bootstrap is real engineering, and it only pays for itself on a proprietary surface big enough and busy enough to justify the upkeep.

- The surface is tiny. One internal helper does not earn a Skill plus an MCP server plus an identity layer. The agent gets it wrong, review catches it, and that costs less than maintaining the provisioning.
- Nobody owns the reference material. Stale identity is worse than no identity: the agent now follows confidently wrong instructions instead of its own wrong guess. See [Stale AI Configuration Artifacts (Context Rot)](../patterns/anti-patterns/stale-ai-configuration-artifacts.md).
- The SDK is a thin wrapper. If it is OAuth plus a header, the nearest public API is already about 80% right and the bootstrap buys little.
- The always-loaded context is already full. Bulk context files add roughly 20% to inference cost with no gain in task success ([Gloaguen et al., 2026](https://arxiv.org/abs/2602.11988)). Keep identity there and push shape, examples, and gotchas behind on-demand calls.
- The verifier is fast and lossless. Unit tests covering the internal SDK on every commit surface the failure in seconds. Provisioning earns most where wrong code looks plausible and reaches production unchecked.

## Example

A team building against `Contoso Identity`, a proprietary mTLS auth SDK, ran the unprovisioned baseline and watched the agent emit OAuth2 on every call. That is the answer the identity layer has to beat, and it goes in the always-loaded `AGENTS.md`:

```markdown
# AGENTS.md (project root)

## Identity: Contoso Identity SDK

Contoso Identity is a **mutual-TLS** authentication SDK using short-lived
client certificates. It is **NOT OAuth**. Do not generate any of:

- `OAuth2Client` / `oauth2_session` / `authorization_code` flows
- `Bearer ` Authorization headers
- `/.well-known/openid-configuration` endpoints
- JWT decode/verify code

If you reach for any of the above, stop — the closest-match prior is
overriding the identity layer.

## Core concepts

- `IdentityClient(cert_path, key_path)` is the entry point. Always
  constructed with a short-lived cert pair from the local agent.
- All calls carry the cert at the TLS layer; never in the body or
  Authorization header.
- Session lifetime <= 5 min; renew via `client.renew()`, never re-handshake.

For API shape and examples, run `chub get contoso/identity` or read
`docs/contoso-identity/` in this repo.
```

Shape and examples go in a Skill the agent pulls on demand, not in `AGENTS.md`:

```yaml
# .claude/skills/contoso-identity/SKILL.md (excerpt)
---
name: contoso-identity
description: Use this skill when calling Contoso Identity SDK. Loads
  API shape, common patterns, and gotchas. Invoke before writing any
  IdentityClient code.
---

## Common pattern: authenticated request
client = IdentityClient(cert_path="./certs/agent.pem",
                        key_path="./certs/agent.key")
response = client.get("/internal/users", timeout=5)
# Note: do NOT pass headers={"Authorization": ...} -- the cert is the auth
```

Always-loaded context stays at about 30 lines. The expensive layers load only when something asks for them. And the agent now carries an explicit prohibition against the exact code the baseline caught it writing.

## Key Takeaways

- Diagnose before you provision. Whichever public framework the unprovisioned baseline produces is the one your identity layer has to name and forbid ([Mastykarz, 2026](https://developer.microsoft.com/blog/when-the-model-has-never-seen-your-code)).
- Retrieval alone leaves the gap open, because the nearest public API wins every decision the docs do not explicitly override ([Zhang et al., arxiv 2603.15159, 2026](https://arxiv.org/abs/2603.15159)).
- Order the layers identity, concepts, shape, patterns, gotchas, and never drop the first. It is the only one that contradicts the wrong guess head-on.
- Split by load shape rather than by topic: identity always-loaded, shape and examples on demand, or context cost outruns the gain in task success ([Gloaguen et al., arxiv 2602.11988](https://arxiv.org/abs/2602.11988)).
- Stale provisioning is worse than none at all. If nobody owns the identity layer, do not build one.

## Related

- [Training-Data Gravity: Agents Default to Deprecated APIs](../patterns/anti-patterns/training-data-gravity.md) — the sibling failure for *stale* priors on public APIs. The zero-prior case has no upper bound on the doc-injection gap that page documents.
- [Seeding Agent Context: Breadcrumbs in Code](seeding-agent-context.md) — the general breadcrumbs technique. This page is the subset where the breadcrumbs need an identity layer, because there is no prior to anchor the trail to.
- [Discoverable vs Non-Discoverable Context](discoverable-vs-nondiscoverable-context.md) — zero-prior identity is the canonical *non-discoverable* content. The model cannot infer it from any file, because the proprietary shape is not in the training distribution.
- [Context Hub: On-Demand Versioned API Docs for Coding Agents](context-hub.md) — the on-demand retrieval surface for the API-shape and examples layers, complementary to the always-loaded identity layer.
- [AGENTS.md as Table of Contents, Not Encyclopedia](../instructions/agents-md-as-table-of-contents.md) — keeps the always-loaded layer lean. Identity and pointers live there, bulk reference does not.
