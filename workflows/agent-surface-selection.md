---
title: "Choosing the Right Surface for a Coding Agent Task"
term: "Agent Surface Selection"
description: "Keep a task in chat while its intent is still forming; once intent is known, move it off chat and let repetition, run length, and triggers decide how much setup the new surface earns."
tags:
  - workflows
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - surface selection for coding agents
  - chat vs automation decision rule
  - when to move a task off chat
last_reviewed: 2026-09-26
maturity: emerging
---

# Choosing the Right Surface for a Coding Agent Task

> Keep a task in chat while intent is forming. Once intent is known, leave chat; repetition, run length, and triggers decide how much setup pays.

A coding agent can run in a chat pane, an inline editor action, a background or cloud agent, a CI job, a comment thread, a hook, or a canvas. Which one fits depends on two facts about the task: whether you already know what you want, and whether the task happens once or keeps happening. Chat wins while intent is unknown. Once intent is known, chat loses, and the second fact sets how far the task moves: a one-off goes to an inline action, while a task that repeats, runs long, or starts from an event earns a surface that costs more to build. GitHub's own case against chat states the boundary directly: "as the user you know what you're going to do with it, and at that point chat is often the wrong UI" ([Burke Holland, GitHub Blog](https://github.blog/ai-and-ml/github-copilot/when-chat-is-the-wrong-ui/)).

## The two questions that decide it

Ask two questions before picking a surface for a task.

Do you already know what you want done? Holland's own defense of chat is that "chat works really well as a universal solution simply because we don't know what people are going to try to do with AI" ([Holland](https://github.blog/ai-and-ml/github-copilot/when-chat-is-the-wrong-ui/)). Earlier turns carry meaning in conversational coding: a study of 42 developers found that 42% of 910 task-oriented requests needed earlier conversational context to be understood correctly, and 83% of participants rated the ability to ask follow-up questions as "somewhat" or "a great deal" important ([Ross et al., IUI 2023](https://arxiv.org/abs/2302.07080v1)). When intent is still forming, the back-and-forth is doing real work, not adding friction.

