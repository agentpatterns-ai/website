---
title: "Agent Governance Plane: Audit Events and Message-Content Surfaces"
term: "Agent Governance Plane"
description: "The four-part admin surface vendors ship for coding agents, and the two conditions — deployment topology and retention — that decide whether its record can reconstruct what the agents did."
aliases:
  - agent audit event stream
  - agent compliance API
  - enterprise agent governance plane
tags:
  - security
  - observability
  - agent-design
  - tool-agnostic
last_reviewed: 2026-08-29
maturity: emerging
---

# Agent Governance Plane: Audit Events and Message-Content Surfaces

> An agent governance plane answers what the agents did only for traffic that reaches the vendor's boundary; other routes leave no record in it.

Two conditions decide whether a vendor governance plane can reconstruct agent activity: whether your agents reach the vendor's API directly, and whether retention outlasts the interval to detection. Where either fails the plane still returns data, and nothing in the response marks what is missing.

Two vendors now ship the same four parts. Replit's August 2026 enterprise release has audit logs adding "more than 50 new events across deployments, access and identity, workspace administration, project activity, secrets, connectors, domains, and agent activity", an Admin API in beta, Workspace Settings, and a Compliance API to "fetch the full contents of user messages for auditing & compliance" ([Replit: Govern Replit at scale](https://replit.com/blog/new-enterprise-governance-tools)). Anthropic ships the same four parts as an Activity Feed, an Admin and Analytics API, organization settings, and session-transcript endpoints ([Anthropic: Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api)).

## Condition 1: the traffic reaches the vendor

