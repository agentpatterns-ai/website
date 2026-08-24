---
title: "Task Completion as Tool Certification (Silent Tool Rot)"
term: "Silent Tool Rot"
description: "In-session task success does not certify a reusable agent-built tool — it can pass its one verification input and still return wrong answers on every new input while raising no error."
tags:
  - anti-pattern
  - agent-design
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - verification-conformance gap
  - silent tool rot
  - conformance gap in tool-evolving agents
last_reviewed: 2026-07-07
maturity: emerging
---

# Task Completion as Tool Certification (Silent Tool Rot)

> In-session task success does not certify an agent-built tool — it can pass its one verification input and still return wrong answers on new ones.

An agent that synthesizes its own tools ships two artifacts per answer: the answer, and a reusable script later tasks compose and depend on. Task completion certifies the answer, not the script. Treating a green in-session run as a passing grade is the mistake: the tool can execute cleanly and still be wrong on every input it did not see during creation.

A pilot preserved each synthesized tool's source and replayed it against a held-out conformance suite. Across 222 tools from three tool-creating protocols on Claude Haiku 4.5, [96.8% recorded per-tool correctness of zero](https://arxiv.org/abs/2604.00392v2): two protocols failed 100% of their tools, one failed 91.7%. Session-level task completion was highest for the protocol whose tools all scored zero, so the gap is invisible to pass-rate dashboards. Hand-written reference implementations scored perfectly on all 16 suites, ruling out a mis-calibrated test ([Kaliyev & Maryanskyy, 2026](https://arxiv.org/abs/2604.00392v2)).

## Why the false signal is convincing

Synthesized tools overfit to their single in-session verification point. The task verifier scores only the one call the task needed — an input within the regime the tool was just fit to — so an overfit tool passes it, while the conformance suite draws from the capability's full contract the tool never saw ([Kaliyev & Maryanskyy, 2026](https://arxiv.org/abs/2604.00392)). The tool learns the shape of one example rather than the capability, then executes without error on unseen inputs and returns a wrong answer (median robustness 0.52 to 0.54). The failure raises no exception, so nothing in the run distinguishes a correct tool from a rotted one. This is the tool-level case of the general rule that [a clean run status is not evidence the task succeeded](run-status-vs-task-status-confusion.md).

## What to emit instead

Preserve each tool's source and replay reusable ones against a held-out conformance suite before trusting them. The paper's audit layer costs millisecond-scale latency and bounded disk I/O, cheap enough to leave on in production, and surfaces three signals between releases ([Kaliyev & Maryanskyy, 2026](https://arxiv.org/abs/2604.00392)):

- Silent Rot: session task completion stays high while held-out conformance for a reused capability drops.
- Reuse Trap: raw reuse of a tool rises but its correct-reuse rate falls, marking an emerging defective dependency.
- Regression Delta: a regression-role task fails after the same capability passed its gap-role task, naming which release broke it.

## When this framing does not apply

The gap only bites once a tool is reused, duplicated, or made load-bearing, so the mitigation is not always worth its cost:

- Strictly ephemeral tools. A tool used once on the same input regime and discarded at session end never reaches reuse; a 10-to-22-probe suite per throwaway script will not repay itself.
- Larger models may narrow the gap. The 96.8% figure is Haiku-4.5 scale; the authors note held-out correctness at Sonnet or larger could change the rates, so treating it as model-independent over-claims ([Kaliyev & Maryanskyy, 2026](https://arxiv.org/abs/2604.00392v2)).
- A reference suite already exists. A tool fit against a supplied test suite is no longer verified against a single input, and the gap shrinks.

## Example

Before — completion treated as the tool's grade: an agent building a date-range parser writes it, the current task passes `2026-01-01..2026-01-31`, the verifier is green, and the tool is kept for reuse. It was fit to one ISO range; on `Q1 2026` or an open-ended range it returns a plausible-looking wrong span and raises no error. The next task that composes it inherits the defect silently.

After — the tool is scored against its contract: the harness preserves the tool's source and replays it against a held-out conformance suite of hidden and adversarial inputs before the tool is trusted for reuse. A per-tool correctness below the threshold flags the tool as rotted, and the reuse decomposition shows correct-reuse falling as raw reuse climbs, so the defect surfaces before a later task depends on it ([Kaliyev & Maryanskyy, 2026](https://arxiv.org/abs/2604.00392)).

## Key takeaways

- A green in-session run says the tool handled one input, not that it implements the capability; task completion and tool correctness are different measurements.
- The failure is silent — rotted tools execute cleanly and return wrong answers, so pass-rate dashboards never show it.
- Verify reusable synthesized tools against held-out conformance inputs, and watch the Silent Rot, Reuse Trap, and Regression Delta signals between releases.
- Skip the overhead for strictly ephemeral single-use tools; spend it where a tool becomes a reused, load-bearing dependency.

## Related

- [Judging Agent Safety by Task Completion (Action-Boundary Violations)](judging-agent-safety-by-task-completion.md) — the sibling failure where completion overstates safety rather than tool correctness.
- [Runtime Scaffold Evolution: Agents That Build Tools](../agent-design/runtime-scaffold-evolution.md) — the pattern this page qualifies: agent-built tools are useful, but reused ones need conformance verification.
- [The Test Homogenization Trap](test-homogenization-trap.md) — the adjacent case where the tests share the model's blind spots rather than the tool overfitting its one input.
- [Run-Status vs Task-Status Confusion in Autonomous Agent Runs](run-status-vs-task-status-confusion.md) — the general rule that a clean exit is not evidence of a correct outcome.
- [Premature Completion: Agents That Declare Success Too Early](premature-completion.md) — the related failure where the completion signal itself fires too early.
