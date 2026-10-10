---
title: "Scoring a Code Review Agent on an Open Benchmark Suite"
term: "Open Code Review Benchmark"
description: "An open code review benchmark such as GitHub's ReviewBench gives a reproducible score for comparing review agents, but it says little about your own codebase's defects."
tags:
  - testing-verification
  - evals
  - code-review
  - tool-agnostic
  - benchmarks
aliases:
  - public code review benchmark
  - ReviewBench (GitHub)
last_reviewed: 2026-10-06
maturity: emerging
---

# Scoring a Code Review Agent on an Open Benchmark Suite

> An open code review benchmark answers "how does my reviewer compare on typical public pull requests", not "will it catch our defects".

An open code review benchmark scores any review agent on a shared set of public pull requests, using one versioned judge and one golden set of known findings. GitHub's ReviewBench is the worked case on this page. It is a different artifact from the LangChain ReviewBench in [Review-Comment-Derived Benchmarks](review-comment-derived-benchmarks.md), which is private and built from one team's review comments.

## Conditions that make it worth the spend

Use an open benchmark when the question is relative and the corpus is a fair stand-in for your work.

- You are comparing two versions of your own harness or model. A fixed corpus, judge, and matcher let a score change attribute mostly to the agent, within run-to-run noise: "We version the benchmark dataset, judge, and matcher used in every evaluation, so results can be compared under the same benchmark configuration" ([GitHub blog](https://github.blog/ai-and-ml/github-copilot/reviewbench-an-open-benchmark-for-ai-code-review/)).
- You want a first baseline before you curate an archive of your own.
- You want to check a vendor claim against one configuration. The leaderboard lists Copilot Code Review, Devin AI, Qodo, Codex, Cubic, Greptile, and Cursor ([review-bench.ai](https://review-bench.ai/), leaderboard read 2026-10-06).
- Your costly defects look like typical public-repository defects, not like project contracts.

Do not use it alone to pick a vendor, or to predict misses in a codebase whose costly defects are tenant scoping, locking, or internal API contracts. The sections below give the reasons.

## What ReviewBench measures

| Part | What it is |
|---|---|
| Corpus | 219 pull requests from 187 public open source repositories in 19 languages, with language and repository-size distributions matching GitHub overall ([GitHub blog](https://github.blog/ai-and-ml/github-copilot/reviewbench-an-open-benchmark-for-ai-code-review/)). Pull request size is weighted toward the reviewable middle and tail, which reduces tiny single-file changes. |
| Golden set | Findings from "real human reviewers, issues inferred from author follow-up commits, deterministic analysis tools, and multiple frontier LLMs across model families", merged by semantic dedupe ([GitHub blog](https://github.blog/ai-and-ml/github-copilot/reviewbench-an-open-benchmark-for-ai-code-review/)). |
| Labeler and judge | One LLM: "We use Claude Sonnet 5 as the LLM grader, applying a consistent evaluation rubric across all submissions" ([GitHub blog](https://github.blog/ai-and-ml/github-copilot/reviewbench-an-open-benchmark-for-ai-code-review/)). |
| Grounded metrics | Recall and precision against the fixed golden true positives. The cross-system comparison. |
| Augmented metrics | Credit novel valid findings, with a per-agent denominator. A per-system diagnostic. |
| Ranking | Users slice by severity and category and set beta in F-beta, and the leaderboard re-ranks ([GitHub blog](https://github.blog/ai-and-ml/github-copilot/reviewbench-an-open-benchmark-for-ai-code-review/)). |

A true positive is "A finding that a competent senior reviewer would expect a PR author to address before merge. TPs are correct, verifiable against the changed code, in scope for the PR, and actionable" ([METHODOLOGY.md](https://github.com/review-bench/ReviewBench/blob/ceb0794a3768da6ef4a56e5311dfb4afd29e5dee/docs/METHODOLOGY.md) §2).

## Reading the score

Compare agents on grounded recall. The authors say "Because augmented recall expands the denominator based on what each agent discovers, we use grounded recall as the headline cross-system comparison and augmented metrics as an additional per-system diagnostic" ([GitHub blog](https://github.blog/ai-and-ml/github-copilot/reviewbench-an-open-benchmark-for-ai-code-review/)). Their worked example shows why. With 10 golden true positives and 5 matched, an agent with 2 novel valid findings scores 7/12 (about 0.58), and an agent with 100 scores 105/110 (about 0.95), "despite identical grounded performance" ([METHODOLOGY.md](https://github.com/review-bench/ReviewBench/blob/ceb0794a3768da6ef4a56e5311dfb4afd29e5dee/docs/METHODOLOGY.md) §7).

Expect low recall and high precision. On the leaderboard as read on 2026-10-06 (snapshot dates run from 2026-06-16 to 2026-10-01), the top grounded recall was 26.0% (Copilot Code Review, Balanced, snapshot 2026-10-01), and grounded precision ran from 84% to 90% across the 28 listed configurations ([review-bench.ai](https://review-bench.ai/)). That is live data, so treat the order of magnitude as the stable part: recall in the twenties, precision in the eighties. The sibling page reports the same low ceiling on other benchmarks ([Review-Comment-Derived Benchmarks](review-comment-derived-benchmarks.md)).

Check label agreement before you slice. The methodology reports agreement between the classifier labels and senior-engineer labels of 96.6% on true positive versus false positive, 98.7% within one level but only 62.9% exact on the three-point severity scale, and 79.7% exact on category ([METHODOLOGY.md](https://github.com/review-bench/ReviewBench/blob/ceb0794a3768da6ef4a56e5311dfb4afd29e5dee/docs/METHODOLOGY.md) §5.4). A slice such as critical-severity recall carries more label noise than the headline.

## Why it works

An open benchmark fixes the inputs a private eval leaves free: the same pull requests, the same golden set, the same versioned judge and matcher, and a fixed denominator for grounded recall ([GitHub blog](https://github.blog/ai-and-ml/github-copilot/reviewbench-an-open-benchmark-for-ai-code-review/)). With those fixed, a score change comes mostly from the agent, within run-to-run noise (the leaderboard reports standard deviations), so a team can compare its harness against other systems and against its own earlier versions. The multi-producer golden set exists because "No single reviewer, whether human or model, can identify everything worth finding in a pull request" (same source).

The mechanism stops at the corpus boundary. The score is evidence about review of public, GitHub-typical pull requests under one classifier's taste. GitHub also reports that offline results track online ones for its own product: "The online A/B test moved in the same direction as ReviewBench predicted: addressed rate (precision) rose 8.0%, recall rose 13.6%, and comment volume rose 61%, while cost per review fell 8.0%" ([GitHub blog](https://github.blog/ai-and-ml/github-copilot/reviewbench-an-open-benchmark-for-ai-code-review/)). That is one vendor testing its own product, and it supports direction only. The methodology itself calls convergence "an empirical question about how faithfully the classifier reproduces human behavior" ([METHODOLOGY.md](https://github.com/review-bench/ReviewBench/blob/ceb0794a3768da6ef4a56e5311dfb4afd29e5dee/docs/METHODOLOGY.md) §8).

## Where the score stops being evidence about your codebase

- Classifier taste. The authors write: "The classifier prompt encodes *our* working group's taste; another team running this methodology could configure the classifier differently and reach different scores for the same agents" ([METHODOLOGY.md](https://github.com/review-bench/ReviewBench/blob/ceb0794a3768da6ef4a56e5311dfb4afd29e5dee/docs/METHODOLOGY.md) §8).
- Project conventions. The same section says certain finding types, "for example, project-conventions violations specific to a single repository", are easier to surface than others, and that "a systematic gap shared by all producers will remain invisible".
- A mostly machine-written golden set. The published golden files show 4,632 findings, 2,623 of them labeled true positive. Of those true positives, 39 (1.5%) carry the producer `human_review`, and only 17 of the 219 pull requests have any human-produced true positive. The largest single producer, `llm_review:claude-sonnet-4.6`, accounts for 1,206 ([review-bench/ReviewBench golden files @ ceb0794](https://github.com/review-bench/ReviewBench/tree/ceb0794a3768da6ef4a56e5311dfb4afd29e5dee/golden), counted by the research step for this page, not stated by the authors).
- Producer concentration. Producers prefixed `ccr:` supply 1,185 of the 2,623 true positives (45%) in the same files. The repository does not define the prefix. Reading `ccr` as Copilot code review is an inference from the launch post, which uses "CCR" for that product. If it holds, the first-ranked system is also a major golden-set producer, and grounded recall then rewards agreement with it. The count shows attribution after dedupe, where "The surviving finding retains the label; duplicates are discarded" ([METHODOLOGY.md](https://github.com/review-bench/ReviewBench/blob/ceb0794a3768da6ef4a56e5311dfb4afd29e5dee/docs/METHODOLOGY.md) §5.4), so it is not exclusive discovery. The authors name the risk: "If any single LLM producer contributes more than a target threshold of the golden TPs (after deduplication), that is a signal to either add more diverse producers or down-weight that producer's unique findings". No threshold value is published ([EXTRACTION.md](https://github.com/review-bench/ReviewBench/blob/ceb0794a3768da6ef4a56e5311dfb4afd29e5dee/docs/EXTRACTION.md) §4.4).
- No held-out split. The 25-pull-request test set is "a representative subset intended for small and test runs, not a separate public/private partition" ([METHODOLOGY.md](https://github.com/review-bench/ReviewBench/blob/ceb0794a3768da6ef4a56e5311dfb4afd29e5dee/docs/METHODOLOGY.md) §3.2). The Martian benchmark states the general risk: "Static datasets risk training data leakage — tools may have seen these PRs during training. That's why we also run the online benchmark" ([withmartian/code-review-benchmark](https://github.com/withmartian/code-review-benchmark)). See [Benchmark Contamination as Eval Risk](benchmark-contamination-eval-risk.md).
- The publisher ranks first. GitHub built the benchmark and Copilot Code Review leads its leaderboard ([review-bench.ai](https://review-bench.ai/), read 2026-10-06).
- An improvement-only leaderboard. "Scores are published to the leaderboard only if they outperform the agent's current leaderboard score, or if this is the agent's first leaderboard entry" ([GitHub blog](https://github.blog/ai-and-ml/github-copilot/reviewbench-an-open-benchmark-for-ai-code-review/)). Published scores are the best runs, not the typical ones.

## Open benchmark or your own archive

| | Open benchmark | Archive built from your reviews |
|---|---|---|
| Cost | Tuning runs are self-funded, and the judge is covered only for the final submission ([README.md](https://github.com/review-bench/ReviewBench/blob/ceb0794a3768da6ef4a56e5311dfb4afd29e5dee/README.md)) | Curation and human adjudication, as described in the sibling page |
| Comparability | Same corpus and judge as every other entry | Only your own versions |
| What it encodes | A working group's taste on public pull requests | Your reviewers' contracts |
| Contamination exposure | Public and static, with no held-out split | Private, if you keep it private |

Run both when the budget allows. Build the archive first when your costly defects are project contracts. [Review-Comment-Derived Benchmarks](review-comment-derived-benchmarks.md) covers that construction.

## When this backfires

- Choosing a vendor from the leaderboard. The publisher ranks first and only improvements are published. A third-party post reports that Martian's online leaderboard orders the same tools differently, with Cubic first and Copilot second ([dev.to](https://dev.to/tessainsley/a-code-review-benchmark-that-isnt-the-vendor-ranking-itself-4jp6), secondary and not checked against Martian's dashboard). Treat it as a sign that rankings differ between benchmarks.
- Hill-climbing on the 25-pull-request test set. It is a subset of the scored set, so gains partly fit the golden set and the judge.
- Ranking by augmented recall. The denominator grows with each agent's own novel findings, and the authors say it "should therefore not be used as the sole basis for ranking agents against each other" ([METHODOLOGY.md](https://github.com/review-bench/ReviewBench/blob/ceb0794a3768da6ef4a56e5311dfb4afd29e5dee/docs/METHODOLOGY.md) §7).
- Codebases dominated by convention or domain defects, such as multi-tenant data access, internal APIs, or regulated code. Some repositories in the golden files are course projects and personal repositories, judging by their names, which fits the aim of matching GitHub-wide repository sizes and is weak evidence for a large private monorepo.
- Severity-sliced decisions, because exact severity agreement is 62.9%.
- Teams without budget for the judge. Every tuning run pays for the agent and the judge model.

## Key Takeaways

- An open benchmark compares reviewers on public pull requests. It does not predict misses in your codebase.
- Rank across systems on grounded recall, and read augmented recall only within one system.
- Expect grounded recall in the twenties and precision in the eighties on ReviewBench, as read on 2026-10-06.
- The published golden files show a mostly machine-produced golden set, with human review supplying 1.5% of true positives.
- Do not tune against the 25-pull-request test set, and do not pick a vendor from the leaderboard alone.
- Build an archive from your own reviews when your costly defects are project contracts.

## Related

- [Review-Comment-Derived Benchmarks for Code Review Agents](review-comment-derived-benchmarks.md) — the private, own-archive alternative; not the same artifact as GitHub's ReviewBench
- [Benchmark Contamination as Eval Risk](benchmark-contamination-eval-risk.md) — why a public static set leaks into tuning
- [Judge Self-Preference Detection](judge-self-preference-detection.md) — the bias check for one model that both produces and grades
- [Benchmark Noise-Floor Audit](benchmark-noise-floor-audit.md) — sizing a score gap before reading it as an order
- [Meta-Evaluate the LLM Judge Before Trusting Rubric Verdicts](meta-evaluate-llm-judge-rubric-verification.md) — the reliability check a single classifier needs
