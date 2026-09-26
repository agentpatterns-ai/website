---
title: "Trajectory Projection: A Flattened View of Agent Traces"
description: "A trajectory projection flattens a thread's traces into one ordered message list for behavioral review and scoring, not for attributing a multi-agent failure to its cause."
term: "Trajectory Projection"
tags:
  - observability
  - agent-design
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - flattened trajectory view
  - trajectory read model
  - session projection over traces
last_reviewed: 2026-09-26
maturity: adopted
---

# Trajectory Projection: A Flattened View of Agent Traces

> A trajectory projection flattens a thread's traces into one ordered message list for reviewing behavior, not for attributing a multi-agent failure to its cause.

A trajectory is a projection over the traces in a thread: it removes the nested run structure and keeps the messages and actions that explain an agent's behavior, each one appearing once, in the order it first happened ([LangChain blog, September 24, 2026](https://www.langchain.com/blog/langsmith-trajectories-tracing)). LangSmith shipped this view under that name. Langfuse offers a comparable session-level view: it groups every trace sharing a session identifier and replays it as "a simple session replay of the entire interaction" ([Langfuse Sessions docs](https://langfuse.com/docs/observability/features/sessions)).

## Route the question to the right artifact

The projection answers one kind of question well and two others badly. Check which one you are asking before you reach for it.

