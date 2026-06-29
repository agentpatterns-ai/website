---
title: "Bootstrapping an Agent-Driven Project from Scratch"
description: "Structure a new project from scratch so agents can participate as effective collaborators from day one, not as an afterthought."
tags:
  - workflows
  - agent-design
  - instructions
  - tool-agnostic
aliases:
  - Greenfield Agent Bootstrap
last_reviewed: 2026-06-12
maturity: emerging
---

# Bootstrapping an Agent-Driven Project from Scratch

> Bootstrapping an agent-driven project defines agent roles, skills, and instruction files as a new codebase's architectural foundation, so agents contribute from the first commit.

Agent-driven bootstrapping treats the agent topology — roles, skills, and instruction files — as the project's initial architecture. Before you write the first feature, you decide which agents own which boundaries, what lives in `AGENTS.md` or `CLAUDE.md` ([an open format adopted across the industry](https://agents.md/)), and how to split tasks to fit context windows. This follows the same structure-shapes-output logic as [Conway's Law](https://en.wikipedia.org/wiki/Conway%27s_law): the agent layout you choose on day one shapes the codebase you end up with.

The detailed workflow — role definition, epic shaping, context-safe task decomposition, and review at PR boundaries — is in [Agent-Driven Greenfield Product Development](agent-driven-greenfield.md).

## When this backfires

Agent-first bootstrapping assumes you can pick a useful topology with no product signal. That assumption fails in specific conditions:

- Unknown domain shape. If you do not yet know the product's core workloads, role boundaries are guesses. A topology chosen before any feature exists tends to lock in the wrong splits, and moving an agent's responsibilities later costs more than moving a module.
- Single-developer or short-lived project. The cost of maintaining `AGENTS.md`, skill libraries, and agent definitions dominates when only one person and one or two agents touch the code. Adding agent support once the project proves itself is cheaper than building it up front.
- Rapidly changing model or tool capabilities. Today's topology assumes today's context windows, tool budgets, and reliability. If any of those shift a lot, you must rework an elaborate [agent-driven greenfield layout](agent-driven-greenfield.md); a thin codebase with minimal agent scaffolding absorbs that change more easily.
- Team unfamiliar with agent workflows. If contributors cannot yet tell a good agent definition from a bad one, the initial topology encodes that inexperience. Build the code first, then add agent support once the team has run agents in the small — that produces more durable decisions.

If any of these hold, the [Repository Bootstrap Checklist](repository-bootstrap-checklist.md) approach — adding agent support to an existing repo in dependency order — is the safer path.

## Key Takeaways

- Agent-first bootstrapping frontloads decisions about roles, skills, and instruction files that an established codebase would retrofit.
- The agent topology acts as the initial architecture; downstream code organization tends to mirror it.
- The approach backfires when the domain is unknown, the project is single-developer or short-lived, tool capabilities are in flux, or the team is new to agents — prefer retrofitting in those cases.
- For the concrete step-by-step workflow, see [Agent-Driven Greenfield Product Development](agent-driven-greenfield.md).

## Related

- [Agent-Driven Greenfield Product Development](agent-driven-greenfield.md)
- [Agent Environment Bootstrapping](agent-environment-bootstrapping.md)
- [Architectural Foundation First](architectural-foundation-first.md)
- [Repository Bootstrap Checklist](repository-bootstrap-checklist.md)
- [Getting Started with Instruction Files](../instructions/getting-started-instruction-files.md)
- [Distilled Bootstrap Contract](distilled-bootstrap-contract.md)
- [Skeleton Projects as Agent Scaffolding](skeleton-projects-as-scaffolding.md)
- [Codebase Readiness for Agents](../agent-design/codebase-readiness.md)
