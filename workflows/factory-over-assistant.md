---
title: "Factory Over Assistant: Orchestrating Parallel Agent Fleets"
term: "Factory Over Assistant"
description: "The shift from watching one agent in a sidebar to orchestrating multiple parallel agents with automated feedback loops — and the infrastructure required to make it work."
tags:
  - workflows
  - human-factors
  - multi-agent
  - tool-agnostic
  - agent-design
aliases:
  - factory model
  - assistant model
last_reviewed: 2026-06-12
maturity: established
---

<!-- source: nibzard/awesome-agentic-patterns (Apache 2.0, https://github.com/nibzard/awesome-agentic-patterns) — retain attribution per license -->

# Factory Over Assistant: Orchestrating Parallel Agent Fleets

> The factory model replaces real-time human attention with automated feedback loops and parallel agents — but only once the supporting infrastructure is in place.

Related lesson: [Becoming a Tech Lead](https://learn.agentpatterns.ai/workflows/becoming-a-tech-lead/) — this concept features in a hands-on lesson with quizzes.

## The two models

Assistant model: one human watches one agent in a sidebar. The human is the feedback loop. They answer questions, correct drift, and approve actions in real time. The agent proceeds only as fast as the human can respond.

Factory model: one human runs multiple [parallel agent sessions](parallel-agent-sessions.md). Automated systems give the main feedback: tests, CI, linters, and build pipelines. The human reviews outputs afterwards instead of watching them run.

| Dimension | Assistant model | Factory model |
|-----------|----------------|---------------|
| Agents active | 1 | Multiple (parallel) |
| Human role | Real-time watcher | Asynchronous reviewer |
| Feedback source | Human attention | Automated systems |
| Time on execution | ~80% | ~20% |
| Time on review/integration | ~20% | ~50%+ |
| Time on infrastructure setup | Minimal | ~30% |

[Source: [awesome-agentic-patterns / factory-over-assistant](https://github.com/nibzard/awesome-agentic-patterns/blob/main/patterns/factory-over-assistant.md)]

## Why the assistant model fails at scale

When agent sessions run for more than a few minutes, the assistant model inverts the ratio you want: most human time goes to watching, not deciding. Three structural problems compound:

Single-stream constraint. You can watch only one agent at a time. A second agent running at the same time needs a second human, or a shift to asynchronous review.

Human as bottleneck. When the human is the feedback loop, human response time caps agent speed. [The bottleneck migration](../human/bottleneck-migration.md) tackles this constraint directly. Automated checks run in milliseconds; humans do not.

Wrong surface. Editor-centric assistant tools optimize for watching, not coordinating. Experienced developers spend most of their time outside the editor, in code review, planning, debugging, and integration. Assistant-model tools still anchor attention to the editor pane.

## Infrastructure prerequisites

The factory model is not a mindset change. It needs systems that replace real-time human oversight:

Automated feedback loops. Tests, linters, build checks, and CI pipelines must be reliable enough for agents to self-correct. An agent cannot tell whether its output is correct from an ambiguous or flaky test. Make [verification dependable](verification-centric-development.md) before you remove human attention.

Monitoring and signal. You need to know when an agent is blocked, has failed, or has finished, without watching all the time. Claude Code agent teams provide `TeammateIdle` hooks that fire when a teammate goes idle, so you can build automated responses or notification pipelines. [Source: [Claude Code agent teams](https://code.claude.com/docs/en/agent-teams)]

Task isolation. Parallel agents editing shared files create conflicts. [Worktree isolation](worktree-isolation.md) gives each agent a private sandbox. Each agent's output lands on a separate branch, reviewed by PR before merge.

Skill libraries. Autonomous agents rely on documented conventions, not real-time clarification. Write your process into CLAUDE.md files, skill definitions, and agent system prompts. This stands in for the guidance you would have given interactively.

## Throughput claims

Anthropic's internal multi-agent research system (a lead agent plus parallel subagents) outperformed single-agent Claude Opus 4 by 90.2% on internal research evaluations. It cut research time by up to 90% for complex queries. [Source: [Anthropic: multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)]

The mechanism: parallel work removes sequential bottlenecks when tasks are independent and feedback is automated.

## Where the factory model fails

The factory model assumes feedback you can automate. It breaks down when:

- Goals are exploratory or undefined. Automated tests cannot define what "correct" means for open-ended research or product discovery.
- Tasks need frequent guidance. If an agent needs human input every few minutes, asynchronous review adds latency without removing the attention load.
- Domain knowledge is not written down. Autonomous agents rely on written conventions in `AGENTS.md` or `CLAUDE.md`. Knowledge that lives only in developers' heads produces misaligned output. See [Encoding Tacit Knowledge into Agent Improvement Loops](encoding-tacit-knowledge.md) for extraction techniques.
- Verification is unreliable. If CI is flaky or tests are thin, agents optimize for passing the gate rather than solving the real problem.
- Safety-critical decisions are required. Architecture choices, security boundaries, and product trade-offs need human judgment. Do not automate them away.

These failure rates are not hypothetical. The MAST taxonomy, built from more than 1,600 annotated traces across seven multi-agent frameworks, found per-framework failure rates of 41% to 87%. Specification ambiguity caused 41.77% of failures, coordination breakdowns 36.94%, and verification gaps 21.30%. [Source: [Why Do Multi-Agent LLM Systems Fail? (Cemri et al., NeurIPS 2025)](https://arxiv.org/abs/2503.13657)] Treat the infrastructure prerequisites above as the floor for keeping a deployment out of the high end of that range. Unambiguous specs, deterministic verification, and explicit coordination protocols separate a working fleet from a 17x error multiplier.

## Example

A team running a large API migration sets up the factory model before it starts any agents:

1. Verify the feedback layer. All migration tests are deterministic and cover the relevant contracts. CI enforces type checking and integration tests.
2. Decompose the work. Split the migration into 12 independent module tasks with no shared state.
3. Fan out. Launch 12 agents in parallel, each in an isolated worktree, each with a task-scoped prompt pointing to its module and test suite.
4. Asynchronous review. Agents open PRs when they finish. The human reviews diffs, not executions. Failed CI blocks merges automatically.

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

The human's constraint is now PR review throughput across all 12 PRs, not agent execution speed.

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
- [Sub-Agents for Fan-Out Research and Context Isolation](../patterns/multi-agent/sub-agents-fan-out.md)
- [Fan-Out and Synthesis](../patterns/multi-agent/fan-out-synthesis.md)
- [Swarm Migration Pattern](../patterns/multi-agent/swarm-migration-pattern.md)
- [Burn the Boats](burn-the-boats.md) — Commitment-forcing deprecation that enables the factory paradigm
- [The Software Factory Model: Industrializing Agent Loops](software-factory-model.md) — The factory-level frame above this operational shift, and where to keep human judgment as it scales
