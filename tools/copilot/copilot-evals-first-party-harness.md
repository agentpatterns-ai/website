---
title: "Copilot Evals: What a First-Party Eval Harness Measures"
description: "Copilot Evals, in public preview since 17 November 2026, tests skills, custom agents and MCP tools against saved runs. What it checks, what it skips, and how to gate on it."
tags:
  - copilot
  - evals
  - testing-verification
aliases:
  - GitHub Copilot Evals
  - Copilot Evals public preview
  - Vally eval engine for Copilot
applies_to: "copilot@1.x"
last_reviewed: 2026-11-23
status: current
---

# Copilot Evals: What a First-Party Eval Harness Measures

> Copilot Evals tests a skill, custom agent, or MCP tool with repeatable tasks and saved runs you compare after each change.

GitHub Copilot Evals turns a task into a saved test for one customization in your Copilot setup, then lets you rerun it after you change that customization. It entered public preview on 17 November 2026 for Copilot Individual, Business, and Enterprise plans, and it uses Vally, "an extensible local eval tool", as its evaluation engine ([GitHub Changelog](https://github.blog/changelog/2026-11-17-github-copilot-evals-is-now-in-public-preview/)). It lowers the cost of a first eval. Choosing what to measure stays with you.

## What it measures

An eval gives an agent a realistic task, describes what a good result looks like, and "check[s] both the result and how the agent got there" ([GitHub Changelog](https://github.blog/changelog/2026-11-17-github-copilot-evals-is-now-in-public-preview/)). Its targets are the skills, custom agents, and MCP tools in your project ([Copilot Evals README](https://github.com/github/evals)).

Vally records the "how" as a trajectory: tool calls, token usage, turns, skill activations, and errors. Each grader scores that record and returns a pass or fail, a score between 0 and 1, and a plain-text evidence string ([Vally: How it works](https://microsoft.github.io/vally/concepts/how-it-works/)). Four grader kinds from Vally's documentation show the range:

- Static checks on the result, such as `file-exists` and `output-contains`. The same input gives the same result.
- A command run in the workspace, such as `npm test` through `run-command`. Also deterministic, and heavier.
- A path check, such as `tool-calls` with a `required` list, which tests whether the agent called a given tool ([Vally: Writing eval specs](https://microsoft.github.io/vally/guides/writing-eval-specs/)).
- An LLM judge, the `prompt` grader, that scores against a rubric. Vally labels this class non-deterministic and says it "requires multiple trials for confidence" ([Vally: Grader taxonomy](https://microsoft.github.io/vally/concepts/grader-taxonomy/)).

By default a trial passes only when every grader passed. The aggregate score is a mean kept for diagnosis ([Vally: Scoring](https://microsoft.github.io/vally/concepts/scoring/)). The Copilot Evals pages I read do not list which of these graders its create skill proposes, so check the proposed checks before you save an eval.

## What it leaves out

- One run is one sample. In Vally, `runs` defaults to 1, so each stimulus has "exactly one" trial unless you ask for more ([Vally: Scoring](https://microsoft.github.io/vally/concepts/scoring/)). GitHub's own caution is that "A passing check doesn't guarantee the AI will get it right every time" ([Copilot Evals README](https://github.com/github/evals)). Set `defaults.runs` above 1 and Vally flags a stimulus whose trials disagree as flaky.
- An eval with no graders passes. Vally leaves a stimulus with no graders out of the score, and an eval whose stimuli run successfully without any graders "passes vacuously". A grader type missing from a `weights` map drops out of the score ([Vally: Scoring](https://microsoft.github.io/vally/concepts/scoring/)).
- A check proves only what it checks. Inference: a green eval says nothing about tasks you did not write, and the sources describe no production-traffic measurement. For a comparison on live usage, see [Gate a Default Harness Switch With Online and Offline Evals](../../patterns/agent-design/shared-runtime-default-harness-eval-gates.md). To judge whether a metric fits the claim you make, see [Match Eval Design and Construct to the Claim You Make](../../verification/claim-matched-eval-design.md).

## Pick the first cases

Start with the failure you already know about. That is my recommendation, not GitHub's. The README's worked example is a release-notes skill tested on "one completed issue and one open issue", with three checks: only completed work appears, issue IDs survive, and the input files stay unchanged ([Copilot Evals README](https://github.com/github/evals)). Each check can pass or fail on its own, so a failure points at one behavior.

The product site shows a `pr-description` skill with three suggested scenarios (shipped versus deferred work, missing verification, instructions hidden in change notes) and starts with the first. GitHub labels that walkthrough "an illustrative workflow" ([Copilot Evals site](https://github.github.io/evals/)). Vally specs carry a `type` of `capability` or `regression` ([Vally: Writing eval specs](https://microsoft.github.io/vally/guides/writing-eval-specs/)). Once a case catches a real failure, keep it as a regression case.

## Feed a review gate

Two layers exist, and the documentation for the second sits with the engine rather than the plugin.

Inside Copilot Evals, you approve each run before it starts, and `/eval compare` compares two saved runs or the same task with and without a skill ([Copilot Evals README](https://github.com/github/evals)). Validating files and reading or comparing saved results "make no model calls". For what the with-and-without delta can and cannot prove, see [Skill Lift](../../verification/skill-lift.md). The site describes the plugin's `setup` skill as "Choose eval folders, suites and CI checks." ([Copilot Evals site](https://github.github.io/evals/)), and it ships three automation blueprints (`eval-health-review`, `eval-smoke-run`, `eval-skill-compare`) for VS Code Agents ([Copilot Evals README](https://github.com/github/evals)). The pages I read give no step-by-step CI recipe for those.

The one documented CI recipe belongs to the Vally CLI. Its quickstart runs `vally lint` on every pull request, a static check with no agent. It runs `vally eval` with `--require-pass` on trusted changes, and that flag makes the step exit 1 when a valid verdict fails. Without the flag, only grader, execution, configuration, or tooling errors fail the step ([Vally: Add to CI](https://microsoft.github.io/vally/get-started/add-to-ci/)). The same page splits suites by priority:

```text
vally eval --suite ci-gate --require-pass
vally eval --suite nightly
```

The `ci-gate` suite filters to priorities p0 and p1, and the nightly suite adds p2 and omits `--require-pass`. Vally's taxonomy guide advises static and complex-static graders in CI and LLM judges in the outer loop ([Vally: Grader taxonomy](https://microsoft.github.io/vally/concepts/grader-taxonomy/)).

Two CI conditions can stop a gate. The recommended workflow needs `copilot-requests: write`, and the quickstart tells an organization owner to enable "Allow use of Copilot CLI billed to the organization". Fork pull requests cannot receive that permission, so the quickstart skips their pre-merge eval and runs it after merge on `main` ([Vally: Add to CI](https://microsoft.github.io/vally/get-started/add-to-ci/)).

That quickstart targets Vally's own CLI and spec files. The pages I read do not say whether the eval files Copilot Evals saves run unchanged under that workflow, so test one before you rely on it.

## Limits of a preview you depend on

- Plans. Public preview covers Copilot Individual, Business, and Enterprise ([GitHub Changelog](https://github.blog/changelog/2026-11-17-github-copilot-evals-is-now-in-public-preview/)).
- Host requirements. The `/eval` commands and Evals Canvas "currently require Copilot CLI experimental mode", though the six skills work without it. Minimums are Node.js 24.0.0 for the CLI plugin (22.15.0 for VS Code), `@microsoft/vally-cli` 0.21.0, Copilot CLI 1.0.85, and Git 2.28.0 ([Copilot Evals README](https://github.com/github/evals)). VS Code needs 1.138.0 or later and a trusted local project ([Copilot Evals: Get started](https://github.github.io/evals/getting-started/)).
- Cost. "Evals does not enforce a total token or credit cap", although each run needs one approval of its costs, tools, and execution effects ([Copilot Evals: Get started](https://github.github.io/evals/getting-started/)).
- Execution. Setup scripts, tools, custom graders, and AI judges "can execute code and incur charges under your normal local permissions" ([Copilot Evals README](https://github.com/github/evals)).
- Telemetry. Released standalone plugin versions send telemetry by default. `COPILOT_EVALS_TELEMETRY=off`, `DO_NOT_TRACK=1`, or `OTEL_SDK_DISABLED=true` turns it off ([Copilot Evals README](https://github.com/github/evals)).
- License. The project is "source available", "not open-source software" ([Copilot Evals README](https://github.com/github/evals)).
- Engine version. The documented minimum Vally version is 0.21.0, a pre-1.0 number. Inference: pin the version in CI and read the release notes before you upgrade, because a pre-1.0 engine may change behavior between releases.

## Example

The README's release-notes case shows the full loop. You enter `/eval create` and describe the pass condition:

```text
Create an eval for this skill using one completed issue and one open issue.
Check that the release notes include only completed work, preserve the
issue IDs, and leave the input files unchanged.
```

You review the proposed cases, fixtures, and checks, save, then run `/eval run` and approve the cost summary. `/eval review` shows passing checks, outputs, and the conversation trace. After you edit the skill, `/eval run` again and `/eval compare` the new run with the saved one ([Copilot Evals README](https://github.com/github/evals)).

## Key Takeaways

- Copilot Evals targets skills, custom agents, and MCP tools, and checks the result plus the path the agent took.
- One trial is one sample. Raise `runs` before you trust a pass, and read flaky flags as signal.
- An eval with no graders passes, and an ungraded stimulus counts toward no score, so confirm every case carries at least one check.
- `/eval compare` compares saved runs before and after a change. The documented CI gate is the Vally CLI with `--require-pass`.
- Fork pull requests skip pre-merge evals in Vally's CI recipe, and the preview sets no cost cap.
- Treat it as a preview: pin versions, set a spend limit of your own, and review saved results before sharing.

## Related

- [Skill Evals: Measuring Skill Quality as a Dataset-Graded Unit](../../verification/skill-evals.md) — the tool-agnostic method behind this kind of harness
- [Skill Eval Loop](../claude/skill-eval-loop.md) — the same loop with Claude's skill-creator
- [Skill Lift: Measuring What a Skill Adds at Runtime](../../verification/skill-lift.md) — what a with-versus-without comparison proves
- [Gate a Default Harness Switch With Online and Offline Evals](../../patterns/agent-design/shared-runtime-default-harness-eval-gates.md) — online and offline gating for a harness change
- [GitHub Copilot Custom Agents and Skills Extensibility Guide](custom-agents-skills.md) — the customizations you would test
