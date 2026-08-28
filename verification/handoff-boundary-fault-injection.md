---
title: "Handoff-Boundary Fault Injection (llmmas-otel)"
term: "Handoff-Boundary Fault Injection"
description: "Inject a delay at the agent-to-agent send and diff the faulted trace against a structurally aligned baseline; the amplification it reports is a runtime number with a heavy tail, not a correctness one."
tags:
  - testing-verification
  - observability
  - multi-agent
  - tool-agnostic
  - arxiv
aliases:
  - agent-to-agent fault injection
  - delay amplification testing
  - trace-aligned baseline comparison
last_reviewed: 2026-08-27
maturity: emerging
---

# Handoff-Boundary Fault Injection (llmmas-otel)

> One injected fault at an agent-to-agent handoff amplified ChatDev's end-to-end runtime 59x on the mean and 6.6x on the median run.

Handoff-boundary fault injection pauses a message on its way between two agents, then compares that run against a baseline trace with the same span structure. The comparison unit is a metric the paper calls amplification: "the extra end-to-end runtime caused by the fault divided by the injected delay" ([Seyedghorban et al., arxiv 2608.24271v1](https://arxiv.org/abs/2608.24271v1)). A value near 1 means the delay cost what it cost. Values above 1 mean the pipeline spread it.

## Three conditions before the number means anything

- The pipeline is multi-phase and message-heavy. On the paper's two-agent Planner-to-Coder demo, both fault types amplified close to linearly. The large factors appear only on ChatDev, which runs three lifecycle phases across many specialized agents ([arxiv 2608.24271v1](https://arxiv.org/abs/2608.24271v1)).
- Runtime is the failure you care about. Amplification counts seconds, and the paper measures no correctness effect anywhere. If the question is whether a delayed handoff produces a worse answer, [HTTP-layer injection scored against pass@1](llm-api-fault-injection-http-layer.md) answers it and this does not.
- Someone has hours to read paired traces. The tool "does not yet provide higher-level analysis features such as paired-run differencing, trace summarization, root-cause ranking, or automated debugging reports; at present, users inspect the produced traces and run artifacts directly" ([arxiv 2608.24271v1](https://arxiv.org/abs/2608.24271v1)).

## The mean and the median disagree

On ChatDev, a 1000 ms delay at the planning-phase LLM call yielded "a mean amplification of 48.1 and a median of 13.9", while the same delay at the Planner-to-Coder send yielded "an even higher mean amplification of 59.2 (median 6.6)" ([arxiv 2608.24271v1](https://arxiv.org/abs/2608.24271v1)). Setup was the 30-task ProgramDev benchmark, five runs per task per condition.

| System | Fault | Mean | Median |
|---|---|---|---|
| Demo (2 agents) | LLM delay 1000 ms | 1.053 | 1.036 |
| Demo (2 agents) | A2A delay 1000 ms | 1.295 | 1.390 |
| ChatDev | LLM delay 1000 ms | 48.1 | 13.9 |
| ChatDev | A2A delay 1000 ms | 59.2 | 6.6 |

Read the bottom two rows together. The handoff wins on the mean by 11 points and loses on the median by more than half. A mean of 59.2 above a median of 6.6 describes a distribution where a handful of runs blow up and most do not, which is a different engineering problem from a boundary that is uniformly slow. Quote the mean and you overstate the typical run by roughly nine times. Report both figures or neither. The ordering that survives both statistics is the demo's, where the handoff amplifies more on mean and median alike.

## Where the injection points sit

Instrumentation covers six span levels: session, segment for the workflow phase, agent step, the paired a2a_send and a2a_receive, tool call, and LLM call. The public API is "thin decorators and context managers", wrapping a host workflow instead of replacing its orchestration ([arxiv 2608.24271v1](https://arxiv.org/abs/2608.24271v1)). Injection reaches four of those hook points, with fourteen boundary-and-fault pairs between them.

| Hook point | Faults available |
|---|---|
| A2A send | delay, drop, truncate |
| A2A receive | delay, drop |
| Tool call | delay, not_installed, timeout, malformed_response |
| LLM call | delay, rate_limit, timeout, network_error, malformed_response |

Copy that table whatever tool you use. The A2A rows are the two a transport-layer injector cannot reach: [AgentChaos patches the HTTP client and matches outgoing requests to LLM endpoints](llm-api-fault-injection-http-layer.md), and a message passed between agents in one process is neither.

## Why it works

Serialization produces the amplification. A multi-phase pipeline runs its stages in order, so a pause at one boundary shifts every later interaction rather than adding its own duration once. The paper attributes ChatDev's factors to "how a localized perturbation can cascade across many downstream interactions and LLM calls", and explains why the communication boundary concentrates it: "the final outcome often depends on the quality and timing of inter-agent handoffs rather than on isolated LLM calls alone" ([arxiv 2608.24271v1](https://arxiv.org/abs/2608.24271v1)).

Structural alignment is what makes the amplification measurable, and it is the half specific to this design. A faulted run records the fault on the same span in the same position as the baseline: an A2A delay lands on the a2a_send span carrying `llmmas.fault.injected=true` and `llmmas.fault.type=a2a.delay`. Injection is "not treated as a separate logging mode or a disconnected experiment pipeline, but as an overlay on the same execution structure used for normal runs" ([arxiv 2608.24271v1](https://arxiv.org/abs/2608.24271v1)). Two traces with identical span trees diff span for span. Two wall-clock numbers do not.

## Example

Walk through a hypothetical four-agent review pipeline where you suspect the reviewer-to-integrator handoff is the weak joint. Mark the six boundaries, run the task five times clean, then add one rule, `a2a.delay = 1000 ms` on that send, and run it five times again. You now have ten structurally identical traces, five carrying `fault.injected=true` on one span.

Compute amplification per pair, then read the spread rather than the average. Five runs at 1.2x say the handoff absorbs the delay and your suspicion was wrong. Four runs at 1.1x and one at 40x say something downstream retries or times out when its input arrives late, and that single trace is the artifact worth opening. The mean of those five is about 8.9x, and it describes none of them.

## When this backfires

- Instrumenting to avoid a structural fix. A hierarchical topology showed "the lowest performance drop of 5.5%, compared to 10.5% and 23.7% of other two structures" under faulty agents, and a reviewing Inspector agent recovered "up to 96.4% errors made by faulty agents" ([Zhang et al., arxiv 2408.00989v4](https://arxiv.org/abs/2408.00989v4)). Neither needs a single span. Spend the hours there first and reach for injection on the residue.
- Expecting the trace to diagnose itself. [AgentChaosBench](https://arxiv.org/abs/2608.14680v1) injects ten operational fault types at tool, model, guardrail, and inter-agent boundaries, then asks language models to read the telemetry. Local detectors up to 14B parameters reach 13.6% to 19.2% top-1 fault-type accuracy, a frontier model reaches 24.8%, and joint type-plus-location "tops out at 22%". Capturing the trace and understanding it are separate budgets.
- Leaving full-fidelity tracing on in production. Jaeger on the Train Ticket microservice benchmark showed "180% and 16% overhead on the tail and average latency, respectively" ([Toslali et al., arxiv 2405.15645v1](https://arxiv.org/abs/2405.15645v1)). That figure is weaker against agent systems, where a span costs microseconds against model calls measured in seconds, but it still argues against leaving an experiment rig on as a monitoring layer.
- A framework with no send seam. The API decorates boundaries the host workflow already has. A managed orchestrator that owns message passing gives you nothing to wrap, and the validation covers two Python systems.

## Key Takeaways

- Amplification is a runtime ratio. The paper measures no correctness effect anywhere, so a 59x figure carries no information about whether the run's answer was right.
- Report mean and median together. ChatDev's handoff delay reads 59.2 mean against 6.6 median, and the two numbers imply different fixes.
- Run both injection surfaces. An HTTP-layer wrapper never sees an in-process message, so it scores every architecture as if its handoffs were free.
- Record the fault on the same span in the same position, so the two runs diff. That design choice is worth copying even in your own rig.
- The published rig stops at artifact generation, and it is validated on two systems at one delay value. Budget the trace-reading time before the injection time.

## Related

- [LLM API Fault Injection at the HTTP Layer (AgentChaos)](llm-api-fault-injection-http-layer.md) — the same inject-and-score loop at the LLM response boundary, scored against pass@1 rather than runtime
- [FLARE: Coverage-Guided Fuzzing for Multi-Agent LLM Systems](flare-multi-agent-fuzzing.md) — explores the input space rather than perturbing a fixed boundary
- [Planted-Bug Methodology: Deliberate Bugs as Observability Calibration](planted-bug-observability-calibration.md) — the calibration step this technique assumes has already passed
- [Failure-Aware Observability for Multi-Agent LLM Systems](../observability/failure-aware-observability-multi-agent.md) — six trace signals for diagnosing an organic failure, where this page causes one
- [Subagent OTel Trace Correlation via agent_id Attribute](../observability/subagent-otel-trace-correlation.md) — the attribute propagation that makes per-agent span queries work
