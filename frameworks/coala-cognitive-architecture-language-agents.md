---
title: "Cognitive Architectures for Language Agents (CoALA): A Classifier for Agent Harnesses"
term: "Cognitive Architectures for Language Agents (CoALA)"
description: "CoALA names language agents along three axes — memory, action space, decision loop — as a classifier for harness artifacts coding-agent teams already maintain."
tags:
  - frameworks
  - agent-design
  - tool-agnostic
aliases:
  - cognitive architectures for language agents
  - CoALA framework
last_reviewed: 2026-06-13
maturity: established
---

# Cognitive Architectures for Language Agents (CoALA): A Classifier for Agent Harnesses

> A descriptive framework that names harness artifacts along three axes — memory, action space, decision loop — so structural gaps in an agent become visible.

CoALA (Cognitive Architectures for Language Agents) is a peer-reviewed conceptual framework published by Sumers, Yao, Narasimhan, and Griffiths in *Transactions on Machine Learning Research* ([arXiv:2309.02427](https://arxiv.org/abs/2309.02427)). It organises every language agent — from a one-shot Copilot edit to a long-running Claude Code session — along three axes borrowed from cognitive science and symbolic AI: a modular **memory** system, a structured **action space**, and a generalised **decision-making loop**. The contribution is taxonomy, not implementation: the paper itself describes its use as "retrospectively" surveying existing agents and "prospectively" identifying gaps, never as a build recipe ([arXiv:2309.02427](https://arxiv.org/abs/2309.02427)).

The value for a practitioner shipping with Claude Code, Copilot, or Cursor is exactly that scope. Naming each component an agent already uses — context window, transcript, RAG index, instruction file — exposes which CoALA category is missing.

## When the Classifier Helps

CoALA earns its keep under three conditions. Outside them, it adds vocabulary without changing behaviour:

- **The harness has grown beyond a single while-loop.** Multi-session agents with persistent state, memory writes, or scheduled work have enough structural surface that naming axes prevents ad-hoc design drift.
- **A team needs a shared term for a recurring debate.** "Is this an episodic or a procedural memory?" forces a decision the prose alternative ("the transcript file thing") never surfaces.
- **An audit needs to detect *what is missing*, not what is wrong.** A taxonomy makes absence visible. A team with no "episodic memory" artifact only notices the gap once the slot has a name.

For single-turn agents — a one-shot code completion, a one-call shell command — CoALA's loop and four memory types describe phases that do not exist. Anthropic's [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) names this directly: "find the simplest solution possible, and only increase complexity when needed." Apply CoALA only after the agent is already complex enough to confuse you.

## The Three Axes

### Memory

CoALA inherits four memory types from cognitive psychology, each defined by what it stores and when it is written ([arXiv:2309.02427 v3](https://arxiv.org/html/2309.02427v3)):

| CoALA type | Paper definition | Harness artifact |
|---|---|---|
| **Working** | Symbolic state held for the current decision cycle — perceptual inputs, active goals | The live context window |
| **Episodic** | Experience from earlier decision cycles — trajectories, history flows | Session transcripts, run logs |
| **Semantic** | World and self knowledge — facts about the environment | RAG corpus, vector index |
| **Procedural** | Implicit LLM weights plus explicit agent code | `CLAUDE.md`, skills, hooks, scaffolding |

The mapping is the practitioner-facing contribution. LangChain's [Memory for Agents](https://blog.langchain.com/memory-for-agents/) cites CoALA's memory taxonomy as the substrate for the LangGraph Memory Store, confirming the categories carry weight in production code, not only in the paper.

The classifier's diagnostic use is the **missing-slot question**: which of the four does your harness lack? An agent with no episodic memory cannot reflect on prior sessions; an agent with no semantic memory has no place to put facts that outlive its training cutoff.

### Action Space

CoALA splits actions into **internal** (operating on memory) and **external** (operating on the environment, called *grounding*) ([arXiv:2309.02427 v3](https://arxiv.org/html/2309.02427v3)):

- **Internal actions** — three sub-types: *retrieval* (read from long-term memory), *reasoning* (update working memory via the LLM), *learning* (write to long-term memory).
- **External actions** — every tool call, shell command, code edit, or HTTP request that affects something outside the agent.

The split matters because the external leg is where permission gating, reversibility, cost, and the [lethal trifecta](../security/lethal-trifecta-threat-model.md) live. Treating retrieval and a `rm -rf` as "the same kind of step" hides the trust boundary.

### Decision-Making Loop

CoALA frames every agent's control flow as a [four-phase cycle](../agent-design/coala-decision-making-loop.md) that repeats until termination ([arXiv:2309.02427 v3](https://arxiv.org/html/2309.02427v3)):

1. **Propose** — generate candidate actions through reasoning or retrieval.
2. **Evaluate** — score candidates (heuristic, LLM judge, learned value).
3. **Select** — choose one via argmax, softmax, or voting.
4. **Execute** — apply the action, observe the result, restart.

Used as a lens, the loop locates every orchestration pattern the site already documents. Generate-rank-verify lives in propose-plus-evaluate-plus-select. A [critic-agent gate](../agent-design/critic-agent-plan-review.md) guards execute. Plan mode front-loads propose.

## Why It Works

A closed vocabulary surfaces gaps that prose hides. Naming the four memory types forces a yes/no audit for each one — does this harness have an episodic store, or not? The mechanism is the same one any taxonomy uses to organise messy domains: making categories explicit makes absence visible ([arXiv:2309.02427](https://arxiv.org/abs/2309.02427)). The paper itself frames this as the framework's primary contribution — "retrospectively organising" existing work so practitioners can locate their design on a common map.

The mechanism breaks the moment readers mistake the taxonomy for a checklist. The paper supplies *no evidence* that an agent missing a memory type performs worse on any task; it only supplies the language to name the gap. The classifier is necessary infrastructure for the conversation, not the answer the conversation produces.

## When This Backfires

- **Single-session, short-horizon agents.** For one-shot Copilot completion or a single Cursor edit, the loop's four phases collapse to "ask the model and apply the diff." Adding CoALA vocabulary delivers nothing the team did not already know ([Anthropic: Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)).
- **Reading the framework as a build spec.** The paper is explicitly descriptive. A team that infers "an agent needs all four memory types" from the taxonomy builds infrastructure nothing reads back — the exact failure mode Anthropic warns about: complexity added without a triggering need.
- **Knowledge versus experience persistence conflation.** CoALA groups facts (semantic) and trajectories (episodic) under the same "long-term memory" umbrella. Applying experience-style decay or forgetting to a semantic fact store produces correctness regressions; [The Missing Knowledge Layer](https://arxiv.org/abs/2604.11364) (arXiv:2604.11364) names this category error explicitly.
- **Vocabulary churn with no behavioural change.** If the team already uses "context window," "transcript," "RAG index," and "skills file" consistently, renaming them as "working," "episodic," "semantic," and "procedural memory" delivers zero new affordance and breaks search across existing docs.
- **Borrowed biological framing held too literally.** The CoALA authors themselves note LLMs "are not subject to biological limitations" ([arXiv:2309.02427 v3](https://arxiv.org/html/2309.02427v3)). Pushing the cognitive-science analogy past its taxonomic use — for example, designing memory consolidation to mimic human sleep cycles without evidence — invents constraints the medium does not have.

## Example

A team operating a Claude Code harness for a regulated codebase audits its memory surface using CoALA's four-slot classifier:

| Slot | Artifact in this harness | Coverage |
|---|---|---|
| Working | Active context window per session | Present |
| Episodic | None — transcripts are discarded at session end | **Gap** |
| Semantic | None — no project-level RAG | **Gap** |
| Procedural | `CLAUDE.md`, `.claude/skills/`, `.claude/hooks/` | Present |

The audit surfaces two missing slots. Acting on them is a separate decision: episodic memory only earns its cost when the agent re-encounters similar problems across sessions; semantic memory only pays when the project has authoritative reference material the LLM cannot infer. CoALA names the gap; the [delegation decision](../agent-design/delegation-decision.md) and [tiered memory architecture](../agent-design/tiered-memory-architecture.md) pages cover whether to fill it.

## Key Takeaways

- CoALA is a descriptive taxonomy along three axes — memory, action space, decision loop — not a build spec, by the authors' own framing ([arXiv:2309.02427](https://arxiv.org/abs/2309.02427)).
- Its practitioner value is exposing missing categories. A team with no episodic-memory artifact only notices the gap once the slot has a name.
- The four memory types map cleanly onto artifacts coding-agent teams already maintain — context window, transcript, RAG index, instruction file.
- The internal/external action split locates permission boundaries, cost, and the lethal-trifecta egress leg on the external side.
- Apply CoALA only when the harness is complex enough that vocabulary helps; for single-session agents, [Anthropic's "start with workflows, not frameworks"](https://www.anthropic.com/research/building-effective-agents) advice dominates.

## Related

- [Anthropic's Effective Agents Framework: A Pattern Map](../agent-design/anthropic-effective-agents-framework.md) — the workflow-first counterpoint to CoALA's taxonomic depth
- [Agent Memory Patterns: Learning Across Conversations](../agent-design/agent-memory-patterns.md) — atomic memory patterns CoALA's taxonomy organises
- [Tiered Memory Architecture: Episodic-to-Semantic Consolidation](../agent-design/tiered-memory-architecture.md) — the consolidation pattern between two CoALA memory types
- [Agent Harness](../agent-design/agent-harness.md) — the scaffolding layer that hosts the CoALA decision loop
- [Cognitive Reasoning vs Execution: A Two-Layer Agent Architecture](../agent-design/cognitive-reasoning-execution-separation.md) — a related boundary cut: reasoning versus action, parallel to CoALA's internal/external split
