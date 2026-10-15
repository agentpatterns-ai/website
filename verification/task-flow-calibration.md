---
title: "Calibrate a Benchmark's Interaction Layer to Your Users"
term: "Task Flow Calibration"
description: "Issue-derived suites fix one polished prompt per task. Measure your users' session lengths, intents, and transitions, then reshape the suite to match."
tags:
  - testing-verification
  - evals
  - benchmarks
  - tool-agnostic
  - arxiv
aliases:
  - task flow calibration
  - interaction-layer calibration
  - TaskFlow Alignment Score
last_reviewed: 2026-10-14
maturity: emerging
---

# Calibrate a Benchmark's Interaction Layer to Your Users

> Task Flow calibration measures your users' session lengths, intents, and message-to-message transitions, then reshapes a benchmark's prompts to match them.

Task Flow calibration treats a benchmark's interaction layer as a parameter you measure on your own population rather than inherit from the suite. The interaction layer is how many user messages a task delivers, what each one asks for, and the order they arrive in. Run it to learn what a task costs under a realistic interaction pattern, not to find a different winner. On the 700 splittable SWE-Bench Pro tasks under one scaffold, splitting each issue into three turns "approximately doubled agent cost" ([Slinko et al., 2026, §4](https://arxiv.org/abs/2610.09633v2)). Resolve-rate shifts "were mixed across models and largely comparable to run-to-run variation, so these runs establish no success ordering" ([Slinko et al., 2026, §4](https://arxiv.org/abs/2610.09633v2)). Every condition ran three times, reported as min-max ranges with no significance test, so those resolve-rate readings are directional ([§5](https://arxiv.org/abs/2610.09633v2)).

## The gap you are closing

Running one 16-label classifier over both the suite's prompts and real user messages turns the mismatch into a measurement. In SWE-Bench Pro, "new features (54.7%) and bug fixes (39.1%) account for 93.8% of tasks" ([Slinko et al., 2026, §1](https://arxiv.org/abs/2610.09633v2)). Across 4,782 agent sessions recorded from JetBrains IDE users, bug fixes (25.9%) and new features (18.9%) "lead but do not dominate as they do in issue-derived datasets" ([§2](https://arxiv.org/abs/2610.09633v2)). What remains asks the agent to explain code, answer general questions, plan, review, refactor and run things.

