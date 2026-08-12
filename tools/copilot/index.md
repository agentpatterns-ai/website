---
title: "GitHub Copilot for AI Agent Development"
description: "Tool-specific reference for GitHub Copilot's agentic features. - Agent Mission Control — Centralized dashboard for assigning, steering, and tracking coding"
tags:
  - copilot
  - agent-design
  - index
applies_to: "copilot@1.x"
last_reviewed: 2026-05-27
status: current
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
- [Copilot Dedicated App (Desktop)](copilot-dedicated-app.md) — Standalone Windows/macOS/Linux desktop client where the agent session is the primary tenant of the window; one thin client over backend-held session state, not a unified app spanning web, mobile, and IDE
- [Copilot Extensions](copilot-extensions.md) — Build agents and skillsets that integrate into Copilot Chat via GitHub Marketplace (deprecated — see [migration guide](../../tool-engineering/copilot-extensions-to-mcp-migration.md))
- [copilot-instructions.md Convention](copilot-instructions-md-convention.md) — Repository-level instruction file for persistent project context
- [Copilot Spaces](copilot-spaces.md) — Named context collections that ground Copilot in curated reference material across repositories, files, PRs, issues, and uploads
- [Custom Agents, Skills & Plugins](custom-agents-skills.md) — Define specialized agents, reusable skills, and installable bundles
- [Embedding the Copilot SDK in a Managed Java Runtime](copilot-sdk-managed-runtime.md) — What embedding an agent loop costs a JVM host with its own concurrency model: the executor seam, container context propagation, and the JDK level it assumes
- [Dependabot Agent Assignment](dependabot-agent-assignment.md) — Route Dependabot alerts to Copilot for autonomous fix generation with human review at merge
- [Managing Agent Skills from the GitHub CLI](gh-skill-cli-management.md) — Install, pin, update, and publish agent skills with `gh skill` for scriptable provisioning
- [MCP Integration](mcp-integration.md) — Connect Copilot to external tools via Model Context Protocol
- [Monorepo Skill and Agent Discovery](monorepo-hierarchical-discovery.md) — Hierarchical configuration discovery from working directory to git root, enabling per-package skills and MCP servers
- [GitHub Copilot App Slash Commands and What They Change](slash-commands-copilot-app.md) — A fixed, GitHub-provided command set mapped by the session state each one changes; your own named operations ship as a custom agent or agent skill, not a prompt file
- [Unified Sessions View and CLI Agent in JetBrains](unified-sessions-view.md) — Chat-window registry aggregating CLI agent, agent mode, custom agent, and sub-agent sessions with worktree or workspace isolation
- [Agent Host Review Comments: Server-Side Feedback Transport](agent-host-review-comments.md) — Server-side review comment storage via three agent tools, enabling async resolution after client disconnect
