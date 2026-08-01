---
title: "AGENTS.md: Project-Level README for AI Coding Agents"
description: "AGENTS.md is an open standard for a project-level instruction file that gives AI coding agents the context they need to work effectively in a codebase."
tags:
  - instructions
  - tool-agnostic
  - standards
aliases:
  - project instruction file
  - AI agent README
last_reviewed: 2026-06-09
maturity: established
---

# AGENTS.md: Project-Level README for AI Coding Agents

> AGENTS.md is an open standard for a project-level instruction file that gives AI coding agents the context they need to work effectively in a codebase.

## What AGENTS.md is

[AGENTS.md](https://agents.md) is a markdown file at the root of a repository that gives AI coding agents project-specific guidance. It works as a README for agents: it explains the project, its conventions, its constraints, and how to navigate the codebase.

Unlike a human README — which explains what software does to someone considering using it — AGENTS.md explains how the project works to someone about to modify it. The audience is an agent beginning a task, not a developer evaluating whether to adopt a tool.

## The discovery convention

The convention is simple: any AI coding tool that supports AGENTS.md looks for the file at the repository root. The tool then loads the file into the agent's context at session start. The agent has project context before it sees the task.

Tools that implement this convention — or their own equivalent:

| Tool | File |
|------|------|
| Any AGENTS.md-compatible tool | `AGENTS.md` |
| Claude Code | `CLAUDE.md` ([docs](https://code.claude.com/docs/en/memory)) |
| GitHub Copilot | `.github/copilot-instructions.md` ([docs](https://docs.github.com/en/copilot/concepts/about-customizing-github-copilot-chat-responses)) |

The AGENTS.md standard provides a single, tool-agnostic location rather than requiring per-tool files. See [how project instruction files relate](../instructions/instruction-file-ecosystem.md) for the full picture.

## What to put in AGENTS.md

AGENTS.md is project orientation, not project documentation. It answers the questions an agent needs answered before it starts any task.

Include:

- What this project is (2 to 3 sentences)
- Where to find conventions, architecture docs, and workflow guides
- Non-obvious constraints: "use bun, not npm", "tests run with `bun test`"
- First steps: what to read before you modify a given area

Exclude:

- The conventions themselves (link to where they live)
- Architecture documentation (link to it)
- Workflow step-by-step instructions (link to them)
- Anything task-specific

The [AGENTS.md as table of contents](../instructions/agents-md-as-table-of-contents.md) pattern goes further: AGENTS.md should be about 100 lines of pointers, not an encyclopedia of project knowledge. The knowledge lives in a `docs/` directory that the agent navigates on demand.

## Why it works

The mechanism is straightforward. Agents operate on context. An agent with no [project context](../instructions/instruction-file-ecosystem.md) defaults to generic behavior: common tooling, conventional patterns, assumptions drawn from training data. None of these are wrong in general; most are wrong for a specific project with specific constraints.

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

For a real, high-profile production example, the SQLite project ships its own `AGENTS.md` ([Willison — sqlite AGENTS.md](https://simonwillison.net/2026/May/27/sqlite-agents/)) — a concrete instance of the same pointers-and-constraints shape outside this synthetic sample.

## When this backfires

AGENTS.md degrades in three conditions:

- Stale content: as the codebase evolves, AGENTS.md drifts. A file that correctly described tooling six months ago now misleads agents into using deprecated commands. Static files need active maintenance — they do not self-update as conventions change.
- Context overconsumption: every line in AGENTS.md consumes context budget before the agent sees the task. Verbose files — architecture writeups, process narratives, duplicated documentation — crowd out room for the task itself. An [ETH Zurich evaluation of AGENTS.md](https://arxiv.org/abs/2602.11988) found context files increased inference cost by over 20% on average, largely because agents followed their instructions into broader-than-necessary exploration. The file works against itself when it embeds knowledge instead of linking to it.
- Mismatch with dynamic environments: AGENTS.md is a static snapshot. A single root file serves projects poorly when they have frequent toolchain changes, several distinct workflows, or constraints that vary per run. MCP servers or runtime-loaded skill files handle dynamic context better than a committed static document.

## FAQ

**How is AGENTS.md different from a README?**

The audience and the moment differ. A human README explains what the software does to someone considering using it; AGENTS.md explains how the project works to someone about to modify it. The reader is an agent beginning a task, not a developer evaluating whether to adopt a tool, so the content is conventions, constraints, and navigation pointers.

**Does adding an AGENTS.md cost anything?**

Yes. Every line consumes context budget before the agent sees the task, and an [ETH Zurich evaluation of AGENTS.md](https://arxiv.org/abs/2602.11988) found context files increased inference cost by over 20% on average, largely because agents followed their instructions into broader-than-necessary exploration. Verbose files — architecture writeups, process narratives, duplicated documentation — crowd out room for the task itself.

**When is a single root file the wrong fit?**

When the environment is not static. AGENTS.md is a snapshot, so it serves projects poorly when they have frequent toolchain changes, several distinct workflows, or constraints that vary per run; MCP servers or runtime-loaded skill files handle dynamic context better. The same risk applies over time, since a file that described tooling correctly six months ago now points agents at deprecated commands.

## Key Takeaways

- AGENTS.md is project orientation for agents: conventions, constraints, and pointers — not documentation
- The discovery convention is simple: root of the repository, loaded at session start
- It converts a generic agent into a project-aware one at fixed cost
- Keep it short (~100 lines); put knowledge in `docs/` and point to it from AGENTS.md
- AGENTS.md covers project context; Agent Skills cover task knowledge — they are complementary

## Related

- [Project Instruction File Ecosystem: CLAUDE.md, copilot-instructions, AGENTS.md](../instructions/instruction-file-ecosystem.md)
- [AGENTS.md as Table of Contents, Not Encyclopedia](../instructions/agents-md-as-table-of-contents.md)
- [Standards as Agent Instructions](../instructions/standards-as-agent-instructions.md)
- [Agent Skills: Cross-Tool Task Knowledge Standard](agent-skills-standard.md)
- [llms.txt: Making Your Project Discoverable to AI Agents](llms-txt.md)
- [Agent Definition Formats: How Tools Define Agent Behavior](agent-definition-formats.md)
- [Agent Cards: Capability Discovery Standard](agent-cards.md)
- [Cross-Tool Translation: Learning from Multiple AI Assistants](../human/cross-tool-translation.md)
