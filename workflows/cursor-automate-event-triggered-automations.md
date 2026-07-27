---
title: "Cursor Automations: Event-Triggered Agents and /automate"
term: "Cursor /automate Skill"
description: "Cursor 3.8's /automate, Slack-emoji and GitHub-event triggers, and default-on computer-use ship a usable event-dispatch surface only when the trifecta is bounded first."
tags:
  - workflows
  - agent-design
  - automation
  - cursor
  - security
aliases:
  - cursor automate skill
  - cursor event triggered automations
  - cursor slack emoji trigger
last_reviewed: 2026-06-29
maturity: emerging
---

# Cursor Automations: Event-Triggered Agents and /automate

> Cursor 3.8's expanded trigger surface and natural-language authoring make event-driven automations cheap to ship — and cheap to ship with the lethal trifecta closed.

Cursor 3.8 (2026-06-18) turns Cursor Automations from a scheduled-job surface into an event-driven dispatch system through four changes: a `/automate` skill that authors automations from plain language, five new GitHub event triggers, a Slack emoji-reaction trigger, and computer-use enabled by default for the cloud agent that runs each automation ([Cursor changelog 06-18-26](https://cursor.com/changelog/06-18-26)). That makes it the Cursor-specific instance of the event-driven dispatch family already documented across [Continuous AI](continuous-ai.md), [Chat-Platform Agent Delegation](chat-platform-agent-delegation.md), and [Programmatic Cloud-Agent Dispatch](programmatic-cloud-agent-dispatch.md) — safe to adopt only once the new surfaces are bounded and the defaults that concentrate the [lethal trifecta](../security/lethal-trifecta-threat-model.md) are closed first.

## When to use this trigger surface

Adopt the 3.8 trigger surface only when all four conditions hold. If any one is missing, stay on a scheduled trigger or a manual dispatch path until the gap is closed.

| Condition | Why it is load-bearing |
|-----------|----------------------|
| The triggering principal is bounded | A Slack emoji from any public-channel member or an issue comment from any repo participant becomes a dispatch authority. Cursor restricts the Slack trigger to public channels and gates fork PRs explicitly ([Cursor docs](https://cursor.com/docs/cloud-agent/automations)) — every other principal-bound surface is the team's responsibility. |
| The automation's instructions live in a reviewed file | `/automate` drafts triggers, instructions, and tools from a natural-language description. Without a checked-in instruction file, no one but the author has seen what the automation actually does before it goes live ([Cursor changelog 06-18-26](https://cursor.com/changelog/06-18-26)). |
| The computer-use tool is scoped or removed | The cloud agent that runs an automation now ships with computer-use enabled by default ([Cursor changelog 06-18-26](https://cursor.com/changelog/06-18-26)). The Cursor docs describe computer-use as the ability to "operate a browser, produce screenshots or recordings, or use your internal services" ([Cursor docs](https://cursor.com/docs/cloud-agent/automations)) — arbitrary egress to anything the cloud sandbox can reach. |
| A lethal-trifecta audit has been run on the trigger | The trigger surface is broad enough that the audit must happen per trigger type, not once per team. The same audit posture this site applies to MCP servers and chat-platform principals (see [Lethal Trifecta Threat Model](../security/lethal-trifecta-threat-model.md)) applies here. |

## The 3.8 trigger surface

The 3.8 release adds three trigger families and a default-on tool. Each maps to a failure condition that the dispatch-family pages on this site already document.

## New trigger channels: Slack emoji and GitHub events

### Slack emoji reaction

Reacting to any Slack message with a designated emoji fires the automation ([Cursor changelog 06-18-26](https://cursor.com/changelog/06-18-26)). The trigger fires only on public channels — private channels are not visible to automations ([Cursor docs](https://cursor.com/docs/cloud-agent/automations)). That restriction blocks one principal class but leaves a more common one open: any member of a public channel — including a Slack Connect external participant — is a valid dispatcher.

The failure mode is the trifecta concentration the [Chat-Platform Agent Delegation](chat-platform-agent-delegation.md) page already covers, now extended to a reaction surface that no longer requires an `@mention`. A single reaction is enough to dispatch.

### Five new GitHub triggers

The release adds: issue comment, PR review comment, PR review submitted, review thread updated, and workflow run completed ([Cursor changelog 06-18-26](https://cursor.com/changelog/06-18-26)). Cursor ships templates that pair these with auto-fix-PR-review-comments and triage-failed-workflows ([Cursor changelog 06-18-26](https://cursor.com/changelog/06-18-26)).

PR triggers from forks are blocked at the trigger level — Cursor cites the risk of executing external code with repo permissions ([Cursor docs](https://cursor.com/docs/cloud-agent/automations)). The remaining triggers fire on principals that are repo-internal but not necessarily author-internal. The issue-comment trigger feeding an auto-fix template is the OWASP LLM01:2025 indirect-injection case verbatim: an attacker who can comment on an issue can plant instructions that flow into the agent prompt ([OWASP](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)).

The workflow-run-completed trigger paired with an auto-fix template on a flaky build is the webhook-retry-storm shape from [Programmatic Cloud-Agent Dispatch](programmatic-cloud-agent-dispatch.md) — every failed run dispatches a new agent. Without a per-trigger budget cap, a flaky workflow drains the team's AI Credit allotment.

## Default-on tooling changes: computer-use and /automate authoring

### Computer-use default-on

The cloud agent kicked off by an automation now has access to its own computer "to produce demos or artifacts of their work," enabled by default ([Cursor changelog 06-18-26](https://cursor.com/changelog/06-18-26)). The Cursor docs scope this as "operate a browser, produce screenshots or recordings, or use your internal services" ([Cursor docs](https://cursor.com/docs/cloud-agent/automations)).

For an automation triggered by trusted content (a scheduled job, a PR your team authored), computer-use is a useful artifact generator. For an automation triggered by untrusted content (a Slack emoji, an issue comment), it broadens the egress leg of the trifecta to arbitrary browsing — the third leg now reaches beyond the forge API to anything the cloud sandbox can render.

### `/automate` authoring

The new in-session `/automate` skill takes a plain-language task description and Cursor configures the trigger, instructions, and tools ([Cursor changelog 06-18-26](https://cursor.com/changelog/06-18-26)). The mechanism is lowered authoring cost: an automation that would not have been worth wiring through the dashboard now ships in one prompt. Cursor frames the problem this addresses as the asymmetric scaling of code review, monitoring, and maintenance against code production ([Cursor blog](https://cursor.com/blog/automations)).

The cost is a review-deficit: the trigger picked, the tools attached, and the team-versus-private scope chosen are model decisions made from free-text input, not configuration committed to source. The Cursor Automations docs warn explicitly that "Memories...should be used with caution if your automation handles untrusted input. Inputs may lead to misleading or malicious memories" ([Cursor docs](https://cursor.com/docs/cloud-agent/automations)) — the same caution applies to the trigger that `/automate` selects from an unreviewed prompt.

## Why it works

The mechanism is the same one that fires every always-on agent loop on this site: event triggers replace the human typing step with a signal the team already produces. The asymmetric-scaling framing Cursor's blog uses — "code review, monitoring, and maintenance haven't sped up to the same extent" as code production ([Cursor blog](https://cursor.com/blog/automations)) — is the same mechanism the [Continuous AI](continuous-ai.md) family captures and that [Programmatic Cloud-Agent Dispatch](programmatic-cloud-agent-dispatch.md) makes explicit at the API level.

Where 3.8 differs is in lowering the authoring cost. The `/automate` skill collapses trigger selection, instruction drafting, and tool wiring into one natural-language step — the marginal automation that would not have justified the dashboard configuration now ships. The four implicit safeguards a human dispatcher provided in the manual-mention case (dedupe, payload sanitization, budget caps, audit attribution) must be reconstructed at the automation level, and the natural-language authoring path makes it easier to ship the automation before those safeguards exist ([Multi-Repo and No-Repo Automation Templates](multi-repo-no-repo-automation-templates.md)).

## When this backfires

| Failure | Concrete shape |
|---------|--------------|
| Slack-emoji trigger fires from any public-channel member | A reaction from any channel member — including a Slack Connect external participant — dispatches the automation. With computer-use default-on, the lethal trifecta closes on a single reaction. The Slack-public-channel restriction blocks one principal class and creates a false sense of bounded exposure. |
| Issue-comment trigger reads untrusted body into prompt | An attacker who can comment on an issue plants instructions into the agent's prompt — the OWASP LLM01:2025 indirect-injection case ([OWASP](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)). Cursor flags the memory-poisoning shape of this in the docs ([Cursor docs](https://cursor.com/docs/cloud-agent/automations)) but does not gate the trigger by default. |
| Workflow-run-completed trigger plus auto-fix template on a flaky build | Every failure dispatches a new agent. Without a per-trigger budget cap, a flaky workflow drains the team's AI Credit allotment — the same retry-storm shape [Programmatic Cloud-Agent Dispatch](programmatic-cloud-agent-dispatch.md) calls out for webhook triggers. |
| `/automate` picks a trigger and scope from free-text input | The mapping from a natural-language description to a Cursor configuration is a model decision. Different team members issuing the same `/automate` request can produce automations with different triggers, scopes, and tools. Without a checked-in instruction file, no one but the author has reviewed what runs. |
| Computer-use default-on for an untrusted-content trigger | The egress leg of the trifecta widens from "post a PR" to "operate a browser, use internal services" ([Cursor docs](https://cursor.com/docs/cloud-agent/automations)). For an automation triggered by trusted content this is a feature; for one triggered by a Slack emoji it is arbitrary browsing under a service-account principal. |

## Key Takeaways

- Cursor 3.8 expands automations from scheduled jobs to event-driven dispatch: five new GitHub triggers, a Slack emoji-reaction trigger, and the `/automate` skill for natural-language authoring ([Cursor changelog 06-18-26](https://cursor.com/changelog/06-18-26)).
- The 3.8 defaults — public-channel emoji trigger, untrusted-content GitHub triggers, computer-use enabled by default — concentrate the lethal trifecta on the automation principal unless the team bounds each leg explicitly.
- `/automate` lowers authoring cost but widens the review-deficit: the trigger and scope picked from a natural-language prompt are model decisions, not source-controlled configuration.
- The mechanism Cursor cites — asymmetric scaling of review/monitoring/maintenance versus code production — is the same one the [Continuous AI](continuous-ai.md) family already documents tool-agnostically; 3.8 is the Cursor-specific worked example.
- Adopt the new triggers only after a lethal-trifecta audit on the trigger principal and a checked-in instruction file for what the automation actually does.

## Related

- [Continuous AI](continuous-ai.md) — the navigation map of always-on agent workflows this trigger surface sits inside
- [Chat-Platform Agent Delegation](chat-platform-agent-delegation.md) — the trifecta-concentration posture extended by the Slack emoji trigger
- [Programmatic Cloud-Agent Dispatch](programmatic-cloud-agent-dispatch.md) — dedupe, sanitization, budget caps, and audit attribution that 3.8 triggers also require
- [Multi-Repo and No-Repo Automation Templates](multi-repo-no-repo-automation-templates.md) — the trigger/scope decoupling Cursor introduced in 3.5 that 3.8 builds on
- [Lethal Trifecta Threat Model](../security/lethal-trifecta-threat-model.md) — the threat model the 3.8 defaults close by default
