---
title: "Frozen-Base Task Mining for Repository Instruction Files"
term: "Frozen-Base Task Mining"
description: "Reverse-apply merged pull requests at one shared base commit to build eval tasks for a repository instruction file, so an optimizer cannot learn facts that were true months ago and are false today."
tags:
  - testing-verification
  - evals
  - instructions
  - skills
  - tool-agnostic
  - arxiv
aliases:
  - reverse-PR task mining
  - frozen base commit task mining
last_reviewed: 2026-09-14
maturity: emerging
---

# Frozen-Base Task Mining for Repository Instruction Files

> Reverting merged pull requests at one frozen base commit yields tasks that keep an optimized instruction file true to the repository it ships against.

Frozen-base task mining builds an eval set by reverse-applying each merged pull request at a single shared commit, then grading the agent on the tests that switch from passing to failing. Kozyrev et al. used it to score candidate `SKILL.md` documents on three Kotlin repositories, and report that only after moving to a frozen base did the optimized documents "consistently describe the state of the repository the agent runs against" ([arXiv:2609.12742v1](https://arxiv.org/abs/2609.12742v1)).

## When this applies

Three conditions gate the method, and most repositories fail at least one.

The repository has to survive the mining. Roughly one merged pull request in five becomes a graded task: 119 out of 660 on koog, 131 out of 452 on ktor, and 100 on kotest. Two repositories never reached the 100-task floor three disjoint splits need. A package rename touched all 213 of JetBrains/tracy's production files in three months, leaving 5 tasks from 203 pull requests. http4k kept 150 reverse-applying patches from 700, of which fewer than 100 broke a test when reverted ([arXiv:2609.12742v1](https://arxiv.org/abs/2609.12742v1)).

Your budget has to cover full agent rollouts, $0.84 each on average. Six optimization runs cost $2,013.98 and 69.2 hours of wall clock ([arXiv:2609.12742v1](https://arxiv.org/abs/2609.12742v1)).

The decision has to survive a weak score. GEPA's documents raised the paired score by 4.9pp on average and SkillOpt's by 0.1pp. Neither result is significant at 20 to 26 held-out tasks per repository, and no run cleared p=0.05, the best being p=0.29. At that split size a sign test rejects only when the document wins four of every five disagreements, and pooled over 69 tasks two of every three ([arXiv:2609.12742v1](https://arxiv.org/abs/2609.12742v1)). Mine the tasks to stop the optimizer learning stale facts, then read the document yourself.

## How to build the task set

Pick one base commit and hold it. Split each merged pull request's diff by path into an implementation half and a test half, then reverse-apply the implementation at that base. Three tiers handle the reversion, cheapest first: `git apply --reverse`, structural re-creation or removal for added and deleted files, and an LLM reconstructing the pre-change source for what survives neither. Re-derive the patch from git afterwards rather than taking the model's output ([arXiv:2609.12742v1](https://arxiv.org/abs/2609.12742v1)).

Then validate. Run the suite once at the unmodified base, reverse-apply each gold patch, and re-run. Whichever tests flip become that task's grading target, which also recovers targets for changes that shipped no tests. Reject a task when nothing switches, when the affected tests already failed, or when the reversion breaks so much of the suite that it stops isolating the change ([arXiv:2609.12742v1](https://arxiv.org/abs/2609.12742v1)).

## Why it works

A reflection-driven optimizer writes assertions grounded in whatever repository state its rollouts ran against. Mining forward at each pull request's own parent commit spreads that state across months of history. The optimizer then writes module paths, build invocations, and APIs that were true then and false at the commit the document ships against, and "the agent followed that advice into failures" ([arXiv:2609.12742v1](https://arxiv.org/abs/2609.12742v1)). Reverting at one frozen base puts the training distribution and the deployment state at the same commit. A claim the optimizer can learn is then a claim that holds where the document gets read.

## When this backfires

Per-PR base commits yield several times as many tasks, and statistical power is the resource this method is shortest on. If you are benchmarking a fixed agent rather than optimizing a document, staleness does not apply and the larger pool is the better trade.

Planning to strip the stale claims in review does not rescue the forward direction. The optimizer organizes the document around them: one such artifact opens by instructing the agent to work out which of "two distinct repository shapes" it is in, describing one repository seen at two points in its own history ([arXiv:2609.12742v1](https://arxiv.org/abs/2609.12742v1)).

The reverter is where contamination enters. Only 25 of koog's 119 graded tasks reverse-apply cleanly, 56 of 100 on kotest and 65 of 131 on ktor, so most of the pool comes from the LLM tier, which "introduces defects of its own that the validation gate cannot see" ([arXiv:2609.12742v1](https://arxiv.org/abs/2609.12742v1)). A static check over the reconstructed sources is the compensating control.

## Example

Under a Claude Code harness running Sonnet 4.5, the synthetic benchmark gskill optimizes against leaves the agent at 100% with no skill on one repository, and moves it from 94.8% to 100% on another. Those instances change a median of 4 and 7 lines and sit in a single file in 98% to 100% of cases ([arXiv:2609.12742v1](https://arxiv.org/abs/2609.12742v1)).

Frozen-base tasks are larger: a median of 54 lines across 3 files on koog, 27 lines across 2 files on ktor, and 16 lines within one file on kotest, with 23%, 50%, and 73% of tasks confined to a single file. The agent resolves 53% of them pooled with no document loaded, which is the room a document has to work in ([arXiv:2609.12742v1](https://arxiv.org/abs/2609.12742v1)).

## Key Takeaways

- Fix one base commit before mining. The base the tasks sit at decides whether an optimizer can write a document that is true where it ships.
- Budget about five merged pull requests per graded task, and one full agent rollout per scored attempt.
- A repository-sized split cannot settle whether the document helps. Use the tasks to constrain what the optimizer learns, and a maintainer's read to decide whether to merge the result.
- Treat the LLM reversion tier as a contamination source and add a static check over what it reconstructs.

## Related

- [Review-Comment-Derived Benchmarks for Code Review Agents](review-comment-derived-benchmarks.md) — the other way to mine merged pull requests for eval tasks, aimed at review agents rather than instruction files
- [Purpose-Built Eval Suites for Model and Harness Swaps](purpose-built-eval-suites.md) — sizing a small suite to the decision it has to support
- [Audit the Noise Floor Before Trusting a Benchmark Gap](benchmark-noise-floor-audit.md) — measuring the variance a reported gain has to clear
- [Evaluating AGENTS.md: When Context Files Hurt More Than Help](../instructions/evaluating-agents-md-context-files.md) — what the published evidence says about whether these documents help at all
- [Reflective Prompt Evolution with Pareto Selection (GEPA)](../patterns/agent-design/gepa-reflective-prompt-evolution.md) — the optimizer these task sets feed
