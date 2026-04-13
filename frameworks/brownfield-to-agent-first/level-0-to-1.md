---
title: "L0 → L1: Making the Repo Readable"
description: "Transform a Human-Only codebase (L0) into an Agent-Readable one (L1) by externalizing implicit knowledge: project instructions, documented architecture, and a CI baseline."
tags:
  - training
  - agent-design
  - workflows
  - tool-agnostic
---

# L0 → L1: Making the Repo Readable

> Agents cannot orient in a codebase that relies on [tribal knowledge](../../anti-patterns/implicit-knowledge-problem.md). The L0→L1 transition externalizes what humans carry in their heads — architecture, conventions, build commands — into structured, machine-readable artifacts.

---

## What L0 Looks Like

An L0 codebase relies on [implicit knowledge](../../anti-patterns/implicit-knowledge-problem.md) — conventions, decisions, and constraints that exist only in Slack threads and team memory:

- No project instructions file — a new agent session starts with no context
- Directory structure reflects historical accident, not architectural intent
- Build and test commands are passed verbally ("you have to run `npm run dev:local` not `npm start`")
- Conventions exist but are not written down ("we never put business logic in the route handlers")
- No CI — tests run manually if they run at all

Agents operating on an L0 repo invent rather than extrapolate. They pick arbitrary directories for new files, reproduce deprecated patterns, and miss non-obvious constraints. Every session needs significant hand-holding to stay on track.

## What L1 Looks Like

At L1, the agent can read the repo and understand the system without being told:

- A project instructions file provides architecture, conventions, and workflow commands
- Directory structure maps to architectural layers
- CI runs on every commit with at minimum lint, build, and smoke tests
- The agent can explain system components and produce accurate architectural summaries

**Exit criterion**: A fresh agent session (no prior context) can produce an accurate description of the repo's architecture and correctly locate where a new feature file should go.

---

## The L0 → L1 Transformation

### Step 1: Write the Project Instructions File

