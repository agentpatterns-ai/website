---
title: "Test Harness Design for LLM Context Windows"
description: "Design test harnesses as LLM-first interfaces: terse stdout, verbose log files, and grep-friendly error lines that keep agent context clean and actionable."
tags:
  - context-engineering
  - testing-verification
  - evals
---

# Test Harness Design for LLM Context Windows

> Design test harnesses as LLM-first interfaces: terse stdout, verbose log files, and grep-friendly error lines that keep agent context clean and actionable.

## The Context Window Is the Interface

Every byte a test suite emits enters the agent's context window. A harness tuned for human readability — stack traces, progress bars, timing breakdowns — becomes noise that consumes tokens, obscures root causes, and degrades reasoning.

Anthropic's [C compiler project](https://www.anthropic.com/engineering/building-c-compiler) found the harness must be designed for the AI, not the human operator. Cursor confirmed this: [removing mid-turn communication language](https://cursor.com/blog/codex-model-harness) improved final code output.

## Principles

### Terse Stdout, Verbose Log Files

Default stdout to summary-level output. Write verbose output — stack traces, per-test results, timing data — to log files. The agent reads the summary; if it needs detail, it greps the log.

The agent cannot choose to ignore parts of stdout — everything printed enters context. Log files give selective access without forcing consumption.

### Place ERROR and Its Reason on the Same Line

On failure, emit the keyword and cause on one line:

```
ERROR: test_auth_flow — expected 200, got 401
```

Not:

```
test_auth_flow
  Status: FAILED
  Expected: 200
  Actual: 401
```

Agents grep for `ERROR` to locate failures. If the cause sits on a separate line, a single grep misses it and the agent spends an extra tool call. One line, one grep, actionable result.

### Provide Pre-Computed Summary Statistics

Agents are time-blind and cannot infer duration from timestamps or pass rates from a list of results. A harness that prints:

```
Tests: 142 passed, 3 failed, 0 skipped — 8.2s
```

beats 145 individual result lines — the signal arrives without consuming 145 lines of context.

### Throttle Incremental Progress Output

Progress indicators that print per test file, compilation unit, or API call flood context with liveness signals rather than information. Print progress only at milestones or on failure — the agent does not need to know that test 37 of 142 is running.

### Emit Machine-Readable Summaries for Structured Access

For agent loops that parse results programmatically, emit a JSON summary alongside the human output:

```json
{"total": 142, "passed": 139, "failed": 3, "failures": ["test_auth_flow", "test_token_refresh", "test_logout"]}
```

The summary stays out of stdout and consumes context only when the agent requests it. Anthropic's [long-running agent harness](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) uses JSON rather than Markdown for feature/test tracking because models are less likely to inappropriately modify JSON.

### Provide a Fast Sampling Mode

For large suites, implement a `--fast` flag that runs a 1-10% random sample, deterministic per invocation but varied across parallel instances. Reserve the full suite for final verification.

### Preserve Errors in Context

A counterintuitive finding from [Manus](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus): leaving failed actions and error messages in context helps models avoid repeating mistakes. Be terse about success but preserve failure output — error traces are the signal agents use to course-correct.

## Caveat: Terseness vs. Ambition

