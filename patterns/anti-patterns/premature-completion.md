---
title: "Premature Completion: Agents That Declare Success Too Early"
term: "Premature Completion"
description: "Coding agents stop after the first visible signal of progress — first test passing, first patch applied — while failing tests remain. Four independent research teams named the same failure mode within a year."
tags:
  - agent-design
  - testing-verification
  - workflows
  - tool-agnostic
  - anti-pattern
aliases:
  - fixing correct code
  - premature termination
  - incomplete-fix inflation
last_reviewed: 2026-06-13
maturity: established
---

# Premature Completion: Agents That Declare Success Too Early

> Coding agents stop after the first visible signal of progress and declare done while failing tests, unmet objectives, or unverified artifacts persist. Distinct from continuing past completion — same surface symptom, different cause, different fix.

## Four names for the same failure

Independent teams have named this pattern four different ways within a year:

| Source | Name | Evidence |
|--------|------|----------|
| [SRI Lab, ETH Zurich](https://www.sri.inf.ethz.ch/blog/fixedcode) | "Fixing correct code" | Agents patch already-passing code >50% of the time across Claude Opus 4.6, Sonnet 4.6, GLM-5, GPT-5.4, Gemini 3 Pro, Qwen3.5 on 235 tasks |
| [ForgeCode](https://forgecode.dev/blog/gpt-5-4-agent-improvements/) | "Premature completion" | GPT-5.4 implements, sounds confident, stops — "edge cases missed, files not saved, tests not run" |
| [SWE-EVO (arxiv 2512.18470)](https://arxiv.org/abs/2512.18470v6) | "Gave Up Prematurely" | *"Agent stops or declares failure while reasonable next steps remain."* |
| [arxiv 2503.15223](https://arxiv.org/html/2503.15223v1) | "Inflated resolution rates" | Full test suites expose 6.2 pp of reported SWE-Bench resolution as patches that fail untouched tests |

Converging terminology across four unrelated teams is strong evidence the failure is real and underdescribed.

## Why it happens

A first-signal-of-progress pattern triggers the agent's "I'm done" token — tests pass, patch applied, reasoning chain terminates. That pattern is a valid proxy on most training data, but under-specified for multi-file or multi-test scope.

- Training distribution: single-fix trajectories dominate the corpus, so the stop token learns to fire on first-fix success ([SRI Lab](https://www.sri.inf.ethz.ch/blog/fixedcode)).
- Context pressure: as trajectories grow, attention to the original spec degrades, and stopping early is cheaper than re-reading ([ForgeCode](https://forgecode.dev/blog/gpt-5-4-agent-improvements/)).
- No reproduction step: agents that patch without first reproducing cannot tell already-passing code from a real bug. A reproduction-first prompt moves GPT-5.4 mini from 24% to 77% on the correct-code task ([SRI Lab](https://www.sri.inf.ethz.ch/blog/fixedcode)).

## Capability-band skew

SWE-EVO reports that the older models o3, gpt-4.1 and gpt-4o "exhibit more looping and early-termination issues". The rising syntax-error failures belong to the smaller variants, not to those older ones ([arxiv 2512.18470v6](https://arxiv.org/abs/2512.18470v6)). GPT-5 shows near-zero early termination — its failures are instruction-following.

Weak models fail before reaching a stopping point. Strong models verify internally. Mid-band models are just good enough to see green and declare done — the band where mitigations matter most.

## Distinguish from adjacent failures

Same surface symptom, different cause, different fix:

| Failure | Primary cause | Fix |
|---------|--------------|-----|
| Premature completion | First-signal-of-progress stop token | Externalize stopping criterion to test-suite state |
| [Objective drift](objective-drift.md) | Context compression lost specifics | Structured session intent re-read after compaction |
| Continuing past completion | Missing termination signal | Max-iteration cap; sentinel hash check |
| Context-pressure abandonment | Token budget exhausted | Context compression; sub-agent delegation |

## Mitigations that work

- Reproduction-first prompting. Require the agent to trigger the bug before patching — this moves GPT-5.4 mini from 24% to 77% on the correct-code task ([SRI Lab](https://www.sri.inf.ethz.ch/blog/fixedcode)).
- Runtime-enforced verification. If the model skips the verification skill, the runtime injects a reminder and blocks termination. There is no opt-out. ForgeCode reports reaching 81.8% on TermBench 2.0 with this change ([ForgeCode](https://forgecode.dev/blog/gpt-5-4-agent-improvements/)).
- Pre-completion checklists as harness variables. LangChain moved Terminal Bench 2.0 from 52.8% to 66.5% through harness-only changes including pre-completion checklists, tunable in the [harness hill-climbing](../agent-design/harness-hill-climbing.md) loop ([LangChain](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)).
- Stopping criteria tied to observable state. Transcript-based verifiers that pattern-match "all tests passing" in agent output give no extra signal — execute against the git branch.

## Mitigations that do not work alone

- "Be thorough" instructions — no behavioral hook tied to observable state.
- Longer reasoning chains — defer the stopping-criterion choice without changing it.
- Chain-of-thought prompting — can mask the failure by producing more confident-sounding wrong completions.

## When this backfires

- Strong-model deployments. GPT-5 and Claude Opus 4.6 show near-zero premature-termination on SWE-EVO. Pre-completion checklists add cost without benefit — upgrading the model is the honest fix.
- Trivial stopping criteria. For single-assertion tasks, agent self-assessment matches observable state already.
- Over-verification spiral. Runtime-enforced verification without an iteration cap can trigger the inverse pathology, [continuing past completion](../../verification/completion-failure-taxonomy.md).
- Benchmark masking. Harnesses that only check final-state pass hide premature completion when agents happen to fix the first bug. Score unfixed-but-should-have-been tests, not net-pass delta.

## Key Takeaways

- Premature completion is a stopping-criterion misalignment — the "done" token fires on first-signal-of-progress patterns that under-specify multi-file work.
- Four independent teams have named this same failure within a year; agents "fix" correct code >50% of the time.
- Mid-tier models are affected most; frontier models verify internally.
- Reproduction-first prompts, runtime-enforced verification, and externalized stopping criteria are the evidence-backed mitigations.
- Distinguish from continuing-past-completion, objective drift, and context-pressure abandonment — same symptom, different fix.

## Related

- [Behavioral Drivers of Coding Agent Success and Failure](../agent-design/behavioral-drivers-agent-success.md) — verification cluster and post-patch loop patterns
- [Harness Hill-Climbing](../agent-design/harness-hill-climbing.md) — pre-completion checklist as a tunable harness variable
- [Completion Failure Taxonomy](../../verification/completion-failure-taxonomy.md) — broader failure classification for completion systems
- [Objective Drift](objective-drift.md) — adjacent failure: subtly different task completed
- [Agent Self-Review Loop](../../code-review/agent-self-review-loop.md) — post-patch verification pattern
- [Pre-Completion Checklists](../../verification/pre-completion-checklists.md) — verification steps before declaring done
- [Red-Green-Refactor for Agents](../../verification/red-green-refactor-agents.md) — test-state as externally observable stopping criterion
- [Shallow Agent Test Coverage from Premature Termination (Lazy Generation)](lazy-generation.md) — the same premature-stop failure narrowed to test generation, where the shortfall skews onto complex branches
- [Assuming Loaded Skills Stay Enforced in Long Contexts](assuming-loaded-skills-stay-enforced.md) — the dropped-obligation version: a required item silently falls out of a long trajectory, and a self-check inherits the same blind spot
