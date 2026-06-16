---
title: "Earned-Complexity Agent Maturity Ladder"
description: "Nine diagnostic layers from single-shot tool calling to multi-agent delegation — each rung exposes the failure modes the next pretends to solve."
tags:
  - training
  - workflows
  - human-factors
  - tool-agnostic
last_reviewed: 2026-05-27
---

# Earned-Complexity Agent Maturity Ladder

> Build agents in this order — single tool call before retries, retries before retrieval, retrieval before planning. Each rung exposes the failure modes the next pretends to solve.

The earned-complexity ladder is a diagnostic map of nine layers from a single LLM tool call to multi-agent delegation. Read the blockquote above as a default heuristic, not a forced sequence: the rungs are prerequisite layers, and the default for greenfield work is to build them in order — the start-simple posture of the [Anthropic effective-agents framework](../../agent-design/anthropic-effective-agents-framework.md). Skip a rung when you can articulate which failure mode at the lower rung you have already solved. Skip without that articulation and you are cargo-culting: copying the architecture of a production system without inheriting the failures that shaped it.

The cargo-cult symptom is consistent. A team reads about Anthropic's multi-agent research system or watches a Devin demo, then builds a planner agent, a critic agent, a memory layer, and a delegation graph — before they have shipped a reliable single-step tool loop. The result is a system that fails in ways the team cannot diagnose, because they never built the layer below the failure. Anthropic's own guidance is to start simple: "we recommend finding the simplest solution possible, and only increasing complexity when needed" and "optimizing single LLM calls with retrieval and in-context examples is usually enough" ([Anthropic Engineering: Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)).

The rungs below are the diagnostic layers. For each: a one-sentence definition, the failure mode the layer exposes (which is the prerequisite logic for the next layer), the cargo-cult symptom, and the canonical anchor on this site.

## Rung 1 — Single-Shot Tool Calling

A single LLM call that invokes one tool and returns. No retries, no validation, no state.

**Exposes**: the model's raw structured-output reliability and the tool's API behaviour under nominal conditions. Without seeing rung 1 fail, you cannot tell the difference between a model that returns malformed arguments and a tool that returns malformed results.

**Cargo-cult symptom**: claiming "the model picks the wrong tool" when the actual failure is that the model's structured output is intermittently malformed and the harness silently retries — invisible at rung 5, visible at rung 1.

**Anchor**: [CLI-First Skill Design](../../tool-engineering/cli-first-skill-design.md).

## Rung 2 — Structured Outputs

Constrained generation — JSON schema, grammar, or function-call format — that the model is required to satisfy.

**Exposes**: the failure modes specific to constraint satisfaction (truncation, schema-conformant-but-semantically-wrong outputs, model refusal under tight constraints). These failures are invisible until you require structure.

**Cargo-cult symptom**: building an evaluator-optimizer loop (rung 3-adjacent) to "fix bad model outputs" when the actual fix is constraining the output shape so the failure is impossible.

**Anchor**: [Controlling Agent Output](../../instructions/controlling-agent-output.md) and [Structured Output Constraints](../../verification/structured-output-constraints.md).

## Rung 3 — Retry and Validation Loops

A bounded retry loop that re-invokes the model when validation fails — schema check, tool error, or semantic guardrail.

**Exposes**: provider flakiness, retry-storm risk, idempotency assumptions in tools, and the cost curve of unbounded retries. Until you build the retry loop, you cannot see which failures are transient and which are systematic.

**Cargo-cult symptom**: assuming retrieval (rung 4) will fix "the model keeps getting it wrong" when the actual issue is that the same prompt is being retried with no validation signal — the model has no new information to use.

**Anchor**: [Deterministic Guardrails](../../verification/deterministic-guardrails.md) and [Agent Self-Review Loop](../../code-review/agent-self-review-loop.md).

## Rung 4 — Retrieval

The model is given context fetched from an external store — RAG, file system, or repository search — based on the input.

