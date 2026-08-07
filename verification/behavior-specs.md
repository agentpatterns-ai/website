---
title: "Behavior Specs: Grading the Trajectory, Not the Result"
term: "Behavior Specs"
description: "Declare expected agent conduct in a BEHAVIOR.md file and grade whole trajectories against it — process supervision for when outcomes resist verification."
tags:
  - testing-verification
  - evals
  - agent-design
  - tool-agnostic
aliases:
  - BEHAVIOR.md
  - agent behavior spec
  - trajectory behavior specification
last_reviewed: 2026-08-05
maturity: emerging
---

# Behavior Specs: Grading the Trajectory, Not the Result

> A behavior spec is never shown to the agent. It exists so a judge can grade whether a recorded trajectory followed it.

A behavior spec is a Markdown file that states the conduct you expect from an agent across many runs, written so a reviewer or an LLM judge can read a recorded trajectory and decide whether the behavior happened. Braintrust and Basis published the format as an open standard on 29 July 2026 ([Braintrust](https://www.braintrust.dev/blog/behavior-specs)), with the reference implementation released under Apache 2.0 ([braintrustdata/agentbehavior](https://github.com/braintrustdata/agentbehavior)). The file lives at `.agents/behaviors/<name>/BEHAVIOR.md` and carries YAML frontmatter with two required fields, `name` and `description`, plus a free-form Markdown body ([agentbehavior.dev](https://agentbehavior.dev)).

## When a behavior spec earns its cost

The evidence for this format is one vendor announcement and one design partner, so check your situation against three conditions before adopting it.

The agent has to run long. The motivating case is an accounting agent that completes a tax return unattended, making hundreds of decisions in a single trajectory ([Braintrust](https://www.braintrust.dev/blog/behavior-specs)). On a three-turn agent the trajectory holds little that an outcome check would miss.

The outcome has to resist verification. Where the result is objectively checkable, outcome supervision is the cheaper instrument: DeepMind found that "pure outcome-based supervision produces similar final-answer error rates with less label supervision" ([Uesato et al., 2022](https://arxiv.org/abs/2211.14275v1)). Process supervision buys correctness of reasoning, at a higher supervision cost.

You have to be able to judge traces at scale. A spec you cannot grade is a document. The authors call judging "a platform problem" and ship a judge prompt alongside the standard, but the grading itself is your bill to pay ([Braintrust](https://www.braintrust.dev/blog/behavior-specs)).

## What separates it from the files the agent reads

Your `AGENTS.md`, skills, and tool descriptions all shape behavior, and the agent reads every one of them. A behavior spec sits on the other side of that line. The standard is explicit: "It is not a prompt and it is never shown to the agent. A behavior spec defines the intended behavior so you can align on it and measure against it" ([Braintrust](https://www.braintrust.dev/blog/behavior-specs)).

That split creates a precedence rule with teeth. When a spec and the runtime context disagree, the spec wins, and the team revises prompts, tools, or context until the agent complies ([Braintrust](https://www.braintrust.dev/blog/behavior-specs)). The standing eval then catches drift, which is what stops the file becoming another stale doc.

The body is free-form, with six recommended labels: Intent, Evidence, Decision, Execution, Recovery, and Failure modes ([agentbehavior.dev](https://agentbehavior.dev)). Write in the second-person imperative so a reader can hold a trajectory against the text and answer yes or no.

## Why it works

A single outcome score over a long trajectory is a credit-assignment failure. It reports that the run was wrong without saying which of hundreds of decisions was wrong, so it cannot direct a fix. Grading each declared behavior separately restores that localization. [Uesato et al. (2022)](https://arxiv.org/abs/2211.14275v1) isolate the effect: process-based feedback cut reasoning error among final-answer-correct solutions from 14.0% to 3.4%, exactly the case of a right answer reached the wrong way. [Lightman et al. (2023)](https://arxiv.org/abs/2305.20050v1) trained a reward model on 800,000 step-level human labels and solved 78% of a representative MATH test subset, beating outcome supervision. Rubric-based process rewards carry into long-horizon software agents for the same stated reason, that sparse outcome rewards give no dense signal across a long run ([Han et al., 2026](https://arxiv.org/abs/2604.14820v1)).

Treat that transfer carefully. The research measures training-time reward models over short reasoning chains; behavior specs judge hour-long trajectories after the fact. The announcement concedes the gap, putting a modern trajectory at four to five orders of magnitude more compute than a 2023 math problem ([Braintrust](https://www.braintrust.dev/blog/behavior-specs)).

## When this backfires

- Short trajectories. The format assumes hundreds of decisions per run. Below that, an outcome check covers the same ground and the judging cost buys nothing.
- Verifiable outcomes. If tests pass or the number reconciles, you already have a cheap oracle. See [Grade Agent Outcomes, Not Execution Paths](grade-agent-outcomes.md) for the case that end-state grading is the default.
- An uncalibrated judge. A `true`/`false`/`NA` verdict is only actionable if the judge agrees with humans on the same traces. Rubric-graded systems are documented as exploitable through latent judge bias ([Wang et al., 2026](https://arxiv.org/abs/2606.04923)), and process labels carry two-sided noise, "false positives that reward incorrect steps and false negatives that penalize correct ones" ([Xie et al., 2026](https://arxiv.org/abs/2601.12748v1)). Measure judge agreement first; [Meta-Evaluate the LLM Judge](meta-evaluate-llm-judge-rubric-verification.md) covers how.
- Spec sprawl. A production agent encodes hundreds of behaviors. The authors warn that writing them all down and keeping them synchronized with the runtime context is unmanageable, and that the file stays sparse on purpose ([Braintrust](https://www.braintrust.dev/blog/behavior-specs)). Elevate only what you will test continuously.
- Specs the model has outgrown. The standard tells teams to retire a spec once the model reliably shows the behavior unaided, and expects prescription to shrink over time ([Braintrust](https://www.braintrust.dev/blog/behavior-specs)). A spec that returns `true` on every trajectory is pure grading cost.
- Optimizing against the grader. The spec is hidden from the agent, which closes the direct hacking route. Teams still tune prompts and tools until the judge says `true`, so the usual proxy-metric caution applies ([Anti-Reward-Hacking](anti-reward-hacking.md)).

## Example

A published spec from the standard, judging whether an agent validated a slide deck before returning it ([Braintrust](https://www.braintrust.dev/blog/behavior-specs)):

```markdown
---
name: validate-rendered-deck
description: Render the current PowerPoint before delivery, inspect it for visual issues, and revalidate after fixes.
---

## Validate the rendered deck before returning it

**Intent:** Ensure the deck the user receives is visually usable, not merely
valid as PowerPoint code.

**Evidence:** Before returning a created or edited PowerPoint, the agent
should use the current saved version of the deck and its rendered slide
images. A render made before the most recent edit is not evidence about the
deck now being returned.

**Decision:** The agent should determine whether the current rendered deck
has formatting, layout, readability, or other visible presentation issues
that make it unsuitable to return.

**Execution:** The agent should render the current deck to images and inspect
those images before returning it to the user.

**Recovery:** If the inspection finds an issue the agent can fix, it should
fix the deck, render the updated version again, and inspect that new render
before returning it. If it cannot render or inspect the deck, it should not
represent the deck as visually validated.

**Failure modes:** Returning an unrendered deck; relying on a render from
before the latest edit; fixing a visual issue without re-rendering; missing a
formatting problem that code-level checks cannot reveal.
```

Each spec in a file is graded on its own, with one of three verdicts. A run where the agent answered a question without touching a deck scores `NA`. A run where it rendered, inspected, and fixed a layout issue scores `true`. A run where it edited the deck and returned it unrendered scores `false` ([Braintrust](https://www.braintrust.dev/blog/behavior-specs)).

## Key Takeaways

- Judging is the expensive half, and the standard does not supply it. Price the grading before you write the first spec.
- Sparseness is the maintenance strategy: few specs, each carrying a standing eval, retired once the model no longer needs them.
- The precedence rule is what keeps a spec honest. If you are not willing to change the implementation when the spec and the runtime disagree, you have written documentation instead.
- Independent evidence supports process supervision as an idea. Nobody outside the two publishing teams has yet evaluated this format.

## Related

- [Grade Agent Outcomes, Not Execution Paths](grade-agent-outcomes.md) — the outcome-first default that behavior specs supplement rather than replace
- [Behavioral Testing for Agents](behavioral-testing-agents.md) — testing decision quality and end-state when execution paths legitimately vary
- [Meta-Evaluate the LLM Judge Before Trusting Rubric Verdicts](meta-evaluate-llm-judge-rubric-verification.md) — measuring judge error before scaling a rubric across production traces
- [Anti-Reward-Hacking: Rubrics That Resist Gaming](anti-reward-hacking.md) — designing graded signals that survive being optimized against
- [Dual Executable Specifications for Long-Horizon Features](dual-executable-specifications.md) — the executable, output-keyed counterpart to a judge-read behavior spec
