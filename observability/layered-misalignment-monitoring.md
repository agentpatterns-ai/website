---
title: "Layered Misalignment Monitoring with Unflagged Sampling"
term: "Layered Misalignment Monitoring"
description: "Escalate suspicious agent activity through reviewers and investigators while sampling unflagged traffic. Keep workload coverage and response timing explicit."
tags:
  - observability
  - security
  - tool-agnostic
last_reviewed: 2026-11-06
maturity: emerging
---

# Layered Misalignment Monitoring with Unflagged Sampling

> Layered misalignment monitoring spends more review effort on suspicious agent activity while sampling unflagged traffic for missed cases.

Layered monitoring separates cheap screening from detailed investigation and human response. OpenAI describes four internal layers, with different routes for different workloads ([October 29 report](https://openai.com/index/how-we-detect-frontier-model-misalignment/)).

## Escalation has workload-specific routes

The reported architecture uses these stages ([system description](https://openai.com/index/how-we-detect-frontier-model-misalignment/)):

| Layer | Evidence and role |
|---|---|
| L0 | High-recall activation probes; randomly sample 5% of unflagged traffic for L1 |
| L1 | Review recent conversation, reasoning, and tool use within the agent's context window |
| L2 | Investigate earlier context windows where available; examine evidence with isolated code execution |
| L3 | Compare transcripts with network logs, telemetry, and prior cases |

Frontier reinforcement learning and internal Codex traffic skip L0. Both receive L1 checks after turns and compaction; a maximum 30-minute interval is being introduced. Separate security and alignment investigators review each flagged case where both are deployed. Some workloads skip L3 ([coverage and cadence](https://openai.com/index/how-we-detect-frontier-model-misalignment/)).

Paging is a separate decision. Highest-priority alerts typically reach responders within 15 minutes of the initial alert when paging is enabled. Internal Codex paging is disabled; some critical alerts can pause workloads automatically ([human response](https://openai.com/index/how-we-detect-frontier-model-misalignment/)). This is not an end-to-end detection deadline.

## Translate the design into a local contract

The following checks are design inferences from those distinctions:

- Name the evidence each stage can read. Mark missing history instead of treating a compacted view as complete.
- Record which workloads bypass screening and which bypass deeper investigation.
- Keep a sample path independent of the first classifier's verdict.
- Assign an owner to alerts and define what happens outside that owner's response hours.

Activation probes require internal model activations. A team with only transcripts needs a different first-stage detector and must evaluate its coverage independently.

## Test the response as well as detection

Use historical incidents and harmless simulated failures to test escalation. Measure missed cases separately from false alarms. Check whether a pause or alert reaches the right workload and operator.

A monitor that emits a finding still needs a response policy. Treat permission enforcement and containment as separate controls; the reported system positions monitoring alongside them ([defense-in-depth scope](https://openai.com/index/how-we-detect-frontier-model-misalignment/)).

## Key Takeaways

- Test a negative-sampling route independently of normal escalation.
- Record detection latency and responder latency as separate intervals.
- Make missing evidence and inactive paging visible in the coverage record.

## Related

- [Trajectory as the Monitoring Unit](trajectory-as-monitoring-unit.md) — select evidence beyond individual calls
- [Agent Observability with OpenTelemetry](agent-observability-otel.md) — collect run telemetry
- [Inline Safety Harness with Cascade Verification](../security/inline-lifecycle-safety-harness.md) — prospective per-call checks
