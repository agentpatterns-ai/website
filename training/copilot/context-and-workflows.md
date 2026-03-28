---
title: "GitHub Copilot: Context Engineering & Agent Workflows"
description: "How context engineering determines agent output quality. Covers context design, task decomposition, delegation, steering, and review workflows."
tags:
  - training
  - copilot
---

# GitHub Copilot: Context Engineering & Agent Workflows

> Context engineering is the discipline of controlling what enters the agent's context window, when, and in what structure. It determines consistent output quality more than any individual prompt.

The difference between a developer who configures Copilot and one who gets consistently good results is **context engineering**. Knowing which surfaces exist and how to configure them is necessary but not sufficient — you also need to design what goes into each layer, manage the finite context budget, decompose tasks to fit within it, and steer agent sessions when they drift.

---

## Context Engineering vs Prompt Engineering vs Harness Engineering

**Prompt engineering** is writing a good question. **Context engineering** is designing the entire information environment the agent operates in — before, during, and across sessions. **Harness engineering** is building the development environment so the agent can self-correct without human intervention.

| | Prompt engineering | Context engineering | Harness engineering |
|-|-------------------|-------------------|-------------------|
| **Scope** | The user message | Everything in the context window: system prompt, instructions, tool outputs, conversation history, file contents | The development environment: type system, test suite, linters, CI pipeline, repo structure |
| **When** | At the moment you ask | Before the session (instructions, skills, Spaces), during (tool results, steering), and across sessions (memory) | Before any session — baked into the codebase and toolchain |
| **Optimises for** | A good answer to this question | Consistent quality across all questions in this codebase | Agent self-correction — the agent iterates until checks pass without human help |
| **Who does it** | The person asking | The team, via committed configuration files | The team, via tooling investments (types, tests, linters, hooks) |
| **Failure mode** | Bad answer to one question | Inconsistent results across sessions | Agent can't verify its own work — every output requires manual review |
| **Durability** | Per-message | Per-repo, evolves with configuration | Permanent — compounds across all agents, all sessions, all team members |

A well-crafted prompt in a poorly configured environment produces inconsistent results. A mediocre prompt in a well-engineered context produces good results reliably. A well-engineered context in a codebase without backpressure still requires manual verification of every output. All three layers compound: prompt quality × context design × environment feedback loops. The [customization stack](customization-primitives.md) — instructions, agents, skills, hooks, MCP, Spaces, memory — is context engineering infrastructure. The type system, test suite, and linter rules covered in [Harness Engineering](harness-engineering.md) are harness engineering infrastructure.

### Why this matters for Copilot specifically

Every token in the context window has an opportunity cost. Copilot's context includes:

```
System prompt (Copilot's own instructions)
+ Organization instructions
+ Repository instructions (.github/copilot-instructions.md)
+ Path-specific instructions (matching .instructions.md files)
+ Agent definition (if using a custom agent)
+ Skill content (if a skill is activated)
+ MCP tool definitions
+ Space contents (if a Space is referenced)
+ Conversation history
+ Tool outputs (file reads, terminal output, search results)
+ Your message
───────────────────────────────────
= Total context consumed
```

You control most of this stack. The [Customization Primitives](customization-primitives.md) page covers how to configure each layer. The rest of this page covers how to decide what goes in them and why.

---

## How the Context Window Works

### Attention is not uniform

Transformer models don't process all tokens equally. Attention follows a [U-shaped curve](../../context-engineering/lost-in-the-middle.md):

- **Highest attention**: The first tokens (system prompt, instructions) and the most recent tokens (your latest message, recent tool output).
- **Lowest attention**: The middle — earlier conversation turns, older tool outputs, verbose file contents loaded 20 messages ago.

This has practical consequences:

| Principle | What to do |
|-----------|-----------|
| **Lead with constraints** | Put critical rules at the top of `copilot-instructions.md`, not buried after context-setting prose. "Do not mock the database" belongs in the first 5 lines. |
| **Recency wins** | If a rule matters for the current task, restate it in your message — don't rely on it being in the instructions file 50,000 tokens ago. |
| **Boilerplate wastes prime position** | "You are a helpful assistant" at the top of an agent file wastes the highest-attention tokens. Start with constraints and domain rules. |

