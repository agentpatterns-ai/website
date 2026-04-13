---
title: "Happy Path Bias: How AI Agents Skip Error Handling"
description: "AI agents systematically neglect error handling, edge cases, and type boundaries — producing code that passes the happy path but breaks in production."
tags:
  - agent-design
  - testing-verification
---

# Happy Path Bias

> Agents produce code that works for the common case but breaks on edge cases, error paths, and type boundaries.

## The Pattern

AI coding agents systematically neglect error handling, edge cases, and type safety. [CodeRabbit's analysis of 470 GitHub PRs](https://www.coderabbit.ai/blog/state-of-ai-vs-human-code-generation-report) found AI-generated code has **2x more error handling issues** and **1.75x more logic/correctness errors** than human-written code.

| Symptom | What the agent does | What breaks |
|---------|--------------------|----|
| Bare exception handling | `except:` or `catch (e) {}` | Swallows real errors silently |
| Type escape hatches | Reaches for `any` (TS) or empty-string defaults | Voids downstream type safety |
| Over-specification | Generates hyper-specific solutions | Fails on variations |

## Why It Happens

The agent's objective is task completion: the code compiles, the tests pass, and the requested feature exists. Error handling, validation, and edge-case coverage are implicit requirements that rarely appear in the task description. A catch-all handler or type escape hatch satisfies the surface-level goal — the code compiles, the task appears done — while deferring failures to production.

## Detection

Linters catch the most common forms before code leaves the editor.

| Rule | Catches |
|------|---------|
| `E722` | Bare `except:` |
| `BLE001` | Blind exception catching (`except Exception`) |
| `TRY003` | Raising vanilla `Exception` instead of specific types |
| `TRY301` | Abstract `raise` in `except` block |
| `TRY400` | `logging.error()` instead of `logging.exception()` in handlers |

For TypeScript: `@typescript-eslint/no-explicit-any` and `no-unsafe-assignment`.

### Pre-commit gate

```yaml
# .pre-commit-config.yaml (excerpt)
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0
    hooks:
      - id: ruff
        args: [--select, "E722,BLE001,TRY003,TRY301,TRY400"]
```

## Mitigation

**In prompts:** "raise ValueError for invalid input, never use bare except" is actionable; "handle errors" is not. Naming anti-patterns by CWE or rule ID reduces vulnerability density by 59-64% ([Endor Labs](https://www.endorlabs.com/learn/anti-pattern-avoidance-a-simple-prompt-pattern-for-safer-ai-generated-code)).

**In CI:** Lint, type check, then test every agent-generated change — catches roughly 60% of AI code failures ([Augment Code](https://www.augmentcode.com/guides/debugging-ai-generated-code-8-failure-patterns-and-fixes)).

**In review:** Look for what the agent *omitted* — missing `finally` blocks, absent validation, no error paths in tests.

## When This Backfires

Adding exhaustive error handling is not always the right call. Conditions where the pattern overreaches:

- **Prototyping and throwaway scripts** — early-stage code that will never reach production can reasonably defer error paths; the cost of comprehensive handling outweighs the signal it provides at that stage.
- **Framework-managed boundaries** — when a runtime, web framework, or CLI harness already catches and logs unhandled exceptions at a top-level boundary, adding redundant try/catch inside every function creates noise without adding recovery logic.
- **Tight feedback loops with known input** — test harnesses, local dev scripts, and internal tooling operating on controlled, well-understood input rarely need the same defensive depth as user-facing production code.
- **Over-specified exception types** — catching `FileNotFoundError` and `PermissionError` separately is correct; catching 15 distinct OS-level exceptions per function creates noise that obscures intent and discourages reading error paths at all.
- **Linter false positives in exploratory code** — `BLE001` and `TRY003` fire on legitimate broad handlers in plugin systems or test harnesses where catching `Exception` is intentional. Blanket rule application without `# noqa` discipline generates suppression churn.
- **Prompt over-specification** — injecting long error-handling instructions into every prompt dilutes the task signal; agents may produce verbose try/except scaffolding that technically satisfies the prompt but obscures the logic under test.

The anti-pattern targets *production-bound* code. Apply enforcement at the CI boundary, not the prompt boundary, to separate signal from noise.

## Example

An agent asked to write a file parser:

=== "Agent output (typical)"

    ```python
    def parse_config(path: str) -> dict:
        with open(path) as f:
            return json.load(f)
    ```

=== "With error paths"

    ```python
    def parse_config(path: str) -> dict:
        try:
            with open(path) as f:
                return json.load(f)
        except FileNotFoundError:
            raise ConfigError(f"Config file not found: {path}")
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in {path}: {e}")
    ```

The first version works when the file exists and contains valid JSON. The second works in production.

## Sources

- [CodeRabbit: AI vs Human Code Generation](https://www.coderabbit.ai/blog/state-of-ai-vs-human-code-generation-report)
- [Augment Code: AI Code Failure Patterns](https://www.augmentcode.com/guides/debugging-ai-generated-code-8-failure-patterns-and-fixes)
- [Ox Security: AI Code Anti-Patterns](https://www.prnewswire.com/news-releases/ox-report-ai-generated-code-violates-engineering-best-practices-undermining-software-security-at-scale-302592642.html)
- [Endor Labs: Anti-Pattern Avoidance Prompts](https://www.endorlabs.com/learn/anti-pattern-avoidance-a-simple-prompt-pattern-for-safer-ai-generated-code)
- [Stack Overflow: Bugs and AI Coding Agents](https://stackoverflow.blog/2026/01/28/are-bugs-and-incidents-inevitable-with-ai-coding-agents/)

## Related

- [Trust Without Verify](trust-without-verify.md) — Accepting agent output as correct because it looks polished
- [Demo to Production Gap](demo-to-production-gap.md) — Code passes demos but fails on real-world edge cases
- [Copy-Paste Agent](copy-paste-agent.md) — Type-safety violations from cloning code without adapting types
- [Deterministic Guardrails](../verification/deterministic-guardrails.md) — Hard checks around agent output
- [Hooks vs Prompts](../verification/hooks-vs-prompts.md) — Lifecycle hooks enforce safety deterministically
- [TDD Agent Development](../verification/tdd-agent-development.md) — Tests first; agents implement against them
- [Pattern Replication Risk](pattern-replication-risk.md) — Agents reproduce codebase patterns at scale, including bad error handling
- [The Yes-Man Agent](yes-man-agent.md) — Executes requests without flagging missing error handling
- [The Effortless AI Fallacy](effortless-ai-fallacy.md) — Underestimating the effort needed to make AI-generated code production-ready
- [Shadow Tech Debt](shadow-tech-debt.md) — Hidden quality issues accumulating in AI-generated code
- [Exception Handling and Recovery Patterns](../agent-design/exception-handling-recovery-patterns.md) — Progressive failure hierarchy for agents that encounter errors at runtime
- [The Test Homogenization Trap](test-homogenization-trap.md) — AI-generated tests share the model's blind spots, missing the same edge cases the code misses
- [Agent Debugging: Diagnosing Bad Agent Output](../observability/agent-debugging.md) — systematic process for tracing why an agent produced wrong or incomplete output
- [Comprehension Debt](comprehension-debt.md) — Unreviewed agent output accumulates as code the team doesn't understand
- [Law of Triviality in AI PRs](law-of-triviality-ai-prs.md) — Reviews focus on style while error-handling gaps go unnoticed
