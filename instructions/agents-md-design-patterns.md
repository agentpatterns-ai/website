---
title: "AGENTS.md Design Patterns: Commands, Boundaries, Personas"
description: "Four patterns from 2,500+ repo analysis: executable commands, code-over-prose style, three-tier boundaries, and specialist personas for AGENTS.md."
tags:
  - instructions
  - technique
  - copilot
aliases:
  - "AGENTS.md best practices"
  - "AGENTS.md writing patterns"
---

# AGENTS.md Design Patterns: Commands, Boundaries, and Personas

> Effective AGENTS.md files give agents a specific job description — not a vague identity — using four concrete patterns drawn from analysis of 2,500+ real repositories.

## Overview

GitHub's analysis of over 2,500 `AGENTS.md` files identified a single primary failure mode: vagueness. Files that say "you are a helpful coding assistant" produce inconsistent results. Files that specify runnable commands, show style via code examples, define explicit permission tiers, and name specialist agents produce consistent behaviour without ongoing [prompt engineering](../training/foundations/prompt-engineering.md).

The four patterns below cover the authoring decisions that differentiate effective files from ineffective ones. They are independent and composable.

## Pattern 1 — Executable Commands

Place runnable commands early in the file. Agents reference them throughout their work.

**What not to write:**

```
Testing: run the test suite
Linting: use the linter
```

**What to write:**

```
Testing: pytest -v tests/
Linting: npm run lint --fix
Type checking: tsc --noEmit
```

Include the actual flags. "Run tests" leaves the invocation open to interpretation; `pytest -v` does not. The most common agent errors in the analysis stemmed from omitting commands entirely or listing tool names without invocation details.

Six areas to cover: commands, testing practices, project structure, code style, git workflow, and boundaries. Missing any one area is the second-most-common failure pattern after vagueness.

## Pattern 2 — Code Over Prose for Style

One real code snippet demonstrating your project's conventions is more reliable than three paragraphs describing them. Show what correct output looks like; agents infer the pattern.

**Instead of:**

> Use descriptive variable names and prefer functional style. Keep functions short and avoid side effects where possible.

**Write:**

```typescript
// Correct
const fetchUserById = (id: string): Promise<User> =>
  db.users.findOne({ id });

// Wrong — imperative, mutation, no return type
function getUser(id) {
  user = db.users.findOne({ id });
  return user;
}
```

This approach also works for commit message format, file naming, and any output that must conform to a specific shape.

## Pattern 3 — Three-Tier Boundaries

Structure permissions as three explicit tiers rather than a flat list of prohibitions.

```markdown
## Boundaries

✅ Always do
- Write a test for every new function
- Use conventional commits: `type(scope): description`

⚠️ Ask first
- Modify the database schema
- Change public API contracts
- Add new dependencies

🚫 Never do
- Commit secrets or credentials
- Push directly to main
- Modify infrastructure files
```

The always/ask/never structure makes the permission model scannable and explicit. The most common constraint across the 2,500+ repositories was "Never commit secrets" — it appeared across nearly all effective files regardless of stack.

Note: this three-tier format is a community convention. The AGENTS.md spec itself provides no standardised boundary syntax; the emoji tiers are an emergent pattern, not a spec requirement.

## Pattern 4 — Specialist Personas

Define narrow, named agents with explicit scope exclusions rather than one generalist. Start with one and expand based on observed mistakes.

```markdown
## Agents

### @test-agent
Writes unit and integration tests. Never removes failing tests. Never modifies
production code — only test files.

### @lint-agent
Fixes code formatting and import ordering. Never modifies logic, renames
variables, or changes function signatures.

### @docs-agent
Reads source code and generates API documentation. Never modifies source files.
```

Each persona answers: what does this agent produce, and what is it not allowed to touch? The scope exclusion is as important as the responsibility — it prevents an agent from drifting into adjacent work during a long session.

The recommended starting point is one specialist (e.g. `@test-agent`), not a full suite. Upfront over-specification produces personas that conflict or leave gaps that no agent owns.

## Trade-offs

| Approach | Pros | Cons |
|----------|------|------|
| Specific executable commands | Agents invoke correctly on first try | Requires updating when tooling changes |
| Code examples for style | Zero interpretation error on format | Longer file; more context consumed |
| Three-tier boundaries | Scannable permission model | Boundary syntax is not standardised across tools |
| Specialist personas | Reduces scope creep and conflicts | Requires knowing failure modes before defining them |
| Vague generalist file | Fast to write initially | Inconsistent agent behaviour, difficult to debug |

## Key Takeaways

- The primary failure in real-world AGENTS.md files is vagueness — specific runnable commands fix most inconsistency
- One code snippet outperforms paragraphs of style description because it eliminates interpretation
- Three-tier boundaries (✅ always / ⚠️ ask / 🚫 never) are a community convention, not a spec requirement
- Start specialist personas from observed failure modes, not upfront planning
- Cover all six areas: commands, testing, project structure, code style, git workflow, boundaries

## Sources

- [How to write a great AGENTS.md — lessons from over 2,500 repositories](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/)
- [AGENTS.md Open Standard](https://agents.md)
- [GitHub Copilot: Custom Instructions](https://docs.github.com/en/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot)

## Unverified Claims

- Stack specificity (e.g. "React 18 with TypeScript, Vite, and Tailwind CSS" over "React project") measurably improves agent behaviour `[unverified]`
- The three-tier emoji format produces higher compliance than prose-only boundaries `[unverified]`

## Related

- [Project Instruction File Ecosystem](instruction-file-ecosystem.md)
- [Example-Driven vs Rule-Driven Instructions](example-driven-vs-rule-driven-instructions.md)
- [Instruction Polarity: Positive Rules Over Negative](instruction-polarity.md)
- [Persona-as-Code: Defining Agent Roles as Structured Docs](../agent-design/persona-as-code.md)
- [AGENTS.md as Table of Contents](agents-md-as-table-of-contents.md)
- [AGENTS.md Distributed Conventions](agents-md-distributed-conventions.md)
- [AGENTS.md: A README for AI Coding Agents](../standards/agents-md.md)
- [Evaluating AGENTS.md: When Context Files Hurt More Than Help](evaluating-agents-md-context-files.md)
- [CLAUDE.md Convention](claude-md-convention.md)
- [Hierarchical CLAUDE.md](hierarchical-claude-md.md)
- [Layered Instruction Scopes](layered-instruction-scopes.md)
- [Negative-Space Instructions](negative-space-instructions.md)
- [Standards as Agent Instructions](standards-as-agent-instructions.md)
