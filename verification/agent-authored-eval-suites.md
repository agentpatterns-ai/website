---
title: "Agent-Authored Eval Suites From Repo Context and Traces"
term: "Agent-Authored Eval Suite"
description: "Have a coding agent map your agent's surface and scaffold a runnable eval task from repo and traces, while capability choice and verifier auditing stay human."
tags:
  - testing-verification
  - evals
  - tool-agnostic
aliases:
  - repo-derived eval generation
  - eval engineering skill
  - trace-derived eval tasks
last_reviewed: 2026-08-19
maturity: emerging
---

# Agent-Authored Eval Suites From Repo Context and Traces

> A coding agent can map your agent's surface and scaffold an eval task, but choosing what to measure and auditing the verifier stay human.

An agent-authored eval suite is an evaluation harness a coding agent builds by reading the target agent's repository and its production traces, then interviewing a human to pick which capabilities to measure. LangChain shipped this as its Eval Engineering Skill in July 2026 and reported that "interviewing the user, leads to much better eval acceptance than one-shot generation" ([Trivedy, LangChain](https://www.langchain.com/blog/towards-automating-eval-engineering)). Treat that finding as the boundary of the technique: the agent handles retrieval and scaffolding, the human decides what is worth scoring.

It fits the case that [incident-to-eval synthesis](incident-to-eval-synthesis.md) does not: an agent with a repository and some traffic but no failure history to mine yet.

## What the agent derives

