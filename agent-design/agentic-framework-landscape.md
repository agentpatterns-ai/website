---
title: "Agentic Framework Landscape: When Each Framework Fits"
description: "Six open-source agentic frameworks (ADK, Agno, Browser Use, Eigent, Letta, mem0) sit at different layers of the agent stack; selection turns on task horizon, action space, memory model, and deployment shape rather than feature counts."
aliases:
  - agentic framework comparison
  - agent framework selection
tags:
  - agent-design
  - memory
  - multi-agent
  - tool-agnostic
last_reviewed: 2026-05-27
---

# Agentic Framework Landscape: When Each Framework Fits

> ADK, Agno, Browser Use, Eigent, Letta, and mem0 occupy different layers of the agent stack — runtime, action space, memory, desktop product — so framework selection is a task-shape match, not a feature-count comparison.

## The Selection Axes

A framework compresses your work when its primitives match your task signature and fights you when they do not. Five axes carry most of the decision:

- **Task horizon** — single turn, single session, or workflows that pause for days and resume from checkpoint.
- **Action space** — tools and code only, browser DOM, full desktop, or all of the above.
- **Memory model** — none, ephemeral within session, server-stateful agent identity, or a memory layer composed over any runtime.
- **Deployment shape** — Python/Node library, control-plane runtime with an HTTP surface, or a packaged desktop app.
- **Language and ecosystem fit** — Python-first, polyglot SDKs, or TypeScript/Electron.

A feature-by-feature matrix flatters whichever framework is doing the comparison. The axes above decide whether you spend the next quarter shipping the agent or rewriting around the wrong primitive.

## Per-Framework Fit

### ADK (Google)

