---
title: "Bootstrapping an Agent-Driven Project from Scratch"
description: "Structure a new project from scratch so agents can participate as effective collaborators from day one, not as an afterthought."
tags:
  - workflows
  - agent-design
  - instructions
aliases:
  - Greenfield Agent Bootstrap
---

# Bootstrapping an Agent-Driven Project from Scratch

> Bootstrapping an agent-driven project means defining agent roles, skills, and instruction files as the architectural foundation of a new codebase, so agents can contribute from the first commit.

Agent-driven bootstrapping treats the agent topology — roles, skills, and instruction files — as the project's initial architecture. Decisions about which agents own which boundaries, what lives in `AGENTS.md` or `CLAUDE.md` ([an open format adopted across the industry](https://agents.md/)), and how tasks are decomposed to fit context windows are made before the first feature is written. This follows the same structure-shapes-output logic as [Conway's Law](https://en.wikipedia.org/wiki/Conway%27s_law): the agent layout you choose at day one shapes the codebase you end up with.

The detailed workflow — role definition, epic shaping, context-safe task decomposition, and review at PR boundaries — is in [Agent-Driven Greenfield Product Development](agent-driven-greenfield.md).

## When This Backfires

Agent-first bootstrapping assumes you can pick a useful topology with no product signal. That assumption fails in specific conditions:

- **Unknown domain shape.** If you do not yet know the product's core workloads, role boundaries are guesses. A topology chosen before any feature exists tends to lock in the wrong splits, and moving an agent's responsibilities later is more costly than moving a module.
- **Single-developer or short-lived project.** The overhead of maintaining `AGENTS.md`, skill libraries, and agent definitions dominates when only one person and one or two agents touch the code. Retrofitting agent support once the project proves itself is cheaper than frontloading it.
- **Rapidly changing model or tool capabilities.** Today's topology assumes today's context windows, tool budgets, and reliability. If any of those shift materially, an elaborate agent layout must be reworked; a thin codebase with minimal agent scaffolding absorbs that change more easily.
- **Team unfamiliar with agent workflows.** If contributors cannot yet tell a good agent definition from a bad one, the initial topology encodes inexperience. Building code first and retrofitting agent support once the team has operated agents in the small produces more durable decisions.

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
- [Getting Started with Instruction Files](getting-started-instruction-files.md)
