---
title: "Human-in-the-Loop Checkpoints as Loop Control"
term: "HITL Checkpoints as Loop Control"
description: "Treat human checkpoints as a loop-control primitive — a deliberate suspend that bounds an iteration or redirects the loop, not a generic safety gate around it."
tags:
  - loop-engineering
  - agent-design
  - tool-agnostic
aliases:
  - human checkpoints as loop control
  - HITL interrupts as loop control
  - human-in-the-loop as convergence aid
last_reviewed: 2026-06-29
maturity: adopted
---

# Human-in-the-Loop Checkpoints as Loop Control

> A human checkpoint inside an agent loop is a deliberate suspend that bounds the iteration or redirects the loop, not a safety gate around it.

## The reframe

The standard framing treats human-in-the-loop (HITL) as a safety mechanism — a gate before sensitive actions. That framing belongs at the workflow boundary and is covered by [Human-in-the-Loop Placement](../workflows/human-in-the-loop.md). This page is about HITL *inside* an agent loop, where the checkpoint is a loop-control primitive: the loop suspends, persists state, and waits for a four-way decision that determines what the next iteration does.

LangGraph's `interrupt()` makes the mechanism concrete. The function pauses graph execution at any point in a node; the checkpointer writes the exact state; the loop waits until a `Command(resume=...)` arrives, whose value becomes the return value of the `interrupt()` call ([LangGraph Interrupts](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/)). The loop did not just pause for approval — it accepted a new input and resumed iterating from there.

## The four decision verbs

