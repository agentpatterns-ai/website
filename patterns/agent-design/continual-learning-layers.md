---
title: "Continual Learning for AI Agents: Three Layers of Knowledge Accumulation"
term: "Continual Learning for AI Agents"
description: "AI agents accumulate knowledge at three layers — model, harness, and context — each with different update costs, speeds, and scopes."
tags:
  - agent-design
  - tool-agnostic
  - memory
  - workflows
last_reviewed: 2026-11-18
maturity: adopted
---

# Continual Learning for AI Agents: Three Layers of Knowledge Accumulation

> Continual learning for AI agents updates model weights, shared harness behavior, or external context; the layer identifies where accumulated knowledge persists.

## The three layers

[LangChain's analysis](https://blog.langchain.com/continual-learning-for-ai-agents/) defines three update targets in any agentic system:

| Layer | What it covers | Update mechanism |
|-------|---------------|-----------------|
| Model | Neural network weights | Fine-tuning (SFT, RL) |
| Harness | Scaffold code plus instructions and tools that are always present | Code changes, prompt rewrites |
| Context | Instructions, skills, and memory that live outside the harness and configure it per agent/user/org | File edits, memory writes |

The distinction identifies what an update changes. Instructions always present belong to the harness; instructions supplied as external configuration belong to context ([LangChain](https://www.langchain.com/blog/continual-learning-for-ai-agents)).

## Model layer

Model-layer learning updates the weights themselves — supervised fine-tuning (SFT) or reinforcement learning methods like GRPO.

LangChain identifies catastrophic forgetting as a central challenge: training on new data can degrade earlier capabilities ([model-layer discussion](https://www.langchain.com/blog/continual-learning-for-ai-agents)).

LangChain describes model updates as mostly agent-level and names per-user LoRA as a finer-grained possibility ([model-layer discussion](https://www.langchain.com/blog/continual-learning-for-ai-agents)). This scope is one dimension of [layered mutability](layered-mutability.md).

The source ranks model updates as high-cost and slow relative to the other layers. It does not compare rollback procedures ([LangChain comparison](https://www.langchain.com/blog/continual-learning-for-ai-agents)).

## Harness layer

The harness is the scaffold code that runs the agent, plus instructions and tools always present for every instance. Harness-layer learning rewrites the scaffold.

LangChain describes Meta-Harness as a loop that evaluates tasks, stores traces, and asks a coding agent to propose harness changes ([layer discussion](https://www.langchain.com/blog/continual-learning-for-ai-agents)). [LangChain separately reports improving Deep Agents](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/), improving Terminal Bench 2.0 from 52.8% to 66.5% through harness changes alone.

The harness powers all instances of the agent. That shared scope does not establish that every proposed change improves every task; LangChain warns that harness changes can overfit and regress other tasks ([harness engineering](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering)).

## Context layer

Context sits outside the harness and configures it: skills, instructions, and memory specific to an agent instance, user, or organization. Also called agent memory.

Context updates can be scoped at multiple levels:

- Agent level — a persistent configuration the agent updates across sessions (for example, OpenClaw's [SOUL.md](https://docs.openclaw.ai/concepts/soul), which the agent updates over time)
- User or tenant level — per-user context that accumulates preferences and conventions (for example, [Hex Context Studio](https://hex.tech/product/context-studio/), [Decagon Duet](https://decagon.ai/blog/introducing-duet))
- Org level — shared context across a team or organization

These scopes coexist: an agent can update its own SOUL.md, accept user-level corrections, and pull from org-level rules.

Updates happen in two modes:

- Offline (batch) — after execution, a background job analyzes traces and updates context. OpenClaw calls this ["dreaming"](https://docs.openclaw.ai/concepts/dreaming). Anthropic also describes "dreaming" for Claude's memory ([Anthropic on agent memory](https://www.anthropic.com/research/components-of-agent-memory)).
- Hot path (inline) — the agent updates memory mid-task, either on user instruction or harness direction.

LangChain ranks context updates as lower-cost and faster than model or harness updates. Their target is external configuration, which the article also calls [agent memory](agent-memory-patterns.md); they do not update model weights ([context-layer discussion](https://www.langchain.com/blog/continual-learning-for-ai-agents)).

Memory updates still need evaluation. Vivioo reports [repeated corrections that were stored but did not reliably surface among competing search results](https://medium.com/@vivioo.io/your-ai-agent-keeps-forgetting-76d7bcefacf0). Use that failure case to test whether a stored correction is retrieved and applied on a later task.

## Choosing the right layer

Use the update target to classify a proposed change: weights, shared harness code or instructions, or external configuration. The source permits learning at all three layers and does not measure which layer contains most improvement opportunities ([LangChain](https://www.langchain.com/blog/continual-learning-for-ai-agents)).

### Trade-offs at a glance

LangChain's comparison gives relative cost and update speed, with no deployment-time estimates or rollback guarantees ([comparison table](https://www.langchain.com/blog/continual-learning-for-ai-agents)).

| Dimension | Model | Harness | Context |
|-----------|-------|---------|---------|
| Cost of updating | High | Medium | Low |
| Speed of updating | Slow | Medium | Fast |
| Update pattern | Offline batch | Offline batch | Offline batch or during execution |

## Traces as input to updates

LangChain describes execution traces as input to updates at all three layers ([traces discussion](https://www.langchain.com/blog/continual-learning-for-ai-agents)):

- Model: collect traces, label outcomes, fine-tune
- Harness: feed traces to a coding agent that proposes scaffold changes
- Context: extract conventions and preferences from traces, write to memory files

Evaluate proposed changes against task outcomes. In LangChain's harness experiment, traces exposed failures that guided changes while the model stayed fixed ([harness engineering](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering)).

## Example

LangChain illustrates its taxonomy with Claude Code ([layer mapping](https://www.langchain.com/blog/continual-learning-for-ai-agents)):

- Model: `claude-sonnet` or similar — updated by Anthropic
- Harness: the Claude Code application itself — updated when you upgrade the CLI
- Context: `CLAUDE.md`, `/skills`, `mcp.json` — updated by you or the agent per project and session

## Key Takeaways

- Classify an instruction by where it lives: always-present harness instructions and external configuration belong to different layers.
- The cost and speed rankings are relative. They do not supply deployment deadlines or rollback guarantees.
- A shared harness change needs evaluation for regressions; shared scope alone does not establish improvement across tasks.
- Use traces to identify candidate changes, then evaluate their effects before retaining them.

## Related

- [Agentic Flywheel: Self-Improving Agent Systems](agentic-flywheel.md)
- [Harness Engineering](harness-engineering.md)
- [CoALA Memory Taxonomy Classifier](coala-memory-taxonomy-classifier.md) — companion taxonomy organized by classify-what, distinct from this update-target / persistence-scope axis
- [Memory Retrieval as a Control Decision](memory-retrieval-as-control.md)
- [Scaffold Architecture Taxonomy for Coding Agents](harness-design-dimensions.md)
- [Memory Synthesis: Extracting Lessons from Execution Logs](memory-synthesis-execution-logs.md)
- [Steering Agent Memory: Judge Salience, Then Correct with Dreaming](salience-steered-memory-with-dreaming.md) — measured results for offline dreaming that corrects context-layer notes against transcripts
- [Continuous Agent Improvement](../../workflows/continuous-agent-improvement.md)
- [Weakest Consistent Learning: What Agent Loops Should Persist](weakest-consistent-learning.md) — how to phrase a learning once the layer is chosen