Two inputs answer different questions ([Trivedy](https://www.langchain.com/blog/towards-automating-eval-engineering)):

- The repository fixes what abilities exist. The skill "reads the repository and maps the agent surface including prompts, models, tools, skills, hooks" and identifies the data and services backing those behaviors.
- Traces fix how dependencies behave. They "show how tools behave in practice such as their arguments, results, and errors," and those observed contracts let the eval reproduce relevant production behavior in a controlled environment.

The output is a runnable task triple: an instruction given to the agent at start, an environment supplied as a Dockerfile, and a verifier that scores completion. The same task then runs unchanged "against different models, prompts, tools, and agent versions."

## What stays a human decision

The skill writes three review specs (`harness.md`, `environment.md`, and `task.md`) and instructs the agent: "Do not build the Harbor task until all three are approved" ([eval-engineering skill](https://github.com/langchain-ai/langchain-skills/blob/main/config/skills/eval-engineering/SKILL.md)). The interview settles what code cannot: which capability matters, and which dependencies run live rather than simulated. Calls that incur costs or require writes to production can be simulated instead of run on every eval invocation ([Trivedy](https://www.langchain.com/blog/towards-automating-eval-engineering)).

## Why it works

Eval authoring splits into a retrieval problem and a preference problem, and only the first is in the repository. Prompts, tool definitions, and backing services determine which abilities the agent has, and traces record how those tools respond; an agent reading code recovers both. Which ability deserves an eval depends on which user job matters, so the skill tells the agent to "ask only what code cannot answer, such as 'Which user job matters most?' or 'What failure must this eval catch?'" ([eval-engineering skill](https://github.com/langchain-ai/langchain-skills/blob/main/config/skills/eval-engineering/SKILL.md)). Hamel Husain reaches the same seam from the annotation side: a principal domain expert holds tacit user understanding "that cannot be fully captured in a rubric" ([Husain and Shankar](https://hamel.dev/blog/posts/evals-faq/)). Dividing the work along that line is why the interview outperforms one-shot generation.

## Inspect the verifier trajectory

LangChain found that "the first verifier was rarely the final one" and improved it by reading two trajectories after each run: the agent's messages, tool calls, and actions, and the verifier's evidence, reasoning, and final score. Reading both surfaces the shortcuts a single view hides: overciting irrelevant sources for full credit, claiming an action never taken, exploiting exposed answer material, or satisfying a proxy without completing the task ([Trivedy](https://www.langchain.com/blog/towards-automating-eval-engineering)). The skill encodes a matching rule for the environment: "Reject a fixture when the Harness can succeed by selecting the only option, following record order, reading answer-coded names, or bypassing the production interface" ([environment-building reference](https://github.com/langchain-ai/langchain-skills/blob/main/config/skills/eval-engineering/references/environment-building.md)). Rubric-side defenses against the same shortcuts live in [anti-reward-hacking](anti-reward-hacking.md).

## When this backfires

- No traces and thin tests. The map then comes from the implementation alone, so the task encodes current behavior as correct. Generated unit tests fail the same way: buggy code "steers LLMs toward generating tests that validate its erroneous behavior rather than expose it" ([Zhao, Zhou and Cohen](https://arxiv.org/abs/2607.22883v1)).
- One model family writes the task, the environment, and the LLM judge. LLM-generated benchmarks "systematically favor the model that created them," and self-bias is strong enough to make each model rank itself first, overriding peer consensus ([Xu et al.](https://arxiv.org/abs/2509.26600v2)). That removes the model comparison a portable task was built to support.
- Nobody with product context runs the interview. The reported gain rests on that step, so skipping it returns you to one-shot generation with a Dockerfile to maintain.
- Nobody audits the environment or the verifier. Auditing 168 benchmarks across nine domains found ambiguous task design, execution environment conflicts, and incorrect ground truths in over 25.7% of tasks; filtering them shifted model rankings and raised average scores on SWE-bench Verified and Terminal-Bench 2 by 9.9% and 9.6% ([Wang et al.](https://arxiv.org/abs/2605.26079v2)). Nothing about agent authorship argues for a lower rate.
- The agent surface changes weekly. A copy that alters prompts, control flow, tool parsing, memory, or model behavior is a reconstruction, and the skill warns not to describe its result as the production agent's result ([harness reference](https://github.com/langchain-ai/langchain-skills/blob/main/config/skills/eval-engineering/references/harness.md)).

If you already have production failures, spend the hour on those first. The minimum viable setup in [Husain and Shankar's evals FAQ](https://hamel.dev/blog/posts/evals-faq/) is "error analysis, not infrastructure": 30 minutes reviewing 20 to 50 outputs with one domain expert as the quality decision maker.

## Example

LangChain ran the flow on its documentation Q&A agent, [chat-langchain](https://github.com/langchain-ai/chat-langchain). The environment held a data corpus exposed through search tools modeled on the production agent, the tasks used realistic documentation questions pulled from real traces, and the verifier checked the answer against a golden answer string and the cited documents ([Trivedy](https://www.langchain.com/blog/towards-automating-eval-engineering)).

The skill's docs-search worked example shows how such a corpus avoids leaking. For a task asking the current account-deletion retention period, the bad environment is "one file named `account-deletion-answer.md` containing '30 days.'" The prescribed corpus carries four documents, each present for a stated reason ([environment-building reference](https://github.com/langchain-ai/langchain-skills/blob/main/config/skills/eval-engineering/references/environment-building.md)):

| Document | Content | Why included |
|---|---|---|
| Current account-deletion policy | 30 days; effective 2026 | supports the answer |
| Archived account-deletion policy | 60 days; superseded in 2025 | requires freshness checking |
| Workspace-deletion policy | 14 days for workspaces | requires scope checking |
| Account-recovery FAQ | recovery process without a retention period | plausible nearby search result |

## Key Takeaways

- The agent maps the surface and builds the scaffolding; a human picks the capability and approves the harness, environment, and task specs before any task is built.
- Traces contribute observed tool contracts (arguments, results, errors), which is what lets a controlled environment behave like production.
- Read the verifier's trajectory alongside the agent's after every run, because the first verifier is rarely the final one.
- Never let one model family author the test set and judge it, or the suite will rank that family first.
- With no traces and thin tests, a repo-derived task certifies whatever the implementation currently does.

## Related

- [Incident-to-Eval Synthesis: Production Failures as Evals](incident-to-eval-synthesis.md) — the post-production counterpart, where each incident becomes a regression case.
- [Agent-Driven Eval Flywheel: Prove a Fix Generalizes](agent-driven-eval-flywheel.md) — runs the improvement loop once a case set exists.
- [Anti-Reward-Hacking: Rubrics That Resist Gaming](anti-reward-hacking.md) — rubric-side defenses against the shortcuts the verifier trajectory exposes.
- [Purpose-Built Eval Suites for Model and Harness Swaps](purpose-built-eval-suites.md) — sizing a small suite to the decision it has to support.
- [Eval Environment Containment for Cyber-Capable Agents](eval-environment-containment.md) — when the containerized environment itself needs a verified boundary.
