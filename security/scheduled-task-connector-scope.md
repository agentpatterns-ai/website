---
title: "Connector Scope on a Scheduled Task: Capability Nobody Asked For"
term: "Scheduled-Task Connector Scope"
description: "A cloud scheduled task gets every connected connector by default, which can exceed what its prompt needs. Check the list at creation, and audit the fleet for later drift."
tags:
  - security
  - claude
aliases:
  - routine connector scope
  - inherited connectors on a scheduled task
  - request scope versus grant scope
last_reviewed: 2026-11-05
maturity: emerging
---

# Connector Scope on a Scheduled Task: Capability Nobody Asked For

> A Claude Code cloud scheduled task includes all currently connected connectors by default. Review its connector list at creation and after edits.

A Claude Code cloud scheduled task can include connectors its prompt does not need. The docs say so directly: "When you create a scheduled task, all of your currently connected connectors are included by default. Remove any that aren't needed to limit which tools Claude has access to during the run" ([Routines, Claude Code docs](https://code.claude.com/docs/en/routines#connectors)). Claude Code 2.1.317 adds a signal at this moment: "a warning to `/schedule` when a new cloud scheduled task gets connectors you did not ask for, with how to remove them" ([changelog](https://code.claude.com/docs/en/changelog#2-1-317)).

## Why the extra connector matters

An included connector can permit writes. The web creation instructions state: "Claude can use an included connector during a run, including writes" ([Routines](https://code.claude.com/docs/en/routines)). The docs describe three relevant properties:

| Property | Source text ([Routines](https://code.claude.com/docs/en/routines)) |
|---|---|
| Acts as you | "Anything a scheduled task does through your connected GitHub identity or connectors appears as you." |
| Classifier in auto mode | "In auto mode, a classifier model allows or blocks actions that would otherwise wait for your approval." |
| Network policy does not narrow it | "MCP connector traffic is routed through Anthropic's servers rather than that path" |

Auto mode can still pause for approval, including for an `ask` rule or repeated classifier blocks. The environment allowlist does not restrict connector hosts. In the same paragraph, the routines docs send you to the connector list instead, to remove the connectors you don't need ([Routines](https://code.claude.com/docs/en/routines)). Which identity the run uses is a separate question, covered in [Whose Permissions a Self-Scheduled Agent Run Carries](self-scheduled-run-authority.md).

## Two controls, and what each misses

Review the connector list when you create a task and when you edit it. The docs allow changes to both the prompt and connectors through the edit dialog ([Routines](https://code.claude.com/docs/en/routines#edit-and-control-scheduled-tasks)). A later prompt edit can change which connectors the task needs.

For existing tasks, compare each prompt with its connector list. Each task's detail page "shows the task's repositories, connectors, prompt, schedule, API tokens, GitHub triggers, and a list of past runs". Use `/schedule update` to change the task ([Routines](https://code.claude.com/docs/en/routines#manage-scheduled-tasks-from-the-cli)).

Prioritize removing unneeded write-capable connectors. OWASP recommends avoiding write permissions when an extension only needs to read data ([Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)).

## Why it works

The saved connector list controls which account connectors the task can use. You can edit that list after creation ([Routines](https://code.claude.com/docs/en/routines#connectors)). OWASP's LLM06:2025 names the resulting state: an agent "has access to extensions which include functions that are not needed for the intended operation of the system" ([Excessive Agency, OWASP](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)). Its first mitigation is to "Limit the extensions that LLM agents are allowed to call to only the minimum necessary."

GitHub Actions shows the opposite construction. A `GITHUB_TOKEN` starts at "the default setting for the enterprise, organization, or repository", but "If you specify the access for any of these permissions, all of those that are not specified are set to `none`" ([Workflow syntax, GitHub Docs](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)). Declaring one scope drops the rest, so the grant follows the declaration.

## When this backfires

- Warning design matters. Akhawe and Felt observed "over 25 million warning impressions" in browsers. Users continued through 70.2% of Chrome SSL warnings. Rates for the other warning categories ranged from a tenth to a third. They conclude that "the user experience of a warning can have a significant impact on user behavior" ([USENIX Security 2013](https://www.usenix.org/conference/usenixsecurity13/technical-sessions/presentation/akhawe)). Separately, Claude Code 2.1.317's connector warning includes removal instructions ([changelog](https://code.claude.com/docs/en/changelog#2-1-317)).
- Over-pruning can leave work incomplete despite a Succeeded status. That status means the session ended without a reported failure. The docs place "missing connector tools, and work Claude couldn't complete" in the transcript rather than the status row ([Routines](https://code.claude.com/docs/en/routines#view-and-interact-with-runs)).
- A task can also start with no connectors. Release 2.1.268 made Claude flag this during conversational creation and explain how to add them ([changelog](https://code.claude.com/docs/en/changelog#2-1-268)). That entry does not explain the default-inclusion policy.

## Example

The routines docs give this CLI creation example:

```text
/schedule daily PR review at 9am
```

Claude collects the same information as the web dialog and saves the task to your account ([Routines](https://code.claude.com/docs/en/routines#create-from-the-cli)). Review the included connectors and remove those the review does not need. For a saved task, use `/schedule update` to change the configuration ([Routines](https://code.claude.com/docs/en/routines#manage-scheduled-tasks-from-the-cli)). After changing its prompt or connectors, open a run's transcript to check completion; Succeeded alone does not establish that the work finished.

## Key Takeaways

- Review a task's connector list as a permission grant. Tightening the environment's network access does not shrink it.
- Recheck connector needs when the prompt changes. Include saved tasks in periodic permission reviews.
- Cut write-capable connectors the prompt never names first. When you trim, check that the prompt does not need what you removed, because Succeeded does not establish task completion.
- When you build a new scheduled surface, copy the GitHub `permissions` construction: naming one scope should drop every scope left unnamed.

## Related

- [Whose Permissions a Self-Scheduled Agent Run Carries](self-scheduled-run-authority.md) — the identity a scheduled run spends, where this page covers which capabilities it holds
- [Cloud-Scheduled Routines vs Local Session Scheduling](../tools/claude/cloud-scheduled-routines.md) — routine mechanics, including the trifecta risk when a routine pairs private-data and egress connectors
- [Per-Agent Capability Stores Beat One Task-Wide Allowlist](per-agent-capability-scoping.md) — why a union grant hands every subtask's reach to whichever step reads poisoned input
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md) — the general least-privilege case for agent tool access
- [Lethal Trifecta Threat Model for AI Agent Development](lethal-trifecta-threat-model.md) — what an unneeded egress connector completes
