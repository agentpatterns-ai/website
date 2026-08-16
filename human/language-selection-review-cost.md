---
title: "Language Selection Scored on Review Cost"
term: "Review-Cost Language Selection"
description: "Once agents write most of the code, score a candidate language on review, verification, and maintenance cost — but only when the language is a free variable and someone still reads the diff."
aliases:
  - review-cost language selection
  - reviewability as a language selection criterion
  - scoring a stack on verification cost
tags:
  - human-factors
  - code-review
  - tool-agnostic
last_reviewed: 2026-08-16
maturity: emerging
status: current
---

# Language Selection Scored on Review Cost

> Once agents write the code, score a language on what review, verification, and maintenance cost, not on how fast a human types it.

Score a candidate language or codebase on how cheaply its output can be read, checked, and maintained, and demote write-ergonomics to a tiebreaker. The re-score pays under three conditions: the language has to be a free variable, someone has to still read the diff, and the cheaper machine-checkable fixes have to be exhausted already. Miss any one and the criterion returns a recommendation you cannot act on.

## Three conditions before you re-score

The language is a free variable. A new service, a component not yet written, or a funded rewrite. Most choices in a running system were made years before an agent touched the repository, and the domain often fixes them anyway.

Someone still reads the diff. Across 400 repeat reviewers and 11,429 reviews over seven months, approval rates rose from 30.1% to 36.8% while inline comment volume fell 22% and review latency rose 3.5x — "reflexive habituation under growing workload rather than rational trust calibration alone", in the authors' reading ([Yu et al., 2026](https://arxiv.org/abs/2606.22721v1)). Faros AI reports changes merged with no review at all, human or agentic, up 31.3% ([Faros AI, 2026](https://www.faros.ai/blog/ai-acceleration-whiplash-takeaways)). A review bot does not restore the condition: across 3,109 pull requests, review-agent-only changes merged at 45.20% against 68.37% for human-only, and 12 of 13 review agents scored average signal ratios below 60% ([Chowdhury et al., 2026](https://arxiv.org/abs/2604.03196v1)).

The machine-checkable budget is already spent. A constraint you can add to the language you already have usually beats one you would have to migrate to, so a re-score before that budget is exhausted proposes a migration you did not need.

## What to score

Rank the properties by what still works when the reviewer is tired.

