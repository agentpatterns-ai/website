---
title: "Claim-Scoped Invalidation for Agent Memory"
term: "Claim-Scoped Invalidation"
description: "Ask whether one stored claim still holds after a commit instead of whether the commit preserved behavior; on identical diffs the question moves precision further than extra evidence or a bigger model does."
aliases:
  - claim-relative invalidation
  - claim-level staleness check
  - impact versus invalidation
tags:
  - context-engineering
  - memory
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-23
maturity: emerging
---

# Claim-Scoped Invalidation for Agent Memory

> Claim-scoped invalidation asks whether one stored claim still holds after a change, rather than whether the change preserved behavior.

Claim-scoped invalidation is how a memory system phrases its staleness question when a commit lands. Instead of classifying the commit once and applying that verdict everywhere it reached, it shows a model one stored claim beside the diff and asks whether that claim holds. [Anand (2026)](https://arxiv.org/abs/2609.25130v1) measures the swap on an execution-grounded benchmark.

## When it applies

Your store has to hold claims a diff could settle. Anand scores test functions and concedes the benchmark "covers the checkable subset of claims" ([Anand 2026](https://arxiv.org/abs/2609.25130v1)). Rewriting each claim as prose costs precision, 0.794 to 0.711 ([Anand 2026](https://arxiv.org/abs/2609.25130v1)); a note no diff can settle does not belong in the gate's input.

Re-running the checks has to be the expensive option. Execution settles staleness exactly, and this gate exists only because verifying a store costs a test run per claim per commit ([Anand 2026](https://arxiv.org/abs/2609.25130v1)). Fifty claims on a quiet repository? Just re-run.

And you have to budget against your own base rate. Reweighted to the observed 1.78% natural flip rate, the claim-scoped arm holds 0.174 precision against a 0.018 base ([Anand 2026](https://arxiv.org/abs/2609.25130v1)) — a tenfold lift that still misfires on most of what it flags.

## Why it works

The two questions have different subjects, so neither answer converts into the other. Whether a diff preserves behavior is a property of the diff, and a commit changing behavior somewhere "invalidates nothing in particular" ([Anand 2026](https://arxiv.org/abs/2609.25130v1)). A rename runs the other way: it preserves behavior "while making every claim that names the old symbol false" ([Anand 2026](https://arxiv.org/abs/2609.25130v1)).

Anand isolates this with a control that holds the evidence fixed. Give the behavior-preservation judge the claim text too and precision moves 0.010 and 0.016 on both models tested; change the question on that same evidence and it moves 0.49 and 0.65 ([Anand 2026](https://arxiv.org/abs/2609.25130v1)). The judge reads the claim and answers what it was asked.

Dependency data does not close it either. `pytest-testmon` records by coverage which tests execute the changed lines, and catches 131 of 151 held-out flips at 0.415 precision ([Anand 2026](https://arxiv.org/abs/2609.25130v1)). His reading: "near-complete knowledge of what a change can reach does not identify what it falsifies" ([Anand 2026](https://arxiv.org/abs/2609.25130v1)), because most tests a change can reach do not flip.

## What the numbers show

The held-out split is 604 claims and 151 flips across 17 repositories at a stratified 25% flip rate, from 10,369 claims and 184 execution-verified flips ([Anand 2026](https://arxiv.org/abs/2609.25130v1)).

| Arm | Precision | Recall | Store re-verified | Flips served stale |
|---|---|---|---|---|
| Symbol anchoring | 0.39 | 0.54 | 35% | 46% |
| `pytest-testmon` | 0.41 | 0.87 | 52% | 13% |
| Diff-scoped model | 0.29 | 0.69 | 59% | 31% |
| Claim-scoped model | 0.79 | 0.72 | 22% | 28% |

Source: [Anand (2026)](https://arxiv.org/abs/2609.25130v1), Tables II and VI.

Scale does not rescue it. Across five models over roughly a 40x price range the diff-scoped arm holds 0.291 to 0.329 precision; the claim-scoped arm spans 0.705 to 0.974 on the same diffs ([Anand 2026](https://arxiv.org/abs/2609.25130v1)). At the diff-scoped question the frontier model is worst of the five, firing on 72% of claims; the cheapest reaches 0.794 on the claim one at $0.025/M ([Anand 2026](https://arxiv.org/abs/2609.25130v1)).

Dropping each repository in turn still leaves a 34.4-point worst-case precision gap over symbol anchoring, and pairing claims with unrelated diffs drops the arm from 15% firing to 0% ([Anand 2026](https://arxiv.org/abs/2609.25130v1)).

## When this backfires

- A missed flip costs more than a wasted check. The claim-scoped arm serves 28% of flips stale against testmon's 13% ([Anand 2026](https://arxiv.org/abs/2609.25130v1)). Buy the coverage database.
- Your store is large. One model call per stored claim per commit is the per-store cost memory systems exist to avoid, at a cheaper constant. No arm ran inside a real system, so the budget figures come from confusion matrices, not a deployment ([Anand 2026](https://arxiv.org/abs/2609.25130v1)).
- You take this as evidence that models cannot judge diffs. They can. On 183 Java commits, 88 preserving and 95 changing, diff-scoped baselines "achieve lower precision, ranging between 81.11 and 84.47" ([Ayub et al. 2026](https://arxiv.org/abs/2607.13111v1)). The predicate is answerable; it answers about the commit.
- The measured setting is narrow: "Twenty-three Python libraries, none of them large, and no other language." ([Anand 2026](https://arxiv.org/abs/2609.25130v1))
- Provenance. A single-author v1 preprint posted on 20 September 2026 ([Anand 2026](https://arxiv.org/abs/2609.25130v1)). Direction sound, magnitudes a hypothesis for your own history.

## Example

The benchmark construction carries a finding worth more than the arms do. The obvious way to mine flips is to look for tests that pass at one commit, go untouched by the next, and fail there. That search returned 1,005 claims and zero flips ([Anand 2026](https://arxiv.org/abs/2609.25130v1)), because a commit that leaves a pre-existing test failing does not pass CI, so "it does not reach mainline" ([Anand 2026](https://arxiv.org/abs/2609.25130v1)).

If you plan to validate a staleness gate against your own history, this is the trap you hit first. On any CI-gated mainline the positive class you are looking for was filtered out before you went looking.

## Key Takeaways

- Try the cheapest model on the claim-scoped question before you try a better model on the diff-scoped one. The price ladder is the wrong axis here.
- Write stored claims so a diff can settle them. That constraint belongs in the extractor, not in the gate that reads its output.
- Quote your operators the natural-rate precision. The stratified benchmark says 0.79; a deployment gets 0.174 ([Anand 2026](https://arxiv.org/abs/2609.25130v1)).
- Pick the arm from your cost asymmetry, not from the headline. Cheap re-verification and expensive staleness point at coverage-based selection instead.
- Before benchmarking any staleness gate on your own repository, check that CI has not already emptied the positive class.

## Related

- [Self-Correcting Memory: Evidence-Backed Claim Repair](../patterns/agent-design/self-correcting-memory-evidence-backed-claims.md) — the content-anchoring approach this paper measures as its structural baseline, the symbol-anchoring row above; it decides staleness with no model call.
- [Fact Supersession Memory for Code Assistants](fact-supersession-memory.md) — the other half of memory currency: what to do when a contradicting fact arrives, rather than when a commit lands.
- [Execution-State Ledger for Long-Horizon Coding Agents](../patterns/agent-design/execution-state-ledger-coding-agents.md) — tracks whether an observation still describes the repository, one level below whether a claim about it is still true.
- [Budgeted Verification of Inherited Agent Constraints](budgeted-constraint-verification.md) — the allocation question this gate feeds: once you know which claims are suspect, which ones get the verification budget.
- [Usage-Reinforced Memory Decay for Long-Running Agents](usage-reinforced-memory-decay.md) — decides what a store keeps at all, where this decides what it still believes.