Session shape diverges too. Of those 4,782 sessions, "50.9% contain a single user message and 33% at least three". Inside that long-session slice, "explain requests (questions about how the project's code works) account for 6.1%, while general programming questions for another 9.7%" ([§2](https://arxiv.org/abs/2610.09633v2)). The paper calls explanation, not general questions, the intent issue-derived benchmarks lack; general questions "still needs its own augmentation" ([§5](https://arxiv.org/abs/2610.09633v2)). A single-turn prompt scores zero on the length component against a three-message target, since its length bin carries no target mass ([Appendix F](https://arxiv.org/abs/2610.09633v2)).

## How to calibrate

The paper gives a seven-step procedure ([Appendix C](https://arxiv.org/abs/2610.09633v2)). Six of the seven steps carry most of the work (selection by TFAS is step 6, stress-test slices step 7, both covered below):

1. Name the target: a user population, a product surface, a session filter, and a measurement window. The filter is part of the definition, because the same sample filtered at one message instead of three is dominated by single-message sessions. "Task Flows also drift as products and models change, so a target should carry its measurement date."
2. Sample user-side messages only. No agent output, no code, no tool logs, which keeps collection cheap and limits what you store.
3. Classify against a taxonomy frozen before measurement, after an inter-model agreement check on at least 100 sessions. Low agreement signals ambiguous label definitions, which the paper says to revise and re-run before the target is fixed, "not corrected afterwards".
4. Measure the target Task Flow as three distributions: session lengths, task types, and directed transitions with start and end edges.
5. "Classify the source benchmark's prompts with the same pipeline to obtain its own Task Flow" and diff it against the target component by component: lengths, intents, transitions.
6. Augment only the gaps you can verify. Report the rest as uncovered rather than filling them with turns nothing can score.

Alignment then has a number on it. The paper's Jensen-Shannon-based TaskFlow Alignment Score moved from 59.6 for plain prompt splitting to 77.8 once question count and placement were tuned per task, on the same 700 tasks against the long-session production target ([Slinko et al., 2026, Table 2](https://arxiv.org/abs/2610.09633v2)).

## Why it works

A score comes out of a task and a protocol together, and issue-derived suites pin the protocol at one upfront message. The study isolates that variable, holding the repository, requested change, environment and final tests fixed while regenerating only the user messages. The authors designed splitting to target overspecification. The original issue states "the goal, context, constraints, and often the approach in one polished message, whereas real users reveal requirements gradually" ([Slinko et al., 2026, §3](https://arxiv.org/abs/2610.09633v2)). The authors read their pilot as showing that "progressive disclosure reliably changes the effort an agent expends". Transfer fails for a second reason: a suite whose prompts are 93.8% feature-or-bugfix lacks the explain intent, which with general questions makes up 15.8% of long-session messages. Splitting also buys intermediate verification: after each issue turn the harness snapshots the repository and re-runs the original test suite, instead of scoring one final patch ([Slinko et al., 2026, Appendix H](https://arxiv.org/abs/2610.09633v2)).

## When this backfires

The study names most of these conditions itself, in its discussion and limitations ([Slinko et al., 2026, §5](https://arxiv.org/abs/2610.09633v2)).

- You only want a ranking. The pilot found no stable resolve-rate ordering, so a calibrated protocol can return the same answer at a higher cost: splitting alone "approximately doubled agent cost", and the calibrated QA turns "add moderate cost on top of Split".
- Your sample is thin. With 13 retained labels plus start and end edges the transition support runs to about 200 cells, most of them rare, so bootstrap-resample whole sessions and confirm the component scores hold before you fix the target ([Appendix C](https://arxiv.org/abs/2610.09633v2)).
- The intents you care about are rare. "Any selection that maximizes alignment with observed frequencies pushes rare intents toward zero" ([Appendix C](https://arxiv.org/abs/2610.09633v2)), so destructive execution and security-relevant review need their own slices, reported apart from the calibrated core.
- The intent has no verifier. The paper reports planning and code-review turns as uncovered because automatic checking of them is unclear, and a turn nothing can score adds realism while subtracting trust.
- You borrowed someone's corpus, or trusted a model's labels. Long-session samples from SpecStory, DataClaw and SWE-chat differ from each other and from the JetBrains sample: "there is no ground-truth interaction distribution, and the target must be measured in its own setting" ([§2](https://arxiv.org/abs/2610.09633v2)). Your own target is provisional too, since the paper's own classifier "lacks a human-labeled accuracy set" and rests on 76.1% mean pairwise inter-model agreement on 100 sessions ([§5](https://arxiv.org/abs/2610.09633v2), [Appendix C](https://arxiv.org/abs/2610.09633v2)).

## Key Takeaways

- Ask any score you read which interaction distribution produced it. A suite that states no target use case is reporting one protocol's number as if it were general.
- Report agent cost per task beside resolve rate. The split protocol roughly doubled the first while leaving the second comparable to run-to-run variation, which a single score hides.
- The explain intent is the gap this approach already closes. A repository question carries a hidden reference answer and an executable proof script, and answer accuracy becomes "a second verified signal alongside resolve rate" ([Slinko et al., 2026, §§3–4](https://arxiv.org/abs/2610.09633v2)).
- Re-measure before you reuse a calibrated suite across a model generation or a product change. An undated target describes a population you may no longer have.

## Related

- [Benchmark-Driven Tool Selection for Code Generation](benchmark-driven-tool-selection.md) — which suite to trust when synthetic puzzles overstate capability
- [Purpose-Built Eval Suites for Model and Harness Swaps](purpose-built-eval-suites.md) — building a small suite over your own tasks, and sizing it to the decision
- [Multi-Turn Conversation Evaluation](multi-turn-conversation-evaluation.md) — scoring the turns once your suite has more than one
- [Trajectory-Aware Benchmark Subset Selection for Agents](trajectory-aware-benchmark-subset-selection.md) — choosing which instances survive a subset, inside a fixed protocol
