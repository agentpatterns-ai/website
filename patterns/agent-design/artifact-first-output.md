---
title: "Artifact-First Output: Deliverables in Files, Pointers in Chat"
term: "Artifact-First Output"
description: "The agent writes long deliverables to named files, replies with a short pointer to the file, and yields the turn when a human decision is pending."
tags:
  - agent-design
  - tool-agnostic
aliases:
  - artifact-first delivery
  - path-in-chat reply
last_reviewed: 2026-11-03
maturity: emerging
---

# Artifact-First Output: Deliverables in Files, Pointers in Chat

> Artifact-first output puts every long deliverable in a named file; the chat reply points to it and yields when a decision is pending.

An agent that follows this rule writes drafts, plans, and review reports to files. Its chat reply names the file, adds little else, and stops when the human must decide. The [Elephant-Goldfish Model](../multi-agent/elephant-goldfish-design-review.md) (EGM) design plugin applies the rule in its drafting and review skills. The authors state a reason for the rule, and nothing in the plugin measures its effect.

## How EGM applies the rule

The `egm-draft` skill forbids "large proposals, drafts, summaries, or plans directly in the chat pane". The rule covers "the Discussion Summary, Design Drafts, and all review reports" ([egm-draft](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-draft/SKILL.md#L24-L30)). The files go to the working directory or the host's artifact directory, and you can name another folder ([harnesses.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/harnesses.md#L108-L123)).

Each of the five review stages writes its own named report, such as `critic_report.md`. The "Consolidated report with all review rubrics" option ([presets](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review/SKILL.md#L197-L201)) runs all five stages without pauses. It writes the five reports, adds `consolidated_review_report.md`, and sends only "a concise chat notification" with its path ([egm-review](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review/SKILL.md#L261-L293)). A paused review keeps every report file ([egm-review](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review/SKILL.md#L257-L259)).

The reply shape depends on the step. After each drafted section, the agent states what changed, must "highlight 2–3 key decisions or additions", and gives the path. Only then does it ask its single approval question ([egm-draft](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-draft/SKILL.md#L93-L104)).

A review stage gate carries only the report path and a choice. The shared execution rules ban "Summary of work", "Status", "Adherence", and "Rule checklist" sections "in your final response". The rules say to respond "only with the technical content and next steps" ([execution instructions](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/resources/execution_instructions.md#L26-L28)). So the highlights describe the design, and the ban covers reports on the agent's own process (inference from both rules).

At a checkpoint the agent stops. After `egm-resolve` writes its annotated report, the skill tells the agent to call zero tools and wait ([egm-resolve](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-resolve/SKILL.md#L110-L134)). Findings marked ESCALATE go first in that chat message, because "They need the user's knowledge, not only approval".

## Why EGM chose it

Long specs or review feedback in chat "clutters conversation history, degrades LLM context performance, and creates poor user ergonomics" ([architecture.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/designs/architecture.md#L32-L34)). Its UX protocol states the aim "To maintain conversation health and prevent context degradation" ([architecture.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/designs/architecture.md#L163-L177)). No measurement backs either. The status-section ban has no stated reason.

A file write still passes the full text through the transcript as tool input (inference; upstream does not discuss it). Any saving comes later, when revisions edit the file and the agent does not reprint the whole draft (inference). On the window cost of leftover text, see [the orchestrator's attention budget](orchestrator-attention-budget.md) and [the dumb zone](../../context-engineering/context-window-dumb-zone.md).

## Costs and limits

- The human must open the file. A reader who stays in chat sees only the pointer and any highlights.
- The agent picks the highlights. EGM forbids the agent to rank architecture options ([egm-draft](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-draft/SKILL.md#L63-L71)), yet the highlight list decides what the human reads first (inference).
- Report files pile up. One full review writes at least five, and the upstream guide shows how to keep the folder out of git ([harnesses.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/harnesses.md#L120-L123)).
- Tests cover the files, not the chat. An opt-in live Codex test checks that the brief, draft, and all five stage reports exist and are not trivial ([test_codex.py](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/tests/integration/test_codex.py#L303-L316)). Its prompt pre-approves every gate: "These simulated approvals do not test interactive approval-gate behavior" ([test_codex.py](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/tests/integration/test_codex.py#L273-L276)). The `artifact_first_delivery` scenario asserts only that the reply contains "draft" ([test_scenarios.yaml](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-draft/test_scenarios.yaml#L97-L107)), and no test runs the scenarios ([test_scenario_coverage.py](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/tests/unit/test_scenario_coverage.py#L22-L51)).
- Some protocol items exist only in the design doc. `RequestFeedback: true` and "Queue Clearance" appear in `architecture.md` and in no shipped skill (inference from a repository search). [Issue #271](https://github.com/google/elephant-goldfish-model/issues/271) reports other design-doc drift, not these two items.

The "Interactive breakdown" option in `egm-resolve` still walks through each finding in chat when the human asks ([egm-resolve](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-resolve/SKILL.md#L145-L149)).

## Applying it

- Give each stage a fixed file name, so a paused session can resume from the files.
- Send the path and little else. Add two or three highlights where the human approves a drafted section.
- Leave process reports out of the reply.
- Ask one question and yield when a decision is pending. An uninterrupted run needs only the final path.

## Example

At Stage 6, `egm-review` writes the full reviewer result to `comprehension_report.md`. The chat then shows "Stage 6 (Comprehension Test) completed. Findings written to comprehension_report.md." It offers three choices: go on to Stage 7, pause while the human edits the doc, or save progress and exit ([egm-review](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review/SKILL.md#L334-L346)).

The report holds the reviewer's paraphrase and findings. The chat holds one decision.

## Key Takeaways

- Keep each reply to the file path plus the least the human needs to decide, and yield when a decision is pending.
- Leave status and rule-checklist sections out of replies; they report on the agent, not the work.
- Treat the context benefit as a stated design reason, because EGM has no measurement and the file write still enters the transcript.
- Check the highlight list for steering, since a human who skips the file sees only that list.

## Related

- [Elephant-Goldfish Design Review](../multi-agent/elephant-goldfish-design-review.md) — the full workflow this rule serves
- [Durable Interactive Artifacts](durable-interactive-artifacts.md) — re-runnable interactive objects, where this page covers plain files
- [The Orchestrator's Attention Budget](orchestrator-attention-budget.md) — the context cost of text left in the window
- [Session Recap](session-recap.md) — a fixed-schema artifact written at a context boundary
- [Offload Thresholds by Payload Origin](../../context-engineering/offload-threshold-by-payload-origin.md) — when tool output becomes a file reference
