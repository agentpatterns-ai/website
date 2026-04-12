---
title: "WRAP Framework for Writing Agent-Ready Issue Descriptions"
description: "A four-step checklist for agent-ready task descriptions: Write effective issues, Refine instructions, Atomic tasks, and Pair with the agent."
tags:
  - instructions
---

# WRAP Framework for Agent Instructions

> A four-step checklist for writing agent-ready task descriptions that maximize autonomous execution quality: Write effective issues, Refine instructions, Atomic tasks, Pair with the agent.

## Origin

GitHub introduced WRAP in a [blog post about the Copilot coding agent](https://github.blog/ai-and-ml/github-copilot/wrap-up-your-backlog-with-github-copilot-coding-agent/). The framework targets issue descriptions for autonomous agents, but the principles apply wherever humans delegate tasks to AI.

## The Framework

### W — Write Effective Issues

Treat every issue as onboarding material for someone who has never seen your codebase. The agent cannot infer project conventions, architectural decisions, or unstated requirements.

**Descriptive titles** scope the work spatially. "Update authentication middleware to use async/await" tells the agent *where* to work. "Update the entire repository" does not.

**Concrete examples** outperform verbose prose. A before/after code snippet communicates the expected transformation faster than a paragraph of requirements ([Effective Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).

**What WRAP omits here:** explicit acceptance criteria. [Feature list files](feature-list-files.md) with per-feature pass/fail criteria prevent agents from marking work complete without satisfying concrete checks ([Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)).

### R — Refine Your Instructions

WRAP identifies three instruction layers for Copilot: repository-level, organization-level, and [custom agents](../tools/copilot/custom-agents-skills.md) for repetitive patterns. This maps to the broader [layered instruction scopes](layered-instruction-scopes.md) pattern — global defaults narrowing to task-specific overrides.

Issue descriptions do not operate in isolation. Repository instructions set conventions (naming, testing, style); the issue body adds task-specific context on top. Adding to repository-level instructions over time improves responses across all subsequent interactions in that repository ([WRAP framework](https://github.blog/ai-and-ml/github-copilot/wrap-up-your-backlog-with-github-copilot-coding-agent/)).

Anthropic's [prompt altitude](system-prompt-altitude.md) principle applies: effective instructions sit in a "Goldilocks zone" — specific enough to guide behavior, flexible enough to provide strong heuristics rather than brittle logic ([Effective Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).

### A — Atomic Tasks

Break large problems into small, independent issues — one module, one concern per issue. Agents working on broad tasks exhaust their context window mid-implementation, producing half-finished work. Constrain each session to "only one feature at a time," maintaining clean, mergeable state between sessions ([Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)).

Atomic scoping also enables [parallel execution](../workflows/parallel-agent-sessions.md). Five narrowly scoped issues run concurrently; one monolithic issue cannot.

**What WRAP omits here:** negative constraints — what the agent should *not* do. Files to leave untouched, patterns to avoid, scope boundaries not to cross. See [instruction polarity](instruction-polarity.md).

### P — Pair with the Coding Agent

Humans provide the *why* behind a task, cross-system implications, and domain judgment. Agents provide tireless execution and consistency in repetitive work.

This maps to the [human-in-the-loop](../workflows/human-in-the-loop.md) pattern. Review agent output at meaningful checkpoints rather than after full completion. Session-opening checklists — read progress files, select highest-priority work, run tests before starting — reduce wasted cycles across sessions ([Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)).

## Why It Works

Transformer models operate under a finite attention budget — every additional token in context competes for the model's pairwise attention. A well-framed issue reduces noise by eliminating ambiguous or irrelevant tokens, concentrating high-signal information exactly where the agent needs it ([Effective Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)). Precision degrades as context grows, so a concise, spatially-scoped issue (W) with layered instruction references (R) and a bounded scope (A) collectively minimize the tokens the agent must process before taking its first meaningful action — reducing both hallucination risk and mid-task context exhaustion.

## When This Backfires

WRAP assumes a backlog-driven workflow with well-defined task boundaries. Several conditions undermine it:

- **Exploratory or research tasks** resist atomization. Breaking "investigate why the auth flow is slow" into sub-issues requires domain knowledge that only emerges during exploration — the overhead of decomposition exceeds the benefit.
- **Solo or fast-moving projects** pay the overhead of crafting detailed issues without the payoff. If the developer is also the reviewer and the only context holder, prose instructions add process without reducing ambiguity.
- **Instruction conflicts**: repository-level instructions (CLAUDE.md, copilot-instructions.md) and issue-body instructions can contradict each other. When they do, agents either hallucinate a resolution or stall — more instructions increase the surface area for conflicts.
- **Modern context windows reduce the atomicity payoff**. Agents running on 200k+ token windows can handle moderate task breadth without context exhaustion. Aggressive decomposition into many micro-issues can fragment related changes and produce harder-to-review PRs.

## What WRAP Misses

WRAP omits several techniques that improve agent task execution:

| Gap | Technique | Source |
|-----|-----------|--------|
| No acceptance criteria format | Feature list files with JSON-structured pass/fail checks | [Anthropic harness research](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) |
| No negative constraints | Instruction polarity — stating what to avoid alongside what to do | [Instruction Polarity](instruction-polarity.md) |
| No verification step | Pre-completion checklists forcing agents to verify against original spec | [Anthropic harness research](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) |
| No example-vs-rule guidance | Diverse canonical examples outperform exhaustive rule lists | [Anthropic context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) |
| No cross-session continuity | Progress files as cognitive bridges between disconnected context windows | [Anthropic harness research](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) |

## When This Backfires

WRAP adds upfront specification cost. This cost is not always justified:

- **Short or exploratory tasks**: A two-line conversational prompt produces faster results than a WRAP-compliant issue when scope is unclear and rapid iteration is preferable to autonomous execution.
- **Tightly coupled work**: Forcing atomicity on tasks with strong cross-module dependencies can create artificial issue boundaries, requiring agents to rediscover and re-state context that would have been implicit in a broader task description.
- **Frequent scope changes**: When product requirements are in flux, time spent writing acceptance criteria for autonomous agents is wasted if the criteria are invalidated before the agent runs. Human-paired iteration outperforms up-front WRAP specification in these conditions.

## Example

The following contrasts a vague GitHub issue with one that applies all four WRAP principles, showing the concrete changes each letter requires.

**Before: vague issue, violates W and A**

```markdown
Title: Fix the auth stuff

We need to update authentication. Make sure it works correctly and add tests.
```

**After: WRAP-compliant issue**

```markdown
Title: Update authentication middleware to use async/await (src/middleware/auth.ts)

## What and where
Replace all synchronous `jwt.verify()` calls in `src/middleware/auth.ts` with
the async `promisify(jwt.verify)()` pattern. Do not touch other files.

## Expected transformation
Before:
    const payload = jwt.verify(token, SECRET);

After:
    const payload = await promisifyVerify(token, SECRET);

## Repository instructions in effect
- Follow the async/await style guide in CLAUDE.md §3
- All new code must pass `npm test` before committing

## Acceptance criteria (supplement — WRAP gap)
- [ ] src/middleware/auth.ts uses async/await throughout
- [ ] npm test exits 0
- [ ] No other files are modified

## Context for pairing
Background: migrating to async to unblock a Node 22 upgrade.
If you hit a type error on `promisify`, check `@types/node` — it may need
bumping to 20+.
```

The rewritten issue applies **W** (descriptive title with file path, concrete before/after snippet), **R** (references CLAUDE.md repository instructions), **A** (scoped to one file with an explicit "do not touch other files" boundary), and **P** (provides the *why* and flags a likely ambiguity for the human reviewer). The acceptance criteria block fills the gap WRAP leaves open: each item is verifiable without human judgement.

## Why It Works

Agents have no persistent state between sessions. Every decision — what to name a variable, which file to modify, when to consider a task done — must be derivable from the current context window. WRAP works because it front-loads the information the agent would otherwise have to infer or hallucinate.

**W** (concrete examples) works because LLMs treat few-shot examples as the strongest signal for expected behavior — a before/after snippet conveys the transformation more precisely than a prose description, with fewer tokens and less ambiguity ([Effective Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).

**A** (atomicity) works because context window exhaustion is the primary failure mode in long-horizon agent tasks. A narrowly scoped task fits the full specification, prior code, and verification steps within a single context window; a broad task forces the agent to truncate earlier context as the implementation grows ([Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)).

## Key Takeaways

- WRAP (Write, Refine, Atomic, Pair) provides a lightweight checklist for agent-ready issue descriptions, applicable beyond Copilot to any agent task assignment system
- Each letter maps to a deeper principle: specification-as-prompt, layered instruction scopes, one-feature-at-a-time scoping, and human-in-the-loop review
- The main gap is the absence of structured acceptance criteria and verification steps — supplement with feature list files and [pre-completion checklists](../verification/pre-completion-checklists.md)

## Related

- [Context Engineering](../context-engineering/context-engineering.md)
- [Specification as Prompt](specification-as-prompt.md)
- [Feature List Files](feature-list-files.md)
- [Instruction Polarity](instruction-polarity.md)
- [Example-Driven vs Rule-Driven Instructions](example-driven-vs-rule-driven-instructions.md)
- [Layered Instruction Scopes](layered-instruction-scopes.md)
- [System Prompt Altitude](system-prompt-altitude.md)
- [Narrow Task Instructions](../security/task-scope-security-boundary.md)
- [Convention Over Configuration](convention-over-configuration.md)
- [Standards as Agent Instructions](standards-as-agent-instructions.md)
- [Negative Space Instructions](negative-space-instructions.md)
- [Harness Engineering](../agent-design/harness-engineering.md) — environment design as the primary lever for agent reliability
