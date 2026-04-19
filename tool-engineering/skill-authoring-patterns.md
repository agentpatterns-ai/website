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

> Skill authoring patterns are repeatable structures that make agent skills reliable — covering how to write descriptions that trigger at the right time, which implementation shape fits each task type, and how to diagnose failures when they occur.

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

Store initial setup in `config.json` under `${CLAUDE_PLUGIN_DATA}`. If absent on first run, prompt via `AskUserQuestion` before proceeding ([source](https://x.com/trq212/status/2033949937936085378)) — this avoids hard-coding team-specific values. For pipeline contexts where `AskUserQuestion` is unusable, see the [Override Pattern](override-interactive-commands.md) for suppressing interactive prompts while reusing the same skill definition.

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

## CLI-First Design (Recommended for Executable Skills)

Skills with non-trivial executable logic should ship a dedicated CLI entry point under `<skill-name>/scripts/<skill-name>.{sh,py}` rather than embedding bash or Python inline in `SKILL.md` ([nibzard catalogue: CLI-First Skill Design](https://github.com/nibzard/awesome-agentic-patterns/blob/main/patterns/cli-first-skill-design.md)). A single CLI interface serves humans (debugging, testing, composition with Unix tools) and agents (deterministic invocation, meaningful exit codes) at the same time.

Inline-shell skills have compounding costs: logic cannot be tested independently, agents re-parse the shell on every invocation, humans debugging must manually extract commands from markdown, and composition requires reassembly.

### The shape

Three skill shapes, chosen by whether the skill has executable logic:

| Shape | Use when | SKILL.md body | Logic lives in |
|-------|----------|---------------|----------------|
| **Script-backed (CLI-first)** | Skill has non-trivial executable logic | description, when to invoke, how to call the CLI, Gotchas, Related | `<skill-name>/scripts/<skill-name>.{sh,py}` |
| **Inline-shell** | One- or two-line commands with no branching | fine to embed directly | SKILL.md itself |
| **Pure reference** | Templates, taxonomies, decision tables | the reference content itself | SKILL.md itself |

CLI-backed scripts should follow Unix philosophy: one script per skill, subcommands for operations, JSON on stdout, errors on stderr, meaningful exit codes, and `--dry-run` where side effects are involved.

### Reference examples

Three existing skills in this repo are written CLI-first and can be used as templates:

- `add-missing-meta` — script at `scripts/add-missing-meta.py`; SKILL.md body is a thin wrapper naming the trigger, the command, and the constraints
- `parse-citations` — Python module importable from other scripts, with the SKILL.md documenting the public API
- `create-audit-backlog` — argparse-based CLI with flags documented in a table; SKILL.md names the triggers and the post-run steps

### Authoring checklist

When writing a new skill, answer:

1. Does this skill have logic more complex than two lines of shell? If yes → CLI-first.
2. If you chose inline, does the SKILL.md explain why (triviality, pure reference, or an environment-specific command that cannot be extracted)?
3. Does the SKILL.md body reduce to description, when to invoke, how to call, Gotchas, and Related — with the actual algorithm living in `scripts/`?

Existing inline-shell skills migrate opportunistically when next touched. No forced refactor — but new skills default to CLI-first.

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

## Why It Works

Skill patterns work because agents are context-constrained token predictors — they produce output proportional to the quality and specificity of their input context. A description field acts as a learned retrieval key: the agent matches incoming user intent against description tokens to decide what to load. Concise, trigger-rich descriptions raise that match probability. Gotchas sections work because they shift the prior toward correct behavior in the narrow set of cases where the base model would otherwise guess wrong; they do not teach the model general knowledge, they override its statistical default for a specific edge case. The delta principle (only write what the base model gets wrong) is efficient because it keeps context small — every token saved in skill instructions is a token available for task reasoning ([source](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).

## When This Backfires

Apply skill authoring patterns selectively — over-engineering is a real cost:

1. **Simple one-off tasks** — a skill with YAML frontmatter, a Gotchas section, and a CLI entry point for a two-command workflow adds setup overhead with no reliability gain. Inline shell or a single README block is sufficient.
2. **Rapidly changing APIs** — skills encode domain knowledge that becomes wrong when the underlying API changes. A skill with stale Gotchas is worse than no skill: it actively misdirects the agent. Skills for fast-moving surfaces need an explicit owner and update cadence.
3. **Skill proliferation** — with many skills loaded, descriptions are shortened to fit a character budget, which strips the trigger keywords that drive selection ([source](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)). A library of 40+ skills degrades all skills' triggering reliability; consolidating rarely-used skills reduces this pressure.
4. **Security surface expansion** — each skill loaded from an external registry is a potential prompt-injection vector. Malicious skills can direct the agent to invoke tools in ways that don't match their stated purpose. Review all third-party skills before installation, especially those bundling shell scripts.

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
- [CLI-First Skill Design](cli-first-skill-design.md)
- [Skill Frontmatter Reference](skill-frontmatter-reference.md)
- [Skill as Knowledge](skill-as-knowledge.md)
- [Skill Library Evolution](skill-library-evolution.md)
- [Skill Tool Runtime Enforcement](skill-tool-runtime-enforcement.md)
- [On-Demand Skill Hooks](on-demand-skill-hooks.md)
- [Progressive Disclosure for Agent Definitions](../agent-design/progressive-disclosure-agents.md)
- [Domain-Specific System Prompts](../instructions/domain-specific-system-prompts.md)
- [Plugin and Extension Packaging](../standards/plugin-packaging.md)
- [Credential Hygiene for Agent Skill Authorship](../security/credential-hygiene-agent-skills.md)
- [Narrow Task Instructions](../security/task-scope-security-boundary.md)
- [Loop Detection](../observability/loop-detection.md)
- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](hook-catalog.md)
- [Hooks and Lifecycle Events: Intercepting Agent Behavior](hooks-lifecycle-events.md)
- [Runbooks as Agent Instructions](../workflows/runbooks-as-agent-instructions.md)
- [Evaluator-Optimizer Pattern](../agent-design/evaluator-optimizer.md)
