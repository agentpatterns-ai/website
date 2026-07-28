---
title: "Issue-Tracker as Agent Dispatch Surface"
description: "Assigning a coding agent from Jira, Linear, or GitHub Issues works only with WRAP ticket discipline, assignment-vs-mention conventions, and status-echo gating."
term: "Issue-Tracker as Agent Dispatch Surface"
tags:
  - workflows
  - agent-design
  - tool-agnostic
aliases:
  - issue-tracker as agent control plane
  - Jira agent dispatch
  - Linear agent dispatch
  - ticket-as-prompt
last_reviewed: 2026-06-03
maturity: established
---

# Issue-Tracker as Agent Dispatch Surface

> Issue-tracker dispatch makes the ticket the agent's prompt — viable only under WRAP ticket discipline, an assignment-vs-mention convention, status-echo gating, and an opt-in pickup filter.

Issue-tracker dispatch is the fourth invocation surface after the IDE, chat platform, and [programmatic REST API](programmatic-cloud-agent-dispatch.md). As of May 2026 it ships on three trackers — GitHub Issues (Copilot coding agent), Jira (Cursor and Copilot via Rovo), and Linear (Linear Agent and Copilot). The contract is identical across all three; what differs is the field model, the mention semantics, and the failure modes that surface in field reports. The pattern reuses every team's async work queue as the agent control plane — when ticket discipline holds. Without it, the machinery amplifies noise: agent-authored PRs on GitHub jumped from 4M in September 2025 to 17M in March 2026, with anecdotal reports that only 1 in 10 is legitimate. ([danilchenko.dev](https://www.danilchenko.dev/posts/2026-04-11-github-ai-agents-pull-requests/))

## Preconditions

Adopt this dispatch surface only when all four conditions hold. Missing one turns the ticket queue into an agent-spam generator.

