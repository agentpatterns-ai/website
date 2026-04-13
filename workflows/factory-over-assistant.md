---
title: "Factory Over Assistant: Orchestrating Parallel Agent Fleets"
description: "The shift from watching one agent in a sidebar to orchestrating multiple parallel agents with automated feedback loops — and the infrastructure required to make it work."
tags:
  - workflows
  - human-factors
  - multi-agent
  - tool-agnostic
aliases:
  - factory model
  - assistant model
---

<!-- source: nibzard/awesome-agentic-patterns (Apache 2.0, https://github.com/nibzard/awesome-agentic-patterns) — retain attribution per license -->

# Factory Over Assistant: Orchestrating Parallel Agent Fleets

> The assistant model ties human attention to a single execution stream. The factory model replaces that attention with automated feedback loops and adds parallelism — but only once the infrastructure to support it is in place.

## The Two Models

**Assistant model**: one human watches one agent in a sidebar. The human is the feedback loop — answering questions, correcting drift, approving actions in real time. The agent can only proceed as fast as the human can respond.

**Factory model**: one human orchestrates multiple parallel agents. Automated systems — tests, CI, linters, build pipelines — are the primary feedback mechanism. The human reviews outputs asynchronously rather than watching execution.

| Dimension | Assistant model | Factory model |
|-----------|----------------|---------------|
| Agents active | 1 | Multiple (parallel) |
| Human role | Real-time watcher | Asynchronous reviewer |
| Feedback source | Human attention | Automated systems |
| Time on execution | ~80% | ~20% |
| Time on review/integration | ~20% | ~50%+ |
| Time on infrastructure setup | Minimal | ~30% |

[Source: [awesome-agentic-patterns / factory-over-assistant](https://github.com/nibzard/awesome-agentic-patterns/blob/main/patterns/factory-over-assistant.md)]

## Why the Assistant Model Fails at Scale

As autonomous agent sessions extend beyond a few minutes, the assistant model inverts the intended ratio: most human time goes to watching rather than deciding. Three structural problems compound:

**Single-stream constraint.** You can only watch one agent at a time. A second agent running simultaneously requires a second human — or a shift to asynchronous review.

**Human as bottleneck.** When the human is the feedback loop, agent speed is bounded by human response time. Automated checks run in milliseconds; humans do not.

**Wrong surface.** Editor-centric assistant UIs optimize for observation, not orchestration. Experienced developers spend the majority of their time outside the editor — in code review, planning, debugging, and integration — yet assistant-model tools anchor attention to the editor pane.

## Infrastructure Prerequisites

The factory model is not a mindset change — it requires systems that replace real-time human oversight:

**Automated feedback loops.** Tests, linters, build checks, and CI pipelines must be authoritative enough for agents to self-correct. If a test is ambiguous or flaky, the agent cannot use it to determine whether its output is correct. Invest in making verification rock-solid before removing human attention.

**Monitoring and signal.** You need to know when an agent is blocked, failed, or finished — without watching continuously. Claude Code agent teams provide `TeammateIdle` hooks that fire when a teammate goes idle, letting you build automated responses or notification pipelines. [Source: [Claude Code agent teams](https://code.claude.com/docs/en/agent-teams)]

**Task isolation.** Parallel agents editing shared files produce conflicts. Worktree isolation ([Worktree Isolation](worktree-isolation.md)) gives each agent a private sandbox. Each agent's output lands on a separate branch, reviewed via PR before merge.

**Skill libraries.** Agents in autonomous mode rely on documented conventions rather than real-time clarification. Encoding your process in CLAUDE.md files, skill definitions, and agent system prompts substitutes for the guidance you would have provided interactively.

## Throughput Claims

Anthropic's internal multi-agent research system (lead agent + parallel subagents) outperformed single-agent Claude Opus 4 by 90.2% on internal research evaluations and reduced research time by up to 90% for complex queries. [Source: [Anthropic: multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)]

The mechanism: parallelization eliminates sequential bottlenecks when tasks are independent and feedback is automated.

## Where the Factory Model Fails

The factory model assumes automatable feedback. It breaks down when:

- **Goals are exploratory or undefined.** Automated tests cannot validate what "correct" means for open-ended research or product discovery.
- **Tasks require frequent guidance.** If an agent needs human input every few minutes, the async review model adds latency without removing attention load.
- **Domain knowledge is not documented.** Agents operating autonomously rely on written conventions. Tacit knowledge that exists only in developers' heads produces misaligned output. See [Encoding Tacit Knowledge into Agent Improvement Loops](encoding-tacit-knowledge.md) for extraction techniques.
- **Verification is unreliable.** If CI is flaky or tests are insufficient, agents optimize for passing the gate rather than solving the actual problem.
- **Safety-critical decisions are required.** Architecture choices, security boundaries, and product trade-offs that require human judgment should not be automated away.

## Example

A team running a large-scale API migration sets up the factory model before spawning agents:

1. **Verify the feedback layer**: all migration tests are deterministic and cover the relevant contracts. CI enforces type checking and integration tests.
2. **Decompose the work**: the migration is split into 12 independent module tasks with no shared state.
3. **Fan out**: 12 agents launch in parallel, each in an isolated worktree, each with a task-scoped prompt pointing to the relevant module and test suite.
4. **Asynchronous review**: agents open PRs on completion. The human reviews diffs, not executions. Failed CI blocks merges automatically.

```bash
# Fan out 12 agents across worktrees
for module in $(cat migration-modules.txt); do
  git worktree add "../wt-${module}" -b "agent/migrate-${module}"
  claude --worktree "../wt-${module}" \
    --permission-mode auto \
    -p "Migrate ${module} per MIGRATION.md. Run tests. Open a PR when done." &
done
wait
```

The human's constraint is now PR review throughput, not agent execution speed.

## Key Takeaways

- The factory model requires automated feedback loops, monitoring infrastructure, task isolation, and documented conventions — not just the decision to run parallel agents
- Build and validate the feedback layer before removing real-time oversight; unreliable tests produce misaligned autonomous output
- The assistant model remains appropriate for exploratory work, novel problems, safety-critical decisions, and tasks requiring frequent human guidance
- Throughput gains come from removing sequential bottlenecks, not from adding agents to tasks that are inherently sequential

## Related

- [Parallel Agent Sessions](parallel-agent-sessions.md)
- [Worktree Isolation](worktree-isolation.md)
- [Attention Management with Parallel Agents](../human/attention-management-parallel-agents.md)
- [The Bottleneck Migration](../human/bottleneck-migration.md)
- [Single-Branch Git for Agent Swarms](single-branch-git-agent-swarms.md)
- [Sub-Agents for Fan-Out Research and Context Isolation](../multi-agent/sub-agents-fan-out.md)
- [Fan-Out and Synthesis](../multi-agent/fan-out-synthesis.md)
- [Swarm Migration Pattern](../multi-agent/swarm-migration-pattern.md)
