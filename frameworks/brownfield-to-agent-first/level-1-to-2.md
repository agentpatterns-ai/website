---
title: "L1 → L2: Adding Feedback Loops to a Brownfield Repo"
description: "Transform an Agent-Readable codebase (L1) into an Agent-Assisted one (L2) by adding automated feedback loops: strong types, comprehensive tests, and linter rules with remediation messages."
tags:
  - training
  - agent-design
  - workflows
  - tool-agnostic
---

# L1 → L2: Adding Feedback Loops

> An L1 repo gives agents context. An L2 repo gives agents a way to verify their own work. The L1→L2 transition adds automated feedback loops so agents can self-correct without human review on every output.

---

## What L1 Looks Like

At L1, the agent can orient itself — it understands the architecture and knows where things go. But after it writes code, it has limited ways to know if that code is correct:

- No type system or a weak one (`any` everywhere)
- Low or no test coverage
- Linter rules that flag violations without explaining how to fix them
- Every agent output requires manual review to catch errors

The agent produces output; you review it; you tell it what's wrong; it tries again. You are the feedback loop.

## What L2 Looks Like

At L2, the agent can validate most of its own work:

- Strong types catch structural errors at write time
- A test suite provides a binary "did I break anything?" signal
- Linter rules include remediation messages the agent can act on directly
- The agent iterates through the [Ralph Wiggum Loop](../../agent-design/ralph-wiggum-loop.md): write → lint fails → read error → fix → lint passes → tests fail → read failure → fix → tests pass

**Exit criterion**: The agent can complete a scoped, well-specified task (add a function with tests) and verify its own output through the feedback loops, without requiring human review to catch mechanical errors.

---

## The L1 → L2 Transformation

### Step 1: Enable a Strong Type System

Type errors are the tightest feedback loop in software development. They fire at write time, at the exact location of the violation, with a specific message about what the type should be. For agents, this is the most actionable form of backpressure.

**TypeScript strict mode** — if your repo uses TypeScript:

```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,           // enables all strict checks
    "noImplicitAny": true,    // flags missing type annotations
    "strictNullChecks": true, // prevents null/undefined errors
    "noUncheckedIndexedAccess": true  // flags array access without null checks
  }
}
```

Enabling strict mode on an existing repo will produce type errors. This is expected. Fix them incrementally — the errors represent real bugs or assumptions that agents would otherwise replicate. Each fixed error makes the type surface more accurate.

**Python** — if your repo uses Python:

```bash
# Add mypy to your dev dependencies
pip install mypy

# mypy.ini or pyproject.toml
[mypy]
strict = true
disallow_untyped_defs = true
```

