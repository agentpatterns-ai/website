---
title: "Grounding Agents in Code the Model Has Never Seen"
term: "Zero-Prior Grounding"
description: "When the model has no training signal for a proprietary SDK or custom framework, it generates against the closest public API instead of admitting uncertainty — context provisioning has to displace that closest-match prior, not just supplement it."
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

> Models never say "I don't know" about proprietary code — they generate the closest public API in training, so grounding must displace that prior.

## The zero-prior case

The familiar provisioning problem is stale-prior: the model knows an old version of a public API and confidently writes against it ([Training-Data Gravity](../patterns/anti-patterns/training-data-gravity.md)). The zero-prior case is structurally different. For internal SDKs, proprietary codebases, and custom frameworks, the pretrained conditional distribution has no mass on the correct API at all. The model does not pause, ask for documentation, or signal uncertainty. It "finds the closest match in its training data and generates code as if that match were your technology" — mapping an unknown `SessionManager.initialize()` to whichever public SDK feels closest by naming and shape ([Mastykarz, "When the model has never seen your code", Microsoft for Developers, 2026](https://developer.microsoft.com/blog/when-the-model-has-never-seen-your-code)).

The output looks reasonable. It compiles often enough to be dangerous. It violates the actual technology's requirements.

This is distinct from three adjacent failure modes. [Training-Data Gravity](../patterns/anti-patterns/training-data-gravity.md) is stale-prior bias on public APIs — the model knows X, X is deprecated. [Unversioned Scaffolding](../patterns/anti-patterns/unversioned-scaffolding-stale-templates.md) is a scaffold-time resolver fallback. [Seeding Agent Context](seeding-agent-context.md) is the general breadcrumbs technique. The zero-prior case is generation-time, every-call, on surfaces the model has never indexed — and the breadcrumbs have to include an identity layer because there is no prior to anchor the trail to.

## Why doc injection alone is insufficient

The intuitive fix — retrieve the internal API reference and inject it at inference — does not close the gap. PriCoder evaluated this directly across three mainstream LLMs on private-library benchmarks: "even given accurate required knowledge, LLMs still struggle to invoke private-library APIs effectively"; their training-side intervention yields "over 20% gains in pass@1 in many settings" beyond doc retrieval ([Zhang et al., "To See is Not to Master", arxiv 2603.15159, 2026](https://arxiv.org/abs/2603.15159)).

Context conditioning shifts the model's distribution only within the support the prior already assigns non-trivial mass — and the prior assigns zero mass to the proprietary surface, so the closest-match attractor wins on every call the docs do not explicitly override. ExploraCoder confirms this from the opposite direction: forcing the agent to test against the real API at intermediate steps gains 11.99% over retrieval-based approaches and 17.28% over pretraining-based methods on unseen APIs ([Wang et al., "ExploraCoder", arxiv 2412.05366, 2024](https://arxiv.org/abs/2412.05366)). The doc is a reference; what is missing is a context-resident mental model that displaces the attractor at decision time.

## The bootstrapping hierarchy

Mastykarz proposes a five-layer teaching strategy. The order is load-bearing — skipping the identity layer leaves the wrong mental model intact ([Mastykarz, 2026](https://developer.microsoft.com/blog/when-the-model-has-never-seen-your-code)):

1. Identity and purpose — what the technology does and, explicitly, what it is not. "Contoso Identity uses mutual TLS with short-lived certificates, NOT OAuth." This is the layer that overrides closest-match.
2. Core concepts — 3 to 5 foundational concepts that replace the model's wrong mental model.
3. API shape and conventions — naming patterns, initialization flow, common signatures. Not an exhaustive reference.
4. Common patterns and workflows — 3 to 5 typical use cases with annotated examples. Example code carries more weight than parameter lists in retrieval studies ([Chen et al., "When LLMs Meet API Documentation", arxiv 2503.15231, 2025](https://arxiv.org/abs/2503.15231)).
5. Edge cases and gotchas — only useful after the basics land.

The five layers split across provisioning surfaces by what they need to be at different times:

| Layer | Surface | Why there |
|-------|---------|-----------|
| Identity, Concepts | [AGENTS.md / CLAUDE.md](../instructions/agents-md-as-table-of-contents.md) | Loads every session; this is the closest-match override |
| API shape, examples | Skills (on-demand) | Pulled in when the agent asks for them — keeps the always-loaded context lean |
| Lookup detail | MCP server | Returns only what the model asks for, centrally maintained |
| Reference implementations | Workspace code | Implicit teaching surface; agents pattern-match it anyway, so the existing code has to model the right shape |
| Diagnostics | Error messages | "Received: { clientId, scope } which appears to be an OAuth configuration" — turns the closest-match into a teaching signal |

The split matters because dumping all five layers into the always-loaded context blows the budget — a controlled evaluation found context files often reduce task success versus no context while raising inference cost over 20% when they include structural overviews ([Gloaguen et al., "Evaluating AGENTS.md", arxiv 2602.11988](https://arxiv.org/abs/2602.11988)). Identity is cheap and always-loaded; API shape and examples are expensive and on-demand.

## The baseline-then-override workflow

The diagnostic that drives provisioning is mechanical: run the task with no extensions and observe which public technology the model defaults to. "The baseline reveals the model's closest match, and that match is what your extensions need to override" ([Mastykarz, 2026](https://developer.microsoft.com/blog/when-the-model-has-never-seen-your-code)).

The identity layer then names the closest-match explicitly and contradicts it. This is the difference between a generic "uses our internal auth" line and the load-bearing form: "uses mutual TLS with short-lived certificates, not OAuth — do not generate `OAuth2Client`, `authorization_code` flows, or `Bearer` headers."

## Why it works

Each generation samples from the pretrained conditional distribution. For an unseen API, that distribution has zero mass on the correct shape, so the model collapses to the closest public API in training rather than admitting uncertainty — closest-match is the prior's reachable optimum, not a hallucination. Library Hallucinations in LLM-Generated Code measured how resilient that optimum is: fabricated library names are accepted in up to 99% of cases under plausible prompts ([Twist et al., "Library Hallucinations in LLM-Generated Code", arxiv 2509.22202, 2026](https://arxiv.org/abs/2509.22202)). Documentation injection adds mass to the right region, but the attractor still wins on every decision the docs do not explicitly override. The identity layer works by changing the frame: instead of "complete this code against the most likely API," the agent reads "this is technology X, X is not Y, treat Y patterns as errors" — displacing the prior across the whole generation, not one call at a time.

## When this backfires

The five-layer bootstrap is engineering. It pays off only when the proprietary surface is large enough, used often enough, and risky enough to justify the maintenance.

- The proprietary surface is tiny. A single internal helper does not justify a Skill plus MCP plus identity layer; the agent will get it wrong and a human review catches it cheaper than the provisioning costs to maintain.
- No one owns the reference material. If the identity layer, Skills, and MCP responses rot, the agent now follows confidently-wrong instructions instead of falling back to its (wrong) closest match — see [Stale AI Configuration Artifacts (Context Rot)](../patterns/anti-patterns/stale-ai-configuration-artifacts.md). Stale identity is worse than no identity.
- The internal SDK is a thin wrapper. If the proprietary surface is essentially OAuth plus a header, the closest-match default is about 80% right and the bootstrap budget buys little.
- Always-loaded context is already saturated. Per [Gloaguen et al., 2026](https://arxiv.org/abs/2602.11988), bulk context-file injection raises inference cost about 20% with no task-success gain. Keep identity in the always-loaded layer; push API shape, examples, and gotchas to on-demand Skills and MCP.
- The verifier is fast and lossless. When unit tests fully cover the internal SDK and run every commit, the closest-match failure surfaces in seconds — the provisioning is highest-value when wrong code looks plausible and reaches production unchecked.

## Example

A team building against `Contoso Identity` (proprietary mTLS auth SDK) ran the agent against the unprovisioned baseline and watched it generate OAuth2 code on every call — the closest-match attractor was clear. The override identity layer goes in the always-loaded `AGENTS.md`:

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

The shape and examples live in a Skill the agent invokes on demand, not in `AGENTS.md`:

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

The split keeps the always-loaded context small (identity only, ~30 lines), pushes the expensive parts behind on-demand Skill invocation, and gives the agent an explicit override against the closest-match it was producing in the baseline run.

## Key Takeaways

- The zero-prior case is structurally different from the stale-prior case: the model has no correct support to fall back on, so it collapses to the closest public API and presents it confidently ([Mastykarz, 2026](https://developer.microsoft.com/blog/when-the-model-has-never-seen-your-code)).
- Doc retrieval alone is insufficient — the closest-match attractor wins on every call the docs do not explicitly override ([Zhang et al., arxiv 2603.15159, 2026](https://arxiv.org/abs/2603.15159)).
- The five-layer bootstrap (identity → concepts → API shape → patterns → gotchas) displaces the prior; the identity layer is load-bearing because it names and contradicts the closest-match the baseline reveals.
- Split provisioning across surfaces by load shape: identity always-loaded, API shape and examples on-demand via Skills / MCP — otherwise context cost outruns task success ([Gloaguen et al., arxiv 2602.11988](https://arxiv.org/abs/2602.11988)).
- Run the unprovisioned baseline first; whichever public framework the model defaults to is what the provisioning has to override.

## Related

- [Training-Data Gravity: Agents Default to Deprecated APIs](../patterns/anti-patterns/training-data-gravity.md) — sibling failure mode for *stale* priors on public APIs; the zero-prior case has no upper bound on the doc-injection gap that page documents.
- [Seeding Agent Context: Breadcrumbs in Code](seeding-agent-context.md) — general breadcrumbs technique; this page is the subset where the breadcrumbs must include an identity layer because the model has no prior to anchor the trail to.
- [Discoverable vs Non-Discoverable Context](discoverable-vs-nondiscoverable-context.md) — zero-prior identity is the canonical *non-discoverable* content; the model cannot infer it from any file because the proprietary shape is not in the training distribution.
- [Context Hub: On-Demand Versioned API Docs for Coding Agents](context-hub.md) — the on-demand-retrieval surface for the API-shape and examples layers, complementary to the always-loaded identity layer.
- [AGENTS.md as Table of Contents, Not Encyclopedia](../instructions/agents-md-as-table-of-contents.md) — keeps the always-loaded layer lean; identity and pointers live there, bulk reference does not.
