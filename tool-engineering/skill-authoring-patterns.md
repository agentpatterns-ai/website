---
title: "Skill Authoring Patterns: Description to Deployment"
description: "Practical patterns for building, testing, and troubleshooting agent skills — the categories they fall into, how to write descriptions that trigger reliably"
tags:
  - instructions
  - agent-design
  - long-form
aliases:
  - Skill design patterns
  - SKILL.md authoring
---

# Skill Authoring Patterns: Description to Deployment

> Practical patterns for building, testing, and troubleshooting agent skills — the categories they fall into, how to write descriptions that trigger reliably, implementation patterns, and what to do when things break.

!!! note "Also known as"
    Skill design patterns, SKILL.md authoring. For the portable skill format itself, see [Agent Skills: Cross-Tool Task Knowledge Standard](../standards/agent-skills-standard.md). For the progressive disclosure architecture, see [Progressive Disclosure for Agent Definitions](../agent-design/progressive-disclosure-agents.md).

Skill authoring patterns are the repeatable structures that make agent skills reliable — covering how to write descriptions that trigger at the right time, what content belongs in a skill versus the base model, and which implementation shape fits each task type. Sources: [Anthropic's Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) (January 2026) and Anthropic's internal practice ([source](https://x.com/trq212/status/2033949937936085378)).

## Skill Categories

Anthropic's internal skill library clusters into nine categories ([source](https://x.com/trq212/status/2033949937936085378)):

| Category | What it covers | Example |
|----------|---------------|---------|
| **Library & API Reference** | Embed documentation for APIs or libraries the agent frequently misuses | Internal SDK usage patterns, authentication flows |
| **Product Verification** | Validate product state against expected criteria before shipping | Feature flag checks, release readiness checklists |
| **Data Fetching & Analysis** | Query internal data sources and summarise results | Metrics dashboards, database queries, report generation |
| **Business Process & Team Automation** | Automate recurring cross-team workflows | Incident triage, onboarding sequences, sprint ceremonies |
| **Code Scaffolding & Templates** | Generate consistent boilerplate for new services or modules | Service stubs, test file structure, PR templates |
| **Code Quality & Review** | Apply team conventions during review or before commit | Style enforcement, security pattern checks, complexity limits |
| **CI/CD & Deployment** | Drive pipeline steps and release operations | Build triggering, environment promotion, rollback procedures |
| **Runbooks** | Encode on-call and operational procedures as executable steps | Database failover, cache flush, alert response |
| **Infrastructure Operations** | Manage cloud resources and configuration | Scaling operations, secret rotation, environment setup |

## Problem-First vs. Tool-First Framing

**Problem-first** skills define steps for an outcome ("set up a project workspace"). **Tool-first** skills embed expertise for a given tool ("I have Linear MCP connected"). This distinction drives which implementation pattern fits.

## Description Craft

The `description` field determines whether the agent loads a skill — it is always present in the system prompt ([progressive disclosure](../agent-design/progressive-disclosure-agents.md)), so it must earn its tokens.

Structure: `[What it does] + [When to use it] + [Key capabilities]`. Include trigger phrases users would actually say; missing triggers cause under-triggering. For over-triggering, add negative triggers:

```yaml
description: Advanced data analysis for CSV files. Use for statistical
  modelling, regression, clustering. Do NOT use for simple data
  exploration (use data-viz skill instead).
```

Debugging approach: ask the agent "When would you use the [skill name] skill?" — it quotes the description back, revealing what's missing.

## Don't State the Obvious

Write skill instructions as a delta from baseline model behavior: only the team conventions, domain-specific rules, and edge cases that the model would otherwise get wrong ([source](https://x.com/trq212/status/2033949937936085378)). Instructions Claude would follow correctly anyway waste tokens and dilute the rules that matter.

## Built-In Variables

`${CLAUDE_SKILL_DIR}` — directory of the current skill file. Use it to reference sibling assets (templates, config snippets) without hardcoding paths.

`${CLAUDE_PLUGIN_DATA}` — stable data directory that survives skill upgrades ([source](https://x.com/trq212/status/2033949937936085378)). Use it for persistent state (user preferences, learned conventions). Data written to `${CLAUDE_SKILL_DIR}` may be deleted on upgrade.

```yaml
name: project-scaffold
description: Scaffolds a new project from templates. Use when starting a new
  service, library, or documentation site.
instructions:
  - Read the template from ${CLAUDE_SKILL_DIR}/templates/service.yaml
  - Read persistent config from ${CLAUDE_PLUGIN_DATA}/config.json
  - Apply the config defaults from ${CLAUDE_SKILL_DIR}/config/defaults.json
```

## Setup Config Pattern

Store initial setup in `config.json` under `${CLAUDE_PLUGIN_DATA}`. If absent on first run, prompt via `AskUserQuestion` before proceeding ([source](https://x.com/trq212/status/2033949937936085378)) — this avoids hard-coding team-specific values.

```markdown
## Setup

On first use, check for `${CLAUDE_PLUGIN_DATA}/config.json`.
- If present: load team name, default assignees, and project key from it.
- If absent: ask the user for these values via AskUserQuestion, then write them to `${CLAUDE_PLUGIN_DATA}/config.json` for future sessions.
```

## Gotchas Section

A `## Gotchas` section is the highest-signal content in any skill ([source](https://x.com/trq212/status/2033949937936085378)) — the cases where Claude would do something plausible but wrong. Build it incrementally from real failures. Each entry names the mistake and the correct alternative:

```markdown
## Gotchas

- **Do not use `linear_search` for ID lookups** — it paginates and misses items created in the last 30 seconds. Use `linear_get_issue` with the exact ID instead.
- **Sprint assignment requires the cycle to be active** — calling `linear_add_to_cycle` on a closed cycle silently succeeds but the issue does not appear in the sprint view.
```

## Skill Composition

Skills can reference other skills by name ([source](https://x.com/trq212/status/2033949937936085378)). There is no native dependency management — if a required skill is absent, the agent must handle that gracefully.

```markdown
## Workflow

1. Run the `code-review` skill to check for style and security issues.
2. If the review passes, proceed with deployment using the steps below.
3. If the `code-review` skill is not installed, perform a manual checklist review before continuing.
```

Reference skills by their exact `name` field, not by filename.

## Five Implementation Patterns

| Pattern | Use when | Key structure |
|---------|----------|---------------|
| **1. Sequential Workflow Orchestration** | Multi-step process in fixed order | Step → tool call → expected output; include rollback instructions |
| **2. Multi-MCP Coordination** | Workflow spans multiple services | Organise by phase; validate before proceeding; pass data explicitly |
| **3. Iterative Refinement** | Output improves with iteration | Draft → quality check → refinement loop; explicit exit condition — see [Loop Detection](../observability/loop-detection.md) |
| **4. Context-Aware Tool Selection** | Same outcome, different tools by context | Decision tree: inspect context → select tool → explain choice; include fallback |
| **5. Domain-Specific Intelligence** | Specialised knowledge beyond tool access | Pre-check (domain rules) → execution → documentation; see [Domain-Specific System Prompts](../instructions/domain-specific-system-prompts.md) |

## Measuring Skill Effectiveness

Track invocation frequency with a `PreToolUse` hook ([source](https://x.com/trq212/status/2033949937936085378)) logging skill name and timestamp. Use the log to find under-triggering skills (description needs work), over-triggering skills (description too broad), and popular skills (expand these). See [Hook Catalog](hook-catalog.md) and [Hooks and Lifecycle Events](hooks-lifecycle-events.md).

## Testing Methodology

Test across three dimensions: **triggering** (loads on relevant queries, not on unrelated ones), **functional** (produces correct outputs consistently across 3-5 runs), and **performance** (compare tool calls, messages, and tokens with vs. without the skill — an effective skill reduces all three).

Iterate on a single challenging task until the agent succeeds, then extract the winning approach into the skill.

## Troubleshooting

| Symptom | Common Cause | Fix |
|---------|-------------|-----|
| Skill never triggers | Description too vague or missing trigger phrases | Add specific phrases users would say; mention relevant file types |
| Skill triggers on unrelated queries | Description too broad | Add negative triggers; narrow scope |
| Skill loads but instructions ignored | Instructions too verbose or buried | Put critical instructions first; use numbered lists; move detail to `references/` |
| MCP calls fail | Connection or auth issues | Test MCP independently without the skill first |
| Slow or degraded responses | Skill content too large | Keep SKILL.md under 5000 words; use progressive disclosure via `references/` |
| Inconsistent results across sessions | Ambiguous instructions | Replace vague language ("validate properly") with explicit checks ("verify name is non-empty, at least one member assigned, date not in past") |

For critical validations, bundle a script — code is deterministic; language interpretation is not.

## Example

The following YAML frontmatter shows the Description Craft pattern in practice. A Linear MCP skill uses the `[What it does] + [When to use it] + [Key capabilities]` structure with explicit trigger phrases and a negative trigger to prevent over-firing.

```yaml
name: linear-issue-manager
description: Manages Linear issues, projects, and cycles via the Linear MCP server.
  Use when creating issues, triaging backlogs, updating issue status, or generating
  sprint summaries. Handles bulk operations and cross-team assignments. Do NOT use
  for Jira or GitHub Issues workflows (use those dedicated skills instead).
```

Below is the core of a Sequential Workflow Orchestration skill (Pattern 1) for that same Linear [MCP integration](../tools/copilot/mcp-integration.md). Each step names the tool call, its required parameters, and the expected output — with an explicit rollback instruction if a step fails.

```markdown
## Workflow: Create Issue and Assign to Cycle

1. **Validate input** — confirm `title` (non-empty) and `teamId` are present; abort with error message if missing
2. **Create issue** — call `linear_create_issue` with `title`, `teamId`, `priority: 2`; capture returned `issueId`
3. **Assign to active cycle** — call `linear_get_active_cycle` for the team, then `linear_add_to_cycle` with `issueId` and `cycleId`
4. **Confirm** — return the issue URL and cycle name to the user

**On failure at step 3**: do not delete the issue; report the `issueId` so the user can assign manually.

## Gotchas

- **Do not call `linear_get_active_cycle` without a `teamId`** — it returns the first team's cycle alphabetically, not the current user's team.
```

Asking the agent "When would you use the linear-issue-manager skill?" after saving the file confirms the description is being read correctly — the agent quotes the trigger phrases back verbatim, revealing any gaps.

## Related

- [Agent Skills: Cross-Tool Task Knowledge Standard](../standards/agent-skills-standard.md)
- [Skill Frontmatter Reference](skill-frontmatter-reference.md)
- [Skill as Knowledge](skill-as-knowledge.md)
- [Skill Library Evolution](skill-library-evolution.md)
- [Skill Tool Runtime Enforcement](skill-tool-runtime-enforcement.md)
- [On-Demand Skill Hooks](on-demand-skill-hooks.md)
- [Progressive Disclosure for Agent Definitions](../agent-design/progressive-disclosure-agents.md)
- [Domain-Specific System Prompts](../instructions/domain-specific-system-prompts.md)
- [Plugin and Extension Packaging](../standards/plugin-packaging.md)
- [Narrow Task Instructions](../security/task-scope-security-boundary.md)
- [Loop Detection](../observability/loop-detection.md)
- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](hook-catalog.md)
- [Hooks and Lifecycle Events: Intercepting Agent Behavior](hooks-lifecycle-events.md)
- [Runbooks as Agent Instructions](../workflows/runbooks-as-agent-instructions.md)
- [Evaluator-Optimizer Pattern](../agent-design/evaluator-optimizer.md)
