---
title: "Behavior-Partitioned Security Tests as Executable Specs"
term: "Behavior-Partitioned Security Tests"
description: "Show a coding model executable security tests upfront, hold whole attack families back for evaluation, and spend budget on test diversity, not more rounds."
tags:
  - testing-verification
  - security
  - tool-agnostic
  - arxiv
aliases:
  - security tests as executable specifications
  - hidden security behavior families
  - SecTDD
last_reviewed: 2026-08-11
maturity: emerging
---

# Behavior-Partitioned Security Tests as Executable Specs

> Showing security tests upfront lifts joint success by 19.3 points and triples the rate at which a green visible suite hides a failure.

Behavior-partitioned security tests split a task's security cases by attack mechanism rather than by individual case, then show one set of families to the model as its specification and hold the rest back for evaluation. Hidden cases vary encoding, boundary values, and nesting while testing the same security property the visible cases state ([Liang et al., 2026](https://arxiv.org/abs/2608.09740v1)). Splitting cases at random would let input memorization pass for security reasoning.

## Where the lift holds

Across 2,705 generation trajectories on 31 Python tasks covering 16 CWE identifiers, showing all visible tests upfront raised hidden functional-and-security joint success by 19.3 percentage points on macro average ([Liang et al., 2026](https://arxiv.org/abs/2608.09740v1)). Three conditions bound that number:

- It held in 7 of 9 benchmark-model pairings. Two reversed: a 7B local model fell from 45.5% to 41.8% joint success as its secure rate dropped from 74.5% to 56.4%, and a hosted model fell from 89.1% to 81.8% ([Liang et al., 2026](https://arxiv.org/abs/2608.09740v1)).
- No Holm-adjusted comparison reached p < 0.05; the effective sample is 31 task instances, not 2,705 trajectories.
- The tasks are small self-contained Python components whose benchmark prompts may appear in pretraining; the authors decline to generalize to Java, C, C++, repo-scale agents, or concurrency.

Adopt this where you can enumerate a task's attack families and measure against a held-out set. Otherwise the visible suite is your oracle.

## The suite gets greener and less honest at once

The share of candidates that clear every visible test and still fail held-out security behavior tracks the regime that produced them ([Liang et al., 2026](https://arxiv.org/abs/2608.09740v1)):

| Regime | Visible-joint passes | Failed hidden | Rate |
|---|---|---|---|
| Requirement only | 213 | 12 | 5.6% |
| Visible tests shown upfront | 389 | 73 | 18.8% |
| Raw failure logs fed back | 360 | 49 | 13.6% |
| Structured failures fed back | 360 | 50 | 13.9% |

Showing tests upfront nearly doubles the passing candidates and more than triples the share of them that are wrong about security.

## Spend the next hour writing new cases

On one benchmark, 55 cells triggered zero revisions because every visible test already passed, and five failed hidden evaluation anyway ([Liang et al., 2026](https://arxiv.org/abs/2608.09740v1)). Feedback cannot repair a property that produces no visible failure, so the authors conclude that "extra iterations are inert" once visible tests pass and hidden attacks fail, and that the engineering answer is "stronger and more diverse tests, not merely more rounds".

How a failure is presented barely matters. Across 465 paired repair cells, structured security-priority feedback and raw execution logs tied in 453; structured produced 80 repairs with zero joint regressions, raw produced 83 with three ([Liang et al., 2026](https://arxiv.org/abs/2608.09740v1)). Any executable failure does the work, so put the effort into generating cases: mutation testing, metamorphic variants, boundary generation, and independent fuzzing.

## Why it works

An executable test converts an implicit security requirement into a concrete acceptance condition the model conditions on while generating, which is why it outperforms a natural-language cue. Across five models and four languages, prompting methods shifted which CWE categories appeared without significantly reducing vulnerability frequency or density ([Kharma et al., 2026](https://arxiv.org/abs/2605.24298v1)). The coverage limit is that mechanism in reverse: revision is driven by observed failures, so a behavior family absent from the visible partition emits no edit signal and no number of rounds reaches it.

## Example

The source illustrates the split on a URL-validation task ([Liang et al., 2026](https://arxiv.org/abs/2608.09740v1)):

| Partition | Cases | Role |
|---|---|---|
| Visible | Basic parsing of well-formed URLs | Shown to the model as the specification |
| Hidden | Deep subdomains, authority fields, encoded delimiters | Withheld; run once after generation stops |

Every hidden case attacks the property the visible cases state. What moves is the encoding, the boundary value, and the nesting depth. A random split of individual cases preserves none of that, because it leaves fragments of each family on both sides.

## When this backfires

- You cannot name the attack families. Partitioning assumes you already know the mechanisms, so on a novel surface there is nothing to hold out.
- Small local models can trade security for visible-test satisfaction, as the 7B reversal shows ([Liang et al., 2026](https://arxiv.org/abs/2608.09740v1)).
- Your team treats a passing suite as a release signal. The 18.8% row is what that signal is worth here.
- The work is functional rather than security-sensitive. Repair rounds lift functional pass rates across every model scale tested, by +4.9 to +17.1 pp on HumanEval and +16.0 to +30.0 pp on MBPP Sanitized ([Arimbur, 2026](https://arxiv.org/abs/2604.10508v1)), so extra rounds are not inert on that axis.
- A competing study argues iterative reprompting is "strictly required" for defense-in-depth authentication code ([Singh et al., 2026](https://arxiv.org/abs/2607.23710v1)), but discloses no held-out partition, so its loop may be measuring the oracle it optimizes against. Where you can afford both, run both.

## Key Takeaways

- Partition security cases by attack mechanism, show one set as the specification, and evaluate on the families you withheld.
- The 19.3 pp joint-success lift held in 7 of 9 conditions, reversed in 2, and reached no Holm-adjusted significance across 31 Python component tasks.
- Showing tests upfront raised the visible-pass-but-hidden-fail rate from 5.6% to 18.8%, so a bigger green suite is a weaker release signal.
- Extra repair rounds cannot reach a behavior family the visible suite never exercises, whatever the round budget.
- Feedback formatting is close to neutral at 453 ties in 465 cells, so invest in mutation, metamorphic, boundary, and fuzzing cases instead.

## Related

- [Bounded Repair-Loop Iterations](bounded-repair-loop-iterations.md) — caps rounds on cost grounds; this page explains why some rounds cannot help at any budget.
- [Security Drift in Iterative LLM Code Refinement](../security/security-drift-iterative-refinement.md) — the scanner-based checkpoint for the same loop, complementary to a held-out test partition.
- [Mutation Testing as a Quality Gate for AI-Generated Test Suites](mutation-testing-quality-gate.md) — one of the named ways to expand the visible signal.
- [Security Knowledge Priming for Code Generation (SPARK)](../instructions/security-knowledge-priming.md) — the prompt-cue alternative, which shifts CWE distribution without cutting vulnerability density.
- [Re-Run the Original Test Suite After Every Refinement Turn](test-suite-after-refinement-turn.md) — catches the functional regressions repair rounds introduce alongside security fixes.