Cursor [found](https://cursor.com/blog/codex-model-harness) that when system prompts emphasized token efficiency, models became reluctant to tackle ambitious tasks. Make the harness output terse by engineering — log files, summaries, structured output — rather than by instructing the model to be brief.

## Anti-Pattern: The Human-Optimized Harness

A human-optimized harness typically includes per-test progress lines (`✓ test_login 42ms`), full stack traces on failure, ASCII progress bars, and timing histograms. Each is context overhead when the agent runs the suite: a 500-test run emits 500 `✓` lines before the failure summary, burying the signal 500 lines deep.

## When This Backfires

An LLM-first harness is the wrong default when:

- **Humans are the primary consumers.** In shared CI, engineers triage failures from the full log; stripping stdout forces them to open a secondary file per failure.
- **The agent will load the full log anyway.** Intermittent failures need surrounding output; one extra tool call per failure beats verbose stdout only at scale.
- **Tests carry diagnostic data in the body.** Property-based suites and snapshot diffs print the offending input; a one-line reason drops the payload needed to diagnose.
- **The suite is small.** Under a few dozen tests, per-test progress is cheap to scan and a custom reporter is not worth the effort.

Reserve the LLM-first harness for suites the agent runs unattended at scale.

## Implementation Checklist

| Property | Good | Bad |
|----------|------|-----|
| Stdout default | Summary line per suite | Line per test |
| Failure format | `ERROR: test_name — reason` (one line) | Reason on separate line |
| Verbose output | Written to log file | Emitted to stdout |
| Summary statistics | Pre-computed and printed | Left for agent to infer |
| Progress output | At milestones or on failure | Per test / per file |

## Example

A pytest `conftest.py` that applies these principles using a custom plugin:

```python
# conftest.py
import json
import pathlib
import pytest

LOG_FILE = pathlib.Path("test-verbose.log")

class AgentFriendlyReporter:
    """Pytest plugin: terse stdout, verbose log file, one-line errors."""

    def __init__(self):
        self.results = {"passed": 0, "failed": 0, "skipped": 0, "failures": []}
        self._log = LOG_FILE.open("w")

    def pytest_runtest_logreport(self, report):
        if report.when != "call":
            return
        if report.passed:
            self.results["passed"] += 1
        elif report.failed:
            self.results["failed"] += 1
            reason = report.longreprtext.splitlines()[-1] if report.longreprtext else "unknown"
            self.results["failures"].append(report.nodeid)
            # One-line error to stdout — grep-friendly
            print(f"ERROR: {report.nodeid} — {reason}")
            # Full trace to log file only
            self._log.write(f"=== {report.nodeid} ===\n{report.longreprtext}\n\n")
        elif report.skipped:
            self.results["skipped"] += 1

    def pytest_sessionfinish(self, session, exitstatus):
        total = self.results["passed"] + self.results["failed"] + self.results["skipped"]
        duration = session.duration if hasattr(session, "duration") else 0
        # Pre-computed summary line
        print(
            f"Tests: {self.results['passed']} passed, {self.results['failed']} failed, "
            f"{self.results['skipped']} skipped — {duration:.1f}s"
        )
        # Machine-readable JSON summary
        pathlib.Path("test-results.json").write_text(json.dumps(self.results))
        self._log.close()

def pytest_configure(config):
    config.pluginmanager.register(AgentFriendlyReporter(), "agent_reporter")
    # Suppress default per-test output
    config.option.verbose = -1
```

Running `pytest` with this plugin produces stdout an agent can consume in a single grep:

```
ERROR: tests/test_auth.py::test_token_refresh — assert 200 == 401
Tests: 141 passed, 1 failed, 0 skipped — 6.4s
```

The full stack trace lives in `test-verbose.log`, and `test-results.json` provides structured access.

## Key Takeaways

- Every byte of test output enters the agent's context window — treat stdout as a constrained resource.
- Write verbose output to log files; keep stdout to summaries and one-line errors.
- Place `ERROR` and its cause on a single line so a single grep returns actionable information.
- Pre-compute summary statistics; agents cannot infer duration or pass rates from raw output.
- Suppress per-test progress lines; print milestones or final results only.
- Provide a `--fast` sampling mode for rapid iteration; reserve full suites for final verification.
- Preserve error output in context — failures are the signal agents need to course-correct.
- Achieve terseness through engineering (log files, structured output), not by instructing the model to be brief.

## Related

- [Context Window Management: The Dumb Zone](../context-engineering/context-window-dumb-zone.md)
- [Token-Efficient Tool Design](../tool-engineering/token-efficient-tool-design.md)
- [Context Compression Strategies](../context-engineering/context-compression-strategies.md)
- [Agent Debugging](../observability/agent-debugging.md)
- [Test-Driven Agent Development](tdd-agent-development.md)
- [Incremental Verification](incremental-verification.md)
