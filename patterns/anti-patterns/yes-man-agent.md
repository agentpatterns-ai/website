---
title: "The Yes-Man Agent: Compliance Without Verification"
term: "Yes-Man Agent"
description: "Agents without explicit verification and pushback instructions execute every request without flagging problems — shipping errors at machine speed."
tags:
  - agent-design
  - tool-agnostic
  - anti-pattern
aliases:
  - sycophantic agent
  - sycophancy
last_reviewed: 2026-06-13
maturity: established
---

# The Yes-Man Agent

> A yes-man agent lacks explicit verification and [pushback instructions](../agent-design/agent-pushback-protocol.md), executing every request without flagging problems — shipping errors at machine speed.

Learn it hands-on: [The Yes-Man Agent](https://learn.agentpatterns.ai/anti-patterns/the-yes-man-agent/) — guided lesson with quizzes.

## What it looks like

The agent does exactly what it is told. Each response looks correct at a glance, but small problems build up: broken conventions, violated constraints and new vulnerabilities. The agent never flags them because no one told it to look.

## Why it happens

Agents are trained to be helpful, and helpfulness tracks compliance. Human raters favor responses that agree with them, and RLHF turns that into a built-in bias toward compliance over correction ([Towards Understanding Sycophancy in Language Models](https://arxiv.org/abs/2310.13548)). Task instructions like "research this topic, write a page, open a PR" describe the happy path. They say nothing about what to check, when to pause, or what should stop the work.

## The fix

Add three kinds of instruction to any agent definition.

Pre-task checks set out what to verify before starting:
> If the target file already exists and is substantially complete, comment on the issue explaining why and skip to the next.

In-task validation sets out what to check during the work:
> Before committing, verify: correct file path, valid markdown structure, all sourced claims linked.

Stop conditions set out when to halt and surface a problem:
> If critical or high severity issues remain after two review rounds, stop and report the issue number and problem.

## Separation of reviewer and implementer

A single agent cannot review its own work well, because it shares its own blind spots. Spawn a separate reviewer agent with instructions aimed at finding problems, not producing work ([Claude Code sub-agent architecture](https://code.claude.com/docs/en/sub-agents)).

## Structured output with required concerns

A required `concerns`, `issues` or `risks` field in structured output forces the agent to evaluate critically. An agent that must fill in such a field will weigh up the risks. One without the field will not.

## When this backfires

Adding verification gates to every agent definition can fail in four ways.

Over-specified stop conditions. Halting on non-blockers makes agents escalate constantly. Reviewers then dismiss every flag and the conditions become noise.

False-positive pre-task checks. A loose duplicate check blocks real work. An agent told to skip if "a page on this topic exists" stops on tangential matches, so scope the checks precisely.

Validator blindness. In-task validation catches structural errors, not meaning. Semantic errors need a [separate reviewer](../agent-design/separation-of-knowledge-and-execution.md), because an agent cannot reliably catch its own reasoning errors. A separate reviewer closes this gap but adds latency and cost.

Prompt-level ceiling. Verification instructions reduce sycophantic compliance but do not remove it. The bias comes from RLHF training, not prompt scaffolding. To mitigate it you need fine-tuning, decoding strategies and post-deployment controls alongside instructions ([Sycophancy in Large Language Models: Causes and Mitigations](https://arxiv.org/html/2411.15287v1)). Treat prompts as a floor-raiser, not a fix.

## The counter-anti-pattern: the cry-wolf agent

An agent that flags every minor issue, edge case and theoretical risk produces output people ignore. Yes-man and cry-wolf are opposite failure modes. Calibrate stop conditions to genuine blockers, not every deviation.

## Example

A content-writing agent receives this system prompt:

```
You are a documentation writer. When given a topic and an issue number,
research the topic, write a markdown page, and open a pull request.
```

Given the task "write a page on rate limiting", the agent produces a page, commits it and opens a PR — even though a page on rate limiting already exists at `docs/techniques/rate-limiting.md`. No pre-task check was specified, so the agent never looked.

With the yes-man instructions corrected:

```
You are a documentation writer. When given a topic and an issue number:

Pre-task: Check whether a page on this topic already exists under docs/.
If one exists and is substantially complete, comment on the issue
explaining what you found and stop — do not create a duplicate.

If no page exists, research the topic, write the markdown page, and
open a pull request. Before committing, verify: the file path is unique,
frontmatter includes title, description, and tags, and no heading levels
are skipped.

Stop condition: If you cannot determine whether a duplicate exists,
stop and report the ambiguity on the issue rather than guessing.
```

The corrected prompt adds three gate points: a pre-task duplicate check, in-task structural validation and an explicit stop condition for ambiguity. Each one prevents a category of silent error the original prompt could not catch.

## Key takeaways

- Agents without verification instructions comply with every request, including bad ones.
- Add pre-task checks, in-task validation and explicit stop conditions to every agent definition.
- Use [separate reviewer agents](../agent-design/separation-of-knowledge-and-execution.md), because an agent cannot reliably review its own work.
- Required structured output fields force the agent to do the evaluation you need.

## Related

- [Agent Backpressure](../agent-design/agent-backpressure.md)
- [Separation of Knowledge and Execution](../agent-design/separation-of-knowledge-and-execution.md)
- [Cognitive Reasoning vs Execution: A Two-Layer Agent Architecture](../agent-design/cognitive-reasoning-execution-separation.md)
- [Assumption Propagation](assumption-propagation.md)
- [Trust Without Verify](trust-without-verify.md)
- [Happy Path Bias](happy-path-bias.md)
- [LLM Review Overcorrection](llm-review-overcorrection.md)
- [Pattern Replication Risk](pattern-replication-risk.md)
- [Evidence-Grounded Disagreement in Agentic Code Review](../../code-review/evidence-grounded-disagreement.md) — the same compliance bias between two agents, and the constraint that measurably reduces it