Does the task happen once, or does it repeat, run long, or start from an event? A one-off task pays the same cost either way. A repeating or event-triggered task pays the cost of chat on every run: a person has to start it, the state resets between sessions, and the model solves the same problem again each time (sources for each cost are under [Why it works](#why-it-works)).

Unknown intent keeps a task in chat. Known intent moves it off chat, and the second question picks how far.

## Where each task shape lands

| Task shape | Surface | Where the output lands | What you must provide |
|---|---|---|---|
| Intent unknown, one-off | Chat or an interactive agent session | Transcript | None |
| Intent known, one-off | Inline editor action | Working-tree edit | None |
| Intent known, well-scoped, runs long, needs judgment | Background or cloud agent | Pull request | Review capacity |
| Intent known, event-triggered | CI job or comment dispatch | Check result or PR comment | Workflow config |
| Intent known, deterministic | Command hook or generated script | Script output, no model call | Written once |
| Intent known, repeats, needs human steering | Canvas | Persistent app state | A custom app build ([Holland](https://github.blog/ai-and-ml/github-copilot/when-chat-is-the-wrong-ui/)) |

Unknown intent stays in chat however often the task repeats. The CI job and hook rows split on where the work runs and whether it needs a model. A CI job starts from a repository event and can call an agent. A hook or script runs fixed steps and calls no model at all.

GitHub's cloud-agent documentation draws the same line between synchronous and asynchronous surfaces. With IDE chat, "individual developers pair in synchronous sessions with the AI assistant. Decisions made during the session are untracked and lost to time unless committed." Its cloud agent instead works with "every step happening in a commit and being viewable in logs" ([GitHub Docs](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent)). Entry points into that asynchronous surface include issue assignment, `@copilot` mentions on a pull request, and automations that run "on a schedule or in response to events" ([GitHub Docs](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent)). Claude Code's GitHub Action covers the same event and comment surfaces: it responds to `@claude` mentions and runs "automatically on any GitHub event" ([Claude Code GitHub Actions](https://code.claude.com/docs/en/github-actions)).

## Why it works

Chat suits unknown intent because each turn lets a person state and correct what they want, and the 42%-of-requests figure above shows later turns depending on earlier ones ([Ross et al.](https://arxiv.org/abs/2302.07080v1)). Once intent is fixed, staying in chat charges three costs that other surfaces avoid. A chat turn needs a person present to start it, which a schedule or an event trigger removes ([GitHub Docs](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent)). A chat transcript resets between sessions — "each new session begins with no memory of what came before" — where git history and progress files carry state across runs instead ([Anthropic](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)). And a chat turn calls the model again on a task it already solved, where a hook instead gives "deterministic control: certain actions always happen rather than relying on the LLM to choose to run them" ([Claude Code hooks guide](https://code.claude.com/docs/en/hooks-guide)).

The same split shows up in inline completion. A programmer who already knows the next step works in what Barke et al. call acceleration mode, where "long, multi-line suggestions are at best dismissed out of hand and at worst distract the programmer away from their flow" ([Barke et al.](https://arxiv.org/abs/2206.15000v3)).

## When this backfires

Moving a task off chat has a cost of its own, and four conditions make that cost the losing trade.

- The task is still ambiguous, exploratory, or a debugging session with an unknown cause. GitHub's own guidance for its background agent keeps this class of task off it by name: "Ambiguous tasks," "Learning tasks," "Complex and broadly scoped tasks," and "Sensitive and critical tasks" such as production incidents ([GitHub Docs](https://docs.github.com/en/copilot/tutorials/cloud-agent/get-the-best-results)).
- The task will not repeat often enough to earn back its setup. Holland's non-chat canvas "took the better part of a day to get the design and automation right" ([Holland](https://github.blog/ai-and-ml/github-copilot/when-chat-is-the-wrong-ui/)); a hook, a CI job, or a canvas built for a handful of runs never recovers that time.
- The event trigger accepts untrusted input on a broad tool grant, such as an arbitrary issue or PR comment. Moving off chat also removes the person who would have caught an injected instruction before it ran, which is why this site's own [comment-dispatch pattern](comment-triggered-agent-dispatch.md) limits that surface to bounded, reversible, cheap-to-verify work.
- Nobody has the review capacity to read what a background surface produces. Within the same repositories, merged agent pull requests attract a verified follow-up fix within 30 days at 1.62 times the odds of human pull requests — 3.68% against 2.34% ([Takerngsaksiri et al.](https://arxiv.org/abs/2609.26847v2)). Most of those fixes came from the same agent, so the cost lands on whoever reviews the second PR as well as the first.

A stronger version of the first point holds when the "chat" being replaced is already an agentic terminal session rather than a plain text box. A session that writes files, runs tests, and commits catches a wrong step at the moment it happens, where a background run leaves the correction to review time. Claude Code's own guidance leans the same way for most agentic coding: "the best results come from tight feedback loops," and "correcting it quickly generally produces better solutions faster" ([Claude Code best practices](https://code.claude.com/docs/en/best-practices)). Every surface that replaces that loop also has to be built, as a workflow file, a hook script, or a canvas. For a task that runs once, that build cost buys nothing.

## Example

Holland's post covers both ends of the setup-cost range, for two different task classes. His objection to chat starts with a repeated, deterministic request: "Stop asking GPT-5.6 Sol Max to 'stage and commit'" ([Holland](https://github.blog/ai-and-ml/github-copilot/when-chat-is-the-wrong-ui/)). His fix moves that request to a generated tool, on the reasoning that "it's almost always better to have the agent build a tool where all future interactions are free vs treating the agent itself as the tool" ([Holland](https://github.blog/ai-and-ml/github-copilot/when-chat-is-the-wrong-ui/)). Claude Code's best-practices guide makes the same argument for hooks: "hooks are deterministic and guarantee the action happens" ([Claude Code best practices](https://code.claude.com/docs/en/best-practices)). At the other end, Holland's Agent Loop canvas coordinates several agents with human gates, and it "took the better part of a day to get the design and automation right" ([Holland](https://github.blog/ai-and-ml/github-copilot/when-chat-is-the-wrong-ui/)). The commit request needed a small tool. The coordination task needed a day of build time, which pays back only if the loop runs many times.

## Key Takeaways

- Keep a task in chat while its intent is still forming. Once intent is known, move it off chat, and let repetition, run length, and triggers decide how much setup the destination earns.
- Earlier turns carry meaning in conversational coding: 42% of requests in one study needed earlier turns to be understood correctly.
- Moving a task off chat trades a per-run model cost for a one-time setup cost, from a small generated tool up to a canvas that took a day to build, and the larger builds pay off only if the task repeats.
- A background agent still needs review capacity: within the same repositories, merged agent PRs need a verified follow-up fix at 1.62 times the odds of human PRs.
- An event-triggered agent with a broad tool grant on untrusted input removes the person who would have caught an injected instruction, so scope the tool grant before removing the human.

## Related

- [Canvas as Durable Workflow State: The Four-Step Blueprint and What It Costs](../patterns/agent-design/canvas-as-durable-workflow-state.md) — the setup-cost case for the highest-investment surface in the table above
- [Comment-Triggered Agent Dispatch on Issues and PRs](comment-triggered-agent-dispatch.md) — the narrow tool-grant discipline the event-triggered row assumes
- [Headless Claude in CI: Using -p and --max-turns for Safe Pipeline Integration](headless-claude-ci.md) — running the CI-job row non-interactively with a turn cap
- [CLI-IDE-GitHub Context Ladder for AI Agent Development](cli-ide-github-context-ladder.md) — a complementary surface model organized by development phase rather than task shape
- [Deterministic Fast Paths: Answer Without a Model Call](../patterns/agent-design/deterministic-fast-paths.md) — the same "skip the model" reasoning applied to answering a question instead of dispatching a task
