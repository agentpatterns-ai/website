---
title: "Failed Reviewer Is Not a Clean Pass: Per-Agent Status in Fan-Out Review"
term: "Not-Run Reviewer Status"
description: "Record a failed or silent reviewer as not run, retry it once, and let it block a clean round instead of counting as zero findings."
tags:
  - multi-agent
  - tool-agnostic
aliases:
  - failed reviewer recorded as not run
  - per-reviewer status in fan-out review
last_reviewed: 2026-11-03
maturity: emerging
---

# Failed Reviewer Is Not a Clean Pass: Per-Agent Status in Fan-Out Review

> Record a reviewer that fails or returns nothing as not run, retry it once, and let any not-run reviewer block a clean round.

An empty merged findings list has two causes. Every reviewer read the target and found nothing, or a reviewer never reported. An aggregator that collects only findings cannot tell them apart. The [Elephant-Goldfish Model](elephant-goldfish-design-review.md) (EGM) separates them with a status for each reviewer. Its synthesizer persona says "A reviewer that times out, fails, or returns no report did not review." It adds "Never count it as a reviewer with zero findings" ([synthesizer](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/agents/synthesizer.md#L39-L40)).

## How the status rule works

EGM splits the rule across the synthesizer persona and the review-loop skill:

1. Retry once. A failed reviewer gets one retry, and a second failure sets its status to `not run` ([synthesizer](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/agents/synthesizer.md#L40)).
2. Report a status for every reviewer. The report layout puts a `Reviewer Status` table ahead of the findings, with each reviewer `completed` or `not run` ([report layout](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/agents/synthesizer.md#L49-L53)). The message to the drafting session repeats them ([notify step](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/agents/synthesizer.md#L65)).
3. Treat silence as not run. "If the synthesizer summary has no status for a requested reviewer, record that reviewer as not run" ([egm-review-loop](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review-loop/SKILL.md#L132-L136)).
4. Block the round. A round is clean when no reviewer raises an unsettled Blocker or Major finding. Also, "A reviewer recorded as not run makes the round not clean" ([clean round](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review-loop/SKILL.md#L161-L164)).

The loop converges after two consecutive clean rounds, and at a cap of 5 rounds it asks the user how to proceed ([convergence and cap](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review-loop/SKILL.md#L165-L173)). A not-run reviewer therefore cannot help end the loop (inference from the clean-round rule). The loop skill passes the rule to the synthesizer and requires a status for each reviewer in its summary ([dispatch step](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review-loop/SKILL.md#L113-L119)).

## Why it works

A [PR #168 reviewer](https://github.com/google/elephant-goldfish-model/pull/168#discussion_r4396035855) warned that "the parent-visible summary can look identical to a completed clean round." The author replied by adding the `Reviewer Status` table ([author reply](https://github.com/google/elephant-goldfish-model/pull/168#discussion_r4396530381)). The reviewer approved the fix and noted that "A live failed-reviewer run was not replayed" ([approval](https://github.com/google/elephant-goldfish-model/pull/168#pullrequestreview-5679858420)).

Without a per-reviewer status, two apparently clean rounds could end the loop despite a silent reviewer (inference). Hook enforcement has the same blind spot ([Zero Violations Is Not Evidence Your Hook Works](../../verification/enforcement-liveness-evidence.md)).

## Stop the reviewer on a denied read

A reviewer that returns a verdict without reading its inputs needs a rule on its own side. Each Claude Code reviewer adapter ends with "If a required file cannot be read, report an incomplete review instead of a verdict" ([comprehension adapter](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/.claude-plugin/agents/comprehension.md#L16-L17)). The packaging design says "A denied read must stop the affected reviewer without a fabricated verdict" ([runtime_packaging.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/designs/runtime_packaging.md#L68-L70)). The Codex guide calls a missing read "an incomplete review, not a clean result" ([codex.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/codex.md#L53-L56)).

The synthesizer's not-run rule names a timeout, a failure, or no report. An incomplete review is a report, and no file at `36343a1` maps it to `not run` (reading of the [synthesizer rule](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/agents/synthesizer.md#L40)). If you adopt the pattern, map an incomplete review to `not run` in the aggregator.

## Two failure policies in one plugin

EGM's documentation generator takes the opposite line. When a bootstrap scout fails or times out, the orchestrator logs a warning, writes the placeholder `"(Details pending/documentation failed)"`, and continues ([egm-bootstrap](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-bootstrap/SKILL.md#L267-L269)).

Upstream does not explain the split. One reading (inference) is that the outputs differ. Without reviewer status, a stop decision can hide a missing input (inference). The bootstrap emits a document, and the placeholder stays in it for a reader to see. Degrade with a visible marker when a human reads the output, and fail closed when the output is a pass or fail. [LLM map-reduce](llm-map-reduce.md) and [bounded batch dispatch](bounded-batch-dispatch.md) take a degrade-and-continue line for bulk work.

## When this backfires

- Each retry adds one reviewer launch to its round.
- A reviewer that fails every time keeps each round from being clean, so the loop cannot converge. Each new round waits for the user to confirm it ([turn boundary](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review-loop/SKILL.md#L175-L179)).
- The rule is prompt text. No Python or JSON file in the plugin at `36343a1` mentions `not run` (inference from a search of the source). The status is as reliable as the model that writes it.
- Upstream reports no data on how often reviewers fail, and no outcomes with or without the rule.

## Example

EGM declares a scenario, `missing_reviewer_status_not_clean`, that gives the loop zero findings and two completed reviewers, although three were requested ([test_scenarios.yaml](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review-loop/test_scenarios.yaml#L43-L53)):

```yaml
  - scenario_id: "missing_reviewer_status_not_clean"
    description: "Verifies a reviewer with no status in the synthesizer summary counts as not run, so a zero-findings round is not clean."
    eval_type: "deterministic"
    system_prompt:
      skill_file: "skills/egm-review-loop/SKILL.md"
    turns:
      - user_input: "The synthesizer summary for round 2 on docs/design.md says: 0 findings; egm-design completed, egm-structural completed. egm-style was also requested. Is round 2 clean?"
        assertions:
          - type: "required_pattern"
            pattern: "(?i)not run"
            message: "A requested reviewer with no status must count as not run, so the round is not clean."
```

The assertion only requires the phrase `not run` in the reply. A reply containing `not run` could still call the round clean and match (inference). No test in the repository runs the scenario against a model (inference from a search of `tests/` and `scripts/`). `test_scenario_coverage.py` checks only that each scenario has its required fields ([coverage test](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/tests/unit/test_scenario_coverage.py#L22-L52)).

## Key Takeaways

- Require a status for every requested reviewer, and treat a missing status as not run.
- Call a round clean only when every requested reviewer completed and no unsettled Blocker or Major finding remains.
- Map a reviewer's incomplete review to not run in the aggregator, because no EGM file at `36343a1` states that mapping.
- Keep placeholders for failed workers to outputs a human reads, where the gap stays visible.
- Test the status rule with an empty findings list and one silent reviewer.

## Related

- [Elephant-Goldfish Design Review](elephant-goldfish-design-review.md) — the full workflow this rule sits in
- [Zero Violations Is Not Evidence Your Hook Works](../../verification/enforcement-liveness-evidence.md) — the same blind spot in hook enforcement
- [Fan-Out Synthesis Pattern](fan-out-synthesis.md) — merging parallel attempts into one result
- [Bounded Batch Dispatch](bounded-batch-dispatch.md) — record a failed item and continue, for bulk work
- [LLM Map-Reduce Pattern](llm-map-reduce.md) — retry failed chunks and degrade on partial results
- [Convergence Detection in Iterative Agent Refinement](../../loop-engineering/convergence-detection.md) — other stop rules for refinement loops
