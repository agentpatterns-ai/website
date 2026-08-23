---
title: "CodeSlop: Search-Trajectory Residue in Agent Patches"
term: "CodeSlop"
description: "Coding agents leave speculative edits and abandoned hypotheses from their own search in the final patch; minimize the trajectory to its behavior-preserving core."
tags:
  - anti-pattern
  - tool-agnostic
  - arxiv
aliases:
  - code slop
  - trajectory minimization
  - agent patch bloat
last_reviewed: 2026-07-21
maturity: emerging
---

# CodeSlop: Search-Trajectory Residue in Agent Patches

> CodeSlop is the removable code an agent's search leaves in the patch — speculative edits that survive because tests pass, not because they are needed.

CodeSlop is the gap between an agent's patch and the smallest behavior-preserving patch that produces the same repair — formally, `len(AP) − len(AP*)` ([Mathai et al., 2026](https://arxiv.org/abs/2607.18161)). It is not bad code. A slop line can be clean, well-named, and reviewed; it is still slop if removing it changes nothing the tests observe. The distinction matters because static quality checks never flag it.

## Where it comes from

Iterative repair is a search. Between test-feedback requests an agent makes edit sequences, and failed hypotheses leave speculative and diagnostic changes behind. Once a solution passes, the agent has no incentive to remove them, so every edit — essential and abandoned alike — persists in the diff. The paper's motivating case: a Linux-kernel fix touched 21 lines where only 3 were required, leaving 18 search artifacts ([Mathai et al., 2026](https://arxiv.org/abs/2607.18161)).

The residue concentrates in exploratory scaffolding, not core logic. On SWE-Bench-Verified, minimization removed 100% of scratch reproduction scripts and 100% of build and config changes, but only 20.4% of source edits ([Mathai et al., 2026](https://arxiv.org/abs/2607.18161v1)). Harmless in one patch, the drift compounds as agents own more of a codebase — independent benchmarking finds agent code 2.3x more verbose than human repositories and verbosity rising across 75.5% of long-horizon trajectories ([Orlanski et al., 2026](https://arxiv.org/abs/2603.24755)).

## Minimize the trajectory — but only against a trustworthy oracle

The fix is a distinct post-repair step: shrink the patch to its behavior-preserving core rather than shipping the first diff that passes tests. This holds only where the test suite is a trustworthy proxy for intended behavior, because minimization preserves behavior relative to the oracle, not in the abstract. Two conditions gate it.

First, do not minimize by line count or by asking the agent to clean up its own patch — prompting an agent to minimize its own work fails in 3.8% to 44.9% of cases, including patch inflation and bug reintroduction ([Mathai et al., 2026](https://arxiv.org/abs/2607.18161v1)). Use counterfactual removal validated against tests. Trajectory minimization (TRIM) walks the recorded edits coarse-to-fine — drop a whole edit sequence, then a file's edits, then individual edits, in reverse order, keeping each removal only if the patch still passes and shrinks.

Second, the oracle must cover the paths the removed code guards. Where it does, the step is nearly free: 17.9% to 32.9% slop reduction across four agent scaffolds with 99.1% oracle preservation on SWE-Bench and near-zero quality loss ([Mathai et al., 2026](https://arxiv.org/abs/2607.18161v1)).

## Why it works

Trajectory minimization works because the trajectory carries structure the flat diff has lost. Edits group into sequences, sequences touch files, files hold atomic edits. Removing whole groups first and refining only where a group cannot be dropped eliminates search residue with far fewer validations than reconstructing edit dependencies from unstructured hunks — TRIM matches Delta Debugging's reduction (32.9% versus 31.5%, p=0.50) with about 1.9x fewer test runs ([Mathai et al., 2026](https://arxiv.org/abs/2607.18161v1)). Each removal is gated on the tests still passing, so the test for "is this slop?" is empirical, not stylistic.

## When this backfires

Minimization is only as good as the oracle, so it backfires where the oracle is thin or the code is deliberately untested.

- Weak or shallow test suites — removing a change that guards an untested path passes tests yet ships a regression; empirically rare (3 of 330 on SWE-Bench) but real.
- Intentional non-functional code — defensive guards, audit and observability hooks, and forward-compatibility structure read as removable slop because no test exercises them. [Abstraction Bloat](abstraction-bloat.md) makes the same warning about stripping audit logging and auth under a "minimum code" rule.
- Expensive validation domains — each removal candidate needs a fresh test run, so where a single run is costly (kernel builds near 30 minutes) even the structured approach carries real cost, and naive delta-debugging is worse.
- Unfamiliar task shapes — the evidence covers kernel and repository repair; domains with different trajectory structure may minimize differently ([Mathai et al., 2026](https://arxiv.org/abs/2607.18161)).

Not every extra line is slop. The step earns its place only where "passes tests" is a trustworthy stand-in for "preserves intended behavior."

## Key Takeaways

- CodeSlop is removable functional redundancy — code the agent's own search left behind, distinct from static quality; clean code can still be slop.
- The cause is structural: iterative repair accumulates speculative and abandoned edits, and nothing rewards removing them once tests pass.
- Treat minimization as a separate post-repair step, but gate it on a strong oracle and use counterfactual test-validated removal, never line-count shrinking or agent self-cleanup.
- Slop concentrates in exploratory scaffolding — reproduction scripts and config — far more than in core source.

## Related

- [Abstraction Bloat](abstraction-bloat.md) — the sibling mechanism: over-engineering by training incentive rather than by search residue
- [Refactoring Runaway](refactoring-runaway.md) — agents bundling unrequested refactors into a fix, a related source of patch inflation
- [Shadow Tech Debt](shadow-tech-debt.md) — how per-PR drift compounds silently across a codebase
- [AI Slop as a Process Problem](../../workflows/slop-as-process-problem.md) — the pipeline-gate mitigation that catches slop at PR time
- [Law of Triviality in AI PRs](law-of-triviality-ai-prs.md) — why the large diffs slop produces get the least review scrutiny
