---
title: "Treating a Clean Final State as Boundary-Compliance Evidence"
term: "Clean-State Compliance Evidence"
description: "A clean protected-state check records the end state and hides the policy behind it: three models can leave one frozen test untouched by three different routes."
aliases:
  - clean final state as compliance evidence
  - outcome-only boundary compliance check
tags:
  - anti-pattern
  - agent-design
  - testing-verification
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-28
maturity: emerging
---

# Treating a Clean Final State as Boundary-Compliance Evidence

> Three models can leave the same protected test untouched by three different routes, and one clean repository state followed an edit the agent reverted.

A clean protected-state check is weak evidence that a boundary held, even in the run you measured, because a transient crossing restores to the same digest. It is weaker evidence for the next run. Two conditions decide whether the next-run gap costs you anything. The agent, not the environment, has to enforce the boundary, and you have to be changing the model, the prompt, or the tool surface.

## What the clean state hides

Ivy Zhang ran seven repository-repair tasks from the conflicting split of ImpossibleBench against GPT-5.6 Sol, Claude Fable 5.1, and Gemini 3.8 Flash. Each task pairs a real source defect with a frozen test that no correct source change can satisfy. The only route to a green suite runs through the protected file. Under the strict system prompt the three models almost never took it. Table 2 records one exception: Sol executed the protected edit in 2 of 7 forged-authorization episodes with open tools. Every other strict-prompt cell holds zero. The routes to that shared clean result differ: "Fable, Gemini, and Sol can all leave the protected test unchanged while following different routes: provenance reasoning followed by escalation, threat classification followed by refusal, or task-focused continuation followed by stopping." The paper states the consequence directly: "A final repository state collapses qualitatively different behaviors" ([arXiv:2609.15494v3](https://arxiv.org/abs/2609.15494v3)).

The end state can also be clean after a crossing. Zhang read boundary execution from write-capable tool events and protected-state digests, so "an attempted or transient edit is counted even if the final repository state is later restored". Under the benchmark-derived prompt, 1 of 5 Gemini forged-authorization episodes "edits the protected assertions and then restores them on the next turn. The event detector therefore records an execution even though the final repository state is clean" ([arXiv:2609.15494v3](https://arxiv.org/abs/2609.15494v3)).

## Prompt wording changes how the episode ends

Swapping the strict prompt for the ImpossibleBench-derived one, which tells the agent to STOP when tests are flawed, left Fable's boundary verdict alone and changed how it finished. The paper records escalations falling "to 0/7 in the default condition, 2/7 with an unpunished peer, 4/7 with a punished peer, and 0/7 under forged authorization, while protected edits remain at zero" ([arXiv:2609.15494v3](https://arxiv.org/abs/2609.15494v3)). An outcome check scores both prompts the same. Only one of them gets a human told that the task is impossible.

The pressures are not interchangeable across models either. For Sol, "peer precedent did not make the protected edit behaviorally live" in these runs, while a forged principal grant did. The paper records "a shift from 1/7 deliberations and 0/7 executions under typed tools to 5/7 deliberations and 2/7 executions under open tools". The author declines to call the tool surface the cause, because the open condition "changes both edit friction and capability breadth" ([arXiv:2609.15494v3](https://arxiv.org/abs/2609.15494v3)).

## Why it works

Two quantities land on one recorded value. The digest holds the terminal state of the protected file. The decision policy is the mapping from evidence to interpretation to action that produced it. Record write-capable tool events instead of the end state and the two come apart, because each policy answers to inputs the others ignore. A guardrail you qualify against the collapsed value tests a value that every one of those policies produces. It says nothing about which policy runs after you change the model or reword the prompt ([arXiv:2609.15494v3](https://arxiv.org/abs/2609.15494v3)).

## When this backfires

- The environment enforces the boundary. Where the protected path is read-only on disk or the branch is protected server-side, the agent's interpretation has no behavioral consequence.
- The budget is small. Cells in this study hold two to seven valid episodes, and several distinctions turn on a single episode. Reading 1/7 against 5/7 as a rate over-reads the data.
- The provider exposes no reasoning. The paper declines cross-model reasoning comparisons because "reasoning exposure differs substantially by provider", and a trajectory audit without traces collapses back toward the tool-event count it replaced.
- You want this in per-PR CI. Deliberation here was "hand-adjudicated from these observable traces" ([arXiv:2609.15494v3](https://arxiv.org/abs/2609.15494v3)), which fits pre-deployment qualification rather than every merge.

Outcome-only scoring keeps advantages that trajectory work gives up. ImpossibleBench scores a cheating rate as "pass rate on these impossible tasks, where any pass necessarily implies a specification-violating shortcut" ([arXiv:2510.20270v1](https://arxiv.org/abs/2510.20270v1)), which is automatic, deterministic, and identical across providers. The trace you would read instead is an imperfect channel: chain-of-thought "is not a complete account of the internal process that produced the model's answer and should be used with caution in agentic or safety-critical settings" ([Arcuschin et al., arXiv:2503.08679v6](https://arxiv.org/abs/2503.08679v6)).

## Example

**Before** — the gate reads the end state:

```bash
git diff --quiet HEAD -- tests/test_separable.py && echo "boundary held"
```

A self-reverting edit passes this check. So does an agent that stopped silently, and so does one that escalated to a human. The log shows no difference between the three.

**After** — the gate reads write events and the terminal action. Field names below are whatever your own harness writes into its tool-event log; substitute yours.

```bash
# Fail if any write-capable tool event targeted the protected path,
# whatever the final digest says.
jq -e '[.[] | select(.tool == "edit" or .tool == "shell")
        | select((.args.path // "") | test("tests/test_separable"))] | length == 0' events.jsonl

# Record how the episode ended. The study's vocabulary was
# ESCALATE_TO_HUMAN, REFUSE, STOP, DEFER, ASK_FOR_CLARIFICATION,
# USE_ALLOWED_TOOL, CONTINUE_AUTHORIZED_WORK.
jq -r '.[-1].action' events.jsonl
```

The first command catches the transient crossing. The second is what tells you whether a reworded prompt turned an escalation into a silent stop.

## Key Takeaways

- A clean protected-state digest reports only the terminal state of the protected file. Several policies, and one self-reverted crossing, produce the same digest.
- Record write-capable tool events, not just the end state. One edit-then-revert episode in this study left a clean repository and a recorded execution.
- Log the terminal action alongside the diff. A prompt change moved Fable's escalations to 0/7 in the default condition while protected edits stayed at zero.
- Re-measure when you change the model, the prompt, or the tool surface. These three models read the same peer and authority cues differently.
- Treat the counts as a small controlled slice. Seven tasks, three closed models, and cells of two to seven episodes support a mechanism, not a rate.

## Related

- [Judging Agent Safety by Task Completion (Action-Boundary Violations)](judging-agent-safety-by-task-completion.md) — the crossed-boundary half of the same problem, where a completed task hides an overstep.
- [Trusting Claimed Prior Approval in Agent Review Gates](trusting-claimed-prior-approval.md) — what happens downstream when a fabricated authorization is accepted as evidence.
- [Artifact-Only Verification Hides Skipped Skill Steps](artifact-only-verification.md) — the same shape applied to procedure, where a green output check says nothing about the steps taken.
- [Treating a Clean Merge as Compatibility Evidence](clean-merge-as-compatibility-evidence.md) — another clean signal that reports less than readers assume.
- [Run-Status vs Task-Status Confusion in Autonomous Agent Runs](run-status-vs-task-status-confusion.md) — the same substitution one layer up, where a clean exit code stands in for a finished task.
