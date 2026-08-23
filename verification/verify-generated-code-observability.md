---
title: "Verify Observability in Agent-Generated Code"
description: "Coding agents pass functional tests but under-instrument the code they write — verify runtime fault-signal coverage with fault injection, not the mere presence of logging."
tags:
  - tool-agnostic
  - testing-verification
  - observability
  - arxiv
maturity: emerging
last_reviewed: 2026-07-10
---

# Verify Observability in Agent-Generated Code

> Agent-generated code passes functional tests but under-instruments — verify runtime fault-signal coverage, not the presence of logging.

Coding agents optimize for functional correctness. A generated service can pass every test and still be undiagnosable in production, because the model instruments code the way it saw code written, not the way failures need to be exposed. Across 200 agent-generated microservice systems deployed on Kubernetes and hit with 13 injected fault types, generated systems surfaced an explicit fault signal for at most 13.99% of failures despite having logging present ([arxiv 2607.05785](https://arxiv.org/abs/2607.05785v1)). Treat observability as an explicit requirement and verify it separately from behavior.

## The gap is semantic, not volumetric

The problem is not missing logs. It is logs that "execute correctly but rarely expose informative fault signals" — abundant output that lacks the failure-specific semantics a diagnosing engineer needs ([arxiv 2607.05785](https://arxiv.org/abs/2607.05785v1)). When the study removed observability statements from 1,223 code instances and asked models to restore them, they placed instrumentation in roughly the right regions but captured the wrong details: best-configuration position scores (F1 around 0.59 to 0.63) consistently beat the token-level scores for what to capture (F1 around 0.38 to 0.40) ([arxiv 2607.05785](https://arxiv.org/abs/2607.05785v1)). Agents know where to log better than they know what a failure needs recorded.

## Verify fault-signal coverage, not logging presence

A test suite confirms the happy path works. It says nothing about whether a production failure would leave a diagnosable trace. Add a separate check that injects faults and asks whether the captured signals name the cause.

The measurable target is fault-signal rate: inject a known failure, then check that a log entry explicitly encodes the failure-related semantics for it. A log counts only when it names the fault, not when it merely fired ([arxiv 2607.05785](https://arxiv.org/abs/2607.05785v1)). Run this across the fault classes you care about — dependency down, dependency slow, queue saturation, clock skew — because coverage varies sharply by fault: upstream failures were exposed 27.45% of the time, clock skew only 1.26% ([arxiv 2607.05785](https://arxiv.org/abs/2607.05785v1)). Gate the change on the fault-signal check the same way you gate on tests.

## Why it works

Generated code under-instruments because agents "primarily learn from static source code rather than runtime system behavior," and observability is "rarely represented as an independent objective in the training data" ([arxiv 2607.05785](https://arxiv.org/abs/2607.05785v1)). Without execution feedback, the model cannot reason about how a failure propagates, so it emits syntactically valid logging with no diagnostic payload. Functional tests pass because the behavior is correct; diagnosability fails because that correct behavior was never made observable. A verification step that exercises real failures is the feedback the training signal lacked.

## When this backfires

- Throwaway prototypes and spikes with no production diagnosis need — a fault-signal gate adds ceremony with no payoff.
- Systems already covered by platform-level auto-instrumentation (service mesh, OpenTelemetry sidecars) where request-boundary signals come for free; hand-authored logs are then duplicative and add cost.
- Chasing log volume instead of fault-specific semantics. Over-instrumentation is its own anti-pattern: high-volume, low-value logs raise cost and bury the entries that matter ([observability anti-patterns](https://dev.to/indika_wimalasuriya/observability-anti-patterns-and-how-aws-can-help-overcome-them-4566)). The target is signal coverage, never line count.
- Trusting a prompt to close the gap. An observability-oriented skill improved fault-signal rate but left a large gap — for one frontier model, only +0.99 percentage points ([arxiv 2607.05785](https://arxiv.org/abs/2607.05785v1)). Prompting alone gives false confidence unless you measure the runtime result.

## Example

A generated order service depends on a database. Functional tests pass. Before trusting it in production, inject a dependency failure and check the logs for an entry that names the cause.

```bash
# Fault injection: take the DB dependency down, drive one request, capture logs.
kubectl -n staging scale deploy/orders-db --replicas=0
curl -s localhost:8080/orders/42 || true
kubectl -n staging logs deploy/orders --since=30s > captured.log

# Pass only if a log entry explicitly names the failure, not just that a request ran.
grep -Eiq 'database.*(unavailable|connection refused|timeout)' captured.log \
  && echo "PASS: fault signal present" \
  || echo "FAIL: DB outage left no diagnosable log"
```

A generic `500 Internal Server Error` line fails this check: the request was logged, but the cause was not. The remediation is a log that records the dependency and failure mode — not another passing functional test.

## Key Takeaways

- Functional tests passing does not mean an agent-generated system is diagnosable; observability is a separate requirement.
- The failure mode is semantic, not volumetric — logs are present but lack failure-specific detail.
- Verify runtime fault-signal coverage with fault injection: a log counts only when it explicitly names the injected fault.
- Coverage varies by fault class, so probe the failures you care about rather than trusting an aggregate.
- Prompting an agent to "add observability" closes only part of the gap; measure the runtime result.

## Related

- [Planted-Bug Methodology: Deliberate Bugs as Observability Calibration](planted-bug-observability-calibration.md) — the same fault-injection shape aimed at calibrating an existing observability stack rather than newly generated code
- [Dependency Gap Validation for AI-Generated Code](dependency-gap-validation.md) — another non-functional property agents under-deliver; verify it in a clean run instead of trusting the output
- [Deterministic Guardrails Around Probabilistic Agents](deterministic-guardrails.md) — wrapping agent output in hard checks that hold regardless of what the model produces
- [Making Observability Legible to Agents](../observability/observability-legible-to-agents.md) — wiring real log, metric, and browser signals into agent context so a diagnosing agent has data to reason over
- [Agent Observability: OTel, Cost Tracking, and Trajectory Logging](../observability/agent-observability-otel.md) — the instrumentation substrate a fault-signal check verifies against
