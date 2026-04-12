---
title: "Declarative Multi-Agent Composition"
description: "Define agents and workflows as data, not code — declarative composition surfaces design decisions, enables tooling, and makes multi-agent systems debuggable."
tags:
  - agent-design
  - multi-agent
  - observability
aliases:
  - "define-and-compose"
  - "declarative agent orchestration"
---

# Declarative Multi-Agent Composition

> Define agents and their coordination as structured data — models, tools, memory, and orchestration rules — then compose them into workflows through explicit wiring rather than imperative code.

## Why Declarative

Imperative multi-agent code tangles agent capabilities, coordination logic, and runtime behavior. When a workflow fails, the developer must trace through code to distinguish a misconfigured agent from a wrong handoff or a runtime error. Declarative specs separate these layers.

A declarative definition captures the **what** (model, tools, memory) without encoding the **how** (framework internals, API call sequences, retry logic). This makes agent configurations:

- **Inspectable** — the full agent spec is readable without running anything
- **Diffable** — changes between workflow versions show up as structured data changes, not code refactors
- **Portable** — the same spec can drive a visual builder, a CLI, or a CI pipeline

## The Define-and-Compose Pattern

The [AutoGen Studio research](https://arxiv.org/abs/2408.15247) (EMNLP 2024), drawing on 200,000+ installations and 135+ user-reported issues, identified **define-and-compose** as the dominant workflow authoring pattern across multi-agent developer tooling.

The pattern has two phases:

**Define** — create each component independently with explicit parameters:

```json
{
  "agent": {
    "name": "code-reviewer",
    "model": "claude-sonnet-4-20250514",
    "tools": ["read_file", "grep", "git_diff"],
    "system_prompt": "You review code changes for correctness and style.",
    "max_tokens": 4096
  }
}
```

**Compose** — wire agents into a workflow by specifying coordination, not implementation:

```json
{
  "workflow": {
    "name": "review-pipeline",
    "agents": ["code-reviewer", "security-auditor", "test-verifier"],
    "orchestration": "sequential",
    "handoff": { "format": "structured-json", "fields": ["verdict", "issues", "notes"] }
  }
}
```

This mirrors how production teams already think — roles first, then coordination — but makes the structure machine-readable.

## Built-In Profiling Changes the Debugging Model

Multi-agent workflows fail in ways single-agent systems do not: coordination failures, context loss at handoffs, and cascading errors across agents. The AutoGen Studio research identified **debugging and sensemaking tools** as a critical, frequently requested capability — multi-agent systems need observability built into the composition layer, not bolted on after.

Effective multi-agent profiling surfaces:

- **Token cost per agent** — identifies which agents consume disproportionate context
- **Tool invocation frequency and success rate** — reveals agents that call tools repeatedly without progress (see [Loop Detection](../observability/loop-detection.md))
- **Message flow between agents** — traces the actual coordination path versus the intended one
- **Per-agent timing** — exposes bottleneck agents in sequential workflows

When agent definitions are declarative, the runtime can instrument every agent boundary automatically. Imperative code requires manual instrumentation at each handoff point.

## The Export-to-Code Path

Visual/declarative tools work for prototyping, but production deployments need code. The pattern that works is **declarative-first, code-second**:

1. **Prototype** in declarative format — fast iteration, visual feedback
2. **Validate** with built-in profiling — catch coordination issues early
3. **Export** to code when the workflow is stable — full control, version-controlled, testable

This avoids the [Framework-First anti-pattern](../anti-patterns/framework-first.md) by starting with explicit specifications rather than opaque abstractions.

## When Declarative Composition Breaks Down

Declarative specs work well for **static workflows** — fixed agent sets with known coordination patterns. They struggle with:

- **Dynamic agent creation** — workflows that spawn agents based on runtime conditions need imperative escape hatches
- **Complex conditional routing** — "if the reviewer finds security issues, spawn a security specialist" is awkward in pure JSON
- **Shared mutable state** — agents that read and write shared context during execution require runtime coordination beyond what a static spec captures

The practical boundary: use declarative composition for the workflow skeleton, imperative code for runtime adaptation.

```mermaid
graph LR
    A[Define Agents<br/>model + tools + prompt] --> B[Compose Workflow<br/>agents + orchestration]
    B --> C[Prototype & Profile<br/>run + observe + iterate]
    C --> D{Stable?}
    D -- No --> B
    D -- Yes --> E[Export to Code<br/>version control + CI]

    style A fill:#e1f5fe
    style B fill:#e1f5fe
    style C fill:#fff3e0
    style E fill:#e8f5e9
```

## Example

A CI pipeline that reviews pull requests using three agents defined declaratively and composed into a sequential workflow:

```yaml
agents:
  code-reviewer:
    model: claude-sonnet-4-20250514
    tools: [read_file, git_diff]
    prompt: "Review code changes for correctness and style violations."
    max_tokens: 4096

  security-scanner:
    model: claude-sonnet-4-20250514
    tools: [read_file, grep, semgrep_run]
    prompt: "Scan changed files for security vulnerabilities."
    max_tokens: 4096

  test-verifier:
    model: claude-sonnet-4-20250514
    tools: [run_tests, read_file]
    prompt: "Verify that existing tests pass and new code has coverage."
    max_tokens: 2048

workflow:
  name: pr-review-pipeline
  orchestration: sequential
  stages:
    - agent: code-reviewer
      output: { verdict: string, issues: list }
    - agent: security-scanner
      output: { vulnerabilities: list, severity: string }
    - agent: test-verifier
      output: { passed: bool, coverage_delta: number }
  final_gate:
    approve_if: "all(stage.verdict != 'reject' for stage in stages)"
```

Adding a fourth agent requires one new block under `agents:` and one new entry under `stages:` — no coordination code changes. The runtime instruments each stage boundary automatically, producing per-agent token counts and timing without manual instrumentation.

## Key Takeaways

- Define agents as structured data (model, tools, memory, prompt) before writing coordination code
- Compose workflows by wiring agent definitions, not by coding agent interactions
- Build profiling into the composition layer — multi-agent debugging requires per-agent observability from the start
- Use declarative specs for prototyping and validation; export to code for production
- Cross-reference coordination issues with [Agent Handoff Protocols](agent-handoff-protocols.md) — handoff protocols define what flows between declarative stages

## Related

- [Agent Handoff Protocols](agent-handoff-protocols.md) — structured contracts between pipeline stages
- [Multi-Agent Topology Taxonomy](multi-agent-topology-taxonomy.md) — choosing the right coordination structure
- [Framework-First Development](../anti-patterns/framework-first.md) — why starting with frameworks before understanding the raw API is risky
- [Agent Debugging](../observability/agent-debugging.md) — diagnosing bad output in single-agent systems
- [Loop Detection](../observability/loop-detection.md) — detecting agents stuck in unproductive cycles
- [OpenTelemetry for Agent Observability](../standards/opentelemetry-agent-observability.md) — standardized observability for agent systems
- [Orchestrator-Worker](orchestrator-worker.md) — the most common multi-agent coordination topology
- [Subagent Schema-Level Tool Filtering](subagent-schema-level-tool-filtering.md) — declarative specs for constraining subagent tool access