The project instructions file ([CLAUDE.md](../../instructions/instruction-file-ecosystem.md), [AGENTS.md](../../standards/agents-md.md), [`.github/copilot-instructions.md`](https://docs.github.com/en/copilot/concepts/about-customizing-github-copilot-chat-responses)) is the single highest-leverage action for an L0 repo. It gives every agent session persistent context that cannot be inferred from code alone.

Anthropic's `/init` command analyzes your codebase and generates a starter `CLAUDE.md` automatically ([Claude Code Best Practices](https://code.claude.com/docs/en/best-practices)). Run it, then refine the output.

**What to include** — only content that would cause mistakes if absent:

```markdown
# Architecture
- src/routes/ → src/services/ → src/repositories/ → Postgres via Drizzle ORM
- Each layer has one responsibility. Routes validate and respond. Services orchestrate. Repositories query.
- Error classes in src/errors/ — throw AppError subclasses, never raw Error objects.

# Build and Test
- `npm run dev` — starts dev server on :3000
- `npm test` — runs Vitest against a local test DB (requires Docker: `docker-compose up db`)
- `npm run lint` — ESLint with custom import-boundary rules

# Key Conventions
- API pagination is 1-based, not 0-based (see docs/conventions/pagination.md)
- All timestamps stored in UTC; never convert at the DB layer
```

**What to exclude** — anything the agent can figure out by reading the code:

| Exclude | Reason |
|---------|--------|
| Standard language conventions ("use `const`") | Agent already knows these |
| Rules ESLint already enforces | Linter provides the feedback |
| File-by-file descriptions | Agent reads files directly |
| Information that changes frequently | Becomes stale; causes confusion |

Treat CLAUDE.md like code: prune it when things it says become inconsistent with how the agent behaves. A bloated CLAUDE.md causes the agent to ignore it ([Anthropic](https://code.claude.com/docs/en/best-practices)).

### Step 2: Document the Architecture

Write an architecture document that covers what cannot be inferred from code structure:

- **Layer diagram** — which layer depends on which, enforced or conventional
- **Key decisions** — "we chose Drizzle over Prisma because X" prevents the agent from "fixing" deliberate choices
- **Constraint rationale** — "never call the payment API directly from routes — always go through PaymentService" with the reason

Keep this document short and accurate. An outdated architecture document is worse than none: the agent will try to follow it and produce incorrect output.

Reference the document from CLAUDE.md:

```markdown
# Architecture
See docs/architecture/overview.md for the full architecture diagram and layer rules.
Summary: routes → services → repositories → Postgres
```

### Step 3: Make the Directory Structure Self-Describing

Directory structure is the first context an agent reads. When directories map to architectural layers with consistent naming, the agent can infer where files belong without being told.

**Before (L0 — reflects historical accident):**
```
src/
  api/
    user.js        # route handler
    db.js          # database access mixed in
  models/
    user.js        # sometimes a model, sometimes a service
  util/
    everything.js  # utility functions, business logic, and DB queries
```

**After (L1 — maps to architecture):**
```
src/
  routes/          # HTTP handlers only — validate input, call services, return responses
  services/        # Business logic — orchestrate repositories, no direct DB
  repositories/    # Database access only — uses Drizzle ORM
  types/           # Shared TypeScript types and interfaces
  errors/          # AppError subclasses — throw these everywhere
  config/          # Environment configuration
```

When renaming directories is not practical immediately, document the actual structure in CLAUDE.md including its known inconsistencies:

```markdown
# Known Structure Inconsistencies
- `src/models/` contains both data models and business logic — refactoring in progress
- New code: follow the services/repositories split documented in architecture.md
- Existing code in `src/models/`: treat as services if it has business logic
```

Documenting known inconsistencies prevents the agent from replicating the legacy pattern in new code.

### Step 4: Establish a CI Baseline

A CI pipeline that runs on every commit is prerequisite infrastructure for every subsequent level. At L1, the bar is low: lint, build, and smoke tests.

A minimal GitHub Actions configuration:

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run lint
      - run: npm run build
      - run: npm test -- --run    # non-interactive for CI
```

If you have no tests, `npm test -- --run` with zero tests still validates the test runner is configured. Add smoke tests for the most critical path (e.g., the app starts and the health endpoint responds) before moving to L2.

### Step 5: Verify the Transition

Run this exit check:

1. Start a new agent session with no context
2. Ask: "Describe this codebase's architecture and where I should add a new user-facing feature"
3. The response should correctly name the layers, identify the right directories, and reference the conventions in your project instructions file

If the agent invents architecture or mislocates new code, your project instructions or directory structure needs more clarity.

---

## When This Backfires

**CLAUDE.md becomes a liability.** Instructions added early become stale as the codebase evolves. A CLAUDE.md that says "routes use Express middleware" when the team has migrated to a different pattern actively misdirects agents — stale instructions produce more errors than no instructions. Treat CLAUDE.md as production code: prune on every significant architectural change, not just when agents start behaving oddly.

**Architecture documents drift faster than code.** A diagram created at L1 that says "routes → services → repositories" becomes incorrect the moment the team introduces a message queue, an event layer, or a service mesh. Agents read the document before reading the code. An outdated architecture document causes agents to pattern-match against the wrong structure and place new code incorrectly. Keep architecture documents short enough to update in minutes, not hours.

**Directory restructuring has a high blast radius.** Renaming `src/models/` to `src/services/` touches every import in every file. On a large brownfield codebase, a directory rename can generate hundreds of merge conflicts and break CI for a day. For teams without strong test coverage or automated import rewriting, the cost of restructuring outweighs the benefit until L2 (when CI is reliable enough to catch breakage). Prefer documenting the inconsistency in CLAUDE.md over restructuring when the codebase is too fragile.

**CI setup stalls on legacy test suites.** "Add smoke tests" is straightforward on a greenfield project. On a brownfield repo with no tests or a flaky, slow suite, getting CI green can take weeks. If CI is blocked on test quality, start with a build-only gate (`npm run build`) and lint. A consistent build check provides most of the L1 value until tests are reliable enough to run in CI.

---

## Key Takeaways

- The project instructions file is the single highest-leverage action for an L0 repo. Generate it with `/init` (Claude Code) and refine from there.
- Include only what would cause mistakes if absent. A concise, accurate file beats a comprehensive, stale one.
- Directory structure communicates architecture. Renaming directories to reflect architectural layers is one of the highest-ROI refactors for agent-assisted development.
- Document known inconsistencies explicitly. An undocumented inconsistency will be replicated; a documented one can be avoided.
- CI baseline is prerequisite infrastructure. Every subsequent level depends on it.

## Related

- [Instruction File Ecosystem](../../instructions/instruction-file-ecosystem.md) — CLAUDE.md, AGENTS.md, `.github/copilot-instructions.md` and how they interact
- [AGENTS.md Standard](../../standards/agents-md.md) — open standard for cross-tool agent project instructions
- [Codebase Readiness for Agents](../../workflows/codebase-readiness.md) — agent-hostile vs agent-friendly code qualities
- [Harness Engineering](../../agent-design/harness-engineering.md) — the full discipline this transition begins
- [L1 → L2: Adding Feedback Loops](level-1-to-2.md) — next module
