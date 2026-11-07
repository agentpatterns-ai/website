---
title: "Journal Tool Intent Beside Observed Effects"
description: "Record an agent's declared purpose alongside harness-observed changes. Separate human-readable disclosure from mechanical contradiction and prevention."
tags:
  - security
  - arxiv
  - agent-design
  - testing-verification
  - tool-agnostic
last_reviewed: 2026-11-06
maturity: emerging
---

# Journal Tool Intent Beside Observed Effects

> Journal tool intent as a claim, then store independently observed effects beside it for review.

EPISTEME requires a shell-call type and reason before execution. Its harness records workspace changes, output, and findings outside the agent's writable workspace. File tools require a reason but receive fixed types. The prototype confines effects with a workspace sandbox and disables networking ([paper, v1](https://arxiv.org/html/2611.06563v1)).

## Interpret exposure separately from detection

On 206 ImpossibleBench tasks per model, Qwen3-235B-A22B and Mistral Large 3 completed 400 of 412 runs; 12 stopped for errors or timeouts. Among 49 runs classified as reward hacking, journals exposed 44. Human raters found disclosure in all 44; mechanical contradictions appeared in only three, overlapping that group. Five remained hidden. Excluding four potentially legitimate test repairs gives 40/45 exposed ([results](https://arxiv.org/html/2611.06563v1)).

The experiment used monitor mode. It does not show that reasons prevent cheating. Post-execution contradictions cannot prevent the effects they describe. Guardrail mode adds a pre-execution command-text check, but that was not the tested mode. Fixed file-tool types also left implementation exploits without type contradictions ([design and evaluation](https://arxiv.org/html/2611.06563v1)).

## Design an auditable record

The following application contract is a recommendation, not an evaluated EPISTEME extension. Give each journal entry three separate fields:

| Field | Producer | Review question |
|---|---|---|
| Declared purpose | Agent | What did it say this action would accomplish? |
| Observed effects | Harness | Which files, references, or external resources changed? |
| Findings | Checker or reviewer | Which rule or task requirement does the evidence violate? |

The paper reports a reason that explicitly proposed a hardcoded lookup table to pass unit tests. It also reports shell edits whose effects contradicted read-only declarations ([observed cases](https://arxiv.org/html/2611.06563v1)). These require different review: compare the first patch with the task specification; compare the second declaration with the recorded diff.

Protect the observation store from the agent. Extend collection to every enabled write surface before claiming complete coverage: workspace hashes alone cannot establish what happened to a remote service. Record collection failures explicitly so missing evidence cannot look like an unchanged workspace.

## Evaluate the journal's limits

Use controlled tasks with known acceptable changes and known forbidden effects. Score human disclosure review separately from automated findings. Include legitimate test repairs to measure false alarms, and direct file edits to test coverage beyond shell commands.

Keep authorization checks before execution. Use the journal afterward to decide whether to accept, investigate, or revert the result. If measuring whether declarations reduce misconduct, compare against a matched harness without them; an exposure rate among observed failures answers a different question.

## Key Takeaways

- Self-reported intent is a reviewable claim, not proof of honesty.
- The reported 44/49 exposure includes human interpretation of reasons.
- Bound effect coverage to the surfaces the harness actually observes.

## Related

- [Explanation-Bound Tool Execution](explanation-bound-tool-execution.md) — validate claims before dispatch
- [Pre-Execution Command Risk Classification](pre-execution-command-risk-classification.md) — classify proposed commands
- [Trajectory as Monitoring Unit](../observability/trajectory-as-monitoring-unit.md) — inspect behavior across calls
