---
title: "The Return Assumption: Status 0 Without the Action"
term: "Return Assumption"
description: "With input closed, 18 of 156 prompting commands returned status 0 without acting. A clean exit says how a command ended, not that it did the work."
aliases:
  - return assumption
  - false return
  - closed-stdin false success
tags:
  - agent-design
  - tool-agnostic
  - anti-pattern
  - arxiv
last_reviewed: 2026-11-05
maturity: emerging
status: current
---

# The Return Assumption: Status 0 Without the Action

> An agent that reads status 0 as proof the action happened misses commands that asked a question, read end of file, and skipped the work.

The return assumption is the belief that each tool call returns "within a bounded time and with its requested action finished" ([arXiv:2611.01930v1](https://arxiv.org/abs/2611.01930v1)). It fails when a command asks a question before it acts and nobody answers. Seven of the 8 tested harnesses close the command's input when no terminal is attached. The program then reads end of file (EOF). It can then take its default and return status 0 without acting.

## When this applies

Three conditions have to hold together:

- The command changes state: deletes, prunes, migrations, key generation, rebases.
- The command asks before it acts, with a confirmation, a passphrase, an editor, or a pager.
- The harness closes input or holds a terminal nobody types at. The 8 tested include Claude Code, Codex CLI, and OpenCode. Without an attached terminal, "every harness except Terminus 2 closes the input of a plain command" ([arXiv:2611.01930v1](https://arxiv.org/abs/2611.01930v1)).

## The anti-pattern

The agent runs `docker system prune` or `rm -i old/*`, sees exit status 0, and reports the cleanup done. Yang et al. ran 158 prompting invocations of 77 programs with no reply. Under closed input, 18 of 156 (11.5%) returned status 0 without the requested action: "docker system prune removes nothing, rm -i and rm -I leave the files, and find -ok and tar -w skip every entry" ([arXiv:2611.01930v1](https://arxiv.org/abs/2611.01930v1)). Another 12 went the other way and acted without the safeguard, as `ssh-keygen` does when it writes a key with an empty passphrase.

The 11.5% is a share of commands chosen because they prompt. It is not a share of all agent tool calls.

Keeping input open trades one failure for two others. At a plain terminal, Tripwire trap runs "take 2.6 times the total run time and 2.9 times the tokens of the controls." In a persistent terminal, "the next scheduled keystroke becomes the answer to the question." Native Terminus 2 fed a queued `cd` to a migration script's prompt and rebuilt the database ([arXiv:2611.01930v1](https://arxiv.org/abs/2611.01930v1)).

## Why it works

Exit status reports how a process ended. It does not record whether the process read a reply or EOF: "The tool result does not show whether the program read a reply or EOF" ([arXiv:2611.01930v1](https://arxiv.org/abs/2611.01930v1)). Agents pick their next step from tool results, so a skipped action and a finished one look the same. The authors trace the gap to conventions that "assume a person who watches the program."

Transcript review can miss the failure. A post-hoc trajectory classifier "flags only 6 of these 34 false successes at a 10% flag rate" ([arXiv:2611.01930v1](https://arxiv.org/abs/2611.01930v1)).

## What to do instead

- Check the postcondition after every state-changing command. List the files, query the row, read the key. The paper describes state-based tests and developer-written postconditions as checks on requested effects ([arXiv:2611.01930v1](https://arxiv.org/abs/2611.01930v1)).
- Use the command's non-interactive options for an action you have approved. Do not count on harness environment variables. "No harness sets DEBIAN\_FRONTEND or CI", and the 8 harnesses' environment settings together prevented 30 of 70 replayed waits ([arXiv:2611.01930v1](https://arxiv.org/abs/2611.01930v1)).
- If you own the harness, report the wait to the agent. The authors' Receipt keeps input open, reads from the kernel what each process waits on, and returns that state. Across 5 LLMs in mini-SWE-agent it cut false successes from 34 to 9 and used 24.4% fewer tokens than a plain terminal ([arXiv:2611.01930v1](https://arxiv.org/abs/2611.01930v1)).

## When this backfires

Keeping input open also has a cost. An OpenCode issue reports commands that wait for stdin until timeout and asks to "default child stdin to closed instead of an open pipe" ([OpenCode #42773](https://github.com/anomalyco/opencode/issues/42773)).

The agent-level numbers have limits. Tripwire is the authors' own benchmark. The five-model false-success comparison uses Qwen and Llama models from 7B to 72B. It includes no hosted API model ([arXiv:2611.01930v1](https://arxiv.org/abs/2611.01930v1)). Of 70 Terminal-Bench 2.0 replayed waits that recur, closed input gives 41 status-0 returns. Of those, 12 skip the command's work ([arXiv:2611.01930v1](https://arxiv.org/abs/2611.01930v1)). The authors report that in "none of the 28 tasks whose waits recur does a confirmation question guard the requested action" ([arXiv:2611.01930v1](https://arxiv.org/abs/2611.01930v1)). These public tasks therefore cannot score the guarded-action failures that Tripwire measures.

## Key Takeaways

- Find out what your harness does with a command's input before you trust its exit codes. Closed input turns a prompt into a silent skip, and a persistent terminal turns it into a hijacked keystroke.
- Put the check where the effect lands. A trajectory classifier run after the fact flagged 6 of 34 false successes at a 10% flag rate ([arXiv:2611.01930v1](https://arxiv.org/abs/2611.01930v1)).
- Choose the command's input mode explicitly. Check whether an unanswered question skips the action, bypasses confirmation, or keeps waiting.

## Related

- [Unsignalled Tool Failure: Returning Success With an Unusable Payload](unsignalled-tool-failure-envelope.md) — the tool-wrapper version of a success envelope around a failure
- [Tool-Call Success as Workflow Effect Evidence](tool-call-success-as-workflow-evidence.md) — every call succeeded and the external effects are still wrong
- [Run-Status vs Task-Status Confusion](run-status-vs-task-status-confusion.md) — the same mix-up one level up, at the whole agent run
- [Override Pattern: Reusing Interactive Commands in Automated Pipelines](../../tool-engineering/override-interactive-commands.md) — suppressing prompts at the command-definition layer
- [Agent-Aware CLI Behavior via Environment Variable](../../tool-engineering/agent-aware-cli-via-env-var.md) — a harness-to-CLI contract that lets a CLI skip prompts on purpose
