---
title: "Feature List Files for Reliable AI Agent Development"
description: "Maintain a structured JSON file defining every feature with status and acceptance criteria; agents work through it sequentially and may not mark a feature complete without satisfying its criteria."
tags:
  - agent-design
  - testing-verification
  - instructions
aliases:
  - feature spec file
  - feature contract
---

# Feature List Files

> Maintain a structured JSON file defining every feature with status and acceptance criteria; agents work through it sequentially and may not mark a feature complete without satisfying its criteria.

## The Problem with Agent Self-Report

Agents left to self-report progress are optimistic. [Anthropic's harness post](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) documents a specific failure mode: "after some features had already been built, a later agent instance would look around, see that progress had been made, and declare the job done." Without an external contract, an agent marks a feature complete based on whether its implementation looks plausible — not whether it actually passes acceptance criteria. This produces partially implemented work labeled as done, which compounds across multi-session projects.

A machine-readable feature list with explicit pass/fail status replaces self-report with a verifiable contract. Per [Anthropic's effective harnesses post](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents), this structure is the foundation of reliable long-running agent work.

## Structure

Each feature entry includes:

```json
{
  "id": "feature-42",
  "description": "User can reset password via email link",
  "status": "failing",
  "acceptance_criteria": [
    "POST /auth/reset-request returns 200 with valid email",
    "Reset link expires after 1 hour",
    "Password changed successfully via link"
  ]
}
```

All features start with `status: "failing"`. The agent cannot change status to `passing` unless the acceptance criteria are met.

## Agent Contract

The system prompt makes the feature list the system of record. This aligns with [LangChain's harness engineering findings](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/): "the more that agents know about their environment, constraints, and evaluation criteria, the better they can autonomously self-direct their work."

- Work through features in priority order
- Select the highest-priority failing feature
- Implement it, run verification, and check each criterion
- Update status to `passing` only when all criteria pass
- Commit and move to the next feature

The explicit instruction from [Anthropic's harness post](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) is blunt: "it is unacceptable to remove or edit tests because this could lead to missing or buggy functionality." This rule must appear verbatim in the agent's instructions.

## Validation Strategy

Unit tests alone are insufficient for many feature validations. As the [Anthropic harness post](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) observed: "Claude tended to make code changes, and even do testing with unit tests or `curl` commands against a development server, but would fail to recognize that the feature didn't work end-to-end." [Browser automation](../tool-engineering/browser-automation-for-research.md) (Playwright, Puppeteer) validates user-facing features the way a human user would — navigating UI flows, submitting forms, checking rendered output.

The acceptance criteria in each feature entry should specify which validation method applies: automated test suite, browser automation, or both.

## The Feature List as Cross-Session State

The feature list is the primary source of truth for multi-session progress. At the start of each session, the agent reads:

1. The feature list — what is passing, what is failing, what is next
2. `git log` — what was committed in prior sessions
3. Progress notes — any blockers or context from previous sessions

This triad replaces context window memory. The feature list does not forget, does not optimistically round up, and does not lose information when context is compacted.

## Scale

[Anthropic's harness post](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) documents using 200+ features defined upfront, with all initial statuses set to failing. At this scale, the feature list becomes a project management artifact as well as an agent contract — it shows scope, progress, and remaining work in a format both agents and humans can read.

## When This Backfires

Feature list files add overhead that outweighs the benefit in several situations:

- **Exploratory or greenfield work**: when requirements are unknown upfront, writing acceptance criteria before any implementation forces premature specification. The list becomes a fiction that diverges from what actually gets built.
- **Short single-session tasks**: for a task completing in one session with no state continuity needed, a feature list is unnecessary scaffolding. The agent's own working memory is sufficient.
- **Criteria that can be gamed**: acceptance criteria defined as command outputs can be satisfied by hardcoding responses. A poorly designed criterion (`task list` shows a checkmark) can be met without the underlying feature working correctly — the list gives false confidence rather than genuine verification.

## Example

A CLI task-management app uses a feature list to drive a multi-session agent build. The file `features.json` is committed to the repo root:

```json
[
  {
    "id": "feat-1",
    "description": "Create a task with title and due date",
    "status": "failing",
    "acceptance_criteria": [
      "Running `task add 'Buy milk' --due 2025-04-01` creates a task in tasks.db",
      "Running `task list` shows the new task with its due date"
    ]
  },
  {
    "id": "feat-2",
    "description": "Mark a task as complete",
    "status": "failing",
    "acceptance_criteria": [
      "Running `task done 1` sets task 1 status to complete in tasks.db",
      "Running `task list` shows task 1 with a checkmark"
    ]
  },
  {
    "id": "feat-3",
    "description": "Filter tasks by status",
    "status": "failing",
    "acceptance_criteria": [
      "Running `task list --status=pending` shows only incomplete tasks",
      "Running `task list --status=done` shows only completed tasks"
    ]
  }
]
```

The system prompt references the file directly:

```text
You are building a CLI task manager. Your contract is features.json in the repo root.

1. Read features.json at the start of every session.
2. Select the highest-priority feature with status "failing".
3. Implement it, then run the acceptance criteria as shell commands.
4. Only set status to "passing" if every criterion succeeds.
5. Commit the code and the updated features.json together.
6. It is unacceptable to remove or edit tests because this could lead to missing or buggy functionality.
```

After the agent completes feat-1, the file updates in place — `feat-1` moves to `"status": "passing"` and the agent proceeds to feat-2. A new session reads the same file and picks up exactly where the previous session stopped.

## When This Backfires

- **Exploratory or greenfield work**: When requirements are unknown upfront, defining all features before implementation forces premature commitment. The feature list becomes a fiction that the agent satisfies formally while missing the actual goal — criteria pass but the product is wrong.
- **Criteria that can be gamed**: Acceptance criteria like "page loads without errors" or "API returns 200" can be satisfied trivially without implementing real functionality. Agents optimize for the letter of the criteria, not the intent. Weak criteria produce false confidence.
- **Feature list staleness**: In fast-moving projects, requirements shift mid-build. A static feature list accumulates entries that no longer reflect what the project needs. The agent dutifully implements outdated features while the actual priorities diverge. Without a human reviewing and updating the list between sessions, it drifts from reality.
- **Scale without decomposition**: At 200+ features, a flat list with no grouping or dependency ordering forces the agent to implement features that depend on unbuilt prerequisites. Priority order alone does not capture dependency graphs — the agent may attempt feature 47 before the infrastructure from feature 12 exists.

## Key Takeaways

- All features start as failing; agents cannot self-promote status without passing acceptance criteria
- The prohibition on editing or removing tests must be explicit in the system prompt
- Use browser automation alongside unit tests for user-facing feature validation
- The feature list is the cross-session source of truth — not git log or agent self-report
- Define features upfront with end-to-end descriptions before any implementation begins

## Related

- [Agent Harness](../agent-design/agent-harness.md)
- [Pre-Completion Checklists](../verification/pre-completion-checklists.md)
- [Specification as Prompt](specification-as-prompt.md)
- [Incremental Verification](../verification/incremental-verification.md)
- [Frozen Spec File](frozen-spec-file.md)
- [WRAP Framework Agent Instructions](wrap-framework-agent-instructions.md)
- [AGENTS.md as Table of Contents](agents-md-as-table-of-contents.md)
- [Layered Instruction Scopes](layered-instruction-scopes.md)
