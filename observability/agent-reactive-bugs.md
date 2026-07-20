---
title: "Agent-Reactive Bugs at the Model-Harness Boundary"
description: "A failure class that surfaces only when a specific model output meets harness code that mishandles it — found in paired model-and-harness traces."
term: "Agent-Reactive Bug"
tags:
  - observability
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - model-harness boundary bug
  - agent-reactive boundary failure
maturity: emerging
last_reviewed: 2026-07-20
---

# Agent-Reactive Bugs at the Model-Harness Boundary

> Agent-reactive bugs surface only when a specific model output meets harness code that mishandles it — reading either component alone never explains them.

An agent-reactive (AR) bug is a failure that appears only when the model emits a particular output and the surrounding harness code handles that output badly. The model output looks syntactically fine on its own, and the harness code has no defect on well-formed input, so inspecting either side in isolation never reveals the fault. The first empirical study of the class found 255 confirmed AR bugs across Codex, Gemini-CLI, LangChain, and CrewAI — about 8.4% of actively-discussed issues in those projects ([Chen et al., 2026](https://arxiv.org/abs/2607.15684)).

The practical consequence: when you triage an agent failure, the useful unit of evidence is the paired trace — the model output next to the harness reaction it provoked — not the model or the harness examined alone.

## Where the boundary sits

Three harness responsibilities parse and act on model output, and each is a place an AR bug can form ([Chen et al., 2026](https://arxiv.org/abs/2607.15684)):

- Output parsing turns the model's text into a structured action. A model that emits a different conversational format than the parser expects breaks here.
- Loop driving decides what to do with each action and when to stop. A model that repeats a failed action drives the loop into a retry cycle.
- Context management compacts or truncates history. Auto-compaction that drops prior edits makes the model act as if the session just started.

## How to recognize one

The study groups AR bugs by symptom and by the model behavior that triggers them. Silent errors dominate the symptoms: 108 of 255 (42%) produce fluent, plausible, wrong output with no exception or warning. Crashes account for 71 (28%), raw error-in-output for 34, retry loops for 33, and hangs for 9 ([Chen et al., 2026](https://arxiv.org/abs/2607.15684)).

The triggers are model-side but the failure is harness-side. The most common are task-instruction non-compliance (67 cases), unexpected tool arguments (62), and message-template conflict (49), followed by immature harness interfaces, statement fabrication, empty responses, context overflow, and tool hallucination ([Chen et al., 2026](https://arxiv.org/abs/2607.15684)). Instruction non-compliance and statement fabrication surface as silent errors more than 80% of the time, which is why they are the hardest to catch.

## The diagnostic move

Read the trace from both sides at once. For a silent error, compare what the agent claims it did against the tool-call log and the workspace diff — the mismatch is the bug, and it is invisible in the narration alone ([Chen et al., 2026](https://arxiv.org/abs/2607.15684)). Because the trigger is stochastically generated, capture the exact output that provoked the failure and replay it as a fixed mock, rather than trying to regenerate it from the live model ([Chen et al., 2026](https://arxiv.org/abs/2607.15684)).

## Why it works

Harness code is written against an implicit contract about model output: a well-typed tool argument, a recognizable action marker, a bounded context length. A stochastic model periodically violates that contract in a way the harness never guarded against, and the interaction — not any single line — is the defect. Paired traces localize it because they show the contract and its violation side by side. Independent work that repairs harness flaws from failed trajectories reaches the same conclusion: the fault lives in the interaction, and the failed trace is where you find it ([harness-flaw repair study, 2026](https://arxiv.org/abs/2606.06324)).

## When this backfires

The boundary framing is not free, and it does not always change who fixes the bug:

- Loud crashes with a clean stack trace, 28% of the sample, are already localized by one-sided harness inspection. The paired-trace step adds overhead without new information.
- Single-tool or deterministic-output agents give the model little contract to violate, so AR bugs are rare and standing up trace capture is not repaid.
- Prototypes without trace infrastructure have no paired trace to read. The cost of instrumenting a throwaway agent exceeds the value.
- Some triggers are genuinely model-side. For statement fabrication and instruction non-compliance, harness guards paper over the symptom; the study found developers routed these to model improvement instead, and user-versus-developer fix mismatches clustered on exactly these categories ([Chen et al., 2026](https://arxiv.org/abs/2607.15684)).

## Example

CrewAI issue 668 is a minimal AR bug ([Chen et al., 2026](https://arxiv.org/abs/2607.15684)). The model invokes a valid tool but omits one argument. The harness binds the missing argument to `None` and passes it on. The tool then calls `.startswith` on that value and raises `AttributeError`.

One-sided inspection fails twice. The model output is a well-formed tool call, so blaming the model finds nothing wrong. The tool code is correct for any real string argument, so blaming the harness finds nothing wrong. The paired trace shows both facts at once — model omitted the argument, harness bound `None` without validating it — and points straight at the fix the study records as the most common accepted mitigation: validate tool arguments before execution ([Chen et al., 2026](https://arxiv.org/abs/2607.15684)).

## Key Takeaways

- Agent-reactive bugs need a specific model output and inadequate harness handling together. Neither component is buggy in isolation, so single-side triage never localizes them.
- Silent errors are the dominant and hardest symptom, at 42% of cases. Detect them by comparing the agent's claimed actions against the tool-call log and workspace state, not by reading its narration.
- Capture and replay the triggering output as a fixed mock. The trigger is stochastic, so a live rerun may not reproduce the failure.
- The boundary framing pays off on silent errors and interaction faults, not on loud crashes, single-tool agents, or bugs whose real cause is model-side.

## Related

- [Harness Bug Detection Patterns](harness-bug-postmortem-patterns.md) — the complementary view: detection gaps in eval suites, where this page covers the interaction-class taxonomy and diagnosis
- [Agent Debugging](agent-debugging.md) — the general process this technique specializes for boundary failures
- [Trajectory Pre-Filter for Failure Diagnosis (TrajAudit)](trajectory-prefilter-failure-diagnosis.md) — concentrating attention on failure-relevant spans in a long trace
- [Offline Trajectory Replay for Multi-Agent Debugging](offline-trajectory-replay-multi-agent-debugging.md) — replaying captured trajectories, the mechanism behind mock-based AR reproduction
- [Circuit Breakers for Agent Loops](circuit-breakers.md) — halting the retry-loop symptom before it exhausts budget