Code-first Python framework — Python 3.11+, Apache 2.0 ([ADK README](https://github.com/google/adk-python)). The 2.0 release centres on two primitives: a graph-based **Workflow Runtime** with routing, fan-out/fan-in, loops, retry, state, human-in-the-loop, and nested workflows, and a **Task API** for structured agent-to-agent delegation. Workflows are durable: from Python 1.16, a resumable workflow persists checkpoints via `DatabaseSessionService` (SQLite or Cloud SQL) and resumes from an Invocation ID after interruption ([ADK Resume Agents](https://google.github.io/adk-docs/runtime/resume/)).

**Fits when**: multi-agent workflows with explicit state transitions, long-running processes needing pause/resume across days, Google Cloud or Gemini-first stacks.

**Skip when**: single-agent short tasks where a `while` loop suffices, non-Python stacks.

### Agno

Python SDK positioned as "build, run, and manage agent platforms" ([Agno README](https://github.com/agno-agi/agno)). The runtime ships 50+ HTTP/SSE/WebSocket endpoints, OpenTelemetry tracing, JWT-based RBAC for multi-tenant isolation, cron scheduling, and pre-built Slack/Telegram/WhatsApp interfaces. Third-party benchmarks report ~2 μs agent instantiation and ~3.75 KiB per agent — roughly four orders of magnitude lighter than LangGraph ([Analytics Vidhya, 2025](https://www.analyticsvidhya.com/blog/2025/03/agno-framework/)). The micro-overhead matters only when instantiating thousands of agents per request.

**Fits when**: production agent platforms needing multi-tenant isolation, RBAC, and observability out of the box.

**Skip when**: single embedded agent inside a larger app — a control plane is overkill.

### Browser Use

Python (3.11+) agent that constrains the action space to a Playwright-controlled browser with a DOM-aware action vocabulary ([Browser Use README](https://github.com/browser-use/browser-use)). Benchmarked on 100 real-world browser tasks ([browser-use/benchmark](https://github.com/browser-use/benchmark)). DOM-based actions are more robust on standard layouts than coordinate-based computer-use models, which "don't yet work reliably enough in production" ([Helicone: Browser Use vs Computer Use vs Operator](https://www.helicone.ai/blog/browser-use-vs-computer-use-vs-operator)).

**Fits when**: the task is genuinely web-shaped — scraping behind logins, form filling, multi-step flows requiring DOM reasoning.

**Skip when**: the same task is reachable via an API (always cheaper), the work spans the desktop OS, or per-step LLM costs at scale outweigh a hybrid Playwright+AI approach ([Scrapfly: Stagehand vs Browser Use](https://scrapfly.io/blog/posts/stagehand-vs-browser-use)).

### Eigent

Open-source desktop multi-agent application built on CAMEL-AI, packaged as a TypeScript/Electron app ([Eigent README](https://github.com/eigent-ai/eigent)). Local model integration (vLLM, Ollama, LM Studio), SSO/RBAC, MCP integration, fully standalone deployment with no cloud account. The unit of distribution is an installed desktop app, not a library.

**Fits when**: end-user multi-agent productivity tooling, on-premise local deployment is a hard requirement (regulated industries, air-gapped environments).

**Skip when**: building an agent into another application — Eigent is the application, not a library.

### Letta (formerly MemGPT)

Stateful agent runtime — Python/TypeScript SDKs and REST API — built around server-side agent identity ([Letta README](https://github.com/letta-ai/letta)). Agents are created with explicit `memory_blocks` (`human`, `persona`) and an agent ID; subsequent requests address the same persistent agent. The model edits its own memory by calling `memory_replace`, `memory_insert`, `memory_rethink` tools — the "self-editing memory" model inherited from MemGPT ([Letta blog: Agent Memory](https://www.letta.com/blog/agent-memory)). Sleep-time compute uses idle periods to reorganise memory ([smeuse: MemGPT/Letta stateful agents](https://blog.smeuse.org/posts/memgpt-letta-stateful-agents)).

**Fits when**: the agent must persist a coherent identity across sessions and users; conversational apps with cross-session continuity.

**Skip when**: single-session tools where state has nowhere to be read back from — adoption adds a stateful service for no benefit and exposes you to the active Letta/Zep/mem0 benchmark dispute ([Atlan: Zep vs Mem0](https://atlan.com/know/zep-vs-mem0/)).

### mem0

Memory layer, not a runtime — Python and Node SDKs ([mem0 README](https://github.com/mem0ai/mem0)). Composes over any agent harness: you keep your loop and tools, mem0 handles extraction, storage, and retrieval. The April 2026 algorithm uses single-pass ADD-only extraction with entity linking and multi-signal retrieval (semantic + BM25 + entity), reporting 91.6 on LoCoMo and 94.8 on LongMemEval ([Mem0 research](https://mem0.ai/research)). The trade-off is real: an independent comparison measured mem0 at ~67% vs full-context ~73% — a ~6% accuracy gap as the price for token efficiency ([MindStudio: Mem0 vs OpenAI built-in memory](https://www.mindstudio.ai/blog/agent-memory-infrastructure-mem0-vs-openai)).

**Fits when**: you have a working agent and want cross-session memory without rewriting; recall-heavy workloads with relaxed accuracy needs (personalisation, support history).

**Skip when**: memory accuracy is load-bearing (medical, legal, compliance) — full-context with retrieval over authoritative sources beats lossy summarisation; or the agent is single-session.

## Why It Works

Framework primitives are designed for a specific task signature. ADK's graph-based Workflow Runtime works for long-running multi-agent processes because durable execution and explicit state transitions are exactly what workflows that pause for days need ([ADK Resume Agents](https://google.github.io/adk-docs/runtime/resume/)). Letta's server-stateful model works for cross-session identity because LLMs follow explicit memory-edit tool contracts more reliably than they manage arbitrary long-form context ([Letta: Agent Memory](https://www.letta.com/blog/agent-memory)). mem0's memory layer works for recall-heavy workloads because retrieval-augmented memory is linear-cost per turn instead of quadratic, paying for the accuracy gap with token economics ([Mem0 research](https://mem0.ai/research)). The wrong framework wastes effort because its primitives are tuned for a different task — you reimplement what it does badly and route around what you do not need.

## When This Backfires

- **No framework is the right answer**. LangChain — a framework vendor — itself argues that abstractions can "obfuscate and make it hard to ensure the LLM has appropriate context at each step" ([LangChain: How to think about agent frameworks](https://blog.langchain.com/how-to-think-about-agent-frameworks/)). For a single-session chatbot or short-horizon code agent, a 100-line `while` loop and a tracing call often beats any of the six.
- **Single-session, short-horizon agent** — adopting Letta or layering mem0 adds infrastructure and an accuracy gap for state that nothing reads back. Stateless is the right answer.
- **Non-Python primary stack** — Agno, ADK, Browser Use are Python-first; mem0 and Letta ship Node SDKs but most of the six force the language choice. A Go or Rust team adopting them stands up a Python sidecar service that complicates ops more than it simplifies agent code.
- **Computer-control beyond the browser** — Browser Use is browser-only; Eigent is desktop-packaged but Electron-bound. OS-level automation (native apps, SSH workflows, system-wide tasks) requires a different harness shape, typically Anthropic's Computer Use or local OS scripting.
- **Picking on benchmark headlines** — the Letta–Zep–mem0 leaderboard dispute signals immaturity in evaluation methodology rather than a clear memory winner ([Atlan: Zep vs Mem0](https://atlan.com/know/zep-vs-mem0/)). If your selection criterion is "best benchmark this quarter", you will re-pick every quarter.
- **High-stakes accuracy with mem0** — the ~6% accuracy gap is acceptable for personalisation chat, not for compliance-critical recall ([MindStudio](https://www.mindstudio.ai/blog/agent-memory-infrastructure-mem0-vs-openai)).

## Example

A team building a code-review agent for internal PRs starts by asking the five axes:

- **Task horizon**: one PR per invocation, single session — no checkpointing needed.
- **Action space**: read repo, call tests, post comments — tools only, no browser.
- **Memory model**: review conventions per repo persist; cross-PR review state does not.
- **Deployment shape**: library inside an existing CI service, not a control plane.
- **Language**: existing CI is Go.

None of the six fits naturally. ADK's Workflow Runtime is overkill for single-PR scope; Browser Use solves the wrong problem; Letta and mem0 add stateful infrastructure for state nothing reads back; Eigent is a desktop product; Agno is Python in a Go shop. The right answer is a direct Anthropic or Gemini SDK call from Go, with repo conventions loaded as `AGENTS.md` on each invocation — the same shape this site uses ([AGENTS.md standard](https://agents.md)).

Compare with a customer-support agent handling cross-session conversation history for thousands of users: horizon is long, memory model is server-stateful per user, deployment is a control plane. Letta is now the closest fit; mem0 is the lighter alternative if accuracy can absorb the gap.

## Key Takeaways

- The six frameworks sit at different layers — runtime (ADK, Agno), action space (Browser Use), memory (mem0), stateful agent runtime (Letta), desktop product (Eigent) — so selection is a task-shape match, not a feature comparison.
- Decide on five axes: task horizon, action space, memory model, deployment shape, language/ecosystem fit. The axes carry the decision; benchmarks rarely do.
- No framework is often the right answer for single-session, short-horizon agents — production teams ship directly on model SDKs plus tracing.
- Picking on benchmark headlines locks you into vendor methodology disputes that turn over quarterly; pick on integration shape instead.

## Related

- [The Agent Stack Bet: Architectural Decisions for Production Agents](agent-stack-bets.md) — the four bets enterprise agents take when prompting stops being the bottleneck
- [Anthropic's Effective Agents Framework: A Pattern Map](anthropic-effective-agents-framework.md) — the augmented-LLM and workflow patterns these frameworks implement
- [Agent Memory Patterns: Learning Across Conversations](agent-memory-patterns.md) — scope and temporal memory choices that frame the Letta and mem0 decisions
- [Tiered Memory Architecture](tiered-memory-architecture.md) — when episodic-to-semantic consolidation pays off, independent of which memory layer you adopt
- [Multi-Agent Topology Taxonomy](../multi-agent/multi-agent-topology-taxonomy.md) — the centralised/decentralised/hybrid choice that ADK and Agno multi-agent setups must make
