---
title: "AGENTS.md: Project-Level README for AI Coding Agents"
description: "AGENTS.md is an open standard for a project-level instruction file that gives AI coding agents the context they need to work effectively in a codebase"
tags:
  - instructions
  - tool-agnostic
aliases:
  - project instruction file
  - AI agent README
---

# AGENTS.md: A README for AI Coding Agents

> AGENTS.md is an open standard for a project-level instruction file that gives AI coding agents the context they need to work effectively in a codebase.

## What AGENTS.md Is

[AGENTS.md](https://agents.md) is a markdown file placed at the root of a repository that provides project-specific guidance to AI coding agents. It functions as a README for agents: explaining the project, its conventions, its constraints, and how to navigate the codebase.

Unlike a human README — which explains what software does to someone considering using it — AGENTS.md explains how the project works to someone about to modify it. The audience is an agent beginning a task, not a developer evaluating whether to adopt a tool.

## The Discovery Convention

The convention is simple: any AI coding tool that supports AGENTS.md looks for the file at the repository root. When found, the file is loaded into the agent's context at session start. This gives the agent project context before it sees the task.

Tools that implement this convention — or their own equivalent:

| Tool | File |
|------|------|
| Any AGENTS.md-compatible tool | `AGENTS.md` |
| Claude Code | `CLAUDE.md` ([docs](https://code.claude.com/docs/en/memory)) |
| GitHub Copilot | `.github/copilot-instructions.md` ([docs](https://docs.github.com/en/copilot/concepts/about-customizing-github-copilot-chat-responses)) |

The AGENTS.md standard aims to provide a single, tool-agnostic location rather than requiring per-tool files. See [Project Instruction File Ecosystem](../instructions/instruction-file-ecosystem.md) for how these files relate.

## What to Put in AGENTS.md

AGENTS.md is project orientation, not project documentation. It answers the questions an agent needs answered before starting any task:

**Include:**

- What this project is (2–3 sentences)
- Where to find conventions, architecture docs, and workflow guides
- Non-obvious constraints: "use bun, not npm", "tests run with `bun test`"
- First steps: what to read before modifying a given area

**Exclude:**

- The conventions themselves (link to where they live)
- Architecture documentation (link to it)
- Workflow step-by-step instructions (link to them)
- Anything task-specific

The [AGENTS.md as Table of Contents](../instructions/agents-md-as-table-of-contents.md) pattern goes further: AGENTS.md should be ~100 lines of pointers, not an encyclopedia of project knowledge. The knowledge lives in a `docs/` directory that the agent navigates on demand.

## Why It Works

The mechanism is straightforward. Agents operate on context. An agent with no project context defaults to generic behavior: common tooling, conventional patterns, assumptions drawn from training data. None of these are wrong in general; most are wrong for a specific project with specific constraints.

Loading AGENTS.md at session start converts a generic agent into a project-aware one. The conversion cost is fixed (one file) and applies to every task for the life of the project.

## Relationship to Agent Skills

AGENTS.md and [Agent Skills](https://agentskills.io) are complementary. AGENTS.md provides project context — what the codebase is and how it works. Agent Skills provide task knowledge — how to perform a specific type of work. AGENTS.md tells the agent "here is the project"; a skill tells the agent "here is how to write a PR description for this project."

The distinction matters for scoping. Rules that apply to every task belong in AGENTS.md. Rules that apply to a specific task type belong in a skill loaded when that task runs.

## Example

The following AGENTS.md is from a TypeScript monorepo using Bun. It is ~60 lines of pointers and constraints — no inline documentation, no workflow tutorials.

```markdown
# AGENTS.md

## What this project is

A monorepo for the Acme platform: a REST API (`packages/api`), a React frontend
(`packages/web`), and shared utilities (`packages/shared`). The API uses Hono on
Bun; the frontend uses Vite + React.

## Runtime and tooling

- **Package manager**: `bun` — never `npm` or `yarn`
- **Test runner**: `bun test` (not `jest`, not `vitest`)
- **Lint**: `bun run lint` (Biome, not ESLint)
- **Build**: `bun run build` from the repo root builds all packages in order

## Conventions

- Shared types live in `packages/shared/src/types/` — do not redefine them in `api` or `web`
- Database migrations are in `packages/api/migrations/` — run `bun run db:migrate` to apply
- Environment variables are validated at startup in `packages/api/src/env.ts` — add new vars there

## What to read before modifying each area

| Area | Read first |
|------|-----------|
| API routes | `packages/api/docs/routing.md` |
| Auth | `packages/api/docs/auth.md` |
| Frontend state | `packages/web/docs/state-management.md` |
| Database schema | `packages/api/migrations/README.md` |

## Non-obvious constraints

- Do not commit `.env` files — use `.env.example` as the template
- `packages/shared` must remain framework-agnostic (no Hono, no React imports)
- All API responses use the envelope format defined in `packages/shared/src/types/response.ts`
```

This file converts a generic agent into a project-aware one: it knows to use `bun test`, where types live, and what to read before touching the auth layer — without embedding that documentation inline.

## Key Takeaways

- AGENTS.md is project orientation for agents: conventions, constraints, and pointers — not documentation
- The discovery convention is simple: root of the repository, loaded at session start
- It converts a generic agent into a project-aware one at fixed cost
- Keep it short (~100 lines); put knowledge in `docs/` and point to it from AGENTS.md
- AGENTS.md covers project context; Agent Skills cover task knowledge — they are complementary

## Related

- [AGENTS.md as Table of Contents, Not Encyclopedia](../instructions/agents-md-as-table-of-contents.md)
- [Cross-Tool Translation: Learning from Multiple AI Assistants](../human/cross-tool-translation.md)
- [Project Instruction File Ecosystem: CLAUDE.md, copilot-instructions, AGENTS.md](../instructions/instruction-file-ecosystem.md)
- [Standards as Agent Instructions](../instructions/standards-as-agent-instructions.md)
- [Agent Skills: Cross-Tool Task Knowledge Standard](agent-skills-standard.md)
- [llms.txt: Making Your Project Discoverable to AI Agents](llms-txt.md)
- [Agent Definition Formats: How Tools Define Agent Behavior](agent-definition-formats.md)
- [Plugin and Extension Packaging: Distributing Agent Capabilities](plugin-packaging.md)
- [Agent Cards: Capability Discovery Standard](agent-cards.md)
- [MCP: The Plumbing Behind Agent Tool Access](mcp-protocol.md)
- [Agent-to-Agent (A2A) Protocol](a2a-protocol.md)
- [Tool Calling Schema Standards](tool-calling-schema-standards.md)
