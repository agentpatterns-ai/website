---
title: "Prescribing TDD Inside the Agent Loop (Process Theater)"
term: "TDD Inside the Agent Loop"
description: "Prescribing red-green-refactor to an agent that writes its own tests showed no quality gain over no TDD instruction, at several times the tokens."
tags:
  - testing-verification
  - workflows
  - tool-agnostic
  - anti-pattern
aliases:
  - agent-authored red-green-refactor
  - prescribing TDD to a coding agent
  - process theater in the agent loop
last_reviewed: 2026-08-13
maturity: emerging
---

# Prescribing TDD Inside the Agent Loop (Process Theater)

> Telling an agent to run red-green-refactor inside its own loop bought no measurable design or test-quality gain, at several times the tokens.

Instructing a coding agent to write a failing test, implement against it, and repeat, with no human between the steps, is a process prescription with no measured payoff. An exploratory evaluation by Birgitta Böckeler of Thoughtworks found "no clearly discernable difference based on TDD workflow versus no TDD workflow. On the contrary, more than once Opus ranked the non-TDD workflow solutions slightly higher in design and test quality" ([Böckeler, August 2026](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html)).

## The anti-pattern

Böckeler separates three ways to combine TDD with an agent, a coarser cut of the same delegation ladder as the [TDD interaction models](../../workflows/tdd-interaction-models.md): a human writes the tests and the agent implements them; the agent writes a failing test and a human reviews it before implementation; or the agent runs the full cycle alone inside its own loop. Only the third is at issue, and she calls it "by far the most common one" ([Böckeler](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html)).

Treating that third form as if it inherited the results of the first two is the mistake. The published results behind test-driven agent workflows rest on human-authored tests: supplying benchmark tests alongside the problem statement raises code-generation success rates ([Mathews & Nagappan](https://arxiv.org/abs/2402.13521)).

TDFlow reports 88.8% on SWE-Bench Lite, 27.8 points above the next best system, and is "specifically designed to solve human-written tests," naming valid reproduction-test generation as its remaining problem ([Han et al.](https://arxiv.org/abs/2510.23761v2)).

## What the evaluation found

Five batches, two TDD and two non-TDD solutions each, over small, medium and large greenfield business-logic tasks. Sonnet 4.6 wrote the solutions and scored TDD adherence from the transcripts; Opus 4.8 ranked them blind to how each was produced ([Böckeler](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html)).

Across the small and medium tasks Opus ranked the two non-TDD solutions first and second and the two TDD solutions third and fourth. A TDD solution took first place once, after the prompt gained an explicit refactor-and-design-review step, and in that batch the other TDD run under the identical prompt ranked last. On the large task TDD landed in the middle. Mutation scores showed no meaningful separation.

TDD runs cost 2.96x to 8.50x the tokens, though the article notes that multiplier tracks turn count more closely than spend and "likely overstates TDD's true dollar cost."

## Why it works

Ranking differences traced back to design timing. Reading the session traces, Opus found the non-TDD and test-first runs "always created the full design (architecture, data types, edge cases, contracts) before writing any code or tests," while under TDD instructions the design "emerged from the sum of many locally-minimal decisions and was rarely revisited," and behavior the agent did not think to test "didn't get implemented at all" ([Böckeler](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html)). Ivett Ördög, quoted in the same article, attributes the resistance to training data: models have seen finished functions with their descriptions and very few step-by-step TDD transcripts, so their internal representation maps requirements straight to code rather than encoding a process for getting there.

The remaining benefits need a person. "When the agent both writes the test and confirms it failed, a red test tells you the agent ran it and saw failure, not that the failure was for the right reason." Agents also "frequently overshot and implemented more than the current test demanded, because they had the full requirement available," so small-step YAGNI restraint does not survive either, and Kent Beck's original rationale of managing fear is "very much about managing a human's fear" ([Böckeler](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html)).

## When this backfires

Reading this as "TDD does not help agents" overshoots the evidence.

- Human-written tests are untouched. A test a person wrote and reviewed still specifies behavior independently of the implementation, the guardrail described in [test-driven agent development](../../verification/tdd-agent-development.md).
- The sample is small, judged largely by one model, and every task was greenfield business logic. Böckeler states that "the data set is of course too small to definitively conclude anything" ([Böckeler](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html)).
- Bug-fix work on an existing codebase is a different regime, where a failing reproduction test is often the only unambiguous statement of the defect. That is the shape TDFlow's results are built on.
- A single ranking per run cannot see a benefit that shows up as a shorter bad tail rather than a higher mean.

## Mitigations

- Monitor outcomes instead of prescribing the process. Böckeler moved to [mutation testing as the regression-quality sensor](../../verification/mutation-testing-quality-gate.md), with [static analysis and periodic modularity reviews](https://martinfowler.com/articles/sensors-for-coding-agents.html) as the refactoring triggers.
- Keep the human where the friction is: specify the tests yourself, or review the failing test before implementation.
- Budget prompt maintenance. TDD instructions are "an uphill battle against the training data" ([Böckeler](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html)), so expect re-tuning on every model change.

## Key Takeaways

- Agent-run red-green-refactor produced no measurable design, test-quality or mutation-score gain over no TDD instruction in a five-batch exploratory evaluation, and ranked slightly worse on the small and medium tasks.
- The mechanism is design timing: TDD instructions suppress the up-front architecture pass the higher-ranked runs made, leaving the design to whatever the first test locked in.
- Red-green, YAGNI restraint and managing fear all depend on a human in the loop; removing the human keeps the ritual and drops the payoff.
- The finding does not extend to human-authored tests, to bug-fix work on existing code, or past a small greenfield sample judged by one model.
- Substitute sensors for prescriptions: mutation score for regression quality, static analysis and modularity review for refactoring triggers.

## Related

- [Test-Driven Agent Development](../../verification/tdd-agent-development.md) — the human-authored-tests form of the workflow, which this evidence does not touch
- [Red-Green-Refactor with Agents](../../verification/red-green-refactor-agents.md) — running the cycle as separate human-gated invocations rather than inside one agent loop
- [Mutation Testing as a Quality Gate](../../verification/mutation-testing-quality-gate.md) — the outcome sensor offered as the replacement for prescribing the process
- [TDD Interaction Models](../../workflows/tdd-interaction-models.md) — the delegation ladder this sits at the bottom of, comparing who writes the test rather than whether the process is prescribed
- [Generating Tests From Agent-Written Code](code-first-test-oracle-bias.md) — the failure mode that survives when one agent authors both halves
- [Assertion-Free Test Theater in Agent-Authored Patches](assertion-free-test-theater.md) — agent-written tests that run green while carrying no real oracle signal
