---
title: "L2 → L3: Building Mechanical Enforcement for Agents"
description: "Transform an Agent-Assisted codebase (L2) into an Agent-Operable one (L3) by adding mechanical enforcement: PreToolUse hooks, structured task definitions, and session scaffolding."
tags:
  - training
  - agent-design
  - workflows
  - tool-agnostic
---

# L2 → L3: Building Mechanical Enforcement

> An L2 repo has feedback loops that let agents self-correct after the fact. An L3 repo prevents certain errors from happening in the first place — enforcement before the agent acts, not after.

---

## What L2 Looks Like

At L2, the agent iterates through a feedback loop: write code, fail lint/tests, read errors, fix, repeat. This works well for mechanical errors — type mismatches, wrong imports, failing tests. But it does not prevent:

- File writes to restricted paths (e.g., directly editing migration files)
- Commands that have irreversible side effects (e.g., deleting data)
- Sessions that accumulate context rot and produce lower-quality output as they run long
- Architecture violations that pass lint and tests but violate documented constraints

L2 relies on the agent finding and fixing errors. L3 prevents categories of error before they occur.

## What L3 Looks Like

At L3, the agent operates within a constrained solution space:

- Hard constraints enforced by hooks prevent certain actions entirely
- Structured task definitions give the agent clear, replayable workflow contracts
- Session scaffolding maintains quality across multi-session work
- The agent completes well-specified tasks without per-action supervision

**Exit criterion**: The agent can execute a scoped, well-defined task end-to-end — writing code, running verification, committing — without requiring human review or intervention for tasks within its defined scope.

---

## The L2 → L3 Transformation

### Step 1: Add PreToolUse Hooks for Hard Constraints

[Hooks](../../tool-engineering/hook-catalog.md) run outside the agent's context and cannot be overridden by instructions. They enforce constraints that must hold regardless of what the agent is told to do.

The enforcement stack, from advisory to mandatory:

```
Instructions         → guidance (agent interprets, may ignore)
Linter rules         → flags violations (agent reads, self-corrects)
Type system          → blocks invalid types (agent must satisfy the compiler)
Pre-commit hooks     → gates commits (code must pass checks)
PreToolUse hooks     → gates tool calls (can block writes, commands)
CI pipeline          → gates merge (PR must pass all checks)
```

