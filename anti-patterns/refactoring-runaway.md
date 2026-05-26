---
title: "Refactoring Runaway: Tangled Refactorings in Agent Patches"
description: "Coding agents bundle unrequested refactorings into bug-fix patches, breaking compilability without improving functional correctness; conditions and detection."
tags:
  - anti-pattern
  - testing-verification
  - workflows
  - tool-agnostic
aliases:
  - tangled refactoring
  - tangled agent patches
  - refactoring-aware refinement
last_reviewed: 2026-05-27
---

# Refactoring Runaway: Tangled Refactorings in Agent Patches

> Coding agents inherit human developers' habit of bundling unsolicited refactors into bug-fix patches; the tangled changes break compilability without improving functional correctness, and stripping or repairing them recovers about half the lost build success.

Tangled refactoring is a fix patch that also renames variables, extracts methods, or moves classes the user never asked for. The empirical signal from [Tian et al., *Refactoring Runaway* (arXiv:2605.22526)](https://arxiv.org/abs/2605.22526) — 3,691 valid patches across SWE-agent, OpenHands, and Agentless with 12 LLMs on Multi-SWE-bench — is that agents do this in 21.43% of patches, and these patches are significantly less likely to compile but no less likely to be functionally correct when they do.

## When This Applies

The finding is qualified, not universal. The detect-and-strip recommendation holds when all three conditions are present:

- **Statically-typed language with signature contracts.** The Multi-SWE-bench evaluation is Java-heavy; the dominant failure mode is method-level refactorings (Add Parameter, Extract Method) that change inherited signatures and silently break the `@Override` contract in subclasses the agent never opened ([arXiv:2605.22526](https://arxiv.org/abs/2605.22526)). Dynamic languages without static signature enforcement see less of this mechanism.
- **High-autonomy agent frameworks.** Tangling rates vary almost 2x by framework — SWE-agent tangles 25.85% of patches, OpenHands 14.68% — and the paper attributes the spread to "frameworks with greater autonomy and fewer constraints" exploring a broader refactoring space ([arXiv:2605.22526](https://arxiv.org/abs/2605.22526)). Constrained completion modes (inline suggestions, single-file edit) tangle far less.
- **No compilation gate in the agent's verification loop.** The whole problem surfaces as build failures the agent could catch itself. Teams that already run `mvn compile` / `tsc --noEmit` inside the agent loop catch this for free.

## Why It Works

LLMs are trained on open-source repositories where 36.72% of human bug-fix patches bundle unrelated refactorings — a baseline established by [Herzig & Zeller's foundational tangled-changes study](https://dl.acm.org/doi/pdf/10.5555/2487085.2487113) and reconfirmed in [arXiv:2605.22526](https://arxiv.org/abs/2605.22526). LLMs reproduce the statistical pattern of their training distribution, so agents inherit tangling behaviour even when the user prompt is narrowly scoped. Compilability breaks specifically because method-level refactorings modify signatures the agent treats as local but which subclasses depend on — a shadow-edit failure where the changed call site is correct but downstream callers in unopened files no longer compile ([arXiv:2605.22526](https://arxiv.org/abs/2605.22526)).

[Agentic Refactoring (arXiv:2511.04824)](https://arxiv.org/abs/2511.04824) corroborates the mechanism on a separate corpus of 15,451 refactoring instances across 12,256 AIDev pull requests: 53.9% of agent refactorings occur in tangled commits, and agents are biased toward low-level edits (35.8% vs 24.4% for humans), making variable renames and small extractions the dominant tangled types.

## Detection and Mitigation

The [RefUntangle approach in Tian et al.](https://arxiv.org/abs/2605.22526) operates in two stages:

1. **Assessment.** For each refactoring detected in the patch, assign one of KEEP / REMOVE / FIX based on necessity (does the bug fix require it?) and safety (does it break downstream callers?).
2. **Refinement.** Regenerate the patch with REMOVE refactorings stripped and FIX refactorings repaired.

Applied to the same 3,691 patches, the approach raises compilability from 19.34% to 38.33% and additionally resolves 2.79% of previously unresolved issues ([arXiv:2605.22526](https://arxiv.org/abs/2605.22526)).

The top tangled refactoring types in agent patches are Extract Variable (expression-level), Add Parameter (method-level), and Move Class — differing from the human top-1 (Extract Method), so detection rules cannot be ported directly from prior human-commit untangling work ([arXiv:2605.22526](https://arxiv.org/abs/2605.22526)).

## When This Backfires

- **Dynamically-typed codebases.** The compilability mechanism depends on static signature contracts. Python, Ruby, and JavaScript codebases lack the `@Override` failure mode that drives the regression result; stripping tangled refactorings forfeits genuine cleanup without commensurate build-stability gain.
- **Opportunistic refactoring is the only debt-paydown channel.** [Martin Fowler's *Opportunistic Refactoring*](https://martinfowler.com/bliki/OpportunisticRefactoring.html) argues that dedicated refactoring sprints get cut under deadline pressure, so the small improvements made while fixing a bug are where code quality actually gets preserved. A strict no-refactor-in-bugfix policy applied uniformly can accelerate [shadow tech debt](shadow-tech-debt.md).
- **Agents already tangle less than humans.** Agents tangle at 21.43% vs the 36.72% human baseline ([arXiv:2605.22526](https://arxiv.org/abs/2605.22526)). The refactoring-aware refinement step is overhead, so for teams whose constraint is human-author tangling, anti-tangling guidance applied uniformly addresses the smaller half of the problem.
- **CI catches it cheaply already.** A build error is loud and trivially detected. Teams running compilation in the agent's verification loop (or in pre-merge CI) get a stronger signal at lower cost than an LLM-based assessment of refactoring necessity.
- **No association with functional correctness.** The same regression analysis finds tangled refactorings have **no significant association with whether the fix works** ([arXiv:2605.22526](https://arxiv.org/abs/2605.22526)). Stripping refactorings is a compilability intervention, not a correctness intervention — frame the cost-benefit accordingly.

## Example

A SWE-agent run on a Java repository produces a patch that fixes a null-pointer bug in `OrderProcessor.processOrder()`. The agent's diff:

```diff
- public Result processOrder(Order o) {
+ public Result processOrder(Order o, ProcessingContext ctx) {
      if (o == null) return Result.failure("null order");
-     return doProcess(o);
+     return doProcess(o, ctx);
  }
```

The null check is the requested fix. The added `ProcessingContext` parameter is a tangled refactoring the agent introduced "to improve testability." The patch compiles at the call site the agent edited but breaks three subclasses in unopened files that override `processOrder(Order)` — the `@Override` contract no longer matches the new signature ([arXiv:2605.22526](https://arxiv.org/abs/2605.22526)).

A refactoring-aware refinement step inspects the patch, classifies the parameter addition as REMOVE (not required for the null-check fix), and regenerates a patch with only the null guard. Build passes; the original tests pass.

## Key Takeaways

- Tangled refactorings appear in 21.43% of agent patches (Multi-SWE-bench, 3 frameworks, 12 LLMs) and break compilability without affecting functional correctness ([arXiv:2605.22526](https://arxiv.org/abs/2605.22526)).
- The mechanism is signature-level: Add Parameter and Extract Method on inherited methods violate the `@Override` contract in subclasses the agent never opened.
- Stripping or repairing tangled refactorings raises compilability from 19.34% to 38.33% on the same patches; the intervention is narrow but high-leverage where it applies.
- The recommendation is qualified — statically-typed language, high-autonomy framework, no existing build gate. Dynamic languages and constrained-completion modes do not see the same problem.
- The cheapest mitigation is a build step inside the agent's verification loop; a refactoring classifier is only worth its cost where build feedback is too slow or too noisy.

## Related

- [PR Scope Creep as a Human Review Bottleneck](pr-scope-creep-review-bottleneck.md) — adjacent failure where human-driven scope growth happens on stalled PRs rather than inside the agent
- [Shadow Tech Debt](shadow-tech-debt.md) — what accumulates if you ban all opportunistic refactoring without an alternative debt-paydown channel
- [Premature Completion](premature-completion.md) — inverse failure mode (agent stops too early); refactoring runaway is doing too much
- [LLM Refactoring Adoption Patterns](../human/llm-refactoring-adoption-patterns.md) — how developers modify ChatGPT-suggested refactorings when refactoring *is* the request
- [Pattern Replication Risk](pattern-replication-risk.md) — adjacent training-distribution-inheritance pathology
