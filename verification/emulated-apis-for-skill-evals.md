---
title: "Emulated APIs for Agent Skill Evals"
term: "Emulated-API Skill Evals"
description: "Run an API-calling skill's evals against a transparent emulator at the real URL — keeping cost, live-data mutation, and shared-state non-determinism out of the score without rewriting the skill under test."
tags:
  - testing-verification
  - evals
  - skills
  - tool-agnostic
aliases:
  - API emulation for skill evals
  - proxy-based API emulation
last_reviewed: 2026-07-20
maturity: emerging
---

# Emulated APIs for Agent Skill Evals

> Run an API-calling skill's evals against a transparent emulator at the real URL — deterministic, free, and non-mutating — instead of the live service.

When a skill wraps an external API, evaluating it against the live service contaminates the measurement. [Skill evals](skill-evals.md) design the dataset, assertions, and trigger cases; this technique controls what the skill's HTTP calls actually hit while those cases run. It is the environment-isolation layer beneath the eval, not a substitute for it.

## Three problems with evaluating against live APIs

Pointing an eval loop at production APIs breaks three ways at once. [Source: [How to test agent skills without hitting real APIs](https://developer.microsoft.com/blog/how-to-test-agent-skills-without-hitting-real-apis/)]

- Cost. A modest suite runs at volume — 50 scenarios across 3 models at 5 repetitions is at least 750 billed calls per session, repeated every iteration.
- Live-data mutation. Once the skill writes, PATCH and DELETE calls change production state, so a later run scores against data an earlier run altered.
- Non-determinism. When other people or systems write the same shared data, a score moves between runs for reasons unrelated to the skill.

## The mock-server trap

The obvious fix — stand up a local mock and point the skill at it — carries two hidden costs. [Source: [Microsoft AX](https://developer.microsoft.com/blog/how-to-test-agent-skills-without-hitting-real-apis/)]

The first is maintenance: a hand-built server that reproduces endpoints, filtering, pagination, and PATCH/DELETE semantics is a project that drifts out of sync the moment the real API ships a change.

The second is subtler and more damaging. Reaching a local mock means rewriting the URLs in the skill file, which changes the skill you evaluate. Swapping `https://api.contoso.com/products` for `http://localhost:3000/products` is a different set of tokens, and every token influences the model's reasoning — so the rewrite injects a variable into the exact thing the eval measures.

## Emulate at the real URL

A transparent proxy removes both costs. You define the base URL, the endpoints, and seed data; the proxy intercepts the skill's HTTP traffic and answers locally. The skill keeps calling the real URLs and cannot tell that a proxy replied instead of the server. [Source: [Microsoft AX](https://developer.microsoft.com/blog/how-to-test-agent-skills-without-hitting-real-apis/)] There is no server to build, and the seed data resets each run so scores stay deterministic.

Microsoft's Dev Proxy implements this pattern and ships a `skill-api-emulation` sample with a product-catalog API and skill definitions for GitHub Copilot CLI, Claude Code CLI, and Codex CLI. [Source: [Microsoft AX](https://developer.microsoft.com/blog/how-to-test-agent-skills-without-hitting-real-apis/)] The proxy intercepts requests and can also simulate errors, rate limits, and latency without touching application code. [Source: [Dev Proxy: what is a proxy](https://learn.microsoft.com/en-us/microsoft-cloud/dev/dev-proxy/concepts/what-is-proxy)] [Source: [InfoWorld: Microsoft's Dev Proxy puts APIs to the test](https://www.infoworld.com/article/4104363/microsofts-dev-proxy-puts-apis-to-the-test.html)]

The bar for a useful emulator is deliberately low: stable URLs, realistic payloads, and correct HTTP semantics for the operations the skill actually performs — you model the calls under test, not the whole API. [Source: [Microsoft AX](https://developer.microsoft.com/blog/how-to-test-agent-skills-without-hitting-real-apis/)]

## Why it works

The technique works because it separates two variables an eval loop otherwise conflates: the token stream the model reasons over (the skill's literal URLs and payload shapes) and the source of each response (live service or local seed data). A network-level proxy holds the first constant and makes the second free and deterministic, so the run measures the skill as shipped rather than a URL-rewritten variant. [Source: [Microsoft AX](https://developer.microsoft.com/blog/how-to-test-agent-skills-without-hitting-real-apis/)] The underlying isolation — impersonate a dependency at the network layer so the client cannot distinguish it from the real one — is established service virtualization. [Source: [SmartBear: API service virtualization](https://smartbear.com/learn/api-testing/api-service-virtualization/)]

## When this backfires

An emulator is still a test double, and doubles drift. A double that returns last month's shape stays green while production breaks, so an emulator kept in sync only by hand gives false confidence exactly like the mock it replaced. Contract testing — verifying the double against the real provider — is the complement that closes this gap, not something emulation removes. [Source: [Pactflow: What is contract testing](https://pactflow.io/blog/what-is-contract-testing/)]

Prefer a different setup when:

- The skill's value is handling real-API edge cases — rate-limit headers, pagination quirks, partial failures, eventual consistency — that the emulator does not seed. It scores the happy path and hides the failures that matter. [Source: [SmartBear](https://smartbear.com/learn/api-testing/api-service-virtualization/)]
- The API has no stable, documented schema, so seed data is a guess that diverges from production undetected.
- Auth flows defeat a transparent proxy — signed requests, short-lived tokens, or mTLS the emulator cannot reproduce.
- Eval volume is low. A handful of manual runs does not amortize the setup and upkeep.
- A vendor sandbox already exists and never drifts. A parallel emulator only adds a divergence surface.

## Example

The same skill, evaluated two ways. The URL rewrite biases the measurement; the proxy preserves it. [Source: [Microsoft AX](https://developer.microsoft.com/blog/how-to-test-agent-skills-without-hitting-real-apis/)]

Rewriting the skill's URL to reach a local mock changes the tokens under test:

```text
skill request: GET http://localhost:3000/products
# different tokens in context than the shipped skill — the eval no longer
# measures what you deploy
```

Leaving the URL and letting a proxy answer keeps them identical:

```text
skill request: GET https://api.contoso.com/products
# Dev Proxy intercepts and responds from products-data.json seed data;
# the skill's tokens are identical to production, and no live data changes
```

## Key Takeaways

- Live APIs make skill evals expensive, mutating, and non-deterministic — three reasons builders skip evaluation entirely.
- Rewriting skill URLs to `localhost` changes the token stream, so you stop measuring the skill you ship.
- A transparent proxy emulates at the real URL: the skill's tokens are unchanged, responses come from resettable seed data.
- Aim for stable URLs, realistic payloads, and correct HTTP semantics for the operations under test — nothing more.
- Emulators drift like any test double; add contract testing and fall back to a real sandbox when the skill's value is handling real-API edge cases.

## Related

- [Skill Evals](skill-evals.md) — the dataset, assertion, and trigger layer this technique isolates the environment for
- [Eval Blind Spots: Structural Gaps in Measurement Methodology](eval-blind-spots.md) — the skill-retrieval realism gap is a sibling measurement confound, at retrieval rather than the API call
- [Runnable Documentation as Agent Verification](runnable-documentation.md) — the same drift risk when tested doubles stand in for real dependencies in CI
- [Deterministic Guardrails Around Probabilistic Agents](deterministic-guardrails.md) — deterministic checks the emulated eval runs inside
- [Eval-Driven Development: Write Evals Before Building Agent Features](../workflows/eval-driven-development.md) — the loop this isolation feeds
- [Emulate Agent-Experience Changes Before Shipping](emulate-ax-changes-before-shipping.md) — the sibling that reuses this interception machinery for the opposite purpose: measuring a *proposed change* to a dependency, not isolating a fixed one
- [Skill Test Coverage as a Release Gate](skill-test-coverage-release-gate.md) — the adequacy question one level up: which of the skill's specified behaviors does any testcase activate at all
