---
title: "Subagent vs In-Context Skill Execution"
term: "Skill Execution Mode"
description: "Invoke a skill package as a subagent when it declares an input-output contract, and load it in-context when it does not. On contract-less packages the measured result reverses."
tags:
  - agent-design
  - context-engineering
  - skills
  - tool-agnostic
  - arxiv
aliases:
  - skill execution mode
  - subagent skill invocation
  - agent skill execution
last_reviewed: 2026-09-10
maturity: emerging
---

# Subagent vs In-Context Skill Execution

> Invoke a skill package as a subagent when it declares an input-output contract; load it in-context when it does not.

A skill package can run two ways. The harness pastes its instructions into the main context and the agent follows them, or the harness spawns a subagent with a fresh context window that runs the package and hands back only its result. The strongest predictor of which mode wins is a property of the package rather than of the harness. Subagent execution beats in-context execution "when skill packages expose clear input-output contracts and their instructions encode the procedural knowledge needed to fulfill those contracts" ([Piriyakulkij et al., 2026](https://arxiv.org/abs/2609.09233v1)). On packages that state no contract the ordering flips, so you make this call per package rather than once for the harness. The contract is the first of four conditions below and the one that reverses the result.

## When the conditions hold

All four have to be true before a subagent is the better call. Each comes from the results and the stated limits in [Piriyakulkij et al., 2026](https://arxiv.org/abs/2609.09233v1).

| Condition | Why it decides the mode |
|---|---|
| The package states its inputs and its output | The orchestrator writes the subagent's brief from that contract. With no declared interface the brief is a guess, and the fresh window pays for context it never receives |
| The task is long enough for context to become the constraint | The whole mechanism is peak-context reduction. On a task that never fills the window there is nothing to reduce and the coordination cost still lands |
| The budget is priced on peak context, not total tokens | Subagent execution lowers the first and raises the second |
| One package answers the subtask | A subagent sees one package. Anything needing two at once has to stay in the main context |

Model size changes how much the win is worth rather than whether it applies. The gain is "largest for smaller models that are more bandwidth limited", while the peak-context reduction is clearest on strong models: for GPT-5.3 Codex and Kimi K2.6, subagents cut peak context on over 80% of tasks ([Piriyakulkij et al., 2026](https://arxiv.org/abs/2609.09233v1)).

## Why it works

Reasoning quality falls as a context grows, and running a subtask in its own window caps how large any single context gets. The paper states the chain: "LLM reasoning capability declines with context length; this decline has been linked to bandwidth-limited attention: LLMs can only communicate a bounded amount of information across long inputs." Splitting follows from that: "If we can decompose a task into smaller, self-contained subtasks and execute each subtask within a separate context window, we expect the peak context length across all these windows to be shorter than that of a single, monolithic context window" ([Piriyakulkij et al., 2026](https://arxiv.org/abs/2609.09233v1)).

The second half is what the main agent stops seeing. "Only the final output of the subagent is visible to the main agent. The main agent then has less information to reason over, and so it can reason better." The results carry a second signature of that: subagent execution "degrades more gracefully as the number of distracting tools increases" ([Piriyakulkij et al., 2026](https://arxiv.org/abs/2609.09233v1)).

## When this backfires

- The package has no contract. The reversal here is measured rather than cautionary: on the original curated SkillsBench packages, "agent skills match or outperform subagents across all models" ([Piriyakulkij et al., 2026](https://arxiv.org/abs/2609.09233v1)).
- Total tokens are what you pay for. Subagent execution "consumes substantially more tokens overall", because each subagent must be handed context the main agent already holds ([Piriyakulkij et al., 2026](https://arxiv.org/abs/2609.09233v1)).
- The subtask needs two skills at once. The authors list it among the downsides of subagent execution, which loses "the ability to combine knowledge from multiple skills to solve a subtask" ([Piriyakulkij et al., 2026](https://arxiv.org/abs/2609.09233v1)).
- The model is weak. The peak-context reduction "is smaller and sometimes reverses", which the authors read as early termination under agent-skill execution: the run ends before it spends the reasoning the task needed, so its context stays short ([Piriyakulkij et al., 2026](https://arxiv.org/abs/2609.09233v1)).
- Every skill call becomes an agent boundary. Multi-agent gains on popular benchmarks are "often minimal", and inter-agent misalignment is one of the three failure categories in the MAST taxonomy, applied to a dataset of more than 1600 annotated traces ([Cemri et al., 2025](https://arxiv.org/abs/2503.13657v3)). Routing every skill through a subagent multiplies exactly those boundaries.

## Example

The paper's own two skill sets are the cleanest illustration, because the tasks are held constant and only the packaging changes. SkillsBench ships 87 long-horizon agentic tasks with human-curated skill packages that "lack input-output contracts", and on inspection "very few satisfy the criteria for effective subagent execution". On those packages, "agent skills match or outperform subagents across all models". The authors then rebuilt the packages: they ran GPT-5.3 Codex over the benchmark three times, collected the successful trajectories, and used Copilot CLI to synthesize procedural packages carrying explicit input-output contracts, succeeding for 64 of the 87 tasks. On the rebuilt packages, subagent execution wins ([Piriyakulkij et al., 2026](https://arxiv.org/abs/2609.09233v1)).

If you want your skills to run well as subagents, the work sits in the package rather than in the dispatch code.

## Key Takeaways

- Read the package before choosing the mode. A declared input-output contract is the signal; narrative prose without one is a reason to keep the skill in the main context.
- You are trading total tokens for peak context. Check which of the two your budget and your failures are actually priced on.
- Rewriting a skill to declare its interface changes which mode wins, so authoring and execution are one decision rather than two.
- A subtask spanning two packages has no subagent option, so the mode is decided when you carve up the skill library rather than at dispatch time.

## Related

- [Delegation Threshold Calibration for Orchestrator Agents](delegation-threshold-calibration.md) — prices any delegation against handoff cost and the token multiplier, one level above the per-package choice here
- [Forked vs Fresh Subagents: When to Inherit the Parent Conversation](../multi-agent/forked-vs-fresh-subagents.md) — what a spawned subagent inherits, once you have decided to spawn one
- [Compositional Skill Routing for Large Skill Libraries](../../context-engineering/compositional-skill-routing.md) — which skill to retrieve, the question that precedes how to run it
- [Sub-Agents for Fan-Out Research and Context Isolation](../multi-agent/sub-agents-fan-out.md) — the isolation mechanism this pattern applies to skill packages
- [Separation of Knowledge and Execution](separation-of-knowledge-and-execution.md) — the three-layer split that makes a skill package a separable unit in the first place
