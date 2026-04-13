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

Prompt files are Markdown files (`.prompt.md`) stored in a repository that encode repeatable agent tasks — generating tests, reviewing code, creating components, or migrating patterns. Unlike always-on repository instructions, prompt files are invoked manually for specific tasks. They sit in the **task-specific, on-demand layer** of the instruction hierarchy.

The value is standardization: when five developers each write their own prompt for "add unit tests to this module," they get five different results. A shared prompt file with embedded file references and structured conventions produces consistent output across the team.

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

File references are the differentiating feature. They transform a generic prompt into one grounded in your project's actual schemas, conventions, and examples. A test generation prompt that references your real test files produces output matching your patterns, not generic ones.

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

All applicable layers combine — they do not replace each other. A prompt file invocation receives repository-wide instructions, any matching path-specific instructions, and the prompt file content.

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

Each file references the relevant project artifacts — test conventions, API schemas, component templates — so the agent receives tight, grounded context rather than broad codebase scanning.

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

- **Stale file references** — prompt files embed relative paths to real project files (test examples, schemas, convention docs). When those source files are renamed, moved, or updated, the prompt silently generates output based on outdated context — often worse than a generic prompt because the model follows stale patterns.
- **Single-workspace scope** — prompt files in `.github/prompts/` apply only to that workspace. Teams sharing conventions across multiple repos must copy and synchronize the same files, reintroducing the prompt variation the library was meant to solve.
- **Tool unavailability degrades silently** — if a tool declared in `tools:` frontmatter is unavailable at invocation (not installed, not authorized), it is ignored without warning. Prompts that depend on specific tool access produce different results without any signal that capabilities are missing.
- **Maintenance overhead on small teams** — creating, reviewing, and updating prompt files through a PR workflow adds process. For teams with fewer than three developers or infrequent task repetition, the overhead exceeds the consistency benefit of inline prompting.

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