### Context budget

The context window is finite. Every token preloaded into context displaces a token available for reasoning, tool results, and implementation.

**Target**: ≤50% context utilization after preloading. The remaining 50% is working memory — space for the agent to read files, run commands, iterate, and think.

This is why the [customization stack](customization-primitives.md) uses **progressive disclosure** — a design pattern where you preload only what every task needs, and load everything else on demand.

---

## Progressive Disclosure: Why Skills Are Designed This Way

### The problem with monolithic context

A 500-line `copilot-instructions.md` that covers every convention, every edge case, and every procedure for every task type has a compounding problem:

1. **Budget waste** — most of those 500 lines are irrelevant to any given task. A developer adding a React component doesn't need the database migration procedure.
2. **Attention dilution** — the more instructions loaded, the less attention any single instruction receives. Critical rules get lost in the volume.
3. **Stale context** — large monolithic files are harder to maintain. Rules drift out of date and start contradicting the codebase.

### The progressive disclosure pattern

The customization stack solves this with two layers:

```
Always-on (preloaded):
  - Repository instructions     (~50 lines of universal rules)
  - Path-specific instructions   (scoped, only when files match)
  - Agent definitions            (<50 lines: identity + scope + quality bar)
  - Skill descriptions           (one-line summaries — just enough for selection)

On-demand (loaded when needed):
  - Full skill content           (SKILL.md + resources, loaded when task matches)
  - Space contents               (loaded when explicitly referenced)
  - File reads / tool outputs    (loaded by the agent during execution)
```

**Skills are the clearest example.** A skill's description is always available — the agent sees "generate-changelog: Generates a CHANGELOG.md entry from recent commits" and decides whether the task matches. Only when the agent activates the skill does the full `SKILL.md` and its resources enter context.

This is not an implementation detail — it's the core design principle. Agent definitions should be under 50 lines. Skills carry all detailed knowledge. The instruction file encodes universal rules, not comprehensive documentation.

### Practical sizing guidance

| Layer | Target size | If it's too big |
|-------|------------|----------------|
| `copilot-instructions.md` | ≤100 lines (~2 pages) | Split area-specific rules into path-specific `.instructions.md` files |
| Path-specific instructions | ≤50 lines each | You're writing documentation, not instructions — link to docs instead |
| Agent definitions | ≤50 lines (body) | Move task procedures into skills; the agent references them on demand |
| Skill descriptions | 1–2 sentences | The description is a trigger, not documentation |
| `SKILL.md` content | No hard limit, but ≤200 lines | Break into multiple focused skills |

---

## Context Rot

### What it is

As a session runs, the context window fills with conversation history, tool outputs, and accumulated state. Output quality degrades — not linearly, but with a cliff.

**Symptoms**:

- The agent ignores instructions it followed reliably earlier in the session
- Outputs become generic, losing project-specific conventions
- The agent loses track of constraints stated 30+ messages ago
- It starts repeating work or contradicting earlier decisions

### Why it happens

Context rot has two causes:

1. **Budget exhaustion** — the window fills, and either compression kicks in (losing detail) or the agent can't load new files it needs.
2. **Attention decay** — even within budget, tokens in the middle of a long context receive less attention. Instructions from message 3 matter less than the tool output from message 47.

### The degradation spectrum

Not all tasks degrade equally:

| Task type | Effective context | Notes |
|-----------|------------------|-------|
| Simple retrieval ("find the function that handles auth") | Large — works well even in long contexts | Lexical matching remains robust |
| Semantic retrieval ("explain the auth flow") | Moderate — degrades past ~32K tokens | Requires connecting concepts across the context |
| Reasoning ("refactor auth to use the new middleware pattern") | Small — 10–20% of window is effective | Multi-step reasoning degrades steeply with context size |
| Bug fixing across files | Very small — severe collapse in long contexts | Requires holding multiple file contents and reasoning about interactions |

