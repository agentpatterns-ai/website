---
title: "Delegation Threshold Calibration for Orchestrator Agents"
term: "Delegation Threshold Calibration"
description: "Calibrate the orchestrator's delegate-or-handle-inline threshold by weighing parallelism gain against handoff cost, review tax, and the multi-agent token multiplier."
tags:
  - agent-design
  - tool-agnostic
  - multi-agent
aliases:
  - orchestrator delegation threshold
  - sub-agent delegation calibration
  - delegate-or-inline threshold
last_reviewed: 2026-06-28
maturity: adopted
---

# Delegation Threshold Calibration for Orchestrator Agents

> Calibrate when an orchestrator hands work to a sub-agent versus finishes it inline — handoff cost and review tax can swamp the parallelism gain.

The delegation threshold is the orchestrator's standing rule for when a sub-task is worth handing off. Raise it and the orchestrator finishes more work directly; lower it and it fans out earlier. The lever is not a free knob — every handoff carries fixed coordination cost, an [Anthropic-measured 15× token multiplier on true multi-agent topologies](https://www.anthropic.com/engineering/multi-agent-research-system), and a review tax on whatever the sub-agent returns. Delegation pays back only when the parallelism or context-isolation gain exceeds those costs. Calibrating the threshold is a separate concern from dispatch mechanics (see [async non-blocking sub-agent dispatch](../multi-agent/async-non-blocking-subagent-dispatch.md)) and from the prior human-to-agent decision (see [the delegation decision](delegation-decision.md)).

## The cost side of delegation

Every sub-agent invocation adds three costs the orchestrator does not pay if it handles the work inline:

