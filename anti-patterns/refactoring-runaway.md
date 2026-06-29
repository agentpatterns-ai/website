---
title: "Refactoring Runaway: Tangled Refactorings in Agent Patches"
term: "Refactoring Runaway"
description: "Coding agents bundle unrequested refactorings into bug-fix patches, breaking compilability without improving functional correctness; conditions and detection."
tags:
  - anti-pattern
  - testing-verification
  - workflows
  - tool-agnostic
  - arxiv
aliases:
  - tangled refactoring
  - tangled agent patches
  - refactoring-aware refinement
last_reviewed: 2026-06-02
maturity: emerging
---

# Refactoring Runaway: Tangled Refactorings in Agent Patches

> Coding agents bundle unsolicited refactors into bug-fix patches; the tangled changes break compilability without improving correctness, and stripping them recovers lost build success.

Tangled refactoring is a fix patch that also renames variables, extracts methods, or moves classes the user never asked for. [Tian et al., *Refactoring Runaway* (arXiv:2605.22526)](https://arxiv.org/abs/2605.22526) — 3,691 patches across SWE-agent, OpenHands, and Agentless with 12 LLMs on Multi-SWE-bench — finds agents do this in 21.43% of patches. These patches are far less likely to compile but no less likely to be functionally correct.

## When this applies

Detect-and-strip holds only when all three conditions are present ([arXiv:2605.22526](https://arxiv.org/abs/2605.22526)):

- Statically-typed language with signature contracts: the dominant failure mode is method-level refactorings (Add Parameter, Extract Method) that change inherited signatures and break the `@Override` contract in subclasses the agent never opened. Dynamic languages see less of this.
- High-autonomy agent frameworks: tangling varies almost 2x — SWE-agent 25.85%, OpenHands 14.68% — which the paper attributes to "frameworks with greater autonomy and fewer constraints." Constrained completion modes (inline suggestions, single-file edit) tangle far less.
- No compilation gate in the agent's loop: teams already running `mvn compile` / `tsc --noEmit` inside the loop catch the resulting build failures for free.

## Why it works

LLMs train on repositories where 36.72% of human bug-fix patches bundle unrelated refactorings — a baseline from [Herzig & Zeller](https://dl.acm.org/doi/pdf/10.5555/2487085.2487113), reconfirmed in [arXiv:2605.22526](https://arxiv.org/abs/2605.22526) — and reproduce that distribution even under narrow prompts. Compilability breaks because method-level refactorings modify signatures the agent treats as local but subclasses depend on: the changed call site is correct, but downstream callers in unopened files no longer compile.

[Agentic Refactoring (arXiv:2511.04824)](https://arxiv.org/abs/2511.04824) corroborates this on 15,451 instances across 12,256 AIDev pull requests: 53.9% of agent refactorings occur in tangled commits, and agents skew toward low-level edits (35.8% vs 24.4% for humans), making variable renames and small extractions the dominant tangled types.

## Detection and mitigation

The [RefUntangle approach](https://arxiv.org/abs/2605.22526) runs two stages. Assessment labels each refactoring KEEP / REMOVE / FIX by necessity and caller-safety. Refinement regenerates the patch with REMOVE refactorings stripped and FIX ones repaired. On the same 3,691 patches this raises compilability from 19.34% to 38.33% and resolves an additional 2.79% of issues. The top agent-tangled types — Extract Variable, Add Parameter, Move Class — differ from the human top-1 (Extract Method), so human-commit untangling rules cannot be ported directly.

## When this backfires

- Dynamically-typed codebases: Python, Ruby, and JavaScript lack the `@Override` failure mode, so stripping refactorings forfeits genuine cleanup with no build-stability gain.
- Opportunistic refactoring is the only debt-paydown channel: [Fowler](https://martinfowler.com/bliki/OpportunisticRefactoring.html) notes dedicated refactoring sprints get cut under deadline pressure, so bug-fix-adjacent improvements are where quality is preserved. A uniform no-refactor-in-bugfix policy can accelerate [shadow tech debt](shadow-tech-debt.md).
- Agents already tangle less than humans (21.43% vs 36.72%, [arXiv:2605.22526](https://arxiv.org/abs/2605.22526)), so uniform anti-tangling guidance addresses the smaller half of the problem.
- CI catches it cheaply already: a build error is a stronger signal at lower cost than an LLM-based assessment of refactoring necessity.
- No association with functional correctness ([arXiv:2605.22526](https://arxiv.org/abs/2605.22526)): stripping refactorings is a compilability intervention, not a correctness one.

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
