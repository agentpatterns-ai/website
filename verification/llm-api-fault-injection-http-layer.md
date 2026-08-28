---
title: "LLM API Fault Injection at the HTTP Layer (AgentChaos)"
term: "HTTP-Layer LLM Fault Injection"
description: "Intercept LLM API responses and corrupt named fields to score agent robustness, on multi-stage systems with an interceptable transport and a clean baseline."
tags:
  - testing-verification
  - evals
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - AgentChaos fault injection
  - LLM API fault injection
  - chaos engineering for agent systems
last_reviewed: 2026-08-10
maturity: emerging
---

# LLM API Fault Injection at the HTTP Layer (AgentChaos)

> Fault injection at the HTTP layer corrupts named LLM response fields to yield a robustness score that tracks agent architecture more than model choice.

HTTP-layer fault injection wraps the agent's HTTP client, forwards each LLM request to the real provider, then mutates a named field of the response before the agent reads it. AgentChaos implements this by monkey-patching `httpx.AsyncClient` and matching outgoing requests to LLM endpoints such as `/chat/completions`, so no agent source code changes ([Tan et al., 2026](https://arxiv.org/abs/2608.06790v1)).

## When this technique pays off

Three preconditions decide whether the harness returns anything you can act on.

- The system has multiple stages. Measured drops in pass@1 ran from 0.87% on a single-agent system (Mini-SE on SWE-bench Pro) to 49.66% on a pipeline system (MapCoder on HumanEval+ under GPT-5.2, falling from 93.96% to 44.3%) ([Tan et al., 2026](https://arxiv.org/abs/2608.06790v1)). A one-agent loop with a human reading the output gives the injector little to propagate.
- The transport is interceptable. The published wrapper patches `httpx.AsyncClient`, so a vendor SDK with its own transport or a gateway in front of the app needs the interception point rebuilt first.
- A clean scored baseline exists. The metric is a delta against an unfaulted pass@1, so a team without an automatically scorable benchmark gets traces rather than a number.

## The fault taxonomy

Six fault types sit in three categories, each applied to either the `content` field or the `tool_calls` field of the response ([Tan et al., 2026](https://arxiv.org/abs/2608.06790v1)).

| Category | Fault types | What they model |
|----------|-------------|-----------------|
| Crash | Error, Timeout | Server overload (HTTP 5xx), network delay |
| Omission | Empty, Truncate | Safety-filter rejection, token-limit cutoff |
| Value | Corrupt, Schema | Encoding errors, format mismatch |

Injection position and persistence are separate axes, giving 65 configurations. Runs where the fault never fired are detected from the execution trace and excluded before scoring, so an unfired configuration cannot inflate the robustness estimate.

## Why it works

Every agent system reaches its model through the same HTTP interface, so one interception point is architecture-agnostic: a single wrapper covered five systems spanning conversation, debate, pipeline, evolutionary, and single-agent designs ([Tan et al., 2026](https://arxiv.org/abs/2608.06790v1)). Because each fault is deterministic, scoped to one named field, and pinned to a chosen call position, the resulting delta is attributable to that fault rather than to sampling noise. The architecture result follows from where recovery is possible. A pipeline propagates an upstream corruption through every downstream stage, while an iterative system gets another generation to absorb it, which is why MapCoder fell 48.61% on HumanEval and EvoMAC only 18.48%. [MAS-FIRE](https://arxiv.org/abs/2602.19843v1) reaches the same conclusion from a different injection layer, reporting that iterative closed-loop designs neutralize over 40% of faults that are catastrophic in linear workflows.

## The truncation blind spot

Truncation is the one fault that resists diagnosis. Rule-based diagnosis identified the fault type 91.04% of the time for Timeout and 96.74% for Empty, but 4.3% for Truncate ([Tan et al., 2026](https://arxiv.org/abs/2608.06790v1)). A truncated response is syntactically well-formed text with no error marker, so a pattern matcher has nothing to match, whereas an empty string is one trivially detected pattern. Overall accuracy is weak either way: 52.45% on fault type and 55.5% on fault step for the rule-based method, 47.25% and 53.52% for the LLM-based one.

The paper generalizes this to omission faults as a class, which its own per-type figures do not support for Empty. Read the finding as truncation-specific. The detection signal is free: the Anthropic Messages API returns `stop_reason: "max_tokens"` and warns that a truncated response may contain an incomplete `tool_use` block ([Anthropic](https://platform.claude.com/docs/en/api/handling-stop-reasons)). A harness has to read that field for it to help.

## When this backfires

- Failures that look like success. The metric is task failure, so plausible-but-wrong output that never raises stays invisible. MAS-FIRE catalogs that class as propagating silently without runtime exceptions ([Jia et al., 2026](https://arxiv.org/abs/2602.19843v1)). A clean injection run is not evidence of robustness.
- Portable magnitudes. [ReliabilityBench](https://arxiv.org/abs/2601.06112v1) runs a comparable chaos harness over 1,280 episodes and reports success falling from 96.9% to 88.1% at perturbation intensity 0.2, with rate limiting as the most damaging fault. Rankings and magnitudes are workload-specific.
- Harnesses that already validate. If you check `stop_reason` and schema-validate tool arguments at the boundary, the omission and value faults arrive already caught.

The harness competes with its own recommendations, which cost one branch per call and need no measurement first: validate output after each call, log `finish_reason` and response length, add stage-level validation.

## Example

A single configuration names four things: the fault type, the target field, the call position, and the persistence strategy. Position is the axis that separates architectures. MapCoder swings from 83.87% impact when the fault lands on the first call to −4.84% on the third, because a pipeline has no later stage left to absorb an early corruption ([Tan et al., 2026](https://arxiv.org/abs/2608.06790v1)). Injecting on every call removes the position question and yields each system's worst figure: MapCoder 62.39%, AutoGen 57.41%, MAD 54.74%, EvoMAC 47.64%, and Mini-SE 10%. Read the position curve rather than the single worst number. A flat curve says the architecture recovers wherever the fault lands, and a spike says one stage carries the whole run.

## Key Takeaways

- The robustness ranking held across all four backbone models tested, so a degraded run is a reason to inspect the orchestration before changing model.
- Record `stop_reason` and response length per call before building a harness to find truncation, because the logging is cheaper than the campaign.
- The pipeline-versus-iterative gap is a design lever: adding a recovery pass moves the score more than swapping models.
- Run the injector only where a delta is computable; without a scored baseline the exercise produces traces you still have to read by hand.

## Related

- [Tool-Use Sim-to-Real Perturbation Taxonomy](tool-use-sim-to-real-perturbation-taxonomy.md) — perturbs tool observations and actions rather than the model's own response
- [FLARE: Coverage-Guided Fuzzing for Multi-Agent LLM Systems](flare-multi-agent-fuzzing.md) — explores the input space instead of corrupting a fixed response field
- [Handoff-Boundary Fault Injection (llmmas-otel)](handoff-boundary-fault-injection.md) — injects at the agent-to-agent message boundary this transport-layer wrapper cannot reach, and scores runtime amplification rather than pass@1
- [Planted-Bug Methodology: Deliberate Bugs as Observability Calibration](planted-bug-observability-calibration.md) — the same inject-then-check-detection loop applied to instrumentation
- [Trajectory Decomposition: Diagnose Where Coding Agents Fail](trajectory-decomposition-diagnosis.md) — per-stage attribution for the runs an injection campaign flags
- [Agent Circuit Breaker](../patterns/agent-design/agent-circuit-breaker.md) — the runtime mitigation for the crash faults this technique simulates
