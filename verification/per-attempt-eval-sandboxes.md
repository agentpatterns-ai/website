---
title: "Per-Attempt Sandboxes for Agents That Change the Filesystem"
term: "Per-Attempt Sandbox"
description: "Score an agent whose output is workspace state by giving every attempt its own clean container, and keep the verifier outside that container or the score is forgeable."
aliases:
  - per-attempt container
  - sandboxed agent evals
  - clean container per attempt
tags:
  - testing-verification
  - evals
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-15
maturity: emerging
---

# Per-Attempt Sandboxes for Agents That Change the Filesystem

> An agent whose output is filesystem state gets scored by reading the workspace, and that takes a clean sandbox per attempt.

A per-attempt sandbox gives each eval trial its own container, built from a pinned image and thrown away once the verifier has read it. Two claims travel together under the phrase "a clean container per attempt", and only one is settled. That attempts must not inherit each other's state is measured, and it holds. That the container therefore makes the score trustworthy is false as most benchmarks build it. The gap between those two is what this page is about.

## Conditions that make it worth building

- The result is on disk, not in the reply. Terminal-Bench's tests "verify that all outcomes described in the instruction have been achieved by testing properties of the final container state; they do not test the agent's commands or console output" ([Duan and others, 2026](https://arxiv.org/abs/2601.11868v1)). If a grader can read the answer out of the transcript, you are paying image build time for nothing.
- Something installs. A resettable checkout handles an agent that edits tracked files. It does not handle `apt install`, a global npm package, or a mutated virtualenv.
- You will compare this week's numbers against last week's. Isolation without stable artifacts gets you a reproducible run you cannot chart.

## Why it works

