---
title: "Structure-Aware Diff Labeling with Two-Stage LLM Pipelines"
description: "A two-stage LLM pipeline that labels diff hunks against a 12-type change taxonomy then refines whole-patch relationships — useful where polyglot coverage matters more than deterministic per-language analysis."
tags:
  - code-review
  - testing-verification
last_reviewed: 2026-05-27
---

# Structure-Aware Diff Labeling with Two-Stage LLM Pipelines

> A two-stage LLM pipeline labels diff hunks against a 12-type change taxonomy and refines cross-hunk relationships — viable as a supplement to static analysis when polyglot coverage and customizable labels outweigh determinism and cost.

Structure-aware diff labeling assigns a change type to each hunk in a patch, then resolves cross-hunk relationships such as which hunk declares a renamed symbol and which hunks consume it. A two-stage LLM pipeline does this without per-language static analysis tooling, trading determinism and cost for language coverage and label customization ([arxiv:2605.26100](https://arxiv.org/abs/2605.26100)).

The approach is qualified: the paper's own evaluation shows performance varies across label types and recommends a hybrid with static analysis for the categories that matter most.

## When This Applies

Use a two-stage LLM labeler when:

- The codebase spans multiple languages and per-language refactor detectors (RefactoringMiner for Java, ts-morph for TypeScript, libcst for Python) would require maintaining separate pipelines.
- The label taxonomy needs to evolve over time — few-shot prompting lets you add categories without retraining or rewriting AST rules ([arxiv:2605.26100](https://arxiv.org/abs/2605.26100)).
- The downstream consumer (reviewer prioritisation, PR routing, automated comment suppression) tolerates non-deterministic output and ~80% precision/recall rather than requiring 100% reproducible labels.

Skip it when a single-language project has mature static-analysis tooling, when CI demands deterministic outputs for audit purposes, or when per-PR token cost dominates the budget.

## The Two Stages

**Stage 1 — Labeler.** Per-hunk classification using few-shot prompting against a fixed label set. The paper uses 12 types: documentation, testing, output handling, retype, code move, style change, logging, rename, error handling, logic change, internal interface change, external interface change ([arxiv:2605.26100](https://arxiv.org/abs/2605.26100)). Each hunk gets a label set with 5 lines of local context. Three modes — per-hunk, per-file, per-patch — trade context length for token cost.

**Stage 2 — Refiner.** Whole-patch inference that captures cross-hunk relationships. A rename labelled in isolation does not record which hunk holds the declaration and which hold the consequences; the Refiner assigns a parent field (parent=0 for declaration, parent=N for usage) and extracts attributes like old/new names and types. It also corrects misclassifications visible only in whole-patch view ([arxiv:2605.26100](https://arxiv.org/abs/2605.26100)).

The single-shot Refiner pass is the load-bearing innovation. Without it, a hunk-only labeller can name change types but cannot link them into the structural patterns that drive review prioritisation — knowing four hunks are renames is less useful than knowing they all consume one declaration.

## Why It Works

Decomposing classification into per-hunk labelling plus a whole-patch refinement makes each LLM call work within its strengths: short-context few-shot inference for the labelling step and large-context relational reasoning for the refinement step. Few-shot prompting transfers across programming languages without per-language training, so one prompt handles Java and Python diffs with comparable accuracy in the paper's benchmark ([arxiv:2605.26100](https://arxiv.org/abs/2605.26100)). The Refiner's whole-patch view supplies the global context that per-hunk inference structurally cannot represent — declaration-to-usage parenting and move source-target pairing emerge from seeing the entire patch in one pass.

## When This Backfires

- **Mature single-language tooling exists.** RefactoringMiner-class static analyzers produce deterministic, reproducible labels for Java refactors at near-zero marginal cost. Trading that for non-deterministic LLM output is a net loss when language coverage isn't a requirement.
- **Cost-sensitive PR-level CI.** The paper's best-performing model (Gemini-3-Pro-Preview) consumed up to 7.5× more output tokens than the second-best model (Claude Sonnet 4.5) ([arxiv:2605.26100](https://arxiv.org/abs/2605.26100)). Running this on every PR at scale is expensive; cheaper models lose meaningful accuracy.
- **Under-represented label types matter most.** Performance varies substantially across label types in the paper's evaluation, with external interface, error handling, and log labels suffering more than rename or logic-change labels ([arxiv:2605.26100](https://arxiv.org/abs/2605.26100)). A workflow that prioritises one of those categories is precisely the case where a hybrid with static analysis is required.
- **Deterministic audit trails.** Compliance contexts that require reproducible classification cannot tolerate LLM non-determinism. Static analysis stays the only viable option.
- **Very large patches.** The Refiner runs whole-patch inference; long diffs blow out the context window and force chunking, which breaks the cross-hunk structural relationship signal the Refiner exists to capture.
- **Headline metrics hide category-level failures.** LLM-as-classifier prompts optimised for catching true positives misclassify more false positives, and chain-of-thought reasoning amplifies misjudgement on certain inputs ([arxiv:2601.18844](https://arxiv.org/abs/2601.18844), [arxiv:2508.12358](https://arxiv.org/abs/2508.12358)). The 84/81 paper result is one calibration point, not a Pareto frontier.

The paper's own recommendation: "a hybrid strategy can be adopted — using LLM-based labeling for most types while relying on static analysis for a small set of critical label types" ([arxiv:2605.26100](https://arxiv.org/abs/2605.26100)).

## Example

The paper's benchmark uses patches drawn from SWE-bench Multilingual and SWE-PolyBench supplemented with fabricated patches for label-type coverage — 95 hunks across 13 PRs, mostly Java with Python included to demonstrate language-agnostic behaviour ([arxiv:2605.26100](https://arxiv.org/abs/2605.26100)).

A representative pipeline shape, per the paper:

```text
Patch (Java + Python files, 12 hunks)
  -> Labeler (per-hunk, 5 lines local context, few-shot)
     hunk[1]: [Rename]
     hunk[2]: [Rename]      <- usage consequence
     hunk[3]: [Logic Change]
     ...
  -> Refiner (whole-patch, single inference)
     hunk[1]: Rename(parent=0, old="getUserId", new="getAccountId")
     hunk[2]: Rename(parent=1)
     hunk[3]: Logic Change
```

Best result on this benchmark: **84% recall, 81% precision** with Gemini-3-Pro-Preview; relative model rankings shift by label type, so the headline number is not the only signal to plan against ([arxiv:2605.26100](https://arxiv.org/abs/2605.26100)).

## Key Takeaways

- The two-stage Labeler-plus-Refiner shape is the structural idea; whole-patch refinement is what lets the pipeline emit relationships, not just types.
- Polyglot coverage and label customisability are the legitimate wins; determinism, cost, and per-category precision are the legitimate trade-offs.
- The paper itself recommends a hybrid with static analysis for label types where accuracy matters — treat LLM labelling as a supplement, not a replacement.
- Cost between models is non-uniform — Gemini-3's accuracy lead comes with ~7.5× the output tokens of Claude Sonnet 4.5.
- Under-represented label types (external interface, error handling, log) are where the approach is weakest; do not build a workflow that depends on those categories alone.

## Related

- [Diff-Based Review](diff-based-review.md) — Review effort scoped to the diff is the substrate this labelling enriches.
- [Agent-Driven PR Slicing](agent-driven-pr-slicing.md) — Slicing decisions can consume structure-aware labels to identify semantic boundaries rather than syntactic ones.
- [Signal Over Volume in AI Review](signal-over-volume-in-ai-review.md) — Per-hunk labels are a precondition for suppressing low-value comments on mechanical change categories.
- [Tunable Effort Levels for Code Review Agents](tunable-review-effort.md) — Labels can route hunks to different review depths instead of treating every change uniformly.
- [Learned Review Rules](learned-review-rules.md) — Both approaches reduce reviewer-side work; labelling structures the input, learned rules structure the output.
