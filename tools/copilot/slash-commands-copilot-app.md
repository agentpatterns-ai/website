---
title: "GitHub Copilot App Slash Commands and What They Change"
description: "Copilot app slash commands are a GitHub-provided set you cannot extend, switching session modes, critic models, and tool permissions from the prompt box."
tags:
  - copilot
  - instructions
aliases:
  - Copilot app slash commands
  - Copilot app command picker
applies_to: "copilot@1.x"
last_reviewed: 2026-08-07
status: current
---

# GitHub Copilot App Slash Commands and What They Change

> Copilot app slash commands are a GitHub-provided set you cannot extend; your own repeatable work ships as a skill or custom agent.

Slash commands in the GitHub Copilot app are shortcuts you type in the prompt box to switch session modes, run built-in skills, and manage a session without writing a long prompt. Type `/` to open the command picker, then select a command or keep typing to filter ([GitHub Docs — app slash commands](https://docs.github.com/en/copilot/reference/github-copilot-app-reference/slash-commands)). GitHub supplies the set. The reference documents "GitHub-provided slash commands for the GitHub Copilot app," and no documented mechanism adds a new one.

## What you cannot author

The app's commands are not where a team packages its own repeatable work. Two commands load your customization instead: `/agent` "Selects a custom agent for the session," and `/skills` "Manages skills; use `/skills reload` to reload skills mid-session" ([GitHub Docs](https://docs.github.com/en/copilot/reference/github-copilot-app-reference/slash-commands)). GitHub builds its own commands on that same mechanism: the reference labels `/orchestrate`, `/create-canvas`, and `/af` as built-in skills. The route to a named operation of your own therefore runs through [a custom agent or an agent skill](custom-agents-skills.md).

A [prompt file library](../../instructions/prompt-file-libraries.md) does not transfer. In VS Code a `.prompt.md` file becomes a slash command you invoke by hand, but Microsoft's docs rule the app out: "Agents running on the Agent Host don't use prompt files. To use an existing prompt with the Copilot agent, convert it to an agent skill" ([VS Code — Prompt files](https://code.visualstudio.com/docs/copilot/customization/prompt-files)).

## What each command family changes

Pick a command by the state you want changed, not by the workflow name.

| Family | Commands | What it changes |
|---|---|---|
| Session mode | `/plan`, `/autopilot`, `/interactive` | How much autonomy the agent has |
| Independent critique | `/rubber-duck`, `/spar`, `/review`, `/security-review` | Who reviews the work, and on which model |
| Built-in skills | `/orchestrate`, `/create-canvas`, `/af` | Invokes a capability GitHub packaged |
| Context and cost | `/compact`, `/context`, `/clear`, `/chronicle cost-tips` | What stays in the session window |
| Tool permissions | `/allow-all-tools` (`/yolo`), `/reset-allowed-tools` | Whether tool calls auto-approve |
| Session topology | `/fork`, `/spawn`, `/fleet`, `/merge-to-parent` | How many sessions run, and their parent links |
| Repository artifacts | `/pr-open`, `/pr-fix-checks`, `/pr-resolve-comments`, `/init` | GitHub state outside the session |

Most commands carry a precondition the reference states per entry: "Requires an active session," "Requires an open pull request with failing checks," "Requires a forked session." Availability "depends on context and can change depending on whether a session has started" ([GitHub Docs](https://docs.github.com/en/copilot/reference/github-copilot-app-reference/slash-commands)).

## Where slash commands sit among Copilot's reusable surfaces

| Surface | Who authors it | When it applies | Reaches the app |
|---|---|---|---|
| [`.github/copilot-instructions.md`](copilot-instructions-md-convention.md) | You | Automatically, on every request | Yes |
| [Custom agent](custom-agents-skills.md) (`.github/agents/`) | You | On demand, via `/agent` | Yes |
| [Agent skill](custom-agents-skills.md) (`SKILL.md`) | You | On demand, or selected for you | Yes |
| [Prompt file](../../instructions/prompt-file-libraries.md) (`.prompt.md`) | You | On demand, in VS Code chat | No |
| App slash command | GitHub | On demand, gated on context | Yes |

Two app commands act on a repository instructions file, which is how that row reaches the app: `/init` "Generates or improves repository instructions," and `/chronicle improve` "Suggests improvements for your instructions file" ([GitHub Docs](https://docs.github.com/en/copilot/reference/github-copilot-app-reference/slash-commands)).

## Why it works

A mode command changes session state rather than prompt framing. GitHub puts the mechanism plainly: "The session mode controls how much autonomy the agent has." In Plan mode, "You review and approve the plan before the agent executes it"; in Autopilot, "The agent works fully autonomously" ([GitHub Docs — agent sessions](https://docs.github.com/en/copilot/how-tos/github-copilot-app/agent-sessions)). A prose instruction to plan first carries no such gate. `/plan` installs one.

The second mechanism is model diversity, Copilot's build of the [critic agent pattern](../../patterns/agent-design/critic-agent-plan-review.md). `/rubber-duck` "Requests critique on your approach or implementation by a model other than the one you have used in the session" ([GitHub Docs](https://docs.github.com/en/copilot/reference/github-copilot-app-reference/slash-commands)), and GitHub gives the causal reason: "the critic is less likely to share the same blind spots, biases, or failure modes as the model that produced the work" ([GitHub Docs — rubber duck agent](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/rubber-duck)). Review by the producing model inherits that model's error distribution, and a contrasting critic decorrelates it.

## When this backfires

- One-off asks: GitHub advises skipping the vocabulary. "You don't need to memorize any commands to get started. Pick a few slash commands that match how you work and build from there" ([GitHub Blog, 2026-08-06](https://github.blog/ai-and-ml/github-copilot/a-guide-to-slash-commands-in-the-github-copilot-app/)).
- Mode state you cannot see: the mode commands set what the dropdown below the prompt field already sets ([GitHub Docs](https://docs.github.com/en/copilot/how-tos/github-copilot-app/agent-sessions)), so they buy keystrokes rather than capability. A user-filed CLI report shows the cost when that state drifts out of view: "Shift tab can lead to occasional execution in wrong mode especially when cli has switched automatically" ([github/copilot-cli#1692](https://github.com/github/copilot-cli/issues/1692)).
- Autopilot on an under-specified task: GitHub's documentation for the CLI's autopilot mode names three costs. The mode "is not ideal for open-ended exploration, feature development without a clear goal." It works best with full permissions, which allow "altering and deleting files." And "AI credits are consumed without your direct involvement" ([GitHub Docs — autopilot](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/autopilot)).
- Sessions outside Claude and GPT: "The rubber duck agent is currently only available if the main agent is using a Claude or GPT large language model" ([GitHub Docs — agent sessions](https://docs.github.com/en/copilot/how-tos/github-copilot-app/agent-sessions)), so the independent-critic path is absent on other session models, including one you supply yourself.
- Runbooks pinned to the vocabulary: the reference warns that "The command list can change over time," so a documented step breaks quietly when a command is renamed or its precondition is absent.
- Cross-client documentation: Copilot CLI's commands are a configuration control surface, described as "your control surface within Copilot CLI" for managing context and permissions ([GitHub Blog, 2026-06-15](https://github.blog/ai-and-ml/github-copilot/github-copilot-cli-for-beginners-overview-of-common-slash-commands/)). The app post draws the same line: "CLI slash commands are designed around a terminal-first workflow… App slash commands are more about workflows."

## Example

The documented plan-then-build handoff, expressed in app commands.

```text
/plan add rate limiting to the public API
# Plan mode: the agent drafts a plan and waits for your approval

/rubber-duck check this plan for missed failure cases
# a model other than the session model returns a critique

/autopilot
# Autopilot mode: the agent implements the approved plan unattended

/pr-open
# opens a pull request from the current session's changes
```

Every command above is verbatim from the app reference, where `/plan [PROMPT]` and `/autopilot [PROMPT]` both take an optional prompt, so the mode switch and the instruction land on one line ([GitHub Docs](https://docs.github.com/en/copilot/reference/github-copilot-app-reference/slash-commands)). GitHub documents the same handoff for the CLI, where an accepted plan offers "Accept plan and build on autopilot" ([GitHub Docs — autopilot](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/autopilot)).

## Key Takeaways

- To get your own named operation in the app, write a custom agent or an agent skill and reach it with `/agent` or `/skills`. A `.prompt.md` file will not appear there.
- Read the picker rather than a runbook. GitHub documents the list as changing, so the commands present in your context are the authority on what exists.
- Confirm the session mode before a long prompt. Executing in a mode you did not intend is the documented failure of this surface.
- Settle the permission grant and the spend you accept before `/autopilot`, because both then apply with no further prompting.

## Related

- [Copilot Dedicated App (Desktop)](copilot-dedicated-app.md) — the surface these commands are typed into
- [Custom Agents, Skills & Plugins](custom-agents-skills.md) — the two containers that `/agent` and `/skills` load
- [Prompt File Libraries for Reusable Agent Instructions](../../instructions/prompt-file-libraries.md) — the `.prompt.md` surface that stops short of the app
- [Critic Agent Pattern: Dual-Model Plan Review](../../patterns/agent-design/critic-agent-plan-review.md) — the tool-agnostic pattern behind `/rubber-duck`
- [Agent-Discoverable Slash Commands](../../patterns/agent-design/agent-discoverable-slash-commands.md) — the case where the planner invokes commands instead of you