- Coordination overhead — context packing, output unpacking, and the wait between dispatch and return. GitHub's Copilot CLI team puts it directly: ["every handoff adds coordination overhead, tool calls, and wait time"](https://github.blog/ai-and-ml/how-we-made-github-copilot-cli-more-selective-about-delegation/).
- Token cost — Anthropic reports that ["multi-agent systems use about 15× more tokens than chats"](https://www.anthropic.com/engineering/multi-agent-research-system) on their research workload. That multiplier is the cost of duplicating context across sub-agents and producing summaries the orchestrator can re-ingest.
- Review tax — every sub-agent output needs review, the same fixed cost [the delegation decision](delegation-decision.md) names. Lowering the threshold multiplies the review tax; raising it spreads it across fewer, larger units.

Tran and Kiela's [equal-budget study](https://arxiv.org/abs/2604.02460) attributes the cost to the Data Processing Inequality: under fixed reasoning-token budgets, splitting a task across context-isolated sub-agents partitions the available information, and the partition is strictly lossy. Apparent multi-agent wins, they argue, often come from uncontrolled compute and context inflation rather than architectural superiority.

## Signals that should move the threshold

GitHub's framing after their tuning project is operational: ["keep simple discovery-and-edit tasks in the main agent, and reserve subagents for work that is broader, cross-cutting, or naturally parallelizable"](https://github.blog/ai-and-ml/how-we-made-github-copilot-cli-more-selective-about-delegation/). That collapses to four signals you can read off a candidate sub-task.

| Signal | Lower the threshold (delegate more) | Raise the threshold (handle inline) |
|--------|------------------------------------|------------------------------------|
| Parallelisability | Independent sub-tasks run concurrently | Sequential — sub-task B needs A's output |
| Isolatability | Context fits in one handoff, returns one self-contained answer | Hidden state shared with siblings or the orchestrator |
| Context already present | Orchestrator lacks the relevant files or facts | Orchestrator's context already holds the answer |
| Review cost vs execution cost | Verifying the sub-agent's output is cheaper than redoing it | Quicker to read the file and act than to write a handoff and verify a reply |

The "context already present" row matters because GitHub's tuning project found ["overuse of exploration subagents when the handoff already contains enough context"](https://github.blog/ai-and-ml/how-we-made-github-copilot-cli-more-selective-about-delegation/) as a top symptom of over-delegation. The same source flags ["sequential delegation, where the main agent waits for a subagent instead of treating delegation as an opportunity for parallel work"](https://github.blog/ai-and-ml/how-we-made-github-copilot-cli-more-selective-about-delegation/) — sub-agents should be ["a parallelism tool, not a pause button"](https://github.blog/ai-and-ml/how-we-made-github-copilot-cli-more-selective-about-delegation/).

Anthropic's coarse scaling rule sets a useful zero point: ["Simple fact-finding requires just 1 agent with 3-10 tool calls, direct comparisons might need 2-4 subagents with 10-15 calls each, and complex research might use more than 10 subagents"](https://www.anthropic.com/engineering/multi-agent-research-system). Fact-finding sits below the threshold; complex research sits above it.

## Structural preconditions

The threshold is the wrong primitive until two structural conditions hold, both drawn from Cognition's [follow-up on what actually works in multi-agent systems](https://cognition.com/blog/multi-agents-working):

- Writes stay single-threaded. Cognition found multi-agent systems work in practice only when ["writes stay single-threaded"](https://cognition.com/blog/multi-agents-working) and additional agents contribute intelligence rather than actions. If sibling sub-agents can both write, threshold calibration will not save you.
- Context is shared, not split. Cognition's original critique still applies: ["every time you split a task across multiple agents, you introduce a communication boundary and context gets lost between handoffs"](https://cognition.com/blog/dont-build-multi-agents). Share the full agent trace, not a summary; if you cannot, raise the threshold sharply.

Without these, lowering the threshold amplifies error rather than throughput. DeepMind's 180-configuration sweep across five architectures and three model families found ["unstructured multi-agent networks amplify errors up to 17.2×"](https://towardsdatascience.com/why-your-multi-agent-system-is-failing-escaping-the-17x-error-trap-of-the-bag-of-agents/) compared with a single-agent baseline. Threshold tuning operates above this floor; it does not substitute for it.

## Why It Works

The mechanism behind the cost is information-theoretic. Tran and Kiela attribute it to the Data Processing Inequality: under fixed reasoning-token budgets, partitioning a task across context-isolated sub-agents is ["strictly lossy"](https://arxiv.org/abs/2604.02460), so single-agent systems are more information-efficient when budgets are normalised. Calibrating the threshold is how the orchestrator stays on the right side of that trade — delegate only when parallelism gain or context-isolation gain visibly exceeds the lossy partition.

The production evidence is GitHub's A/B test on Copilot CLI after raising the delegation threshold and tightening handoff criteria: ["a 23% reduction in tool failures per session, a 27% reduction in search tool failures, an 18% reduction in edit tool failures, a 5% improvement in P95 wait time", with "no quality regression"](https://github.blog/ai-and-ml/how-we-made-github-copilot-cli-more-selective-about-delegation/). The trajectory analysis adds ["15% reduction in failed subagent search calls" and "12% lower average subagent LLM duration per user"](https://github.blog/ai-and-ml/how-we-made-github-copilot-cli-more-selective-about-delegation/). The win came from removing low-benefit handoffs, not from removing delegation.

## When This Backfires

- Stateful coupling between sibling sub-tasks. If delegated work shares hidden state — open files, environment, intermediate decisions — the orchestrator pays handoff cost twice and still produces conflicting intermediate decisions. Cognition's ["context gets lost between handoffs"](https://cognition.com/blog/dont-build-multi-agents) critique applies in full.
- Small total task budget. When total work is sub-minute, the fixed handoff overhead per [GitHub's tuning post](https://github.blog/ai-and-ml/how-we-made-github-copilot-cli-more-selective-about-delegation/) dominates the parallel-speedup. The orchestrator is faster doing the work inline.
- Context already loaded in the orchestrator. ["Overuse of exploration subagents when the handoff already contains enough context"](https://github.blog/ai-and-ml/how-we-made-github-copilot-cli-more-selective-about-delegation/) was a top symptom in GitHub's tuning post — re-delegating a question whose answer is already in the orchestrator's context is pure overhead.
- Equal-budget regime where the orchestrator is competent. [Tran and Kiela](https://arxiv.org/abs/2604.02460) show that under matched token budgets, single-agent systems match or beat multi-agent on multi-hop reasoning across Qwen3, DeepSeek-R1-Distill-Llama, and Gemini 2.5. Lowering the threshold here gives away the equal-budget single-agent advantage.
- Unstructured fan-out without a centralised synthesis plane. DeepMind's [17.2× error amplification finding](https://towardsdatascience.com/why-your-multi-agent-system-is-failing-escaping-the-17x-error-trap-of-the-bag-of-agents/) holds for flat-topology delegation. Lowering the threshold without a verifying orchestrator amplifies error, not throughput.

## Example

GitHub described their Copilot CLI tuning in operational terms — symptoms first, then the threshold change, then the measured outcome. The symptoms were five: ["unnecessary handoffs for simple tasks that the main agent could complete faster on its own"; "overuse of exploration subagents when the handoff already contains enough context"; "repeated or overlapping searches across the main agent and subagents"; "sequential delegation, where the main agent waits for a subagent instead of treating delegation as an opportunity for parallel work"; "failure-prone subagent paths, including stale file paths, moved files, incorrect relative paths, and workspace mismatches"](https://github.blog/ai-and-ml/how-we-made-github-copilot-cli-more-selective-about-delegation/).

The threshold change was a single rule, restated for the orchestrator's planner: keep simple discovery-and-edit tasks in the main agent; reserve sub-agents for work that is broader, cross-cutting, or naturally parallelisable; treat handoffs as opportunities for parallelism, not as pauses. Every handoff carries a specification: ["what the user asked, what is already known, what the subagent owns"](https://github.blog/ai-and-ml/how-we-made-github-copilot-cli-more-selective-about-delegation/).

The measured outcome on the A/B was ["a 23% reduction in tool failures per session, a 27% reduction in search tool failures, an 18% reduction in edit tool failures, a 5% improvement in P95 wait time"](https://github.blog/ai-and-ml/how-we-made-github-copilot-cli-more-selective-about-delegation/) with no quality regression — a production result for raising the threshold once the symptom set was diagnosed.

## Key Takeaways

- The delegation threshold is the orchestrator's calibration of when fan-out pays back — raise it when the orchestrator already holds context or the work is sequential, lower it when the work is broader, cross-cutting, or naturally parallelisable ([GitHub Blog, 2026](https://github.blog/ai-and-ml/how-we-made-github-copilot-cli-more-selective-about-delegation/)).
- Handoff cost is real and measurable — coordination overhead plus an Anthropic-reported [15× token multiplier on true multi-agent](https://www.anthropic.com/engineering/multi-agent-research-system) plus a review tax — so the threshold lives above a fixed cost floor.
- Calibration only matters above structural preconditions: single-threaded writes and shared context. Without them, lowering the threshold can amplify error up to [17.2×](https://towardsdatascience.com/why-your-multi-agent-system-is-failing-escaping-the-17x-error-trap-of-the-bag-of-agents/).
- This page sits above [async non-blocking sub-agent dispatch](../multi-agent/async-non-blocking-subagent-dispatch.md) (mechanics) and beside [the delegation decision](delegation-decision.md) (human-to-agent) — orchestrator-to-sub-agent threshold tuning is the missing layer.

## Related

- [The Delegation Decision: When to Use an Agent vs Do It Yourself](delegation-decision.md)
- [Async Non-Blocking Sub-Agent Dispatch](../multi-agent/async-non-blocking-subagent-dispatch.md)
- [Orchestrator-Worker Pattern](../multi-agent/orchestrator-worker.md)
- [Agent Composition Patterns: Chains, Fan-Out, Pipelines, Supervisors](agent-composition-patterns.md)
- [Recursive Sub-Agent Delegation Depth](../multi-agent/recursive-sub-agent-delegation-depth.md)
