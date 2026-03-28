---
title: "GitHub Copilot: Harness Engineering for Agent-Ready Code"
description: "Make your codebase agent-ready with backpressure, repo legibility, mechanical enforcement, multi-session scaffolding, and convergence detection."
tags:
  - copilot
  - harness-engineering
  - agent-design
---

# GitHub Copilot: Harness Engineering

> Harness engineering is the discipline of shaping the development environment — types, tests, linters, CI gates, repo structure, and session scaffolding — so that agents self-correct by default rather than requiring manual inspection of every output.

**Environment design beats prompt tuning.** A codebase with strict types, comprehensive tests, and good linter rules makes Copilot dramatically more effective than any amount of instruction crafting in a codebase without feedback loops. The type system, test suite, linters, CI pipeline, repo structure, and session scaffolding determine whether agents can self-correct — or whether every output requires manual review.

---

## Environment Over Prompts

### The investment that compounds

Every improvement to your development environment benefits both human developers and agents simultaneously. A stricter type system catches bugs for everyone. A better test suite validates changes regardless of who wrote them. A linter with clear error messages guides anyone — human or agent — toward the right pattern.

But agents benefit disproportionately. A human developer who encounters a type error can reason about the fix from experience. An agent encountering the same error reads the error message literally and attempts the fix it suggests. The quality of that error message — its specificity, its remediation guidance — directly determines whether the agent self-corrects or spirals.

This is why harness engineering compounds: every improvement you make today applies to every agent session in the future, across every team member, on every surface.

### The three pillars

| Pillar | What it means | Example |
|--------|--------------|---------|
| **Legibility** | The repo is its own documentation. An agent can orient itself by reading the codebase structure, not by being told about it. | Clear directory naming, consistent file patterns, dependency layers that match the import graph |
| **Mechanical enforcement** | Constraints are enforced by tools, not by instructions. The agent can't make certain categories of mistake because the tooling prevents them. | Linters that block cross-layer imports, pre-commit hooks that run formatters, CI gates that require test passage |
| **Constrained solution spaces** | The architecture limits the number of valid approaches. The agent doesn't need to choose the right pattern — there's only one valid pattern. | A single ORM (no raw SQL allowed), a single test framework, a standard component template |

### What this looks like in practice

**Before harness engineering**:
```markdown
## copilot-instructions.md
- Use Drizzle ORM for all database access
- Don't use raw SQL
- Don't import from src/db/connection.ts directly
- Use repository classes in src/repositories/
- Error classes live in src/errors/ — use them
- Don't throw raw Error objects
```

The agent reads these instructions. It usually follows them. Sometimes it doesn't — especially in long sessions where attention to instructions degrades (Module C: context rot). When it doesn't, you catch it in review.