Capture happens where the requests land. "Anthropic records each conversation server-side as its requests reach the Claude API; nothing is installed on the device", so "activity that never reaches the API (for example, local files the session never sent) is not captured" ([Anthropic: Retrieve session transcripts](https://platform.claude.com/docs/en/manage-claude/compliance-sessions)).

Deployment topology, not policy, therefore draws the coverage boundary. The Compliance API returns nothing for Claude Code "authenticated with a Claude Console API key, run through a third-party cloud platform (Amazon Bedrock, Google Cloud, or Microsoft Foundry), or run in Claude Code on the web", nor for local sessions under HIPAA readiness or zero data retention ([Anthropic: Design your compliance integration](https://platform.claude.com/docs/en/manage-claude/compliance-integration-patterns)). An enterprise that standardizes agent access on Bedrock buys a governance plane silent about its largest workload.

## Condition 2: retention outlasts detection

Replit sets "Audit log retention is 30 days by default", with longer retention on request ([Replit](https://replit.com/blog/new-enterprise-governance-tools)). Anthropic retains Activity Feed records and session transcripts for 6 years by default ([Anthropic: Design your compliance integration](https://platform.claude.com/docs/en/manage-claude/compliance-integration-patterns)). Two orders of magnitude separate one feature name, so read the number before you rely on the category.

Turning it on late does not help: recording "begins when the Compliance API is first enabled for your organization, and activity from before enablement is not backfilled" ([Anthropic](https://platform.claude.com/docs/en/manage-claude/compliance-integration-patterns)).

## The four surfaces

| Surface | Answers | Does not answer |
|---|---|---|
| Audit event stream | Who did what, when, from which address, in SIEM-joinable form | Whether the export is complete; the feed is at-least-once and carries no checksum |
| Admin API | Workspace, member, project, and usage state, on a schedule | Per-event history, which the audit stream holds instead |
| Policy settings | What is permitted now, and which teams hold a delegated exception | What was permitted at the time of an incident |
| Message-content endpoint | The prompts, responses, and tool calls of a session | Anything masked, because nothing is |

The vendor documents the completeness gap itself: the feed is "at-least-once", "The list endpoints do not return a `total_count` field or a checksum", and "Activity volume is not a completeness check" ([Anthropic](https://platform.claude.com/docs/en/manage-claude/compliance-integration-patterns)). Your export log is what attests to a complete run.

## Why it works

Policy controls record the decision to permit, not the act. One agent session crosses repositories, tools, identities, and machines, so no repository's history holds the sequence. The platform boundary is the one point every action passes through, so a record built there carries the whole run: a session transcript is "the sequence of user prompts, assistant responses, and tool calls and results in that conversation" ([Anthropic: Retrieve session transcripts](https://platform.claude.com/docs/en/manage-claude/compliance-sessions)). The same mechanism sets the limit. Capture happens as requests reach the API, so the record ends wherever the traffic diverges.

The content endpoint is itself governable: "Calls to the Compliance API itself emit `compliance_api_accessed` activities" ([Anthropic: Design your compliance integration](https://platform.claude.com/docs/en/manage-claude/compliance-integration-patterns)), so a pull of message contents lands in the same stream as everything else and an auditor can be audited.

## When this backfires

- Agents run through Bedrock, Google Cloud, Microsoft Foundry, a Console API key, or the web client. The content endpoints return nothing for those sessions, so an org reading the plane as authoritative concludes the agents were idle ([Anthropic](https://platform.claude.com/docs/en/manage-claude/compliance-integration-patterns)).
- Retention expires before anyone asks. A 30-day default plus a non-retroactive start makes the plane useless for an incident discovered a quarter later.
- Nobody has decided who may pull message contents. "Nothing masks URLs, credentials, or personal data in that content, so treat transcripts as sensitive" ([Anthropic: Retrieve session transcripts](https://platform.claude.com/docs/en/manage-claude/compliance-sessions)). A standing pull of employee prompts discloses every secret a developer pasted into a chat.
- The stream goes to an untuned SIEM. Detection pipelines already suffer where "alert fatigue severely limits security operations effectiveness due to too many false positives or low-impact events" ([arXiv:2605.27299v1](https://arxiv.org/abs/2605.27299v1)), and 50 more event types do not improve that.
- You control the egress path anyway. A gateway every agent already routes through gives one schema, your retention, and the ability to deny a request in flight, which no after-the-fact feed can do. The vendor plane still adds the access-and-identity, secrets, and workspace-administration events a gateway never sees ([Replit](https://replit.com/blog/new-enterprise-governance-tools)), so treat it as a supplement to that chokepoint rather than a replacement for it.

## Example

A platform team enables the plane and writes down what it covers. Terminal and IDE sessions on the enterprise account are captured; the nightly batch jobs on Bedrock are not, so those keep their own gateway logs. The activity feed is polled on a cursor, deduplicated on `id`, and each run logs its starting cursor, terminal `last_id`, record count, and the final page's `request-id`, because the API offers no checksum. Message-content retrieval is restricted to one named compliance reviewer with a separate key, and the `compliance_api_accessed` events are alerted on, so a pull nobody expected is visible the same day. The written gap list is what the team hands its auditor; the integration is the easy half.

## Key Takeaways

- Write down which agent routes the plane cannot see, and keep that list beside the integration. It is the part an auditor will ask about, and the part a dashboard never shows.
- Read the retention number rather than the feature name. Replit defaults to 30 days, Anthropic retains activity for 6 years, and neither backfills the period before you switched capture on.
- Log each export run's cursors, record count, and final `request-id`. The API offers no checksum, so that log is your only evidence a pull was complete.
- Give message-content retrieval its own key and its own named owner, then alert on the events that record each call.

## Related

- [Enterprise Agent Hardening: Three Production Gates](enterprise-agent-hardening.md) — the governance, observability, and reproducibility gates this plane supplies evidence for.
- [Team-Scoped Agent Policy Delegation](team-scoped-policy-delegation.md) — the delegated-exception half of the policy surface, in depth.
- [Tenant Model Policy: Organization-Scoped Rules for AI Model Selection](../patterns/agent-design/tenant-model-policy.md) — the admin-tier model rules the same settings surface carries.
- [Cryptographic Governance Audit Trail](cryptographic-governance-audit-trail.md) — what it takes to make an action log tamper-evident rather than merely present.
- [A Governance Framework for Production Agents](../workflows/governing-production-agents.md) — the cost, control, and compliance axes these surfaces sit inside.