Machine-checkable, and worth the most weight ([Balahan and Seroter, 2026](https://developers.googleblog.com/why-go-is-an-ideal-language-for-ai-assisted-software-engineering/)):

- A static type system that rejects a hallucinated method or a wrong argument type at compile time.
- A check loop fast enough that the agent fixes its own type errors before a human sees the change.
- A standard library broad enough that the agent reaches for a maintained package rather than one its training data suggested.
- Deterministic refactoring tools that update stale patterns without hand edits.

Human-legible, and worth less than its advocates claim: one canonical format, and a design that limits how many ways the same logic can be written. The case for this tier: "If a language offers a dozen different ways to express the same logic, an AI model will inevitably generate a fragmented, haphazardly stylized hodgepodge of syntax" ([Balahan and Seroter, 2026](https://developers.googleblog.com/why-go-is-an-ideal-language-for-ai-assisted-software-engineering/)).

Two discounts apply to that tier. The source is vendor advocacy — Go's group product manager and a Google Cloud evangelist making the case for Go — so its property list is a scoring template, and the shortlist attached to it is not transferable. And the measurements contradict the premise: Faros finds agent output already arrives "idiomatic, well-named, stylistically consistent with the surrounding codebase", with the structural and logical failures "beneath the surface" ([Faros AI, 2026](https://www.faros.ai/blog/ai-acceleration-whiplash-takeaways)).

## Why it works

The cost of a change is generation plus review. Generation collapsed toward zero, because an agent can produce "hundreds of lines of syntactically valid code in seconds" ([Balahan and Seroter, 2026](https://developers.googleblog.com/why-go-is-an-ideal-language-for-ai-assisted-software-engineering/)). Review did not, because it is bounded by comprehension rather than typing: defect-detection ability degrades beyond 200 to 400 lines per sitting, and defect density drops sharply above 500 lines per hour ([SmartBear, citing the Cisco Systems study](https://smartbear.com/learn/code-review/best-practices-for-peer-code-review/)). Faros AI's two-year telemetry across 22,000 developers puts numbers on the split: task throughput per developer up 33.7%, median time in review up 441.5% ([Faros AI, 2026](https://www.faros.ai/blog/ai-acceleration-whiplash-takeaways)).

When one term of a sum collapses and the other carries a hard ceiling, the surviving term sets the total, so a criterion scoring a language against that total has to move with it. [The Bottleneck Migration](bottleneck-migration.md) covers the shift itself; the selection consequence is what this page adds.

## When this backfires

- The defects are semantic. Canonical formatting and limited expressive variance reduce the cost of reading code, not of reconstructing intent. On the failure class Faros measures, the human-legible tier delivers nothing.
- A constraint is available instead. A small reviewer model inspecting a Python codebase with 11 inserted backdoors raised its recall from 54.5% unconstrained to 90.9% given a constrained substrate and a roughly 200-line command-line tool ([Winninger, 2026](https://arxiv.org/abs/2607.02389v1)). Spend that budget before a migration.
- The property list came from a vendor. Scoring candidates against a list reverse-engineered from one language returns that language. Derive the list from your own review-cost data.
- There is no review step. Solo work, prototypes, and disposable artifacts have no review queue, so the criterion has no cost to reduce.
- The decision reaches past code. Architecture, service boundaries, and production reliability stay with humans, because an agent has "a limited view of the greater context in which the code it generates must operate" ([Balahan and Seroter, 2026](https://developers.googleblog.com/why-go-is-an-ideal-language-for-ai-assisted-software-engineering/)). A language cannot be scored on work it never touches.

## Key Takeaways

- Score a language on review, verification, and maintenance cost once agents author most of the code; the write-speed criterion measures a term that no longer binds ([Balahan and Seroter, 2026](https://developers.googleblog.com/why-go-is-an-ideal-language-for-ai-assisted-software-engineering/)).
- The re-score requires all three conditions: a free variable, a review that still happens, and a machine-checkable budget already spent. Within the score, rank machine-checkable properties above human-legible ones.
- Reviewers habituate: approval up 14.5 percentage points across experience deciles with inline comments down 22% ([Yu et al., 2026](https://arxiv.org/abs/2606.22721v1)), and 31.3% more changes merge unreviewed ([Faros AI, 2026](https://www.faros.ai/blog/ai-acceleration-whiplash-takeaways)).
- Exhaust the constraints available in your current language before a re-score becomes a migration proposal; a constrained substrate and a small command-line tool took one reviewer's backdoor recall from 54.5% to 90.9% with no language change ([Winninger, 2026](https://arxiv.org/abs/2607.02389v1)).
- Vendor property lists select their own language. Take the properties, leave the conclusion.

## Related

- [The Bottleneck Migration](bottleneck-migration.md) — the premise this page builds on: generation got cheap and review became the constraint.
- [Author-to-Reviewer Role Inversion in AI-Assisted Teams](author-to-reviewer-role-inversion.md) — the staffing answer to the same shift, where this page gives the technology-selection answer.
- [Programming Language Choice Still Shapes Agent Artifacts](programming-language-choice-shapes-agent-artefacts.md) — scores languages on training-corpus density and the artifact's quality ceiling, a property of the generator rather than the reader.
- [Convenience Loops and AI-Friendly Code](convenience-loops-ai-friendly-code.md) — why typed codebases produce fewer agent corrections, which is the machine-checkable tier measured inside the generation loop.
- [Language Choice as an Agent Token-Cost Lever](../token-engineering/language-choice-token-cost.md) — the token-spend view of the same decision, with the same free-variable caveat.
