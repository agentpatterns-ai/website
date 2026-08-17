---
title: "Review-Comment-Derived Benchmarks for Code Review Agents"
term: "Review-Comment-Derived Benchmark"
description: "Build a code review agent benchmark from curated comments trusted reviewers left on your merged PRs, so the eval scores the codebase-specific contracts public benchmarks never encode."
tags:
  - testing-verification
  - evals
  - code-review
  - tool-agnostic
aliases:
  - PR-comment-derived eval
  - reviewer-derived code review benchmark
last_reviewed: 2026-08-16
maturity: emerging
---

# Review-Comment-Derived Benchmarks for Code Review Agents

> Curated comments from trusted reviewers on your merged PRs make a code review benchmark that scores codebase-specific defects generic benchmarks miss.

A review-comment-derived benchmark turns comments that trusted reviewers left on merged pull requests into eval tasks. Each task freezes one PR's diff and metadata, and a verifier checks whether the agent recovers the defect the reviewer found. LangChain built ReviewBench this way because it trusted few existing benchmarks, "because they don't incorporate our internal review standards" ([LangChain](https://www.langchain.com/blog/evaluating-code-review-agents-with-reviewbench)).

## Conditions that make it worth building

Three conditions have to hold before the construction cost pays back.

Your review archive survives curation. Attrition is severe. The independent c-CRAB dataset started from 671 pull requests carrying 1,313 review comments and finished with 184 instances and 234 validated comments across 56 repositories ([arXiv:2603.23448v3](https://arxiv.org/abs/2603.23448v3)). That is close to six raw comments per validated label.

You can fund human adjudication after the automated filter. LangChain passed unfiltered reviews through an LLM gate, then manually reviewed each survivor, and states that "this curation is what makes ReviewBench useful as an eval" ([LangChain](https://www.langchain.com/blog/evaluating-code-review-agents-with-reviewbench)).

You are answering a question about your own harness. ReviewBench's largest published effect came from the prompt rather than the model: on a matched 20-task slice, a structured review prompt took one configuration to a score of 0.32, above the static-review runs of two other models on the same tasks and with no new tools ([LangChain](https://www.langchain.com/blog/evaluating-code-review-agents-with-reviewbench)). For a public reproducible score, c-CRAB already publishes one. This is the sizing judgment any [purpose-built eval suite](purpose-built-eval-suites.md) demands.

## The construction pipeline

| Stage | Input | Output |
|---|---|---|
| Collect | Comments from trusted reviewers on merged PRs | Candidate findings |
| Gate | The unfiltered comment stream, through an LLM classifier | Shortlist with weak candidates flagged |
| Adjudicate | Shortlist, read by a human | Comments naming a real issue the change introduced, specific enough for a verifier |
| Freeze | One PR per surviving finding | Seeded repository plus a local stub serving frozen PR metadata and diff, so "the task does not depend on live GitHub state" ([LangChain](https://www.langchain.com/blog/evaluating-code-review-agents-with-reviewbench)) |
| Verify | Agent findings, each with location, title, and explanation | Coverage and precision against the curated baseline |

## How coverage and precision are scored

Coverage counts a baseline issue as found when the verifier judges that the agent identified the same underlying problem in the same code path, so the score follows the defect rather than the reviewer's phrasing. Precision is the share of submitted findings the verifier judges correct, including findings that match no baseline issue but the code supports. LangChain weights the two evenly into an F1 headline. Expect low absolute numbers. Across 59 tasks covering 64 baseline issues under a bare harness, "the strongest runs recover about 30% of the baseline issues" ([LangChain](https://www.langchain.com/blog/evaluating-code-review-agents-with-reviewbench)). Four automated review tools scored between 20.1% and 32.1% on c-CRAB ([arXiv:2603.23448v3](https://arxiv.org/abs/2603.23448v3)).

## Why it works

A review defect is defined by a contract the diff does not contain. Two of LangChain's benchmark issues are a query that fetched and deleted a resource by ID without checking the tenant, and an endpoint migration that dropped a filter the original API applied. Catching either requires the agent to "reconstruct implicit system contracts from the surrounding code instead of just inspecting the changed lines in isolation" ([LangChain](https://www.langchain.com/blog/evaluating-code-review-agents-with-reviewbench)). That is the capability an [agentic review architecture](../code-review/agentic-code-review-architecture.md) exists to supply. A synthetic bug encodes only contracts its generator already knows. A reviewer's comment records a human applying one that lives in the team's heads, which is why curation carries the technique rather than merely preparing it. c-CRAB reaches the same construction independently and finds that automated tools "address design, documentation, and maintainability substantially less frequently" than humans ([arXiv:2603.23448v3](https://arxiv.org/abs/2603.23448v3)).

## When this backfires

- Skipping adjudication after the gate. An LLM cleaner measured on this task reaches 66% to 85% precision at detecting valid comments ([arXiv:2502.02757v2](https://arxiv.org/abs/2502.02757v2)), so gate output shipped as labels promotes nits to baseline issues and penalizes agents for ignoring them.
- Trusting an unmeasured judge. Across 21 judges and roughly 541,000 judgments, raw agreement overstated chance-corrected agreement by 33 to 41 percentage points on MT-Bench, and judge rankings moved by as many as 14 positions across benchmarks ([arXiv:2606.19544v1](https://arxiv.org/abs/2606.19544v1)). [Meta-evaluate the judge](meta-evaluate-llm-judge-rubric-verification.md) first.
- Reading a small suite as a leaderboard. ReviewBench runs 59 tasks and its authors want more "so results are more stable" ([LangChain](https://www.langchain.com/blog/evaluating-code-review-agents-with-reviewbench)), so a ranking drawn from it moves with sampling noise.
- Homogeneous reviewers. A defect class nobody on the team reviews for cannot enter the baseline, and a high score then licenses shipping into that gap.
- Moving standards. When a contract such as tenant scoping changes, the baseline issue silently becomes wrong and the eval starts penalizing current behavior.

## Key Takeaways

- Put the budget on curation. Close to six raw comments yield one validated label.
- Keep the human step after the LLM gate. At 66% to 85% precision the gate produces a shortlist, never labels.
- Score the underlying defect and the code path it sits in, so wording changes leave the result alone.
- Freeze PR metadata and diff behind a local stub so results do not move with the upstream repository.
- Build it to compare harnesses. A structured review prompt beat model swaps on the one matched comparison published so far.

## Related

- [Purpose-Built Eval Suites for Model and Harness Swaps](purpose-built-eval-suites.md) — the general case for a local suite; this page is the code review instance of it
- [Human-Review-Driven Curation of Golden Eval Datasets](human-review-golden-dataset-curation.md) — the ongoing curation loop that keeps a suite calibrated after you have built one
- [Meta-Evaluate the LLM Judge Before Trusting Rubric Verdicts](meta-evaluate-llm-judge-rubric-verification.md) — the reliability check the verifier in this pipeline needs
- [Benchmark Contamination as Eval Risk](benchmark-contamination-eval-risk.md) — why the same PRs must not both train and grade the agent
- [Agentic Code Review Architecture](../code-review/agentic-code-review-architecture.md) — the reviewer architecture these tasks are designed to stress