**Exposes**: retrieval noise, recency vs relevance trade-offs, chunking-strategy failures, and the dependency of generation quality on retrieval quality. Adding retrieval before rung 3 means you cannot tell whether a wrong answer is a retrieval problem or a generation problem.

**Cargo-cult symptom**: adding agentic memory (a rung 5-adjacent pattern) to "remember context" when the actual fix is making retrieval deterministic and citation-anchored.

**Anchor**: [Structured Domain Retrieval](../../context-engineering/structured-domain-retrieval.md) and [Retrieval-Augmented Agent Workflows](../../context-engineering/retrieval-augmented-agent-workflows.md).

## Rung 5 — Stateful Workflows

A multi-step process where state persists across steps — task queues, intermediate artifacts, run state machines.

**Exposes**: state-drift bugs, schema-evolution problems, recovery-from-partial-failure design, and the cost of running long-lived processes. Once you build stateful workflows, you can see exactly which step in a pipeline degrades and how state corruption propagates.

**Cargo-cult symptom**: spawning a multi-agent topology (rung 9) to "split the work" when the real problem is that a single-agent stateful workflow has no checkpoint and can't resume after a failure.

**Anchor**: [Agent Development Lifecycle](../../agent-design/agent-development-lifecycle.md) and the [Workflows section](../../workflows/index.md).

## Rung 6 — Human Approval Checkpoints

The workflow pauses for human confirmation before consequential actions — writes, sends, payments, deletes.

**Exposes**: the alert-fatigue curve (humans rubber-stamp identical-looking prompts), confirmation-gate log quality, and the gap between what you logged and what would let you reconstruct the action. Adding approval gates surfaces which actions are actually consequential and which are reversible enough to not need a gate.

**Cargo-cult symptom**: building full autonomy (rung 7+) for tasks whose downstream effects are irreversible — sending email, running migrations, posting to public channels — because "the agent handles it" feels like progress.

**Anchor**: [Human-in-the-Loop](../../workflows/human-in-the-loop.md).

## Rung 7 — Async Task Orchestration

Long-running work runs asynchronously — background jobs, foreground/background handoffs, async sub-agent dispatch, event-driven triggers.

**Exposes**: race conditions across tool calls, deadlock and starvation patterns, observability gaps when work is no longer synchronous, and the cost of polling versus event-driven coordination.

**Cargo-cult symptom**: defaulting to async sub-agents to "speed things up" when the work is short-lived enough that synchronous tool calls would finish before the async setup overhead amortizes.

**Anchor**: [Async Non-Blocking Subagent Dispatch](../../multi-agent/async-non-blocking-subagent-dispatch.md) and [Background/Foreground Handoff](../../workflows/background-foreground-handoff.md).

## Rung 8 — Multi-Step Planning

The agent generates a plan before executing — explicit plan-then-execute separation, decomposed sub-goals, plan revision on failure.

**Exposes**: plan-quality versus execution-quality trade-offs, plan-compliance enforcement, and the failure mode where a model executes a flawed plan to completion rather than re-planning mid-task. Planning is only useful once execution (rungs 1-3) is reliable — a plan over flaky primitives compounds the flakiness.

**Cargo-cult symptom**: jumping to multi-agent delegation (rung 9) "because each agent specializes in a step" before testing whether a single agent with a written plan and a critic loop already handles the task.

**Anchor**: [Cognitive Reasoning vs Execution Separation](../../agent-design/cognitive-reasoning-execution-separation.md) and [Plan Compliance in Agents](../../agent-design/plan-compliance-in-agents.md).

## Rung 9 — Multi-Agent Delegation

Multiple agents coordinate — orchestrator/worker, peer-to-peer, role-based topologies, handoff protocols.

**Exposes**: the failure modes Walden Yan (Cognition) catalogued — "fragile systems due to poor context sharing and conflicting decisions" — and the 15× token cost amplification Anthropic measured on its research system ([Anthropic Engineering: Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system); [Cognition: Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents)). These costs are invisible at rung 8 because the token bill scales linearly with planning, not exponentially with agent count.

