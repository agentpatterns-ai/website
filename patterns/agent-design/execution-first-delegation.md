---
title: "Execution-First Delegation: The AI-as-Executor Pattern"
term: "Execution-First Delegation"
description: "Write a delegation contract instead of scripting steps: specify the goal, constraints, success condition, and recovery path; the agent handles the how."
tags:
  - agent-design
  - workflows
  - tool-agnostic
aliases:
  - AI-as-executor pattern
  - delegation contract pattern
last_reviewed: 2026-06-12
maturity: adopted
---

# Execution-First Delegation: The AI-as-Executor Pattern

> Execution-first delegation hands the agent an outcome and a set of boundaries instead of a step list, then lets it determine how.

## The shift

In prompt-response AI, you describe each step: "read this file, extract these fields, format as JSON." You stay the orchestrator. The model executes individual instructions.

In execution-first delegation, you hand over an intent: "prepare this repository for release." The agent explores the codebase, plans, runs commands, changes files, and adapts on failure. You do not specify the sequence. This is the move from prompt-response to goal-directed systems traced in [agentic AI architecture evolution](agentic-ai-architecture-evolution.md). Your job shifts from writing instructions to writing contracts.

| Prompt-Response | Execution-First |
|-----------------|-----------------|
| You specify the steps | You specify the goal |
| Model executes each instruction | Agent plans and sequences autonomously |
| Failure requires human re-prompting | Agent adapts within defined constraints |
| Prompt quality determines output | Boundary quality determines safety |
| Appropriate for predictable, fixed workflows | Appropriate when steps can't be predicted upfront |

## The delegation contract

When you delegate execution, you write a contract with four parts:

```
Goal        — what the agent must accomplish
Constraints — what it may and may not do
Success     — how to know when it's done
Recovery    — what to do if something goes wrong
```

Skip any part and you get predictable failures:

- No constraints: the agent reads the intent broadly, exceeds scope, and makes irreversible changes
- No success condition: the agent runs forever or stops at an arbitrary point
- No recovery path: the agent stalls on a blocker with no fallback

## Why boundaries matter more than phrasing

In prompt-response workflows, the main skill is phrasing. You write clearly, use examples, and format well. In execution-first workflows, the main skill is bounding. What can the agent touch, how far can it go, and when must it stop?

[Anthropic's research on autonomous agents](https://www.anthropic.com/engineering/building-effective-agents) names stopping conditions and human-in-the-loop checkpoints as required structural elements, not optional add-ons. [nibzard's production-agent pattern library](https://www.nibzard.com/agentic-handbook) concludes that most agent failures are loop design failures, not model failures. The model ran correctly within an under-specified contract.

## MCP as the grounding layer

Agents that work on intent need structured access to real tools and data. Without it, context gets stuffed into prompts as stale text. Model Context Protocol (MCP) replaces that with structured runtime access. The agent queries what it needs during execution, under defined permissions:

- "Here is the current state of the deployment system (as text)" — prompt-embedded, stale, untestable
- "You have access to the deployment API via MCP" — structured, permissioned, live

## When to use execution-first delegation

Execution-first fits a task with these traits:

- Unpredictable steps: you cannot list what needs to happen before starting
- Adaptive execution: the right next step depends on what the previous step found
- Large scope: the work spans many files, systems, or decisions
- Clear stopping condition: you can define done precisely enough that the agent recognizes it

Avoid it when you can define every step in advance. A fixed, predictable workflow is better served by a [prompt chain](../../context-engineering/prompt-chaining.md), because an autonomous loop adds cost and non-determinism for no gain.

[Addy Osmani notes](https://addyo.substack.com/p/the-80-problem-in-agentic-coding) this fits greenfield or self-contained projects more cleanly than large, tightly coupled codebases, where the contract is harder to specify.

## Design checklist

Before you delegate execution to an agent, check that:

- [ ] Goal is outcome-defined: "prepare the repo for release", not "run these five commands"
- [ ] Constraints are explicit: which files, systems, or operations are off-limits
- [ ] Success condition is testable: the agent can verify completion without asking
- [ ] Recovery path exists: what the agent should do when it hits a blocker
- [ ] Scope is bounded: no permission escalation or scope expansion without a checkpoint (see [blast radius containment](../../security/blast-radius-containment.md))
- [ ] Irreversible operations are gated: deploys, deletes, and external writes need explicit authorization

## When this backfires

- Auditable workflows: regulated domains need step-by-step execution records. An autonomous loop produces a goal-oriented trace, not a procedure audit trail.
- Tightly coupled codebases: when system boundaries are unclear, setting safe constraints (such as [blast radius containment](../../security/blast-radius-containment.md)) is harder than listing the steps. The contract grows more complex than the scripted alternative.
- High-volume predictable operations: autonomous loops cost more tokens and produce non-deterministic paths. [Prompt chains](../../context-engineering/prompt-chaining.md) are cheaper and easier to test.
- Contract specification failure: the pattern shifts complexity from steps to boundaries. Under-specified contracts produce the same loop-failure modes the pattern is meant to prevent.

[Anthropic's measurement of agent autonomy](https://www.anthropic.com/research/measuring-agent-autonomy) reports full auto-approve runs in roughly 20% of new-user Claude Code sessions and 40% of experienced-user sessions. It also finds that 32% of human interruptions supply missing technical context the agent could not infer. Treat execution-first delegation as the right tool when steps are unpredictable and the boundary is specifiable, not as the default mode.

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

Compare this to an under-specified version: "Update the docs for the release." That version gives the agent no constraints, no boundary on scope, and no way to know when it is done.

## Key Takeaways

- Execution-first delegation shifts the developer's role from writing instructions to writing contracts — goal, constraints, success condition, and recovery path — once [the delegation decision](delegation-decision.md) says to hand the task over at all.
- Boundary quality determines safety; phrasing quality is secondary in autonomous workflows.
- Appropriate when steps are unpredictable upfront; inappropriate when every step can be defined in advance.
- Under-specified contracts produce the same failures as under-specified prompts — just harder to debug.
- MCP provides structured runtime tool access, replacing fragile prompt-embedded context.

## Related

- [The Delegation Decision: When to Use an Agent vs Do It Yourself](delegation-decision.md)
- [Controlling Agent Output](../../instructions/controlling-agent-output.md)
- [Rollback-First Design](rollback-first-design.md)
- [MCP: The Plumbing Behind Agent Tool Access](../../standards/mcp-protocol.md)
- [Agent-First Software Design](agent-first-software-design.md)
- [Agentless vs Autonomous: When Simple Beats Complex](agentless-vs-autonomous.md)
- [Human-in-the-Loop Placement: Where and How to Supervise](../../workflows/human-in-the-loop.md)
- [Agentic AI Architecture: From Prompt-Response to Goal-Directed Systems](agentic-ai-architecture-evolution.md)
