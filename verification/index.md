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
- [Nonstandard Errors in AI Agents](nonstandard-errors-ai-agents.md) — Agents analyzing identical data diverge systematically by model family; treat single-run outputs as one point from an unsampled distribution

## Behavioral Testing

- [Behavioral Testing for Agents](behavioral-testing-agents.md) — Test decision quality and end-state for non-deterministic agent systems using capability matrices, three grading methods, and acceptable variance thresholds

## Regression Testing

- [Golden Query Pairs as Continuous Regression Tests for Agents](golden-query-pairs-regression.md) — Maintain curated question-answer pairs with known-good outputs and run them continuously using semantic grading to catch capability regressions

## Eval-Driven Development

- [Eval-Driven Development: Write Evals Before Building Agent Features](../workflows/eval-driven-development.md) — Define correctness criteria before implementation so every agent change is validated against a stable, reusable test suite

## Review Techniques

- [Five-Pass Blunder Hunt](five-pass-blunder-hunt.md) — Run the same critique prompt five times in sequence on a plan or spec; each pass normalises the issues it finds, forcing later passes deeper into structural and logical problems
- [Pre-Completion Checklists](pre-completion-checklists.md) — Block agent completion signals with a mandatory verification sequence

## Rubric Design

- [Anti-Reward-Hacking: Rubrics That Resist Gaming](anti-reward-hacking.md) — Design eval rubrics with orthogonal signals so no single metric is gameable by agents

## Tooling

- [Test Harness Design for LLM Context Windows](llm-context-test-harness.md) — Terse stdout, verbose log files, and grep-friendly error lines that keep agent context clean and actionable during evaluation runs
