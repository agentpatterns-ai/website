---
title: "Running an Agent Experience Evaluation From Gates to Fixes"
term: "AX Evaluation Workflow"
description: "Run an agent experience evaluation as stacked gates, trajectory triage, failure attribution, and a source-first fix, and learn what five runs per scenario can and cannot show."
tags:
  - workflows
  - agent-design
  - tool-agnostic
aliases:
  - AX evaluation end to end
  - agent experience evaluation workflow
last_reviewed: 2026-10-15
maturity: emerging
---

# Running an Agent Experience Evaluation From Gates to Fixes

> An agent experience (AX) evaluation runs in four steps: stack gates, triage trajectories, attribute each failure, and fix the source before writing a skill.

An AX evaluation measures whether a coding agent succeeds with your library, extension, or docs. This page orders the steps the Microsoft AX Practitioner Playbook describes and covers four the corpus lacks: gate order, trajectory triage, failure attribution, and the rules for a stop-gap. Criteria, judge calibration, prompt purity, and environment contamination stay on [AX Evals](../verification/ax-evals-agent-facing-surface.md). Testing a single change before it ships stays on [Emulate AX Changes](../verification/emulate-ax-changes-before-shipping.md). The layers a failure can live in stay on [The AX Stack](../patterns/agent-design/ax-stack-layered-model.md).

Every playbook outcome figure below comes from Microsoft DevRel, which evaluated Microsoft technologies with its own tool.

## When to use it

Use the full method when you own a surface an agent reads or calls, can add and remove it, and must defend a number to another team or track regressions over months.

If you only need to know what to fix next, reading ten agent transcripts by hand and fixing the obvious doc errors gets most of the value for far less cost. One small doc fix is also cheaper to ship and watch than to measure.

## Why scores mislead

