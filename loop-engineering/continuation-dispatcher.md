---
title: "Continuation Dispatcher: Who Owns the Iterate-or-Stop Call"
term: "Continuation Dispatcher"
description: "Put the iterate-or-stop decision in one named predicate that reads declared signals and returns a stop reason, in loops where the harness owns continuation."
tags:
  - loop-engineering
  - agent-design
  - pattern
  - tool-agnostic
aliases:
  - loop continuation dispatcher
  - should_continue predicate
  - iterate-or-stop decision point
last_reviewed: 2026-08-15
maturity: emerging
---

# Continuation Dispatcher: Who Owns the Iterate-or-Stop Call

> Put the iterate-or-stop decision in one named predicate, but only when the harness owns continuation rather than the model.

A continuation dispatcher is a single named function that owns whether a loop runs another pass. It reads a declared set of signals, returns a stop reason instead of a boolean, and is the only place in the loop where that decision is made. Angela Shi states the rule directly in a worked retrieval pipeline: "The LLM can contribute signal to the iteration decision but the decision to iterate or stop must be in code, with explicit rules" ([Shi, 2026](https://towardsdatascience.com/rag-workflow-and-loop-engineering-the-dispatcher-that-decides-when-to-loop-and-when-to-stop/)).

"Continuation dispatcher" is this site's name for that function. It is not Shi's: in her pipeline the dispatcher routes patterns and a separate `should_continue` owns the loop decision, and she is explicit that "the dispatcher decides only which patterns to fire upfront, not whether to loop". Read every use of the term here as naming her `should_continue`, not her dispatcher.

That rule is a position on one design axis, not a universal one.

## Decide who owns continuation first

Anthropic splits agentic systems on exactly this line. "Workflows are systems where LLMs and tools are orchestrated through predefined code paths," whereas "Agents, on the other hand, are systems where LLMs dynamically direct their own processes and tool usage, maintaining control over how they accomplish tasks" ([Anthropic — Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)). Putting continuation in code is what choosing the workflow side means in practice.

In an agent-shaped loop the model already owns the call. The Claude Agent SDK runs until "Claude produces output with no tool calls, at which point the loop ends and the final result is delivered." Its code-side caps report as `error_max_turns` and `error_max_budget_usd`, which are failure subtypes rather than the designed stop ([Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/agent-loop)). A predicate that overrides the model's own stop signal converts ordinary completions into errors.

Build a dispatcher when the loop has a fixed set of moves, when the same input must follow the same path twice, or when someone has to read back why iteration ended. Otherwise let the model stop and keep the caps as [runaway guardrails](loop-budgeting.md).

## What the dispatcher may read

Declared inputs are what separate a dispatcher from a stop condition scattered through the loop body. Shi's reads three signals in priority order (candidate stability, keyword stability, and falling confidence), glossed as "nothing new will be found", "the LLM is repeating itself", and "the loop is making things worse", with a failsafe above it in the orchestrator, which budgets across several loops at once: "Two to three iterations cover the vast majority of cases; the composite's hard cap is four, because several loops can fire on one question and each needs its own pass" ([Shi, 2026](https://towardsdatascience.com/rag-workflow-and-loop-engineering-the-dispatcher-that-decides-when-to-loop-and-when-to-stop/)).

That construction generalizes past retrieval. Shrivastava's halt cascade has the same four levels: critic approval, then semantic convergence between consecutive drafts, then a quality plateau, then a hard cap as failsafe ([Shrivastava, 2026](https://arxiv.org/abs/2606.27009v1)).

Keep every signal cheap relative to an iteration. Consulting a judge each round to feed the decision produced "the most expensive policy—+129% tokens", while "judge-free entropy_only cuts 38% of operational tokens versus max_iterations at statistically indistinguishable quality (ΔIS=−0.004, p=0.81)" on HotpotQA ([Shrivastava, 2026](https://arxiv.org/abs/2606.27009v1)).

## Return a reason, not a boolean

A caller that cannot tell "converged" from "hit the cap" cannot decide whether to resume. The Claude Agent SDK makes that the contract rather than a convention: `ResultMessage.subtype` is "the primary way to check termination state", separating `success` from `error_max_turns`, `error_max_budget_usd`, and `error_during_execution` ([Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/agent-loop)). A predicate returning `bool` discards that distinction at the one point where keeping it is free.

## Why it works

The mechanism is decision locality. Explicit rules do not stop more accurately than a model, and the evidence below says they often stop worse. What a single named predicate buys is a decision with a test surface: a pure function of declared state can be unit-tested without running the loop, logged on every pass, and diffed when someone changes a threshold.

Shi names the payoff and the reason it matters. Under model-directed routing "the same question on the same document can take different paths on different runs. For audit, compliance, legal review, this is disqualifying," which is why the design also requires that "Every iteration must produce an `IterationRecord`" ([Shi, 2026](https://towardsdatascience.com/rag-workflow-and-loop-engineering-the-dispatcher-that-decides-when-to-loop-and-when-to-stop/)). Reproducibility is a property of where the decision lives, not of how good the decision is.

## When this backfires

- The loop is agent-shaped. When the model directs its own tool use, a code predicate fires mid-task and the harness records it as a failure, not a stop ([Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/agent-loop)).
- The constants were copied rather than calibrated. A cap of four is a fact about one pipeline. The length gap between failed and successful runs alone spans 12.6% to 82.5% across code agents ([Majgaonkar et al., 2025](https://arxiv.org/abs/2511.00197v1)), so a borrowed dispatcher stops the wrong runs with full determinism.
- A fixed cap is doing the real work. A loop that "runs a fixed number of rounds and then returns whatever it last produced" wastes tokens on easy inputs and truncates hard ones ([Shrivastava, 2026](https://arxiv.org/abs/2606.27009v1)). Determinism does not repair a cap that was never right.
- You need failure prediction rather than stop detection. Linear probes on internal activations "predict eventual task failure from the first interaction round, substantially earlier than agent-monitoring methods based only on observable behavior", and "adding behavioral features to hidden-state probes provides no further gain" ([Ruan et al., 2026](https://arxiv.org/abs/2607.06503v2)). A predicate over observable loop state has a ceiling here.
- Choosing the round matters more than choosing the moment. An oracle round-selector beat every practical stopping policy by 0.115 Information Score, which "reframes the problem from 'when to stop' (easy) to 'which round is best' (open)" ([Shrivastava, 2026](https://arxiv.org/abs/2606.27009v1)). A dispatcher solves the easy half.
- The loop runs a handful of times. Naming, typing, logging, and testing the predicate is fixed cost, and the [go/no-go gate](agent-loop-go-no-go-gate.md) already rejects loops at that cadence.

## Example

Shi's dispatcher is a plain predicate carrying its stop reasons in the docstring, so the rules read without tracing the loop:

```python
def should_continue(history: list, current: _ResultProto,
                    confidence_drop_threshold: float = 0.1) -> bool:
    """Decide whether the iteration loop should run another pass.

    Three reasons to stop, in order of priority:
      1. Candidates are stable (same set as last pass)
      2. Suggested keywords are stable
      3. Confidence is decreasing past the threshold
    """
```

Source: [Shi, 2026](https://towardsdatascience.com/rag-workflow-and-loop-engineering-the-dispatcher-that-decides-when-to-loop-and-when-to-stop/).

Two changes carry it into a general harness. Return an enum of stop reasons instead of `bool`, so a caller can resume on `hit_cap` and archive on `converged`. Then calibrate both `confidence_drop_threshold` and the cap against recorded runs from your own harness, because neither number transfers ([Majgaonkar et al., 2025](https://arxiv.org/abs/2511.00197v1)).

Microsoft ships the hybrid in VS Code, and its release notes describe the division plainly: "Instead of relying on fixed rules, a small utility model reads a transcript of the chat and decides whether the task is done," while "To keep things bounded, Autopilot loops a maximum of three times before it stops" ([VS Code 1.124 release notes](https://code.visualstudio.com/updates/v1_124)). The model judges; the code caps.

## Key Takeaways

- The dispatcher pattern presumes the harness owns continuation. On Anthropic's workflow-versus-agent axis that is the workflow side, and agent-shaped loops stop on the model's own signal instead.
- Declared inputs, rather than better inputs, are the point. Three cheap signals plus a failsafe cap is the shape that recurs from retrieval pipelines to research halt cascades.
- Return a stop reason. `converged`, `hit_cap`, and `regressing` are different instructions to the caller, and a boolean erases all three.
- Auditability is the honest payoff. Explicit rules buy reproducible paths and readable iteration records, not more accurate stopping.
- Calibrate every constant against your own runs, and expect the dispatcher to solve the tractable half of the problem while round selection stays open.

## Related

- [Convergence Detection in Iterative Agent Refinement](convergence-detection.md) — the signals a dispatcher reads when the goal is diminishing returns rather than a hard cap
- [Loop Budgeting: Allocating Iteration and Token Budget Across Turns](loop-budgeting.md) — choosing the cap primitive that sits behind the dispatcher as failsafe
- [Calibrated Early Termination and Warm Restart for Agent Runs (FailFast-RestartSmart)](early-termination-and-warm-restart.md) — predicting a doomed run, the case where an observable-state predicate is the wrong instrument
- [Agent Loop Go/No-Go: When Looping Earns Its Cost](agent-loop-go-no-go-gate.md) — the upstream gate that decides whether a loop should exist at all
- [Agent Loop Middleware — Safety Nets and Message Injection](agent-loop-middleware.md) — the other deterministic component wrapped around a probabilistic loop
- [Stuck-Loop Recovery: Detecting and Escaping Non-Converging Agent Loops](stuck-loop-recovery.md) — what the harness does when the dispatcher reports the loop is making things worse
