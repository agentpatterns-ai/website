---
title: "Stateful Agent Evals via State Snapshots and Transition Assertions"
term: "Stateful Agent State and Transition Evals"
description: "Assert on intermediate state and transitions, not just final output, to catch the four state-drift failures (wrong-but-consistent narrative, mid-context amnesia, stale assumptions, state corruption) that outcome-only and per-turn scorers structurally miss in side-effecting agents."
tags:
  - testing-verification
  - evals
  - agent-design
  - observability
  - tool-agnostic
  - arxiv
aliases:
  - state-based agent evaluation
  - state assertion evals for agents
  - transition assertions for stateful agents
last_reviewed: 2026-06-28
maturity: emerging
---

# Stateful Agent Evals via State Snapshots and Transition Assertions

> Assert on intermediate state and transitions, not just final output, so state-corruption failures stop hiding behind correct-looking endings.

## When to Reach for It

This technique is qualified — it pays off only when all of these hold:

- The agent has consequential side effects between steps — creates tickets, runs migrations, sends emails, writes to external systems. A bad intermediate decision produces bad consequences, not just a bad answer ([Braintrust, 2026-06-26](https://www.braintrust.dev/blog/stateful-agent-evals)).
- The bug class is state corruption that survives into the next step, not a single wrong tool call. Output-only scoring will accept a self-consistent-but-wrong trajectory; per-turn scoring will not see the corruption because each turn is locally coherent.
- You can afford a resettable, real-enough environment. Real-enough means the systems the agent meaningfully interacts with are present and writable; resettable means each eval run starts clean. AppWorld is the upper-bound illustration — roughly 60K LOC engine, 40K LOC benchmark, 1.8K unit tests over 14 months ([Wang et al., 2512.12791](https://arxiv.org/abs/2512.12791)).
- Outcome verification cannot directly assert the failure mode. If a passing test suite, an expected DB row, or a correct API response already proves correctness, [outcome grading](grade-agent-outcomes.md) is simpler and equally sound.

If any of those fail, the simpler defaults are [outcome grading](grade-agent-outcomes.md) for capability and [trajectory decomposition](trajectory-decomposition-diagnosis.md) or [dominator-graph invariants](dominator-graph-trajectory-invariants.md) when branching is real.

## Four Failure Classes Output-Only and Per-Turn Scorers Miss

Four state-drift failures only surface when an evaluator inspects the state the agent carries and mutates ([Braintrust, 2026-06-26](https://www.braintrust.dev/blog/stateful-agent-evals)):

- Wrong-but-consistent narrative — an early mis-summary becomes the substrate for every later step. The trajectory is internally self-consistent; the output looks thoughtful. Output-only scoring accepts it.
- Mid-context amnesia — a fact provided in step 2 is dropped, the agent completes a slightly different objective. Per-turn scoring sees coherent replies; outcome scoring sees a plausible result against the wrong objective.
- Stale assumptions — the agent honors an earlier policy or environment after the world changed. Each turn aligns with the stored history; only a transition check ("policy version at step N matches policy version at action time") catches it.
- State corruption — concurrent tasks or buggy updates silently break an invariant; the contradiction only surfaces many steps later. The failure has no local signal — it is only observable as a violated cross-step invariant.

## The Two Scoring Layers

The methodology pairs scoring at two levels ([Braintrust, 2026-06-26](https://www.braintrust.dev/blog/stateful-agent-evals)):

| Layer | What it scores | Typical scorer |
|-------|---------------|----------------|
| Span-level (per step) | Was this decision correct given the state at this step? | Code-based check on structured outputs (correct endpoint, expected fields, schema-valid args); LLM-as-judge for "was this tool call appropriate given context?" |
| Trace-level (end-to-end) | Did the agent reach the goal, take a reasonable path, and leave the environment in the right state? | Goal-completion judge with access to the full span tree; deterministic terminal-state checks where expressible |

The diagnostic case is when the two disagree — span-level pass but trace-level fail is the "thoughtful path, wrong destination" signal that maps to wrong-but-consistent narrative.

Three structural pieces have to be in place before either layer is meaningful:

1. Span grouping — every step logs as a child span under one trace ID. Without it, each step is an unrelated root span and trace-level scoring has nothing to score.
2. State capture — before/after snapshots logged alongside the action: the tool call arguments, the response, the relevant slice of accumulated context. This is what assertions read against.
3. A resettable environment — every run starts from a known state. If artifacts from run N affect run N+1, scores stop being comparable fast ([Braintrust, 2026-06-26](https://www.braintrust.dev/blog/stateful-agent-evals)).

## Why It Works

Failures emerging from accumulated state must be scored where that state is observable. Output-only grading projects the trajectory into a single end-state slice — the projection in which wrong-but-consistent narrative, mid-context amnesia, stale assumptions, and state corruption vanish, because a corrupted state can still produce a result that pattern-matches "correct" ([Braintrust, 2026-06-26](https://www.braintrust.dev/blog/stateful-agent-evals)). Per-turn scoring projects into independent slices — the projection in which they also vanish, because each turn is locally coherent on top of the corruption. The state itself between steps is the smallest projection that exposes all four; assertions on snapshots, transitions, and cross-step invariants are the smallest check that lives at that altitude. This is the same mechanism that justifies pairing per-turn with trace-level scoring for [multi-turn conversations](multi-turn-conversation-evaluation.md), lifted from conversation turns to side-effecting state mutations.

## When This Backfires

The technique is not free, and four conditions make it actively harmful:

- The agent is one-shot or has no consequential side effects. A PR-fix or summarisation agent that takes a task and returns a patch has no across-step state corruption surface. Mid-trajectory state assertions measure a dimension the workload lacks; [outcome grading](grade-agent-outcomes.md) plus [trajectory decomposition](trajectory-decomposition-diagnosis.md) cover the relevant axes.
- Over-specification penalises valid alternative paths. Asserting "the agent must set field X at step 3" rejects correct runs that produced the same end state through a different intermediate sequence. Frontier models routinely discover unexpected valid paths ([Anthropic, Demystifying Evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)). State assertions belong on invariants the world must satisfy (no negative balances, no orphaned rows, policy version matches action), not on prescribed sequences the agent must follow.
- Environment maintenance cost exceeds the violation cost. Building a resettable production-like replica is expensive. AppWorld's roughly 60K + 40K LOC + 1.8K tests over 14 months is the illustrative ceiling ([Wang et al., 2512.12791](https://arxiv.org/abs/2512.12791)). At low volume × low violation cost, the eval infrastructure outweighs the bugs it catches; sampling outcome grading is the cheaper coverage.
- The judge is below the precision floor. AgentRewardBench evaluated 12 LLM judges across 1,302 web-agent trajectories — none cleared 70% precision (GPT-4o 69.8%, Claude 3.7 Sonnet 68.8%, against 89.3% human agreement) ([AgentRewardBench, 2025](https://arxiv.org/abs/2504.08942)). Mid-trajectory LLM-as-judge state checks at scale will produce noisy verdicts. Pin to deterministic schema/structural checks where expressible; only reach for an LLM judge once they are exhausted.

The [trajectory-opaque evaluation gap](eval-blind-spots.md) frames the conjugate safety case for outcome-only grading; the over-specification trap is the conjugate cost for over-eager state assertions. The two warnings bound the space the technique is correct in.

## Example

A support agent processes a return-and-refund request. Three side-effecting steps: look up the order, verify return eligibility, issue the refund. A naïve outcome-only check ("refund row exists in DB") passes a run where the agent issued a refund against the wrong order id — the row exists, the policy was violated, the customer who didn't request a refund got one.

The two-layer scoring catches it. The pseudocode below shows the *shape* of the span-level and trace-level scorers — adapt to your framework's actual scoring API ([Braintrust's `@traced` / `wrapTraced` and trace-scoped scorers](https://www.braintrust.dev/blog/stateful-agent-evals) are one reference implementation):

```python
# Span-level scorer — runs per step, reads the captured state snapshot
def score_step(span):
    if span.tool == "issue_refund":
        # Cross-step invariant: refund target == order looked up earlier in this trace
        looked_up_order = span.trace.find_span("lookup_order").output["order_id"]
        refunded_order = span.input["order_id"]
        return {"passes": refunded_order == looked_up_order,
                "reason": "refund target matches looked-up order"}
    return {"passes": True}

# Trace-level scorer — runs once at end, asserts terminal state + invariants
def score_trace(trace):
    refund_row = db.refunds.get(trace.metadata["customer_id"])
    return {
        "refund_issued_to_correct_order": refund_row.order_id == trace.input["order_id"],
        "no_duplicate_refunds": db.refunds.count(trace.metadata["customer_id"]) == 1,
        "policy_version_matches_action": refund_row.policy_version == trace.metadata["policy_at_request"],
    }
```

The span-level check catches the wrong-order refund mid-trajectory; the trace-level invariants catch state corruption (duplicate row from a retry) and stale-assumption failures (refund issued under a policy that had since been updated). Neither check prescribes which tools the agent must call or in what order — the assertions are on what the world must look like at well-defined points, not on the path taken.

## Key Takeaways

- Output-only and per-turn scoring structurally miss four state-drift failures — wrong-but-consistent narrative, mid-context amnesia, stale assumptions, and state corruption — because they project the trajectory into the wrong granularity.
- Pair span-level scoring (per-step, against captured state) with trace-level scoring (end-to-end, against terminal state and cross-step invariants). The disagreement cases are the diagnostic.
- The hard problem is environment design, not metric choice — make state explicit (what's real vs mocked), resettable between runs, and don't chase perfect replay ([Braintrust, 2026-06-26](https://www.braintrust.dev/blog/stateful-agent-evals)).
- Assert on invariants the world must satisfy, not on prescribed tool sequences. Over-specified state checks reproduce the path-grading anti-pattern at a different altitude.
- The technique is qualified: skip it for one-shot agents without side effects, when outcome verification is directly assertable, when environment maintenance exceeds violation cost, or when an LLM judge sits below the ~70% precision floor without a deterministic backstop.

## Related

- [Grade Agent Outcomes, Not Execution Paths](grade-agent-outcomes.md) — the canonical default; state assertions are a tool for the failure surface outcome grading cannot see, not a replacement.
- [Multi-Turn Conversation Evaluation](multi-turn-conversation-evaluation.md) — the same per-step + trace-level mechanism, lifted from conversation turns to state mutations.
- [Trajectory-Opaque Evaluation Gap](eval-blind-spots.md) — the conjugate framing: outcome-only grading misses safety violations even before state is in play.
- [Dominator-Graph Trajectory Invariants for Non-Deterministic Agents](dominator-graph-trajectory-invariants.md) — when branching is real, dominance over trajectory graphs is the trajectory-level alternative to point state assertions.
- [Behavioral Testing for Non-Deterministic AI Agents](behavioral-testing-agents.md) — broader framing that situates state assertions within capability-matrix grading and end-state verification.
- [Trajectory Decomposition: Diagnose Where Coding Agents Fail](trajectory-decomposition-diagnosis.md) — per-stage IR diagnostics that complement state assertions when the failure is "where" rather than "what state".
