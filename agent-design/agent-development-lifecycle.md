---
title: "Agent Development Lifecycle for Agent Products"
term: "Agent Development Lifecycle"
description: "A four-phase meta-lifecycle for teams shipping agent products — build, test, deploy, monitor — with feedback signals from production runs flowing back into the next evaluation and build cycle."
tags:
  - agent-design
  - workflows
  - observability
  - evals
  - tool-agnostic
aliases:
  - ADLC
  - agent product lifecycle
  - agent shipping lifecycle
last_reviewed: 2026-06-12
maturity: established
---

# Agent Development Lifecycle for Agent Products

> A four-phase loop — build, test, deploy, monitor — for teams whose unit of work is the agent, with verdict-labelled traces feeding the next cycle.

## A Lifecycle for the Agent, Not the Feature

The Agent Development Lifecycle (ADLC) is a four-phase loop — build, test, deploy, monitor — for teams whose product *is* the agent, with verdict-labelled production traces feeding the next build cycle ([LangChain blog](https://www.langchain.com/blog/the-agent-development-lifecycle)).

It inverts two SDLC framings already on this project. [The 7 Phases of AI Development](../workflows/7-phases-ai-development.md) is a feature-level workflow for using an agent to ship code; [SDLC-Phase Skill Taxonomy](../workflows/sdlc-skill-taxonomy.md) organises a skill library so an agent acting on a codebase activates the right skills. Both treat the agent as the implement; ADLC treats it as the product.

The ordering is deliberate — test before deploy, monitor after deploy, feed learnings into the next build. Each phase produces an artifact the next consumes: scope doc, eval verdict, deploy artifact, verdict-labelled trace corpus.

```mermaid
graph LR
    B[Build] --> T[Test]
    T --> D[Deploy]
    D --> M[Monitor]
    M -->|verdict-labelled traces| B
    M -->|regression cases| T
```

## The Four Phases

### Build

Define scope, choose architecture, wire the harness. LangChain extends the phase beyond code, citing no-code and low-code surfaces that let non-engineers participate ([LangChain blog](https://www.langchain.com/blog/the-agent-development-lifecycle)). Produces: a runnable agent and a scope doc the test phase can score against.

### Test

Score the agent against an eval suite **before** it touches production. [Eval-Driven Development](../workflows/eval-driven-development.md) covers the discipline: define success criteria first, then build toward them. Reverse this and teams embed the live agent's bugs into the definition of correct. Produces: a pass/fail verdict and a gated deploy artifact.

### Deploy

Ship the agent in a controlled way. Canary rollouts, traffic shadowing, and rollback paths apply directly — [Canary Rollout for Agent Policy](../workflows/canary-rollout-agent-policy.md) covers the mechanics, and deploy-time permission scoping is the other half ([Permission Framework Over Model Trust](../security/permission-framework-over-model.md)). Produces: a running deployment plus the observability hooks the monitor phase consumes.

### Monitor

Trace every run, label every trace with a verdict, alert on drift. Agent dashboards track usage, feedback, latency, cost, tool calls, evaluator scores, and recurring failure patterns ([LangChain blog](https://www.langchain.com/blog/the-agent-development-lifecycle)).

The verdict step is load-bearing. [Traces Need Feedback to Power Learning](../observability/traces-need-feedback-to-power-learning.md) covers the four feedback sources — deterministic rule, LLM-as-judge, indirect user signal, direct user verdict — and the OTel `gen_ai.evaluation.result` channel for attaching them. Without that coupling, monitor produces trajectories nobody can act on. Produces: a verdict-labelled trace corpus and a regression-case stream for the next test cycle.

## Closing the Loop

[Continuous Agent Improvement](../workflows/continuous-agent-improvement.md) operationalises the Monitor → Build back-edge as an observation-to-update loop for agent configurations.

The underlying mechanism: **agents fail on distributions, not on cases**. Bug-fix-and-redeploy optimises one failing trace; a four-phase lifecycle with verdict-labelled traces optimises the failure-rate trend across a population. The phases are the minimum cut points where verdict-carrying signal can flow back.

## When ADLC Adds Value

The lifecycle pays off when regression cost exceeds four-phase ceremony cost. That threshold rises with:

- Multi-tenant or multi-user products where one regression affects many sessions
- Long-horizon agents whose failure modes only surface across populations of runs
- Teams with at least one prior regression that cost real time

## When It Does Not

Failure conditions where ceremony costs more than it returns:

- **Single-agent solo team, pre-PMF**: rebuild–redeploy–glance-at-logs dominates until a regression actually hurts. The four phases describe a destination, not a starting state.
- **Stateless one-shot agents**: deterministic tool surfaces benefit more from classical web-service SRE than an agent-specific lifecycle.
- **Batch or cron-driven agents with no user surface**: three of four [feedback sources](../observability/traces-need-feedback-to-power-learning.md) are unavailable, so monitor collapses to deterministic-rule scoring.
- **Multi-tenant agents with strict privacy constraints**: trace-to-eval feedback (the [Eval-Driven Development](../workflows/eval-driven-development.md) input) can violate compliance unless inputs are not persisted — significant infra cost before the loop closes.

Ship the rebuild loop first; let the four phases differentiate as failure modes surface.

## Tool Mapping Is Not the Pattern

LangChain names its own stack: LangGraph for build, LangSmith for test and monitor, LangSmith Deployment for deploy ([LangChain blog](https://www.langchain.com/blog/the-agent-development-lifecycle), [Medium](https://medium.com/@sehaj23chawla/langsmith-and-langgraph-in-2026-how-langchains-agent-stack-quietly-became-the-default-f1609af5d658)). Other vendors converge on the same loop shape — Domino's "Agentic AI Development Lifecycle" ([NAND Research](https://nand-research.com/domino-data-lab-winter-release-2026-the-agentic-ai-development-lifecycle/)) and EPAM's "Agentic Development Lifecycle" ([EPAM](https://www.epam.com/insights/ai/blogs/agentic-development-lifecycle-explained)). The vendor stack is one instantiation; any team can wire the same lifecycle from OTel traces, an eval runner, and a deploy pipeline.

One caveat on scope: several 2026 framings treat security and governance as a first-class lifecycle concern, not a deploy-time control — prompt-injection red-teaming, governed agent catalogs, and mandatory release gates appear as intrinsic phases ([Cycode](https://cycode.com/blog/securing-adlc/), [Codebridge](https://www.codebridge.tech/articles/agentic-ai-software-development-lifecycle-the-production-ready-playbook), [IBM](https://www.ibm.com/think/topics/agent-development-lifecycle-adlc)). The loop here folds that into deploy via [Permission Framework Over Model Trust](../security/permission-framework-over-model.md); regulated or multi-tenant teams should treat governance as a cross-cutting gate on every phase, not one checkpoint.

## Example

A two-person team ships a support-triage agent and wants the loop without a vendor platform:

- **Build**: define scope (classify and route inbound tickets, never auto-reply), pick a single-agent harness, wire OTel tracing. Artifact: a runnable agent plus a one-page scope doc.
- **Test**: 40 labelled tickets become the eval suite. CI runs the agent against them and gates merge on ≥ 90% routing accuracy — written *before* the agent exists, so live bugs cannot redefine "correct." Artifact: a pass/fail verdict.
- **Deploy**: a canary routes 5% of live tickets through the new policy with a one-command rollback; permission scoping blocks any write path beyond the ticketing API. Artifact: a running deployment emitting traces.
- **Monitor**: every run is traced and labelled — deterministic rule (did routing match the human's later reassignment?), plus a direct thumbs-up/down from the agent on duty. A weekly job converts each mis-route into a regression case (Monitor → Test) and surfaces recurring failure clusters for the next scope revision (Monitor → Build).

No LangGraph or LangSmith required — OTel, a pytest eval runner, and a feature-flagged deploy reproduce the same back-edges.

## Key Takeaways

- ADLC is a meta-lifecycle for the agent product itself — distinct from a feature-level SDLC or a skill-library SDLC; same loop shape, different unit of work.
- The four phases — build, test, deploy, monitor — produce explicit hand-off artifacts: scope doc, eval verdict, deploy artifact, verdict-labelled traces.
- The Monitor → Test back-edge is operationalised by an incident-to-eval pipeline; the Monitor → Build back-edge by a [continuous-improvement loop](../workflows/continuous-agent-improvement.md).
- The mechanism is distributional: verdict-labelled traces let teams optimise failure-rate trends, not one-off failing cases.
- The lifecycle is not free — small teams pre-PMF, stateless one-shot agents, batch jobs with no user surface, and privacy-constrained agents should ship the collapsed rebuild loop first.

## Related

- [The 7 Phases of AI Development](../workflows/7-phases-ai-development.md) — feature-level SDLC for using an agent to ship code; contrast point.
- [SDLC-Phase Skill Taxonomy](../workflows/sdlc-skill-taxonomy.md) — lifecycle for an agent acting on a codebase; contrast point.
- [Eval-Driven Development](../workflows/eval-driven-development.md) — the test phase, in depth.
- [Traces Need Feedback to Power Learning](../observability/traces-need-feedback-to-power-learning.md) — how the monitor phase produces verdict-labelled traces.
- [Continuous Agent Improvement](../workflows/continuous-agent-improvement.md) — the Monitor → Build back-edge.
- [Canary Rollout for Agent Policy](../workflows/canary-rollout-agent-policy.md) — the deploy phase, in depth.
