---
title: "Writing Retained Instructions for Later Tasks"
term: "Retained Instructions"
description: "Evaluate retained instructions on later tasks: covered test-runner guidance and a known-failures list reduced repeated work in one small study."
tags:
  - instructions
  - tool-agnostic
  - arxiv
aliases:
  - retained experience scope
  - retained instructions for later tasks
last_reviewed: 2026-10-28
maturity: emerging
staleness_risk: true
---

# Writing Retained Instructions for Later Tasks

> Retained instructions reduced repeated work in two covered transfer cases; evaluate their contents, later-task scope, and extra work together.

A retrospective can retain a test command or a list of known failures. Both worked in covered cases in Treude and Baltes's study: a SymPy test-runner pointer reduced the targeted action from 5 of 5 sessions to 0 of 5, and an Astropy three-test list reduced it from 3 of 5 to 0 of 5. Five other informative transfer events encountered problems outside the adaptations' contents ([arXiv:2610.34938v1, section IV](https://arxiv.org/abs/2610.34938v1)).

## When this applies

The evidence is narrow. Read these conditions before acting on anything below.

- One agent and one retrospective skill: Claude Code 2.1.295 with Opus 5.5, running `/retro` from source commit `b0618bc` on 30 SWE-bench Verified issues ([arXiv:2610.34938v1, section III](https://arxiv.org/abs/2610.34938v1)).
- The evaluated transfer evidence concerns environment problems, such as pre-existing test failures or a missing test runner. The authors name evaluation of adaptations for code navigation and coding conventions as future work ([arXiv:2610.34938v1, section VI](https://arxiv.org/abs/2610.34938v1)).
- The later tasks were picked because they reproduced the problem each adaptation targeted. The authors state this "may overestimate how often adaptations would help on unselected tasks" ([arXiv:2610.34938v1, section V](https://arxiv.org/abs/2610.34938v1)).
- Seven transfer events were informative, with five sessions per harness. The authors say these counts "do not establish that covering the encountered problem explains the differences between adaptations, which differ in several properties at once and were grouped after labeling" ([arXiv:2610.34938v1, section V](https://arxiv.org/abs/2610.34938v1)).

## What transferred and what did not

Across the seven informative events, the two adaptations whose content covered the instances later sessions encountered removed the targeted action. A SymPy `CLAUDE.md` line naming `bin/test` as the test runner "prevented the initial attempt to run the unavailable pytest in every adapted session, reducing recurrence from 5 of 5 sessions to 0 of 5". An Astropy known-failures file listing three failing tests took recurrence from 3 of 5 sessions to 0 of 5; every session hit one of the three listed failures ([arXiv:2610.34938v1, section IV](https://arxiv.org/abs/2610.34938v1)).

Of the five that did not cover what sessions hit, one reduced the targeted action from 5 of 5 sessions to 2 of 5 and four left it unchanged. For those four: "In four transfer events, recurrence did not decrease. In each of them, sessions encountered failures absent from the transferred known-failures files" ([arXiv:2610.34938v1, section IV](https://arxiv.org/abs/2610.34938v1)). In the fifth event, sessions hit NumPy failures outside the script's stored list, which it reported as new.

The Astropy result supports keeping useful instance lists. The uncovered cases motivate checking what a list covers and how its instruction treats an unlisted failure.

## Consultation and repeated work

Claude Code loaded the transferred context-file instructions in every adapted session and usually consulted their referenced files. Consultation does not establish that an adaptation changed behavior ([arXiv:2610.34938v1, sections III–IV](https://arxiv.org/abs/2610.34938v1)).

One Sphinx known-failures file "told Claude Code to treat any failure absent from the file as caused by its own edits". On an unrelated control issue, "four of five adapted sessions ran baseline comparisons, compared with none of five original-harness sessions", and the authors name the result plainly: "An incomplete failure list was thus followed by the verification it was meant to prevent" ([arXiv:2610.34938v1, section IV](https://arxiv.org/abs/2610.34938v1)). On the other two control tasks the pattern appeared more weakly, at 1 of 5 and 0 of 5 adapted sessions against none under the original harness.

The study marks an adaptation `consulted` when the agent read a referenced file or ran a recommended command: "Consulting a file did not establish that Claude Code acted on its contents" ([arXiv:2610.34938v1, section III](https://arxiv.org/abs/2610.34938v1)).

## Writing the adaptation

None of these is measured as an intervention. Each targets a failure the study observed.

1. Name actionable repository guidance when the session reveals it. In the SymPy case, the retained line named the repository's test runner after a failed `pytest` call.
2. Give an enumerated list an open-world default. State that failures outside the list may still be pre-existing and say how to check, so a session that steps outside the enumeration does not read that as proof it broke something.
3. Record the enumeration's basis. A list derived from one container at one dependency version should say so, which is what lets a later reader judge whether it still covers anything.
4. Keep one adaptation to one change. The SymPy `CLAUDE.md` file "removed the failed pytest call but bundled a second line telling Claude Code to run the CI lint checks before finishing. Every adapted session ran them, and median elapsed time rose from 88 to 156 seconds" ([arXiv:2610.34938v1, section IV](https://arxiv.org/abs/2610.34938v1)). Evaluate bundled changes separately before deciding which lines to retain.

The authors conclude: "Retained changes also need continued evaluation, because outdated or incomplete instructions can remain ineffective or add work" ([arXiv:2610.34938v1, section VI](https://arxiv.org/abs/2610.34938v1)). For how to run that check on a proposed edit, see [observability-driven harness evolution](../patterns/agent-design/observability-driven-harness-evolution.md); for the metadata that makes a later removal defensible, see [rule lifecycle metadata](rule-lifecycle-metadata.md).

## Example: A Known-Failures Instruction

**Before — the observed instruction:** the Sphinx file told the agent to treat a failure absent from the list as caused by its own edits. On an unrelated control issue, baseline comparisons rose from 0 of 5 original-harness sessions to 4 of 5 adapted sessions ([arXiv:2610.34938v1, section IV](https://arxiv.org/abs/2610.34938v1)).

**After — an untested recommendation:** record that the list describes observed failures and does not classify unlisted ones. Evaluate the revised instruction on both pre-existing failures and genuine regressions. The study did not test this replacement; its possible missed-regression cost remains unknown.

## When this backfires

- Replacing a concrete list with vague guidance can lose actionable information. The covered Astropy three-test list succeeded in this study.
- Treating unlisted failures as possibly pre-existing can weaken a real regression signal. Measure that cost alongside extra verification work.
- Stable infrastructure alone does not establish that a list covers every failure a later task can encounter.

These are authoring cautions drawn from the reported cases, not measured effects of the proposed revisions.

## Key Takeaways

- Retain actionable instructions and record the scope of any list they reference.
- Reading a referenced file establishes consultation; measure whether the targeted action recurs.
- Evaluate each retained change on later tasks and track additional work from bundled instructions.

## Related

- [Rule Lifecycle Metadata for Prunable Instruction Surfaces](rule-lifecycle-metadata.md) — the `source`, `applies_to`, and `retire_when` fields that record an instruction's basis so a later removal is defensible
- [The No-Op Test: Prune Agent Docs by Behavior, Not Length](behavioral-no-op-test.md) — the behavioral check for whether a retained line still moves the agent at all
- [Agent Context File Evolution: Treating ACFs as Configuration Code](agent-context-file-evolution.md) — the maintenance loops that keep a monotonically growing context file under the compliance ceiling
- [Observability-Driven Harness Evolution](../patterns/agent-design/observability-driven-harness-evolution.md) — how to test whether a proposed harness edit changes behavior on a later task
- [Accumulated Behavioral Rules from Review Feedback](../workflows/accumulated-behavioral-rules.md) — the surrounding loop that turns session evidence into persistent rules
