---
title: "L3 → L5: Reaching Agent-First from a Brownfield Repo"
description: "Transform an Agent-Operable codebase (L3) through Agent-Safe (L4) to Agent-First (L5) by adding evals, output validation gates, goal specifications, and agentic CI integration."
tags:
  - training
  - agent-design
  - workflows
  - evals
  - tool-agnostic
---

# L3 → L5: Reaching Agent-First

> L3 gives agents a constrained, reliable execution environment. L4 adds validated output gates so agent work is bounded and auditable. L5 is the target state: goal-driven execution where the agent plans and implements multi-step workflows autonomously.

---

## What L3 Looks Like

At L3, the agent executes scoped tasks reliably without per-action supervision. Mechanical enforcement, structured tasks, and progress files are in place. Remaining gaps:

- Agent PRs require full human review — no automated quality gate beyond lint/tests
- No measurement of agent output quality over time
- Tasks require explicit step-by-step specification; the agent cannot plan independently
- No CI-level agentic workflow — every agent session is manually initiated

## What L5 Looks Like

At L5, the agent operates as a first-class contributor:

- Output validation gates catch known failure classes before human review
- Evals measure agent quality continuously and gate model upgrades
- The agent receives goal specifications (intent + success criteria) rather than step-by-step tasks
- Agent work integrates into CI/CD — issues trigger agent sessions, agent sessions produce PRs

**L4 is an intermediate state**: bounded-risk autonomy. L5 adds goal-driven planning and CI integration on top.

