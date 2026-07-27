---
title: "Dependabot Agent Assignment for AI-Driven Vulnerability Remediation"
description: "Assign Dependabot alerts to GitHub Copilot's coding agent so it opens a draft fix PR automatically, keeping human review at the merge gate."
tags:
  - copilot
  - workflows
  - security
applies_to: "copilot@1.x"
last_reviewed: 2026-07-28
status: current
---

# Dependabot Agent Assignment

> Route Dependabot alerts to GitHub Copilot for autonomous fix generation, with human review at the merge gate.

## How it works

Dependabot alerts flag vulnerable dependencies. Each alert now accepts an assignee: a collaborator, a team, or `@copilot`. Assigning to a human sends a notification. Assigning to `@copilot` does something different. GitHub invokes the [Copilot coding agent](coding-agent.md) to generate a fix and open a draft pull request. This needs GitHub Code Security and a Copilot plan that includes coding agent access ([Dependabot agent-assignment changelog](https://github.blog/changelog/2026-04-07-dependabot-alerts-are-now-assignable-to-ai-agents-for-remediation/)).

The workflow:

```mermaid
graph TD
    A[Dependabot Alert] --> B{Assign}
    B -->|Human / Team| C[Notification sent]
    B -->|@copilot| D[Agent generates fix]
    D --> E[Draft PR opened]
    E --> F[Human reviews & merges]
```

Assignment requires write access or higher on the repository. The draft PR requires human review — there is no auto-merge path.

## Alert routing

Not every alert is a good candidate for agent assignment. Two filters narrow the queue before you decide what to delegate:

Auto-triage rules dismiss low-risk alerts automatically, before they reach the queue. GitHub Code Security can match these rules on CVSS score, EPSS percentage, dependency scope (development or production), and whether a patch is available. Alerts that pass become candidates for assignment.

Manual triage decides which of the remaining alerts go to the agent and which go to a human. The fix complexity drives the decision:

| Alert type | Agent assignment | Reason |
|------------|-----------------|--------|
| Version bump with available patch | Good fit | Mechanical change, verifiable by tests |
| Transitive dependency update | Good fit | No application code changes required |
| Advisory requiring code changes | Human review first | Business logic impact, needs contextual judgment |
| No patch available | Not applicable | Agent cannot fix what doesn't exist |

Use the Security Overview filter `assignee:@copilot` to see which alerts the agent is working on across repositories.

## Trust boundaries

Two controls bound the agent's autonomy:

1. Write access gate. Only users with write, maintain, or admin permissions can assign an alert to the agent. Read-only collaborators cannot trigger a fix.

2. Draft PR review. The [Copilot coding agent](coding-agent.md) opens a draft, not a ready-to-merge PR. A human must inspect the diff, check test coverage, and approve before merging. The agent cannot bypass this gate.

This positions agent assignment inside the [human-in-the-loop](../../security/defense-in-depth-agent-safety.md) boundary: autonomous execution, mandatory human verification.

## Example

In the Dependabot alerts tab, open any alert with an available patch. Use the **Assignees** dropdown in the alert details panel to select **Copilot** ([full steps in GitHub's docs](https://docs.github.com/en/code-security/dependabot/dependabot-alerts/viewing-and-updating-dependabot-alerts)). The alert list updates to show `@copilot` as the assignee, and the agent starts generating the fix.

To track all agent-assigned alerts across an organization's repositories in Security Overview:

```
assignee:@copilot is:open
```

This query lists every open Dependabot alert currently delegated to the agent, so you can monitor progress without opening individual repositories.

## When this backfires

Agent assignment degrades or fails in three conditions:

1. No test suite. The agent opens a PR, but without automated tests there is no signal that the dependency bump is safe. Reviewers must exercise the diff by hand, which negates much of the time saving.
2. Complex transitive updates. When a version bump pulls in a chain of transitive upgrades, the agent may resolve conflicts mechanically and miss semantic breakage in nested packages. A human still needs to inspect the full dependency graph.
3. No available patch. The agent cannot synthesize a fix for an advisory that has no upstream patch. Assigning these alerts burns an agent session whose tokens still bill as [GitHub AI credits](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing), and produces a draft PR with no useful changes.

## Key Takeaways

- Assigning a Dependabot alert to `@copilot` replaces a manual notification with autonomous fix generation
- Auto-triage rules reduce the assignment queue by dismissing low-risk alerts before they surface
- The draft PR model keeps a human at the merge gate — the agent executes, but cannot ship
- Risk-based routing (version bumps and transitive updates to agent; logic-impacting advisories to humans) maximizes throughput while preserving review quality

## Related

- [Copilot Coding Agent](coding-agent.md)
- [GitHub Agentic Workflows](github-agentic-workflows.md)
- [Defense-in-Depth Agent Safety](../../security/defense-in-depth-agent-safety.md)
- [Safe Outputs Pattern](../../security/safe-outputs-pattern.md)
