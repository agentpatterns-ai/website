---
title: "Continuous AI: A Navigation Map of Always-On Agent Workflows"
term: "Continuous AI"
description: "A navigation parent for the continuous-* and triage workflow families — each a distinct always-on application with its own trigger, authority, and data source."
tags:
  - workflows
  - agent-design
  - index
  - tool-agnostic
last_reviewed: 2026-08-05
maturity: established
---

# Continuous AI: A Navigation Map of Always-On Agent Workflows

> Continuous AI groups the always-on agent workflows here — each a distinct application with its own trigger, authority, and data source.

Related lesson: [Agents in the Pipeline](https://learn.agentpatterns.ai/workflows/agents-in-the-pipeline/) — this concept features in a hands-on lesson with quizzes.

"Continuous AI" is GitHub's umbrella term for running agents continuously inside a repository on schedules and events, producing reviewable artifacts rather than autonomous commits ([GitHub Blog](https://github.blog/ai-and-ml/generative-ai/continuous-ai-in-practice-what-developers-can-automate-today-with-agentic-ci/)). The pages below share that always-on shape but differ in what fires them, what they are allowed to write, and what they read. This page is a map, not a merge: each member is its own application and stays a separate page.

## The continuous-* family

These workflows run agents on a recurring loop or event stream against a codebase or backlog.

- [Continuous AI (Agentic CI/CD)](continuous-ai-agentic-cicd.md) — agents run alongside CI/CD to handle judgment-heavy tasks deterministic rules cannot express, emitting reviewable PRs and reports.
- [Continuous Documentation](continuous-documentation.md) — agents detect documentation-code drift on schedule or push and open PRs that realign docs.
- [Continuous Agent Improvement](continuous-agent-improvement.md) — an observe-categorize-update-verify loop that keeps AGENTS.md and skills accurate as the project evolves.
- [Continuous Autonomous Task Loop](continuous-autonomous-task-loop.md) — a self-directed loop that reads a backlog, executes each item via a ReAct inner turn, commits, and repeats with fresh context.

## The triage family

These workflows continuously classify and route inbound work — issues, alerts, or security findings.

- [Continuous Triage](continuous-triage.md) — agents summarize, label, and route issues on every event or schedule, with read-only defaults and constrained safe outputs.
- [Auto-Triage Workflow](auto-triage-workflow.md) — a monitor-correlate-investigate-propose-fix agent on alert streams that tags an owner or opens a fix PR, safe only under three named preconditions.
- [Backlog Triage as a Named Agent Skill](backlog-triage-skill.md) — a single skill that encodes a label state machine and emits a durable agent brief as the hand-off contract.
- [AI-Powered Vulnerability Triage](ai-powered-vulnerability-triage.md) — decomposes security analysis into threat-model, suggest, and audit stages to suppress hallucinated findings.

## How to choose

Match the trigger to the family. A schedule or push against your own code points at the continuous-* family. An inbound stream of issues, alerts, or vulnerabilities points at the triage family. Within each family, the distinguishing axis is authority: read-only classification ([continuous triage](continuous-triage.md)), constrained writes behind preconditions ([auto-triage](auto-triage-workflow.md), vulnerability triage), or full PR-producing loops ([agentic CI/CD](continuous-ai-agentic-cicd.md), continuous documentation).

Tooling is converging on a concrete trigger taxonomy for these always-on agents. Cursor's Automations release ships event-triggered agents fired by a Slack emoji reaction, five GitHub events (issue comment, PR review comment, PR review submitted, review-thread updated, and workflow-run completed), and an `/automate` skill for authoring them ([Cursor changelog, 2026-06-18](https://cursor.com/changelog/06-18-26)) — a worked example of the event-stream triggers that distinguish the triage family from the schedule-driven continuous-* loops. GitHub has since shipped comment-triggered automations for Copilot ([GitHub changelog, 2026-08-03](https://github.blog/changelog/2026-08-03-trigger-copilot-automations-with-comments)). Cursor and Copilot now both fire automations from comment events.

## Key Takeaways

- Continuous AI is a *family* of distinct always-on workflows, not one mergeable pattern — each member keeps its own page.
- Two sub-families: the continuous-* loops act on your own code or backlog; the triage family classifies inbound issues, alerts, and findings.
- Choose by trigger first (schedule/push vs. inbound stream), then by authority (read-only, preconditioned writes, or full PR loops).

## Related

- [Workflows index](index.md) — the full catalog these families sit within
- [Programmatic Cloud Agent Dispatch](programmatic-cloud-agent-dispatch.md) — the dispatch surface that fires many of these always-on loops
- [Safe Outputs Pattern](../security/safe-outputs-pattern.md) — the write-constraint mechanism the triage family relies on
