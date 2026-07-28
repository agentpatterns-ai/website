---
title: "Workflows for AI Agent Development"
description: "End-to-end workflows for agent-assisted development — from project bootstrapping and team onboarding to parallel sessions, evals, and continuous improvement."
tags:
  - workflows
  - agent-design
  - tool-agnostic
  - index
last_reviewed: 2026-05-27
---

# Workflows

> End-to-end workflows for agent-assisted development — from bootstrapping to team onboarding.

Learn it hands-on: [Capstone — The Workflow Decision Table](https://learn.agentpatterns.ai/workflows/the-workflow-decision-table/) — guided lesson with quizzes.

## Pages

- [Agent Debugging](../observability/agent-debugging.md) — Diagnosing bad agent output
- [Agent Commit Attribution: Signed Commits and Agent Identity](agent-commit-attribution.md) — Configure agents to sign or annotate their commits with verifiable identity metadata so audit trails distinguish agent-generated changes from human-authored ones
- [Agent-Driven Greenfield Product Development](agent-driven-greenfield.md) — Build a new product agent-first by defining roles, decomposing to context-safe tasks, and executing through autonomous agent loops
- [Central Repo for Shared Agent Standards](central-repo-shared-agent-standards.md) — Distribute shared agent skills, instruction files, and coding conventions from a central repository to downstream projects
- [Enterprise Skill Marketplace: Distribution, Usage Reporting, and Quality Evals](enterprise-skill-marketplace.md) — Scale a shared skill library with MDM distribution, private plugin marketplaces, OTel usage telemetry, and a manual eval cadence for high-traffic skills
- [Closed-Loop Agent Training from Tool Schemas](closed-loop-agent-training.md) — Generate synthetic training data from MCP tool definitions, fine-tune small models to match frontier performance, and re-train incrementally as schemas evolve
- [Skill Library Refinement Loops](skill-library-refinement-loops.md) — Four complementary feedback mechanisms that together keep a shared skill library accurate and useful
- [Continuous Agent Improvement](continuous-agent-improvement.md) — Iterating on agent quality over time
- [Continuous Documentation as an Agent-Driven Practice](continuous-documentation.md) — AI agents detect documentation-code drift on schedule or push and open reviewable PRs to realign docs as a continuous pipeline
- [Accumulated Behavioral Rules from Review Feedback](accumulated-behavioral-rules.md) — Codify each accepted review comment as a persistent behavioral rule the agent loads and self-checks, so it stops repeating the same class of mistake
- [Escape Hatches](escape-hatches.md) — Unsticking stuck agents
- [Daily-Use Skill Library: Encoding Your Process as Agent Skills](daily-use-skill-library.md) — Build a small library of purpose-built skills that encode your engineering process from ideation through architecture
- [SDLC-Phase Skill Taxonomy: Full-Lifecycle Skill Libraries](sdlc-skill-taxonomy.md) — Organize a skill library around SDLC phases so phase-entry commands activate only the relevant skills at each stage
- [Introspective Skill Generation](introspective-skill-generation.md) — Mine agent patterns across sessions to generate new skills, agents, and hooks
- [Eval-Driven Development: Write Evals Before Building Agent Features](eval-driven-development.md) — Define evaluation tasks and success criteria before implementing agent features to make "done" objective and prevent requirement drift
- [How Teams Build SE Agents: A Seven-Stage Build Loop](se-agent-build-workflow.md) — The seven-stage loop practitioners follow when building SE agents, and where engineering effort moves once implementation gets cheap
- [Getting Started: Setting Up Your Instruction File](../instructions/getting-started-instruction-files.md) — Create and iterate on your first CLAUDE.md, AGENTS.md, or copilot-instructions.md in under thirty minutes
- [Google Search Console Monitoring Workflow](../geo/gsc-search-console-monitoring.md) — Automate GSC and Bing WMT verification, index coverage tracking, and weekly CWV + query reports via API
- [LLM-as-Judge Evaluation with Human Spot-Checking](llm-as-judge-evaluation.md) — Combine automated LLM rubric scoring with targeted human review to evaluate multi-agent output at scale without sacrificing quality on edge cases
- [Continuous Autonomous Task Loop](continuous-autonomous-task-loop.md) — Self-directed agent loop that selects, executes, commits, and iterates over a task backlog with fresh context per task and rate-limit handling
- [Factory Over Assistant: Orchestrating Parallel Agent Fleets](factory-over-assistant.md) — Shift from watching one agent to orchestrating parallel agents with automated feedback loops — and the infrastructure required to make it viable
- [The Software Factory Model: Industrializing Agent Loops](software-factory-model.md) — Harness many agent loops into a production line bounded by verification, and decide per loop where the lights stay on for human judgment
- [Parallel Agent Sessions Shift the Bottleneck from Writing Code to Making Decisions](parallel-agent-sessions.md) — Running multiple simultaneous agent sessions transforms the engineer's role from contributor to tech lead
- [Concurrent Agent Pull Requests and Merge-Conflict Cost](concurrent-agent-pr-merge-conflicts.md) — Co-active overlapping agent PRs are the norm; budget for the measured merge-conflict cost and climb a coordination ladder instead of blanket-serializing dispatch
- [QA Session to Issues Pipeline](qa-session-to-issues-pipeline.md) — Multi-stage agent pipeline that transforms raw QA session documents into investigated, context-rich GitHub issues via codebase investigation
- [Backlog Triage as a Named Agent Skill](backlog-triage-skill.md) — A single skill encodes a state machine into issue labels and produces a durable agent brief as the executor hand-off contract
- [Labels as Locks: Pipelined Backlog Processing with Issue Labels as Stage Gates](labels-as-locks-pipeline.md) — Coordinate concurrent agents on a backlog by gating stages with labels and locking work with a claim label plus timestamped comment as a lease — for idempotent, minutes-scale work
- [Auto-Triage Workflow: Bug-Monitoring Agent that Connects Related Reports and Opens Fix PRs](auto-triage-workflow.md) — Four-stage agent workflow (monitor, correlate, investigate, propose-fix) that watches alert streams and either tags the right owner or opens a fix PR — only safe under three named preconditions
- [Throwaway-Prototype Skill: Build to Discard, Keep Only the Answer](throwaway-prototype-skill.md) — A scoped skill that builds the smallest end-to-end thing to resolve one design question, forbids polish, and captures only the verdict before the code is deleted
- [PostToolUse Hooks: Automatic Formatting and Linting After Every File Edit](../tools/claude/posttooluse-auto-formatting.md) — Configure a PostToolUse hook so that formatting and linting run automatically after every file Claude writes or edits
- [Repository Bootstrap Checklist](repository-bootstrap-checklist.md) — Adding agent support to an existing repo
- [Dev Containers for AI Coding Agents: Claude Code vs Copilot CLI](devcontainers-for-ai-coding-agents.md) — Compare the two official devcontainer paths — Claude Code's reference container with an egress-allowlisting firewall versus Copilot CLI's install-only Feature plus Codespaces inclusion
- [Experiential-Learning Setup Agents with Snapshot Rollback (SetupX)](experiential-setup-agents-snapshot-rollback.md) — Capture dual-modality fix records, trial them under Docker snapshot rollback, and verify with prosecutor-judge — when prebuilt environments are not an option
- [Simulation and Replay Testing for Agent Workflows](simulation-replay-testing.md) — Validate agent prompt changes by replaying a past task in isolation and diffing the result against what was actually merged
- [Single-Branch Git for Agent Swarms](single-branch-git-agent-swarms.md) — At 10+ parallel agents, feature branches cause merge conflicts and waste context on rebases; single-branch with advisory reservations and mechanical guards is the alternative
- [Single-CLI Agent Platform: Create to Production in One CLI](single-cli-agent-platform.md) — Bundle scaffold, run, eval, deploy, and publish into one CLI when the team is on a single cloud and wants the agent itself to self-serve its own deploys
- [Sparse-Checkout Worktrees for Monorepo Agent Isolation](../tools/claude/sparse-paths-monorepo-isolation.md) — Use worktree.sparsePaths to limit an agent's file-system view to one service subtree, reducing context noise and accidental blast radius in large monorepos
- [Lazy Worktree Isolation: Enter the Worktree on First Write, Not on Dispatch](lazy-worktree-isolation.md) — Background sessions start in the parent checkout and only relocate into an isolated git worktree on the first Edit or Write tool call
- [Team Onboarding for Agent Workflows](team-onboarding.md) — Bringing a team up to speed on agent-assisted development
- [The AI Development Maturity Model](ai-development-maturity-model.md) — Phases of AI coding tool adoption, from skeptic to agent-native workflows
- [Plan Mode: Read-Only Exploration Before Implementation](../tools/claude/plan-mode.md) — Restrict agents to read-only operations to surface understanding and correct approach before any code is written
- [The Research-Plan-Implement Pattern](research-plan-implement.md) — Structure agent work in three explicit phases to avoid context-wasteful rework from premature coding
- [Mise en Place for Agentic Coding](mise-en-place-agentic-coding.md) — Three-phase preparation methodology (contextual grounding, collaborative specification, task decomposition) that front-loads alignment work before parallel agent fan-out
- [The Plan-First Loop: Design Before Code](plan-first-loop.md) — Summarize, correct, plan, and approve before the agent writes a single line of implementation code
- [Cloud Planning with Inline-Comment Review and Execute-Anywhere Choice](cloud-planning-execute-anywhere.md) — Generate the plan in a cloud session, review it inline in the browser, then defer the cloud-versus-local execution choice to approval time
- [The Velocity-Quality Asymmetry: Why AI Speed Gains Fade Without QA Investment](velocity-quality-asymmetry.md) — Empirical evidence shows AI coding tools produce transient velocity gains but persistent quality degradation — sustainable speed requires scaling QA as a first-class concern
- [TDD Interaction Models: Throughput Versus Test Quality](tdd-interaction-models.md) — Four ways to split the TDD cycle between human and agent, and why full autonomy trades verified specification coverage for raw development speed
- [AI Slop as a Process Problem: Encoding Quality Standards as Pipeline Gates](slop-as-process-problem.md) — Treat AI-generated slop the way CI/CD treats broken builds — a per-PR agent gate enforcing version-controlled standards, sized to agent throughput rather than reviewer attention
- [Kaizen-Style Continuous Code Quality Loop (Pomona)](kaizen-continuous-quality-loop.md) — Pair a Scanning skill and a Repair skill to file small, single-purpose code-quality PRs a reviewer accepts quickly — for mechanical tasks under a per-day review cap
- [Vibe Coding: Outcome-Oriented Agent-Assisted Development](../patterns/anti-patterns/vibe-coding.md) — Delegate implementation entirely to the agent and focus on evaluating outcomes for low-risk, throwaway work
- [Agent Observability in Practice: OTel, Cost Tracking, and Trajectory Logging](../observability/agent-observability-otel.md) — Wire up OpenTelemetry on Claude Code and LangChain agents for cost dashboards, compliance audit trails, and trajectory debugging
- [Prototype Before Optimizing: Establish Quality Baselines Before Token Constraints](prototype-before-optimizing.md) — Defer production efficiency constraints until after establishing quality baselines to avoid locking in suboptimal architectures
- [Background-to-Foreground Handoff](background-foreground-handoff.md) — Transfer work from a background agent to a human at the ~90% completion mark using distilled summaries and artifact-based handoff points
- [In-Thread Side-Channel](in-thread-side-channel.md) — Ask a mid-task clarifying question inside one session using a tagged sub-conversation that returns the agent to its prior goal
- [Canary Rollout for Agent Policy Changes](canary-rollout-agent-policy.md) — Gate agent policy updates behind a traffic-split rollout so regressions surface on a small blast radius before full deployment
- [Governing Production Agents: Cost, Control, Compliance](governing-production-agents.md) — A tri-axis framework that designs cost budgets, runtime control, and compliance auditability as one enforced system applied to every model, tool, and agent call
- [Burn the Boats — Commitment-Forcing Deprecation](burn-the-boats.md) — Remove a working feature entirely with a hard deadline to force full commitment to a new paradigm and stop anchoring to obsolete approaches
- [The 7 Phases of AI-Assisted Feature Development](7-phases-ai-development.md) — Feature-level workflow model with entry and exit criteria: Research, Prototype, PRD, Issues, Implement, QA, Ship
- [Monolith-to-Sub-Agents Refactor](monolith-to-subagents-refactor.md) — Five-step migration checklist for taking a brittle monolithic agent prototype to an orchestrated pipeline with schema-first outputs, dynamic RAG, tracing, and framework-native circuit breakers
- [Chat-Platform Agent Delegation](chat-platform-agent-delegation.md) — Mention a cloud coding agent in a Slack or Microsoft Teams channel to delegate from where coordination already happens, with a concentrated lethal-trifecta posture that the IDE entry point hides
- [Cursor Automations: Event-Triggered Agents and the /automate Skill](cursor-automate-event-triggered-automations.md) — Cursor 3.8's expanded trigger surface (GitHub events, Slack emoji, default-on computer-use) and the /automate natural-language authoring skill ship event-driven dispatch only when the lethal trifecta is bounded per trigger
- [Public-Channel Agent Work as Lehrwerkstatt](public-channel-agent-work.md) — Force agent conversations into public channels so the team learns from every transcript — a high-yield organizational practice with hard psychological-safety and data-scope preconditions
- [Stakeholder Trust Through Evals and Observability](stakeholder-trust-evals-observability.md) — Three-artifact stakeholder review cycle — dashboards, custom trace views, ad-hoc query — that transfers eval and observability data to non-engineers when paired with narrated error analysis, plural headline metrics, and an in-workflow surface
- [Parallel Polyglot Ports as a Spec-Ambiguity Oracle](parallel-polyglot-ports-spec-oracle.md) — Generate multiple AI-paired ports from one executable spec and treat divergence as a signal that the spec under-specifies behavior — not as a fault-tolerance vote
- [Spec-Anchored Drift-Gated Architecture (Spec Growth Engine)](spec-growth-engine.md) — Make spec-code divergence a blocking merge gate and scope each agent's context to an ownership path in a machine-readable spec graph — only under stable contracts
- [Staged Literal Porting with a Per-Stage Numeric Oracle](staged-literal-port-with-numeric-oracle.md) — Split an LLM-assisted port into a numerics stage and a parallelism stage, forbid the assistant from improving the source, and gate each stage on output drawn from the prior version
- [Building Custom Agents from Substrate to Production (Agents All the Way Down)](agents-all-the-way-down-methodology.md) — Framework-free methodology with two substrate preconditions and three iterative practices (prototype, harvest as CLI via the Turtle pattern, agent-tests-agent) for one-developer custom-agent builds
- [Knowledge-Based Pull Requests for Cross-Trust-Boundary Contributions](knowledge-based-pull-requests.md) — Distil an external contribution into a confirmed knowledge package, then have a project-owned trusted agent regenerate the code in-house — for the high-context contributions where reconstructing intent from the diff is expensive
- [Whole-Codebase Visibility as a Migration Prerequisite](whole-codebase-visibility-migration-prerequisite.md) — Three-condition scoping check (codebase size, multi-repo or cross-VCS scope, discovery-bound shape) that decides whether a large-scale agent-driven migration needs whole-codebase visibility infrastructure or whether agentic search will do
- [Legacy Code Archaeology: Reconstruct Intent Before Migrating](legacy-code-archaeology.md) — Use a coding agent to excavate an undocumented legacy system's intent — under adversarial forensic prompting and a runnable period-accurate baseline — before modernizing, for the comprehension-first case where no migration blueprint yet exists
