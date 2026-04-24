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

The agent orients itself but cannot verify its output:

- Weak or no type system (`any` everywhere)
- Low or no test coverage
- Linter rules that flag violations without remediation
- Every output requires manual review

You are the feedback loop.

## What L2 Looks Like

The agent validates most of its own work:

- Strong types catch structural errors at write time
- A test suite gives a binary "did I break anything?" signal
- Linter rules carry remediation messages the agent can act on
- Iteration runs through the [Ralph Wiggum Loop](../../agent-design/ralph-wiggum-loop.md): write → lint fails → fix → lint passes → tests fail → fix → tests pass

**Exit criterion**: the agent completes a scoped task (add a function with tests) and verifies its output without human review of mechanical errors.

---

## The L1 → L2 Transformation

### Step 1: Enable a Strong Type System

Type errors fire at write time, at the exact location of the violation, with a specific message about what the type should be — the most actionable form of backpressure.

**TypeScript strict mode**:

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

Enabling strict mode on an existing repo produces type errors. Fix them incrementally — they represent real bugs or assumptions agents would otherwise replicate.

**Python**:

```bash
# Add mypy to your dev dependencies
pip install mypy

# mypy.ini or pyproject.toml
[mypy]
strict = true
disallow_untyped_defs = true
```

**Why agents benefit disproportionately**: a human reasons from experience; an agent reads the message literally. Error specificity and location determine whether the agent self-corrects ([Anthropic](https://code.claude.com/docs/en/best-practices)).

### Step 2: Build Test Coverage on Critical Paths

A test suite gives a binary answer to "did I break anything?" Agents run tests, read failures, and fix — only if the suite exists.

**Prioritize by agent risk, not business risk:**

| Path | Why it matters | Priority |
|------|----------------|----------|
| Route handlers | New features add or modify routes | High |
| Service layer | Layer boundary violations concentrate here | High |
| Data access / repositories | ORM and schema errors need integration tests | High |
| Utilities and helpers | [Pattern replication](../../anti-patterns/pattern-replication-risk.md) — agents copy utilities ([GitClear, 2025](https://www.gitclear.com/ai_assistant_code_quality_2025_research)) | Medium |
| Configuration loading | Subtle misuse needs test assertions | Medium |

Cover the paths agents modify most before chasing edge cases.

**Write assertions with informative failure output:**

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

The more structured the assertion, the more specific the agent's fix.

**Integration tests over unit tests** for agent-critical paths: they catch ORM misuse, transaction errors, and layer violations that mocked unit tests miss. LangChain's Terminal Bench gains came from structural verification, not mock-based unit tests ([LangChain](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)).

### Step 3: Write Linter Rules with Remediation Messages

Standard linter rules flag violations; agent-useful rules explain the fix. The message enters context at the exact moment of the wrong decision — just-in-time delivery.

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

**High-value rule targets:**

| Rule | Prevents | Remediation should say |
|------|----------|------------------------|
| No direct DB imports | Layer violations | "Use repository in src/repositories/" |
| No raw `Error` throw | Inconsistent error handling | "Use AppError subclasses from src/errors/" |
| No implicit `any` in new files | Type coverage erosion | "Annotate the parameter type explicitly" |
| No console.log in src/ | Debug output in production | "Use the logger from src/utils/logger.ts" |
| Import boundaries by directory | Architecture violations | "This layer cannot import from X; put shared code in Y" |

### Step 4: Add a Pre-Commit Hook

A pre-commit hook gates agent output before it enters version history.

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

Commit → hook runs → on failure the commit is rejected with the error → agent reads, fixes, commits again. This is the [Ralph Wiggum Loop](../../agent-design/ralph-wiggum-loop.md) at the commit boundary.

### Step 5: Verify the Transition

Exit check:

1. Ask the agent to add a function to an existing service that calls a repository
2. Does it write code, run lint, read the error, and self-correct without intervention?
3. Introduce a deliberate type error — does the agent fix it?

If the agent still needs you to correct mechanical errors (wrong imports, types, error class), the loops are not tight enough. Typical causes: linter rules without remediation messages, too many `any` types, tests that miss the paths the agent modifies.

## When This Backfires

The L1→L2 transition is high-leverage but not free. Three conditions make it a poor investment:

- **Large existing `any` surface**: strict mode on a codebase with hundreds of implicit `any` types floods unrelated files with errors. Fix cost dwarfs the agent benefit until most are annotated. Start with `noImplicitAny` scoped to new files; expand incrementally.
- **High-churn paths with low test stability**: if integration tests on agent-critical paths break frequently from schema or environment drift, agents learn to ignore failing tests rather than treat them as signal. Stabilize the environment before relying on tests as a feedback source.
- **Monorepos with shared strict config**: enabling strict mode in one package cascades errors into shared libraries consumed elsewhere. Coordinate across package owners or use path-scoped tsconfig overrides to contain the blast radius.

---

## Key Takeaways

- **Agent autonomy scales with backpressure quality**, not with model capability ([Anthropic](https://code.claude.com/docs/en/best-practices)). A codebase with strict types and meaningful test coverage on critical paths enables autonomous agent iteration. A codebase without them requires manual review of every output.
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
- [Brownfield to Agent-First: Repo Maturity Framework](index.md) — full L0–L5 framework overview
