---
title: "Agentic Code Review Architecture With Tool-Calling"
description: "Move code review from static diff analysis to an agentic architecture that uses tool-calling to gather repository context for deeper reviews."
term: "Agentic Code Review Architecture"
tags:
  - testing-verification
  - code-review
  - copilot
aliases:
  - "Agentic Code Review"
  - "Tool-Calling Code Review"
last_reviewed: 2026-06-13
maturity: adopted
---

# Agentic Code Review Architecture

> Agentic code review replaces static diff analysis with a tool-calling architecture where the reviewer explores the repository to judge how changes fit the larger codebase.

## The shift

Traditional AI code review works on the diff alone. The reviewer sees the changed lines without the surrounding architectural context. Agentic code review replaces this with a tool-calling architecture. The reviewer explores the repository, reads linked issues, traces dependencies, and examines the directory structure before it writes feedback.

GitHub Copilot code review made this shift in [October 2025 (public preview)](https://github.blog/changelog/2025-10-28-new-public-preview-features-in-copilot-code-review-ai-reviews-that-see-the-full-picture/) and [March 2026 (GA)](https://github.blog/changelog/2026-03-05-copilot-code-review-now-runs-on-an-agentic-architecture/). The reviews now comment on architectural effects, pattern violations, and cross-cutting concerns, not just line-level syntax.

## How agentic review works

### Tool-calling for context gathering

The reviewer uses [agentic tool-calling to gather full project context, including code, directory structure, and references](https://github.blog/changelog/2025-10-28-new-public-preview-features-in-copilot-code-review-ai-reviews-that-see-the-full-picture/). The agent retrieves whatever it needs to understand how the changes fit the wider architecture.

This means the reviewer can:

- Read files outside the diff to understand call sites, interfaces, and dependencies
- Examine directory structure to verify new files follow project conventions
- Read linked issues and PRs to identify [subtle gaps where code appears sound in isolation but misaligns with project requirements](https://github.blog/ai-and-ml/github-copilot/60-million-copilot-code-reviews-and-counting/)

### Hybrid LLM and deterministic analysis

The system [blends LLM detections and tool-calling with deterministic tools like ESLint and CodeQL](https://github.blog/changelog/2025-10-28-new-public-preview-features-in-copilot-code-review-ai-reviews-that-see-the-full-picture/). This hybrid approach combines two methods:

- LLM analysis for semantic understanding, pattern recognition, and architectural judgment
- Deterministic tools: CodeQL for security analysis, ESLint for style and rule enforcement

Together they produce high-signal findings across security and quality.

### Strategic review planning

For complex PRs, the agent [maps out its review strategy ahead of time](https://github.blog/ai-and-ml/github-copilot/60-million-copilot-code-reviews-and-counting/). This helps on long pull requests where context is easily lost. The previous architecture would [finalize results at the end of a review, often "forgetting" early discoveries](https://github.blog/ai-and-ml/github-copilot/60-million-copilot-code-reviews-and-counting/). Planning ahead avoids that failure mode, so the agent catches problems as it reads rather than at the end.

## Measured impact

The agentic architecture produced an [8.1% increase in positive developer feedback](https://github.blog/ai-and-ml/github-copilot/60-million-copilot-code-reviews-and-counting/) despite slower reviews. The team describes this as [a deliberate trade-off worth making, because meaningful analysis needs computation time](https://github.blog/ai-and-ml/github-copilot/60-million-copilot-code-reviews-and-counting/).

The system keeps [cross-review memory](https://github.blog/ai-and-ml/github-copilot/60-million-copilot-code-reviews-and-counting/), so it recognizes patterns across pull requests rather than treating each one as isolated. Flagging a pattern in one section can inform future reviews of the same codebase.

## Architectural implications

Any AI code review system gains from the same structural shift:

1. Give the reviewer tools, not just data. A reviewer that can read files, search, and trace dependencies produces more accurate findings than one that only sees the diff.
2. Blend analysis methods. Use LLMs for judgment calls (architectural fit, naming quality, design patterns) and deterministic tools for rule-based issues (security patterns, style violations, type errors).
3. Plan before reviewing. For large PRs, have the agent scan the overall change scope and create a review strategy before it examines individual files. This stops early findings from being forgotten.
4. Read beyond the diff. The most useful comments come from understanding how changed code interacts with unchanged code: call sites, shared interfaces, and test coverage of affected paths. This is the cross-file blind spot [diff-based review](diff-based-review.md) cannot cover on its own.

## Operational considerations

Agentic code review needs compute infrastructure for tool-calling loops. GitHub's implementation needs [self-hosted runners for organizations that opted out of GitHub-hosted runners](https://github.blog/changelog/2026-03-05-copilot-code-review-now-runs-on-an-agentic-architecture/). Custom implementations must account for the added latency and cost from multiple tool calls per review.

As of March 2026, you can [trigger reviews from the GitHub CLI](https://github.blog/changelog/2026-03-11-request-copilot-code-review-from-github-cli/) with `gh pr edit --add-reviewer @copilot`, or by selecting Copilot during `gh pr create` (requires CLI 2.88.0+). See [Copilot CLI Agentic Workflows](../tools/copilot/copilot-cli-agentic-workflows.md) for details.

## When this backfires

Agentic code review adds overhead that can outweigh its benefits in several cases:

- Small or trivial PRs: a tool-calling review loop has fixed startup latency that exceeds the value added on single-file or typo-fix PRs. Static diff review is faster and enough.
- Latency-sensitive pipelines: teams running sub-minute CI gates will find that agentic review's multi-tool round-trips clash with their merge velocity targets. The 8.1% quality gain does not make up for a blocked pipeline.
- Self-hosted runner constraints: GitHub's implementation needs self-hosted runners for organizations that have opted out of GitHub-hosted runners. Teams without that infrastructure cannot adopt the feature without operational changes.
- Over-reaching architectural comments: the agent's wider context access can produce low-signal comments on code that is intentionally isolated or handled by conventions the agent does not know. Without a custom review persona tuned to project norms, false positives increase reviewer fatigue.

## Example

A pull request modifies a shared authentication helper used by six services. With static diff review, the AI sees only the changed lines in the helper and comments on syntax and naming. With agentic review, the workflow runs like this:

1. Context gathering: the agent reads the helper file, then calls file-read tools on each of the six services that import it. It examines how each one uses the interface being changed.
2. Issue linkage: the agent reads the linked issue to understand the intended behavior change against what the diff implements.
3. Review strategy: before it comments, the agent maps the full change scope: the modified interface, affected call sites, related tests, and existing documentation.
4. Findings: the agent surfaces that three of the six services rely on the old return shape. It flags this as a breaking change the diff-only view would miss, and references the specific call sites by file and line.

You can trigger the same review with GitHub Copilot from the CLI: `gh pr edit --add-reviewer @copilot`. The agent runs in a loop, calling tools to gather context before it posts inline comments.

## Key Takeaways

- Agentic code review replaces static diff analysis with tool-calling that explores full repository context
- The hybrid approach blends LLM semantic analysis with deterministic tools (CodeQL, ESLint) for high-signal findings
- Strategic review planning prevents context loss on complex PRs
- Reading linked issues and tracing dependencies enables reviews that evaluate architectural fit, not just line-level correctness
- The approach produced an 8.1% increase in positive developer feedback despite higher latency

## Related

- [Agent-Assisted Code Review](agent-assisted-code-review.md)
- [Self-Improving Code Review Agents — Learned Rules](learned-review-rules.md)
- [Copilot CLI Agentic Workflows](../tools/copilot/copilot-cli-agentic-workflows.md)
- [Signal Over Volume in AI Review](signal-over-volume-in-ai-review.md)
- [Committee Review Pattern](committee-review-pattern.md)
- [Diff-Based Review Over Output Review](diff-based-review.md)
- [Tiered Code Review](tiered-code-review.md)
- [CRA-Only Review and the Merge Rate Gap](cra-merge-rate-gap.md) — merge rate evidence for CRA-only versus mixed reviewer compositions
- [Match Tool Instructions to the Agent Workflow](../instructions/match-tool-instructions-to-workflow.md) — why upgrading this architecture's toolset regressed cost and detection until the review instructions were rewritten
