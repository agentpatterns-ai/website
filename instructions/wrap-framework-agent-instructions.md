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

### R — Refine Your Instructions

WRAP identifies three instruction layers for Copilot: repository-level, organization-level, and [custom agents](../tools/copilot/custom-agents-skills.md) for repetitive patterns — the broader [layered instruction scopes](layered-instruction-scopes.md) pattern. Repository instructions set conventions (naming, testing, style); the issue body adds task-specific context on top, improving responses across all subsequent interactions ([WRAP framework](https://github.blog/ai-and-ml/github-copilot/wrap-up-your-backlog-with-github-copilot-coding-agent/)).

Anthropic's [prompt altitude](system-prompt-altitude.md) principle applies: effective instructions sit in a "Goldilocks zone" — specific enough to guide behavior, flexible enough to provide strong heuristics rather than brittle logic ([Effective Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).

### A — Atomic Tasks

Break large problems into small, independent issues — one module, one concern per issue. Agents on broad tasks exhaust their context mid-implementation, producing half-finished work. Constrain each session to one feature, keeping clean mergeable state between sessions ([Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)). Atomic scoping also enables [parallel execution](../workflows/parallel-agent-sessions.md): five narrow issues run concurrently; one monolithic issue cannot.

### P — Pair with the Coding Agent

Humans provide the *why*, cross-system implications, and domain judgment; agents provide tireless execution. This maps to [human-in-the-loop](../workflows/human-in-the-loop.md) — review at meaningful checkpoints rather than after full completion. Session-opening checklists (read progress files, select highest-priority work, run tests before starting) reduce wasted cycles across sessions ([Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)).

## What WRAP Misses

WRAP omits several techniques that improve agent task execution:

| Gap | Technique | Source |
|-----|-----------|--------|
| Acceptance criteria format | [Feature list files](feature-list-files.md) with pass/fail checks | [Anthropic harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) |
| Negative constraints | [Instruction polarity](instruction-polarity.md) — what to avoid | [Instruction Polarity](instruction-polarity.md) |
| Verification step | Pre-completion checklists against the original spec | [Anthropic harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) |
| Example-vs-rule guidance | Diverse canonical examples beat exhaustive rule lists | [Anthropic context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) |
| Cross-session continuity | Progress files bridge disconnected context windows | [Anthropic harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) |

## When This Backfires

WRAP assumes a backlog-driven workflow with well-defined task boundaries and pays an upfront specification cost. Several conditions undermine it:

- **Exploratory or research tasks** resist atomization — domain knowledge emerges during exploration, so a conversational prompt beats a WRAP-compliant issue.
- **Solo or fast-moving projects** pay the spec overhead without the payoff. If the developer is also the reviewer, prose instructions add process without reducing ambiguity.
- **Tightly coupled work**: forcing atomicity on cross-module changes creates artificial boundaries, forcing agents to rediscover implicit context.
- **Instruction conflicts**: repository instructions (CLAUDE.md, copilot-instructions.md) and issue-body instructions can contradict each other; agents then hallucinate a resolution or stall.
- **Modern context windows reduce the atomicity payoff**. 200k+ token windows handle moderate task breadth, so aggressive decomposition fragments related changes and produces harder-to-review PRs.
- **Frequent scope changes**: acceptance criteria written for a moving target are wasted; human-paired iteration outperforms WRAP here.

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

Agents have no persistent state between sessions; every decision must be derivable from the current context window. Transformer models operate under a finite attention budget — every additional token competes for pairwise attention, so precision degrades as context grows ([Effective Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)). WRAP front-loads what the agent would otherwise infer or hallucinate, concentrating high-signal tokens where they matter.

**W** (concrete examples): LLMs treat few-shot examples as the strongest signal for expected behavior — a before/after snippet conveys a transformation more precisely than prose.

**A** (atomicity): context exhaustion is the primary failure mode in long-horizon tasks. A narrow task fits the full spec, prior code, and verification steps in one window; a broad task forces the agent to truncate earlier context as the implementation grows ([Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)).

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
