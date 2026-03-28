---
title: "Eval-Driven Development Training for AI Agent Teams"
description: "Training pathway covering eval-driven development from first principles to production hardening — write evals before building agent features."
tags:
  - training
  - testing-verification
  - evals
  - tool-agnostic
---

# Eval-Driven Development

> A practitioner pathway for teams adopting eval-driven development — the discipline of defining measurable success criteria before writing agent feature code.

Traditional testing assumes deterministic systems: same input, same output. Agents are non-deterministic. The same prompt, same task, same environment can produce different results across runs. This pathway teaches the evaluation discipline that replaces gut-feel quality assessment with reproducible, automated measurement.

The modules progress from foundational concepts through hands-on suite construction to production-grade hardening. Each builds on the previous — start at the beginning if eval-driven development is new to your team.

## Core Modules

| Module | Topic | Duration |
|--------|-------|----------|
| [What Evals Are and Why Agents Need Them](what-evals-are.md) | How evals differ from tests, the non-determinism problem, [pass@k vs pass^k](../../verification/pass-at-k-metrics.md), why traditional QA fails for agents | 30–45 min |
| [Writing Your First Eval Suite](writing-first-eval-suite.md) | Task design, success criteria, grader selection, running a baseline, the 20–50 task starting point | 30–45 min |
| [Grading Strategies](grading-strategies.md) | Code-based grading, LLM-as-judge, human review, calibration against human judgment, when to use each | 30–45 min |
| [The Eval-First Development Loop](eval-first-loop.md) | Eval-driven workflow, evals as executable specifications, converting existing manual checks, model upgrade testing | 30–45 min |
| [Hardening Evals for Production](hardening-evals.md) | Anti-reward hacking, [incident-to-eval synthesis](../../verification/incident-to-eval-synthesis.md), golden query pairs, [layered accuracy defense](../../verification/layered-accuracy-defense.md), grader validation | 30–45 min |

## Supplementary

| Module | Topic | Duration |
|--------|-------|----------|
| [Step-by-Step: Building Your First Eval-Driven Feature](step-by-step-first-feature.md) | Hands-on walkthrough building a PR description generator — tasks, graders, baseline, iteration, and shipping | 60–90 min |

## Prerequisites

This pathway is self-contained but benefits from familiarity with:

- [Foundational Disciplines](../foundations/index.md) — especially the harness engineering module
- [Eval Engineering](../foundations/eval-engineering.md) — the complementary module that this pathway expands into a full course
- [Eval-Driven Development](../../workflows/eval-driven-development.md) — the reference page covering the core workflow pattern
