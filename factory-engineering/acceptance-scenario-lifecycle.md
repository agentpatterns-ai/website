---
title: "Acceptance Scenario Lifecycle for Software Factories"
term: "Acceptance Scenario Lifecycle"
description: "Maintain acceptance evidence as requirements, generated products, and dependencies change. Assign scenario owners, record versions, and review stale results."
tags:
  - factory-engineering
  - tool-agnostic
last_reviewed: 2026-11-06
maturity: emerging
---

# Acceptance Scenario Lifecycle

> Acceptance scenarios need maintained evidence when generated products require end-to-end checks beyond ordinary developer tests.

An acceptance scenario lifecycle connects stated requirements to product observations and later maintenance decisions. Use it when you can maintain separate acceptance cases and check dependency doubles. The workflow below is editorial synthesis from [StrongDM's factory account](https://factory.strongdm.ai/), [Anthropic's evaluation guidance](https://www.anthropic.com/research/demystifying-evals-for-ai-agents), and [versioned evaluation practice](https://docs.langchain.com/langsmith/evaluation-concepts). Its complete factory-wide form lacks independent outcome validation in the evidence reviewed here. Anthropic evaluates agents; applying that guidance to generated products is an explicit extension.

## Keep requirements visible

Give developers the full product requirement and ordinary development checks. Reserve concrete acceptance cases only when they test that stated contract. Anthropic describes Terminal-Bench graders that assumed an unspecified script filepath. Such failures expose ambiguous tasks. [Anthropic's task-design guidance](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)

StrongDM reports end-to-end user stories used as holdouts, often outside the codebase, after agents exploited narrow tests. This supports attributed practice, without proving that holdouts prevent gaming. Repository location alone does not establish independence; use [oracle protection](../patterns/agent-design/protect-the-oracle-from-the-agent.md) for change authority and enforcement. [StrongDM's account](https://factory.strongdm.ai/)

## Assign responsibility at each transition

Use these proposed responsibilities to adapt [evaluation ownership and maintenance](https://www.anthropic.com/research/demystifying-evals-for-ai-agents) to product delivery. They do not prescribe staffing or a fixed stage count. One person can hold several responsibilities where local controls permit.

| Transition | Responsible actor | Required handoff |
|---|---|---|
| Specification | Product or domain owner approves requirements; contributors propose cases; scenario owner approves coverage | Requirement revision and mapped cases |
| Implementation | Coding agent produces the candidate; scenario owner reviews requested expectation changes | Identified artifact and separate scenario-change request |
| Validation | Evaluation maintainer supplies versions; runner executes cases | Product observations, trial evidence, and verdict record |
| Interpretation | Scenario owner diagnoses failures and uncertainty with domain experts | Product verdict or inconclusive result with reason and diagnosis owner |
| Maintenance | Product owner approves contract changes; scenario owner revises or retires cases | Revision decision, successor references, and affected reruns |

Inspect the delivered product's external behavior. The coding agent's completion message cannot establish that outcome. Preserve multiple trial results when behavior varies, and calibrate model graders with experts. This applies Anthropic's [outcome and grader guidance](https://www.anthropic.com/research/demystifying-evals-for-ai-agents) to the candidate artifact.

End this workflow at the acceptance record and maintenance decision. A pass grants no merge or release permission. Use the [factory engineering index](index.md) for the wider delivery process.

## Record the evidence and its limits

LangSmith versions dataset edits and associates experiments with application versions. Extend those practices with this recommended verdict record; neither source establishes automatic capture of every field. [Dataset management](https://docs.langchain.com/langsmith/manage-datasets), [evaluation concepts](https://docs.langchain.com/langsmith/evaluation-concepts)

- Requirement and scenario IDs with revisions
- Tested artifact digest, environment configuration, and double revisions
- Grader or rubric revision, plus judge model and settings when used
- Trial IDs, timestamps, observed outputs, and coverage limits
- Verdict, reason, responsible owner, and linked contract-change decision

Use pass or fail for supported product judgments. Record inconclusive for missing observations, environment failure, or unresolved grader disagreement. Retain the reason and assign diagnosis before rerunning. This policy adapts Anthropic's [insufficient-evidence and infrastructure guidance](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).

Treat stale as evidence applicability, separate from the verdict. Review reuse after changes to the artifact, requirement, scenario, grader, or relevant dependency. Preserve original results under their versions. This proposed rule combines [versioned evaluation](https://docs.langchain.com/langsmith/evaluation-concepts) with [dependency contract checks](https://martinfowler.com/bliki/ContractTest.html).

For legitimate contract changes, obtain product-owner approval before revising expectations. Retire obsolete cases with a reason and successor reference; rerun affected cases. For escaped defects, diagnose a missing case, faulty expectation, or deficient double before adding regression coverage. These are proposed maintenance decisions based on [production-feedback guidance](https://www.anthropic.com/research/demystifying-evals-for-ai-agents) and [contract testing](https://martinfowler.com/bliki/ContractTest.html).

## Why it works

Version associations identify what a result tested. Contract checks examine whether doubles still match dependencies. Together, they support selecting evidence to review and rerun after changes. This causal argument combines [LangSmith's experiment model](https://docs.langchain.com/langsmith/evaluation-concepts) and [Fowler's contract tests](https://martinfowler.com/bliki/ContractTest.html); it does not establish general correctness or autonomous release safety.

## When this backfires

Keep focused deterministic checks. Broad UI tests can be brittle, costly, and slow; Fowler allows exceptions when higher-level tests are reliable and cheap. If requirements change faster than owners can review scenarios, prefer visible checks close to implementation until you can maintain the separate suite. This is a workflow cost judgment, without a measured team-size threshold. [Test Pyramid](https://martinfowler.com/bliki/TestPyramid.html)

## Example

StrongDM names Okta, Jira, Slack, Google Docs, Google Drive, and Google Sheets as service twins. It describes building doubles from API contracts and observed edge cases, then comparing them with live dependencies. Agreement covers exercised behavior; it does not establish completeness. [Digital Twin Universe](https://factory.strongdm.ai/techniques/dtu)

Use doubles for hazardous or expensive cases, with a separate fidelity check against real dependencies. Base that check on [StrongDM's comparison loop](https://factory.strongdm.ai/techniques/dtu) and [contract testing](https://martinfowler.com/bliki/ContractTest.html). Investigate contract failures separately from application failures.

Stripe supplies a concrete limitation: its sandbox mocks payment-gateway requests, so charge latency differs from live behavior. Stripe recommends simulated delays based on observed live-call durations for load tests. A sandbox pass therefore cannot establish production latency. Record that limit beside the verdict. This is Stripe's documented limitation, not a reported StrongDM defect. [Stripe load-testing guidance](https://docs.stripe.com/rate-limits)

## Key Takeaways

- Preserve old verdicts when expectations change; rerun against the approved contract.
- Separate inconclusive results from product failures and stale evidence from current evidence.
- Keep acceptance results separate from permission to merge or release.

## Related

- [Release Authority Boundaries for Software Factories](release-authority-boundaries.md)
- [Factory Engineering Across Software Delivery Systems](factory-engineering.md)
- [Sim-to-Real Tool-Use Perturbations](../verification/tool-use-sim-to-real-perturbation-taxonomy.md) — coverage beyond modeled dependency behavior
- [Simulation and Replay Testing](../workflows/simulation-replay-testing.md) — replay development tasks to assess agent changes, distinct from product acceptance
- [Evidence-Bundled Agent PRs](../verification/evidence-bundled-agent-prs.md) — package evidence for reviewers
- [Issue-to-PR Delegation Pipeline](../workflows/issue-to-pr-delegation-pipeline.md) — stage inputs, outputs, and terminal states
