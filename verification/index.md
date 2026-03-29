---
title: "Verification: Testing, Evals, and Guardrails for Agents"
description: "How to measure agent output quality, design evaluation suites, apply guardrails, and use evals to drive agent development and catch regressions."
tags:
  - testing-verification
---

# Verification

> How to measure agent output quality, design evaluation suites, and use evals to drive development.

## Measuring Quality

- [Grade Agent Outcomes, Not Execution Paths](grade-agent-outcomes.md) — Evaluate agents by the final state they produce, not the sequence of steps they took to get there
- [Use pass@k and pass^k to Separate Agent Capability from Consistency](pass-at-k-metrics.md) — pass@k measures capability ceiling; pass^k measures consistency — report both to distinguish agents that sometimes succeed from those that reliably do
- [Trajectory Decomposition: Diagnose Where Coding Agents Fail](trajectory-decomposition-diagnosis.md) — Decompose agent trajectories into search, read, and edit stages with per-stage precision and recall to pinpoint where and why an agent went wrong
- [Nonstandard Errors in AI Agents](nonstandard-errors-ai-agents.md) — Agents analyzing identical data diverge systematically by model family; treat single-run outputs as one point from an unsampled distribution
- [Benchmark-Driven Tool Selection for Code Generation](benchmark-driven-tool-selection.md) — Use realistic, telemetry-derived benchmarks to evaluate AI coding tools — synthetic puzzles hide language-specific and task-specific weaknesses
- [Completion Failure Taxonomy](completion-failure-taxonomy.md) — Two-thirds of code completion failures are model errors, but one quarter are integration failures — fix both to improve acceptance rates

## Behavioral Testing

- [Behavioral Testing for Agents](behavioral-testing-agents.md) — Test decision quality and end-state for non-deterministic agent systems using capability matrices, three grading methods, and acceptable variance thresholds

## Regression Testing

- [Golden Query Pairs as Continuous Regression Tests for Agents](golden-query-pairs-regression.md) — Maintain curated question-answer pairs with known-good outputs and run them continuously using semantic grading to catch capability regressions
- [Pre-Change Impact Analysis](pre-change-impact-analysis.md) — Build a code-to-test dependency map and deliver it as a lightweight agent skill so agents verify at-risk tests before committing, cutting regressions by 70%

## Eval-Driven Development

- [Eval-Driven Development: Write Evals Before Building Agent Features](../workflows/eval-driven-development.md) — Define correctness criteria before implementation so every agent change is validated against a stable, reusable test suite

## Review Techniques

- [Five-Pass Blunder Hunt](five-pass-blunder-hunt.md) — Run the same critique prompt five times in sequence on a plan or spec; each pass normalises the issues it finds, forcing later passes deeper into structural and logical problems
- [Pre-Completion Checklists](pre-completion-checklists.md) — Block agent completion signals with a mandatory verification sequence

## Rubric Design

- [Anti-Reward-Hacking: Rubrics That Resist Gaming](anti-reward-hacking.md) — Design eval rubrics with orthogonal signals so no single metric is gameable by agents

## Guardrails

- [Deterministic Guardrails Around Probabilistic Agents](deterministic-guardrails.md) — Wrap agent output in hard, deterministic checks — linting, schema validation, CI gates — that enforce correctness regardless of what the agent produces
- [Dependency Gap Validation for AI-Generated Code](dependency-gap-validation.md) — AI coding agents declare a fraction of the dependencies their code actually needs at runtime — validate in clean environments before trusting the manifest

## Tooling

- [Test Harness Design for LLM Context Windows](llm-context-test-harness.md) — Terse stdout, verbose log files, and grep-friendly error lines that keep agent context clean and actionable during evaluation runs
