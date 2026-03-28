---
title: "Verification Ledger for Tracking Agent Output Quality"
description: "Replace self-reported agent claims with structured records — every verification step is an INSERT with tool and exit code; every evidence bundle is a SELECT."
aliases:
  - verification log
  - audit trail
  - evidence log
tags:
  - agent-design
  - testing-verification
  - observability
---

# Verification Ledger

> Replace self-reported agent claims ("Build passed") with structured records — every verification step is an INSERT, every evidence bundle is a SELECT.

## The Problem with Self-Reported Verification

Agent workflows typically rely on the agent's own prose assertions about verification: "Build passed. Tests green. No issues found." These claims are unfalsifiable within the conversation. The agent may hallucinate that checks passed, skip steps silently, or assert results without running the actual tool. See [Trust Without Verify](../anti-patterns/trust-without-verify.md) for the full anti-pattern.

## Structured Proof

A verification ledger records every check as structured data rather than prose. Burke Holland's [Anvil agent](https://github.com/burkeholland/anvil/blob/main/agents/anvil.agent.md) implements this with a SQL table:

```sql
CREATE TABLE IF NOT EXISTS anvil_checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    phase TEXT NOT NULL CHECK(phase IN ('baseline', 'after', 'review')),
    check_name TEXT NOT NULL,
    tool TEXT NOT NULL,
    command TEXT,
    exit_code INTEGER,
    output_snippet TEXT,
    passed INTEGER NOT NULL CHECK(passed IN (0, 1)),
    ts DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

The core rule: every verification step must be an INSERT with the tool name, command, exit code, and output. The evidence bundle is a SELECT query against this table, not agent-written prose. If the INSERT did not happen, the verification did not happen.

## Baseline Capture

Before making any changes, the agent captures the current system state — IDE diagnostics, build exit code, test results — and INSERTs them with `phase = 'baseline'`. This enables regression detection: any check that was `passed=1` before changes but `passed=0` after reveals a regression the agent introduced, not a pre-existing failure.

## Gate Enforcement

Gates prevent the agent from skipping ahead. The Anvil pattern uses SQL count checks as gates ([Anvil agent](https://github.com/burkeholland/anvil/blob/main/agents/anvil.agent.md)):

- "Do NOT proceed to implementation until baseline INSERTs are complete"
- "Do NOT present evidence until `SELECT COUNT(*) FROM anvil_checks WHERE phase = 'after'` returns sufficient rows"

This enforces ordering through data, not through trusting the agent to follow instructions. The agent cannot present a passing evidence bundle if the rows do not exist.

## Evidence Bundles

The bundle is generated from a query, eliminating hallucinated results:

```sql
SELECT phase, check_name, tool, command, exit_code, passed, output_snippet
FROM anvil_checks WHERE task_id = '{task_id}' ORDER BY phase DESC, id;
```

The output is presented as a structured table showing baseline state, post-change state, regressions (baseline passed but after failed), and review verdicts. Confidence levels derive from data: "High" means all tiers passed and reviewers found zero issues; "Low" means a check failed or a reviewer raised an unresolved concern.

## Applying the Pattern

The full SQL-backed ledger requires tooling that supports persistent databases across agent turns (Anvil uses VS Code's session storage). Lighter implementations use the same principle:

- **File-based**: write verification results to a JSON or YAML file after each check, read it back to generate the bundle
- **Inline structured output**: require the agent to emit verification in a fixed schema (tool, command, exit_code, passed) rather than prose — parseable by downstream gates
- **CI integration**: pipe verification records into existing CI reporting, making agent-produced evidence auditable alongside human CI runs

The key constraint is that evidence must be produced by tool calls, not asserted by the agent. See [Deterministic Guardrails](deterministic-guardrails.md) for the broader principle.

## Example

A coding agent uses a JSON file as a lightweight verification ledger. Before editing any source files, the agent runs the existing test suite and records the baseline:

```json
[
  {
    "task_id": "fix-auth-timeout",
    "phase": "baseline",
    "check_name": "unit-tests",
    "tool": "pytest",
    "command": "pytest tests/unit -q",
    "exit_code": 0,
    "passed": 1,
    "output_snippet": "42 passed in 3.1s"
  },
  {
    "task_id": "fix-auth-timeout",
    "phase": "baseline",
    "check_name": "type-check",
    "tool": "mypy",
    "command": "mypy src/auth.py",
    "exit_code": 0,
    "passed": 1,
    "output_snippet": "Success: no issues found"
  }
]
```

After making changes, the agent re-runs the same checks and appends `"phase": "after"` entries. A gate in the agent instructions enforces the rule: "Do NOT mark the task complete until `verification.json` contains at least one `after` entry for every `baseline` check_name, and all `after` entries show `passed: 1`." The agent reads the file back to generate an evidence summary:

```text
| Phase    | Check       | Tool   | Exit | Passed |
|----------|-------------|--------|------|--------|
| baseline | unit-tests  | pytest | 0    | yes    |
| baseline | type-check  | mypy   | 0    | yes    |
| after    | unit-tests  | pytest | 0    | yes    |
| after    | type-check  | mypy   | 0    | yes    |

Regressions: 0. Confidence: High.
```

If the agent skips a check, the missing `after` row makes the gap visible and the gate blocks completion.

## Key Takeaways

- Self-reported verification is unfalsifiable — replace prose claims with structured records
- Baseline capture before changes enables regression detection
- Gate enforcement through data queries prevents agents from skipping verification steps
- Evidence bundles generated from queries eliminate hallucinated results
- Confidence levels should derive from verification data, not agent judgment

## Related

- [Trust Without Verify](../anti-patterns/trust-without-verify.md)
- [Incremental Verification](incremental-verification.md)
- [Deterministic Guardrails](deterministic-guardrails.md)
- [Behavioral Testing for Agents](behavioral-testing-agents.md)
- [Data Fidelity Guardrails](data-fidelity-guardrails.md)
- [Diff-Based Review](../code-review/diff-based-review.md)
- [Pre-Completion Checklists](pre-completion-checklists.md)
- [Model a Single Agent Turn as Many Inference and Tool-Call Iterations](../agent-design/agent-turn-model.md)
- [Structured Output Constraints](structured-output-constraints.md)
- [Grade Agent Outcomes](grade-agent-outcomes.md)
