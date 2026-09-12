---
title: "Verifying Agent Changes in the Copilot App"
description: "The Copilot app's diff, terminal, and browser panels address one session workspace. What accepting a diff does to your checkout, who holds the terminal prompt, and what the browser sends back."
tags:
  - copilot
  - workflows
  - code-review
aliases:
  - Copilot app diff panel
  - Copilot app terminal panel
  - Copilot app browser panel
applies_to: "copilot@1.x"
last_reviewed: 2026-09-11
status: current
---

# Verifying Agent Changes in the Copilot App

> The Copilot app's diff, terminal, and browser panels all address one session workspace, so the code you read is the code you ran.

These three panels pay off when the change renders a UI you can open, you can check it without a debugger, and nobody has to audit which sites the agent reached. Drop the debugger condition and you return to the IDE mid-review, with the app as a fourth window instead of a replacement for three. Drop either of the others and a panel sits idle or a compliance question goes unanswered. GitHub compresses the loop into one sentence: "Review the diff, validate in the integrated terminal and browser, and open a pull request that uses your team's existing checks and merge requirements" ([GitHub Changelog, 2026-06-17](https://github.blog/changelog/2026-06-17-github-copilot-app-generally-available/)).

## The two diff surfaces

The app shows diffs in two places, and they exit differently. Inside a session, click **Changes** above the prompt box to see what the agent did, then click **Create PR** to keep it ([GitHub Docs — Getting started with the GitHub Copilot app](https://docs.github.com/en/copilot/get-started/quickstart-copilot-app)). On an existing pull request, open **Files changed**, start a session to comment or ask for changes, then click **Review** at the top of the pull request view to submit ([GitHub Docs — Managing issues and pull requests](https://docs.github.com/en/copilot/how-tos/github-copilot-app/managing-issues-and-pull-requests)).

Both render the same before-and-after comparison ([GitHub Blog, 2026-09-10](https://github.blog/ai-and-ml/github-copilot/github-copilot-app-for-beginners-using-the-diff-terminal-and-browser/)). What differs is what your comment becomes. In the session it is a prompt the agent acts on. On the pull request it is a review other people read.

## What accepting does to your checkout

Usually nothing, because the session was never in your checkout. You pick where it runs when you start it: "in a new working tree, in your local repository, or in a cloud sandbox" ([GitHub Docs — Working with agent sessions](https://docs.github.com/en/copilot/how-tos/github-copilot-app/agent-sessions)). Only the middle option writes to the tree you already have open. The default shape is parallel sessions "each on its own branch and worktree" ([GitHub Changelog, 2026-06-17](https://github.blog/changelog/2026-06-17-github-copilot-app-generally-available/)).

That bites on the first terminal command. A fresh worktree has no `node_modules`, no `.env`, and no build output, so `npm run dev` fails for reasons unrelated to the diff in front of you.

## Who drives the terminal

You do. "You can run the code by hand or configure it as a script (available through the Run button)." Several can run side by side: "You can have multiple terminal windows open at once, so you can switch between them and keep running commands" ([GitHub Blog, 2026-09-10](https://github.blog/ai-and-ml/github-copilot/github-copilot-app-for-beginners-using-the-diff-terminal-and-browser/)). The agent is not locked out of the surface. GitHub describes canvases as "bidirectional surfaces where you and the agent operate on the same plan, pull request, terminal, or browser session" ([GitHub Changelog, 2026-06-17](https://github.blog/changelog/2026-06-17-github-copilot-app-generally-available/)), which is the [canvas control surface](../../patterns/agent-design/canvas-as-control-surface.md) applied to a shell.

## What the browser panel sends back

One route is documented. The Pick and Polish tool lets you "select an element and adjust it with the agent" ([GitHub Blog, 2026-09-10](https://github.blog/ai-and-ml/github-copilot/github-copilot-app-for-beginners-using-the-diff-terminal-and-browser/)). Past that, the app's documentation sets out no context behavior for the browser panel: no consent gate, no statement on tab isolation, no domain controls.

The same vendor's IDE browser documents all three. An agent "can't read or interact with a page you opened until you select **Share with Agent**", agent-opened pages carry "no access to the cookies or storage from your everyday browsing", and admins get `chat.agent.allowedNetworkDomains` and `chat.agent.deniedNetworkDomains` ([GitHub Changelog, 2026-07-01](https://github.blog/changelog/2026-07-01-browser-tools-for-github-copilot-in-vs-code-are-generally-available/)). Before you assume parity, check the heading: the element-level feedback improvement that reads like an app feature shipped under VS Code 1.132 ([GitHub Changelog, 2026-08-07](https://github.blog/changelog/2026-08-07-github-copilot-weekly-releases-august-3/)).

## Why it works

The isolated workspace is the reason. Each session "runs in its own isolated workspace" ([GitHub Docs — Working with agent sessions](https://docs.github.com/en/copilot/how-tos/github-copilot-app/agent-sessions)), so the lines the diff renders, the commands the terminal runs, and the page the browser loads all resolve against one checkout. Split those across three tools and nothing enforces the correspondence: you read a branch diff in an editor while a terminal elsewhere sits on a different tree with different uncommitted state, and they disagree silently. The panels do not make review sharper. They remove the chance that the artifact you read and the artifact you ran are different artifacts.

## When this backfires

- Nothing renders. An API service, a CLI, a library, or a data pipeline gets two useful panels and an empty third.
- Verification needs a debugger. The app's documented feature list runs from parallel workspaces to canvases and names no debugger, breakpoints, or test explorer ([GitHub Docs — About the GitHub Copilot app](https://docs.github.com/en/copilot/concepts/agents/github-copilot-app)), so a change checked by stepping through it sends you back to the IDE.
- Someone has to audit browser reach. VS Code ships a documented consent gate and domain allow and deny lists; the app's own documentation sets out no equivalent for its browser panel.
- The evidence is cheaper than the reading. A dev server that starts proves the happy path compiles, at far less effort than reading 600 changed lines. Treat a green preview as one signal, not as the review.
- The documentation is one blog post. Neither panel appears in the app's feature list or its workflow walkthrough ([GitHub Docs — About the GitHub Copilot app](https://docs.github.com/en/copilot/concepts/agents/github-copilot-app)), so every description of them is vendor-authored and none of it is reference documentation.

## Key Takeaways

- Two diffs, two meanings. A comment in the session diff is a prompt; a comment on the Files changed diff is a review someone else reads.
- Pick the session's run location deliberately. Choose your local repository only when you want the agent writing into the tree you have open; the other two options keep it out.
- Budget for a cold tree when you pick a new working tree. The first terminal command runs against a checkout with no installed dependencies and no local environment file.
- You hold the terminal prompt, and the agent can still act on the same surface through a canvas.
- The browser panel's only documented path back into agent context is Pick and Polish. Its governance story is published for VS Code and missing from the app's docs.

## Related

- [GitHub Copilot Dedicated App as Agent-First Surface](copilot-dedicated-app.md) — the surface-choice argument these panels sit inside, and the session-as-unit claim they make concrete
- [GitHub Copilot App Slash Commands and What They Change](slash-commands-copilot-app.md) — the prompt-box surface beside these panels, mapped by the session state each command changes
- [Canvas as Control Surface: Steering a Long-Running Agent Mid-Run](../../patterns/agent-design/canvas-as-control-surface.md) — the bidirectional-surface pattern the terminal and browser panels instantiate
- [Browser as Agent Action Space](../../patterns/agent-design/browser-as-agent-action-space.md) — when handing an agent a browser is worth its failure modes, and when a script is the better answer
- [Scoped Browser DevTools Access for Runtime Diagnosis](../../patterns/agent-design/scoped-devtools-access-runtime-diagnosis.md) — the narrower runtime-observation surface to reach for when a preview is not enough
