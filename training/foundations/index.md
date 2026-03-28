---
title: "Foundational Disciplines for AI-Assisted Development"
description: "Tool-agnostic training in prompt, context, harness, and tool engineering — the four disciplines that determine agent quality."
tags:
  - training
  - tool-agnostic
---

# Foundational Disciplines

> The four practitioner disciplines that determine agent output quality — independent of which tool you use.

These modules teach the conceptual frameworks behind effective AI-assisted development. Each discipline addresses a different layer of the system: what you say (prompts), what the agent sees (context), what it can do (tools), and what catches mistakes (harness). The [capstone](prompt-context-harness-capstone.md) shows how the four compound.

## Core Modules

| Module | Topic | Duration |
|--------|-------|----------|
| [Prompt Engineering](prompt-engineering.md) | [System prompt altitude](../../instructions/system-prompt-altitude.md), polarity, rule- vs example-driven instructions, compliance ceiling, domain-specific prompts, negative-space instructions | 30–45 min |
| [Context Engineering](context-engineering.md) | Context window mechanics, [attention sinks](../../context-engineering/attention-sinks.md), lost-in-the-middle, compression strategies, dynamic context assembly, JIT loading, [prompt caching](../../context-engineering/prompt-caching-architectural-discipline.md) | 30–45 min |
| [Harness Engineering](harness-engineering.md) | Repo legibility, mechanical enforcement, constrained solution spaces, [backpressure](../../agent-design/agent-backpressure.md), feedback loop quality, pre-completion checklists, [convergence detection](../../agent-design/convergence-detection.md) | 30–45 min |
| [Tool Engineering](tool-engineering.md) | [Tool description quality](../../tool-engineering/tool-description-quality.md), token-efficient design, schema design, MCP architecture, skill authoring, [tool minimalism](../../tool-engineering/tool-minimalism.md), poka-yoke tools | 30–45 min |
| [How the Four Disciplines Compound](prompt-context-harness-capstone.md) | The multiplication model, diagnosing failures by discipline, investment progression, decision frameworks | 30–45 min |

## Complementary Modules

| Module | Topic | Duration |
|--------|-------|----------|
| [Eval Engineering](eval-engineering.md) | [Pass@k metrics](../../verification/pass-at-k-metrics.md), LLM-as-judge, golden query pairs, [incident-to-eval synthesis](../../verification/incident-to-eval-synthesis.md), [behavioral testing](../../verification/behavioral-testing-agents.md), anti-reward hacking | 30–45 min |
| [Autonomous Research Loops](autonomous-research-loops.md) | Experimentation vs information research loops, termination design, doom loop prevention, context management, grounding strategies, control surfaces | 30–45 min |
