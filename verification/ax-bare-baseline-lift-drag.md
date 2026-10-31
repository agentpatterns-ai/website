---
title: "Measure Agent Experience Against a Bare Baseline"
term: "Bare Baseline"
description: "Score every agent-friendly change against the same tasks run with no extensions, report task cost beside quality, and keep the conclusion scoped to the agent profile you measured it on."
tags:
  - testing-verification
  - evals
  - cost-performance
  - tool-agnostic
aliases:
  - lift and drag
  - bare-baseline AX measurement
  - propensity and efficacy
last_reviewed: 2026-10-10
maturity: emerging
---

# Measure Agent Experience Against a Bare Baseline

> Run the same tasks with no extensions loaded, then score every change against that baseline on quality and on task cost.

An Agent Experience figure is readable once you know three things about it: whether the run measured propensity or efficacy, what it cost beside what it scored, and the agent profile it ran on. Microsoft's Agent Experience guidance says to record all three and to compare every change against a bare baseline, "the same tasks run with no extensions, just the harness and the model" ([Mastykarz, *What is Agent Experience (AX)?*](https://developer.microsoft.com/blog/what-is-agent-experience-ax)).

Read the published figures as screening results. Each comes from five runs per scenario, fewer trials than an agentic eval score needs for its measurement reliability to converge ([Mustahsan and others, arXiv:2512.06710v1](https://arxiv.org/abs/2512.06710v1)), and all of them are one vendor measuring its own technology in one harness family. The post concedes the limit: "Each result holds for the scenarios and agent profile we measured." ([Mastykarz](https://developer.microsoft.com/blog/what-is-agent-experience-ax)) So run your own tasks rather than import the numbers.

## Propensity and efficacy

Naming your product in the task is what separates the two questions. Propensity asks whether the agent finds and chooses your technology, so the task names no product and you watch what it reaches for. Efficacy asks whether it uses your technology correctly once it has, so you name the product and check whether it calls your current API or a deprecated one. The post's own recap is that "propensity tells you whether agents reach your technology. Efficacy tells you what happens when they do." ([Mastykarz](https://developer.microsoft.com/blog/what-is-agent-experience-ax))

One score averaged over both adds a discovery result to a correctness result and attributes the sum to neither. [Generative engine optimization](../geo/what-is-geo.md) sits on the propensity half and stops there, asking whether AI search mentions your product rather than whether the agent used it correctly ([Mastykarz](https://developer.microsoft.com/blog/what-is-agent-experience-ax)).

## Lift and drag, with cost in the same row

Against the bare baseline a change either improves outcomes, which is lift, or leaves them the same or worse, which is drag. Task cost is the second column and it is not optional: it counts "every token at its price, not just the token count", and the rule is to "report it next to quality, every time" ([Mastykarz](https://developer.microsoft.com/blog/what-is-agent-experience-ax)). Only paired numbers surface lift too expensive to keep. A JSON input mode for a CLI landed there at 4x to 11x more per task with no correctness gain ([CLI JSON payload rewrite](../patterns/anti-patterns/cli-json-payload-rewrite.md)), as did a model upgrade costing 3.7x more per run on code upgrades despite cheaper tokens ([cheaper per token, costlier per task](../patterns/anti-patterns/cheaper-per-token-costlier-per-task.md)).

The agent profile is the scoping unit: operating system, harness, model and its settings, and the extensions loaded. "A result belongs to the profile it was measured with" ([Mastykarz](https://developer.microsoft.com/blog/what-is-agent-experience-ax)). Record it with the number and re-run when any part of it moves. The same dependence holds when the unit under test is a skill, where a measured gain belongs to one [model and harness pair](configuration-specific-skill-utility.md).

## Fix the surface the trail points at

Order your fixes by who they reach. Docs and interfaces reach every agent that fetches them, because an agent reading them while it works "sees your update on its very next run", while an extension "only helps developers who install it" ([Mastykarz](https://developer.microsoft.com/blog/what-is-agent-experience-ax)). So read the trail, find the surface the agent already opened, and fix that before writing a skill.

The SPFx upgrade case is the worked version. Instructing the agent to use CLI for Microsoft 365 raised configuration correctness from 30 of 80 to 75 of 80, and that instruction "only works for developers who either know of the CLI or who install the skill that carries it" ([Mastykarz](https://developer.microsoft.com/blog/what-is-agent-experience-ax)). Adding a second documentation source instead of fixing the first added no meaningful lift: the context7 MCP server's "tools didn't load into the agent's context at all" in 3 of 5 runs and "were available but never invoked" in the other 2 ([*Behind SPFx Dev Skills*](https://devblogs.microsoft.com/microsoft365dev/behind-spfx-dev-skills-testing-what-agents-know-and-fixing-what-they-miss/)).

Editing the release notes was not one edit. A tip naming the CLI was already there, and the agents kept their manual plan even after the exact command was added. Moving the tip "made no difference", and removing the linked migration guide "hurt manual runs without reliably increasing CLI adoption". A warning is what flipped it: "In the baseline, no run used the CLI. With the warning in place and the detailed migration link removed, agents in our simulations discovered and used the CLI on their own." Restoring the step-by-step guide sent them back to manual, so the team rewrote it to explain what changes and point readers at the CLI to apply it. The team shipped both halves, sending the docs fixes upstream and still releasing the skill ([*Behind SPFx Dev Skills*](https://devblogs.microsoft.com/microsoft365dev/behind-spfx-dev-skills-testing-what-agents-know-and-fixing-what-they-miss/)).

## Why it works

A bare baseline turns a score into a difference, and a difference can be attributed. The other three rules each close off a rival explanation for it. An agent's output is a function of its whole input stream, so an unrecorded OS, harness build, or loaded extension is a competing cause, which the profile records. Naming the product decides which behavior the run measures. Quality and spend come out of the same run and can move in opposite directions, which is why cost sits in the same row.

The ordering rule runs on distribution rather than on agent behavior. A docs or interface fix is retrieved by whoever retrieves it and a skill is loaded by whoever installed it, so the same correctness gain reaches different populations depending on where you put it. The trail is what tells you where to try: Microsoft went at the release notes because the agent's trail showed it fetching them unprompted ([Mastykarz](https://developer.microsoft.com/blog/what-is-agent-experience-ax)). Which edit would work was a separate question: "Several attempts didn't work." ([*Behind SPFx Dev Skills*](https://devblogs.microsoft.com/microsoft365dev/behind-spfx-dev-skills-testing-what-agents-know-and-fixing-what-they-miss/))

## When this backfires

- You do not own the surface the trail points at. Where it belongs to a platform team or a third-party aggregator, the ordering rule names a fix you cannot apply, and the fix still has to keep serving human readers.
- The agent never loads the surface. Availability is not use, as the context7 result shows, so content the agent does not retrieve is unmeasurable work.
- Your run budget cannot resolve the comparison. Out of five runs a pass rate can only come out as 0, 20, 40, 60, 80, or 100 percent, where the intraclass correlation of an agentic eval score converges "by n=8–16 trials for structured tasks and n≥32 for complex reasoning" ([Mustahsan and others, arXiv:2512.06710v1](https://arxiv.org/abs/2512.06710v1)).
- The edit is advisory. A tip pointing at the right tool got 1 of 5 runs to use it where a warning naming the failing approach got 5 of 5 ([Mastykarz](https://developer.microsoft.com/blog/what-is-agent-experience-ax)), so an edit that leaves the agent's existing plan uncontradicted returns a null you will misread as evidence that docs do not move agents.
- You assumed the agent reads reference documentation. In 557 instrumented sessions, API reference drew 1.3% of 3,033 documentation interactions against 60.5% for instruction files and working notes. API references accounted for "only 2.3% of observable repository-local consultations in our data" ([Gao and Chen, arXiv:2608.20195v1](https://arxiv.org/abs/2608.20195v1)). Your trail picks the surface, not a published [read-count distribution](../instructions/documentation-read-counts.md).
- The profile churns faster than you can measure it. Where the harness ships weekly, a conclusion can expire before the runs behind it finish.

## Example

One scenario, read with the three scoping facts attached:

```text
Scenario: upgrade an SPFx project
Profile (stated for the baseline and CLI-instruction runs):
  Windows, GitHub Copilot Chat, Claude Sonnet 4.6, 5 runs

bare baseline              configuration correctness 30/80; no run used the CLI
+ CLI instruction          75/80                  reaches developers who install it
+ rewritten release notes  agents chose the CLI    reaches every agent that fetches them
```

Both interventions produce lift, and only one reaches developers who install nothing. Report the 75 of 80 without the reach column and you lose the finding that decided what shipped. The profile line also shows the rule biting its own source: the write-up states that profile for the baseline and instruction runs and does not restate one for the documentation tests, so the third row is not strictly profile-matched to the first two ([*Behind SPFx Dev Skills*](https://devblogs.microsoft.com/microsoft365dev/behind-spfx-dev-skills-testing-what-agents-know-and-fixing-what-they-miss/)).

## Key Takeaways

- Name the question before reading the number. A score that mixes tasks naming your product with tasks that do not is a discovery result and a correctness result added together.
- A result with no task cost beside it cannot distinguish lift from lift you will not keep paying for.
- Write the agent profile next to the score: OS, harness, model settings, loaded extensions. Treat the score as expired the moment any of them changes.
- Five runs per scenario screens out the obvious and resolves nothing close, so size the budget to the gap that would change your decision.
- Order fixes by reach rather than by effort, and let the trail pick the surface. A documentation fix the agent never retrieves reaches nobody, which is the same outcome as a skill nobody installs.
- Expect the documentation fix to take several attempts and to regress something on the way. One edit that moves an agent is not evidence that editing docs is easy.

## Related

- [AX Evals: Measure the Agent-Facing Surface, Not the Model](ax-evals-agent-facing-surface.md) — How to build the eval so the with-versus-without delta is attributable: criterion design, judge calibration, and the environment controls behind the profile.
- [Emulate Agent-Experience Changes Before Shipping](emulate-ax-changes-before-shipping.md) — The delivery mechanism for one hypothesis, intercepting a proposed doc or API change locally so the baseline comparison costs minutes.
- [Skill Utility Depends on Model and Harness Configuration](configuration-specific-skill-utility.md) — The same scoping argument where the unit under test is a skill, measured across nine model and harness pairs.
- [Cheaper-Per-Token Model Upgrades That Cost More Per Task](../patterns/anti-patterns/cheaper-per-token-costlier-per-task.md) — The counterexample that makes task cost a required column rather than a nice-to-have.
- [Documentation Read Counts Measure Retrievability, Not Value](../instructions/documentation-read-counts.md) — What agents actually open, and why a read-count distribution is not a demand signal for which surface to fix.
- [Search-Set Harness Gain as Capability Evidence](../patterns/anti-patterns/search-set-gain-as-capability-evidence.md) — What the cost column is for: raising the bare baseline to the tuned harness's inference budget turns part of a reported gain into something the baseline already had.