A checkpoint exposes four loop-control verbs, codified by the [LangChain HITL middleware](https://docs.langchain.com/oss/python/langchain/human-in-the-loop):

| Verb | Loop effect | When it fits |
|------|-------------|--------------|
| `approve` | Continue with the proposed action unchanged | The agent's proposal is right; the gate exists for audit |
| `edit` | Replace the action's arguments, then continue | Right kind of step, wrong specifics |
| `reject` | Skip the action; the model gets the rejection as tool feedback and re-plans | The action is wrong; the loop should try a different branch |
| `respond` | Synthesize a tool result from the human's reply; do not run the tool | The human is the tool — `ask_user` style prompts |

Reject and respond change what the loop iterates on next; edit changes the next-iteration state in place. The checkpoint is part of the loop's transition function, not external to it.

## Three placements that earn their cost

Per-iteration checkpoints are almost always the wrong default — they saturate the human at machine speed. Three placements pay back the per-call cost.

### On low confidence

Trip the interrupt only when an in-loop confidence score — a classifier score, a self-reported planning-step uncertainty, or a divergence between two verifier models — falls below a configured threshold. The loop handles most turns autonomously; the human sees only the ones flagged as uncertain. This fails when "confidence" reduces to vibes: the checkpoint then fires on every turn and you have rebuilt per-iteration HITL.

### On budget threshold

Trip the interrupt when the loop has spent a configurable fraction of its token, dollar, or tool-call budget without converging — the [example](#example) below trips at 80% of budget. This is the dual of the [Goal-Driven Autonomous Loop](goal-driven-autonomous-loop.md) budget-limit template — the loop's `budget_limit.md` injection wakes the human instead of winding the agent down.

Budget-threshold checkpoints earn their cost on long-running autonomous loops where the failure mode is silent overspend. They fail on short loops where the budget is per-task — the interrupt fires too often.

### On irreversible action

Trip the interrupt before any action the loop cannot undo from its own state — merging a PR, publishing content, deploying to production, calling an external paid API. This overlaps with the workflow-level [Human-in-the-Loop Placement](../workflows/human-in-the-loop.md) reversibility frame; the loop-control angle is that the checkpoint also exposes the four decision verbs, so a rejected merge can become an edited merge message rather than just a stop.

## Why it works

The mechanism rides on the loop's existing state. LangGraph's persistence layer writes the exact node state at the interrupt point, the `thread_id` acts as a cursor for resumption, and the resume value substitutes back into the `interrupt()` call without re-running upstream nodes ([LangChain — Making it easier to build human-in-the-loop agents with interrupt](https://www.langchain.com/blog/making-it-easier-to-build-human-in-the-loop-agents-with-interrupt)). HITL is one consumer of the same checkpointer that powers fault tolerance and time travel.

The four verbs work as loop control because the resume value feeds back into the node's executing logic. Edit mutates the next call's arguments; reject substitutes a rejection message into the tool-result slot so the model re-plans; respond synthesizes a tool result the agent treats as ground truth. Each verb changes the loop's trajectory, not just its permission state. Anthropic's framing fits the same shape: agents "can pause for human feedback at checkpoints or when encountering blockers" ([Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)).

The per-call interrupt cost is the state-snapshot write plus the wait latency; both compress to near-zero on resume. The human-side cost — context-switch recovery — does not compress, which is why the three placements above are sparse by design.

## When this backfires

The mechanism is sound. The placement is where this goes wrong, and four conditions produce loops that look HITL-controlled but cost more than they save.

- Per-iteration checkpoints in high-throughput loops. When the loop fires tens of actions per minute and every one trips a checkpoint, reviewers approve by reflex within hours. The gate exists in the diagram but not in practice — the [HITL Placement page](../workflows/human-in-the-loop.md) catalogs this as rubber-stamping under load, and it shows up the same way inside a loop. Mitigation: raise the confidence threshold or move to an on-the-loop monitoring posture.
- Checkpoints where an automated verifier already exists. If a test, lint, schema check, or [convergence detector](convergence-detection.md) can grade the step mechanically, an HITL checkpoint is theatre — the verifier is already the stop condition and the human adds latency without signal. Push the gate to a deterministic in-loop check and reserve human checkpoints for the cases the verifier cannot decide.
- Indefinite suspends on autonomous loops. `interrupt()` waits forever by design. A loop that fires a checkpoint at 2am holds state until someone resumes it, costing storage and producing nothing. On overnight or weekend runs this is a multi-hour throughput loss disguised as a safety win. Mitigation: pair every interrupt with a timeout that picks a documented default (abort, escalate, or apply a conservative auto-decision) so the loop continues without a human.
- Reaching for HITL because the stop condition is under-specified. If the only way the loop converges is by waking a person, the loop is not engineered; it is a turn-by-turn workflow with extra steps. Push the missing predicate into the verifier where you can. HITL checkpoints should be the residual that remains after the deterministic gates handle what they can. Empirical baselines reinforce the limit: 45.1% of merged Claude Code PRs still required human revision ([Watanabe et al., arXiv:2509.14745](https://arxiv.org/abs/2509.14745)), and at that rate per-action gating would saturate any reviewer before it saved time.

The opposite framing is sometimes the right call: solve loop control deterministically and place HITL only at the loop boundary — the [HITL Placement](../workflows/human-in-the-loop.md) reversibility frame is exactly that posture, and it is cheaper for most agent loops than internal checkpoints. The angle on this page is the residual — the cases where the loop's in-flight decisions genuinely need a human verb and the four-decision-type mechanism is the way to deliver one.

## Example

A goal-driven autonomous loop refactoring a service has a 200K-token budget and a CI verifier. Two checkpoints earn their cost:

```python
# Pre-call middleware: budget-threshold checkpoint
def budget_threshold_check(state: AgentState) -> AgentState:
    if state.tokens_used > 0.8 * state.budget and not state.warned:
        decision = interrupt({
            "reason": "80% budget consumed without convergence",
            "remaining": state.budget - state.tokens_used,
            "options": ["extend", "narrow-scope", "abort"],
        })
        state.warned = True
        if decision == "abort":
            state.terminate = True
        elif decision == "extend":
            state.budget *= 1.5
        elif decision == "narrow-scope":
            state.messages.append(narrow_scope_prompt())
    return state

# Pre-action middleware: irreversible-action checkpoint
def merge_checkpoint(tool_call) -> ToolCall | None:
    if tool_call.name == "merge_pr":
        decision = interrupt({
            "action": "merge_pr",
            "args": tool_call.args,
            "ci_status": fetch_ci_status(tool_call.args["pr"]),
        })
        # The four verbs in action:
        if decision.type == "approve": return tool_call
        if decision.type == "edit":    return tool_call.with_args(decision.args)
        if decision.type == "reject":  return None  # model re-plans
        if decision.type == "respond": return synthetic_result(decision.message)
```

Per-iteration HITL is absent by design. The convergence loop runs autonomously; the human is woken only on the two pre-declared trip conditions. The reject path on the merge checkpoint is what makes this loop control rather than just a gate — a rejected merge feeds back into the model as a tool result, and the loop re-plans the next iteration.

## Key Takeaways

- A loop-internal HITL checkpoint is a control primitive, not a wrapper: the human's response substitutes back into the node and changes what the next iteration does.
- Four decision verbs — `approve`, `edit`, `reject`, `respond` — map to loop-control actions: continue, redirect-with-new-state, abort-and-replan, substitute-tool-result.
- Three placements earn their cost: on low confidence (with a meaningful score), on budget threshold (on long-running loops with external caps), and on irreversible action (overlapping with the workflow-level reversibility frame).
- Per-iteration checkpoints are the failure mode; they rubber-stamp under load and saturate the human at machine speed.
- Pair every `interrupt()` with a timeout default; an unbounded wait is a throughput loss disguised as a safety win.

## Related

- [Human-in-the-Loop Placement: Where and How to Supervise](../workflows/human-in-the-loop.md) — the workflow-boundary framing of HITL; this page is its loop-internal counterpart
- [Agent Loop Middleware — Safety Nets and Message Injection](agent-loop-middleware.md) — the pre-call injection mechanism is the substrate for resuming a checkpointed loop with human input
- [Goal-Driven Autonomous Loop with Budget Cap](goal-driven-autonomous-loop.md) — the budget-threshold placement is the dual of this loop's `budget_limit.md` injection
- [Convergence Detection in Iterative Agent Refinement](convergence-detection.md) — the in-loop verifier that should handle the cases an HITL checkpoint must not
- [Agent Loop Go/No-Go: When Looping Earns Its Cost](agent-loop-go-no-go-gate.md) — the upstream gate; HITL-controlled loops still have to pass the four conditions before they exist at all
