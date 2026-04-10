---
title: "Dependabot Agent Assignment for AI-Driven Vulnerability Remediation"
description: "Route Dependabot alerts to GitHub Copilot for autonomous fix generation, with human review at the merge gate."
tags:
  - copilot
  - workflows
  - security
---

# Dependabot Agent Assignment

> Route Dependabot alerts to GitHub Copilot for autonomous fix generation, with human review at the merge gate.

## How It Works

GitHub's Dependabot alerts surface vulnerable dependencies. Each alert now accepts an assignee — a collaborator, team, or `@copilot`. Assigning to Copilot triggers a different path than assigning to a human: instead of sending a notification, GitHub invokes the [Copilot coding agent](coding-agent.md) to generate a fix and open a draft pull request.

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

## Alert Routing

Not every alert is a good candidate for agent assignment. Two mechanisms filter the queue before a human decides what to delegate:

**Auto-triage rules** dismiss low-risk alerts automatically — before they appear in the queue. Rules can match on CVSS score, EPSS percentage, dependency scope (development vs. production), and whether a patch is available. Alerts that pass through become candidates for assignment.

**Manual triage** decides which passing alerts to assign to the agent vs. a human. The decision turns on the fix complexity:

| Alert type | Agent assignment | Reason |
|------------|-----------------|--------|
| Version bump with available patch | Good fit | Mechanical change, verifiable by tests |
| Transitive dependency update | Good fit | No application code changes required |
| Advisory requiring code changes | Human review first | Business logic impact, needs contextual judgment |
| No patch available | Not applicable | Agent cannot fix what doesn't exist |

Use the Security Overview filter `assignee:@copilot` to track which alerts are in-flight with the agent across repositories.

## Trust Boundaries

The assignment model enforces two controls that bound agent autonomy:

1. **Write access gate** — only users with write/maintain/admin permissions can assign an alert to the agent. Anonymous or read-only collaborators cannot trigger fix generation.

2. **Draft PR review** — the agent opens a draft, not a ready-to-merge PR. A human must inspect the diff, verify test coverage, and explicitly approve before merging. The agent cannot bypass this gate.

This positions agent assignment inside the [human-in-the-loop](../../security/defense-in-depth-agent-safety.md) boundary: autonomous execution, mandatory human verification.

## Example

In the Dependabot alerts tab, open any alert with an available patch. Use the **Assignees** dropdown in the alert details panel to select **Copilot** ([full steps](https://docs.github.com/en/code-security/how-tos/manage-security-alerts/manage-dependabot-alerts/viewing-and-updating-dependabot-alerts#viewing-and-prioritizing-dependabot-alerts)). The alert list updates to show `@copilot` as the assignee and the agent begins generating the fix.

To track all agent-assigned alerts across an organization's repositories in Security Overview:

```
assignee:@copilot is:open
```

This query surfaces all open Dependabot alerts currently delegated to the agent, enabling progress monitoring without opening individual repositories.

## Key Takeaways

- Assigning a Dependabot alert to `@copilot` replaces a manual notification with autonomous fix generation
- Auto-triage rules reduce the assignment queue by dismissing low-risk alerts before they surface
- The draft PR model keeps a human at the merge gate — the agent executes, but cannot ship
- Risk-based routing (version bumps and transitive updates to agent; logic-impacting advisories to humans) maximises throughput while preserving review quality

## Unverified Claims

- Plan tier requirements for agent assignment (GitHub Advanced Security, Copilot Enterprise, or all paid Copilot plans) [unverified — feature flag `dependabot-alerts-assignees` gating not confirmed in public pricing docs]
- Whether the agent uses the same ephemeral GitHub Actions runner as the standard Copilot coding agent [unverified]

## Related

- [Copilot Coding Agent](coding-agent.md)
- [GitHub Agentic Workflows](github-agentic-workflows.md)
- [Defense-in-Depth Agent Safety](../../security/defense-in-depth-agent-safety.md)
- [Safe Outputs Pattern](../../security/safe-outputs-pattern.md)
