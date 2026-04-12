---
title: "Agentic Code Review Architecture With Tool-Calling"
description: "Move code review from static diff analysis to an agentic architecture that uses tool-calling to gather repository context for deeper reviews."
tags:
  - testing-verification
  - code-review
  - copilot
aliases:
  - "Agentic Code Review"
  - "Tool-Calling Code Review"
---

# Agentic Code Review Architecture

> Agentic code review replaces static diff analysis with a tool-calling architecture where the reviewer actively explores the repository, producing reviews that understand how changes fit the larger codebase.

## The Shift

Traditional AI code review operates on the diff alone — the reviewer sees changed lines without surrounding architectural context. Agentic code review replaces this with a tool-calling architecture where the reviewer actively explores the repository, reads linked issues, traces dependencies, and examines directory structure before generating feedback.

GitHub Copilot code review made this shift in [October 2025 (public preview)](https://github.blog/changelog/2025-10-28-new-public-preview-features-in-copilot-code-review-ai-reviews-that-see-the-full-picture/) and [March 2026 (GA)](https://github.blog/changelog/2026-03-05-copilot-code-review-now-runs-on-an-agentic-architecture/), enabling reviews that comment on architectural impact, pattern violations, and cross-cutting concerns — not just line-level syntax.

## How Agentic Review Works

### Tool-Calling for Context Gathering

The reviewer uses [agentic tool-calling to gather full project context, including code, directory structure, and references](https://github.blog/changelog/2025-10-28-new-public-preview-features-in-copilot-code-review-ai-reviews-that-see-the-full-picture/). The agent dynamically retrieves whatever it needs to understand how changes fit within the broader architecture.

This means the reviewer can:

- Read files outside the diff to understand call sites, interfaces, and dependencies
- Examine directory structure to verify new files follow project conventions
- Read linked issues and PRs to identify [subtle gaps where code appears sound in isolation but misaligns with project requirements](https://github.blog/ai-and-ml/github-copilot/60-million-copilot-code-reviews-and-counting/)

### Hybrid LLM and Deterministic Analysis

The system [blends LLM detections and tool-calling with deterministic tools like ESLint and CodeQL](https://github.blog/changelog/2025-10-28-new-public-preview-features-in-copilot-code-review-ai-reviews-that-see-the-full-picture/). This hybrid approach combines:

- **LLM analysis** — semantic understanding, pattern recognition, architectural judgment
- **Deterministic tools** — CodeQL for security analysis, ESLint for style and rule enforcement

Together they deliver high-signal findings across security and code quality.

### Strategic Review Planning

For complex PRs, the agent [maps out its review strategy ahead of time](https://github.blog/ai-and-ml/github-copilot/60-million-copilot-code-reviews-and-counting/), improving performance on long pull requests where context is easily lost. This prevents the failure mode of the previous architecture, which would [finalize results at the end of a review, often "forgetting" early discoveries](https://github.blog/ai-and-ml/github-copilot/60-million-copilot-code-reviews-and-counting/), catching problems as it reads rather than at completion.

## Measured Impact

The agentic architecture produced an [8.1% increase in positive developer feedback](https://github.blog/ai-and-ml/github-copilot/60-million-copilot-code-reviews-and-counting/) despite increased review latency — [a deliberate trade-off the team describes as worthwhile because meaningful analysis requires computation time](https://github.blog/ai-and-ml/github-copilot/60-million-copilot-code-reviews-and-counting/).

The system maintains [cross-review memory](https://github.blog/ai-and-ml/github-copilot/60-million-copilot-code-reviews-and-counting/), enabling pattern recognition across pull requests rather than treating each as isolated — so flagging a pattern in one section can inform future reviews of the same codebase.

## Architectural Implications

Any AI code review system benefits from the same structural shift:

1. **Give the reviewer tools, not just data.** A reviewer with access to file reading, search, and dependency tracing produces more accurate findings than one that only sees the diff.
2. **Blend analysis methods.** Use LLMs for judgment-requiring issues (architectural fit, naming quality, design patterns) and deterministic tools for rule-based issues (security patterns, style violations, type errors).
3. **Plan before reviewing.** For large PRs, have the agent scan the overall change scope and create a review strategy before examining individual files — preventing early findings from being forgotten.
4. **Read beyond the diff.** The most valuable comments come from understanding how changed code interacts with unchanged code — call sites, shared interfaces, and test coverage of affected paths.

## Operational Considerations

Agentic code review requires compute infrastructure for tool-calling loops. GitHub's implementation requires [self-hosted runners for organizations that opted out of GitHub-hosted runners](https://github.blog/changelog/2026-03-05-copilot-code-review-now-runs-on-an-agentic-architecture/). Custom implementations must account for added latency and cost from multiple tool calls per review.

As of March 2026, reviews can be [triggered from the GitHub CLI](https://github.blog/changelog/2026-03-11-request-copilot-code-review-from-github-cli/) via `gh pr edit --add-reviewer @copilot` or by selecting Copilot during `gh pr create` (requires CLI 2.88.0+). See [Copilot CLI Agentic Workflows](../tools/copilot/copilot-cli-agentic-workflows.md) for details.

## When This Backfires

Agentic code review adds overhead that can outweigh its benefits in several conditions:

- **Small or trivial PRs** — a tool-calling review loop has fixed startup latency that exceeds the value added on single-file or typo-fix PRs. Static diff review is faster and sufficient.
- **Latency-sensitive pipelines** — teams running sub-minute CI gates will find agentic review's multi-tool round-trips incompatible with their merge velocity targets; the 8.1% quality gain does not compensate for a blocked pipeline.
- **Self-hosted runner constraints** — GitHub's implementation requires self-hosted runners for organizations that have opted out of GitHub-hosted runners; teams without that infrastructure cannot adopt the feature without operational changes.
- **Over-reaching architectural comments** — the agent's broader context access can produce low-signal comments on code that is intentionally isolated or handled by conventions the agent does not know; without a custom review persona tuned to project norms, false positives increase reviewer fatigue.

## Example

A pull request modifies a shared authentication helper used by six services. With static diff review, the AI sees only the changed lines in the helper and comments on syntax and naming. With agentic review, the workflow looks like:

1. **Context gathering** — the agent reads the helper file, then calls file-read tools on each of the six services that import it, examining how each consumes the interface being changed.
2. **Issue linkage** — the agent reads the linked issue to understand the intended behavior change versus what the diff actually implements.
3. **Review strategy** — before commenting, the agent maps the full change scope: modified interface, affected call sites, related tests, and existing documentation.
4. **Findings** — the agent surfaces that three of the six services rely on the old return shape; it flags this as a breaking change the diff-only view would miss, and references the specific call sites by file and line.

The same PR with GitHub Copilot's agentic review can be triggered from the CLI: `gh pr edit --add-reviewer @copilot`. The agent runs in a loop, calling tools to gather context before posting inline comments.

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
- [Review-Then-Implement Loop](review-then-implement-loop.md)
- [Committee Review Pattern](committee-review-pattern.md)
- [Context Engineering](../context-engineering/context-engineering.md)
- [Agent-Authored PR Integration](agent-authored-pr-integration.md)
- [Diff-Based Review Over Output Review](diff-based-review.md)
- [Predicting Reviewable Code](predicting-reviewable-code.md)
- [Tiered Code Review](tiered-code-review.md)
- [PR Description Style as a Lever for Agent PR Merge Rates](pr-description-style-lever.md)
- [Human-AI Review Synergy](human-ai-review-synergy.md)
- [Agent PR Volume vs. Value](agent-pr-volume-vs-value.md)
- [CRA-Only Review and the Merge Rate Gap](cra-merge-rate-gap.md) — merge rate evidence for CRA-only versus mixed reviewer compositions