| Question | Read this |
|---|---|
| What did the agent do, and was the behavior right? | The trajectory — built for SME review, annotation queues, and dataset curation ([LangChain blog](https://www.langchain.com/blog/langsmith-trajectories-tracing)) |
| Did a retry or timeout happen, and how long did each step take? | The trace, which keeps the timing, retries, and execution metadata the projection drops ([LangChain blog](https://www.langchain.com/blog/langsmith-trajectories-tracing)) |
| Which agent or step caused a multi-agent failure? | Neither. Use a dependency-guided attribution method such as FALAT, or [per-node replay](offline-trajectory-replay-multi-agent-debugging.md) ([FALAT, arxiv 2606.00765v1](https://arxiv.org/abs/2606.00765v1); [CHIEF, arxiv 2602.23701v1](https://arxiv.org/abs/2602.23701v1)) |

## How the projection is built

LangSmith layers agent telemetry in three tiers, with the trajectory projected over them. Every unit of work an agent performs is recorded as a run. Runs belonging to a single operation form a trace, carrying the full execution tree, timing, and metadata. A thread links every trace in a multi-turn session. The trajectory is a view over all three: it flattens every run in the thread, across the main agent and any subagents, into one message sequence ordered by first appearance ([LangChain blog](https://www.langchain.com/blog/langsmith-trajectories-tracing)). The trace stays available underneath, and a reviewer can jump from a trajectory step into its trace. LangSmith calls the trace the source of truth for exactly how something executed.

Merging subagent messages into one sequence creates the projection's main reading hazard. The order records when each message first appeared, not what caused what, so two adjacent messages from different subagents need not be related. By analogy, the projection works like a [CQRS](https://martinfowler.com/bliki/CQRS.html) read model: derived from the record and shaped for one kind of query.

Vendors disagree on the word itself. Anthropic uses "transcript", "trace", and "trajectory" as synonyms for the complete record of a trial, tool calls and intermediate results included ([Anthropic, Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)). LangSmith's trajectory means the opposite: a lossy view with execution detail already stripped out. Check which sense a source intends before comparing claims across vendors.

## Why it works

Two mechanisms support the projection, and they carry different weight. A behavioral question is about the sequence of messages and actions, and a nested run tree mixes that sequence with execution metadata a reviewer has to scan past. Cutting the metadata cuts what a human reads. Langfuse makes a comparable argument for its session view: once engineers propagate a session identifier, "product managers and domain experts can replay conversations, score and annotate them in annotation queues... all without writing code" ([Langfuse for product teams](https://langfuse.com/resources/engineering/langfuse-for-product-teams)). No controlled study measures review time on a projection against a raw trace, so this half is a shared vendor design argument, not a measured result.

The second mechanism is indirect. The data shows long inputs hurt LLM judges on agent traces, though these studies measure error localization, not projection against trace. On TRAIL's 148 annotated traces and 841 tagged errors, the best model, Gemini-2.5-Pro, scores 11% on trace debugging; input length correlates with location accuracy at Pearson r = -0.379 and with joint accuracy at r = -0.291, and three of the eight tested models exceeded their context window on the longest traces ([TRAIL, arxiv 2505.08638v3](https://arxiv.org/abs/2505.08638v3)). Who&When finds the same pattern in multi-agent failure logs: "all three methods exhibit a decline in both metrics as context length increases," with step-level accuracy the more sensitive of the two ([Who&When, arxiv 2505.00212v3](https://arxiv.org/abs/2505.00212v3)). LangChain makes the length argument for online evaluators: thread-level inputs repeat context as turns accumulate, and a trajectory keeps each message once ([LangChain blog](https://www.langchain.com/blog/langsmith-trajectories-tracing)). A message-shaped input is also the format trajectory evaluators already expect: `agentevals` takes "a list of OpenAI format dicts or... LangChain BaseMessage classes," not a raw span tree ([agentevals README](https://github.com/langchain-ai/agentevals)).

## When this backfires

Flattening removes the structure that root-cause attribution needs. FALAT reports that "single-pass LLM judges treat trajectories as flattened inputs, making them vulnerable to positional bias, order sensitivity in the presented evidence, and limited hypothesis revision across long chains"; on the Who&When benchmark, its dependency-guided search reaches 46.0% step-level accuracy on algorithm-generated failures against 38.8% for the strongest single-pass judge (Claude-Sonnet-4), and 29.1% against 18.9% on hand-crafted ones. Its ablation isolates the structure itself: removing the hierarchical representation cuts step-level accuracy by 10.3 points on algorithm-generated trajectories and 5.0 on hand-crafted ones ([FALAT, arxiv 2606.00765v1](https://arxiv.org/abs/2606.00765v1)). CHIEF reports the same problem from the multi-agent side: treating "execution logs as flat sequences" leaves "ambiguous responsibility boundaries" between agents ([CHIEF, arxiv 2602.23701v1](https://arxiv.org/abs/2602.23701v1)).

The projection also hides a whole failure class on purpose. Timing, retries, and execution metadata live in the trace, not the trajectory, so an online evaluator scoring only trajectories cannot see them. Each still needs a separate trace-level check ([LangChain blog](https://www.langchain.com/blog/langsmith-trajectories-tracing)).

Two narrower conditions argue against building the projection at all. LangChain itself notes that for short, single-turn workflows the answer "is usually easy to find" in the trace directly ([LangChain blog](https://www.langchain.com/blog/langsmith-trajectories-tracing)). And flattening removes nesting and repeated context, not messages, so a session that overflows a judge's context can still overflow it once projected.

## Example

LangChain's launch post walks through a support-agent session of nine turns and sixty messages, where a customer complains that the answer was wrong. In the trajectory view, a reviewer scans the conversation, tool calls, and agent actions in order and finds the turn where the agent reused an old tool result instead of fetching current data. Only then do they open the underlying trace for that step, to read the exact tool input, output, timing, retries, and nested run structure ([LangChain blog](https://www.langchain.com/blog/langsmith-trajectories-tracing)). The trajectory located the step and the trace explained it. Neither view does both jobs.

To score the same trajectories automatically, pick an `agentevals` match mode. `strict` fits when order carries policy meaning, such as a policy lookup that must run before a vacation-time request. `unordered` checks "the same tool calls in any order," for example a policy lookup at any point before a pizza-party spend is authorized ([agentevals README](https://github.com/langchain-ai/agentevals)). Because projection order records arrival rather than cause, use `strict` only where the order is a real constraint.

## Key Takeaways

- A trajectory projection is a read-model derived from the trace; the trace stays the source of truth for execution detail.
- Use the trajectory for SME review, annotation queues, online behavioral scoring, and dataset curation; use the trace for retries, timing, and execution metadata.
- For root-cause attribution in a multi-agent failure, reach for a hierarchical or dependency view instead of the flat trajectory.
- Match the evaluator's match mode to the question: `strict` when call order is a real constraint, `unordered` when only coverage matters.
- "Trajectory" is not a fixed term across vendors. Confirm whether a source means the lossy projection or the complete record before comparing claims.

## Related

- [Trajectory as the Monitoring Unit for Production Agents](trajectory-as-monitoring-unit.md) — why the trajectory, not the prediction, is what production agent monitoring should track
- [Traces Need Feedback to Power Learning](traces-need-feedback-to-power-learning.md) — attaching verdicts to traces, the step SME review of a trajectory feeds
- [Offline Trajectory Replay for Multi-Agent Workflow Debugging](offline-trajectory-replay-multi-agent-debugging.md) — per-node rubric scoring against a captured trajectory, offline
- [Subagent OTel Trace Correlation via agent_id Attribute](subagent-otel-trace-correlation.md) — making subagent spans queryable by agent identity, the correlation this projection flattens away
- [Failure-Aware Observability for Multi-Agent LLM Systems](failure-aware-observability-multi-agent.md) — a six-signal taxonomy for catching a multi-agent run mid-failure