| Condition | Why it is load-bearing |
|-----------|----------------------|
| Ticket-writing discipline (WRAP or equivalent) | An empirical study of 2,000+ Copilot-assigned issues finds ticket quality features alone predict merge outcome at 72% AUC; verbose descriptions cut merge likelihood by 9% and external-dependency mentions by 4-9%. ([Bui et al., arxiv 2512.21426](https://arxiv.org/html/2512.21426v1)) |
| Explicit assignment-vs-mention convention | Assignment starts a new session scoped to the ticket; in-comment `@mention` resumes or refines an existing session. Teams without a convention create duplicate parallel sessions racing on the same branch. ([Atlassian: Cursor in Jira](https://www.atlassian.com/blog/company-news/cursor-in-jira), [GitHub Blog](https://github.blog/ai-and-ml/github-copilot/assigning-and-completing-issues-with-coding-agent-in-github-copilot/)) |
| Status-echo gating | Every progress update posted as a new comment buries the original requirements; the `hide-older-comments: true` knob in `gh-aw` exists because the spam pattern was severe enough to standardize. ([github.github.com gh-aw](https://github.github.com/gh-aw/reference/safe-outputs/)) |
| Opt-in pickup filter (label, template, or assignee gate) | The same source reports that the 4-to-17M PR surge surfaced agent-PR signal-to-noise problems severe enough that GitHub introduced a kill switch; gating by `agent-ready` label or template tag bounds the blast radius before scale forces a hard cutoff. ([danilchenko.dev](https://www.danilchenko.dev/posts/2026-04-11-github-ai-agents-pull-requests/)) |

## The contract

The pattern has three contract elements that recur across all three trackers.

### 1. Ticket-as-prompt

The ticket body, comments, and linked attachments become the agent's prompt. GitHub publishes the WRAP framework — Write effective issues (clear title, full context, examples), Refine instructions (repo, org, or enterprise custom instructions), Atomic tasks (one issue = one concern), Pair with the agent (human in review). ([GitHub Blog: WRAP up your backlog](https://github.blog/ai-and-ml/github-copilot/wrap-up-your-backlog-with-github-copilot-coding-agent/)) Best-practice guidance is consistent across vendors: include a problem description, complete acceptance criteria, file or function references, and formatting rules; avoid unrelated goals in the same ticket. ([GitHub Docs](https://docs.github.com/copilot/how-tos/agents/copilot-coding-agent/best-practices-for-using-copilot-to-work-on-tasks))

The empirical correlate: the Bui et al. random-forest model finds shorter, self-contained tickets merge; verbose descriptions decrease merge likelihood by 9%, external-API references by 4-9%. The ticket is the dominant predictor of agent success. ([arxiv 2512.21426](https://arxiv.org/html/2512.21426v1))

### 2. Mention semantics

Assignment and `@mention` are not interchangeable. Assignment kicks off a new agent session bound to the ticket; mention in a comment either restarts the session or refines an existing one with the comment as additional instruction. Cursor in Jira documents both paths: "Assign work items to Cursor, or mention `@Cursor` in a comment to kick off a cloud agent." ([Cursor changelog 2026-05-19](https://cursor.com/changelog/05-19-26)) GitHub Copilot uses the same dual semantics — issue assignment is the primary entry point; mid-task `@copilot` comments refine. ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/assigning-and-completing-issues-with-coding-agent-in-github-copilot/))

Without an explicit team convention, the failure mode is duplicate-session races: a PM assigns the ticket to the agent, a developer adds an `@mention` to refine, and the tracker spawns two parallel sessions both pushing to the same branch. Standardize on one of the two semantics per ticket lifecycle stage — typically assignment for initial dispatch, mention for refinement.

### 3. Status echo

The agent must echo progress back into the ticket without flooding the comment thread. The three trackers handle this differently:

- GitHub Copilot: posts an 👀 emoji reaction on assignment, then exposes a PR checklist with task breakdown and live session logs; commits push iteratively to the branch. ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/assigning-and-completing-issues-with-coding-agent-in-github-copilot/))
- Cursor in Jira: notifies the requester in Jira when input is needed or work is ready for review; auto-links the PR back to the ticket on completion. ([Atlassian](https://www.atlassian.com/blog/company-news/cursor-in-jira))
- [GitHub Agentic Workflows](../tools/copilot/github-agentic-workflows.md) (gh-aw): exposes `hide-older-comments: true` as a safe-output option specifically because repeated status comments became unreadable noise. ([github.github.com gh-aw](https://github.github.com/gh-aw/reference/safe-outputs/))

The status-echo contract is what makes the ticket usable as an asynchronous coordination artifact. When it fails — Atlassian community reports of Rovo "hallucinating success on write actions" without flagging completion failures — trust in the entire dispatch surface erodes.

## Cross-tracker surface map

| Tracker | Dispatch | Status echo | Cross-vendor agent option | Notes |
|---------|----------|-------------|---------------------------|-------|
| GitHub Issues | Assignment to `@copilot`; `@copilot` comment | 👀 reaction, PR checklist, live session logs | Native (Copilot); Claude Code via GitHub Actions `@claude` | Documented best-practice = WRAP. ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/wrap-up-your-backlog-with-github-copilot-coding-agent/)) |
| Jira | Assign work item to Cursor; `@Cursor` in comment | In-Jira notifications; auto-linked PR | Cursor (via Rovo); Copilot coding agent for Jira (public preview 2026-03-05) | Requires Cursor admin + Jira Commercial Cloud with Rovo enabled. ([Cursor changelog](https://cursor.com/changelog/05-19-26)) |
| Linear | Linear Agent (public beta 2026-03-24); `@mention` agent in issue | In-issue comments; Slack thread routing | Linear Agent (native); Copilot cloud agent integration | Webhook-driven extensions (Cyrus + Hookdeck for Claude Code) available. ([Linear changelog 2026-03-24](https://linear.app/changelog/2026-03-24-introducing-linear-agent), [GitHub Docs](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/integrate-cloud-agent-with-linear)) |

## Diagram

```mermaid
graph TD
    A[PM / dev writes ticket] --> B[Pickup filter:<br>label / template / assignee gate]
    B -->|gated out| Z[Stays in human triage]
    B -->|gated in| C[Dispatch mode]
    C -->|assignment| D[New agent session]
    C -->|@mention| E[Resume / refine session]
    D --> F[Agent reads ticket + comments + attachments]
    E --> F
    F --> G[Sandboxed execution]
    G --> H[Status echo: gated comments + PR link]
    H --> I[Human review on PR]
    I -->|refine via @mention| E
    I -->|merge| J[Ticket auto-closed]
```

## Why it works

The mechanism is infrastructure reuse. Every software team already runs an asynchronous work queue with auditable state transitions. Exposing the queue as an agent control plane reuses that machinery — no new dashboard, no separate audit trail, no parallel notification surface. Bui et al. formalize why this works: ticket-quality features alone predict Copilot merge success at 72% AUC, meaning the ticket is the prompt in a precise statistical sense. ([Bui et al., arxiv 2512.21426](https://arxiv.org/html/2512.21426v1))

The corollary is the failure mechanism: where ticket-writing rigor is absent, the dispatch surface amplifies the absence. The 17M-PR / ~10% legitimate ratio on GitHub is the same machinery operating without the WRAP-style discipline that made it work — the queue still dispatches, but every dispatch is a wasted run. ([danilchenko.dev](https://www.danilchenko.dev/posts/2026-04-11-github-ai-agents-pull-requests/))

## When this backfires

- Tickets written for humans, not agents — terse, ambiguous "make the search faster" with no acceptance criteria and no file references causes the agent to fan out across the codebase and produce a PR that misses the intent. The 4-9% per-dimension merge-rate decrease in the Bui paper compounds when multiple ticket-quality dimensions fail simultaneously. ([arxiv 2512.21426](https://arxiv.org/html/2512.21426v1))
- Vendor field-model mismatches — Atlassian community reports describe Rovo agents that "hallucinate success on write actions" and "don't distinguish cleanly between field types and their scope," meaning the status-echo contract appears to work but actually fails silently. When one user has access to multiple boards, Rovo picks the wrong board's context, breaking exactly at organizational scale. ([Atlassian Community: Rovo limitations](https://community.atlassian.com/forums/Rovo-questions/Does-anyone-else-feel-like-Rovo-is-just-A-not-AI/qaq-p/3215367))
- Comment-thread spam without gating — every progress update posted as a new comment buries the original requirements. The pattern was severe enough that `gh-aw` shipped `hide-older-comments: true` as a first-class output knob; GitHub itself killed a Copilot "tips" feature after it generated 11,400 spam comments. ([github.github.com gh-aw](https://github.github.com/gh-aw/reference/safe-outputs/), [danilchenko.dev](https://www.danilchenko.dev/posts/2026-04-11-github-ai-agents-pull-requests/))
- Mention-vs-assignment confusion — without an explicit team convention, a PM assigning the ticket and a developer adding an `@mention` to refine spawn two parallel sessions racing on the same branch. Idempotency is the team's problem, not the tracker's.
- Unfiltered auto-pickup at backlog scale — enabling ticket-tracker dispatch on a multi-thousand-ticket backlog without a label or template gate produces the GitHub-scale failure pattern: 17M agent PRs in March 2026, ~10% legitimate. ([danilchenko.dev](https://www.danilchenko.dev/posts/2026-04-11-github-ai-agents-pull-requests/))
- Tasks the agent should not be doing at all — fix-related PRs from coding agents show measurable rejection patterns at the PR review stage; the dispatch surface cannot rescue tasks where the agent lacks the deep business-logic understanding to solve them. ([arxiv 2602.04226: Why Agentic-PRs Get Rejected](https://arxiv.org/pdf/2602.04226))

## Example

A minimal WRAP-shaped ticket the GitHub Blog cites as an effective Copilot prompt:

```
Title: Session token not persisted to localStorage after login

W (What): Users are being logged out on every page refresh. The session token
   is not being persisted to localStorage after login.
R (References): Authentication logic is in src/auth/session.ts. The login
   handler is handleLogin() in src/pages/Login.tsx.
A (Acceptance criteria):
   - After logging in, a page refresh keeps the user logged in.
   - All existing tests in src/__tests__/auth.test.ts pass.
   - Add a test verifying session persistence across a simulated reload.
P (Plan): The handler currently sets state but does not call
   tokenStore.persist(). Wire it in and verify.
```

The same ticket dispatched without the R/A/P sections — "users get logged out on refresh, please fix" — is the ticket pattern the Bui paper finds 4-9% less likely to merge per missing dimension. ([GitHub Blog: WRAP](https://github.blog/ai-and-ml/github-copilot/wrap-up-your-backlog-with-github-copilot-coding-agent/), [arxiv 2512.21426](https://arxiv.org/html/2512.21426v1))

## Key Takeaways

- Issue-tracker dispatch is the fourth agent invocation surface alongside IDE, chat, and programmatic API — portable across GitHub Issues, Jira, and Linear with an identical three-element contract.
- The contract is: ticket-as-prompt, mention vs assignment semantics, status-echo gating.
- Empirical evidence (72% AUC random-forest on ticket-quality features) puts the dominant variance in merge success on the ticket, not the agent. Invest in WRAP-style ticket discipline before the dispatch surface returns value.
- Status echo without gating turns the comment thread into agent spam — `hide-older-comments`-style discipline is mandatory.
- Without an opt-in pickup filter, the dispatch surface produces the GitHub-scale 17M-PR / 10%-legitimate failure pattern.

## Related

- [Issue-to-PR Delegation Pipeline](issue-to-pr-delegation-pipeline.md) — the GitHub-specific five-phase pipeline this dispatch surface feeds
- [Chat-Platform Agent Delegation](chat-platform-agent-delegation.md) — the chat dispatch surface; same contract elements, different principal
- [Programmatic Cloud-Agent Dispatch via REST API and Webhooks](programmatic-cloud-agent-dispatch.md) — the REST / webhook / cron dispatch surface
- [Backlog Triage as a Named Agent Skill](backlog-triage-skill.md) — the upstream skill that ensures tickets reach the dispatch surface in a WRAP-ready state
- [QA Session to Issues Pipeline](qa-session-to-issues-pipeline.md) — generates the kind of investigated, context-rich tickets that succeed on this dispatch surface
- [Trigger-Level Gating for Autonomous Agent Intake](../patterns/agent-design/trigger-level-agent-intake-gating.md) — the opt-in pickup filter above, expanded into the three gates that decide whether an agent starts and what it may change
