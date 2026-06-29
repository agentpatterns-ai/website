---
title: "Claude Code Dynamic Workflows"
description: "Claude writes a JavaScript script that a background runtime executes to orchestrate subagents at scale, keeping the orchestration plan and intermediate results out of Claude's context."
aliases:
  - "dynamic workflows"
  - "workflow orchestration script"
tags:
  - agent-design
  - context-engineering
  - cost-performance
  - claude
applies_to: "claude-code@2.x"
last_reviewed: 2026-06-03
status: current
---

# Claude Code Dynamic Workflows

> A workflow is a JavaScript script Claude writes and the runtime executes to orchestrate subagents at scale, keeping intermediate results out of Claude's context.

## How they work

[Dynamic workflows](https://code.claude.com/docs/en/workflows) (research preview, requires Claude Code v2.1.154 or later) move the orchestration plan out of the conversation and into a script. You describe a task, Claude writes a JavaScript script that coordinates [subagents](sub-agents.md), and a background runtime executes it while your session stays responsive. The script holds the loop, the branching, and the intermediate results. Only the final answer returns to your context.

Reach for a workflow when a task needs more agents than one conversation can coordinate, or when the orchestration is worth codifying as something you can rerun — a codebase-wide bug sweep, a 500-file migration, or cross-checked research.

Workflows are available on all paid plans, the Anthropic API, Amazon Bedrock, Google Cloud Vertex AI, and Microsoft Foundry. On Pro, enable them from the Dynamic workflows row in `/config`.

## Workflows vs sub-agents vs skills

All three run a multi-step task. The difference is who holds the plan ([source](https://code.claude.com/docs/en/workflows#when-to-use-a-workflow)).

| | Sub-Agents | Skills | Workflows |
|---|---|---|---|
| What it is | A worker Claude spawns | Instructions Claude follows | A script the runtime executes |
| Who decides what runs next | Claude, turn by turn | Claude, following the prompt | The script |
| Where intermediate results live | Claude's context | Claude's context | Script variables |
| What's repeatable | The worker definition | The instructions | The orchestration itself |
| Scale | A few per turn | A few per turn | Dozens to hundreds per run |
| Interruption | Restarts the turn | Restarts the turn | Resumable in the same session |

Because the script holds the intermediate results, the orchestrator's context stays clean, which lets one run coordinate up to 1,000 agents. Moving the plan into code also lets a workflow apply a repeatable quality pattern, not just run more agents. For example, independent agents can review each other's findings, or draft a plan from several angles and weigh them, before anything is reported.

## Writing and running a workflow

The bundled `/deep-research` workflow is the quickest demonstration (requires the WebSearch tool). To turn your own task into a workflow, ask for one in plain language ("run a workflow to…") or include the trigger keyword in your prompt, and Claude writes one instead of working turn by turn. The trigger keyword [changed to `ultracode` in v2.1.160](https://code.claude.com/docs/en/workflows#ask-for-a-workflow-in-your-prompt) (it was `workflow` before); natural-language requests work in both. Setting `/effort ultracode` (xhigh reasoning plus automatic workflow orchestration) lets Claude decide when a task warrants one.

Once a run does what you wanted, open `/workflows`, select it, and press `s` to save the script as a `/<name>` command — in `.claude/workflows/` to share with the repo, or `~/.claude/workflows/` for personal use.

## Runtime and limits

The runtime executes the script in an isolated environment, separate from your conversation, and tracks each agent's result so a run is [resumable](https://code.claude.com/docs/en/workflows#how-a-workflow-runs) within the same session. Resume only works in-session: exit Claude Code mid-run and the next session starts the workflow fresh. The runtime caps a run at up to 16 concurrent agents and 1,000 agents total, takes no mid-run user input (only agent permission prompts can pause it), and gives the script no direct filesystem or shell access — the agents read, write, and run commands; the script only coordinates them.

Subagents spawned by a workflow always run in `acceptEdits` mode and inherit your [tool allowlist](https://code.claude.com/docs/en/settings#permission-settings); tools outside the allowlist can still prompt mid-run.

## Example

A bundled run needs only a question. The agents work in the background and one cited report lands when they finish:

```text
/deep-research What changed in the Node.js permission model between v20 and v22?
```

For your own task, a plain-language request (or the `ultracode` keyword on v2.1.160+) routes a single prompt through the runtime instead of a turn-by-turn pass:

```text
Run a workflow to audit every API endpoint under src/routes/ for missing auth checks
```

Claude writes the orchestration script, the approval prompt shows the planned phases, and the run proceeds in the background. If it does what you wanted, save it from `/workflows` with `s` so the same orchestration reruns on every branch.

## When this backfires

- Token cost scales with agent count. A run that spawns dozens of agents can use far more tokens than working the same task in conversation. Every agent uses your session's model unless the script routes a stage elsewhere, so check `/model` before a large run.
- No mid-run sign-off. The runtime takes no user input mid-run, so a workflow cannot pause for approval between stages. For staged sign-off, run each stage as its own workflow.
- Research preview. The feature and its limits may change, so gate dependent automation behind a version check and confirm against the [canonical docs](https://code.claude.com/docs/en/workflows).
- Overkill for linear work. A task one conversation can hold needs [sub-agents](sub-agents.md) or [agent teams](agent-teams.md), not the overhead of a script. Workflows earn their cost only when scale or repeatability is the point.

## Key Takeaways

- A workflow is a script Claude writes and a background runtime executes, moving the orchestration plan out of the conversation
- Intermediate results live in script variables, so the orchestrator's context holds only the final answer — enabling up to 1,000 agents per run
- The decision axis is who holds the plan: Claude turn-by-turn (sub-agents, skills) versus the script (workflows)
- `/deep-research` is bundled; a plain-language request, the `ultracode` keyword (v2.1.160+; `workflow` before it), or `/effort ultracode` has Claude write one; save a run as a `/<name>` command
- Research preview (v2.1.154+); disable via `/config`, `"disableWorkflows": true`, or `CLAUDE_CODE_DISABLE_WORKFLOWS=1`

## Related

- [Sub-Agents](sub-agents.md)
- [Claude Code Agent Teams](agent-teams.md)
- [Deterministic Orchestration for Structured Modernization](../../agent-design/deterministic-orchestration-structured-modernization.md)
- [Orchestrator-Worker Pattern for AI Agent Development](../../multi-agent/orchestrator-worker.md)
- [Sub-Agents for Fan-Out Research and Context Isolation](../../multi-agent/sub-agents-fan-out.md)
- [Claude Code Feature Flags and Environment Variables](feature-flags.md)
