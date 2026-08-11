---
title: "AX Evals: Measure the Agent-Facing Surface, Not the Model"
term: "AX Eval"
description: "Score whether your library, CLI, MCP server, or docs let a coding agent succeed, and design the eval so the score is attributable to that surface rather than to the model, the OS, or the workspace path."
tags:
  - testing-verification
  - evals
  - tool-agnostic
aliases:
  - agent experience evals
  - agent-experience evaluation
  - AX evaluation
last_reviewed: 2026-08-11
maturity: emerging
---

# AX Evals: Measure the Agent-Facing Surface, Not the Model

> An AX eval scores whether your tools, docs, and errors let an agent succeed, and attribution to that surface is the whole design problem.

An AX eval puts your product's agent-facing surface under test with the model held fixed. You score the same scenarios with and without your library, extension, or docs in place, and the difference between those conditions is the result. That delta only means something if nothing else moved. Microsoft's team reports that evals built without the discipline to hold everything else still produce "confident, consistent, and unfortunately meaningless results." [Source: [Microsoft, Building AX evals that actually work](https://developer.microsoft.com/blog/building-ax-evals-that-actually-work/)]

## When an AX eval is worth building

Four conditions have to hold before the number is worth acting on.

- You own a surface an agent reads or calls, and you can add and remove it. A library, CLI, MCP server, extension, or docs set.
- You can run a paired contrast. Without a baseline condition, a pass rate is an absolute number with nothing to attribute it to.
- Your run budget clears the noise floor. Microsoft sets a minimum of five runs per scenario, while measurement-reliability work puts convergence at 8 to 16 trials for structured tasks and 32 or more for complex reasoning ([Mustahsan and others, 2025](https://arxiv.org/abs/2512.06710v1)). Five screens out the obvious; it does not resolve a close result.
- You can calibrate the grader. An uncalibrated judge ranks your surface by how well it pleases an unmeasured rubric.

## What contaminates the score

Keep the rubric out of the agent's context first. Microsoft calls the rule absolute: "the scenario instruction should contain _only_ the developer prompt. No evaluation criteria mixed in, no scoring rubric alongside the task, no metadata about what you're testing." An agent that can read the rubric optimizes for grading instead of for the task. Beyond that, three failure modes recur across naive AX evals. [Source: [Microsoft AX evals](https://developer.microsoft.com/blog/building-ax-evals-that-actually-work/)]

- Vague criteria. A check like "uses proper error handling" has no shared definition, so two evaluators reading identical output return different verdicts.
- Presence standing in for usage. A library name in a source file is not the library working. Verifying correct usage means building and running the project, which inspecting the generated code never does.
- Environment contamination, the least visible of the three. Directory names carrying `poc`, `test`, `demo`, or `prototype` signal disposability, and the reported consequence is that "the agent eases up on enterprise-level concerns, skips authentication, simplifies error handling." Run from a neutral path such as `/workspace/project` rather than `/home/azureuser/test-workspace/poc-api`, use a generic user identity, and record a per-run manifest of OS, tool versions, model version, and harness version. [Source: [Microsoft, The hidden variables in your agent eval](https://developer.microsoft.com/blog/the-hidden-variables-in-your-agent-eval/)]

## Criteria as pass, fail, or skip

Write each criterion as a checklist item with an explicit condition for all three outcomes. The skip branch is what keeps the data honest: a criterion about authentication should not force a verdict on code that solved the problem with no authentication flow, and scoring that as a failure understates your surface. Independent per-check verdicts also give you a direction to act on rather than an opaque aggregate. [Source: [Microsoft AX evals](https://developer.microsoft.com/blog/building-ax-evals-that-actually-work/)]

## Calibrate the judge, then narrow its job

Validate the judge on two axes before it grades anything. For accuracy, run it against 5 to 10 outputs whose correct verdicts you already know and tighten the criteria until it agrees. For consistency, re-score identical code and confirm the verdicts match. A smaller model with explicit criteria can match a frontier judge, which moves the cost from model choice to criterion authoring. [Source: [Microsoft AX evals](https://developer.microsoft.com/blog/building-ax-evals-that-actually-work/)]

Then take work away from it. Judges make arithmetic errors, so have the judge return per-criterion verdicts with evidence and compute aggregates in code. Judges also fail at exact domain reasoning: Microsoft's mini-class models could not reliably compare semantic version ranges, so a custom tool handled version comparison and the judge only reported what was installed. [Source: [Microsoft AX evals](https://developer.microsoft.com/blog/building-ax-evals-that-actually-work/)] Once verdicts gate a pipeline, check them against human labels as well ([judge meta-evaluation](meta-evaluate-llm-judge-rubric-verification.md)).

## Read the two variances separately

Run-over-run variance inside one condition measures environmental instability. Variance between conditions measures your surface. A scenario passing 90% with your extension and 50% without demonstrates a reliable benefit; 70% in both conditions says the extension does nothing for that task. [Source: [Microsoft AX evals](https://developer.microsoft.com/blog/building-ax-evals-that-actually-work/)] Version your rubrics, and do not compare scores across rubric versions without recalibrating.

## Why it works

An agent's output is a function of its entire input stream, so any uncontrolled part of that stream becomes a rival explanation for the score. The effect is measurable: on one task, several models picked .NET on Windows and Python or Node.js on Linux, and one model flipped its runtime choice outright. [Source: [Microsoft, hidden variables](https://developer.microsoft.com/blog/the-hidden-variables-in-your-agent-eval/)] Every rule above holds one more part of that stream constant, so the between-condition delta belongs to your surface. Neutral paths and generic identities remove semantic confounds, prompt purity keeps the rubric out of what the agent optimizes against, building and running replaces a proxy with the outcome, and repeat runs separate the delta from the non-determinism that remains.

## When this backfires

- No paired contrast exists. If your surface cannot be removed for a baseline run, the eval returns a number about the model.
- The run budget sits under the noise floor. Five runs report a 70% versus 65% split with the same confidence as a 90% versus 50% one, and only the second is resolvable ([Mustahsan and others, 2025](https://arxiv.org/abs/2512.06710v1)).
- Most criteria need exact reasoning. Version comparison, arithmetic, and schema conformance want a deterministic checker, not a judge that is wrong at an unmeasured rate.
- The rubric changes every sprint. Scores are not comparable across rubric versions without recalibration, so churn destroys the time series you were building.
- The rubric itself is the defect. Rubrics fail in eight distinct modes across reliability, content validity, and consequential validity, and the annotators who built that taxonomy reached only 0.64 mean Cohen's kappa classifying them ([RIFT, 2026](https://arxiv.org/abs/2604.01375v2)). Better criteria do not make a rubric self-validating.
- Eval design is unbudgeted. Coding assistants asked to build agent evals produced suites averaging 12 or more metrics per agent, at 30% first-run execution success without explicit evaluation knowledge ([An Empirical Study of Automating Agent Evaluation, 2026](https://arxiv.org/abs/2605.11378v2)).
- Change cadence is low. For a rarely-changing surface, production telemetry on whether the integration compiled and how often the developer intervened costs less and never goes stale.

## Example

A criterion written as a three-outcome checklist item, in the shape Microsoft uses: [Source: [Microsoft AX evals](https://developer.microsoft.com/blog/building-ax-evals-that-actually-work/)]

```text
- API keys are not hardcoded in source files
  - skipped: Application does not use API keys
  - passes: Keys loaded from environment variables or secrets manager
  - fails: Keys appear as string literals in source code
```

Compare that with "uses proper security practices." The checklist version returns the same verdict from two evaluators reading the same code, and its skip branch keeps a project that uses no API keys out of the failure column instead of depressing the score for a criterion that never applied.

## Key Takeaways

- The unit under test is your agent-facing surface with the model held fixed, so the result is a with-versus-without delta rather than a pass rate.
- Neutral workspace paths, generic identities, and a per-run environment manifest are part of the measurement, not hygiene around it.
- Never let the scoring rubric into the agent's prompt; the agent will optimize for the grader.
- Give every criterion a skip condition, or projects the criterion does not apply to will silently depress the score.
- Calibrate the judge for accuracy and consistency, then move aggregation and exact reasoning into code and tools.
- Five runs per scenario is a screening floor; close results need the 8 to 16 trials structured tasks converge at, or more.

## Related

- [Emulate Agent-Experience Changes Before Shipping](emulate-ax-changes-before-shipping.md) — the delivery mechanism for a single AX hypothesis: intercept a proposed doc, API, or MCP change locally and measure it against a baseline
- [AX/UX/DX Triad: Three Experience Layers in Agent Systems](../patterns/agent-design/ax-ux-dx-triad.md) — the design surface this eval measures, and why agent-facing output is separate from human-facing output
- [Purpose-Built Eval Suites for Model and Harness Swaps](purpose-built-eval-suites.md) — the sibling where the configuration under test is the model, prompt, and harness rather than your product
- [Meta-Evaluate the LLM Judge Before Trusting Rubric Verdicts](meta-evaluate-llm-judge-rubric-verification.md) — how far judge calibration has to go once verdicts gate a pipeline
- [Eval Awareness: Designing Evals Agents Cannot Recognize](eval-awareness.md) — the other reason eval-shaped signals in the environment change what you measure
- [Skill Evals](skill-evals.md) — the same paired with-and-without runner applied to a skill instead of a product surface
