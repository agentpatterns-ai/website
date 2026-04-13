---
title: "GitHub Copilot for AI Agent Development"
description: "Tool-specific reference for GitHub Copilot's agentic features. - Agent Mission Control — Centralized dashboard for assigning, steering, and tracking coding"
tags:
  - copilot
  - agent-design
---
# GitHub Copilot

> Tool-specific reference for GitHub Copilot's agentic features.

## Pages

- [Agent Mission Control](agent-mission-control.md) — Centralized dashboard for assigning, steering, and tracking coding agent tasks across repositories
- [Copilot CLI BYOK and Local Model Support](copilot-cli-byok-local-models.md) — Connect Copilot CLI to any OpenAI-compatible provider or run fully local models for cost control, data residency, and offline workflows
- [Agent Mode](agent-mode.md) — Local, synchronous agentic execution in VS Code, JetBrains, Eclipse, and Xcode
- [Cloud Agent Organization Controls](cloud-agent-org-controls.md) — Three-tier governance model for runner configuration, firewall policy, and commit traceability
- [Cloud Agent: Research, Plan, and Code Phases](cloud-agent-research-plan-code.md) — Three-phase execution model with explicit developer checkpoints between Research, Plan, and Code
- [Coding Agent](coding-agent.md) — Asynchronous agent that works via GitHub Actions to plan, implement, and open PRs
- [Copilot Extensions](copilot-extensions.md) — Build agents and skillsets that integrate into Copilot Chat via GitHub Marketplace (deprecated — see [migration guide](../../tool-engineering/copilot-extensions-to-mcp-migration.md))
- [copilot-instructions.md Convention](copilot-instructions-md-convention.md) — Repository-level instruction file for persistent project context
- [Copilot Spaces](copilot-spaces.md) — Named context collections that ground Copilot in curated reference material across repositories, files, PRs, issues, and uploads
- [Custom Agents, Skills & Plugins](custom-agents-skills.md) — Define specialized agents, reusable skills, and installable bundles
- [Dependabot Agent Assignment](dependabot-agent-assignment.md) — Route Dependabot alerts to Copilot for autonomous fix generation with human review at merge
- [MCP Integration](mcp-integration.md) — Connect Copilot to external tools via Model Context Protocol
- [Monorepo Skill and Agent Discovery](monorepo-hierarchical-discovery.md) — Hierarchical configuration discovery from working directory to git root, enabling per-package skills and MCP servers
