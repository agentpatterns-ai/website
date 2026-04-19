---
title: "AGENTS.md as a Table of Contents, Not an Encyclopedia"
description: "Keep AGENTS.md to ~100 lines as a pointer map and put structured knowledge in a versioned docs/ directory treated as the system of record."
tags:
  - context-engineering
  - instructions
aliases:
  - Pointer Map
  - AGENTS.md Content Strategy
---

# AGENTS.md as a Table of Contents, Not an Encyclopedia

> Keep AGENTS.md to ~100 lines as a pointer map; put structured knowledge in a versioned docs/ directory treated as the system of record.

!!! info "Also known as"
    Pointer Map, AGENTS.md Content Strategy. For the complementary pattern on **where** to place AGENTS.md files (distributed across directory levels), see [Encode Project Conventions in Distributed AGENTS.md Files](agents-md-distributed-conventions.md).

## Why Monolithic AGENTS.md Files Fail

The OpenAI Harness team identified "one big AGENTS.md" as an early failure mode with four specific consequences ([OpenAI Harness Engineering](https://openai.com/index/harness-engineering/)):

1. **Context crowding.** A large AGENTS.md consumes context space that should be available for the task, the relevant code, and the documentation for that specific problem. Agents have less room to reason about the actual work.

2. **Attention dilution.** When every instruction is present simultaneously, no instruction is prominent. Agents pattern-match locally rather than navigating intentionally to the relevant section of the knowledge base.

3. **Unverifiable scope.** A monolithic file grows without clear ownership. Agents cannot tell which sections are current; humans stop maintaining it because the file is intimidating to edit.

4. **Instant rot.** Architectural decisions change. A single file updated piecemeal accumulates contradictions. What was true at month one is stale by month six, but the file still reads as authoritative.

## The Pattern: Pointer Map + Structured Docs

The fix is a structural one: AGENTS.md is a brief index — what this project is, where conventions live, what to read first for each type of task. The knowledge itself lives in a versioned `docs/` directory.

```
AGENTS.md                    # ~100 lines: what, where, first steps
docs/
  architecture/              # ADRs, system design, key decisions
  conventions/               # Coding standards, naming, patterns
  workflows/                 # How to do common tasks
  onboarding/                # What agents need before starting a task
```

An AGENTS.md entry looks like: *"For API conventions, see `docs/conventions/api.md`. For deployment procedures, see `docs/workflows/deploy.md`."* The agent follows the pointer when it needs that context, rather than having it preloaded.

This follows the same principle as [retrieval-augmented context loading](../context-engineering/retrieval-augmented-agent-workflows.md): pull context when needed, not at session start.

## Enforcing Freshness Mechanically

Pointers only work if the linked documents exist and are current. The Harness team runs "dedicated linters and CI jobs [that] validate that the knowledge base is up to date, cross-linked, and structured correctly," plus a recurring "doc-gardening" agent that scans for obsolete documentation and opens fix-up pull requests ([OpenAI Harness Engineering](https://openai.com/index/harness-engineering/)). Mechanical enforcement of this kind is the same class of deterministic sensor that Martin Fowler catalogs as part of the harness: tests, linters, type checkers, and structural analysis that run fast and produce reliable signals ([Martin Fowler — Harness Engineering](https://martinfowler.com/articles/harness-engineering.html)).

Practical approaches:

- CI that breaks if AGENTS.md contains a broken link to docs/
- Lint rules that flag docs/ files not referenced from AGENTS.md
- Automated prompts to review docs/ files older than a set threshold

## What Belongs in AGENTS.md

| Include | Exclude |
|---------|---------|
| Project overview (2-3 sentences) | Full architectural documentation |
| Pointer to conventions docs | The conventions themselves |
| Pointer to workflow docs | Step-by-step workflow instructions |
| Key constraints (1-2 critical rules) | Exhaustive rule lists |
| First steps for new agents | Background context and history |

The test: would removing this line require a pointer to docs/ instead? Put it in docs/. Would removing it leave agents with no path to a critical concept? It belongs in AGENTS.md as a pointer.

## Example

Below is an AGENTS.md for a TypeScript monorepo that follows the pointer-map pattern. Each entry names the concept and links to the document that contains the actual content — nothing is expanded inline.

```markdown
# Acme Monorepo — Agent Instructions

## What this repo is
A TypeScript monorepo with three packages: `api` (Fastify), `web` (Next.js), and `shared` (types + utils).
Primary language: TypeScript 5.x. Package manager: pnpm workspaces.

## Before starting any task
1. Run `pnpm typecheck` to confirm the type baseline.
2. Run `pnpm test` to confirm no pre-existing failures.

## Key pointers
- Coding conventions and naming rules → `docs/conventions/coding-standards.md`
- How to add a new API route → `docs/workflows/add-api-route.md`
- How to add a new UI page → `docs/workflows/add-ui-page.md`
- ADRs and architecture decisions → `docs/architecture/`
- Deployment procedure → `docs/workflows/deploy.md`
- Do NOT modify `packages/shared/generated/` — these files are auto-generated by `pnpm codegen`

## Critical constraints
- All public functions in `packages/shared` must have JSDoc with `@param` and `@returns`.
- Database migrations live in `packages/api/migrations/`; never edit them after they have run in production.
```

The AGENTS.md is under 30 lines. The conventions, workflow steps, and architectural history are each in their own versioned file. A CI lint step can check that every path under `## Key pointers` resolves to a real file:

```bash
# scripts/lint-agents-md.sh — run in CI
grep -oP '(?<=→ `)docs/[^`]+' AGENTS.md | while read -r path; do
  if [ ! -e "$path" ] && [ ! -d "$path" ]; then
    echo "AGENTS.md broken link: $path"
    exit 1
  fi
done
```

If any linked document is deleted or renamed without updating AGENTS.md, the CI job fails before the stale pointer reaches a running agent.

## When This Backfires

The pointer-map pattern assumes the agent will follow pointers on demand. An ETH Zurich study of 138 Python tasks across four agents found that repository-level context files — even human-written ones — consistently drive up inference cost by raising the number of agent steps by 19-20%, and that LLM-generated context files reduced task success by ~3% on average compared to no context file at all ([Gloaguen et al. 2026, *Evaluating AGENTS.md*](https://arxiv.org/abs/2602.11988)). The pattern is worse than the alternative when:

- **The repository is small or conventional.** If a single `README.md` and obvious file layout already answer "what is this and where does it live," an AGENTS.md pointer map just adds tokens without directing behavior.
- **Agents do not reliably follow pointers.** Some agent harnesses pre-load AGENTS.md but never traverse the linked docs, leaving the agent with a table of contents and no content. The study found instructions are followed, but context files "do not function as effective repository overviews."
- **The docs/ directory is drafted by an agent rather than maintained by humans.** LLM-generated context files in the study degraded performance; without the discipline of human authorship and the CI/doc-gardening machinery described above, the pointer map decays into stale links.

## Key Takeaways

- Monolithic AGENTS.md crowds context, dilutes attention, and rots — structural fix: a ~100-line pointer map backed by a versioned `docs/` directory.
- Enforce freshness mechanically — CI link validation is more reliable than human maintenance.
- The principle is tool-agnostic: applies equally to CLAUDE.md, Copilot instructions, and Cursor rules.

## Related

- [Encode Project Conventions in Distributed AGENTS.md Files](agents-md-distributed-conventions.md) — complementary technique covering *where* to place AGENTS.md files
- [AGENTS.md Design Patterns: Commands, Boundaries, and Personas](agents-md-design-patterns.md) — structural patterns for organizing AGENTS.md content
- [Evaluating AGENTS.md: When Context Files Hurt More Than Help](evaluating-agents-md-context-files.md) — research on when AGENTS.md files degrade agent performance
- [Retrieval-Augmented Agent Workflows](../context-engineering/retrieval-augmented-agent-workflows.md) — the broader principle of pulling context on demand
- [AGENTS.md: A README for AI Coding Agents](../standards/agents-md.md) — the underlying AGENTS.md standard
- [Hierarchical CLAUDE.md: Structuring Context Files at Multiple Levels](hierarchical-claude-md.md) — layering instruction files across directory levels
- [Separation of Knowledge and Execution](../agent-design/separation-of-knowledge-and-execution.md) — why knowledge belongs in docs, not instructions
- [Harness Engineering](../agent-design/harness-engineering.md) — the discipline of designing agent environments so agents succeed by default