[Anthropic autonomy data](https://www.anthropic.com/research/measuring-agent-autonomy) shows experienced users (~750 sessions) enable full auto-approve in 40%+ of their work, but 80% of tool calls still come from agents with at least one safeguard. L5 is the objective, not an expectation for every task type.

---

## The L3 → L4 Transition: Adding Safety Gates

### Step 1: Define Output Validation Rules

At L3, agent output passes if lint, types, and tests pass. L4 adds policy-level validation: rules that check what the agent changed, not just whether the code compiles.

**Diff validation in CI:**

```yaml
# .github/workflows/agent-pr.yml
name: Agent PR Validation
on:
  pull_request:
    branches: [main]
    # Triggered for PRs from agent branches
    paths-ignore: ['docs/**', '*.md']

jobs:
  validate-agent-output:
    if: startsWith(github.head_ref, 'agent/') || startsWith(github.head_ref, 'copilot/')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Check test coverage threshold
        run: |
          npm test -- --coverage --run
          # Configure coverage thresholds in vitest.config.ts under coverage.thresholds
          # CI fails automatically when coverage drops below the configured threshold

      - name: Verify no direct DB imports added
        run: |
          git diff origin/main...HEAD -- '*.ts' | grep '^+.*from.*db/connection' \
            && echo "FAIL: agent PR added direct DB imports" && exit 1 \
            || echo "PASS: no direct DB imports found"

      - name: Verify new endpoints have tests
        run: |
          # Custom script that checks: any new route file must have a corresponding .test.ts
          node scripts/check-test-pairing.js
```

**Coverage enforcement on changed files** beats global coverage thresholds in brownfield repos with uneven coverage: it prevents erosion on new code without forcing a big-bang coverage rewrite.

### Step 2: Add Observability for Agent Sessions

L4 requires visibility into what agents did and why — not just whether the output is correct — for audit and debugging when results surprise.

**Structured agent work branches:** name them consistently (`agent/issue-123-add-rate-limiting`, `copilot/feature/user-preferences`) so agent PRs are identifiable and CI can apply agent-specific validation rules.

**Commit annotation:** include a structured trace in the commit message or as a PR comment:

```
feat(rate-limit): implement sliding window rate limiter

Implementation notes (agent session):
- Considered token bucket approach; chose sliding window for accuracy at boundary
- Redis MULTI/EXEC used for atomic increment — see comment in rate-limiter.ts:47
- Alternative: in-memory store with periodic flush (rejected: doesn't support multi-instance)

Tests: 12 unit, 2 integration (all passing)
Lint: clean
Type check: clean
```

An in-band audit trail — reviewers understand agent decisions without reading the full session transcript.

### Step 3: Define Rollback Triggers

Define the conditions under which agent work is automatically rejected or flagged before granting broader autonomy:

| Trigger | Response |
|---------|----------|
| CI fails on agent PR | Auto-close PR, comment with failure summary, re-open issue |
| Coverage drops below threshold on changed files | Block merge, request human review |
| Diff size exceeds limit (e.g., >500 lines) | Flag for human review before merge approval |
| Agent PR modifies security-sensitive paths | Require security team approval |

[Anthropic's autonomy research](https://www.anthropic.com/research/measuring-agent-autonomy) confirms 80% of tool calls come from agents with at least one safeguard — L4 formalizes and automates those safeguards.

---

## The L4 → L5 Transition: Goal-Driven Execution

### Step 1: Write Goal Specifications

L3 tasks prescribe steps; L5 goal specifications declare the outcome and acceptance criteria, leaving the plan to the agent.

```yaml
# goals/add-user-preferences.yaml
goal: Add user preferences storage and retrieval

success_criteria:
  - GET /users/:id/preferences returns structured preferences object
  - PUT /users/:id/preferences validates and persists preferences
  - All operations protected by existing auth middleware
  - Integration tests cover happy path and validation errors
  - Coverage on new files >= 90%

constraints:
  - Must use existing auth middleware (do not modify src/middleware/auth.ts)
  - Preferences stored in existing Postgres DB (no new services)
  - Follow existing service/repository/route pattern

out_of_scope:
  - UI changes
  - Admin preferences management
  - Preference versioning or history
```

The agent decomposes the spec into steps, executes them, verifies against success criteria, and submits a PR. The human reviews the PR, not the plan.

**Why goal specs outperform step-by-step tasks at L5**: structured task definitions constrain *how* the agent works; goal specs define *what* "done" means and let the agent find a better path than a human would prescribe. The [SASE paper (arXiv:2509.06216)](https://arxiv.org/abs/2509.06216) frames this as the SE 3.0 → SE 4.0 transition: goal-agentic to domain-autonomous.

### Step 2: Add Evals for Continuous Quality Measurement

Evals measure agent output quality across runs and over time — answering "is the agent getting better or worse?" in a way pass/fail CI cannot. CI checks syntactic validity; evals check whether output is correct, complete, and consistent with your quality bar.

A minimal eval suite for a brownfield repo:

```python
# evals/test_agent_endpoints.py
# Run with: pytest evals/ -v

def test_agent_adds_endpoint_with_tests():
    """Agent should add a new endpoint and include integration tests"""
    result = run_agent_task("add GET /health/detailed endpoint")
    assert result.files_created  # agent created new files
    assert any("test" in f for f in result.files_created)  # tests included
    assert result.ci_passes  # lint, type, test all pass

def test_agent_respects_layer_boundaries():
    """Agent should not add direct DB imports to route handlers"""
    result = run_agent_task("add endpoint to fetch user count from database")
    route_files = [f for f in result.files_modified if "routes/" in f]
    for f in route_files:
        assert "db/connection" not in open(f).read()

def test_agent_handles_existing_pattern():
    """Agent should follow existing repository pattern, not invent alternatives"""
    result = run_agent_task("add UserPreferences repository")
    repo_file = find_file(result, "repositories/user-preferences")
    assert repo_file is not None
    assert uses_drizzle_orm(repo_file)  # not raw SQL
```

See the [Eval-Driven Development](../../workflows/eval-driven-development.md) and [Eval Engineering](../../training/foundations/eval-engineering.md) modules for full eval design methodology.

### Step 3: Integrate Agents into CI/CD

At L5, agents enter the pipeline without manual invocation: an issue triggers a session, the session produces a PR, CI validates it, and human review focuses on design — not mechanical correctness.

**GitHub Actions workflow for issue-triggered agent work:**

```yaml
# .github/workflows/agent-implementation.yml
name: Agent Implementation
on:
  issues:
    types: [labeled]

jobs:
  implement:
    if: github.event.label.name == 'agent-implement'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run agent implementation
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          claude -p "
            Read GitHub issue #${{ github.event.issue.number }}.
            Implement the feature described using the goal specification pattern.
            Follow .claude/skills/implement-issue/SKILL.md.
            Create a PR when complete.
          " \
          --allowedTools "Read,Write,Edit,Bash(git*),Bash(npm*),Bash(gh*)" \
          --permission-mode auto

      - name: Label issue as in-progress
        run: gh issue edit ${{ github.event.issue.number }} --add-label "agent-in-progress"
```

This depends on L3 and L4 infrastructure: hooks, output validation gates, and rollback triggers are what make per-task autonomy safe.

### Step 4: Verify the Transition

L4 exit check:

1. Open a PR from an agent branch that introduces a direct DB import (layer-rule violation). Verify CI validation catches and blocks it.
2. Review 10 recent agent PRs — what share required human corrections beyond review comments? Target: below 20%.

L5 exit check:

1. Create a well-scoped issue with a clear acceptance criterion. Apply the `agent-implement` label. Does the agent ship a PR that meets the criterion without clarification?
2. Compare agent PR review time to human PR review time. L5 review should focus on design, not mechanical errors.

---

## When to Stay at L3 or L4

Not every team needs the full L3→L5 pipeline. Stop at L3 if:

- **Low agent PR volume** — under a handful of agent sessions per week, CI automation overhead (evals, issue-triggered workflows, coverage gates) costs more than it saves.
- **Unstable codebase structure** — eval suites break with every architecture change; in fast-moving repos where the service/repository pattern itself is evolving, they become a maintenance burden, not a quality gate.
- **Unbounded API cost exposure** — issue-triggered sessions fire on every label with no per-task budget cap; backlogs can generate surprise spend before PR review catches systematic failure.

Stop at L4 if:

- **Tasks are not goal-decomposable** — open-ended exploration, cross-cutting refactors, or work that depends on unwritten requirements lacks the verifiable acceptance criteria L5 needs.
- **Insufficient test coverage** — evals are only meaningful for testable behaviors. Below ~50% coverage on the touched code paths, evals give false confidence rather than real signal.

---

## Key Takeaways

- **L4 is about trust, not capability.** The infrastructure that makes agent work reviewable and rollback-safe is what justifies expanding scope — not confidence in the model. Define rollback triggers before granting broader autonomy.
- **Goal specifications unlock planning**. Structured tasks constrain how agents work; goal specs define what "done" means and let agents find better paths than step-by-step task lists.
- **Evals are the L5 quality gate.** Pass/fail CI validates syntax; evals validate quality. You need both to operate at L5 without accumulating hidden quality debt.
- **L5 is the objective, not the expectation for every task.** Experienced users enable full auto-approve in ~40% of sessions ([Anthropic](https://www.anthropic.com/research/measuring-agent-autonomy)). Reserve L5 workflows for well-specified, testable tasks in well-understood parts of the codebase.
- **The transformation is the practice.** The infrastructure you build to reach L5 — types, tests, hooks, evals, structured tasks — benefits human developers equally. It is not agent-specific overhead; it is engineering rigor relocated.

## Related

- [Eval-Driven Development](../../workflows/eval-driven-development.md) — the workflow pattern for writing evals before building agent features
- [Progressive Autonomy Model](../../human/progressive-autonomy-model-evolution.md) — how to scale agent trust incrementally with metrics
- [Structured Agentic Software Engineering](../../agent-design/structured-agentic-software-engineering.md) — the SE 0–5 maturity model and structured artifact types ([arXiv:2509.06216](https://arxiv.org/abs/2509.06216))
- [Headless Claude in CI](../../workflows/headless-claude-ci.md) — running Claude Code non-interactively in CI pipelines
- [Agent Harness](../../agent-design/agent-harness.md) — the initializer/coding-agent architecture for long-running work
- [L2 → L3: Building Mechanical Enforcement](level-2-to-3.md) — previous module
- [Brownfield to Agent-First: Repo Maturity Framework](index.md) — full L0–L5 framework overview
