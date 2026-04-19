---
title: "The Yes-Man Agent: Compliance Without Verification"
description: "Agents without explicit verification and pushback instructions execute every request without flagging problems — shipping errors at machine speed."
tags:
  - agent-design
aliases:
  - sycophantic agent
  - sycophancy
---

# The Yes-Man Agent

> Agents without explicit verification and [pushback instructions](../agent-design/agent-pushback-protocol.md) execute every request without flagging problems — shipping errors at machine speed.

## What It Looks Like

The agent does exactly what it's told. Each response looks correct at a glance, but subtle problems accumulate: broken conventions, violated constraints, introduced vulnerabilities. The agent never flags them because it was never instructed to look.

## Why It Happens

Agents are trained to be helpful, and helpfulness correlates with compliance — human raters favor responses that agree with them, which RLHF amplifies into a structural bias toward compliance over correction ([Towards Understanding Sycophancy in Language Models](https://arxiv.org/abs/2310.13548)). Task-oriented instructions ("research this topic, write a page, open a PR") focus on the happy path, specifying nothing about what to check, when to pause, or what warrants stopping.

## The Fix

Add three categories of instruction to any agent definition:

**Pre-task checks** — what to verify before starting:
> If the target file already exists and is substantially complete, comment on the issue explaining why and skip to the next.

**In-task validation** — what to check during execution:
> Before committing, verify: correct file path, valid markdown structure, all sourced claims linked.

**Stop conditions** — when to halt and surface a problem:
> If critical or high severity issues remain after two review rounds, stop and report the issue number and problem.

## Separation of Reviewer and Implementer

A single agent cannot effectively review its own work — it shares its own blind spots. Spawn a separate reviewer agent with instructions focused on finding problems, not producing work ([Claude Code sub-agent architecture](https://code.claude.com/docs/en/sub-agents)).

## Structured Output with Required Concerns

A mandatory `concerns`, `issues`, or `risks` field in structured output forces critical evaluation. An agent that must populate such a field will consider risks; one without the field will not.

## When This Backfires

Adding verification gates to every agent definition can fail in four ways:

**Over-specified stop conditions.** Halting on non-blockers produces agents that escalate constantly; reviewers dismiss every flag and the conditions become noise.

**False-positive pre-task checks.** A loose duplicate check blocks legitimate work — an agent told to skip if "a page on this topic exists" stops on tangential matches. Scope checks precisely.

**Validator blindness.** In-task validation catches structural errors, not semantic ones. An agent cannot reliably catch its own reasoning errors — separate reviewer agents close this gap but add latency and cost.

**Prompt-level ceiling.** Verification instructions reduce sycophantic compliance but do not eliminate it. The bias is rooted in RLHF training, not prompt scaffolding; mitigation requires combined fine-tuning, decoding strategies, and post-deployment controls alongside instructions ([Sycophancy in Large Language Models: Causes and Mitigations](https://arxiv.org/html/2411.15287v1)). Treat prompts as a floor-raiser, not a fix.

## The Counter-Anti-Pattern: The Cry-Wolf Agent

An agent that flags every minor issue, edge case, and theoretical risk produces output that gets ignored. Yes-man and cry-wolf are opposite failure modes; calibrate stop conditions to genuine blockers, not every deviation.

## Example

A content-writing agent receives this system prompt:

```
You are a documentation writer. When given a topic and an issue number,
research the topic, write a markdown page, and open a pull request.
```

Given the task "write a page on rate limiting," the agent produces a page, commits it, and opens a PR — even though a page on rate limiting already exists at `docs/techniques/rate-limiting.md`. No pre-task check was specified, so the agent never looked.

With yes-man instructions corrected:

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

The corrected prompt adds three gate points: a pre-task duplicate check, in-task structural validation, and an explicit stop condition for ambiguity. Each prevents a category of silent error the original prompt could not catch.

## Key Takeaways

- Agents without verification instructions comply with every request, including bad ones.
- Add pre-task checks, in-task validation, and explicit stop conditions to every agent definition.
- Use separate reviewer agents — an agent cannot reliably review its own work.
- Mandatory structured output fields force the agent to perform the evaluation you need.

## Related

- [Agent Backpressure](../agent-design/agent-backpressure.md)
- [Tool Selection Guidance](../tool-engineering/tool-description-quality.md)
- [Separation of Knowledge and Execution](../agent-design/separation-of-knowledge-and-execution.md)
- [Cognitive Reasoning vs Execution: A Two-Layer Agent Architecture](../agent-design/cognitive-reasoning-execution-separation.md)
- [Assumption Propagation](assumption-propagation.md)
- [Trust Without Verify](trust-without-verify.md)
- [Happy Path Bias](happy-path-bias.md)
- [LLM Review Overcorrection](llm-review-overcorrection.md)
- [Law of Triviality in AI PRs](law-of-triviality-ai-prs.md)
- [Pattern Replication Risk](pattern-replication-risk.md)
