---
title: "Prompt File Libraries for Reusable Agent Instructions"
description: "Version-controlled prompt templates invoked on demand via slash commands, reducing variation and embedding real project file context into repeatable agent workflows."
tags:
  - instructions
aliases:
  - "prompt templates"
  - "reusable prompts"
---

# Prompt File Libraries

> Store reusable, parameterized prompt templates as version-controlled files that team members invoke on demand, reducing prompt variation and embedding file-based context into repeatable workflows.

## The Concept

Prompt files are Markdown files (`.prompt.md`) stored in a repository that encode repeatable agent tasks — generating tests, reviewing code, creating components, or migrating patterns. Unlike always-on repository instructions, they are invoked manually and sit in the **task-specific, on-demand layer** of the instruction hierarchy.

The value is standardization: five developers writing their own "add unit tests" prompt produce five different results, while a shared prompt file with embedded file references and structured conventions produces consistent output across the team.

## Anatomy of a Prompt File

In GitHub Copilot, prompt files live in `.github/prompts/` and use YAML frontmatter plus Markdown body content ([VS Code: Prompt Files](https://code.visualstudio.com/docs/copilot/customization/prompt-files)).

```markdown
---
description: "Generate unit tests following project conventions"
name: "unit-tests"
argument-hint: "Describe the module to test"
agent: "agent"
model: "o4-mini"
tools:
  - "githubRepo"
  - "codebase"
---

Follow the testing conventions in `../../docs/testing.md`.

Use the patterns established in `../../tests/example.test.ts`.

Generate tests for the specified module using Arrange-Act-Assert pattern.
Ensure coverage of edge cases and error paths.
```

### Frontmatter Fields

| Field | Purpose |
|-------|---------|
| `description` | Brief explanation shown in slash command picker |
| `name` | Display name after typing `/` (defaults to filename) |
| `argument-hint` | Guidance text shown in chat input |
| `agent` | Execution mode: `ask`, `agent`, `plan`, or a custom agent name |
| `model` | Override the current model selection |
| `tools` | Array of available tools; overrides agent defaults |

Source: [VS Code Prompt Files documentation](https://code.visualstudio.com/docs/copilot/customization/prompt-files)

### File References

Prompt files embed workspace context through two mechanisms:

- **Markdown links**: `[label](../../relative/path)` — injects the referenced file's content
- **Hash references**: `#file:../../relative/path` — alternative syntax for the same purpose

File references are the differentiating feature: they ground a generic prompt in the project's actual schemas, conventions, and examples. A test generation prompt that references real test files produces output matching the team's patterns rather than the model's defaults.

### Variable Substitution

Prompts support dynamic values ([VS Code: Prompt Files](https://code.visualstudio.com/docs/copilot/customization/prompt-files)):

| Variable | Resolves to |
|----------|-------------|
| `${selection}` | Current editor selection |
| `${input:name:placeholder}` | User-provided value at invocation |

## Where Prompt Files Fit in the Instruction Hierarchy

Copilot uses three instruction layers, each with different scoping and activation ([GitHub Docs: Custom Instructions](https://docs.github.com/en/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot)):

| Layer | File | Activation | Scope |
|-------|------|------------|-------|
| Repository-wide | `.github/copilot-instructions.md` | Automatic on every request | Global conventions |
| Path-specific | `.github/instructions/*.instructions.md` | Automatic when file path matches glob | Domain-specific rules |
| Task-specific | `.github/prompts/*.prompt.md` | Manual invocation via `/` command | On-demand workflows |

Applicable layers combine rather than replace each other: a prompt file invocation receives repository-wide instructions, matching path-specific instructions, and the prompt file content together.

### Tool Priority Resolution

When a prompt file specifies `tools` in frontmatter, the resolution order is: prompt file tools > referenced agent tools > default agent tools ([VS Code: Prompt Files](https://code.visualstudio.com/docs/copilot/customization/prompt-files)).

## Cross-Tool Equivalents

| Tool | Mechanism | Location | Invocation |
|------|-----------|----------|------------|
| GitHub Copilot | Prompt files (`.prompt.md`) | `.github/prompts/` | `/` slash commands |
| Claude Code | Skills (`SKILL.md`) | `.claude/skills/<name>/` | `/` slash commands |
| Cursor | Project Rules | `.cursor/rules/` | Auto-apply or glob-matched |

**Claude Code Skills** follow the [Agent Skills open standard](https://agentskills.io) — see [Agent Skills: Cross-Tool Task Knowledge Standard](../standards/agent-skills-standard.md) — supporting `$ARGUMENTS` substitution, subagent execution via `context: fork`, and dynamic shell injection.

**Cursor Rules** activate based on context via glob-pattern scoping ([Cursor: Rules](https://cursor.com/docs/context/rules)) — unlike prompt files, they are not manually invoked.

## Library Organization

Organize prompt files by workflow stage or domain:

```
.github/prompts/
  generate-tests.prompt.md
  review-pr.prompt.md
  add-api-endpoint.prompt.md
  migrate-to-async.prompt.md
  create-component.prompt.md
```

Each file references the relevant project artifacts — test conventions, API schemas, component templates — giving the agent tight, grounded context instead of broad codebase scanning.

## Example

A backend team maintains a prompt file for scaffolding new API endpoints:

```markdown
# .github/prompts/add-api-endpoint.prompt.md
---
description: "Scaffold a new REST endpoint with validation, tests, and OpenAPI spec"
name: "add-endpoint"
argument-hint: "Resource name (e.g., 'invoices')"
agent: "agent"
tools:
  - "codebase"
---

Follow the routing conventions in `../../src/routes/README.md`.

Use the validation patterns from `../../src/middleware/validation.ts`.

Match the test structure in `../../tests/routes/users.test.ts`.

For the given resource:
1. Create the route handler in `src/routes/`
2. Add request/response validation schemas
3. Generate integration tests covering happy path and 400/404/409 error cases
4. Update the OpenAPI spec in `docs/openapi.yaml`
```

A developer invokes `/add-endpoint` in Copilot Chat, enters "invoices" as the argument, and receives scaffolded code that follows the team's existing routing, validation, and test patterns — because the prompt file references those real project files rather than relying on the model's generic knowledge.

## When This Backfires

Prompt file libraries degrade in several predictable conditions:

- **Stale file references** — embedded paths to test examples, schemas, or convention docs go silently wrong when the source files are renamed, moved, or updated, leaving the prompt to generate output from outdated context.
- **Single-workspace scope** — files in `.github/prompts/` apply only to that workspace; teams sharing conventions across repos must copy and synchronize, reintroducing the variation the library was meant to solve.
- **Silent tool unavailability** — tools declared in `tools:` frontmatter that are not installed or authorized at invocation are ignored without warning, producing different results with no signal that capabilities are missing.
- **Overhead on small teams** — PR-driven creation and review adds process; for teams under three developers or with infrequent task repetition, the overhead exceeds the consistency benefit of inline prompting.

## Related

- [Instruction File Ecosystem](instruction-file-ecosystem.md)
- [Layered Instruction Scopes](layered-instruction-scopes.md)
- [Prompt Governance via PRs](prompt-governance-via-pr.md)
- [Specification as Prompt](specification-as-prompt.md)
- [Skill Library Evolution](../tool-engineering/skill-library-evolution.md)
- [Custom Agents and Skills (Copilot)](../tools/copilot/custom-agents-skills.md)
- [Example-Driven vs Rule-Driven Instructions](example-driven-vs-rule-driven-instructions.md)
- [@import Composition Pattern](import-composition-pattern.md)
- [Standards as Agent Instructions](standards-as-agent-instructions.md)
- [CLAUDE.md Convention for Structuring Agent Instructions](claude-md-convention.md)
- [Domain-Specific System Prompts with Concrete Examples](domain-specific-system-prompts.md)
