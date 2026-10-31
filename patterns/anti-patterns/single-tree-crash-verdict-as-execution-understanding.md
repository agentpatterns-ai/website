---
title: "Single-Tree Crash Verdicts as Execution Understanding"
term: "Single-Tree Crash Verdict"
description: "A correct crash verdict can come from noticing suspicious code. Opus trajectories that reached the crash site had similar prediction-rate increases on both trees."
tags:
  - anti-pattern
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - single-tree crash evaluation
  - crash verdict without a control tree
  - source intervention pairing
last_reviewed: 2026-10-26
maturity: emerging
---

# Single-Tree Crash Verdicts as Execution Understanding

> A crash verdict on the failing tree alone cannot separate execution reasoning from noticing suspicious code.

Ask an agent whether a reproducer crashes the broken tree, get a correct yes, and you have learned less than it looks. Huang et al. put it plainly: "A correct prediction alone, however, does not establish this ability, since it may come from merely spotting suspicious code" ([arXiv:2610.29332v1](https://arxiv.org/abs/2610.29332v1), abstract). Their answer is a control arm. Pair two source trees that differ by one commit, hold the reproducer fixed, verify both outcomes by execution, then require the agent to predict a crash more often on the crashing tree.

## What the paired test shows

The `sysrb.v1` split of SysRB holds 934 execution-validated source-tree pairs: 545 Linux kernel crashes from syzbot and 389 open-source system library crashes found by OSS-Fuzz, drawn from ARVO. Four coding agents (Claude Opus 5, GLM 5.3 and DeepSeek V4 Flash on Claude Code, Gemini 3.8 Flash on Google Antigravity CLI) each sampled eight trajectories per tree, with no way to compile the source or run the reproducer ([arXiv:2610.29332v1](https://arxiv.org/abs/2610.29332v1), §3.4 and §4.1).

Discriminability is the crash-prediction rate on the crashing tree minus the rate on the non-crashing tree. Pooled over the full dataset it ran from +12.3% for DeepSeek V4 Flash to +67.7% for Claude Opus 5, with false-negative rates of 27.5% to 76.8% against false-positive rates of 2.8% to 10.9% ([arXiv:2610.29332v1](https://arxiv.org/abs/2610.29332v1), Table 2). "Agents thus rarely raise false alarms but miss many real crashes; even Opus misses more than a quarter of them."

The confound has a measured size, and it lands almost evenly on both arms. Among Claude Opus 5 trajectories grouped by which code they reached, those that read and reasoned about the crash site while never observing the deciding commit returned a crash verdict in 42.6% of runs on the crashing tree, against 6.0% for trajectories that reached neither site. On the non-crashing tree the same comparison gave 39.2% against 5.1%. A rise of roughly 37 percentage points on one arm came with roughly 34 on the other, so discriminability gained about 3 ([arXiv:2610.29332v1](https://arxiv.org/abs/2610.29332v1), Table 6).

Nearly all measured discrimination came from trajectories reaching the deciding code, but reaching it was not sufficient. Agents observed it in 55.6% to 89.0% of trajectories, while discriminability conditional on observing it reached only 21.5% to 75.4% ([arXiv:2610.29332v1](https://arxiv.org/abs/2610.29332v1), Table 4). Distance makes that worse. On the Linux split Opus fell from about 65% in the same-function and same-file groups to 38% when the crash landed in a different subsystem.

## Why it works

Differencing cancels whatever the agent applies to both trees. The metric is Youden's J, so "guessing crash with equal likelihood on both trees contributes zero in expectation, even when it is right on one of them" ([arXiv:2610.29332v1](https://arxiv.org/abs/2610.29332v1), §3.2). That holds only while the commit stays the single perceptible difference, which is why both trees ship as Docker images from one base image, with git history removed "and filesystem metadata randomized so that" the change is the only intended difference. Among trajectories that never reached the commit, discriminability ran −0.6 to +1.9 percentage points, so "Virtually all measured discriminability therefore comes from trajectories that observe the intervention site."

## When this backfires

- Instability prunes hard. The design needs one commit that flips an outcome verified by repeated execution. Of the validated Linux pairs, 545 of 779 survived that pruning, as did 389 of the 582 OSS-Fuzz candidates whose vulnerable revision was already the fix commit's parent ([arXiv:2610.29332v1](https://arxiv.org/abs/2610.29332v1), §3.4).
- Sampling cost is the headline. One tree's verdict frequency took eight runs, and Opus averaged 63.1 turns and $6.39 per run ([arXiv:2610.29332v1](https://arxiv.org/abs/2610.29332v1), Table 2), so a single paired instance is sixteen Opus runs.
- Concurrency-shaped failures scored lower in the measured setup. Mean per-crash discriminability for Opus on Linux was +39.5 on hung task and +40.5 on deadlock, against +68.5 on KASAN reports ([arXiv:2610.29332v1](https://arxiv.org/abs/2610.29332v1), Table 3), so a gate over those classes separates the pair poorly.
- The pair has to be a fair question. Writing about minimal sentence pairs for language models rather than source trees, Vamvas and Sennrich name two conditions for contrastive evaluation: "a tested hypothesis should be well-motivated, since experiments show that contrastive evaluation can lead to false positives", plus test data chosen to minimize the distributional gap between evaluation and deployment ([arXiv:2109.07465v1](https://arxiv.org/abs/2109.07465v1), abstract).
- A high score buys sensitivity, not a correct causal account. The authors say their approach "still lacks direct measurement of crash reasoning", and they flag that "coding agents may have been trained on the commits and can produce crash verdict affected by data contamination."

## Example

Figure 2 of the paper traces one Linux instance, fix `893eaef1`, with Claude Opus 5. The rates below are not from that instance. They are the paper's Table 6 rates over all Claude Opus 5 trajectories. The study validates both outcomes by execution first. "The agent examines each tree independently, without knowing which crashes" ([arXiv:2610.29332v1](https://arxiv.org/abs/2610.29332v1), §1).

**Before — treating a correct crash prediction as execution understanding:** Table 6 groups Opus trajectories that examine the crash site without observing the deciding commit. On the crashing tree, their crash-prediction rate is 42.6%, compared with 6.0% for trajectories reaching neither site.

**After — checking the non-crashing control:** The corresponding rates on the non-crashing tree are 39.2% and 5.1%. The increase appears on both trees, so it adds about 3 percentage points of discriminability ([arXiv:2610.29332v1](https://arxiv.org/abs/2610.29332v1), Table 6).

## Key Takeaways

- Run the diagnosis question on both sides of the deciding commit and score the difference, not the verdict on the broken tree.
- Treat unchanged prediction rates across the pair as no demonstrated discrimination. Opus trajectories that read the crash site had crash rates about 37 points higher on the crashing tree and about 34 on the non-crashing one. These observational groups differed by about 3 points of discriminability.
- Tune for misses, not false alarms. Across all four agents the false-negative range sat well above the false-positive range, so a no-crash verdict is the weak one.
- Budget two trees times eight samples before promising this gate, and report deadlock and hung-task results separately, where Opus on Linux reaches about 40% discriminability.
- Evidence is one paper on four agents and 934 pairs from the Linux kernel and OSS-Fuzz projects, so measure the rates again on your own tasks.

## Related

- [Held-Out Tasks as a Harness Shortcut Defense](held-out-tasks-as-shortcut-defense.md) — the sibling failure where resampling the questions leaves the shortcut in place; here it is the missing second condition rather than the fixed protocol
- [Answer-Reachable Eval Environments](answer-reachable-eval-environments.md) — the environment leaking the fix, which is what removing git history from both trees prevents
- [Pass-Only Grading Treats Luck and Judgment the Same](pass-only-grading-lucky-pass.md) — a correct outcome reached by a weak process, scored identically to a reasoned one
- [When Your Agent's Verifier Reads the Same False Premise](verifier-reads-the-same-premise.md) — the other way a check inherits the answer it is meant to test
- [Destructive-Failure Mechanism Attribution by Mitigation Owner (ClayBuddy Three)](destructive-failure-mechanism-attribution.md) — routing a diagnosed failure to the owner who can fix it, once the diagnosis is trustworthy