PreToolUse hooks are the tightest gate — they fire before the tool executes. Hooks receive JSON context on stdin; use `jq` to extract fields. Configure them in `.claude/settings.json` ([Claude Code hooks](https://code.claude.com/docs/en/hooks)):

```json
{
  "hooks": {
    "PreToolUse": [
      {"matcher": "Write", "hooks": [{"type": "command", "command": ".claude/hooks/block-migrations-write.sh"}]},
      {"matcher": "Bash", "hooks": [{"type": "command", "command": ".claude/hooks/block-db-reset.sh"}]}
    ]
  }
}
```

```bash
#!/bin/bash
# .claude/hooks/block-migrations-write.sh
# JSON context is passed on stdin; use jq to extract fields
FILE_PATH=$(jq -r '.tool_input.file_path')
if [[ "$FILE_PATH" =~ migrations/ ]]; then
  jq -n '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny",
    permissionDecisionReason: "Direct migration edits are blocked. Use the migration generator: npm run db:generate"}}'
fi
```

```bash
#!/bin/bash
# .claude/hooks/block-db-reset.sh
COMMAND=$(jq -r '.tool_input.command')
if echo "$COMMAND" | grep -q 'db:reset'; then
  jq -n '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny",
    permissionDecisionReason: "Database reset is blocked in agent sessions. Run manually if required."}}'
fi
```

**High-value hook targets:**

| Constraint | Hook type | Why not just an instruction |
|-----------|-----------|---------------------------|
| Block writes to `/migrations/` | `PreToolUse: Write` | Migrations need reviewed generation, not direct edits |
| Block destructive DB commands | `PreToolUse: Bash` | Irreversible; cannot be undone by `git revert` |
| Block writes to production config | `PreToolUse: Write` | Security boundary |
| Require branch name pattern | `PreToolUse: Bash` (git commit) | Governance; enforced uniformly |

**The rule for choosing between hook and instruction**: If the consequence of violation is irreversible or security-critical, use a hook. If the consequence is correctible (wrong import, wrong pattern), use a linter rule with remediation. Instructions are for context and intent, not enforcement.

### Step 2: Define Structured Task Definitions

At L2, the agent receives tasks in natural language. Structured task definitions make workflows replayable, auditable, and executable by any agent session without re-explaining the context.

Anthropic's harness engineering research demonstrates that structured task artifacts significantly improve multi-session agent reliability — the initializer/coding-agent architecture uses JSON feature lists rather than markdown so the agent cannot inadvertently delete or reinterpret requirements ([Anthropic Engineering](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)).

A practical task definition in a skill file (`.claude/skills/add-endpoint/`):

```markdown
---
name: add-endpoint
description: Add a new REST API endpoint following project conventions
---
## Inputs
- `route`: URL path (e.g., `/users/:id/preferences`)
- `method`: HTTP method
- `description`: What the endpoint does

## Steps
1. Define the request/response types in `src/types/api.ts`
2. Add the route handler in `src/routes/` — validate input, call service, return response
3. Add the service method in `src/services/` — business logic only, no direct DB access
4. Add the repository method in `src/repositories/` if new DB access is needed
5. Write integration tests covering the happy path and the most common error case
6. Run `npm run lint && npm run type-check && npm test -- --run`
7. Commit with message: `feat(<route>): add <method> endpoint`

## Success Criteria
- All lint, type, and test checks pass
- No direct DB imports in the route or service layers
- New types are defined in `src/types/api.ts`
```

The agent invokes this with `/add-endpoint route=/users/:id/preferences method=GET description="Get user preferences"`. The structured format eliminates the ambiguity of natural language task requests and encodes your architectural rules directly into the workflow.

### Step 3: Add Session Scaffolding

Long agent sessions accumulate context and degrade quality ([Anthropic: Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)). L3 repos design for short, focused sessions with clean handoff artifacts.

**Progress files for multi-session work:**

For work spanning multiple sessions (large features, extended refactors), maintain a progress file the agent reads at the start of each session:

```markdown
<!-- .progress/feature-rate-limiting.md -->
# Rate Limiting Feature

## Completed
- [x] RateLimiter class in src/middleware/rate-limiter.ts (commit abc123)
- [x] Unit tests for RateLimiter (commit abc124)

## In Progress
- [ ] Apply rate limiting to /api/upload endpoint

## Not Started
- [ ] Apply rate limiting to /api/export endpoint
- [ ] Add rate limit headers to all responses

## Notes
- Uses sliding window algorithm, not fixed window
- Redis key format: `ratelimit:{userId}:{endpoint}`
```

At session start: "Read `.progress/feature-rate-limiting.md` and the git log for the last 5 commits, then resume the in-progress item."

This replaces accumulated conversation context (which degrades) with a persistent, editable artifact (which stays accurate). Anthropic's multi-session harness architecture uses this pattern — `claude-progress.txt` bridges context between sessions ([Anthropic Engineering](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)).

**Structured commit messages as handoff notes:**

When the agent completes a task, the commit message should serve as a handoff artifact:

```
feat(rate-limit): add RateLimiter middleware with sliding window

Implemented:
- RateLimiter class with configurable window and max requests
- Redis-backed distributed counting via MULTI/EXEC

Tests passing: 12 unit (window boundary, reset, overflow)

Next: Apply RateLimiter to /api/upload endpoint (see .progress/rate-limiting.md)
```

**One task per session:**

Decompose large features into single-session units with verifiable outcomes. A session should end when a specific test passes or a specific file is in a correct state — not "I finished as much as I could." Clean sessions prevent context rot from compounding across a long task.

### Step 4: Verify the Transition

Run this exit check:

1. Ask the agent to write to a restricted path (e.g., directly edit a migration file). The hook should block it with a clear message.
2. Ask the agent to execute a standard task using a skill definition. It should follow the steps without requiring clarification about conventions.
3. Pause a multi-session task mid-way. Start a new session, point it to the progress file, and verify it resumes correctly without losing context.

---

## Key Takeaways

- **Instructions provide context; hooks provide enforcement.** Use instructions for things the agent should understand; use hooks for things the agent must not do regardless of instruction.
- **Structured task definitions eliminate ambiguity** and encode architectural rules into replayable workflows. They are the difference between "the agent knows the pattern" and "the agent always follows the pattern."
- **Session scaffolding preserves quality across multi-session work.** Progress files and structured commit messages replace degrading conversation history with durable, editable artifacts.
- **One task per session** with a verifiable exit condition. Decompose large features before giving them to an agent.

## Related

- [Hook Catalog](../../tool-engineering/hook-catalog.md) — practical reference for PreToolUse and PostToolUse hooks
- [Skill-Tool Runtime Enforcement](../../tool-engineering/skill-tool-runtime-enforcement.md) — combining hooks with skills for layered enforcement
- [Agent Harness](../../agent-design/agent-harness.md) — initializer + coding agent pattern for long-running work
- [Rollback-First Design](../../agent-design/rollback-first-design.md) — making agent operations reversible by default
- [L1 → L2: Adding Feedback Loops](level-1-to-2.md) — previous module
- [L3 → L5: Reaching Agent-First](level-3-to-5.md) — next module
