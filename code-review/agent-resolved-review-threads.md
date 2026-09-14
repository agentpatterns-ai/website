---
title: "Agent-Resolved Review Threads"
term: "Agent-Resolved Review Threads"
description: "A review agent that closes the threads it opened breaks merge gated on conversation resolution and precision measured from resolve events, and a closed thread no longer proves a person read it."
aliases:
  - auto-resolution in code review
  - agent closing its own review comments
  - automatic resolution of review comments
tags:
  - code-review
  - testing-verification
  - copilot
last_reviewed: 2026-09-12
maturity: emerging
---

# Agent-Resolved Review Threads

> A reviewing agent that closes its own threads breaks resolution-gated merge and resolve-click precision, and a closed thread no longer proves anyone read it.

Two conditions decide how much this change costs your repository.

Is the required-conversation-resolution rule the control between the diff and `main`? Where tests and a merge queue also gate the branch, resolution was one signal among several. Where it was the gate, it now clears without a person acting.

Do you read resolve events as data? A dashboard counting "Incorrect" per rule loses the record on exactly the comments a fix addressed.

Meet neither and the feature mostly saves bookkeeping. The cost that remains is the one every team pays: the model that wrote a finding now decides it is fixed.

## What shipped

GitHub Copilot code review resolves its own comments as of 11 September 2026. The trigger is a commit, judged during the next review pass: "When you push a commit that addresses a Copilot code review comment, Copilot now resolves that comment during its rereview" ([GitHub Changelog](https://github.blog/changelog/2026-09-11-auto-resolution-and-analysis-updates-in-copilot-code-review)). The changelog names one trigger and no other: "Comments are automatically resolved when a later commit addresses the underlying feedback" (same source).

It closes only what it judges addressed: "Feedback that is still outstanding stays open, so nothing gets lost" (same source). The goal is the worklist, where open comments "reflect only the feedback that still needs your attention" (same source).

The same entry also changes which findings exist. Copilot code review "now uses the full set of shell tools from the Copilot SDK, running behind the Copilot agent firewall", and GitHub's experiments with that change report it "surfaced more high severity findings and fewer nits". The `Lite` tier switched to "an ensemble of agents to produce a review rather than one agent working alone", which "increased the average number of addressed comments per review by 47% for high severity findings, 31% for medium, and 11% for low, while reducing review cost by about 8%" (same source).

## Why it works

Thread state stops being a record and becomes a derivation. A human-clicked resolve is a fact about one person's bookkeeping at one moment, and it cannot notice a later commit reintroducing the problem. Recomputing the state on each rereview ties it to the code.

The state it replaces was weaker than its reputation. Resolve rights have sat with the author since 2018: "only the pull request author or users with write access to the repository have the ability to resolve the conversation" ([GitHub Changelog](https://github.blog/changelog/2018-09-19-conversation-resolution-permissions/)). The alternative running in production elsewhere is coarser still. Atlassian's RovoDev Code Reviewer counts a comment resolved when it "triggered code changes in the subsequent commits", reporting 38.70% over a one-year period ([arXiv:2601.01129v2](https://arxiv.org/abs/2601.01129v2)). That definition keys on the commit, not on the fix.

The cost is who does the deriving. The model that wrote the finding decides the finding is discharged. Asked whether its own output preserved behavior, a producing model silently endorsed 31.7% of real semantic drift cases, and the per-model miss rate ran from 0% to 100% ([arXiv:2605.21537v1](https://arxiv.org/abs/2605.21537v1)). That task is code modernization rather than comment triage, so read it as the nearest measurement of the shape, not as this feature's error rate.

## When this backfires

- The commit touches the flagged line without removing the cause. The thread closes, on a judgment from the finding's author. In recursive fine-tuning the same structure has a measured worst case: "In the clearest case, the binary self-gate enters a rubber-stamp regime where acceptance scores rise while benchmark correctness falls", so the authors want "exogenous verification rather than model-coupled self-review" ([arXiv:2606.28438v1](https://arxiv.org/abs/2606.28438v1)). That setting is training rather than pull requests, and the structure is the same.
- You measure reviewer precision from resolve events. The resolution-reason dropdown fires on a human click: you "specify the reason for resolving a Copilot code review comment by either selecting 'Addressed', 'Won't fix', or 'Incorrect'" ([GitHub Changelog](https://github.blog/changelog/2026-08-27-copilot-code-review-resolution-reasons-and-expanded-capabilities)). Auto-resolution takes the click on fixed comments and leaves it on the rest, so the surviving records lean toward "Won't fix" and "Incorrect". A biased denominator is worse than a small one.
- Merge is gated on "require that all your pull request conversations are resolved before merging" ([GitHub Changelog](https://github.blog/changelog/2021-06-16-new-tools-to-discover-and-resolve-pull-request-conversations-now-generally-available/)) and little else. Green no longer needs a person.
- Your review ritual is a human reading each thread before closing it. The thread closes first now, so resolved and read come apart on the timeline.
- Pull requests carry two or three comments. The bookkeeping saved rounds to zero; the lost record costs the same per comment.

## What to do instead

Move the merge gate onto something auto-resolution cannot clear: required status checks, a merge queue, or an approving reviewer with authorship rules ([agent approval authority](agent-approval-authority.md) covers the second gate this product now clears). Audit on resolver identity rather than resolved count, so a repository where the agent closes most threads reads as a changed posture and not a quiet week. For per-rule precision, use a field the agent does not consume, as [dismissal reason capture](dismissal-reason-capture.md) sets out.

## Key Takeaways

- The one trigger the changelog names is a later commit, evaluated during rereview. Do not design around a passing check or a timer clearing threads for you.
- Conversation resolution was never a second-reader gate: the author could resolve their own threads from 2018 on. This loses a weak signal, not a strong one.
- The ensemble and shell-tool changes alter which findings appear. Only auto-resolution alters who closes them. Evaluate the two separately.
- The dismissal record is the real casualty, and it fails selectively. You keep the records for findings nobody fixed.
- A self-closed thread is not a reviewed thread. Where the decision must be independent, gate on a check the reviewing agent does not control.

## Related

- [Agent Approval Authority in Code Review](agent-approval-authority.md) — the required-approvals rule clearing the same way; that page decides whether to enable it, this one covers the rule you did not get asked about
- [Capturing Dismissal Reasons for Agent Review Findings](dismissal-reason-capture.md) — the precision measurement auto-resolution starves
- [Agentic Review Comment Acceptance](agentic-review-comment-acceptance.md) — how often review comments are accepted at all, which sets the base rate a resolve signal is meant to track
- [Agent Self-Review Loop](agent-self-review-loop.md) — the same producer-judges-own-work structure, one stage earlier
- [Agentic Code Review Architecture](agentic-code-review-architecture.md) — the tool-calling reviewer the shell-tool expansion extends