The playbook names two ways an evaluation misleads. In one, evaluations "report perfect scores for code that never compiled, because nobody actually built it." In the other, a "used Platform X" check passed whether or not the agent used Platform X, because it matched the word and never checked the meaning. The playbook adds that a confident wrong result "is worse than no result, because you'll act on it." [Source: [playbook chapter 2](https://github.com/microsoft/scope/blob/283d14c52821f7f97b21ccc9c03378e9fd50601a/docs/ax-playbook/ax-practitioner/references/playbook/ch02-the-evaluation-model.md)] The four steps below remove those rival explanations one at a time.

## The four steps

### Step 1: stack the gates

Gates are mechanical, binary checks. They stack, so each runs only if the previous one passed. [Source: [chapter 2](https://github.com/microsoft/scope/blob/283d14c52821f7f97b21ccc9c03378e9fd50601a/docs/ax-playbook/ax-practitioner/references/playbook/ch02-the-evaluation-model.md)]

1. Prerequisite: did the agent pick the right technology? If you asked for Cosmos DB and it built on MongoDB, nothing after this is worth measuring.
2. Build: does the code compile?
3. Test: do its tests pass, if it has any?
4. Run: does the app start?
5. Deploy: does it deploy, when deployment is part of the job?

Record cost with every score. The playbook says: "A profile that lifts quality at three times the price forces a real decision, and you can't have that conversation if you only ever looked at the score." [Source: chapter 2]

### Step 2: triage the trajectories

The readout lists which criterion failed. The playbook puts the split this way: "The readout tells you what failed. The trajectories tell you why." The readout reports a failed criterion without saying which cause produced it, and the trajectory separates the causes. [Source: [chapter 9](https://github.com/microsoft/scope/blob/283d14c52821f7f97b21ccc9c03378e9fd50601a/docs/ax-playbook/ax-practitioner/references/playbook/ch09-investigating-agent-trajectories.md)]

| What the trajectory shows | Stage | First surface to inspect | Kind of fix |
|---|---|---|---|
| The extension never loads | Discovery failure | Packaging, registration, startup, and harness limits | Infrastructure |
| The extension loads and the agent does not use it | Lack of invocation | Tool or skill name, description, and vocabulary | Better tool descriptions or vocabulary alignment |
| The agent uses the extension and applies it wrongly | Application failure | Returned content, response shape, docs, and instructions | Better content or plan-invalidation language in your docs |

[Source: [chapter 9](https://github.com/microsoft/scope/blob/283d14c52821f7f97b21ccc9c03378e9fd50601a/docs/ax-playbook/ax-practitioner/references/playbook/ch09-investigating-agent-trajectories.md) for the stages and fixes, [chapter 10](https://github.com/microsoft/scope/blob/283d14c52821f7f97b21ccc9c03378e9fd50601a/docs/ax-playbook/ax-practitioner/references/playbook/ch10-common-failure-patterns.md) for the surfaces]

The surface column says where to look first. In the playbook's words: "The pattern tells you where to investigate first. It doesn't prove the fix, but it narrows the search." [Source: chapter 10]

Aim first at results that split across runs, such as the 2/5 case the playbook describes. "Contradictory behavior tells you the agent's decision is weakly motivated," and "a small content change can tip a 2/5 result to 5/5 because the agent was already close to the right decision." [Source: chapter 9]

### Step 3: attribute the failure to a source

Name what caused the failure before you design a fix: the docs, the extension, the training data, or the agent. The playbook calls stale training data with no extension correcting it "The most common root cause." [Source: chapter 9]

### Step 4: fix the source first and bound any stop-gap

The playbook states the rule as: "Don't band-aid a doc problem with a skill when you could fix the doc." A new skill should be the last resort "because the improvement then depends on developers finding, installing, and updating it." [Source: chapter 9]

Treat each fix as a hypothesis. The playbook says to change one thing, rerun the same scenarios and profiles, and compare against the original baseline. If the outcome does not improve, "don't ship it just because the new wording sounds better." [Source: [chapter 11](https://github.com/microsoft/scope/blob/283d14c52821f7f97b21ccc9c03378e9fd50601a/docs/ax-playbook/ax-practitioner/references/playbook/ch11-turning-findings-into-improvements.md)] Change one surface at a time, "Otherwise, you won't know which change caused the result." [Source: chapter 10]

When you ship a bridge because the source owner has not fixed it yet, chapter 11 sets four rules:

- "Label it clearly as independent and don't imply endorsement."
- "State which gap it addresses and link to the supporting evidence."
- "Name who maintains it and how updates will be handled."
- "Define the condition for retiring it when the source is fixed."

The last rule keeps a stop-gap from outliving its cause. Scope the claim as well: "Results belong to the tested scenario, profiles, versions, and point in time." [Source: chapter 11]

## Example

The playbook's own case is an SPFx upgrade evaluation that targeted v1.22.0. "The bare profile installed the wrong version in 4 out of 5 runs." The agent fetched the migration guide, read npm commands hardcoded to v1.22.1, and followed them instead of the version the user asked for. [Source: [chapter 9](https://github.com/microsoft/scope/blob/283d14c52821f7f97b21ccc9c03378e9fd50601a/docs/ax-playbook/ax-practitioner/references/playbook/ch09-investigating-agent-trajectories.md)]

The readout for that evaluation shows a failed version criterion. Only the trajectory shows the cause, a hardcoded version in a doc the agent trusted. That points step 3 at the docs and step 4 at the migration guide, not at a new skill.

## Why it works

Each step removes one rival explanation for a score. A gate replaces an assumed outcome with a mechanical one, so a perfect score cannot come from code that never compiled. Trajectories separate three causes that look identical in the readout. Anthropic gives the same reason for reading transcripts: a failed task's transcript shows whether the agent made a real mistake or the graders rejected a valid solution ([Anthropic](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)).

Repeat runs separate a pattern from sampling noise. A study of agent evaluation variance recommends statistical power analysis to set the number of runs ([Bjarnason and others](https://arxiv.org/abs/2602.07150v3)).

## When this backfires

- Small differences. The playbook advises at least five runs per scenario and profile, then concedes: "While five runs isn't statistically significant, in our experience, it allows you to strike balance between evaluations not being overly expensive and starting to see results group and can discern obvious failures." [Source: [chapter 2](https://github.com/microsoft/scope/blob/283d14c52821f7f97b21ccc9c03378e9fd50601a/docs/ax-playbook/ax-practitioner/references/playbook/ch02-the-evaluation-model.md)] An independent study of SWE-Bench-Verified found that single-run pass@1 estimates vary by 2.2 to 6.0 percentage points depending on which run is selected, so with five runs per scenario a gap of one run can come from run-to-run variance ([Bjarnason and others](https://arxiv.org/abs/2602.07150v3)).
- The judge is a language model. Calibrated criteria still sit on a judge with known weaknesses, including "a tendency toward leniency" ([Judging the Judges](https://arxiv.org/abs/2406.12624v6)). The AX Evals page covers the rule that a judge change breaks comparability.
- Self-evaluation. Microsoft reports "dozens of shipped fixes to docs and agent extensions, including 46 improvements to the Azure Cosmos DB Agent Kit" ([Microsoft blog](https://developer.microsoft.com/blog/introducing-the-agent-experience-ax-practitioner-playbook/)). The source reports no lift per fix.
- The evaluation system is the vendor's. The playbook says the method does not depend on a specific system, and the same chapter promotes the authors' own tool. [Source: [chapter 7](https://github.com/microsoft/scope/blob/283d14c52821f7f97b21ccc9c03378e9fd50601a/docs/ax-playbook/ax-practitioner/references/playbook/ch07-running-evals-and-generating-the-readout.md)]
- The owner does not act. The method ends at bringing evidence to the team that owns the surface, so a recorded finding can stay unfixed.

## Key Takeaways

- Stack the gates in order: prerequisite, build, test, run, deploy. Each runs only if the one before passed.
- Read trajectories as well as the readout. They separate a failure to load, a failure to invoke, and a failure to apply.
- Name the source of a failure before you fix it. The playbook calls stale training data the most common root cause.
- Fix the doc before you write a skill, and give any bridge a maintainer and a retirement condition.
- Five runs find obvious failures. By the playbook's own account, they are not statistically significant.
- Every playbook outcome figure is Microsoft reporting on its own work with its own tool.

## Related

- [AX Evals: Measure the Agent-Facing Surface, Not the Model](../verification/ax-evals-agent-facing-surface.md) — criteria, judge calibration, prompt purity, and environment contamination
- [Emulate Agent-Experience Changes Before Shipping](../verification/emulate-ax-changes-before-shipping.md) — test a proposed fix as a hypothesis before it ships
- [The AX Stack](../patterns/agent-design/ax-stack-layered-model.md) — the layers a failure can live in and the three extension failure modes
- [Continuous Agent Improvement](continuous-agent-improvement.md) — the observe, update, and verify loop for agent configuration
