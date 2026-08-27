---
title: "Verification Ledger for Tracking Agent Output Quality"
term: "Verification Ledger"
description: "Replace self-reported agent claims with structured records — every verification step is an INSERT with tool and exit code; every evidence bundle is a SELECT."
aliases:
  - verification log
  - audit trail
  - evidence log
tags:
  - agent-design
  - testing-verification
  - observability
  - tool-agnostic
last_reviewed: 2026-06-12
maturity: established
---

# Verification Ledger for Tracking Agent Output Quality

> Replace self-reported agent claims ("Build passed") with structured records — every verification step is an INSERT, every evidence bundle is a SELECT.

Learn it hands-on with [The Verification Ledger guided lesson](https://learn.agentpatterns.ai/verification/the-verification-ledger/), which includes quizzes.

## The problem with self-reported verification

Agent workflows usually rely on the agent's own prose claims about verification: "Build passed. Tests green. No issues found." You cannot falsify these claims within the conversation. The agent may hallucinate that checks passed, skip steps silently, or assert results without running the tool — the [trust without verify](../patterns/anti-patterns/trust-without-verify.md) anti-pattern. Spotify's Honk team saw the same problem. They wired deterministic verifiers (format, build, test) into the agent loop and blocked PR creation when any verifier fails ([Spotify Engineering, "Background Coding Agents: Predictable Results Through Strong Feedback Loops"](https://engineering.atspotify.com/2025/12/feedback-loops-background-coding-agents-part-3)). See [Trust Without Verify](../patterns/anti-patterns/trust-without-verify.md) for the full anti-pattern.

## Structured proof

A verification ledger records every check as structured data rather than prose. Burke Holland's [Anvil agent](https://github.com/burkeholland/anvil/blob/main/agents/anvil.agent.md) does this with a SQL table:

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

## Baseline capture

Before making any changes, the agent captures the current system state — IDE diagnostics, build exit code, test results — and INSERTs them with `phase = 'baseline'`. This lets you detect regressions: any check that was `passed=1` before the changes but `passed=0` after reveals a regression the agent introduced, not a pre-existing failure.

## Gate enforcement

Gates stop the agent from skipping ahead. The Anvil pattern uses SQL count checks as gates ([Anvil agent](https://github.com/burkeholland/anvil/blob/main/agents/anvil.agent.md)):

- "Do NOT proceed to implementation until baseline INSERTs are complete"
- "Do NOT present evidence until `SELECT COUNT(*) FROM anvil_checks WHERE phase = 'after'` returns sufficient rows"

This enforces ordering through data, not through trusting the agent to follow instructions. The agent cannot present a passing evidence bundle if the rows do not exist.

## Evidence bundles

A query generates the bundle, which rules out hallucinated results:

```sql
SELECT phase, check_name, tool, command, exit_code, passed, output_snippet
FROM anvil_checks WHERE task_id = '{task_id}' ORDER BY phase DESC, id;
```

The output is shown as a structured table: baseline state, post-change state, regressions (baseline passed but after failed), and review verdicts. Confidence levels come from the data. "High" means all tiers passed and reviewers found zero issues. "Low" means a check failed or a reviewer raised an unresolved concern.

## Applying the pattern

The full SQL-backed ledger needs tooling that supports persistent databases across agent turns (Anvil uses VS Code's session storage). Lighter versions use the same principle:

- File-based: write verification results to a JSON or YAML file after each check, then read it back to generate the bundle
- Inline structured output: have the agent emit verification in a fixed schema (tool, command, exit_code, passed) rather than prose, so downstream gates can parse it
- CI integration: pipe verification records into existing CI reporting, so agent-produced evidence is auditable alongside human CI runs

The key constraint is that tool calls must produce the evidence, not the agent's own claims. See [Deterministic Guardrails](deterministic-guardrails.md) for the broader principle.

## When this backfires

The ledger is not free. Schema, INSERTs, gate queries, and bundle reads all cost time. It can cost more than it returns in these cases:

- Throwaway or exploratory work: one-shot edits, spikes, and scratch scripts do not need baseline/after bookkeeping. The overhead outweighs the regression-detection value on work you will discard.
- Unreliable underlying checks: flaky tests or false-positive linters mean the ledger faithfully records noise rather than the signal [deterministic guardrails](deterministic-guardrails.md) are meant to produce. Green rows mislead reviewers when the checks themselves do not tell signal from noise.
- Wrong checks recorded: complete rows for the wrong surface (for example, unit tests when the change breaks an integration contract) produce a clean bundle for a broken change. Ledger completeness is not verification completeness, the same gap a [pre-completion checklist](pre-completion-checklists.md) closes by listing the checks that must run.
- Agent writes its own rows: if the same agent runs the tool and writes the row, it can fake exit codes or skip the INSERT when a check fails. The ledger only holds when execution and recording are separated — CI, a harness, or a hook.
- Single-turn agents without persistent state: a SQL ledger is too heavy here. Inline [structured output](structured-output-constraints.md) (JSON per check) captures the same invariants with less plumbing.

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

## FAQ

**When does a verification ledger backfire?**

It costs more than it returns on throwaway or exploratory work, where baseline/after bookkeeping outweighs the regression-detection value. It also backfires when the underlying checks are unreliable — flaky tests or false-positive linters mean the ledger faithfully records noise — or when complete rows cover the wrong surface, producing a clean bundle for a change that actually broke something else.

**Can the same agent that runs the checks also write its own ledger rows?**

No. If the agent that executes a check also writes its row, it can fake exit codes or skip the INSERT when a check fails. The ledger only holds when execution and recording are separated, such as through CI, a harness, or a hook, so the recording step cannot be gamed by the agent it is meant to verify.

**What's a lightweight alternative to a full SQL-backed ledger?**

Not every setup supports persistent databases across agent turns. Lighter versions keep the same principle: write verification results to a JSON or YAML file after each check and read it back to generate the bundle, or have the agent emit a fixed schema (tool, command, exit_code, passed) so downstream gates can parse it instead of parsing prose.

**How did Spotify's Honk team put this pattern into production?**

The Honk team wired deterministic verifiers — format, build, and test — directly into the agent loop and blocked PR creation whenever any verifier failed, replacing trust in the agent's own claims with a hard gate on real check results ([Spotify Engineering, "Background Coding Agents: Predictable Results Through Strong Feedback Loops"](https://engineering.atspotify.com/2025/12/feedback-loops-background-coding-agents-part-3)).

## Related

- [Trust Without Verify](../patterns/anti-patterns/trust-without-verify.md)
- [Agent-Generated Verification Reports: A Structured Round-Trip for Human Review](agent-generated-verification-report.md) — the human-verified counterpart, for changes no machine check covers
- [Incremental Verification](incremental-verification.md)
- [Deterministic Guardrails](deterministic-guardrails.md)
- [Behavioral Testing for Agents](behavioral-testing-agents.md)
- [Data Fidelity Guardrails](data-fidelity-guardrails.md)
- [Pre-Completion Checklists](pre-completion-checklists.md)
- [Grade Agent Outcomes](grade-agent-outcomes.md)
- [Evidence-Chain Run Logs](evidence-chain-run-logs.md) — records whether the reported symptom moved, not only whether the checks ran
- [Claim-to-Evidence Trace Graphs for Auditing Agent Runs](claim-to-evidence-trace-graphs.md) — typed edges linking a claim to the artifacts and checks behind it, rather than a flat table of check results
