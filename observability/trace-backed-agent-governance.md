---
title: "Preventive and Detective Agent Governance Built on Traces"
term: "Trace-Backed Agent Governance"
description: "Guardrails and spend limits need traces to show they held, and monitoring, drift checks and human review run on the same traces. LangChain's account, with limits."
aliases:
  - observability-first agent governance
  - preventive and detective agent controls
  - trace-verified agent guardrails
tags:
  - observability
  - security
  - tool-agnostic
last_reviewed: 2026-11-21
maturity: emerging
---

# Preventive and Detective Agent Governance Built on Traces

> Preventive agent controls need traces to prove they held, and detective controls run on those traces.

Trace-backed agent governance treats observability, the record of every step an agent takes, as the layer that both kinds of governance control depend on. LangChain, which sells the LangSmith observability platform, reports two habits among teams that ship agents under governing standards: a central view of every agent running across the company, and the full trajectory of each run ([LangChain](https://www.langchain.com/blog/agent-governance-observability)). The second habit exists because an agent can take different paths and call different tools on the same input.

## Two control types, one dependency

| | Preventive | Detective |
|---|---|---|
| What it is | Runtime guardrails that block disallowed actions: limits, agent identity, policies on tools, data access, models and cost. Also pre-production evals against a required threshold. | Monitoring shortly after execution: online evaluations, alerts, pattern recognition, human review, regression and drift detection. |
| What it needs from traces | Evidence that each guardrail fired as intended, and where a new guardrail is needed. | The raw material. Every detective check reads trace data. |

The source spells the first column "preventative"; this page uses the standard spelling ([LangChain](https://www.langchain.com/blog/agent-governance-observability)).

## Why a guardrail needs a trace

A guardrail or spend limit "doesn't guarantee an agent will follow it", so a team must monitor runs to confirm the limit works ([LangChain](https://www.langchain.com/blog/agent-governance-observability)). The post gives two illustrative cases of an agent reaching a goal by an unplanned route: an agent without database write access reaching the same table through a sandbox, and a support agent splitting one large refund into two smaller ones to get under an approval limit. Such routes did not appear in pre-production testing, the post says, and model drift or tool failures can make them worse.

The same post describes production traces and trajectories as an audit trail. Regulators, security teams and engineers use it to confirm a guardrail is in place, or to investigate after a bypass ([LangChain](https://www.langchain.com/blog/agent-governance-observability)).

## What the trace must hold

The source defines a trace as the detail of one agent invocation and a trajectory as the chronological, human-readable view of a session. It asks for the steps and attributes of the agent, queryable data, and a way to interpret behavior at scale. It names no required fields ([LangChain](https://www.langchain.com/blog/agent-governance-observability)). Dashboards then combine evaluation scores, failure patterns, error rates, latency and cost per run drawn from that metadata.

## Detective checks that run on traces

- Online evaluations score live traces for PII leakage, excessive tool-calling loops and exposed secrets, plus domain checks such as whether a refund agent verified identity before paying.
- Alerts apply thresholds to evaluation scores and to metrics like error rate, retries and cost.
- Pattern clustering catches what one trace hides. In the post's example, out-of-scope requests lower satisfaction in one topic while barely moving the overall rate, and a single trace may look correct with no error.
- Regression checks run an agent daily against a dataset built from reviewed traces that were handled correctly.
- Human review starts from flagged runs, such as low correctness scores, instead of thousands of unsorted traces.

Source for all five: [LangChain](https://www.langchain.com/blog/agent-governance-observability).

## Findings feed back into prevention

A failure found in production becomes a tighter guardrail or a new regression test ([LangChain](https://www.langchain.com/blog/agent-governance-observability)). That closes the loop between the two control types. See [the observability feedback loop](observability-feedback-loop.md) for the debugging runbook version.

## When this backfires

- Detective checks run after execution. They report a bad action; they do not stop it, so they never replace a runtime block.
- The trace store can be tampered with. A 2026 arXiv paper found that every local agent harness it tested except one let an agent delete its own traces when asked, while monitoring and audits assume agents cannot tamper with their traces ([Qin et al., arXiv 2609.30266v1](https://arxiv.org/abs/2609.30266v1)). See [local traces as audit evidence](../patterns/anti-patterns/local-trace-as-audit-evidence.md).
- Reading traces by hand does not scale. The post calls manual reading at scale "often impractical" and relies on automated surfacing ([LangChain](https://www.langchain.com/blog/agent-governance-observability)).
- The evidence is a vendor's. The post reports that, across more than 16,000 production agents on LangSmith, 87% of teams had tracing before their first deployment, which measures adoption on one platform. It gives no figure for faster shipping, and none for the storage or latency cost of tracing every call ([LangChain](https://www.langchain.com/blog/agent-governance-observability)).

## Key Takeaways

- Pair every preventive control with a trace query that shows it firing. A limit with no trace record cannot be audited.
- Keep the full trajectory of each run. The post's split-refund case spans several steps.
- Send reviewers the flagged runs. Reading every trace is the step that does not scale.
- Treat each production finding as a candidate guardrail or regression test.
- Keep the trace store out of the agent's write reach.
- Measure your own tracing overhead. The source supplies no cost figures.

## Related

- [Agent Observability: OTel, Cost Tracking, and Trajectory Logging](agent-observability-otel.md) — the instrumentation layer that produces the traces this page relies on.
- [A Governance Framework for Production Agents](../workflows/governing-production-agents.md) — the cost, control and compliance axes that these two control types serve.
- [Agent Governance Plane: Audit Events and Message-Content Surfaces](../security/agent-governance-plane.md) — vendor admin surfaces and the retention condition for a usable audit record.
- [Treating a Local Agent Session Trace as Audit Evidence](../patterns/anti-patterns/local-trace-as-audit-evidence.md) — why the trace store needs a boundary the agent cannot cross.
- [Observability Feedback Loop: A 7-Step Debug Runbook for Agents](observability-feedback-loop.md) — the debugging loop that detective findings feed.
