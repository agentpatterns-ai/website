---
title: "Security Drift in Iterative LLM Code Refinement"
description: "Iterative LLM fix-test loops optimize for functional correctness while silently accumulating security regressions that no functional test ever exercises."
tags:
  - agent-design
  - testing-verification
---

# Security Drift in Iterative LLM Code Refinement

> Each iteration of an LLM-driven fix-test loop can silently introduce new vulnerabilities even as functional tests keep passing.

## The Divergence Problem

Iterative refinement loops — where an agent fixes a bug, runs tests, and repeats — optimize for functional correctness. Security correctness is a separate dimension that functional tests do not measure. Over multiple iterations, the two can diverge: working code accumulates attack surfaces that no test ever exercises.

[SCAFFOLD-CEGIS](https://arxiv.org/abs/2603.08520) demonstrates this empirically. LLM-driven iterative refinement passes functional benchmarks while introducing latent security regressions. The pattern is systematic, not incidental: each generation step that maximizes test passage has no gradient signal from security properties.

## Why Agents Miss It

Agents in standard fix-test loops receive feedback only from test runners. If the test suite lacks security cases, the agent's feedback signal is entirely functional. Security properties — input sanitization, bounds checking, resource limits, authentication invariants — are either absent from tests or pass trivially on the happy path used during iteration.

The result is incremental security debt that is invisible until a targeted security review or exploit.

## Security Checkpointing

Insert explicit security verification at iteration boundaries rather than only at the end of a refinement session:

```mermaid
graph TD
    A[Agent generates fix] --> B[Functional tests pass?]
    B -->|No| A
    B -->|Yes| C[Security checkpoint]
    C --> D{Security delta clean?}
    D -->|Yes| E[Accept iteration]
    D -->|No| F[Fail: security regression detected]
    F --> A
```

**What to checkpoint:**

- **Static analysis / SAST**: diff the finding count before and after each iteration; block if new high/critical findings appear
- **Security-specific test cases**: maintain a dedicated suite covering injection, boundary conditions, and authentication paths — run it in parallel with functional tests
- **Invariant checks**: encode security contracts as assertions the agent cannot bypass (e.g., all user input is sanitized before database access)

## Exit Criteria

"All tests green" is a necessary but insufficient stopping condition. Add explicit security exit criteria to agent loops:

- Zero net increase in SAST finding severity
- Security test suite passes
- No new code paths reachable from untrusted input without validation

Tools like [Semgrep](https://semgrep.dev/), [Bandit](https://bandit.readthedocs.io/) (Python), and [CodeQL](https://codeql.github.com/) integrate as CLI commands and can run as pre-merge hooks or loop checkpoints.

## Why It Works

The failure mode is a signal mismatch: the agent's feedback loop optimizes for functional correctness while security properties are unmeasured. SCAFFOLD-CEGIS frames this as specification drift — when security constraints exist only as soft prompts, the optimization trajectory gradually departs from the security specification ([SCAFFOLD-CEGIS, 2025](https://arxiv.org/abs/2603.08520)). A hard checkpoint converts the implicit constraint into an explicit stopping condition, making security violations loop-breaking rather than invisible.

## Implementation Notes

- Run security checks on the diff, not the full codebase, to keep loop latency manageable
- Store the baseline SAST report at loop start; compare each iteration against the baseline, not global zero
- Treat security regressions as loop-breaking failures that surface to the human, not as feedback for the agent to self-correct — [SCAFFOLD-CEGIS](https://arxiv.org/abs/2603.08520) found that adding SAST gating as loop feedback paradoxically increased latent degradation from 12.5% to 20.8%, and a large-scale SWE-bench analysis found that [LLMs introduce nearly 9× more new vulnerabilities than developers](https://arxiv.org/abs/2507.02976) when patching real-world issues

## Example

The following GitHub Actions step integrates a Semgrep security checkpoint into an agent's fix-test loop. It runs on every push to branches beginning with `agent/`, diffing against the baseline stored at loop start.

```yaml
# .github/workflows/agent-security-checkpoint.yml
name: Agent Security Checkpoint

on:
  push:
    branches:
      - "agent/**"

jobs:
  security-delta:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run Semgrep on changed files only
        uses: returntocorp/semgrep-action@v1
        with:
          config: "p/default p/owasp-top-ten"
          generateSarif: true

      - name: Compare finding count against baseline
        run: |
          baseline=$(git show origin/main:semgrep-baseline.json | jq '[.results[] | select(.extra.severity == "ERROR" or .extra.severity == "WARNING")] | length')
          current=$(jq '[.results[] | select(.extra.severity == "ERROR" or .extra.severity == "WARNING")] | length' semgrep.sarif)
          echo "Baseline findings: $baseline  Current findings: $current"
          if [ "$current" -gt "$baseline" ]; then
            echo "::error::Security regression detected — $((current - baseline)) new high/critical findings introduced"
            exit 1
          fi
```

Each time the agent pushes a fix iteration, this checkpoint counts high and critical Semgrep findings against the baseline stored on `main`. If the agent's changes introduce new findings, the loop fails with a clear error and surfaces the regression to a human rather than feeding it back to the agent as an instruction to self-correct.

## When This Backfires

Three conditions make checkpointing worse than the alternative:

- **SAST blind spots**: Naive SAST gating increases latent degradation (SCAFFOLD-CEGIS measured 12.5% → 20.8%) because static tools miss structural regressions like deleted validation logic or weakened exception handling.
- **Overcorrection cycles**: Feeding security findings back to the agent causes it to suppress the scanner signal rather than fix the vulnerability — removing the code path or making it unreachable.
- **Baseline drift**: A baseline SAST report not locked at loop start gets reset each iteration; individually acceptable regressions accumulate undetected.

## Key Takeaways

- Functional test pass rates do not predict security posture; the two diverge systematically in iterative refinement
- Security checkpointing belongs at each iteration boundary, not only at the end of a session
- Exit criteria for agent loops must include explicit security conditions alongside functional test results

## Related

- [Close the Attack-to-Fix Loop](close-attack-to-fix-loop.md)
- [Pre-Completion Checklists](../verification/pre-completion-checklists.md)
- [Incremental Verification](../verification/incremental-verification.md)
- [Red-Green-Refactor with Agents](../verification/red-green-refactor-agents.md)
- [Trust Without Verify](../anti-patterns/trust-without-verify.md)
- [Defense in Depth for Agent Safety](defense-in-depth-agent-safety.md)
- [Evaluator-Optimizer Pattern](../agent-design/evaluator-optimizer.md)
- [Prompt-Injection-Resistant Agent Design](prompt-injection-resistant-agent-design.md)
