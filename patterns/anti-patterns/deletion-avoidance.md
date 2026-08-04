---
title: "Deletion Avoidance: Agents That Guard Code Instead of Removing It"
term: "Deletion Avoidance"
description: "Coding agents retain code an edit requires removing and wrap it in a guard instead; deletion recall peaks at 71.7% and the patches still pass, because suites rarely check removal."
tags:
  - anti-pattern
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - guard-and-go patches
  - incomplete deletion in agent patches
  - retained path as live fallback
last_reviewed: 2026-08-03
maturity: emerging
status: current
---

# Deletion Avoidance: Agents That Guard Code Instead of Removing It

> Coding agents keep code an edit was meant to remove, wrapping it in a guard so the patch passes tests with the removal undone.

A green suite is not evidence the agent removed what the change required. The suite was written before the removal was required, so nothing in it fails when the old path survives. Across the five leading models on the SWE-bench Verified leaderboard, deletion recall against the developer patch peaks at 71.7% on tasks all five solve ([Ebrahimi et al., arXiv:2607.28887v1](https://arxiv.org/abs/2607.28887v1)).

## When this applies

Ask "did the agent delete what it should have?" as a separate review question under three conditions, and only under them:

- Removal was the intent. A branch kept behind a flag as a [temporary compensatory mechanism](../agent-design/temporary-compensatory-mechanisms.md) is the plan, not a defect.
- You pair it with an over-deletion check. Every intervention the authors tested moved error from retention to excess rather than removing it ([arXiv:2607.28887v1](https://arxiv.org/abs/2607.28887v1)).
- The retained code costs something. Where the leftover branch is unreachable and dead-code elimination handles it at build time, the finding is noise.

## What the measurements show

The failure is not localization. Models reach the right file for 92.5% to 94.4% of required deletions and the right scope for 68.1% to 74.4%, then remove the exact line in only 44.6% to 51.6% of cases ([arXiv:2607.28887v1](https://arxiv.org/abs/2607.28887v1)). The agent knows where the code is.

Instead of cutting, 29.0% of passing patches wrap the target in a guard, a shape the authors name Guard-and-Go. Its commonest form, 40.2% of cases, keeps the removed logic as the default execution path and routes the reported case through a new branch. Those patches run 1.67 times the developer patch size at the median and pass at 72.2% against 85.2% for delete-and-replace ([arXiv:2607.28887v1](https://arxiv.org/abs/2607.28887v1)).

Retrofit 34 deletion-heavy tasks with tests that fail while the target remains and four frontier models drop from 63.2% to 41.9%. Removing the addition work does not rescue them: on CanItDelete, 200 tasks whose entire required edit is deletion, the best model reaches 79.0% and a smaller open model falls to 18.0% ([arXiv:2607.28887v1](https://arxiv.org/abs/2607.28887v1)).

Maintainers already discount the result. Reviewers of 296 passing agent pull requests merged them 24 points below the benchmark score, citing verbosity and departure from repository conventions ([arXiv:2607.28887v1](https://arxiv.org/abs/2607.28887v1)).

## Why it works

Deletion is undertrained rather than out of reach, and the missing signal is the absence of any penalty for keeping code. The authors attribute the behavior to additive skew in training corpora and to deletion examples being underrepresented in code post-training mixtures. Test-based evaluation compounds both: it accepts a guard because the original suite never checks removal, so neither supervised fine-tuning nor reinforcement learning sees a gradient punishing retention ([arXiv:2607.28887v1](https://arxiv.org/abs/2607.28887v1)).

Their pilot supports the causal reading. Adding 12,821 deletion examples, 0.7% of a 15.9 billion token code mixture, moved a 7B model from 6.5% to 13.7% on CanItDelete and lifted its SWE-bench Verified score from 25.40% to 30.70%.

## Detection

Read the diff for its shape, not its outcome. A patch that adds a condition around the code the ticket asked you to delete is the signature, and a fix larger than the change warranted is where that condition hides. Review catches this cheaply. A test that fails while the target remains catches it automatically, but it couples to implementation, so reserve that assertion for removals worth gating on and delete it once the migration lands.

Prompting is a weak lever alone. GPT-5.6 Sol barely moved under an explicit deletion instruction or a region pointer, reaching 80.5% only once given exact line spans ([arXiv:2607.28887v1](https://arxiv.org/abs/2607.28887v1)).

## When this backfires

- Mid-migration codebases. Flag-guarded migration work retains the old path on purpose, so a check reading every retained branch as avoidance fires constantly and teaches reviewers to skip it.
- Weak rollback. Retention pressure converts into over-deletion: exact line spans cut incomplete deletion to 0.6% but left over-deletion at 16.5%, and the post-training pilot cut incomplete deletion 13.9 points while raising over-deletion 6.2 ([arXiv:2607.28887v1](https://arxiv.org/abs/2607.28887v1)). Where reverting a bad removal is expensive, that trade is negative.
- Scope expansion already dominates. Agents deleting what nobody asked them to delete is its own measured failure, at 5.4% to 27.7% in permissive agent frameworks against 0.2% to 4.5% in an ask-to-continue one ([Overeager Coding Agents, arXiv:2605.18583v1](https://arxiv.org/abs/2605.18583v1)). Budget spent chasing unremoved lines is budget not spent on containment.
- Removal-assertion brittleness. Such a test is derived from one developer patch, and the authors note their own deterministic evaluator cannot judge semantic equivalence or intentional restructuring, so a valid alternate repair reads as a failure ([arXiv:2607.28887v1](https://arxiv.org/abs/2607.28887v1)).
- Outside the measured envelope. Evidence covers Python and JavaScript, high-starred repositories, 34 retrofit tasks, and one 7B pilot reported as three-run means without variance ([arXiv:2607.28887v1](https://arxiv.org/abs/2607.28887v1)).

## Key Takeaways

- Ask for the removal explicitly when you want one; the exact-span result shows agents comply once the target is unambiguous, and infer it poorly otherwise.
- Never add deletion pressure without an over-deletion check; the measured effect of every fix so far is a swap, not a repair.
- Skip the check entirely on deliberate retention, unreachable code, and behavior-only review contexts.

## Related

- [Refactoring Runaway: Tangled Refactorings in Agent Patches](refactoring-runaway.md) — the additive twin: agents bundling unrequested refactors into a fix
- [Premature Completion: Agents That Declare Success Too Early](premature-completion.md) — stopping at the first green signal with work outstanding
- [Assertion-Free Test Theater in Agent-Authored Patches](assertion-free-test-theater.md) — why a present test is not a check
- [Shadow Tech Debt](shadow-tech-debt.md) — the accumulated cost of individually-passing agent patches
- [Overeager-Behavior Elicitation](../../verification/overeager-behavior-elicitation-scope-trap-fragments.md) — measuring the opposite failure, agents doing more than asked
