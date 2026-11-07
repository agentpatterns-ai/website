---
title: "Traces Need Feedback to Power Learning"
description: "Attach feedback to agent traces, review it in conversation context, and turn scores plus explanations into calibrated evaluators and regression datasets."
term: "Trace-Feedback Coupling"
tags:
  - observability
  - evals
  - testing-verification
  - tool-agnostic
aliases:
  - trace-feedback coupling
  - feedback-attached traces
  - trace as eval corpus
last_reviewed: 2026-11-06
maturity: established
---

# Traces Need Feedback to Power Learning

> A trace records behavior. Attach feedback with its source and explanation to make that behavior useful for evaluation and learning.

## Connect behavior to a verdict

Harrison Chase describes feedback as the missing input between observing an agent and improving its model, harness, or context. His platform contract has three parts: store traces, attach feedback to the relevant run or thread, and generate feedback through evaluators, rules, or review ([LangChain, May 5](https://www.langchain.com/blog/agent-observability-needs-feedback-to-power-learning)).

Braintrust likewise advocates keeping traces and evaluations together so a suspicious run can become a dataset entry without repeated exports ([trace and eval workflow](https://www.braintrust.dev/blog/traces-and-evals-same-place)). Separate systems can still work when stable identifiers preserve the join. Make retrieving the judged trajectory an acceptance check for any integration.

## Keep the four feedback sources distinct

Chase identifies direct user feedback, indirect behavior, model judges, and deterministic rules. He also discusses reported regex-based frustration detection as a possible signal; that report does not establish the current behavior of every coding assistant ([feedback sources](https://www.langchain.com/blog/agent-observability-needs-feedback-to-power-learning)).

Use the following review contract to avoid treating every signal as an equivalent verdict:

| Source | Example | Recommended interpretation |
|---|---|---|
| Direct user | Rating or written correction | Preserve the explanation and task context |
| Indirect user | Reverted diff or reopened ticket | Investigate cause before labeling agent failure |
| LLM judge | Policy-compliance score | Compare with expert judgments on representative cases |
| Deterministic rule | Schema failure or frustration-word match | Name exactly what matched; do not infer correctness from vocabulary |

A frustration match can select a trace for review without proving the agent was wrong. Keep a signal's origin visible when promoting it into a training or regression label.

## Review the conversation, then reuse the judgment

LangChain's November 3 guidance adds a concrete human-review path. Annotation queues can contain one run or an entire thread. Reviewers inspect earlier messages and tool calls, then record a score and their reason. Those judgments can calibrate LLM judges, improve online evaluators, and seed golden datasets ([human insight and trace review](https://www.langchain.com/blog/human-insight-strategic-advantage-agents)).

For a multi-turn failure, select the thread when earlier decisions explain the final answer. As a local review policy, retain the rubric version and the evidence behind each score. Review disagreements before converting them into expected outputs. A scalar score without its rationale gives the next reviewer little basis for correcting a bad label.

## Carry evaluation results through OpenTelemetry

The current GenAI convention defines the event name `gen_ai.evaluation.result`. It remains in development, and language support varies. Where possible, parent the event to the evaluated GenAI operation span; otherwise, use `gen_ai.response.id` when the span ID is unavailable ([GenAI event specification](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-events.md)).

The specification defines these fields:

| Attribute | Requirement |
|---|---|
| `gen_ai.evaluation.name` | Required evaluation name |
| `gen_ai.evaluation.score.label` | Required when applicable |
| `gen_ai.evaluation.score.value` | Required when applicable |
| `gen_ai.evaluation.explanation` | Recommended explanation |

Emit through your instrumentation's supported event/log API. Verify correlation and display in the chosen backend; accepting OTLP does not by itself establish a particular evaluation UI. Keep a frustration signal distinguishable from a reviewed correctness judgment when mapping feedback into these fields. The field contract above comes from the specification; no SDK implementation is tested here.

## Turn reviewed traces into regression cases

LangChain frames trace mining as a way to find improvement signals and curate data for model, harness, and memory changes ([data-mining discussion](https://www.langchain.com/blog/improving-agents-is-a-data-mining-problem)). Feed reviewed failures into [incident-to-eval synthesis](../verification/incident-to-eval-synthesis.md). Use [trajectory attribution for context repair](../context-engineering/trajectory-attribution-context-repair.md) to investigate contributing instructions or retrieved material; a failure label alone does not establish cause.

Keep sampling within review capacity and retain unreviewed status explicitly. Recheck automated judgments against expert labels: *Justice or Prejudice?* documents task-dependent biases across its judge evaluations, rather than a universal error rate for all judges ([paper, v2](https://arxiv.org/html/2410.02736v2)).

## Key Takeaways

- Attach the feedback source, explanation, and relevant run or thread.
- Use conversation context to turn a flag into a defensible judgment.
- Reuse reviewed cases for judge calibration and regression tests.
- Verify telemetry correlation and backend support end to end.

## Related

- [Agent Observability: OTel, Cost Tracking, and Trajectory Logging](agent-observability-otel.md) — the instrumentation layer
- [Observability Feedback Loop](observability-feedback-loop.md) — the debug runbook that consumes reviewed traces
- [Incident-to-Eval Synthesis](../verification/incident-to-eval-synthesis.md) — turn incidents into regression cases
- [Harness Bug Detection Patterns](harness-bug-postmortem-patterns.md) — identify gaps in evaluation coverage
