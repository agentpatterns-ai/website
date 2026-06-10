---
title: "Multi-Turn Conversation Evaluation: Per-Turn and Trace-Level Scoring Together"
term: "Multi-Turn Conversation Evaluation"
description: "Single-turn scoring misses across-turn failures — context loss, intent drift, circular exchange. Pair per-turn scorers with a trace-level resolution check so the two layers catch what each misses alone."
tags:
  - testing-verification
  - evals
  - observability
  - agent-design
  - tool-agnostic
aliases:
  - per-turn vs trajectory scoring
  - conversation-level evaluation
  - trace-level scoring for conversations
last_reviewed: 2026-06-03
---

# Multi-Turn Conversation Evaluation

> Multi-turn conversation evaluation pairs per-turn scoring with a trace-level resolution check to catch failures that compound across turns.

## Two Layers, Different Failures

A conversational agent can score 100% on per-turn brand alignment while resolving 40% of issues — every reply is polite and policy-compliant, but the conversation never reaches a fix. Per-turn scoring sees only local quality; it cannot tell whether the agent dropped a fact from turn 2 or kept the user in a polite loop. ([Braintrust, 2026](https://www.braintrust.dev/blog/multi-turn-scoring))

Trace-level scoring grades the conversation as one unit against a goal-completion criterion (typically binary: "was the issue resolved?"). It catches the across-turn failures per-turn scoring is blind to, but its verdict is coarse and hides which turn drifted. Both are needed; the most diagnostic case is when they disagree.

| Per-turn | Trace-level | What it means |
|----------|------------|---------------|
| High | High | Both layers happy — good baseline |
| Low | High | Rough responses but issue resolved — fix tone, not flow |
| High | Low | "Sounds good, fixes nothing" — system prompt lacks resolution steps |
| Low | Low | Bot is broken — debug from the trace |

The high-per-turn + low-trace cell is the cheapest diagnostic in the table — per-turn metrics alone would call this conversation a success.

## Three Failure Classes Single-Turn Scoring Misses

Conversations carry state across turns. Three failure classes only emerge in that state-carrying setting:

- **Context loss** — the agent forgets a fact the user gave earlier (order number, account email). The per-turn response is locally coherent; the next turn re-asks for the dropped fact.
- **Intent drift** — the conversation gradually leaves the original goal. Stateful drift detection (RNN over per-turn embeddings, DeepContext) reaches F1 0.84 versus 0.67 for stateless filters like Llama-Prompt-Guard-2 and Granite-Guardian — the gap is the multi-turn signal stateless eval cannot see. ([DeepContext, 2026](https://arxiv.org/abs/2602.16935))
- **Circular exchange** — every turn is locally fine but the conversation makes no progress. The trace-level resolution check is the first metric to fail on a polite loop.

Drift-Bench formalises a related taxonomy of input faults that only surface across clarification turns — implicit intent, missing parameters, false presuppositions, ambiguous expressions. Agents that handle each turn well in isolation drop substantially when these faults force iterative disambiguation. ([Drift-Bench, 2026](https://arxiv.org/abs/2602.02455))

## What to Wire

Three pieces have to be in place before trace-level scoring works:

1. **Span grouping** — every turn logs as a child span under a shared trace ID. Without it, each turn is an unrelated root span and trace-level scoring has nothing to score: the framework cannot tell which turns belong together. ([Braintrust, 2026](https://www.braintrust.dev/blog/multi-turn-scoring))
2. **A per-turn scorer** — graded turn-by-turn (helpfulness, tone, policy compliance, format). LLM-as-a-judge against three or four binary sub-criteria is the standard pattern.
3. **A trace-level scorer** — graded against goal completion for the whole conversation, typically binary: did the agent satisfy the user's stated goal by the end of the trace.

Online scoring rules then run both scorers asynchronously against new production traces — per-turn rules span-scoped, trace-level rules trace-scoped. Sampling rate is the cost lever: 100% at low volume, lower as traffic scales.

## Why It Works

Failures emerging from accumulated state must be scored where that state is observable. Per-turn scoring projects the conversation into independent slices — exactly the projection in which context loss, intent drift, and circular exchange vanish; the trace is the smallest unit that exposes all three. The argument generalises beyond chatbots: the 2025 multi-turn agent survey names five evaluation dimensions — task completion, response quality, user experience, memory and context retention, planning and tool integration — and only the first two are cleanly observable per-turn. ([Multi-Turn Agent Survey, 2025](https://arxiv.org/abs/2503.22458))

## When This Backfires

Trace-level scoring is not free. Narrow scope when:

- **The agent is one-shot, not conversational.** A PR-fix or CI agent that takes a task and returns a patch has no across-turn failure surface. [pass@k metrics](pass-at-k-metrics.md) and [trajectory decomposition](trajectory-decomposition-diagnosis.md) cover the relevant axes; trace-level conversation scoring measures a dimension the workload lacks.
- **The judge is below the precision floor.** AgentRewardBench evaluated 12 LLM judges across 1,302 web-agent trajectories — none cleared 70% precision (GPT-4o 69.8%, Claude 3.7 Sonnet 68.8%, against 89.3% human agreement). Below that ceiling roughly one trace verdict in three is wrong. Pin to deterministic resolution checks (was a refund issued, a ticket closed) before defaulting to an LLM judge. ([AgentRewardBench, 2025](https://arxiv.org/abs/2504.08942))
- **Logs are not grouped.** If production logs every LLM call as its own root span, retrofitting trace-level scoring needs re-instrumentation or timestamp reconstruction. The failure is silent — scoring runs against fragments and produces numbers that look real.
- **Volume × per-trace cost exceeds the violation cost.** Every trace-level judge call is its own inference; at tens of thousands of conversations a day the bill can exceed the value of the violations caught. Sampling cuts cost but moves the metric from continuous to spot-check.

The distinct [Trajectory-Opaque Evaluation Gap](trajectory-opaque-evaluation-gap.md) covers the conjugate safety case: outcome-only grading misses safety violations even in single-turn conversations. Pair the two — per-turn + trace-level for quality and resolution, outcome + trajectory auditing for safety.

## Example

A customer-support chatbot resolves a return-and-refund request over four turns. Two scoring layers are wired against the trace:

**Per-turn scorer (brand alignment, LLM-judge against helpfulness + tone + policy):**

```
Turn 1: 50%  (acknowledged frustration, no next steps)
Turn 2: 50%  (asked for order number, did not state return policy)
Turn 3: 50%  (offered exchange, did not address the discount-code request)
Turn 4: 100% (clear conditions for qualifying)
Average: 62.5%
```

**Trace-level scorer (conversation quality, LLM-judge against binary resolution):**

```
Conversation quality: 100%
Reason: agent obtained order number, acknowledged the discount-code request,
        confirmed return status, and stated qualifying conditions. Issue
        resolved.
```

The divergence is diagnostic. Per-turn at 62.5% would normally trigger a tone-and-policy review; trace at 100% says the issue was fixed despite rough edges. The action is different in each direction: the per-turn scorer points engineering at the response-template prompt, the trace-level scorer at goal-completion logic. Acting on either number alone produces the wrong fix. ([Braintrust, 2026](https://www.braintrust.dev/blog/multi-turn-scoring))

## Key Takeaways

- Per-turn scoring evaluates each response in its local context; trace-level scoring evaluates the conversation against a goal-completion criterion. Both are required because they catch orthogonal failures.
- The high-per-turn + low-trace cell ("sounds good, fixes nothing") is the cheapest diagnostic — it points at the resolution gap that per-turn metrics alone would call a success.
- Three failure classes only emerge across turns: context loss, intent drift, and circular exchange. Single-turn scoring is structurally blind to all three.
- Span grouping is the prerequisite. Without a shared trace ID across turns, the framework cannot tell which turns belong to one conversation.
- Trace-level LLM judges have a measured precision ceiling near 70%; deterministic resolution checks (was a refund issued) are more reliable when they are expressible.

## Related

- [Trajectory-Opaque Evaluation Gap](trajectory-opaque-evaluation-gap.md)
- [Trajectory Decomposition: Diagnose Where Coding Agents Fail](trajectory-decomposition-diagnosis.md)
- [pass@k and pass^k: Capability and Consistency Metrics](pass-at-k-metrics.md)
- [Grade Agent Outcomes, Not Execution Paths](grade-agent-outcomes.md)
- [Anti-Reward-Hacking: Rubrics That Resist Gaming](anti-reward-hacking.md)
- [Using the Agent to Analyze Its Own Evaluation Transcripts](agent-transcript-analysis.md)
