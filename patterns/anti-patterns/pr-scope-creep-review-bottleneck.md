---
title: "PR Scope Creep as a Human Review Bottleneck"
description: "When a stalled PR blocks dependent work, you add that work to the same PR — making it larger, slower to review, and harder to merge, compounding the bottleneck."
term: "PR Scope Creep as a Human Review Bottleneck"
aliases:
  - review bottleneck
  - PR scope creep
tags:
  - human-factors
  - workflows
  - code-review
  - tool-agnostic
  - anti-pattern
last_reviewed: 2026-11-09
maturity: established
---

# PR Scope Creep as a Human Review Bottleneck

> Adding dependent work to a stalled PR enlarges its review scope. A stack can keep those review decisions separate.

## The pattern

A blocked dependency does not have to become a larger review unit. Adding its dependent work to the same PR combines changes that reviewers could otherwise inspect separately. GitHub's [stacked pull requests](https://github.blog/changelog/2026-10-06-stacked-pull-requests-generally-available/) provide one way to separate those review units while keeping their merge relationship explicit.

The review-capacity concern has measured examples. [Faros' 2025 telemetry](https://www.faros.ai/blog/ai-software-engineering), covering more than 10,000 developers across 1,255 teams, reports 98% more merged PRs and 91% longer review time on high-AI-adoption teams, alongside a 154% increase in average PR size. These are reported associations, not a measured effect of adding dependent work to a stalled PR.

The later [Faros 2026 report](https://www.faros.ai/blog/ai-acceleration-whiplash-takeaways) uses a different comparison: each organization's periods of lowest and highest AI adoption. Its telemetry covers 22,000 developers and more than 4,000 teams; median time in review rises 441.5%. Keep that within-organization baseline separate from the earlier report rather than presenting the percentages as directly comparable estimates.

## What to do instead

Use a separate PR for each change that needs its own review decision. When one depends on another, consider a stack: GitHub documents smaller, focused PRs that can be reviewed independently and merged together ([GitHub](https://github.blog/changelog/2026-10-06-stacked-pull-requests-generally-available/)).

Before adopting that workflow, distinguish two questions:

1. Can the reviewer understand and approve each change separately?
2. Must the changes land together, and can the repository's merge path validate that group?

These are workflow checks, not a universal line-count rule. Neither the Faros associations nor GitHub's feature announcement establishes that every PR above a particular size has the same review cost.

## When this backfires

Stacking separates review units; it does not remove merge requirements. GitHub's general-availability announcement says a stack enters the merge queue as one merge group. Its announced auto-merge behavior waits until all selected PRs meet merge requirements. A stack therefore does not make an unready dependency ready ([GitHub](https://github.blog/changelog/2026-10-06-stacked-pull-requests-generally-available/)).

Check the supported host too: the October 2026 announcement makes stacks available on github.com plans and describes GitHub Enterprise Server support as forthcoming. Do not infer availability on a particular server installation from that announcement.

## Example: separate review, grouped merge

GitHub documents independent PR review followed by a grouped merge. With the merge-commit method, each PR gets its own merge commit ([GitHub](https://github.blog/changelog/2026-10-06-stacked-pull-requests-generally-available/)).

Use that distinction when planning dependent work: keep its review decision visible instead of enlarging an existing PR solely because its dependency has not merged. See [Native Pull Request Stacks in an Agent Pipeline](../../workflows/native-pr-stacks-agent-pipeline.md) for the pipeline integration.

## Key Takeaways

- Faros reports increased review time alongside increased AI adoption; preserve each report's comparison baseline.
- A stack can separate review decisions while preserving a dependency's merge relationship.
- Grouped merging still requires ready PRs; it is not a substitute for verification or reviewer capacity.

## Related

- [The Bottleneck Migration](../../human/bottleneck-migration.md) — why review becomes the binding constraint when generation gets cheap
- [Law of Triviality in AI PRs](law-of-triviality-ai-prs.md) — reviewer psychology behind rubber-stamping large diffs
- [LLM Code Review Overcorrection](llm-review-overcorrection.md) — how AI reviewers misclassify correct code at scale
- [Shadow Tech Debt](shadow-tech-debt.md) — how AI-accelerated delivery creates invisible debt accumulation
- [Diff-Based Review Over Output Review](../../code-review/diff-based-review.md)
- [Agentic Code Review Architecture](../../code-review/agentic-code-review-architecture.md)
- [Agent-Authored PR Integration: Collaboration Signals](../../code-review/agent-authored-pr-integration.md)
- [Cognitive Load, AI Fatigue, and Sustainable Agent Use](../../human/cognitive-load-ai-fatigue.md) — managing the cognitive costs of sustained AI-augmented work, including review fatigue
