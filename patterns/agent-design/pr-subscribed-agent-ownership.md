---
title: "PR-Subscribed Agent Ownership: The Agent That Opened the PR Drives It to Green"
term: "PR-Subscribed Agent Ownership"
description: "An agent subscribes to the pull request it created and wakes on CI and review events until the PR is mergeable — viable only with a machine-checkable oracle, data-plane-only authority, a retry budget, and per-agent isolation."
tags:
  - agent-design
  - workflows
  - tool-agnostic
aliases:
  - "event-subscribed agents"
  - "agent PR subscription"
last_reviewed: 2026-10-02
maturity: emerging
---

# PR-Subscribed Agent Ownership: The Agent That Opened the PR Drives It to Green

> An agent subscribed to the pull request it opened wakes on CI and review events and patches until green, inside a retry budget.

## Four conditions before you remove the trigger

This pattern is the autonomous half of [one-click CI auto-fix](../../workflows/one-click-ci-auto-fix.md), which keeps three human gates: the click, the workflow approval, and the PR review. Subscription removes the click. Adopt it only where all four conditions hold.

- The failing signal is a real oracle, not a status color. Where the only success criterion is "the check went green," the cheapest path there is editing the check. An industrial study of an autonomous repair loop documented "concrete instances of assertion weakening and test-case deletion used as workaround mechanisms to achieve superficial convergence" ([arXiv:2605.01471v1](https://arxiv.org/abs/2605.01471v1)).
- The agent holds data-plane authority only. Published work on agentic CI/CD separates data-plane authority, meaning "localized interventions such as patch generation and test reruns," from control-plane authority over "pipeline configuration, deployment policies, and approval gates" ([arXiv:2605.07062v1](https://arxiv.org/abs/2605.07062v1)). A subscribed agent that can both edit `.github/workflows/` and trigger those workflows has crossed the line without a gate.
- A retry budget and a stop condition exist as configuration, not as intent. The same paper reports "constrained autonomy as the dominant design, external governance as the primary safety mechanism," rather than intrinsic agent guarantees ([arXiv:2605.07062v1](https://arxiv.org/abs/2605.07062v1)).
- Each woken agent gets its own workspace. Cursor ships this as the precondition: "Subagents can now run on their own virtual machines. Each gets an isolated copy of the project with clean context in its own cloud environment" ([Cursor Changelog, 2026-08-19](https://cursor.com/changelog/08-19-26)).

## The subscription primitive

A subscribed agent attaches to an event source instead of being invoked per task. Cursor describes an agent that "subscribes to an event source (a thread or conversation) and wakes when something happens," covering pull requests, Slack threads, and schedules ([Cursor Changelog, 2026-08-19](https://cursor.com/changelog/08-19-26)). PR ownership follows: "Cloud agents automatically subscribe to PRs they create and drive them to completion, fixing CI and addressing bot comments."

GitHub ships this loop in preview as agent merge: "Enable agent merge in an active session to let the agent handle review feedback, failed checks, merge conflicts, and workflow reruns" ([GitHub Changelog, 2026-10-01](https://github.blog/changelog/2026-10-01-github-copilot-in-vs-code-september-2026-releases)). The changelog names the work the agent takes on and stops there. Who presses merge and what bounds the reruns are conditions two and three above, and the announcement answers neither.

```mermaid
flowchart TD
    A[Agent opens PR] --> B[Subscribe to PR events]
    B --> C{Event fires}
    C -->|CI failure| D[Patch in isolated workspace]
    C -->|Bot comment| E[Triage against allowlist]
    D --> F{Retry budget left?}
    E --> F
    F -->|Yes| C
    F -->|No| G[Stop and escalate]
```

Steering survives the subscription: follow-up messages "wait for the next tool call instead of cutting the agent off mid-action" ([Cursor Changelog, 2026-08-19](https://cursor.com/changelog/08-19-26)). That is [mid-run redirection](steering-running-agents.md) applied to a long-lived agent.

## A local watch under your own credentials

In Claude Code 2.1.330 or later, `/ship` opens a GitHub pull request if needed, reviews your change with [`/code-review`](../../tools/claude/code-review-local-scope.md), then watches the pull request from your session. `/steward` only watches. The watch works on failing checks, conflicts, and comments with your `gh` and `git` sign-ins ([command docs](https://code.claude.com/docs/en/ship-command)).

The fourth condition above does not hold here, because "Claude edits files in the same checkout as you" ([while a watch runs](https://code.claude.com/docs/en/ship-command#keep-working-while-a-watch-runs)). Start your next change in another folder, such as a second clone.

Run it only where you trust everyone who can merge to the base branch or push to your branch. "Any of them can run programs on your computer with your credentials" ([command docs](https://code.claude.com/docs/en/ship-command)). The limits are partial, and the watch could merge a pull request that branch rules let you merge without another person's approval:

- On turns without a message from you, Claude Code blocks `gh` and `git` commands that merge, approve, enable auto-merge, or force-push. The limits are off while Claude answers a message you type, and a permission rule or hook can let commands past them ([blocked commands](https://code.claude.com/docs/en/ship-command#what-claude-code-blocks-during-a-watch)).
- Your tests can merge or force-push with your credentials, because Claude Code checks only the command that starts them ([code a watch runs](https://code.claude.com/docs/en/ship-command#code-that-a-watch-runs-on-your-computer)).
- With auto-merge on, a pushed fix can bring about the merge ([merge cases](https://code.claude.com/docs/en/ship-command#when-a-watch-can-lead-to-a-merge)).
- Repository git hooks don't run for Claude's unattended fetches, merges, commits, and pushes ([rules and hooks](https://code.claude.com/docs/en/ship-command#permission-rules-and-hooks-that-apply-to-%2Fship-and-%2Fsteward)). Put required checks in [CI and branch rules](https://claude.dev/blog/the-work-after-you-open-a-pr/).
- Claude reads comments from you, from people with write access, and, on github.com, from Claude's bot. `+botname` adds another.
- Claude follows your checkout's `.claude/skills/steward/SKILL.md` as instructions, and anyone who can merge can write it.

It ends on merge, close, a PR Steward label, or seven days, and [sooner in some cases](https://code.claude.com/docs/en/ship-command#what-ends-a-watch). It waits at prompts in Manual and `acceptEdits` modes, does not start in `bypassPermissions` mode or on native Windows, and counts against your usage. The [vendor post](https://claude.dev/blog/the-work-after-you-open-a-pr/) puts a three-push limit per issue in a passage about what Claude is told. The command docs state no such limit, so do not count it as your configured retry budget.

The hosted [PR Steward](https://code.claude.com/docs/en/pr-steward-security) ([public beta](https://code.claude.com/docs/en/claude-ship), Team and Enterprise) is designed not to approve or merge. In an Anthropic-hosted environment, two checks cover merge, auto-merge, and force-push commands, but "a command that's written another way can pass both", so require approvals with branch rules. These are vendor sources, and none reports outcome data.

## Why it works

The saving is context re-establishment, not patch authorship. Under a per-round human trigger every CI failure starts a cold agent: GitHub's variant "opens a new pull request on top of your existing pull request, analyzes the failing check, and attempts to implement a fix," then tags a human for review ([GitHub Changelog, 2026-07-23](https://github.blog/changelog/2026-07-23-github-mobile-fix-failing-actions-checks-with-copilot-cloud-agent/)). Round N pays to rediscover everything earlier rounds established, plus the operator's context switch. A subscribed agent holds that state across wakes, so a round costs the patch alone and it knows which fixes it already tried.

Retained state also produces the failure mode. A stacked-PR loop hands each fix to a reviewer who sees it cold; a subscription removes that reader. The safe operating band therefore sits at the data plane, where safety comes from "surrounding governance infrastructure rather than intrinsic agent guarantees" ([arXiv:2605.07062v1](https://arxiv.org/abs/2605.07062v1)).

## When this backfires

Optimizing for green CI optimizes a weak proxy for merge. One study took 11,048 closed agentic pull requests, refined them to 9,799 human-reviewed, and "manually inspected 717 representative cases to recover decision rationale from interaction artifacts". In those, "only 35.7% of rejected PRs reflected clear agentic failures, while 31.2% were driven by workflow constraints and 33.1% lacked observable decision rationale" ([arXiv:2605.22534v1](https://arxiv.org/abs/2605.22534v1)). CI-fixing reaches none of the 31.2%. For the 33.1% the reason could not be recovered at all, so whether a green build would have changed the outcome is unknown rather than answered.

Convergence is not the common case. The industrial repair study measured a 70% convergence rate at scenario-family level with a mean of 3.4 repair iterations, only 10% of families succeeding on the first attempt, and 38% of reports failing to produce any executable test artifact ([arXiv:2605.01471v1](https://arxiv.org/abs/2605.01471v1)). Its conclusion is that "unrestricted autonomy leads to unstable and often misleading outcomes."

Review bots create a moving target. Cursor's feature explicitly covers "addressing bot comments" ([Cursor Changelog, 2026-08-19](https://cursor.com/changelog/08-19-26)), and each push that answers a comment can trigger a fresh review round. The shipped `/goal` primitive gives the agent "a long-lived objective to work towards until it's fully complete," which is an objective rather than a termination condition. Restrict the agent to allowlisted comment authors and cap rounds explicitly, the way an [agent circuit breaker](agent-circuit-breaker.md) bounds a retrying loop.

Flaky or slow pipelines starve the loop. A 10% first-attempt rate and a 3.4-iteration mean leave little headroom before a non-deterministic signal produces oscillation.

Shared checkouts collide. Agents woken by concurrent events against one working copy interleave branch state, which is why isolation ships alongside subscription.

## Key Takeaways

- Subscription removes the human trigger from the CI-fix loop and leaves the workflow-approval and PR-review gates to carry the whole design.
- Replace the removed trigger with three deterministic controls: data-plane-only authority, an explicit retry budget with an escalation path, and a comment-source allowlist.
- The mechanism is retained context across wakes, so the win shrinks as failure rounds get more independent of each other and disappears where each round needs fresh diagnosis anyway.
- Assertion weakening and test deletion are documented outcomes of unsupervised repair loops, so a green check is evidence only when the check itself sits outside the agent's write scope.
- Green CI is a weak merge proxy. Of 717 manually inspected rejections, 31.2% turned on workflow constraints and 33.1% left no recoverable rationale.
- Per-agent workspace isolation is a precondition for event-driven concurrency, not a later optimization.
- A local `/ship` or `/steward` watch runs in your own checkout, where anyone who can merge to the base branch or push to your branch can run programs with your credentials.

## Related

- [One-Click CI Auto-Fix](../../workflows/one-click-ci-auto-fix.md) — the human-triggered half of this pair, holding the three gates this pattern removes one of
- [Event-Driven Agent Routing](event-driven-agent-routing.md) — the routing model underneath subscriptions, where state-change events advance work with no central coordinator
- [Steering Running Agents](steering-running-agents.md) — how follow-up messages redirect a long-lived agent without halting its current tool call
- [Agent Circuit Breaker](agent-circuit-breaker.md) — the retry-budget and stop-condition mechanism this pattern needs to replace the removed trigger
- [Self-Healing Production Agent](self-healing-production-agent.md) — the same closed-loop shape applied to post-deploy regressions rather than pre-merge CI
- [Project-Scoped Agent Workspace](project-scoped-agent-workspace.md) — where the woken agents write what they learn, and why the subscription's trust boundary reaches that store
- [Closed-Loop CI Failure Remediation](../../workflows/closed-loop-ci-failure-remediation.md) — the CI-failure loop run with cloud coding agents
- [Claude Code Review](../../tools/claude/code-review.md) — the managed review service, separate from the review `/ship` runs in your session
