---
title: "Building Agent Eval Environments With a World Spec"
term: "World Spec"
description: "Hold the domain knowledge every eval task shares in one versioned world spec so task construction parallelizes, worth doing for a dataset rather than a handful of cases and only with an audit budget for what the pipeline emits."
tags:
  - testing-verification
  - evals
  - tool-agnostic
aliases:
  - eval world spec
  - task spec pipeline
  - spec-to-task eval construction
last_reviewed: 2026-08-26
maturity: emerging
---

# Building Agent Eval Environments With a World Spec

> A world spec holds the domain knowledge every eval task shares, so building the next task stops meaning rediscovering the domain.

A world spec is a versioned file of project-wide knowledge that every task in an eval dataset draws on: schemas for the services the environment must mock, scripts for parsing traces, and which grader type suits which kind of output. It sits above per-task specs in a two-step construction pipeline. LangChain describes the split as a first step that "takes traces, code, and/or human input to build a detailed spec" and a second that "takes that spec and creates an eval task and an environment for that task" ([Trivedy and Hollon, LangChain](https://www.langchain.com/blog/building-agent-environments-and-tasks)).

[Agent-authored eval suites](agent-authored-eval-suites.md) covers getting one runnable task out of a repository and its traces. The world spec is what stops you paying that discovery cost again on every task after it.

## Conditions that make it worth building

Three have to hold before the artifact returns its cost.

- You need many tasks, not a handful. LangChain builds the world spec while creating the first task and validates it on the next two: "you may even want to do this for the first two or three tasks to make sure the world spec is truly complete" ([Trivedy and Hollon](https://www.langchain.com/blog/building-agent-environments-and-tasks)). Three to five tasks never amortizes that setup — write them directly and size the suite to the decision, as in [purpose-built eval suites](purpose-built-eval-suites.md).
- You have production traces. They supply the task patterns and the observed tool behavior; named world-spec contents include "common questions that users are asking mined from existing agent traces" ([Trivedy and Hollon](https://www.langchain.com/blog/building-agent-environments-and-tasks)).
- You have budget to audit every task the pipeline emits. That is what decides whether the score means anything, and it is priced below.

## What lives where

The dividing rule: world-spec knowledge "is NOT specific to a single task - if it was, it would live in the task spec" ([Trivedy and Hollon](https://www.langchain.com/blog/building-agent-environments-and-tasks)).

| Artifact | Holds | Examples from LangChain's internal benchmarks |
|---|---|---|
| World spec | Knowledge shared across the whole dataset | APIs and schemas for backend services to mock, such as Salesforce and Notion; scripts for generating environment data; the standard scoring function used for all cases |
| Task spec | One task, in natural-language markdown | What the environment looks like, what the inputs should be, how the outputs should be scored |
| Task | The runnable artifact | An input, an environment, and a test script, generated from the two specs above |

Anything constant moves up. For a general QA chatbot the environment "may always be the same (it's just the inputs/outputs that change)", in which case it "could be consolidated in the 'world spec' and shared across tasks" ([Trivedy and Hollon](https://www.langchain.com/blog/building-agent-environments-and-tasks)). That is a design option to check against your own agent, not a property of QA chatbots.

## Three controls that keep generated tasks honest

Run each task with a real agent and read the trajectory. LangChain uses this to find "flaws in environment design such as overly specific instructions or leaky abstractions", with a concrete tell: "a poorly written table entry saying 'Answer placeholder'" ([Trivedy and Hollon](https://www.langchain.com/blog/building-agent-environments-and-tasks)). Chasing those defects pays on its own — on the Reward Hacking Benchmark, "simple environmental hardening reduces exploit rates by 5.7 percentage points (87.7% relative)" without lowering honest task success ([arxiv.org/abs/2605.02964v1](https://arxiv.org/abs/2605.02964v1)).

Calibrate difficulty against two model tiers. That tells you "whether tasks are too easy or too hard for a certain tier of model or if the task is broken for a stronger model because of a reward hack" ([Trivedy and Hollon](https://www.langchain.com/blog/building-agent-environments-and-tasks)). Read the trajectories while you do it: a pass rate cannot separate a hard task solved from an easy shortcut taken, and the same benchmark found models near a 0% exploit rate on standard tasks show elevated rates on harder variants ([arxiv.org/abs/2605.02964v1](https://arxiv.org/abs/2605.02964v1)).

Name the data-generation method in the world spec, because "Agents are bad at knowing what method to use for generating different types of data" — rubric-guided LLMs for free text, sqlite scripts with a fixed schema for tabular ([Trivedy and Hollon](https://www.langchain.com/blog/building-agent-environments-and-tasks)).

## Why it works

Eval construction carries two costs with different shapes, and the spec is the seam between them. Deciding what a task should measure is a preference question needing human rounds; building the environment, seeding data, and writing the grader is mechanical. Writing the decision down as markdown first lets each be paid in its own currency: the separation "allows you to create many of different specs, centralize the human review process there, and then parallelize building them", and "It's much easier for humans review a markdown spec rather than the raw code and data of a task" ([Trivedy and Hollon](https://www.langchain.com/blog/building-agent-environments-and-tasks)).

The world spec removes the other cost driver: rediscovering the same domain facts on every task. Structuring a generator's inputs beats asking it for cases outright — unstructured prompting gives "generic, repetitive outputs" where a dimension-structured approach "produces far better synthetic data for testing LLM applications" ([evals FAQ](https://hamel.dev/blog/posts/evals-faq/)).

## When this backfires

- You audit less than you generate. The scaling prompt asks for ten task specs at once, and construction defects already dominate hand-built benchmarks: an audit of 168 found ambiguous design, environment conflicts, and wrong ground truths in over 25.7% of tasks ([Wang et al.](https://arxiv.org/abs/2605.26079v2)), and SWE-bench Verified "uses insufficient test cases, while TAU-bench counts empty responses as successful", shifting measured performance "by up to 100% in relative terms" ([Zhu et al.](https://arxiv.org/abs/2507.02825v5)). Spec mediation does not lower that rate. It raises the rate at which you accumulate tasks carrying it.
- You have no traces. Specs then derive from the implementation alone, and the tasks certify whatever the agent currently does as correct. Mine real failures instead, via [incident-to-eval synthesis](incident-to-eval-synthesis.md).
- Your domain is one where synthetic data misleads. Husain and Shankar name five: specialized document structure, low-resource languages and dialects, cases where you cannot verify a sample is realistic, high-stakes domains, and underrepresented user groups ([evals FAQ](https://hamel.dev/blog/posts/evals-faq/)).
- You expect the tasks to come out hard. They will not: "agents tend to create tasks that are too easy", and calibrating difficulty "usually requires running each task multiple times, reviewing the trajectories, and asking the agent to make the task easier or harder" ([Trivedy and Hollon](https://www.langchain.com/blog/building-agent-environments-and-tasks)).

A world spec moves the bottleneck from writing tasks to auditing them. Good trade, but only if you move the effort too — the audit side is where the measured defects already sit.

## Key Takeaways

- Knowledge true of every task in the dataset goes in the world spec. Knowledge true of one task goes in the task spec.
- Build the world spec by making the first task and having the agent write down what it learned, then validate it by making a second and third.
- The markdown spec is the review surface. Humans approve prose, and agents build the environment, data, and grader from it.
- Tier calibration reports a pass rate, and a reward hack also reports a pass. Read the trajectory, or the difficulty curve fits shortcuts.
- The artifact pays back on a dataset, not on a handful of cases. For three or five tasks, write them by hand and spend the time on error analysis.

## Related

- [Agent-Authored Eval Suites From Repo Context and Traces](agent-authored-eval-suites.md) — how the first runnable task gets built from repo and traces, which is the step this one scales.
- [Incident-to-Eval Synthesis: Production Failures as Evals](incident-to-eval-synthesis.md) — the task provenance to prefer when you have real failures to mine.
- [Measuring Synthetic Eval Data Quality (SynAE)](synae-synthetic-eval-quality.md) — scoring the synthetic set a pipeline like this produces against a production reference.
- [Purpose-Built Eval Suites for Model and Harness Swaps](purpose-built-eval-suites.md) — sizing a suite to the decision, and the case for staying small.
- [Eval Environment Containment for Cyber-Capable Agents](eval-environment-containment.md) — isolating an eval environment, a separate concern from constructing one.
