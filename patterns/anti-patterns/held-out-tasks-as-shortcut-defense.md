---
title: "Held-Out Tasks as a Harness Shortcut Defense"
term: "Benchmark-Wide Harness Shortcut"
description: "Held-out tasks resample the questions and leave the benchmark protocol fixed, so an automatically tuned harness can bank a gain that lives in the protocol and survives every task swap."
tags:
  - anti-pattern
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - held-out task blind spot
  - protocol-level eval overfitting
  - counterfactual harness search
last_reviewed: 2026-09-19
maturity: emerging
---

# Held-Out Tasks as a Harness Shortcut Defense

> Held-out tasks change the questions and leave the protocol alone, so a shortcut living in the protocol survives the swap.

Swapping in fresh tasks moves one variable. A benchmark also carries a protocol: "file names, directory layout, metadata, tool aliases, demonstration order, feedback format" ([Zhu et al., 2026, §3.1](https://arxiv.org/abs/2609.18366v1)). Held-out evaluation resamples the tasks and holds that fixed, so "tasks change, but the protocol correlation does not" ([§1](https://arxiv.org/abs/2609.18366v1)).

## When the gap is real

Three conditions have to hold together. A team missing one of them can keep using held-out tasks.

- A search procedure, not a person, proposes harness edits from repeated benchmark feedback. That is the pressure that finds a benchmark-wide shortcut.
- The protocol carries one. "58.1% of questions in the benchmark OfficeQA Full mention numerical scales such as millions or billions", and in its 697-document corpus "the next nonblank line after 95.2% of unit statements begins a table" ([Zhu et al., 2026, §1](https://arxiv.org/abs/2609.18366v1)).
- Production does not share that protocol. Where the deployed agent sees the benchmark's layout and tool aliases, protocol-dependent gain is gain.

## What the held-out score misses

Vary the protocol as well, under checks that pin the question, answer, documents, access and scorer. Then measure how much of the tuned harness's gain over the starting harness disappears. In the first round of CHASE (Counterfactual Harness Search and Evolution), the Challenger re-encoded retrieved text as table context. On the evolution split that moved the evolved harness's gain over its starting point from 8.16% on the released benchmark to −5.10% on the counterfactual, with question, answer and documents untouched ([Zhu et al., 2026, §5.3](https://arxiv.org/abs/2609.18366v1)). The authors read the reversal as a gain that "depends on how retrieved evidence is represented", and a task swap leaves that representation unchanged.

The gain can also run the other way, which I did not expect. On the 208 Syn-Ledger certification tasks, all three optimized methods gained more over the starting harness under the shortcut-neutralized benchmark than under the released one: for CHASE, 23.08% against 5.29%. Absolute scores still fell, for CHASE from 87.18% to 38.30% ([Zhu et al., 2026, Table 2](https://arxiv.org/abs/2609.18366v1)).

## Why it works

A validity-preserving protocol change moves the one variable held-out tasks cannot, so it separates capability from protocol dependence. The paper names what the difference measures: Δ_BS is "the extra gain obtained by the 'bad genius' Proposer through increased reliance on the benchmark-wide shortcut rather than improved task-solving capability" ([Zhu et al., 2026, §3.1](https://arxiv.org/abs/2609.18366v1)). Seven invariants gate each transformation and every one must pass ([Table B.2](https://arxiv.org/abs/2609.18366v1)).

## When this backfires

- The tuning loop may not be worth defending. Compared against test-time scaling and discovery baselines "under comparable feedback and inference budgets", "automatic harness evolution does not consistently outperform simple test-time scaling methods and exhibits limited generalization" on Terminal-Bench 2.1 with GPT-5.4 and Claude Opus 4.6 ([Wang et al., 2026](https://arxiv.org/abs/2607.12227v2)).
- Search cost is the headline. Against HarnessCompass, the fixed-gate baseline, CHASE "runs 2.47 times as many attempts and uses 2.43 times as many total tokens" during search ([Zhu et al., 2026, §C.5](https://arxiv.org/abs/2609.18366v1)).
- A constraint can consume a whole round. After the first counterfactual entered the archive, every second-round candidate violated the ε=0.05 constraint despite released gains as high as 15.31%, so the method fell back to the original harness ([Zhu et al., 2026, §5.3](https://arxiv.org/abs/2609.18366v1)).
- A transformation that is not provably semantics-preserving moves the problem instead of solving it. Writing about LLM reasoning tests rather than agent harnesses, the LGMT authors say informal transformations "frequently introduce semantic drift". Developers then struggle to tell a genuine defect from "a follow-up test case that inadvertently altered the original underlying logic" ([Zhou et al., 2026, §1](https://arxiv.org/abs/2605.23965v3)).
- A clean archive reads stronger than it is. The authors scope their result to "the evaluated counterfactual family, whose coverage is limited by our three-round search budget" ([Zhu et al., 2026, §6](https://arxiv.org/abs/2609.18366v1)).

## Key Takeaways

- Held-out tasks resample the semantic task and leave the benchmark protocol fixed, so a protocol-level shortcut survives them.
- Measure how much of the tuned harness's gain disappears under a validity-preserving protocol change, not the score change, because the change moves the baseline harness too.
- One counterfactual turned a reported 8.16% gain into −5.10% with questions, answers and documents unchanged.
- The released gain can understate too: CHASE's 5.29% released gain was 23.08% once the shortcut was neutralized, even as its absolute score fell.
- Price it first. The counterfactual search ran 2.47 times the attempts of the fixed-gate baseline, on evidence of one real benchmark and one synthetic at a three-round budget.

## Related

- [Harness Hill-Climbing](../agent-design/harness-hill-climbing.md) — the eval-driven tuning loop this failure mode sits inside, whose held-out validation step is the defense in question
- [DSPy Programmatic Prompt Optimization](../agent-design/dspy-programmatic-prompt-optimization.md) — the automated optimizer that supplies the search pressure
- [Answer-Reachable Eval Environments](answer-reachable-eval-environments.md) — the other way a benchmark environment inflates a score, by leaving the fix reachable
- [Eval Blind Spots](../../verification/eval-blind-spots.md) — what a held-out task set does and does not cover
- [Reliability of an Automatically Selected Agent Harness](../agent-design/harness-selection-reliability.md) — run-to-run selection variance when a search picks the winning configuration
