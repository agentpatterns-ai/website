---
title: "AGENTS.md as a Table of Contents, Not an Encyclopedia"
description: "Keep AGENTS.md to ~100 lines as a pointer map, put structured knowledge in a versioned docs/ directory, and tag every terminal rule with source, applicability, and expiry so the file is self-pruning under periodic audit."
tags:
  - context-engineering
  - instructions
  - tool-agnostic
aliases:
  - Pointer Map
  - AGENTS.md Content Strategy
last_reviewed: 2026-06-13
maturity: established
---

# AGENTS.md as a Table of Contents, Not an Encyclopedia

> Keep AGENTS.md to ~100 lines as a pointer map into a versioned docs/ directory, and tag each terminal rule with source, applicability, and expiry.

Learn it hands-on: [Instruction Files and Altitude](https://learn.agentpatterns.ai/harness-engineering/instruction-files-and-altitude/) — guided lesson with quizzes.

!!! info "Also known as"
    Pointer Map, AGENTS.md Content Strategy. For the complementary pattern on where to place AGENTS.md files (distributed across directory levels), see [Encode Project Conventions in Distributed AGENTS.md Files](agents-md-distributed-conventions.md).

## Why monolithic AGENTS.md files fail

The OpenAI Harness team identified "one big AGENTS.md" as an early failure mode with four specific consequences ([OpenAI Harness Engineering](https://openai.com/index/harness-engineering/)):

1. Context crowding. A large AGENTS.md consumes context space that should belong to the task, the relevant code, and that problem's documentation. That leaves agents less room to reason about the actual work.

2. Attention dilution. When every instruction is present at once, none is prominent. Agents pattern-match locally rather than navigate to the relevant section of the knowledge base.

3. Unverifiable scope. A monolithic file grows without clear ownership — the same unbounded accumulation described by [the instruction compliance ceiling](instruction-compliance-ceiling.md). Agents cannot tell which sections are current, and humans stop maintaining it because it is intimidating to edit.

4. Instant rot. Architectural decisions change, and a file updated piecemeal accumulates contradictions. What was true at month one is stale by month six, but still reads as authoritative.

## The pattern: pointer map plus structured docs

The fix is structural. AGENTS.md is a brief index — what this project is, where conventions live, what to read first per task type. The knowledge itself lives in a versioned `docs/` directory.

```
AGENTS.md                    # ~100 lines: what, where, first steps
docs/
  architecture/              # ADRs, system design, key decisions
  conventions/               # Coding standards, naming, patterns
  workflows/                 # How to do common tasks
  onboarding/                # What agents need before starting a task
```

An AGENTS.md entry looks like: "For API conventions, see `docs/conventions/api.md`. For deployment procedures, see `docs/workflows/deploy.md`." The agent follows the pointer when it needs that context, rather than having it preloaded.

This follows the same principle as [retrieval-augmented context loading](../context-engineering/retrieval-augmented-agent-workflows.md): pull context when needed, not at session start.

## Enforcing freshness mechanically

Pointers only work if the linked documents exist and are current. The Harness team runs "dedicated linters and CI jobs [that] validate that the knowledge base is up to date, cross-linked, and structured correctly," plus a recurring "doc-gardening" agent that scans for obsolete documentation and opens fix-up pull requests ([OpenAI Harness Engineering](https://openai.com/index/harness-engineering/)). Mechanical enforcement of this kind is the same class of deterministic sensor that Martin Fowler catalogs as part of the harness: tests, linters, type checkers, and structural analysis that run fast and produce reliable signals ([Martin Fowler — Harness Engineering](https://martinfowler.com/articles/harness-engineering.html)).

Practical approaches:

- CI that breaks if AGENTS.md contains a broken link to docs/
- Lint rules that flag docs/ files not referenced from AGENTS.md
- Automated prompts to review docs/ files older than a set threshold

## Rule lifecycle metadata

The pointer map controls AGENTS.md size structurally. [Lifecycle metadata](rule-lifecycle-metadata.md) controls it over time — without it, the same one-way ratchet refills the file. The walkinglabs harness-engineering lecture names the failure mode directly: "agent makes a mistake, you say 'add a rule to prevent this,' add it to AGENTS.md, it works temporarily, agent makes a different mistake, add another rule, repeat, file bloats out of control" ([walkinglabs lecture 04](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/lectures/lecture-04-why-one-giant-instruction-file-fails/index.md)). Each addition is one-way because no one can tell what is safe to delete.

The discipline that closes the loop is per-rule metadata. The walkinglabs lecture prescribes three fields for every rule:

- Source — "why was this rule added?" The failure mode, PR comment, or incident that produced it. Auditable provenance: `git blame` answers who and when, but not why.
- Applicability — "when is this rule needed?" The condition under which it fires: file pattern, task type, branch — the same scoping axes covered in [layered instruction scopes](layered-instruction-scopes.md). Rules that "always apply" are usually misformed, because the failure mode being prevented has a scope.
- Expiry — "under what circumstances can this rule be removed?" The observable that retires it: model capability rises, feature removed, never fires for N weeks.

## Expiry as a closed-form deletion predicate

The framing the walkinglabs lecture uses: "Manage your instructions like you manage code dependencies — unused dependencies should be deleted, otherwise they just slow the system down." The metadata converts deletion from an open-ended judgment call into a closed-form predicate — has the expiry observable fired? With the predicate, the default flips from "keep when uncertain" to "delete when expired."

Anthropic's own Claude Code best-practices teaches a compatible discipline without naming the triple: "Treat CLAUDE.md like code: review it when things go wrong, prune it regularly, and test changes by observing whether Claude's behavior actually shifts." and "If Claude already does something correctly without the instruction, delete it or convert it to a hook." ([Claude Code best practices](https://code.claude.com/docs/en/best-practices)). "Already does it correctly" is one expiry observable; "feature removed" and "never fired in N weeks" are others.

## Compact format for lifecycle metadata

The metadata cannot itself bloat the file — that defeats the purpose. Keep it inline as a one-line YAML or HTML-comment annotation on terminal rules (rules that prescribe behavior). Pointers and structural sections do not need metadata; following the [separation of knowledge and execution](../agent-design/separation-of-knowledge-and-execution.md), the linked doc carries its own.

```markdown
## Critical constraints

<!-- source: incident 2025-03-14 (prod migration rolled back)
     applicability: any edit under packages/api/migrations/
     expiry: when migration tool gains pre-flight dry-run flag -->
- Database migrations live in `packages/api/migrations/`; never edit them after they have run in production.

<!-- source: PR #1842 review comment from @security-team
     applicability: any new function in packages/shared/
     expiry: when TypeDoc generation lands in CI (issue #2103) -->
- All public functions in `packages/shared` must have JSDoc with `@param` and `@returns`.
```

The annotations are HTML comments so they render invisibly in GitHub previews but remain visible to agents reading the file. A quarterly audit script can grep for `expiry:` lines, evaluate the observable (was the migration flag added? did TypeDoc land?), and open a PR removing rules whose expiry has fired.

## When to skip the metadata

The discipline pays off when ownership rotates and the rule set is large enough that no one carries the full provenance in their head. Skip the annotation overhead when:

- The repo has fewer than ~10 terminal rules. A quarterly visual scan catches stale rules without per-line annotation.
- A single author owns AGENTS.md. They hold source, applicability, and expiry in working memory, so written metadata adds maintenance without preventing rot.
- The expiry is already tracked elsewhere as the source of truth. A rule like "use Python 3.12 syntax" has its expiry encoded in `pyproject.toml`, and duplicating it into the rule creates two places to update.
- The line is a pointer, not a terminal rule. Pointers route to docs/, and the linked doc carries its own provenance and review cadence.

## What belongs in AGENTS.md

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

## When this backfires

The pointer-map pattern assumes the agent will follow pointers on demand. An ETH Zurich study of 138 Python tasks across four agents found that repository-level context files — even human-written ones — consistently raise inference cost by adding 19-20% more agent steps, and that LLM-generated context files reduced task success by ~3% on average compared to no context file at all ([Gloaguen et al. 2026, Evaluating AGENTS.md](https://arxiv.org/abs/2602.11988)). The pattern is worse than the alternative when:

- The repository is small or conventional. If a single `README.md` and obvious file layout already answer "what is this and where does it live," an AGENTS.md pointer map just adds tokens without directing behavior.
- Agents do not reliably follow pointers. Some agent harnesses pre-load AGENTS.md but never traverse the linked docs, which leaves the agent with a table of contents and no content. The study found instructions are followed, but context files "do not function as effective repository overviews."
- The docs/ directory is drafted by an agent rather than maintained by humans. LLM-generated context files in the study degraded performance. Without the discipline of human authorship and the CI and doc-gardening machinery described above, the pointer map decays into stale links.

## Key Takeaways

- Monolithic AGENTS.md crowds context, dilutes attention, and rots — structural fix: a ~100-line pointer map backed by a versioned `docs/` directory.
- Pointer maps fix size structurally; per-rule source/applicability/expiry metadata fixes it temporally — together the file is self-pruning under periodic audit.
- Enforce freshness mechanically — CI link validation and expiry-observable audits are more reliable than human maintenance.
- The principle is tool-agnostic: applies equally to CLAUDE.md, Copilot instructions, and Cursor rules.

## Related

- [Encode Project Conventions in Distributed AGENTS.md Files](agents-md-distributed-conventions.md) — complementary technique covering *where* to place AGENTS.md files
- [AGENTS.md Design Patterns: Commands, Boundaries, and Personas](agents-md-design-patterns.md) — structural patterns for organizing AGENTS.md content
- [Evaluating AGENTS.md: When Context Files Hurt More Than Help](evaluating-agents-md-context-files.md) — research on when AGENTS.md files degrade agent performance
- [AGENTS.md: A README for AI Coding Agents](../standards/agents-md.md) — the underlying AGENTS.md standard
- [Hierarchical CLAUDE.md: Structuring Context Files at Multiple Levels](hierarchical-claude-md.md) — layering instruction files across directory levels
- [Separation of Knowledge and Execution](../agent-design/separation-of-knowledge-and-execution.md) — why knowledge belongs in docs, not instructions
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md) — why unbounded rule growth degrades agent behavior; the mechanism lifecycle metadata defends against
- [Harness Engineering](../agent-design/harness-engineering.md) — the discipline of designing agent environments so agents succeed by default