**After harness engineering**:
```
Instructions file (guidance)        → same rules as above, but shorter
ESLint rule (enforcement)           → blocks direct imports from src/db/connection.ts
ESLint rule (enforcement)           → flags `throw new Error(` with remediation: "use AppError from src/errors/"
TypeScript strict mode (types)      → no implicit any, null checks required
Integration tests (verification)    → test suite hits real DB, catches ORM misuse
Pre-commit hook (gate)              → runs linter + type check before commit
```

The instructions file still exists — it provides context and intent. But the critical rules are now mechanically enforced. The agent can't import from `src/db/connection.ts` because the linter blocks it. It can't throw raw `Error` objects because the linter flags them with a specific fix. It can't skip null checks because TypeScript strict mode requires them. And if it somehow produces code that passes all static checks but is functionally wrong, the test suite catches it.

Instructions tell the agent what to do. The harness ensures it can't do otherwise.

---

## Backpressure

### What it is

Backpressure is automated feedback that tells the agent what's wrong and how to fix it. The agent writes code, runs checks, reads error messages, fixes the issues, and repeats — without human intervention. This is the **[Ralph Wiggum Loop](../../agent-design/ralph-wiggum-loop.md)**: iterate until all checks pass.

```
Agent writes code
  → Linter flags 3 issues (with remediation messages)
  → Type checker reports 2 errors (with expected types)
  → Test suite fails 1 test (with assertion diff)
  → Agent reads all feedback
  → Agent fixes all 6 issues
  → All checks pass
  → Agent declares completion
```

### The backpressure spectrum

Not all feedback loops are equally useful. They differ in speed, precision, and the quality of guidance they provide:

| Feedback source | Speed | Precision | Remediation quality |
|----------------|-------|-----------|-------------------|
| **Type system** | Immediate (editor) | Exact location + expected type | High — the error message usually contains the fix |
| **Linter** | Immediate (editor/pre-commit) | Exact location + rule name | Variable — depends on whether the rule includes remediation guidance |
| **Unit tests** | Fast (seconds) | Assertion-level (expected vs actual) | High — the diff between expected and actual output is the diagnosis |
| **Integration tests** | Moderate (seconds–minutes) | System-level | Moderate — shows what failed, but root cause may be indirect |
| **CI pipeline** | Slow (minutes) | Build/deploy level | Low — "build failed" requires investigation to find the cause |

The agent's ability to self-correct scales directly with the precision and speed of the feedback. Type errors and linter warnings are the tightest loop — the agent sees them instantly with exact locations and specific fixes. CI failures are the loosest — the agent gets a pass/fail after minutes, with limited diagnostic information.

### Autonomy scales with backpressure quality

This is the most important insight in harness engineering:

> **Agent autonomy is determined by the codebase, not the agent.**

A codebase with strict types, 80%+ test coverage, and comprehensive linting enables Copilot to iterate autonomously through the [Ralph Wiggum Loop](../../agent-design/ralph-wiggum-loop.md). The agent writes, checks fail, the agent reads the errors, fixes them, and repeats until clean. Minimal human oversight required.

A codebase with no types, 20% test coverage, and no linting means every agent output requires manual review. The agent has no way to verify its own work. You become the feedback loop.

| Backpressure quality | Agent autonomy | Human review burden |
|---------------------|---------------|-------------------|
| Strict types + high test coverage + comprehensive linting | High — agent self-corrects most issues | Low — review focuses on design and completeness |
| Moderate types + moderate coverage + basic linting | Moderate — agent catches some issues, misses others | Moderate — review catches mechanical issues the tooling missed |
| No types + low coverage + no linting | Minimal — agent operates blind | High — every output requires full manual inspection |

### Practical investment priorities

If you're starting from a weak backpressure position, invest in this order:

1. **TypeScript strict mode** (or equivalent typed language configuration) — highest-leverage single change. Catches null errors, type mismatches, and missing properties at write time.
2. **Linter rules with remediation messages** — ESLint rules that don't just flag violations but tell the agent how to fix them. "Use `AppError` from `src/errors/` instead of raw `Error`" is actionable; "Unexpected error throw" is not.
3. **Test coverage for critical paths** — focus on the paths agents are most likely to touch: handlers, services, data access. Integration tests over unit tests — they catch more real-world failures.
4. **Pre-commit hooks** — gate commits on linter + type check. The agent can't commit broken code.
5. **CI pipeline with clear output** — the final safety net. Structure CI output so failures are diagnosable from the log.

---

## Repo Legibility

### The repo as its own documentation

An agent that can orient itself by reading the codebase — without being told where things are — starts every session faster and makes fewer wrong-directory mistakes. Legibility is about making the codebase self-describing.

### Directory structure as architecture

```
src/
  types/          ← shared type definitions (no imports from other src/ dirs)
  config/         ← environment configuration (imports only types/)
  repositories/   ← database access (imports types/, config/)
  services/       ← business logic (imports types/, config/, repositories/)
  routes/         ← HTTP handlers (imports services/, types/)
  middleware/     ← request pipeline (imports types/, config/)
  errors/         ← error classes (imports types/)
  test/           ← test utilities and helpers
```

When directories map to architectural layers and the import graph matches the directory hierarchy, the agent can infer architectural rules from the structure alone. It doesn't need to be told "don't import from `src/db/connection.ts`" — the import structure makes the allowed dependencies visible.

### Naming conventions that communicate intent

| Pattern | What it tells the agent |
|---------|----------------------|
| `*.repository.ts` | Database access layer — uses ORM, returns domain types |
| `*.service.ts` | Business logic — orchestrates repositories, no direct DB access |
| `*.handler.ts` or `*.route.ts` | HTTP layer — validates input, calls services, returns responses |
| `*.test.ts` / `*.spec.ts` | Test file — mirrors the source file structure |
| `*.dto.ts` | Data transfer object — used at API boundaries |

Consistent naming eliminates an entire class of agent decisions. When every repository file ends in `.repository.ts`, the agent doesn't have to decide where to put database access code — the pattern is self-evident.

### The instructions file as an architectural map

Module B covered `.github/copilot-instructions.md` as a customization primitive. From a harness engineering perspective, the instructions file's highest-value role is as a compressed architectural map — not a rule book.

**Good architectural map** (helps the agent orient):
```markdown
## Architecture
- src/routes/ → src/services/ → src/repositories/ → Postgres via Drizzle
- Each layer has a single responsibility. Routes validate + respond. Services orchestrate. Repositories query.
- Error classes in src/errors/ — throw these, never raw Error objects.

## Build & Test
- `npm test` — Vitest, hits real test DB on port 5432
- `npm run lint` — ESLint + custom rules for import boundaries
```

**Bad rule book** (dilutes attention, duplicates what tooling enforces):
```markdown
- Always use async/await, never callbacks
- Use const instead of let where possible
- Prefer arrow functions for callbacks
- Use template literals instead of string concatenation
- Always handle promise rejections
- ...50 more rules that ESLint already enforces
```

If ESLint already enforces a rule, don't repeat it in the instructions file. The agent will encounter the linter error if it violates the rule — that's the backpressure working. Reserve the instructions file for context that tooling can't provide: architectural intent, layer responsibilities, and conventions that require understanding rather than enforcement.

### Linter messages as just-in-time context

Custom linter rules with remediation guidance are the most targeted form of agent context — they appear exactly when the agent needs them, at the exact location of the violation, with a specific fix.

```javascript
// eslint custom rule: no-direct-db-import
module.exports = {
  create(context) {
    return {
      ImportDeclaration(node) {
        if (node.source.value.includes('src/db/connection')) {
          context.report({
            node,
            message:
              'Direct database imports are not allowed. ' +
              'Use repository classes from src/repositories/ instead. ' +
              'See src/repositories/user.repository.ts for an example.',
          });
        }
      },
    };
  },
};
```

When Copilot encounters this error, it gets:

1. **What's wrong**: "Direct database imports are not allowed"
2. **What to do instead**: "Use repository classes from `src/repositories/`"
3. **Where to look**: "See `src/repositories/user.repository.ts` for an example"

This is more effective than any instruction file entry because it appears at the moment of violation, not preloaded into context 50,000 tokens earlier. It's just-in-time context injection via the backpressure system.

---

## Mechanical Enforcement

### Hooks as the enforcement layer

Module B introduced hooks as a customization primitive. From a harness engineering perspective, hooks are the final enforcement layer — they run outside the agent's context and cannot be overridden.

The enforcement stack, from softest to hardest:

```
Instructions         → guidance (agent interprets, may ignore)
Linter rules         → flags violations (agent reads errors, self-corrects)
Type system          → blocks invalid types (agent must satisfy the compiler)
Pre-commit hooks     → gates commits (code must pass checks to be committed)
Copilot hooks        → gates tool calls (hook can block file writes, command execution)
CI pipeline          → gates merge (PR must pass all checks)
Branch protection    → gates deployment (requires approvals, signed commits)
```

Each layer catches what the layer above missed. Instructions catch intent violations the linter can't express. Linters catch pattern violations types can't express. Types catch structural violations tests can't express. And so on.

### Which enforcement mechanism for which rule

| Rule type | Best enforcement | Why |
|-----------|-----------------|-----|
| "Use Vitest, not Jest" | Linter rule (flag `jest` imports) | Deterministic, exact location, auto-fixable |
| "Don't write to `/migrations/`" | Copilot hook (`preToolUse`) | Must block the action before it happens |
| "All API responses must include `requestId`" | Integration test | Validates behaviour, not just syntax |
| "Functions must not exceed 50 lines" | Linter rule | Measurable, enforceable at write time |
| "Use the repository pattern for data access" | Linter rule (block direct DB imports) + instructions (explain the pattern) | Enforcement + context |
| "PRs require at least one approval" | Branch protection | Platform-level enforcement |

### Pre-commit hooks for agent workflows

Pre-commit hooks are the tightest gate before code leaves the agent's local environment. They run synchronously on every commit — if the hook fails, the commit is rejected.

A minimal pre-commit configuration for agent-friendly codebases:

```yaml
# .pre-commit-config.yaml (or equivalent)
hooks:
  - lint          # ESLint / language linter
  - type-check    # tsc --noEmit / mypy / equivalent
  - format        # Prettier / Black / equivalent
```

The agent commits → the hook runs linting, type checking, and formatting → if any fail, the commit is rejected with error output → the agent reads the errors and fixes them → the agent commits again.

This is the [Ralph Wiggum Loop](../../agent-design/ralph-wiggum-loop.md) at the commit boundary. The agent cannot commit code that violates your lint rules or type constraints. It's not a suggestion — it's a gate.

---

## Multi-Session Work

### The problem with long sessions

Module C covered context rot — output quality degrading as sessions run long. The harness engineering response is to design for sessions that are **short, focused, and leave clean handoff artifacts**.

### Progress files

For work that spans multiple sessions (multi-day features, large refactors), maintain a progress file that the agent reads at the start of every session:

```markdown
<!-- .progress/feature-rate-limiting.md -->
# Rate Limiting Feature

## Completed
- [x] RateLimiter class in src/middleware/rate-limiter.ts (commit abc123)
- [x] Unit tests for RateLimiter (commit abc124)
- [x] Integration with Redis for distributed rate limiting (commit def456)

## In Progress
- [ ] Apply rate limiting to /api/upload endpoint

## Not Started
- [ ] Apply rate limiting to /api/export endpoint
- [ ] Add rate limit headers to all responses
- [ ] Dashboard metrics for rate limit hits

## Notes
- Rate limiter uses sliding window algorithm, not fixed window
- Redis key format: `ratelimit:{userId}:{endpoint}`
- Tests require Redis on port 6379 (docker-compose up redis)
```

At the start of each session, the agent reads the progress file and git log to establish what's done and what's next. This replaces accumulated conversation context (which degrades) with a persistent, editable artifact (which stays accurate).

### Structured commits as handoff notes

When the agent completes a task, the commit message should serve as a handoff note for the next session:

```
feat(rate-limit): add RateLimiter middleware with sliding window

Implemented:
- RateLimiter class with configurable window and max requests
- Redis-backed distributed counting via MULTI/EXEC
- Per-user and per-endpoint scoping

Tests passing:
- 12 unit tests for RateLimiter (window boundary, reset, overflow)
- 2 integration tests (Redis connection, distributed counting)

Next task:
- Apply RateLimiter to /api/upload endpoint (see rate-limiter.md)
```

This isn't just good commit hygiene — it's a structured handoff artifact that the next agent session (or a human) can read to resume work without re-investigating what was done.

### One feature per session

Long sessions accumulate context and degrade quality. Short sessions start fresh. The optimal unit of work for a single agent session:

- **One feature or one fix** — not "implement rate limiting across the whole API"
- **Verifiable outcome** — the session ends when a specific test passes or a specific file is correct
- **Clean exit** — commit, update progress file, stop

If the feature is too large for one session, decompose it (Module C: task decomposition) and track each chunk in the progress file.

### Checkpoints

For VS Code Agent mode and the CLI, create manual checkpoints before risky operations:

```
Before: git stash or git commit -m "checkpoint: before rate limiter refactor"
Agent works...
If wrong: git stash pop or git revert
If right: continue
```

The coding agent creates checkpoints automatically — it works on a `copilot/*` branch and opens a draft PR. The branch is the checkpoint. If the work is wrong, close the PR and delete the branch. Instant rollback.

---

## Safe Operations

### Rollback-first design

Before deciding how an agent will perform an action, decide how you will undo it. If undoing the action costs more than one command, reconsider the approach.

| Operation | Reversible primitive | Undo cost |
|-----------|---------------------|-----------|
| Code changes | Git branch | `git branch -D` — instant |
| PR submission | Draft PR | Close without merging — instant |
| File creation | Git tracked | `git checkout -- file` — instant |
| Status update | Labels (not field edits) | Remove label — instant |
| Discussion | Comment (not body edit) | Delete comment — instant |
| Deployment | Feature flag | Toggle off — instant |
| Email / webhook / notification | **Not reversible** | ∞ — gate with human approval |

**Rule**: External side effects that leave the repository boundary — emails, Slack messages, webhook calls, payment API calls — cannot be reversed. Always gate these with human approval, never automate them in agent workflows.

### Idempotent operations

Design agent operations so running the same task twice produces the same end state — not duplicate artifacts.

**Check before create**:
```bash
# Bad: always creates a new branch (fails or duplicates on retry)
git checkout -b feature/issue-123

# Good: creates or switches to existing branch (safe to retry)
git checkout feature/issue-123 2>/dev/null || git checkout -b feature/issue-123
```

**Upsert over insert**:
```bash
# Bad: always posts a new comment (duplicates on retry)
gh pr comment 42 --body "Analysis complete"

# Good: updates existing comment or creates new one
gh pr comment 42 --body "Analysis complete" --edit-last 2>/dev/null || \
gh pr comment 42 --body "Analysis complete"
```

**Use natural keys**: Issue numbers, commit SHAs, and task IDs are natural idempotency keys. Use them in branch names (`feature/issue-123`), commit messages (`fix #123`), and comment markers so the agent can detect prior work on retry.

---

## Convergence Detection

### Knowing when to stop

Agents iterate. The [Ralph Wiggum Loop](../../agent-design/ralph-wiggum-loop.md) runs until checks pass. But some tasks — documentation, architecture specs, code refactors — don't have a binary pass/fail. How do you know when to stop?

### Three signals

| Signal | What to measure | Convergence indicator |
|--------|----------------|----------------------|
| **Change velocity** | Lines changed per iteration | Changes slow to near-zero |
| **Output size** | Total output length | Stabilises or shrinks |
| **Content similarity** | Diff between consecutive iterations | Diff approaches zero |

When all three signals indicate convergence, further iteration produces diminishing returns. Stop.

### The [five-pass blunder hunt](../../verification/five-pass-blunder-hunt.md)

For prose, specifications, and design documents, apply this mechanical convergence test:

1. Run the same critique prompt against the output five times in succession
2. Observe the critique quality and volume across passes
3. When passes 4 and 5 produce nearly identical critiques to pass 3, the output has converged

```
Pass 1: "Missing error handling for null input, unclear naming in section 3"
Pass 2: "Section 3 naming improved. Consider adding a diagram for the flow."
Pass 3: "Minor: 'data' is vague in line 12. Otherwise solid."
Pass 4: "Minor: 'data' is vague in line 12. Otherwise solid."
Pass 5: "No significant issues found."
→ Converged at pass 3. Stop.
```

### Failure patterns

Not all iteration converges. Watch for these failure patterns:

| Pattern | Symptom | Cause | Response |
|---------|---------|-------|----------|
| **Oscillation** | Agent alternates between two states (adds a feature, removes it, adds it back) | Unresolvable trade-off in the constraints | Stop the agent. Resolve the trade-off yourself, then restart with clearer constraints. |
| **Expansion** | Output grows each iteration without improving | Scope drift — the agent keeps adding tangentially related content | Stop and constrain scope explicitly. |
| **Low-quality plateau** | Output stabilises but at an unsatisfactory quality level | The approach is wrong, not the execution | Restart with a different approach, not more iterations of the same one. |

### Hard limits as safety nets

Always pair convergence detection with a hard iteration limit:

- **Code tasks**: Max 3 fix-and-retry cycles after initial implementation. If 3 cycles of the [Ralph Wiggum Loop](../../agent-design/ralph-wiggum-loop.md) haven't fixed the issue, the problem likely requires a different approach, not more iteration.
- **Prose/spec tasks**: Max 5 critique-and-refine passes. Diminishing returns after pass 3 in most cases.
- **Refactoring tasks**: Max 2 rounds of self-review. If the second round finds significant issues, the refactoring scope was too large for one session.

---

## Putting It Together: The Agent-Ready Codebase Checklist

### Backpressure

- [ ] TypeScript strict mode (or equivalent) enabled
- [ ] Linter configured with project-specific rules
- [ ] Custom linter rules include remediation messages (not just violation flags)
- [ ] Test coverage on critical paths (handlers, services, data access)
- [ ] Pre-commit hooks run linting + type checking

### Legibility

- [ ] Directory structure maps to architectural layers
- [ ] Consistent file naming conventions (`.service.ts`, `.repository.ts`, `.handler.ts`)
- [ ] `.github/copilot-instructions.md` is an architectural map, not a rule book (≤100 lines)
- [ ] Path-specific `.instructions.md` files for areas with distinct conventions

### Enforcement

- [ ] Import boundary rules enforced by linter (not just instructions)
- [ ] Copilot hooks for hard constraints (path restrictions, security checks)
- [ ] CI pipeline gates merge on lint + type check + test passage
- [ ] Branch protection requires PR review

### Session scaffolding

- [ ] Progress files for multi-session work
- [ ] Commit message convention includes "what's done" and "what's next"
- [ ] One feature per agent session discipline

### Safe operations

- [ ] All agent work on branches (never direct to main)
- [ ] Draft PRs for agent-authored changes
- [ ] External side effects gated by human approval
- [ ] Idempotent operation patterns for retryable tasks

---

## Key Takeaways

- **Environment design beats prompt tuning.** Investing in types, tests, and linters improves agent output quality more — and more durably — than tweaking instruction files. Every harness improvement compounds across all future sessions.
- **Agent autonomy scales with backpressure quality**, not with model capability. A codebase with strict types and comprehensive tests enables autonomous agent iteration. A codebase without them requires manual review of every output.
- **Linter messages are the best form of agent context** — they appear at the exact moment and location of a violation, with a specific remediation. Write custom linter rules with actionable error messages.
- **Instructions provide context; the harness provides enforcement.** Use both, but don't rely on instructions for rules that must be followed mechanically. If the consequence of violation is real — security, data integrity, compliance — enforce it with tooling, not text.
- **Design for short, focused sessions** with clean handoff artifacts. Progress files, structured commits, and one-feature-per-session discipline prevent context rot and make multi-session work reliable.
- **Make operations reversible by default.** Branches, draft PRs, and feature flags make agent work cheap to undo. Gate irreversible external side effects with human approval.
- **Know when to stop iterating.** Convergence detection (change velocity, output similarity, the [five-pass blunder hunt](../../verification/five-pass-blunder-hunt.md)) prevents wasted cycles. Hard iteration limits prevent runaway agent sessions.

## Related

**Training**

- [GitHub Copilot: Platform Surface Map](surface-map.md) — all surfaces and when to use each
- [GitHub Copilot: Customization Primitives](customization-primitives.md) — configuring instructions, agents, skills, hooks, MCP, Spaces, memory
- [GitHub Copilot: Context Engineering & Agent Workflows](context-and-workflows.md) — context engineering, [progressive disclosure](../../agent-design/progressive-disclosure-agents.md), delegation, steering

**Harness Engineering**

- [Harness Engineering](../../agent-design/harness-engineering.md) — the discipline of designing agent environments for success by default
- [Agent Harness](../../agent-design/agent-harness.md) — initialiser + coding agent pattern for long-running work
- [Agent Backpressure](../../agent-design/agent-backpressure.md) — automated feedback loops and the autonomy spectrum
- [Agent Loop Middleware](../../agent-design/agent-loop-middleware.md) — post-loop safety nets and pre-call message injection
- [Rollback-First Design](../../agent-design/rollback-first-design.md) — making agent operations reversible by default
- [Idempotent Agent Operations](../../agent-design/idempotent-agent-operations.md) — designing operations safe to retry
- [Convergence Detection](../../agent-design/convergence-detection.md) — knowing when to stop iterating

**Enforcement & Verification**

- [Hook Catalog](../../tool-engineering/hook-catalog.md) — practical reference for guardrail hooks
- [Skill-Tool Runtime Enforcement](../../tool-engineering/skill-tool-runtime-enforcement.md) — runtime enforcement patterns
- [LLM Context Test Harness](../../verification/llm-context-test-harness.md) — designing test output as an LLM-first interface

**Context Management**

- [Context Window Dumb Zone](../../context-engineering/context-window-dumb-zone.md) — why context rot degrades output quality and how to size budgets by task type