A reused environment makes the score a function of run order, and the evidence is a before-and-after rather than an argument. SWE-bench first tried conda environments, then added explicit package versioning on top of them. "In hindsight, it is underspecified," its maintainers wrote, because evaluation "remained sensitive to discrepancies originating from different platforms and user-specific configurations, leading to inconsistent results." Per-sample Docker images moved ground-truth reproduction to 99.78% (2289/2294) of SWE-bench tasks and 100% (300/300) of SWE-bench Lite ([SWE-bench, 2024](https://github.com/SWE-bench/SWE-bench/tree/0c0de95298dc502afa94b49bd8384e5f3ef81790/docs/20240627_docker)). Microsoft names the same machine differences as hidden variables, from operating system and shell down to absolute file paths and silent tool updates, and warns that "a model switch that 'improves scores by 8 points' might be entirely explained by the fact that you ran it on a different machine" ([Microsoft, 2026](https://developer.microsoft.com/blog/the-hidden-variables-in-your-agent-eval/)).

## Put the verifier outside the agent's container

A fresh container per attempt bounds contamination between attempts. It does nothing about contamination between the agent and the thing scoring it, because the two normally share one filesystem. Terminal-Bench states it plainly: "Agents run inside a container into which the tests are copied and executed" ([Duan and others, 2026](https://arxiv.org/abs/2601.11868v1)). SWE-bench Verified has the same shape, and an audit describes the consequence. The harness "resets files enumerated in the upstream test patch but does not reset arbitrary files the agent creates, and a conftest.py dropped at the repository root survives the reset and is auto-discovered by pytest" ([Wang and others, 2026](https://arxiv.org/abs/2605.12673v1)). Ten lines of pytest hook then report every test as passing without running one.

That audit found 219 distinct flaws across ten popular agent benchmarks, with synthesized exploits reaching "near-perfect scores on most of the benchmarks without solving a single task" ([Wang and others, 2026](https://arxiv.org/abs/2605.12673v1)). Its isolation checklist leads with the fix, "Run evaluation code outside the agent's container or VM", and where the two genuinely must share one it falls back to read-only mounts for test files and scoring scripts plus OS-level read and write boundaries.

## What a run has to emit

A job directory is per-run and local to the machine that ran it, so comparing across weeks means keeping every folder and sharing a result means zipping one ([Braintrust, 2026](https://www.braintrust.dev/blog/harbor-agent-evals)). Four artifacts survive that: the task cases as a dataset, one row per trial carrying the agent's output alongside the expected answer, verifier rewards converted into named score fields you can chart and filter, and the trajectory of tool calls and model turns behind each score. The last one earns its cost only if somebody opens a failing trial and reads back to the call where the agent went wrong.

## When this backfires

- The verifier lives in the agent's container. You have bought isolation against the wrong adversary and can still be handed a forged score ([Wang and others, 2026](https://arxiv.org/abs/2605.12673v1)).
- The agent produces an answer rather than an effect. A classifier or summarizer leaves nothing on disk, so [outcome grading](grade-agent-outcomes.md) over the response is cheaper and measures the same thing.
- Attempts share state the container does not own. A fresh image does not reset a staging database, a third-party API, or a rate-limit counter. Isolation stops at the container edge, which is where [emulated APIs](emulated-apis-for-skill-evals.md) take over.
- The bill outruns the decision. SWE-bench needs about 120GB of free disk to start, and about 2,000GB to cache instance images for the fast path ([SWE-bench, 2024](https://github.com/SWE-bench/SWE-bench/tree/0c0de95298dc502afa94b49bd8384e5f3ef81790/docs/20240627_docker)). Terminal-Bench 2.0 ran between 32 and 100 containers in parallel to get through 32,155 trials ([Duan and others, 2026](https://arxiv.org/abs/2601.11868v1)). A three-config comparison over ten tasks does not need that machinery, and [sizing the suite to the decision](purpose-built-eval-suites.md) comes first.
- The image is nothing like production. A developer's machine has a configured language server feeding diagnostics back mid-generation, and "an eval rig running in a container or CI environment might not" ([Microsoft, 2026](https://developer.microsoft.com/blog/the-hidden-variables-in-your-agent-eval/)). You have traded one confound for another.

## Example

Harbor is a Python framework for specifying sandboxed agent tasks, from the team behind Terminal-Bench, and it runs each task in an isolated Docker container. A task holds three files: an environment definition, an instruction for the agent, and a verifier that inspects the container once the agent stops ([Braintrust, 2026](https://www.braintrust.dev/blog/harbor-agent-evals)). Terminal-Bench 2.0 is distributed in that format and ran its published numbers on Daytona sandboxes, repeating each model and agent combination at least five times ([Duan and others, 2026](https://arxiv.org/abs/2601.11868v1)).

One flag turns the local job directory into a synced project carrying the dataset, per-trial rows, score fields, and trajectory listed above ([Braintrust, 2026](https://www.braintrust.dev/blog/harbor-agent-evals)):

```bash
uv run harbor run \
  --path task \
  --agent terminus-2 \
  --model openai/gpt-4.1-mini \
  --job-name braintrust-harbor-example \
  --plugin braintrust \
  --plugin-kwarg project_name=example-harbor
```

Note what that command does not settle. Where the verifier sits is a property of the task, not of the runner. The same audit found SkillsBench running "the agent and the verifier in the same Modal-style container under Harbor", with the agent as root and sharing Python site-packages with the tooling the verifier later invokes ([Wang and others, 2026](https://arxiv.org/abs/2605.12673v1)). Portable artifacts make a bad score easier to chart, not harder to forge.

## Key Takeaways

- Score effect-producing agents by reading the final workspace state, because the transcript is an incomplete record of what the agent did.
- Per-attempt containers are measured, not assumed. SWE-bench went from a conda setup its own maintainers called underspecified to 99.78% ground-truth reproduction.
- The container boundary that matters most sits between the agent and the verifier, and almost every shipping benchmark puts them on one filesystem.
- Emit four things per run: the dataset, one row per trial, named score fields from the verifier's rewards, and the trajectory.
- Skip the whole apparatus when nothing installs, when the answer is in the reply, or when the disk bill is larger than the decision.

## Related

- [Grade Agent Outcomes, Not Execution Paths](grade-agent-outcomes.md) — the grading principle this implements, with a filesystem as the outcome being read
- [Stateful Agent Evals via State Snapshots and Transition Assertions](stateful-agent-state-and-transition-evals.md) — names a resettable environment as a precondition, then scores the span and trace behavior inside it
- [Purpose-Built Eval Suites for Model and Harness Swaps](purpose-built-eval-suites.md) — sizing the suite to the decision, which is what tells you whether the container bill is justified
- [Eval Environment Containment for Cyber-Capable Agents](eval-environment-containment.md) — the same boundary read as a safety control rather than a measurement control
- [Anti-Reward-Hacking: Rubrics That Resist Gaming](anti-reward-hacking.md) — the wider class of failures a tamperable verifier belongs to
