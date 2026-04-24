---
title: "Premature Completion: Agents That Declare Success Too Early"
description: "Coding agents stop after the first visible signal of progress — first test passing, first patch applied — while failing tests remain. Four independent research teams named the same failure mode within a year."
tags:
  - agent-design
  - testing-verification
  - workflows
aliases:
  - fixing correct code
  - premature termination
  - incomplete-fix inflation
---

# Premature Completion

> Coding agents stop after the first visible signal of progress and declare done while failing tests, unmet objectives, or unverified artifacts persist. Distinct from continuing past completion — same surface symptom, different cause, different fix.

## Four Names for the Same Failure

Independent teams have named this pattern four different ways within a year:

| Source | Name | Evidence |
|--------|------|----------|
| [SRI Lab, ETH Zurich](https://www.sri.inf.ethz.ch/blog/fixedcode) | "Fixing correct code" | Agents patch already-passing code **>50%** of the time across Claude Opus 4.6, Sonnet 4.6, GLM-5, GPT-5.4, Gemini 3 Pro, Qwen3.5 on 235 tasks |
| [ForgeCode](https://forgecode.dev/blog/gpt-5-4-agent-improvements/) | "Premature completion" | GPT-5.4 implements, sounds confident, stops — "edge cases missed, files not saved, tests not run" |
| [SWE-EVO (arxiv 2512.18470)](https://arxiv.org/abs/2512.18470) | "Premature termination" | Table 5: *"stopped or concluded early after encountering difficulty, without exhausting reasonable next steps"* |
| [arxiv 2503.15223](https://arxiv.org/html/2503.15223v1) | "Inflated resolution rates" | Full test suites expose **6.2 pp** of reported SWE-Bench resolution as patches that fail untouched tests |

Converging terminology across four unrelated teams is strong evidence the failure is real and underdescribed.

## Why It Happens

The agent's "I'm done" token is triggered by a first-signal-of-progress pattern — tests pass, patch applied, reasoning chain terminates — that is a valid proxy on most training data but under-specified for multi-file or multi-test scope.

- **Training distribution**: single-fix trajectories dominate the corpus; the stop token is conditioned on first-fix success ([SRI Lab](https://www.sri.inf.ethz.ch/blog/fixedcode)).
- **Context pressure**: as trajectories grow, attention to the original spec degrades; stopping early is cheaper than re-reading ([ForgeCode](https://forgecode.dev/blog/gpt-5-4-agent-improvements/)).
- **No reproduction step**: agents that patch without first reproducing cannot tell already-passing code from a real bug. A reproduction-first prompt moves GPT-5.4 mini from **24% to 77%** on the correct-code task ([SRI Lab](https://www.sri.inf.ethz.ch/blog/fixedcode)).

## Capability-Band Skew

SWE-EVO's Figure 6 shows "o3, gpt-4.1, gpt-4o exhibit more syntax, looping, and early-termination failures on SWE-EVO, indicating less robust long-horizon trajectories compared to gpt-5" ([arxiv 2512.18470](https://arxiv.org/abs/2512.18470)). GPT-5 shows near-zero early termination — its failures are instruction-following.

Weak models fail before reaching a stopping point. Strong models verify internally. Mid-band models are just good enough to see green and declare done — the band where mitigations matter most.

## Distinguish From Adjacent Failures

Same surface symptom, different cause, different fix:

| Failure | Primary cause | Fix |
|---------|--------------|-----|
| **Premature completion** | First-signal-of-progress stop token | Externalise stopping criterion to test-suite state |
| [Objective drift](objective-drift.md) | Context compression lost specifics | Structured session intent re-read after compaction |
| Continuing past completion | Missing termination signal | Max-iteration cap; sentinel hash check |
| Context-pressure abandonment | Token budget exhausted | Context compression; sub-agent delegation |

## Mitigations That Work

- **Reproduction-first prompting.** Require the agent to trigger the bug before patching — moves GPT-5.4 mini from 24% to 77% on the correct-code task ([SRI Lab](https://www.sri.inf.ethz.ch/blog/fixedcode)).
- **Runtime-enforced verification.** If the model skips the verification skill, the runtime injects a reminder and blocks termination. No opt-out. ForgeCode reports reaching 81.8% on TermBench 2.0 with this change ([ForgeCode](https://forgecode.dev/blog/gpt-5-4-agent-improvements/)).
- **Pre-completion checklists as harness variables.** LangChain moved Terminal Bench 2.0 from 52.8% to 66.5% through harness-only changes including pre-completion checklists, tunable in the [harness hill-climbing](../agent-design/harness-hill-climbing.md) loop ([LangChain](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)).
- **Stopping criteria tied to observable state.** Transcript-based verifiers that pattern-match "all tests passing" in agent output provide zero additional signal — execute against the git branch.

## Mitigations That Don't Work Alone

- **"Be thorough" instructions** — no behavioural hook tied to observable state.
- **Longer reasoning chains** — defer the stopping-criterion choice without changing it.
- **Chain-of-thought prompting** — can mask the failure by producing more confident-sounding wrong completions.

## When This Backfires

- **Strong-model deployments.** GPT-5 and Claude Opus 4.6 show near-zero premature-termination on SWE-EVO. Pre-completion checklists add cost without benefit — upgrading the model is the honest fix.
- **Trivial stopping criteria.** For single-assertion tasks, agent self-assessment matches observable state already.
- **Over-verification spiral.** Runtime-enforced verification without an iteration cap can trigger the inverse pathology (continuing past completion).
- **Benchmark masking.** Harnesses that only check final-state pass hide premature completion when agents happen to fix the first bug. Score unfixed-but-should-have-been tests, not net-pass delta.

## Key Takeaways

- Premature completion is a stopping-criterion misalignment — the "done" token fires on first-signal-of-progress patterns that under-specify multi-file work.
- Four independent teams have named this same failure within a year; agents "fix" correct code >50% of the time.
- Mid-tier models are affected most; frontier models verify internally.
- Reproduction-first prompts, runtime-enforced verification, and externalised stopping criteria are the evidence-backed mitigations.
- Distinguish from continuing-past-completion, objective drift, and context-pressure abandonment — same symptom, different fix.

## Related

- [Behavioral Drivers of Coding Agent Success and Failure](../agent-design/behavioral-drivers-agent-success.md) — verification cluster and post-patch loop patterns
- [Harness Hill-Climbing](../agent-design/harness-hill-climbing.md) — pre-completion checklist as a tunable harness variable
- [Completion Failure Taxonomy](../verification/completion-failure-taxonomy.md) — broader failure classification for completion systems
- [Objective Drift](objective-drift.md) — adjacent failure: subtly different task completed
- [Agent Self-Review Loop](../agent-design/agent-self-review-loop.md) — post-patch verification pattern
- [Pre-Completion Checklists](../verification/pre-completion-checklists.md) — verification steps before declaring done
- [Red-Green-Refactor for Agents](../verification/red-green-refactor-agents.md) — test-state as externally observable stopping criterion