**Why the agent benefits disproportionately**: A human developer encountering a type error reasons from experience. An agent reads the error message literally. The quality of the error message — its specificity, its location — directly determines whether the agent self-corrects ([Anthropic: Claude Code Best Practices](https://code.claude.com/docs/en/best-practices)).

### Step 2: Build Test Coverage on Critical Paths

A test suite gives the agent a binary answer to "did I break anything?" Agents can run tests, read the failure output, diagnose the issue, and fix it without human intervention — but only if the test suite exists.

**Prioritize by agent risk, not business risk:**

| Path | Why these paths matter | Investment priority |
|------|------------------------|---------------------|
| Route handlers | Most new features add or modify routes | High |
| Service layer | Layer boundary violations concentrate here | High |
| Data access / repositories | ORM and schema errors caught by integration tests, not static analysis | High |
| Utilities and helpers | [Pattern replication](../../anti-patterns/pattern-replication-risk.md) amplifies here — agents copy existing utilities ([GitClear, 2025](https://www.gitclear.com/ai_assistant_code_quality_2025_research)) | Medium |
| Configuration loading | Subtle misuse difficult to catch without test assertions | Medium |

You do not need 100% coverage to move to L2. You need coverage on the paths agents are most likely to modify — a test suite that provides meaningful signal when an agent makes a common error. Aim for the critical paths above before worrying about edge cases.

**Test design for agent feedback**: Write assertions that produce informative failure messages.

```typescript
// Less useful for agent feedback
expect(result).toBeTruthy();

// More useful — agent reads the diff and knows exactly what changed
expect(result).toEqual({
  userId: '123',
  status: 'active',
  createdAt: expect.any(Date),
});
```

When a test fails, the agent reads the expected vs actual diff. The more structured the assertion, the more specific the fix the agent produces.

**Integration tests over unit tests** for agent-critical paths: integration tests catch ORM misuse, transaction handling errors, and layer violations that unit tests with mocks miss. LangChain's Terminal Bench improvements came from structural verification, not mock-based unit tests ([LangChain](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)).

### Step 3: Write Linter Rules with Remediation Messages

Standard linter rules flag violations. Agent-useful linter rules explain what to do instead. The error message enters the agent's context at the exact moment it makes the wrong decision — this is just-in-time context delivery.

**Good remediation message:**
```
ERROR: Direct database imports are not allowed.
  Use repository classes from src/repositories/ instead.
  See src/repositories/user.repository.ts for an example.
```

**Poor (agent must infer the fix):**
```
ERROR: Forbidden import from 'src/db/connection'.
```

**Custom ESLint rule example** — enforcing the repository pattern:

```javascript
// eslint-rules/no-direct-db-import.js
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
              'Example: import { UserRepository } from "../repositories/user.repository"',
          });
        }
      },
    };
  },
};
```

**High-value rule targets for agent-assisted codebases:**

| Rule | What it prevents | Remediation message should say |
|------|-----------------|-------------------------------|
| No direct DB imports | Layer violations | "Use repository in src/repositories/" |
| No raw `Error` throw | Inconsistent error handling | "Use AppError subclasses from src/errors/" |
| No implicit `any` in new files | Type coverage erosion | "Annotate the parameter type explicitly" |
| No console.log in src/ | Debug output in production | "Use the logger from src/utils/logger.ts" |
| Import boundaries by directory | Architecture violations | "This layer cannot import from X; put shared code in Y" |

### Step 4: Add a Pre-Commit Hook

A pre-commit hook ensures that the agent cannot commit code that fails lint or type checks. This gates the output before it enters version history.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: lint
        name: ESLint
        entry: npm run lint
        language: system
        types: [javascript, typescript]
      - id: type-check
        name: TypeScript
        entry: npm run type-check
        language: system
        pass_filenames: false
```

Or with Node tooling directly:

```json
// package.json
{
  "scripts": {
    "lint": "eslint src/ --max-warnings 0",
    "type-check": "tsc --noEmit"
  }
}
```

```bash
# .husky/pre-commit (if using Husky)
npm run lint && npm run type-check
```

The agent commits code → the hook runs → if either fails, the commit is rejected with the error output → the agent reads the errors and fixes them → the agent commits again. This is the [Ralph Wiggum Loop](../../agent-design/ralph-wiggum-loop.md) at the commit boundary.

### Step 5: Verify the Transition

Run this exit check:

1. Ask the agent to add a new function to an existing service — something that involves calling a repository
2. Watch the agent iterate: does it write code, run lint, read the error, and self-correct without your intervention?
3. Ask the agent to introduce a deliberate type error — does the type checker catch it and does the agent fix it?

If the agent consistently requires your intervention to correct mechanical errors (wrong imports, wrong types, wrong error class), the feedback loops are not tight enough yet. Typical causes:
- Linter rules that flag violations without remediation messages
- Type system enabled but too many `any` types remaining
- Tests exist but don't cover the paths the agent modifies

## When This Backfires

The L1→L2 transition is high-leverage but not free. Three conditions make it a poor investment:

- **Large existing `any` surface**: Enabling TypeScript strict mode on a codebase with hundreds of implicit `any` types produces a flood of errors across unrelated files. The cost to fix them dwarfs the agent benefit until the bulk of the `any` types are already annotated. Start with `noImplicitAny` scoped to new files only; expand incrementally.
- **High-churn paths with low test stability**: If the integration tests covering agent-critical paths break frequently due to schema changes or environment drift, agents learn to ignore failing tests rather than treat them as signal. Test maintenance cost exceeds test signal value. Stabilize the test environment before relying on it as a feedback source.
- **Monorepos with shared strict mode config**: Enabling strict mode on one package in a monorepo often cascades type errors into shared libraries consumed by other packages. The migration cannot be isolated to the package the agent works in. Coordinate across package owners before enabling — or use path-scoped tsconfig overrides to contain the blast radius.

---

## Key Takeaways

- **Agent autonomy scales with backpressure quality**, not with model capability ([Anthropic](https://code.claude.com/docs/en/best-practices)). A codebase with strict types and 80%+ test coverage on critical paths enables autonomous agent iteration. A codebase without them requires manual review of every output.
- **Linter messages are the best form of agent context**: they fire at the exact moment and location of a violation. Write custom rules with actionable remediation messages.
- **Prioritize integration tests** over mocked unit tests for agent-critical paths. They catch the errors agents actually make: ORM misuse, layer violations, transaction handling.
- **Pre-commit hooks are not optional**. They are the gate that prevents the feedback loop from being bypassed. Without them, agents can commit and push non-compliant code.
- **Fix type errors incrementally**. Enabling strict mode produces errors — this is expected. Each error fixed is a potential agent mistake prevented.

## Related

- [Agent Backpressure](../../agent-design/agent-backpressure.md) — the automated feedback loop pattern and the autonomy spectrum
- [Codebase Readiness for Agents](../../workflows/codebase-readiness.md) — the agent-hostile vs agent-friendly signal table
- [Harness Engineering](../../agent-design/harness-engineering.md) — the full discipline these steps build toward
- [L0 → L1: Making the Repo Readable](level-0-to-1.md) — previous module
- [L2 → L3: Building Mechanical Enforcement](level-2-to-3.md) — next module
