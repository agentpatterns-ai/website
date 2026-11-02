---
title: "Copilot Projects: Harness-Sized Fan-Out Across Repositories"
description: "Copilot Projects, in public preview since 28 October 2026, lets Copilot choose how many agents to run across repositories and returns results for review, so the agent count is the product's decision."
tags:
  - copilot
  - agent-design
  - workflows
term: "Copilot Projects"
aliases:
  - Copilot Projects
  - GitHub Copilot app Projects
applies_to: "copilot@1.x"
last_reviewed: 2026-10-31
status: current
---

# Copilot Projects: Harness-Sized Fan-Out Across Repositories

> Copilot Projects lets Copilot choose how many agents to run across repositories, so you review the results it returns instead of sizing the fan-out.

Projects in the GitHub Copilot app give work that spans several repositories "one home, with its context, agents, and results together." You describe a goal and add context. Copilot decides how many agents the work needs ([GitHub changelog, 2026-10-28](https://github.blog/changelog/2026-10-28-github-copilot-app-universe-releases)).

## Preview status

The changelog states: "Copilot Projects are now in public preview." The documentation adds that Projects "are in public preview and subject to change" ([GitHub Docs — Working with projects](https://docs.github.com/en/copilot/how-tos/github-copilot-app/working-with-projects)). Treat the behavior below as the state on 2026-10-31, not a stable contract.

## Who sets the width

In an operator-sized fan-out you pick the count: one agent per page, per issue, or per audit dimension. In Projects you hand over a goal. The changelog says "Copilot runs as many agents as the work needs and brings back results (e.g., pull requests) for your review." The documentation describes the same split: "Copilot coordinates the work toward your goal," and you "follow overall progress in the project rather than directing each session separately."

These two sources publish no cap and no sizing rule. They do not say whether a setting exposes the agent count before the work starts, so check that in the app.

## What you give up

- Up-front sizing. You set the goal and the context, for example repositories, design mocks, Slack threads, or meeting notes, and you can add task constraints. Copilot decides how the work splits across sessions. Whether you can bound the split per agent is a point to verify in the app. You can open one session and "send a message in Steer this session," but only after it exists.
- A fixed review load. Each item under Open "shows the session's status, the associated pull request, and the number of lines added and deleted." Review volume can vary with the goal, and Copilot sets how many sessions run.
- A single place to read everything. The project groups work by status: Needs input, Open, Working, and Done. You can still inspect an individual session's conversation, changes, pull request, and plan, and review other artifacts the sessions produce.

## Compare with a controller you build

The [adaptive sandbox fan-out controller](../../patterns/multi-agent/adaptive-sandbox-fanout-controller.md) also varies the agent count instead of fixing it. There, you write the loop, choose the signals, and set the stop rules. In Projects the product holds that loop, and the documentation does not publish its signals or limits. Choose a controller you own when you need a hard cost bound or a stop rule you can audit. For the general trade-off between lead-agent control and delegated work, see [orchestrator-worker](../../patterns/multi-agent/orchestrator-worker.md).

## When to skip Projects

The changelog keeps the narrow path: "For a focused task in a single repository, you can still start a session directly from that repository." For a focused task in one repository, the changelog also offers a direct session. Use a project when the goal spans repositories or needs no repository at all.

## What the same changelog entry does not say about Projects

The entry also covers connected-tool context, image generation, and computer use. The entry attaches the approval prompt to computer use: "Copilot asks for your approval before controlling an app". It attaches the managed-settings switch to computer use too: "your organization can disable the feature through managed settings". It states neither for Projects. For computer use, see [computer use as the last integration tier](../../patterns/agent-design/computer-use-last-integration-tier.md).

## Key Takeaways

- Projects moves the fan-out decision into the product. The count is Copilot's, and you see it as a list of sessions grouped by status.
- Size your review capacity before you start a broad goal. These two sources publish no cap on how many sessions or pull requests come back.
- Keep single-repository tasks as direct sessions.
- Do not assume Projects inherits the computer-use governance lines. The changelog gives them for computer use only.
- The feature is in public preview and "subject to change". Re-check the documentation before you build a process on it.

## Related

- [Copilot Dedicated App (Desktop)](copilot-dedicated-app.md) — the app that hosts Projects and its session list
- [Agent Mission Control](agent-mission-control.md) — the web dashboard for dispatching and watching Copilot sessions across repositories
- [Adaptive Sandbox Fan-Out Controller](../../patterns/multi-agent/adaptive-sandbox-fanout-controller.md) — the operator-built version of a variable agent count
- [Orchestrator-Worker](../../patterns/multi-agent/orchestrator-worker.md) — the general pattern of a lead agent that delegates to workers
- [Computer Use as the Last Integration Tier](../../patterns/agent-design/computer-use-last-integration-tier.md) — the other feature in the same changelog entry