**Cargo-cult symptom**: building a multi-agent system for a task Anthropic explicitly flags as unsuitable: "domains that require all agents to share the same context or involve many dependencies between agents" and "most coding tasks [which] involve fewer truly parallelizable tasks than research" ([Anthropic multi-agent](https://www.anthropic.com/engineering/multi-agent-research-system)).

**Anchor**: [Multi-Agent section](../../multi-agent/index.md), [Anthropic Effective Agents Framework](../../agent-design/anthropic-effective-agents-framework.md), [Agent Handoff Protocols](../../multi-agent/agent-handoff-protocols.md).

## Why It Works

Each rung exposes a class of failure that the next rung's pattern is designed to absorb. The diagnostic principle is additive complexity: if layer N is unreliable, no signal at layer N+1 is interpretable. A retry loop over malformed structured output cannot tell you whether retries should be unbounded — because the underlying schema failure is the bug, not the transient one the retry pattern was designed for. A retrieval system over a flaky tool call cannot tell you whether your chunking strategy is wrong — because the retrieval noise compounds on top of generation noise and you cannot attribute the failure. This is the mechanism behind Anthropic's "simplest solution first" recommendation ([Anthropic Engineering: Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)) and Cognition's parallel "context engineering primacy" position ([Cognition: Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents)). The two camps disagree about whether multi-agent is ever worth the climb; they agree that climbing without the lower rungs produces fragile systems.

## When This Backfires

The strict-sequence reading of the ladder is wrong in three specific cases:

- **Framework-supported greenfield projects**: when a team adopts a modern agent framework (LangGraph, CrewAI, Pydantic AI), rungs 1-7 ship as defaults. Forcing the team to "earn" each rung by hand-rolling primitives adds weeks of work for negligible diagnostic benefit. The rungs are still conceptual prerequisites — the team must understand each layer's failure mode — but they do not need to build each one from scratch.
- **Research and synthesis workloads**: Anthropic's multi-agent research system targets a task class — parallel document scanning and synthesis — where rung 9 is the correct destination ([Anthropic multi-agent](https://www.anthropic.com/engineering/multi-agent-research-system)). A team building a research assistant from day one should not pretend rung 1 is sufficient; they should still build evals at rung 1 before scaling.
- **Teams already shipping**: a team that has run a tool-calling chatbot in production for two years has earned rungs 1-3. They do not need to re-earn them on a new project. The ladder addresses cargo-culting at greenfield, not all complexity decisions.

The ladder also does not address the dominant failure mode in agent-building, which is operating without evals. A team with evals fails diagnostically at any rung; a team without evals fails the same way at rung 1 and rung 9. Evals are orthogonal — see [Eval Engineering](eval-engineering.md).

## Key Takeaways

- The nine rungs are diagnostic layers, not a forced sequence. Skip a rung when you can articulate which failure mode at the lower rung you have already solved.
- The cargo-cult symptom is consistent: adopting an upper-rung pattern to "fix" a problem that the rung below would have exposed clearly.
- Anthropic and Cognition disagree about the value of rung 9 for any given task; they agree that climbing without the lower rungs produces fragile systems.
- Framework adoption can ship rungs 1-7 as defaults — the team still owes the diagnostic understanding, not necessarily the hand-rolled implementation.
- Evals are not on the ladder. A team without evals fails the same way at every rung.

## Related

- [How the Four Disciplines Compound](prompt-context-harness-capstone.md) — the capstone module on prompt/context/harness/tool engineering as multiplicative factors.
- [Agentless vs Autonomous: When Simple Beats Complex](../../agent-design/agentless-vs-autonomous.md) — empirical case for starting at a lower rung than the trend suggests.
- [Anthropic Effective Agents Framework](../../agent-design/anthropic-effective-agents-framework.md) — the canonical seven-level progression this ladder elaborates.
- [Delegation Decision](../../agent-design/delegation-decision.md) — when delegating to an agent (rung 8-9 territory) pays off.
- [Agentic AI Architecture Evolution](../../agent-design/agentic-ai-architecture-evolution.md) — reference architecture spanning the upper rungs.
