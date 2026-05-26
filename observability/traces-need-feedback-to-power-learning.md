---
title: "Traces Need Feedback to Power Learning"
description: "Production traces only become a learning corpus when each one carries a verdict — couple feedback to the trace at write time, generate it from four sources, and store it on the run, not in a separate analytics tool."
tags:
  - observability
  - evals
  - testing-verification
  - tool-agnostic
aliases:
  - trace-feedback coupling
  - feedback-attached traces
  - trace as eval corpus
last_reviewed: 2026-05-27
---

# Traces Need Feedback to Power Learning

> A trace records what the agent did. A verdict labels whether it was right. Couple the two at write time and the trace store doubles as an eval corpus; leave them apart and you accumulate trajectories nobody can act on.

## The Gap a Trace Alone Cannot Close

Tracing-as-debugging works for one bug at a time. It does not scale into a learning loop, because the trace alone does not say whether the trajectory was good. As Harrison Chase puts it: "Traces alone do not create that loop. You also need feedback: signals that tell you whether the agent's behavior was useful, accepted, rejected, inefficient, risky, or wrong" ([LangChain, May 5 2026](https://www.langchain.com/blog/agent-observability-needs-feedback-to-power-learning)).

The same trace can describe a 40-step success or a 40-step failure. Without a verdict you cannot filter failures worth turning into evals, compare good and bad trajectories on one task, drive [incident-to-eval synthesis](../verification/incident-to-eval-synthesis.md) from production volume, or detect drift across the three improvement layers — model weights, harness scaffolding, retrieved context.

The fix is structural: every trace gets a verdict attached to the run, not stored in a parallel analytics system whose join keys never line up with the trace ID.

## The Four Sources of Feedback

The article names four feedback sources. Each has a different cost, latency, and noise profile, and a production system usually wires several together ([LangChain](https://www.langchain.com/blog/agent-observability-needs-feedback-to-power-learning)).

| Source | Example | Strength | Failure mode |
|--------|---------|----------|--------------|
| Direct user | Thumbs up/down, star rating, written correction | Cleanest verdict | Sparse — most users never rate |
| Indirect user | Lines of code accepted, diffs reverted, ticket reopened, answer copied, same question re-asked | High volume | Misattribution — a reverted diff might not be the agent's fault |
| LLM-as-judge | Online evaluator scoring helpfulness or policy compliance | Runs at scale | [Bias and ungrounding](https://arxiv.org/html/2503.05061v1) — judges drift from human verdicts when never recalibrated |
| Deterministic rule | Regex, schema check, citation validator | Cheap, exact, no model call | Only catches what you knew to look for |

The article's deterministic example: Claude Code's leaked `userPromptKeywords.ts` regex scans prompts for frustration words like "wtf", "horrible", "awful" and emits the hit as a feedback signal ([PCWorld](https://www.pcworld.com/article/3104748/claude-code-is-scanning-your-messages-for-curse-words.html), [Blake Crosley analysis](https://blakecrosley.com/blog/claude-code-source-leak)). When a cheap rule captures the signal, no model call is needed to label the trace.

## What the Platform Has to Do

Chase reduces the platform contract to three behaviours: store traces (trajectory, tool calls, metadata, timing, errors), store feedback attached to the run/trace/thread, and generate feedback (rules, online evaluators, sampling, annotation queues) ([LangChain](https://www.langchain.com/blog/agent-observability-needs-feedback-to-power-learning)).

The middle requirement is load-bearing. Feedback that lives in a different system than the trace breaks the join — you can describe how often users gave thumbs-down, but you cannot pull the *trajectories* that earned them for replay, eval seeding, or ablation.

## Tool-Agnostic Channel: OTel `gen_ai.evaluation.result`

OpenTelemetry has codified the channel. The GenAI semantic conventions define a `gen_ai.evaluation.result` event for attaching evaluator output to a run, parallel to the inference span ([OpenTelemetry GenAI events spec](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-events/)). Emit one event per verdict source — human thumbs-down, judge score, regex hit — each carrying the trace ID; downstream queries join on it.

This is the tool-agnostic equivalent of LangSmith's per-run feedback API or Phoenix's annotation primitives, ingestible by any backend that speaks the spec.

## When This Backfires

- **Ungrounded LLM-as-judge** — Judges never recalibrated against human verdicts encode their own biases — verbosity, position, self-preference — into the eval corpus. Frontier judges exceeded 50% error rates on bias benchmarks ([Justice or Prejudice, arxiv 2410.02736](https://arxiv.org/html/2410.02736v1)). Treat judge output as a triage signal, not a ground-truth label.
- **Indirect-signal misattribution** — A reverted diff might be a stylistic preference; a reopened ticket might be a follow-up question. Treating either as a binary failure label without causal validation poisons the corpus with false negatives.
- **Trace volume outpacing labelling capacity** — High-traffic agents accumulate traces faster than humans or judges can label them; without sampling rules the trace store becomes a graveyard.
- **Feedback decoupled from the trace** — Thumbs-up/down in product analytics while traces sit in an APM tool means the trace ID never appears in the analytics fact table. The loop never closes.

## Example

Capturing a regex-driven frustration signal as an OTel evaluation event, attached to the same span as the agent's response:

```python
from opentelemetry import trace

FRUSTRATION = re.compile(
    r"\b(wtf|horrible|awful|this sucks)\b",
    re.IGNORECASE,
)

def emit_frustration_feedback(span: trace.Span, user_message: str) -> None:
    """Attach a deterministic verdict to the current run span."""
    if not FRUSTRATION.search(user_message):
        return
    span.add_event(
        name="gen_ai.evaluation.result",
        attributes={
            "gen_ai.evaluation.name": "user_frustration_regex",
            "gen_ai.evaluation.score.label": "negative",
            "gen_ai.evaluation.explanation": "matched frustration regex",
        },
    )
```

The event sits on the same trace as the agent run, joined by trace ID. Backends that speak the OTel GenAI spec — LangSmith, Phoenix, Datadog LLM Observability, any OTLP-compatible store — surface it next to the trajectory rather than in a separate analytics tool ([Datadog OTel GenAI support](https://www.datadoghq.com/blog/llm-otel-semantic-convention/)).

## Key Takeaways

- Traces tell you what happened; feedback tells you what it meant — only the pair powers learning.
- Wire four feedback sources by cost: deterministic rules first, indirect user signals next, LLM-as-judge for scale, direct user verdicts where available.
- Store feedback on the run, not in a parallel analytics tool — the join key is the trace ID.
- Use the OTel `gen_ai.evaluation.result` event as the tool-agnostic channel; backends decode it natively.
- Recalibrate LLM-as-judge against human verdicts on a schedule — ungrounded judges drift.

## Related

- [Agent Observability: OTel, Cost Tracking, and Trajectory Logging](agent-observability-otel.md) — the instrumentation layer this pattern attaches feedback to
- [Observability Feedback Loop](observability-feedback-loop.md) — the seven-step debug runbook that consumes verdict-labelled traces one bug at a time
- [Incident-to-Eval Synthesis](../verification/incident-to-eval-synthesis.md) — the offline-corpus consumer that feedback-labelled traces feed
- [Audit Eval Suite](../agent-readiness/audit-eval-suite.md) — verifies the loop closes by checking that production traces and the eval corpus share provenance
- [Bootstrap OTel Init](../agent-readiness/bootstrap-otel-init.md) — wires the exporter that emits traces and evaluation events
- [Harness Bug Detection Patterns](harness-bug-postmortem-patterns.md) — three structural eval gaps that feedback-labelled traces help expose
