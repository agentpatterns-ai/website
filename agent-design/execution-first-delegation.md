---
title: "Execution-First Delegation: The AI-as-Executor Pattern"
description: "Write a delegation contract instead of scripting steps: specify the goal, constraints, success condition, and recovery path; the agent handles the how."
tags:
  - agent-design
  - workflows
aliases:
  - AI-as-executor pattern
  - delegation contract pattern
---

# Execution-First Delegation

> Instead of scripting steps, specify the outcome and the boundaries. The agent determines how.

## The Shift

In prompt-response AI, you describe each step: "read this file, extract these fields, format the output as JSON." You are still the orchestrator; the model executes individual instructions.

In execution-first delegation, you hand over an intent: "prepare this repository for release." The agent explores the codebase, plans the required steps, runs commands, modifies files, and adapts if something fails — all without you specifying the sequence.

The developer's job changes from writing instructions to writing contracts.

| Prompt-Response | Execution-First |
|-----------------|-----------------|
| You specify the steps | You specify the goal |
| Model executes each instruction | Agent plans and sequences autonomously |
| Failure requires human re-prompting | Agent adapts within defined constraints |
| Prompt quality determines output | Boundary quality determines safety |
| Appropriate for predictable, fixed workflows | Appropriate when steps can't be predicted upfront |

## The Delegation Contract

When you delegate execution, you are writing a contract with four parts:

```
Goal        — what the agent must accomplish
Constraints — what it may and may not do
Success     — how to know when it's done
Recovery    — what to do if something goes wrong
```

Skipping any part produces predictable failures:

- **No constraints** → agent interprets intent broadly, exceeds scope, makes irreversible changes
- **No success condition** → agent runs indefinitely or stops at an arbitrary point
- **No recovery path** → agent gets stuck on a blocker with no fallback

## Why Boundaries Matter More Than Phrasing

In prompt-response workflows, the primary skill is phrasing — write clearly, use examples, format the request well.

In execution-first workflows, the primary skill is bounding — what can the agent touch, how far can it go, and when must it stop?

[Anthropic's research on autonomous agents](https://www.anthropic.com/engineering/building-effective-agents) identifies stopping conditions and human-in-the-loop checkpoints as required structural elements, not optional add-ons. [nibzard's production-agent pattern library](https://www.nibzard.com/agentic-handbook) concludes: most agent failures are loop design failures, not model failures — the model executed correctly within an under-specified contract.

## MCP as the Grounding Layer

Agents operating on intent need structured access to real tools and data. Without it, context gets embedded in prompts — ownership rules, API schemas, dependency constraints stuffed into text.

Model Context Protocol (MCP) replaces prompt-embedded context with structured runtime access. The agent queries what it needs during execution, under defined permissions.

The architectural difference:

- "Here is the current state of the deployment system (as text)" — prompt-embedded, stale, untestable
- "You have access to the deployment API via MCP" — structured, permissioned, live

## When to Use Execution-First Delegation

Execution-first is appropriate when the task has these characteristics:

- **Unpredictable steps** — you cannot enumerate what needs to happen before starting
- **Adaptive execution required** — the right next step depends on what the previous step found
- **Large scope** — the work spans many files, systems, or decisions
- **Clear stopping condition** — you can define done precisely enough that the agent can recognize it

Avoid it for tasks where every step can be defined in advance. A fixed workflow with predictable inputs is better served by a scripted sequence or a [prompt chain](../context-engineering/prompt-chaining.md) — adding an autonomous loop introduces cost and non-determinism without benefit.

[Addy Osmani notes](https://addyo.substack.com/p/the-80-problem-in-agentic-coding) this fits greenfield or self-contained projects more cleanly than large existing codebases with tight coupling — the contract is harder to specify when system boundaries are unclear.

## Design Checklist

Before delegating execution to an agent, verify:

- [ ] **Goal is outcome-defined** — "prepare the repo for release" not "run these five commands"
- [ ] **Constraints are explicit** — which files, systems, or operations are off-limits
- [ ] **Success condition is testable** — the agent can verify completion without asking
- [ ] **Recovery path exists** — what the agent should do when it hits a blocker
- [ ] **Scope is bounded** — no permission escalation or scope expansion without a checkpoint
- [ ] **Irreversible operations are gated** — deploys, deletes, and external writes require explicit authorization

## Example

A delegated release-preparation task with a well-formed contract:

```
Goal: Prepare this repository for the v2.4.0 release.

Constraints:
- Only modify files in /docs and /CHANGELOG.md
- Do not push to any branch — local commits only
- Do not modify version numbers in package.json
- Do not create or delete branches

Success: CHANGELOG.md has a v2.4.0 section and all docs links resolve correctly.

Recovery: If a link is broken and cannot be fixed by editing docs/,
          add it to broken-links.md and continue.
```

Compare this to an under-specified version: "Update the docs for the release." The latter gives the agent no constraints, no boundary on what it can touch, and no way to know when it's done.

## Related

- [The Delegation Decision: When to Use an Agent vs Do It Yourself](delegation-decision.md)
- [Progressive Autonomy with Model Evolution](../human/progressive-autonomy-model-evolution.md)
- [Controlling Agent Output](controlling-agent-output.md)
- [Rollback-First Design](rollback-first-design.md)
- [MCP: The Plumbing Behind Agent Tool Access](../standards/mcp-protocol.md)
- [Agent-First Software Design](agent-first-software-design.md)
- [Loop Strategy Spectrum](loop-strategy-spectrum.md)
- [Agents vs Commands](agents-vs-commands.md)
- [Convergence Detection in Iterative Refinement](convergence-detection.md)
- [Idempotent Agent Operations](idempotent-agent-operations.md)
- [Classical SE Patterns as Agent Design Analogues](classical-se-patterns-agent-analogues.md)
- [Cognitive Reasoning vs Execution: A Two-Layer Agent Architecture](cognitive-reasoning-execution-separation.md)
- [Empowerment Over Automation](empowerment-over-automation.md)
- [Human-in-the-Loop Placement: Where and How to Supervise](../workflows/human-in-the-loop.md)
- [Agentless vs Autonomous: When Simple Beats Complex](agentless-vs-autonomous.md)
- [Agentic AI Architecture: From Prompt-Response to Goal-Directed Systems](agentic-ai-architecture-evolution.md)
- [Agent Composition Patterns: Chains, Fan-Out, Pipelines, Supervisors](agent-composition-patterns.md)
