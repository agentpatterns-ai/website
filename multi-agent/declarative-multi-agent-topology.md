---
title: "Declarative Multi-Agent Topology: Topology-as-Code"
term: "Declarative Multi-Agent Topology"
description: "Define an entire agent graph — agents, flows, gates, hooks, group chats — in a single declarative file that compiles to any target runtime, making agent relationships auditable and portable."
tags:
  - multi-agent
  - agent-design
  - tool-agnostic
aliases:
  - topology-as-code
  - agent graph definition
last_reviewed: 2026-06-13
maturity: emerging
---

<!-- source: nibzard/awesome-agentic-patterns (Apache 2.0, https://github.com/nibzard/awesome-agentic-patterns) — retain attribution per license -->

# Declarative Multi-Agent Topology: Topology-as-Code

> Encode an entire agent graph in one declarative file a compiler targets to any framework, making the topology auditable, portable, and reusable across runtimes.

## The problem

Multi-agent systems built imperatively scatter orchestration logic across framework-specific code. Relationships between agents stay implicit. Switching frameworks means rewriting [coordination logic](multi-agent-topology-taxonomy.md), not just adapting configs. The topology is not a reviewable artifact. It emerges from the code instead.

Topology-as-code separates graph structure from runtime implementation. The topology file is the single source of truth. A compiler then emits the framework-specific code or configuration.

## Five core primitives

The pattern builds on five building blocks, documented in the [nibzard/awesome-agentic-patterns catalog](https://github.com/nibzard/awesome-agentic-patterns/blob/main/patterns/declarative-multi-agent-topology-definition.md):

| Primitive | What it defines |
|-----------|----------------|
| Agents | Name, model, role, tools, operational constraints |
| Flows | Directed connections — pipelines, fan-out, fan-in, cycles |
| Gates | Approval checkpoints — human, automated, or conditional |
| Hooks | Lifecycle callbacks — pre-run, post-run, on-error |
| Group chats | Multi-agent conversation protocols with turn-taking rules |

Together these five elements describe the full graph: who the agents are, how work moves between them, where it stops for review, what fires on lifecycle events, and how agents converse.

## Compilation model

A compiler reads the topology file, parses it into an abstract syntax tree, and emits platform-specific outputs:

```mermaid
graph LR
    A[topology.at] --> B[Parser / AST]
    B --> C[Claude Code]
    B --> D[Codex]
    B --> E[Cursor]
    B --> F[Gemini CLI]
    B --> G[GitHub Copilot]
```

Each emitted output is a native config or scaffold for the target runtime. Translation is lossy. Not every platform exposes all five primitives, so the declarative file holds the intended topology and the compiler approximates it for each target.

## Reference implementation

[AgenTopology](https://github.com/agentopology/agentopology) (Apache 2.0) implements this pattern with:

- `.at` file syntax for declaring topology
- Multi-platform scaffolding targeting Claude Code, Codex, Cursor, Gemini CLI, Copilot, and Kiro
- Interactive visualizer rendering the graph
- Validation engine with built-in rules (the repo advertises 82, though its docs are internally inconsistent on the count)
- Claude Code skill interface for natural-language topology design

As of June 2026 the project is early-stage (under 100 GitHub stars) and the surrounding tooling is still young. Adapter fidelity across target platforms has not been independently verified. The project states adapters are "ground-truth validated against real-world configs" but does not list per-platform feature gaps, so evaluate against your target runtime before adopting. The repo's own docs are inconsistent on the rule count (82 in one place, 29 in another), so treat the validation surface as still settling.

## How this differs from related patterns

This pattern is distinct from three related pages on this site:

| Pattern | Scope | Unit |
|---------|-------|------|
| [Declarative Multi-Agent Composition](declarative-multi-agent-composition.md) | Define agents and workflows as structured data within a framework | Single workflow spec |
| [Portable Agent Definitions](../standards/portable-agent-definitions.md) | Package a single agent's identity, tools, and compliance as a portable artifact | Individual agent |
| [Multi-Agent Topology Taxonomy](multi-agent-topology-taxonomy.md) | Which topology (centralized, decentralized, hybrid) to choose | Decision guide |
| Topology-as-code | Encode the entire graph — agents + relationships + gates — as a portable, compilable artifact | Whole system |

## Trade-offs

| Benefit | Cost |
|---------|------|
| One topology definition targets multiple frameworks | New syntax to learn — DSL on top of existing frameworks |
| Graph is visible and reviewable in one file | Abstraction ceiling — platform-specific features may not map cleanly |
| Gates and permissions are explicit and version-controlled | Compiler quality varies; adapter fidelity depends on maintenance |
| Common patterns (pipeline, fan-out, supervisor) become reusable templates | Immature project — limited tooling and community support as of 2025–2026 |
| Topology file is documentation — readable without running anything | Mismatch risk — emitted code can diverge from topology intent when adapters lag framework updates |

## Example

A two-agent code-review topology with a human approval gate, illustrating the five-primitive structure. The schema below is representative of the pattern — exact `.at` syntax varies by implementation:

```yaml
agents:
  reviewer:
    model: claude-sonnet-4
    role: "Review code changes for correctness and style."
    tools: [read_file, git_diff]

  security-scanner:
    model: claude-sonnet-4
    role: "Scan changed files for security vulnerabilities."
    tools: [read_file, grep, semgrep_run]

flows:
  - from: reviewer
    to: security-scanner
    type: parallel

  - from: [reviewer, security-scanner]
    to: gate:human-approval
    type: fan-in

gates:
  human-approval:
    type: human
    message: "Review both agents' findings before merging."
```

Running the compiler against this file emits platform-specific configs for each target. Adding a third agent requires one new block under `agents:` and one new entry under `flows:` — no coordination code changes.

## Key Takeaways

- Topology-as-code separates graph structure from runtime implementation — the topology file is the reviewable artifact, not the emitted code
- Five primitives cover the full graph: agents, flows, gates, hooks, group chats
- A compiler targets the same topology at multiple frameworks, but translation is lossy — adapters approximate the intent
- Gates encoded in the topology file keep approval checkpoints explicit and version-controlled
- The pattern is sound; the ecosystem is early-stage — evaluate implementations against your target platforms before committing

## Related

- [Declarative Multi-Agent Composition](declarative-multi-agent-composition.md) — define agents and workflows as structured data within a single framework
- [Multi-Agent Topology Taxonomy](multi-agent-topology-taxonomy.md) — choosing between centralised, decentralised, and hybrid topologies
- [Portable Agent Definitions](../standards/portable-agent-definitions.md) — packaging individual agent identity as a portable, version-controlled artifact
- [Agent Handoff Protocols](agent-handoff-protocols.md) — typed contracts between pipeline stages that flows enforce
- [Subagent Schema-Level Tool Filtering](subagent-schema-level-tool-filtering.md) — declarative constraints on subagent tool access
- [Fan-Out Synthesis Pattern](fan-out-synthesis.md) — parallel agent execution that flows can encode
