---
title: "copilot-instructions.md as a Repo-Level Instruction Convention"
description: ".github/copilot-instructions.md is GitHub Copilot's repository-level instruction file that injects project context into every Copilot interaction automatically."
aliases:
  - Copilot Instruction File
  - copilot-instructions.md
tags:
  - instructions
  - copilot
---

# copilot-instructions.md as a Repo-Level Instruction Convention

> `.github/copilot-instructions.md` is GitHub Copilot's repository-level instruction file -- a single Markdown file that injects project context into every Copilot interaction without repeating it per prompt.

??? note "Also known as: Instruction File Convention, Project Instruction Files"
    Copilot-specific convention. See also [Instruction File Ecosystem](../../instructions/instruction-file-ecosystem.md) (tool-agnostic) and [CLAUDE.md Convention](../../instructions/claude-md-convention.md).

## What It Does

Copilot reads `.github/copilot-instructions.md` on every chat request, [agent mode](agent-mode.md) session, [coding agent](coding-agent.md) task, and code review ([docs](https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot), [GitHub Blog](https://github.blog/ai-and-ml/unlocking-the-full-power-of-copilot-code-review-master-your-instructions-files/)). Contents are appended to the system prompt automatically -- no reference or import needed.

## File Location and Format

Place the file at `.github/copilot-instructions.md`. Standard Markdown. Keep it under two pages ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/5-tips-for-writing-better-custom-instructions-for-copilot/)) -- files approaching 1,000 lines degrade code review consistency ([GitHub Blog](https://github.blog/ai-and-ml/unlocking-the-full-power-of-copilot-code-review-master-your-instructions-files/)).

## What to Include

GitHub [recommends](https://github.blog/ai-and-ml/github-copilot/5-tips-for-writing-better-custom-instructions-for-copilot/) five categories:

1. **Project overview** -- purpose, audience, key features.
2. **Tech stack** -- frameworks, ORMs, runtimes, test runners.
3. **Coding guidelines** -- naming, error handling, formatting.
4. **Project structure** -- folder layout and directory purposes.
5. **Available resources** -- scripts, automation, MCP servers.

For the [coding agent](coding-agent.md), add exact build/test commands, environment setup, and CI requirements ([docs](https://docs.github.com/copilot/how-tos/agents/copilot-coding-agent/best-practices-for-using-copilot-to-work-on-tasks)).

## What Not to Include

- **Task-specific instructions** -- belong in the prompt or path-specific files ([docs](https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot)).
- **Full documentation** -- link instead of embedding. Exception: code review cannot follow links, so inline review-specific content ([GitHub Blog](https://github.blog/ai-and-ml/unlocking-the-full-power-of-copilot-code-review-master-your-instructions-files/)).
- **Vague directives** -- "be more accurate" wastes tokens; use imperative rules.
- **Narrative prose** -- lists and headings work more reliably than paragraphs ([GitHub Blog](https://github.blog/ai-and-ml/unlocking-the-full-power-of-copilot-code-review-master-your-instructions-files/)).
- **Tool-specific syntax** -- Claude Code or Cursor directives are ignored; keep the file Copilot-specific or tool-neutral.

## Instruction Hierarchy

Copilot combines instructions from three scopes; higher-priority scopes win on conflict ([docs](https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot)):

| Priority | Scope | Where configured |
|----------|-------|------------------|
| 1 (highest) | Personal | GitHub.com user settings |
| 2 | Repository | `.github/copilot-instructions.md` |
| 3 (lowest) | Organization | Organization-level Copilot settings |

## Path-Specific Instructions

For file-specific rules, create `*.instructions.md` files in `.github/instructions/` with an `applyTo` glob ([docs](https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot)):

```markdown
---
applyTo: "**/*.py"
---
Use type hints on all function signatures. Prefer `pathlib` over `os.path`.
```

These files also support `excludeAgent` (`"code-review"` or `"coding-agent"`) to skip a feature. Move language-specific rules here to keep the repo-wide file short.

## Feature Support Matrix

Support varies by IDE ([docs](https://docs.github.com/en/copilot/reference/custom-instructions-support)):

| Platform | Chat | Code Review | Coding Agent |
|----------|------|-------------|--------------|
| VS Code | Repo + Path + Agent | Repo + Path | Repo + Path + Agent |
| JetBrains | Repo + Path + Agent | Repo + Path | Repo + Path + Agent |
| GitHub.com | Repo + Path + Personal | Repo + Path + Org | Repo + Path + Agent |
| Visual Studio | Repo only | Repo only | -- |
| Xcode | Repo + Path | Repo + Path | Repo + Path + Agent |

## copilot-instructions.md vs. AGENTS.md

| Dimension | copilot-instructions.md | AGENTS.md |
|-----------|------------------------|-----------|
| Standard | GitHub Copilot proprietary | [Open standard](https://agents.md) |
| Read by | GitHub Copilot features | Any AGENTS.md-compatible tool |
| Location | `.github/copilot-instructions.md` | `AGENTS.md` at repo root |
| Hierarchy | Flat + path-specific | Directory-level traversal |
| Portability | Copilot only | Cross-tool |

Multi-tool teams can maintain both or consolidate into AGENTS.md (losing path-specific `applyTo` globs). See [Instruction File Ecosystem](../../instructions/instruction-file-ecosystem.md) for convergence strategies.

## When This Backfires

- **Over-stuffed files**: Implementation details, full documentation, or task-specific context bloat the system prompt and consume token budget that would otherwise hold conversation or code context. Stick to project-wide rules ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/5-tips-for-writing-better-custom-instructions-for-copilot/)).
- **Personal settings override**: Personal-scope instructions silently override repository instructions on conflict, so teammates with conflicting personal Copilot settings see different behavior.
- **IDE feature gaps**: Visual Studio only reads the repo-wide file -- path-specific and organization scopes are unsupported, so `applyTo` workflows break silently there.
- **Instructions don't guarantee compliance**: GitHub notes that "providing instructions doesn't guarantee perfect code" -- the same request can yield different results across sessions ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/5-tips-for-writing-better-custom-instructions-for-copilot/)). Treat instructions as a probabilistic nudge, not a contract.

## Example

A minimal `copilot-instructions.md` for a Node.js API project:

```markdown
# Project Overview

REST API for order management. Node.js 20, Express, PostgreSQL, Prisma ORM.

# Tech Stack

- Runtime: Node.js 20 (ESM)
- Framework: Express 5
- Database: PostgreSQL 16 via Prisma
- Tests: Vitest + Supertest
- CI: GitHub Actions

# Coding Guidelines

- TypeScript strict mode. No `any`.
- Use `zod` for request validation.
- Prefer named exports.
- Error responses follow RFC 9457 (Problem Details).

# Build & Test

- `npm run build` — compile TypeScript
- `npm test` — run Vitest suite
- `npm run lint` — ESLint + Prettier check

# Project Structure

- `src/routes/` — Express route handlers
- `src/services/` — business logic
- `src/db/` — Prisma client and migrations
- `tests/` — integration and unit tests
```

## Key Takeaways

- `.github/copilot-instructions.md` is appended to Copilot's system prompt on every chat, agent mode, coding agent, and code review interaction -- no import needed.
- Keep it under two pages; cover project overview, tech stack, coding guidelines, structure, and available resources.
- Personal scope outranks repository scope, which outranks organization scope -- conflicting personal settings silently override team intent.
- Move language- or path-specific rules into `.github/instructions/*.instructions.md` with `applyTo` globs; Visual Studio ignores them.
- Compared to `AGENTS.md`: Copilot-proprietary, flat plus path-specific, single location -- not portable to other tools.

## Related

- [Project Instruction File Ecosystem](../../instructions/instruction-file-ecosystem.md)
- [AGENTS.md: A README for AI Coding Agents](../../standards/agents-md.md)
- [Layer Agent Instructions by Specificity](../../instructions/layered-instruction-scopes.md)
- [Instruction Polarity](../../instructions/instruction-polarity.md)
- [GitHub Copilot Agent Mode](agent-mode.md)
- [GitHub Copilot Coding Agent](coding-agent.md)
- [Custom Agents, Skills & Plugins](custom-agents-skills.md)
- [GitHub Copilot MCP Integration](mcp-integration.md)