**The practical implication**: For complex reasoning tasks, a fresh context with precisely loaded files outperforms a long-running session with accumulated history.

### Prevention and remediation

| Strategy | When to use | How |
|----------|------------|-----|
| **Fresh sessions for complex tasks** | Before starting a multi-file refactor or complex bug fix | Start a new chat. Load specific files with `#file` references. State the task clearly. |
| **Manual compaction** | Mid-session, when you notice quality dropping | Copilot CLI: `/compact`. VS Code: start a new session (no manual compact yet). |
| **Sub-agent isolation** | Research phase separate from implementation | In Copilot CLI, use a separate session for research. Summarise findings, then start a new session for implementation. |
| **Smaller tasks** | Prevent rot by finishing before it starts | Break large tasks into agent-sized chunks (see next section). |

---

## Task Decomposition for Agents

### The "clear written outcome" test

Before assigning a task to any agent surface (VS Code Agent, coding agent, CLI), ask:

> Can I describe the desired outcome clearly enough that a competent developer who's new to the repo could verify the result?

If yes → delegate. If no → the task needs decomposition or is better done by a human who holds the implicit context.

### What's too big

A task is too big for a single agent session when:

- It requires changes across **more than 5–7 files** (context budget pressure)
- The correct approach depends on **decisions not yet made** (the agent will guess wrong)
- It requires understanding **implicit context** that's not in the codebase (team preferences, unwritten rules, business context)
- It would take a human reviewer **more than 30 minutes** to verify the result

### What's too small

A task is too small for delegation when:

