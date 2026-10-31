---
title: "Mock-Boundary Validation for Agent-Built Systems"
term: "Mock-Boundary Validation"
description: "A passing mock-based suite does not validate the behavior of the real boundaries it replaces. In one single-developer report, four escaped defects all sat where the mocks ended."
tags:
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - real-environment validation at mocked seams
  - mocked-boundary defect concentration
last_reviewed: 2026-10-26
maturity: emerging
---

# Mock-Boundary Validation for Agent-Built Systems

> A green mock-based suite can miss real integration failures; mock-boundary validation checks the browser, model API, and SDK behavior it replaces.

List the boundaries your suite replaces with a test double, then check each one against the real thing before you read a green run as working software. An experience report on one developer building a compliance-critical exam-grading application, with an assistant writing all the code, records that "Four features passed the full suite and an automated headless smoke test, yet failed in use". Its authors draw the practitioner recommendation from that: "Validate in the real environment, not only against mocks: the browser, the language model, and integration boundaries are where the costly defects hide" ([Weber, Zimmermann and Franceschetti, arXiv:2610.30916v1](https://arxiv.org/abs/2610.30916v1)).

## What the case reports, and how far it reaches

This is one developer, one application, over one study period. The report calls itself "a single-case, single-developer, self-reported study" and says "the numbers are descriptive" rather than measured under control ([arXiv:2610.30916v1](https://arxiv.org/abs/2610.30916v1)). The application is roughly 9,000 lines of code excluding tests, and its suite grew from 415 automated assertions at the three-day mark to 804 by the 9 July 2026 cut-off ([arXiv:2610.30916v1](https://arxiv.org/abs/2610.30916v1)). The authors state that "all results come from one model family, Anthropic's Claude, in three successive versions during the study period" ([arXiv:2610.30916v1](https://arxiv.org/abs/2610.30916v1)). Treat what follows as evidence about that project, not an effect size for yours.

Four features in that project passed and then failed in use, and their locations were not scattered. "All four incidents arose where the mocks end: at the browser, the language-model API, and the SDK boundary" ([arXiv:2610.30916v1](https://arxiv.org/abs/2610.30916v1)). The report reads its own lesson as prior art rather than a discovery: "a green mock-based suite does not imply a working system, the classicist argument against doubles at the seams" ([arXiv:2610.30916v1](https://arxiv.org/abs/2610.30916v1)).

## Why it works

The report interprets its coverage gap through the relative cost of writing tests and code: "When a test costs about as much as the code it checks, coverage grows fastest where tests are trivial to write, in pure domain logic, and stays thin at the integration, framework, and SDK boundaries. The suite then comes back green where testing is easy and stays silent where the costly defects live" ([arXiv:2610.30916v1](https://arxiv.org/abs/2610.30916v1)). The suite checks behavior under its test doubles' assumptions. It does not establish that those assumptions match the real dependencies. A neighboring slice has been measured directly: the [test adequacy of LLM-dependent harness code](llm-dependent-harness-test-adequacy.md), meaning the harness statements that depend on model output.

## What seam validation does not reach

The severest defect in the case was not at a seam. One exam's edits surfaced in another, and "A hidden assumption about question identifiers caused it, not a mocked boundary. The defect survived several hundred passing tests and an automated interface harness. A human at the screen found and fixed it" ([arXiv:2610.30916v1](https://arxiv.org/abs/2610.30916v1)). A seam inventory narrows where to look first. It does not replace someone using the running system on real data.

## When this backfires

- The system has few external seams. The reported concentration comes from an application whose surface is a browser, two model SDKs, and image and PDF libraries. Build the inventory for your own dependencies; the report does not measure the return on validating a different seam set.
- The real-environment check has to be automated. If you cover every seam through full end-to-end tests, account for their costs. Mike Wacker put it plainly on the Google Testing Blog: "When the tests do run, flaky tests tend to be a fact of life. And even if a test finds a bug, that bug could be anywhere in the product" ([Wacker, 2015](https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html)).
- The evaluator is not the builder. In the reported case the developer was also the user and the domain expert, and the report sets its own limit there: "Hence, the boundary is the cost and availability of trustworthy evaluation" ([arXiv:2610.30916v1](https://arxiv.org/abs/2610.30916v1)). Where the person who can judge the running system is someone else, every real-environment look costs a handoff.
- A contract test can check part of the integration. Pactflow, which sells contract-testing tooling, claims you can use it "to replace many (or in some cases, all) of your end-to-end integrated tests". It defines end-to-end integrated testing as involving "all the components being deployed together in a real environment" ([Pactflow](https://pactflow.io/blog/what-is-contract-testing/)). Consider it where both sides of the integration can be verified; a published schema alone is not that verification.

## Example

The four escaped defects in the reported case, in the report's own description of each ([arXiv:2610.30916v1](https://arxiv.org/abs/2610.30916v1)):

- "An inline document preview rendered as a security error: the browser blocks data: URLs in iframes, which only a real browser shows."
- "A generation feature silently produced empty output: the token budget truncated the response, which the tests could not see because they mock the language model."
- "An overwrite was destructive only on an empty response from the language model".
- "a notebook plot was too large for the real API".

The report locates the set rather than mapping each one: "All four incidents arose where the mocks end: at the browser, the language-model API, and the SDK boundary." All three boundaries existed in the architecture before any of these failures. So the inventory is readable off the code, not off the defect log.

## Key Takeaways

- Write the seam list down as an artifact, one line per boundary the suite replaces with a double, and identify which real dependency behaviors the doubles leave untested.
- Use a contract test where both sides can be verified. Use a real-environment run where the boundary is a browser, a model, or an SDK limit.
- Keep one human pass over the running system on real data. In the reported case it was the only layer that caught a high-severity defect away from every mock.
- Read the single-developer scope honestly before carrying any of this upstream. The report offers mechanisms and descriptive counts, not a measured effect.

## Related

- [Test Adequacy of LLM-Dependent Harness Code](llm-dependent-harness-test-adequacy.md) — coverage thinning measured directly, over the harness statements that depend on model output
- [Emulated APIs for Agent Skill Evals](emulated-apis-for-skill-evals.md) — running an API-calling skill against a transparent emulator, and why doubles still drift
- [Constraint Decay in Backend Code Generation](constraint-decay-backend-agents.md) — where contract assertions under-detect, so a response shape passes while the query underneath is wrong
- [Mutation Testing as a Quality Gate for AI-Generated Test Suites](mutation-testing-quality-gate.md) — whether the tests that do exist would notice a regression
- [The Bottleneck Migration](../human/bottleneck-migration.md) — the economics behind the shift this page's source reports from inside one project
