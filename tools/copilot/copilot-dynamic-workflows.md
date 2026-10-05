---
title: "GitHub Copilot Dynamic Workflows: Orchestration in Code"
description: "How a Copilot dynamic workflow fixes a task's steps in code, where its permission boundary actually falls, and how the CLI and app surfaces differ."
term: "dynamic workflow"
aliases:
  - dynamic workflows
  - Copilot dynamic workflow
  - copilot workflow run
tags:
  - workflows
  - agent-design
  - copilot
applies_to: "copilot@1.x"
last_reviewed: 2026-10-02
status: current
---

# GitHub Copilot Dynamic Workflows

> A Copilot dynamic workflow is a program in a Copilot extension that fixes a task's steps and calls agents for analysis and judgment.

A dynamic workflow is a program that carries out a task and hands the parts needing analysis or judgment to one or more agents. GitHub defines it the same way: "A dynamic workflow is a program that defines how a task is carried out" ([GitHub Docs](https://docs.github.com/en/copilot/concepts/agents/dynamic-workflows)). GitHub announced it on 2026-10-01 for Copilot CLI, the Copilot app, and the Copilot SDK, on all Copilot plans. It remains in public preview ([GitHub Changelog](https://github.blog/changelog/2026-10-01-dynamic-workflows-in-copilot-cli-and-the-copilot-app)). The app needs no setup. The CLI needs experimental features on, through `--experimental` or `/experimental on` ([GitHub Docs](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-dynamic-workflows)).

## Where the permission boundary falls

Two layers sit here, and they are governed differently. The agent steps keep the graduated model already used in [Copilot CLI](copilot-cli-agentic-workflows.md). Subagents "use the CLI's permission system and inherit the permission grants of the session that started them". In an interactive CLI session, a request outside those grants surfaces as a normal permission prompt while that subagent waits. `copilot workflow run` shows no such prompts ([GitHub Docs](https://docs.github.com/en/copilot/concepts/agents/dynamic-workflows)). None of that needs the step list in advance, because approval attaches to each tool request rather than to a plan.

The workflow's own code sits outside it. A dynamic workflow is a Copilot extension, and "An extension can also run its own code directly, outside these permission prompts" (same page). Extensions carry a blunter warning: "Extensions execute on your computer with your privileges." Treat one like any script you did not write ([GitHub Docs](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-cli-extensions)). In the default Load & Augment mode, Copilot may scaffold an extension and reload it so code it just wrote runs without a session restart. Review the program rather than the steps it will pick.

## Choosing between a workflow, autopilot, and fleet

GitHub's comparison turns on who plans rather than on agent count ([GitHub Docs](https://docs.github.com/en/copilot/concepts/agents/dynamic-workflows)):

| Aspect | Autopilot | `/fleet` | Dynamic workflow |
|---|---|---|---|
| Who defines the process? | Copilot decides the next steps | Copilot decides how to divide and coordinate the work | The workflow author defines the steps, conditions, and handoffs |
| How work runs | Depends on the task and Copilot's decisions | Independent work can be delegated in parallel | The process can use one agent or many, with work happening in sequence, in parallel, or both |

Reuse covers the steps and the rules; GitHub notes the route through them still changes with the inputs. For anything short, the docs set the floor themselves: "For a quick answer or a simple change, a normal prompt in the standard chat mode is usually sufficient."

[GitHub Agentic Workflows](github-agentic-workflows.md) answer a different question. Those are repository Markdown files compiled to GitHub Actions and fired by repository events. Reach for them when a push or an issue comment is the trigger, and for a dynamic workflow when you start the run yourself.

## CLI and app differences

- Monitoring. `/workflows` in a CLI session, where `P` pauses, `X` cancels, and `R` resumes; a Workflows button above the prompt box in the app. In the app, "Run monitoring is only available for local sessions" ([GitHub Docs](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-dynamic-workflows)).
- CLI only. A headless entry point, `copilot workflow run`, plus scheduling through `/every` and `/after`.
- App only. Canvas controls, which an extension can supply to start a workflow.
- Sharing. Copy the extension directory to `~/.copilot/extensions/` for all your sessions, or to `.github/extensions/` to share it with a repository.

## Why it works

Moving the plan into a program deletes the step where each stage rebuilds state from the conversation. The survey *Code as Agent Harness* treats that rebuild as a cause rather than a convenience. Most multi-agent coding systems it reviews "rely on agents to reconstruct state implicitly from conversational history at each invocation", and without a formal shared substrate agents cannot reliably detect when their understanding of the program state has drifted. That makes implicit state "the technical root of system brittleness rather than a scalability convenience" ([arXiv:2605.18747v1](https://arxiv.org/abs/2605.18747v1)). A dynamic workflow supplies that substrate as program values, and it can fix their format: "A workflow can ask agents to return results in a specified format so that later steps can use them" ([GitHub Docs](https://docs.github.com/en/copilot/concepts/agents/dynamic-workflows)).

## Example

Run an existing workflow from a script. The command shows no approval prompts, so every permission the agents need is granted up front ([GitHub Docs](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-dynamic-workflows)):

```bash
copilot workflow run java-security-checks \
   --args @workflow-input.json \
   --result-file security-results.json \
   --allow-tool=read
```

Read the exit code before the result file. Exit `1` covers a pause, a limit that stopped the run, a cancellation, and a failure alike. An older result file may still be there from a previous run ([GitHub Docs](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-programmatic-reference)). To tell those cases apart, add `--output-format json` and read `data.run.status`, which reports `completed`, `halted`, `paused`, `cancelled`, or `error`.

## When this backfires

- Headless runs starved of permissions. `copilot workflow run` prints no prompts, and "Requests that cannot be approved automatically are denied", so a workflow that worked interactively loses steps in CI unless `--allow-tool` and `--allow-url` cover everything its agents touch.
- Pipelines that read a non-zero exit as a crash. To a script checking only the exit code, the checkpoint pause that makes these workflows attractive looks the same as a failure.
- Spend bounded by an estimate. Usage is reported after it occurs, so work already underway can carry the total past the [AI credit](../../human/copilot-vs-claude-billing-semantics.md) limit: "This is an approximate maximum, not a hard ceiling." A workflow that launches many subagents "can take a long time to complete and consume a large number of AI credits", so test at small scope first. Limits can be defined in three places: your prompt, the workflow, and your personal settings. A limit in your prompt overrides the other two ([GitHub Docs](https://docs.github.com/en/copilot/concepts/agents/dynamic-workflows)).
- Repository code you have not read. A shared workflow is executable JavaScript in `.github/extensions/`, run with your privileges, and `GITHUB_COPILOT_PROMPT_MODE_EXTENSIONS=true` permits loading project extensions in automation.
- Version drift. A revised workflow reaches teammates only after they pull the repository and reload extensions, so two people can run one workflow name at different versions.
- One-off work, where fixing interfaces in advance becomes the constraint. Bechard et al. found a minimal terminal agent matching or beating more structured architectures on enterprise automation, and named the cause: "tool-use agents underperform due to rigid tool interfaces that limit which fields can be set and which query patterns can be expressed" ([arXiv:2604.00073v3](https://arxiv.org/abs/2604.00073v3)). The authors frame that result as "a property of the tool catalogs we test, not an inherent limitation of the MCP protocol itself", and say it characterizes "the servers we evaluated, not the full space of MCP implementations". Their Appendix C.6 compares a single agent with a planner-executor design and reports that with Opus 4.6 the accuracy gap "disappears almost entirely", and suggests that "explicit multi-agent orchestration primarily compensates for limitations in the underlying model's ability to reason over complex task structures".

## Key Takeaways

- A dynamic workflow is a program in a Copilot extension; its author fixes the steps, conditions, and handoffs, and agents handle the analysis or judgment
- Subagents inherit the session's permission grants and, in an interactive CLI session, prompt for anything new, so no fixed step list is needed to govern them
- The extension's own code runs outside those prompts, with your privileges, which makes the program the thing to review
- `copilot workflow run` is the headless path: pre-grant permissions, then check the exit code before the result file, and read `data.run.status` to tell a pause from a failure
- Limits can be defined in three places, and a limit named in the prompt overrides the other two
- The feature is in public preview and subject to change, so confirm behavior against the docs before automating against it

## Related

- [Copilot CLI Agentic Workflows](copilot-cli-agentic-workflows.md)
- [GitHub Agentic Workflows](github-agentic-workflows.md)
- [Claude Code Dynamic Workflows](../claude/dynamic-workflows.md)
- [GitHub Copilot App Slash Commands and What They Change](slash-commands-copilot-app.md)
- [Orchestrator-Worker Pattern for AI Agent Development](../../patterns/multi-agent/orchestrator-worker.md)
