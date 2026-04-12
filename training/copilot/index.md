---
title: "GitHub Copilot Training Modules for Engineering Teams"
description: "Tool-specific training modules covering GitHub Copilot surfaces, customization primitives, context engineering, harness engineering, and team adoption."
tags:
  - training
  - copilot
---

# GitHub Copilot

> Tool-specific modules covering GitHub Copilot surfaces, customization, and team adoption.

## Core Modules

| Module | Topic | Duration |
|--------|-------|----------|
| [Platform Surface Map](surface-map.md) | All surfaces (VS Code, GitHub.com, CLI, coding agent, mobile), Spaces, code review, third-party agents — what exists and when to use it | 30–45 min |
| [Customization Primitives](customization-primitives.md) | Instructions, prompt files, agents, skills, hooks, MCP, memory, Spaces, [content exclusions](../../instructions/content-exclusion-gap.md) — how to extend each surface | 30–45 min |
| [Context Engineering & Agent Workflows](context-and-workflows.md) | Context engineering vs prompt engineering, [progressive disclosure](../../agent-design/progressive-disclosure-agents.md), [context rot](../../context-engineering/context-window-dumb-zone.md), task decomposition, delegation contracts, steering, review workflows, anti-patterns | 30–45 min |
| [Harness Engineering](harness-engineering.md) | Making codebases agent-ready — [backpressure](../../agent-design/agent-backpressure.md), repo legibility, linter messages as context, mechanical enforcement, multi-session scaffolding, safe operations, [convergence detection](../../agent-design/convergence-detection.md) | 30–45 min |
| [Team Adoption & Governance](team-adoption.md) | [Progressive autonomy](../../human/progressive-autonomy-model-evolution.md), tiered code review, cost management, security boundaries, shared configuration, measuring impact, adoption anti-patterns, rollout timeline | 30–45 min |

## Complementary Modules

Elective modules for teams that want to go deeper on specific topics. Not required for the core curriculum.

| Module | Topic | Duration |
|--------|-------|----------|
| [Advanced Patterns](advanced-patterns.md) | Multi-agent orchestration, parallel sessions, agentic workflows, CI/CD integration, batch operations, Agents page, event-driven routing | 30–45 min |
| [Model Selection & Routing](model-selection.md) | Model roster, premium request multipliers, when to override Auto, cascade routing, the [reasoning sandwich](../../agent-design/reasoning-budget-allocation.md), coding agent cost optimisation, competitive evaluation | 30–45 min |