- **Describing it takes longer than doing it** — the delegation overhead exceeds the execution time
- It's a single-line change you already know how to make
- The review tax (verifying the agent's work) exceeds the implementation time

### The decomposition pattern

Break large tasks into a sequence of agent-sized chunks, each with a verifiable outcome:

```
Large task: "Migrate all database access from raw SQL to Drizzle ORM"

Decomposed:
1. Create Drizzle schema for the users table → verify: schema file exists, types match DB
2. Migrate UserRepository to use Drizzle → verify: tests pass, no raw SQL in file
3. Create Drizzle schema for the orders table → verify: schema file, types
4. Migrate OrderRepository → verify: tests pass
5. Remove raw SQL utilities → verify: no imports remain, tests pass
```

Each chunk is a separate agent session. Context stays fresh. Each result is independently verifiable.

---

## The Delegation Decision

### Supervised vs async

This is the same decision from the [surface framework](surface-map.md), now with context engineering reasoning:

| Factor | VS Code Agent (supervised) | Coding agent (async) |
|--------|---------------------------|---------------------|
| **Context** | You can steer mid-task, add context the agent didn't find | The agent works with whatever's in the issue + repo |
| **Session length** | You'll notice quality degradation and can restart | The agent manages its own context; you can't intervene |
| **Verification** | You see every edit as it happens | You review the PR after the fact |
| **Best for** | Tasks where you'd catch a wrong turn early | Tasks where the outcome is clearly verifiable from the PR |

### The delegation contract

Whether delegating to VS Code Agent or the coding agent, frame the task as a **contract**, not a step-by-step script:

```markdown
## Goal
Add rate limiting to the /api/upload endpoint.

## Constraints
- Use the existing RateLimiter class from src/middleware/rate-limiter.ts
- Limit: 10 requests per minute per authenticated user
- Return 429 with a Retry-After header

## Success condition
- The rate limiter test in src/middleware/__tests__/rate-limiter.test.ts passes
- A new integration test covers the 429 response case
- No other tests are broken

## Recovery
- If RateLimiter doesn't support per-user limits, add the capability to RateLimiter first
- If the test infrastructure doesn't support time mocking, flag it — don't implement a workaround
```

The agent decides *how*. You define *what*, *within what boundaries*, and *how to verify*.

---

## The Agent Workflow Loop

A well-structured agent session follows a consistent pattern:

### 1. Prime

Load context before asking the agent to act. **Read before write.**

**In VS Code Agent mode**:
```
Look at #file:src/middleware/rate-limiter.ts and #file:src/routes/upload.ts.
I need to add per-user rate limiting to the upload endpoint.
[... delegation contract ...]
```

**In the coding agent** (via issue):
```
The upload endpoint at src/routes/upload.ts needs per-user rate limiting.
The existing RateLimiter class is at src/middleware/rate-limiter.ts.
[... delegation contract ...]
```

The explicit file references ensure the agent reads the right files *first*, before reasoning about the task. Without them, the agent may start implementing before understanding the existing code.

### 2. Execute

The agent works autonomously — reading files, making edits, running commands, iterating.

**What to watch for** (VS Code Agent / CLI):

- **Tool calls** reveal the agent's plan. If it's reading files you didn't expect, it may be heading in the wrong direction.
- **Terminal output** shows test results and build errors in real time.
- **The first file edit** tells you whether the agent understood the existing patterns.

### 3. Steer (if needed)

If the agent is heading in the wrong direction, send a steering message **immediately** — the earlier, the better.

**Good steering**:
```
Stop — don't create a new rate limiter class. Use the existing one at
src/middleware/rate-limiter.ts. Read it first.
```

**Bad steering**: Waiting until the agent finishes a wrong approach, then asking it to redo everything. By then, the context is polluted with the wrong approach's tool outputs and edits.

**When to steer vs restart**:

- **Steer**: The agent is on a wrong path but hasn't gone far. A course correction recovers.
- **Restart**: The agent has made extensive wrong changes, and the context is saturated with the wrong approach. A fresh session with a better prompt is faster.
- **Let it finish**: The approach is acceptable, even if not exactly what you'd have done. The review tax for a slightly different approach is lower than restarting.

Over-steering signals an underspecified initial prompt. If you're steering every 3 messages, fix the prompt — don't manage the run.

### 4. Review

Agent work always requires human review. The question is how to structure it.

---

## Review Workflows

### The agent self-review loop

The coding agent reviews its own changes before opening a PR. It runs:

1. **Copilot code review** — style, patterns, common issues
2. **CodeQL** — code scanning for vulnerabilities
3. **Secret scanning** — hardcoded credentials
4. **Dependency checks** — known vulnerable packages

This catches mechanical issues. It does **not** catch:

- Architectural misjudgments
- Incorrect business logic
- Design decisions that technically work but are wrong for the codebase
- Missing requirements (the agent implemented what was asked, but the ask was incomplete)

### Human review focus

Since the agent's self-review handles mechanical checks, human reviewers should focus on what agents can't judge:

| Human review focus | What to look for |
|-------------------|-----------------|
| **Design fit** | Does this change fit the existing architecture, or did the agent introduce a parallel pattern? |
| **Completeness** | Did the agent address the full requirement, or just the literal text of the issue? |
| **What's missing** | Missing error paths, unhandled edge cases, absent `finally` blocks, no input validation |
| **Implicit knowledge** | Would a team member who knows the system have done this differently? Why? |

### The review pipeline

```
Agent self-review (automated)     → catches: style, vulnerabilities, secrets, dependency issues
  ↓
Copilot Code Review (automated)   → catches: patterns, common bugs, missed edge cases
  ↓
Human review                      → catches: design, architecture, business logic, completeness
```

Configure Copilot Code Review to run automatically on all PRs (Repository Settings → Code review → Copilot). This catches issues between the agent's self-review and human review — a second automated pass from a fresh context.

---

## Anti-Patterns

### Trust without verify

**What it is**: Accepting agent output because it looks polished — without running tests, checking diffs, or verifying claims.

**Why it's dangerous**: Agent output quality (fluency, formatting, confidence) is independent of correctness. The agent is most dangerous when it's *almost* right — close enough to pass a casual review, wrong enough to cause production issues.

**Prevention**: Verify against external ground truth. Run the tests. Read the diff line by line. Check that cited files and functions actually exist. If the agent says "this follows the existing pattern in UserRepository," open `UserRepository` and check.

### Infinite context loading

**What it is**: Dumping entire documentation, all project files, or comprehensive reference material into context "just in case" the agent needs it.

**Why it's dangerous**: Excess context dilutes attention, wastes budget, and accelerates context rot. The agent's ability to follow specific instructions decreases as total context volume grows.

**Prevention**: Load the minimum context needed. Use `#file` references for specific files, not `#codebase` for everything. Let skills and Spaces provide on-demand context rather than preloading.

### The yes-man agent

**What it is**: The agent executes every request without flagging problems — missing requirements, contradictory instructions, tasks that conflict with the codebase's existing patterns.

**Why it's dangerous**: Errors ship at machine speed. A human developer would say "this doesn't make sense because..." — the default agent just does it.

**Prevention**: Instructions that explicitly require the agent to flag concerns:

```markdown
## In copilot-instructions.md or an agent definition:

Before implementing, check:
- Does this conflict with existing patterns in the codebase?
- Are there missing requirements that would change the approach?
- Is this task well-defined enough to implement confidently?

If any check fails, explain the concern before proceeding.
```

### Scope creep in agent sessions

**What it is**: Starting with "add rate limiting" and gradually adding "also fix the error handling" and "while you're there, refactor the middleware" within the same session.

**Why it's dangerous**: Each addition pushes the session further from its original context. The agent's understanding of the combined task becomes progressively less coherent. Review becomes harder because the PR mixes unrelated changes.

**Prevention**: One task per session. One PR per task. If you spot something else that needs fixing, note it and start a separate session.

### Happy path bias

**What it is**: Agent-generated code that works for the common case but breaks on edge cases, error paths, and boundary conditions.

**Why it's dangerous**: The happy path is what you test manually and demo to stakeholders. The edge cases are what breaks in production at 2 AM.

**Prevention**: Name error scenarios explicitly in your delegation contract. "Handle the case where the user has no avatar URL (null). Handle the case where the upload exceeds the size limit. Handle the case where the rate limiter Redis connection is down." Naming specific failure modes reduces vulnerability density significantly compared to vague "handle errors" instructions.

---

## Worked Example: Issue to Merged PR

### Setup

Repository with:
```
.github/
  copilot-instructions.md            ← Stack, conventions, build commands
  instructions/
    api.instructions.md              ← Fastify conventions for src/routes/**
  agents/
    test-writer.agent.md             ← Test generation specialist
  hooks/
    security.json                    ← Block writes to /migrations/
```

### The task

Issue: "The `/api/users/:id` endpoint returns a 500 when the user has a null `avatar_url`. It should return the user object with `avatar_url: null` instead of crashing."

### Step 1: Assign to coding agent

Assign the issue to Copilot. The agent reads:

- The issue description (task context)
- `.github/copilot-instructions.md` (project conventions)
- `.github/instructions/api.instructions.md` (API-specific rules, matched by `applyTo` glob)

### Step 2: Agent works (async)

The agent:

1. Reads `src/routes/users.ts` — finds the handler
2. Reads the user repository — finds the query
3. Identifies the bug: `user.avatar_url.toString()` throws on null
4. Fixes the handler to handle null avatar
5. Writes a test for the null case
6. Runs the test suite — all pass
7. Self-reviews: Copilot code review, CodeQL, secret scanning
8. Opens a draft PR on a `copilot/fix-null-avatar` branch

### Step 3: Automated review

Copilot Code Review runs automatically on the PR. It checks:

- The fix matches the project's error handling patterns
- The test follows project conventions (from the instructions file)
- No new issues introduced

### Step 4: Human review

You review the PR. Agent self-review and Copilot code review already caught mechanical issues. You focus on:

- **Completeness**: Are there other places where `avatar_url` is assumed non-null?
- **Design fit**: Does the fix follow the existing null-handling pattern, or did the agent introduce a new one?
- **What's missing**: Should there be a migration to add a NOT NULL default, rather than handling null in every consumer?

### Step 5: Merge

The fix is correct and complete. Approve and merge.

Total human time: ~5 minutes of review. The agent handled investigation, fix, test, and self-review autonomously.

---

## Key Takeaways

- **Context engineering, not prompt engineering**, determines consistent output quality. A well-configured `.github/` directory with instructions, agents, skills, and hooks outperforms clever prompts in an unconfigured repo.
- **Attention is not uniform**. Critical rules belong at the top of instruction files. Restate important constraints in your message when working in long sessions.
- **Progressive disclosure is a budget pattern**: preload only universal rules; load task-specific knowledge on demand via skills. Agent definitions should be under 50 lines. Instructions files under 100.
- **Context rot is real**. Long sessions degrade output quality, especially for reasoning tasks. Start fresh sessions for complex work. Use `/compact` in the CLI. Break large tasks into agent-sized chunks.
- **Frame tasks as contracts** (goal, constraints, success condition, recovery), not step-by-step scripts. The agent decides how; you define what and how to verify.
- **Steer early or restart**. Don't wait for the agent to finish a wrong approach. The earlier you intervene, the less context is polluted.
- **Agent self-review handles mechanical checks**. Human review should focus on design, completeness, and implicit knowledge the agent can't access.
- **Name failure modes explicitly**. "Handle the case where X is null" produces better error handling than "handle errors." Specificity in the delegation contract translates directly to code quality.

## Related

**Training**

- [GitHub Copilot: Platform Surface Map](surface-map.md) — all surfaces and when to use each
- [GitHub Copilot: Customization Primitives](customization-primitives.md) — configuring instructions, agents, skills, hooks, MCP, Spaces, memory
- [GitHub Copilot: Harness Engineering](harness-engineering.md) — backpressure, repo legibility, mechanical enforcement
- [GitHub Copilot: Advanced Patterns](advanced-patterns.md) — multi-agent orchestration, parallel sessions, automation
- [GitHub Copilot: Model Selection & Routing](model-selection.md) — model roster, premium multipliers, context budget costs
- [GitHub Copilot: Team Adoption & Governance](team-adoption.md) — rollout, tiered review, shared configuration
- [Copilot CLI Agentic Workflows](../../tools/copilot/copilot-cli-agentic-workflows.md) — interactive and headless CLI modes, graduated authorization, delegation

**Context Engineering**

- [Context Engineering](../../context-engineering/context-engineering.md) — foundational discipline
- [Context Priming](../../context-engineering/context-priming.md) — pre-loading relevant files before agent tasks
- [Attention Sinks](../../context-engineering/attention-sinks.md) — how position affects attention weight
- [Context Budget Allocation](../../context-engineering/context-budget-allocation.md) — managing finite context as a budget
- [Context Compression Strategies](../../context-engineering/context-compression-strategies.md) — tiered compression for long sessions
- [Context Window Dumb Zone](../../context-engineering/context-window-dumb-zone.md) — where quality degrades and why

**Agent Design**

- [Progressive Disclosure for Agents](../../agent-design/progressive-disclosure-agents.md) — minimal definitions, on-demand skills
- [Delegation Decision](../../agent-design/delegation-decision.md) — when to delegate vs do it yourself
- [Steering Running Agents](../../agent-design/steering-running-agents.md) — mid-run course correction
- [Agent Self-Review Loop](../../agent-design/agent-self-review-loop.md) — automated pre-human review
- [Agent Backpressure](../../agent-design/agent-backpressure.md) — how type systems and tests enable agent autonomy

**Anti-Patterns**

- [Trust Without Verify](../../anti-patterns/trust-without-verify.md) — accepting polished output without verification
- [Infinite Context](../../anti-patterns/infinite-context.md) — context volume vs quality trade-off
- [Yes-Man Agent](../../anti-patterns/yes-man-agent.md) — agents that execute without flagging problems
- [Happy Path Bias](../../anti-patterns/happy-path-bias.md) — missing edge cases and error paths
