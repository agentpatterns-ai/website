---
title: "Workflows for AI Agent Development"
description: "End-to-end workflows for agent-assisted development — from project bootstrapping and team onboarding to parallel sessions, evals, and continuous improvement."
---

# Workflows

> End-to-end workflows for agent-assisted development — from bootstrapping to team onboarding.

## Pages

- [Agent Debugging](../observability/agent-debugging.md) — Diagnosing bad agent output
- [Claude Code ↔ Copilot CLI: Changelog-Driven Feature Parity](changelog-driven-feature-parity.md) — Track which CLI tool shipped each capability first and when the other matched it
- [Agent-Driven Greenfield Product Development](agent-driven-greenfield.md) — Build a new product agent-first by defining roles, decomposing to context-safe tasks, and executing through autonomous agent loops
- [Central Repo for Shared Agent Standards](central-repo-shared-agent-standards.md) — Distribute shared agent skills, instruction files, and coding conventions from a central repository to downstream projects
- [Enterprise Skill Marketplace: Distribution, Usage Reporting, and Quality Evals](enterprise-skill-marketplace.md) — Scale a shared skill library with MDM distribution, private plugin marketplaces, OTel usage telemetry, and a manual eval cadence for high-traffic skills
- [Closed-Loop Agent Training from Tool Schemas](closed-loop-agent-training.md) — Generate synthetic training data from MCP tool definitions, fine-tune small models to match frontier performance, and re-train incrementally as schemas evolve
- [Content Pipeline: Idea to Published Page](content-pipeline.md) — How ideas move through GitHub issues, agent drafting, multi-reviewer quality gates, and into the published site
- [Content & Skills Audit Workflow](content-skills-audit.md) — Automated staleness detection for URLs, site maps, and sourced claims
- [Continuous Agent Improvement](continuous-agent-improvement.md) — Iterating on agent quality over time
- [Escape Hatches](escape-hatches.md) — Unsticking stuck agents
- [Introspective Skill Generation](introspective-skill-generation.md) — Mine agent patterns across sessions to generate new skills, agents, and hooks
- [Eval-Driven Development: Write Evals Before Building Agent Features](eval-driven-development.md) — Define evaluation tasks and success criteria before implementing agent features to make "done" objective and prevent requirement drift
- [Getting Started: Setting Up Your Instruction File](getting-started-instruction-files.md) — Create and iterate on your first CLAUDE.md, AGENTS.md, or copilot-instructions.md in under thirty minutes
- [Google Search Console Monitoring Workflow](gsc-search-console-monitoring.md) — Automate GSC and Bing WMT verification, index coverage tracking, and weekly CWV + query reports via API
- [Evaluation-Driven Development for Agent Tools](eval-driven-tool-development.md) — Build agent tools in a prototype-evaluate-analyze-iterate loop rather than optimizing in the dark
- [LLM-as-Judge Evaluation with Human Spot-Checking](llm-as-judge-evaluation.md) — Combine automated LLM rubric scoring with targeted human review to evaluate multi-agent output at scale without sacrificing quality on edge cases
- [Parallel Agent Sessions Shift the Bottleneck from Writing Code to Making Decisions](parallel-agent-sessions.md) — Running multiple simultaneous agent sessions transforms the engineer's role from contributor to tech lead
- [QA Session to Issues Pipeline](qa-session-to-issues-pipeline.md) — Multi-stage agent pipeline that transforms raw QA session documents into investigated, context-rich GitHub issues via codebase investigation
- [PostToolUse Hooks: Automatic Formatting and Linting After Every File Edit](posttooluse-auto-formatting.md) — Configure a PostToolUse hook so that formatting and linting run automatically after every file Claude writes or edits
- [Repository Bootstrap Checklist](repository-bootstrap-checklist.md) — Adding agent support to an existing repo
- [Simulation and Replay Testing for Agent Workflows](simulation-replay-testing.md) — Validate agent prompt changes by replaying a past task in isolation and diffing the result against what was actually merged
- [Single-Branch Git for Agent Swarms](single-branch-git-agent-swarms.md) — At 10+ parallel agents, feature branches cause merge conflicts and waste context on rebases; single-branch with advisory reservations and mechanical guards is the alternative
- [Sparse-Checkout Worktrees for Monorepo Agent Isolation](sparse-paths-monorepo-isolation.md) — Use worktree.sparsePaths to limit an agent's file-system view to one service subtree, reducing context noise and accidental blast radius in large monorepos
- [Team Onboarding for Agent Workflows](team-onboarding.md) — Bringing a team up to speed on agent-assisted development
- [The AI Development Maturity Model](ai-development-maturity-model.md) — Phases of AI coding tool adoption, from skeptic to agent-native workflows
- [Plan Mode: Read-Only Exploration Before Implementation](plan-mode.md) — Restrict agents to read-only operations to surface understanding and correct approach before any code is written
- [The Research-Plan-Implement Pattern](research-plan-implement.md) — Structure agent work in three explicit phases to avoid context-wasteful rework from premature coding
- [The Plan-First Loop: Design Before Code](plan-first-loop.md) — Summarize, correct, plan, and approve before the agent writes a single line of implementation code
- [The Velocity-Quality Asymmetry: Why AI Speed Gains Fade Without QA Investment](velocity-quality-asymmetry.md) — Empirical evidence shows AI coding tools produce transient velocity gains but persistent quality degradation — sustainable speed requires scaling QA as a first-class concern
- [Vibe Coding: Outcome-Oriented Agent-Assisted Development](vibe-coding.md) — Delegate implementation entirely to the agent and focus on evaluating outcomes for low-risk, throwaway work
- [Agent Observability in Practice: OTel, Cost Tracking, and Trajectory Logging](../observability/agent-observability-otel.md) — Wire up OpenTelemetry on Claude Code and LangChain agents for cost dashboards, compliance audit trails, and trajectory debugging
- [Per-Page OG Image Generation at MkDocs Build Time](og-image-generation.md) — Auto-generate branded 1200×630 Open Graph images from page metadata at build time so every social share shows a unique, on-brand preview card
