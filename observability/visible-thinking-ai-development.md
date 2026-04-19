---
title: "Visible Thinking Practices in AI-Assisted Development"
description: "When AI compresses development time, meaningful commits, signal-rich PRs, and structured prompts become the primary quality differentiators."
tags:
  - human-factors
  - workflows
  - observability
---

# Visible Thinking in AI-Assisted Development

> When AI handles production speed, the practices that document reasoning — meaningful commits, signal-rich PRs, and clear branch naming — become the primary quality differentiators.

## The Shift

AI coding tools compress the time between idea and implementation. Code production is no longer the bottleneck. What remains scarce is the reasoning trail: why a decision was made, what alternatives were considered, and what constraints shaped the solution.

Visible thinking — explicit documentation of intent and rationale across the development lifecycle — makes work reviewable, maintainable, and trustworthy. GitHub frames it directly: "Speed and control aren't trade-offs. They reinforce each other" ([GitHub Blog: Speed Is Nothing Without Control](https://github.blog/ai-and-ml/generative-ai/speed-is-nothing-without-control-how-to-keep-quality-high-in-the-ai-era/)).

## Quality Signals Across the Lifecycle

### Issues as Specifications

Capture the problem, success criteria, constraints, and risks in the issue before engaging an agent. A well-structured issue both guides the AI toward the right solution and creates a reviewable record of intent.

### Branch Naming

Use meaningful branch names that convey purpose. When agents generate branches, enforce a convention (e.g., `feature/add-oauth-flask`, `fix/null-check-user-service`) that communicates scope at a glance. Generic names like `agent-fix-1` lose signal.

### Meaningful Commits

Commit messages should narrate reasoning, not just describe changes. Instead of `Added dark mode toggle`, explain the decision: `chose localStorage for persistence to avoid server dependency` ([GitHub Blog: Speed Is Nothing Without Control](https://github.blog/ai-and-ml/generative-ai/speed-is-nothing-without-control-how-to-keep-quality-high-in-the-ai-era/)).

When working with agents, review and rewrite AI-generated commit messages before pushing. The commit log is the permanent reasoning record — it outlasts the chat session that produced the code.

### Signal-Rich Pull Requests

Structure PR descriptions to answer three questions ([GitHub Blog: Speed Is Nothing Without Control](https://github.blog/ai-and-ml/generative-ai/speed-is-nothing-without-control-how-to-keep-quality-high-in-the-ai-era/)):

- **Why**: The problem or opportunity that motivated the change.
- **What changed**: Concrete description of the implementation approach.
- **Trade-offs**: Alternatives considered and reasons for the chosen path.

This structure matters more when AI generates the code, because the reviewer cannot infer reasoning from the implementation alone. The PR description bridges the gap between what the agent produced and why the developer accepted it.

## Structured Prompting as Visible Intent

How you prompt an agent is itself a form of visible thinking. GitHub recommends a structured framework ([GitHub Blog: Speed Is Nothing Without Control](https://github.blog/ai-and-ml/generative-ai/speed-is-nothing-without-control-how-to-keep-quality-high-in-the-ai-era/)):

- **Goals**: State the outcome, not the action ("improve readability while preserving functionality" rather than "refactor this file").
- **Constraints**: Specify boundaries ("no third-party dependencies," "no breaking changes").
- **Context**: Reference related files, architecture decisions, and existing conventions.
- **Output format**: Define the expected shape of the result.

Saving prompts alongside code — in commit messages, PR descriptions, or instruction files — preserves decision context that would otherwise vanish when the chat session ends. This mirrors Anthropic's guidance to "prioritize transparency by explicitly showing the agent's planning steps" ([Anthropic: Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)), and Claude Code best practices recommend checking CLAUDE.md into git so constraints persist across sessions ([Claude Code Best Practices](https://code.claude.com/docs/en/best-practices)).

## Anti-Patterns

- **Accepting defaults**: Merging AI-generated commits and PRs without editing their messages discards the opportunity to document reasoning.
- **Reasoning-free velocity**: Shipping code faster without documenting why it was built that way creates a codebase that is fast to produce and slow to maintain.
- **Opaque agent sessions**: Running agents without recording the prompts, constraints, or goals that shaped the output makes the work unreviewable after the fact.

## Example

The following pair of commit messages illustrates the difference between a default AI-generated message and one rewritten to document reasoning.

```bash
# Default AI-generated commit — describes the change, not the decision
git commit -m "Add dark mode toggle"

# Rewritten to capture reasoning — explains why, what constraint shaped the choice
git commit -m "feat(ui): add dark mode toggle using localStorage

Chose localStorage over a user preference API to avoid adding a server
dependency. Follows the no-new-endpoints constraint from the issue spec."
```

A matching PR description applies the same structure to the pull request body:

```markdown
## Why
Users on low-brightness displays reported eye strain; the issue (#412) set
no-new-endpoints as a hard constraint.

## What changed
- Added `useDarkMode` hook that reads/writes `localStorage('theme')`
- Toggled `data-theme` attribute on `<html>` to drive CSS variables

## Trade-offs
Server-side persistence (so preference follows the user across devices) was
ruled out by the constraint. Accepted trade-off: preference resets on new
devices.
```

The reasoning recorded in the commit and PR outlasts the chat session. A reviewer — or a future maintainer — can reconstruct why `localStorage` was chosen without access to the original prompt.

## When This Backfires

Visible thinking practices assume documentation overhead is recoverable — that is, the time spent writing clear commit messages and PR descriptions costs less than the time saved later in review and maintenance. This breaks down in several situations:

- **Extreme time pressure with short-lived code**: Throwaway scripts, hotfixes with an immediate rollback plan, or spike branches that are deleted after a demo rarely justify detailed commit narration. The reasoning record has no audience.
- **AI-generated documentation accepted uncritically**: When developers prompt agents to generate commit messages and PR descriptions without review, the visible thinking artifacts are present but meaningless — they document what the agent guessed the reasoning was, not the actual constraints and trade-offs.
- **Context saturation in large teams**: As codebases grow and commit volume increases, the signal-to-noise ratio of commit history degrades. Teams that enforce verbose commits without pruning or tagging conventions often find the log unsearchable — the documentation exists but cannot be found.
- **Misaligned tooling**: Repositories using squash-merge strategies collapse all commit reasoning into a single PR description. Branch-level commit discipline is lost, making per-commit narration pointless unless PR descriptions absorb that detail.

## Key Takeaways

- AI shifts the quality bottleneck from code production to reasoning documentation — commit messages, PR descriptions, and issue specifications are where experienced developers add irreplaceable value.
- Structure PR descriptions around why, what changed, and trade-offs to bridge the gap between AI-generated code and human review.
- Treat structured prompts as artifacts worth preserving — they capture the intent and constraints that shaped each implementation decision.

## Related

- [Progressive Autonomy with Model Evolution](../human/progressive-autonomy-model-evolution.md)
- [Agent Transcript Analysis](../verification/agent-transcript-analysis.md)
- [The Plan-First Loop: Design Before Code](../workflows/plan-first-loop.md)
- [Pre-Completion Checklists](../verification/pre-completion-checklists.md)
- [Trajectory Logging and Progress Files](trajectory-logging-progress-files.md)
- [Agent Debugging: Diagnosing Bad Agent Output](agent-debugging.md)
- [Making Observability Legible to Agents](observability-legible-to-agents.md)
- [Agent Observability in Practice: OTel, Cost Tracking, and Trajectory Logging](agent-observability-otel.md)
- [Loop Detection](loop-detection.md)
- [Event Sourcing for Agents: Separating Cognitive Intention from State Mutation](event-sourcing-for-agents.md)
- [PR Description Style as a Lever for Agent PR Merge Rates](../code-review/pr-description-style-lever.md)
