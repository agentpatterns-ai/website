---
title: "Agent Failure Trajectories and the Recovery Window"
term: "Recovery Window"
description: "Treat a coding agent's failure as a trajectory with an onset, an evolution, and a narrow recovery window — intervene before lock-in, not at the final error."
tags:
  - agent-design
  - tool-agnostic
  - observability
  - arxiv
  - reliability
aliases:
  - failure trajectory analysis
  - agent failure lock-in
  - agent recovery window
last_reviewed: 2026-07-13
maturity: emerging
---

# Agent Failure Trajectories and the Recovery Window

> A coding agent's failure unfolds as a trajectory — onset, evolution, a narrow recovery window — so intervene before lock-in, not at the final error.

A coding agent's failure is a process, not a single end-state error. It runs through three phases: an onset (the decisive wrong step), an evolution (later steps that build on that step), and a recovery window (the short span in which a correction is still possible before the run locks in). Final-outcome evaluation only sees the wreckage; the value is upstream, in the window before every action extends rather than corrects the error ([Zhao et al., 2026](https://arxiv.org/abs/2607.09510)).

The condition that governs this technique: the recovery window is narrow and failure signals lag the decisive error, so the payoff comes from validating early — checking the agent's premises before it acts — and from giving any monitor the task specification, not from naive late-stage detection.

## The three phases

A study of 1,794 valid CLI coding-agent trajectories (filtered from 3,843 runs across seven frontier models, with over 63,000 annotated steps) measured the shape of failure directly ([Zhao et al., 2026](https://arxiv.org/abs/2607.09510)):

- Onset is early. The decisive error has a median onset of 7 execution steps, inside the first quarter of a failed run (median length 27 steps).
- Signals lag. Observable failure symptoms emerge a median of about 10 steps after the decisive error — the first visible failure lands near step 16. The run looks healthy while it is already diverging.
- The recovery window is short. The median gap between the decisive error and lock-in is one step. Still, 60.9% of failed runs leave at least one recovery step and 43.9% leave three or more.

After lock-in, agents rarely stop: only 18% terminate, while 82% continue unproductively, and repairing the wrong problem accounts for 39% of wasted execution.

## Why it works

Failures become unrecoverable through error propagation. The dominant failure class is epistemic: the agent misuses information it already has (57.9% of errors), and the single largest type is a false premise (30.7%). The agent adopts an unverified assumption — reading `sudo: not found` as a permissions problem rather than a missing program — then reasons consistently on top of it ([Zhao et al., 2026](https://arxiv.org/abs/2607.09510)). Because each later step is taken to be coherent with that premise, every subsequent action extends rather than corrects the error. The wrong foundation is laid early and symptoms surface late, so validation has to move earlier than final-outcome checks to catch it in time. Responding to a signal is what separates outcomes: 92% of successful trajectories act on at least one error signal, against only 37% of failed ones.

Independent trajectory analysis corroborates the early-signal finding — a coding agent's opening strategy, reading first versus patching first, is observable within the first 10 steps and correlates with the final outcome across agents ([behavioral drivers of coding-agent success](behavioral-drivers-agent-success.md)).

## When this backfires

- No specification at monitoring time. The dominant spec-relative failures (false premise, specification neglect) are only 12 to 15% detectable without the task requirements, rising to 22 to 32% when they are supplied ([Zhao et al., 2026](https://arxiv.org/abs/2607.09510)). A monitor without the spec mostly cannot catch them, so the process framing buys little.
- Irreversible external side effects. Where actions hit external services — deploys, pushes, API writes — checkpoint-restore cannot undo them. Intervening before lock-in then degrades to aborting, not recovering; pair it with [rollback-first design](rollback-first-design.md).
- Naive real-time detection. The paper's own monitors reach 82% precision on locked-in runs but only 3.7 to 8.7% lead time before lock-in, so a detector reacting to symptoms fires too late. Front-load premise validation instead of trusting live symptom-watching.
- Short or trivial tasks. When failure is immediate and obvious from the final output, the onset-evolution-recovery apparatus adds annotation and monitoring overhead with no gain over a simple completion check.

## Example

A CLI agent runs a build step and sees `sudo: not found`. It adopts the false premise that it lacks permissions and spends the next several steps rewriting commands to avoid `sudo` — an internally consistent but wrong path. The real cause is that `sudo` is not installed in the container. The decisive error was the first step of that detour; the recovery window was the very next step, before the agent committed to the permissions theory. A premise check — confirm this is a permissions error before working around it — would have caught it inside the window. Ten steps later, when the build still fails for unrelated reasons, the run has already locked in ([Zhao et al., 2026](https://arxiv.org/abs/2607.09510)).

## Key Takeaways

- Failure is a trajectory: a decisive error at a median step 7, symptoms about 10 steps later, and a median recovery window of one step before lock-in.
- The dominant cause is epistemic — a false premise the agent then reasons consistently on top of, so the error compounds rather than surfaces.
- Move validation earlier than final-outcome evaluation: verify the agent's premises before it acts, since 92% of successful runs act on an early signal versus 37% of failed ones.
- Give any monitor the task specification, or it catches only 12 to 15% of the failures that matter; without it, prefer prevention and fail-fast termination over late symptom-watching.

## Related

- [Behavioral Drivers of Coding Agent Success and Failure](behavioral-drivers-agent-success.md) — independent trajectory analysis showing early opening-strategy signals predict the outcome
- [Trajectory-Conditioned Model Escalation (SWE-Router)](trajectory-conditioned-model-escalation.md) — reads a partial trajectory to decide when to escalate, an intervention inside the recovery window
- [Exception Handling and Recovery Patterns for AI Coding Agents](exception-handling-recovery-patterns.md) — failing forward versus catastrophically once an error occurs
- [Rollback-First Design](rollback-first-design.md) — making actions reversible so intervention can undo, not just abort
- [Five-Failure-Layers Diagnostic](five-failure-layers-diagnostic.md) — attributing a failure to a harness layer once you have caught it
- [Strained Coherence as a Pre-Failure Signal in Agent Trajectories](../../observability/strained-coherence-pre-failure-signal.md) — a complementary early signal for detecting divergence before lock-in
- [Completion Failure Taxonomy](../../verification/completion-failure-taxonomy.md) — a categorization of why agent output misses, at the completion level
