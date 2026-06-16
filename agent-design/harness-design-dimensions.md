---
title: "Harness Design Dimensions and Archetypes"
description: "Five design dimensions and five archetypes derived from 70 agent-system projects — a population-level lens for characterising harness choices."
tags:
  - agent-design
  - tool-agnostic
  - harness-engineering
  - arxiv
  - long-form
aliases:
  - agent harness design dimensions
  - agent-system archetypes
  - harness archetype taxonomy
last_reviewed: 2026-05-27
maturity: emerging
---

# Harness Design Dimensions and Archetypes

> A source-grounded study of 70 agent-system projects reduces harness infrastructure to five recurring design dimensions and five archetypes — a population-level lens for reading and comparing harnesses.

## Why Dimensions Beat Ad-Hoc Comparison

Harness code — the non-LLM mediator handling tools, context, delegation, safety, and orchestration — determines agent behaviour as much as the model. Independent evidence: pure harness changes took Terminal Bench 2.0 from 52.8% to 66.5% ([LangChain](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)). Projects therefore diverge sharply in how they engineer this layer.

[Hu Wei (2026) "Architectural Design Decisions in AI Agent Harnesses"](https://arxiv.org/abs/2604.18071) analyses 70 publicly available agent-system projects through source code and technical material. The output is a shared vocabulary for reading harness choices at the ecosystem level.

## Five Design Dimensions

```mermaid
graph TD
    H[Agent Harness] --> SA[Subagent Architecture]
    H --> CM[Context Management]
    H --> TS[Tool Systems]
    H --> SM[Safety Mechanisms]
    H --> OR[Orchestration]
```

Each dimension is a position choice, not a binary ([arXiv:2604.18071](https://arxiv.org/abs/2604.18071)):

- **Subagent architecture** — flat, hierarchical, or peer coordination between specialised agents.
- **Context management** — file-persistent, hybrid, and hierarchical strategies dominate the corpus; ephemeral in-memory is rarer in production systems.
- **Tool systems** — registry-oriented systems are dominant; [MCP](../tool-engineering/mcp-result-persistence-annotation.md)- and plugin-oriented extensions are emerging.
- **Safety mechanisms** — intermediate isolation ([sandboxes](../security/sandbox-runtime-comparison.md), [permission prompts](../security/permission-gated-commands.md)) is common; high-assurance audit ([provenance-aware decision auditing](../security/provenance-aware-decision-auditing.md)) is rare.
- **Orchestration** — the control flow and scheduling layer around agent loops.

The paper complements the 12-dimension / 13-system scaffold-architecture taxonomy ([arXiv:2604.03515](https://arxiv.org/abs/2604.03515)) detailed in the next section: finer-grained analysis of individual scaffolds, lower population coverage. Pick the five-dimension view for cross-ecosystem reading; pick the 12-dimension view when characterising a single scaffold in depth.

## Co-occurrence: Choices Cluster

Design dimensions are not independent. [arXiv:2604.18071](https://arxiv.org/abs/2604.18071) reports three recurring clusters:

| Cluster | What pairs with what |
|---------|----------------------|
| Coordination ↔ context | Deeper subagent coordination pairs with more explicit context services |
| Execution ↔ governance | Stronger execution environments correlate with more structured governance |
| Tooling ↔ ecosystem | Formalised tool-registration boundaries align with broader ecosystem ambitions |

The implication for design: a single upgrade rarely lands in isolation. Adding multi-agent coordination without corresponding [context services](../context-engineering/phase-specific-context-assembly.md) leaves agents starved of state; tightening tool boundaries without ecosystem commitments imposes cost without the reach that justifies it.

## Five Archetypes

The same paper groups the 70 projects into five recurring archetypes ([arXiv:2604.18071](https://arxiv.org/abs/2604.18071)):

| Archetype | Profile |
|-----------|---------|
| Lightweight tools | Minimal harness infrastructure; a thin loop around tool calls |
| Balanced CLI frameworks | Moderate complexity; CLI-oriented with adaptive loops and registry tools |
| Multi-agent orchestrators | Deep coordination, explicit context services, role-specialised subagents |
| Enterprise systems | Structured governance, stronger isolation, broader ecosystem scope |
| Scenario-verticalised projects | Domain-specific harnesses optimised for one class of workflow |

Archetypes are descriptive clusters, not prescriptions. A project's archetype emerges from the dimension choices that reinforce each other — which is why the co-occurrence clusters matter more than any individual dimension.

## Reading a Harness with the Framework

Apply the five dimensions in order when evaluating or designing a harness:

1. Where on the subagent spectrum — single loop, delegated roles, or peer coordination?
2. Which context strategy — file-persistent, hybrid, hierarchical, or ephemeral?
3. Which tool system — direct shell, typed registry, MCP, or plugin?
4. Which safety posture — none, intermediate isolation, or high-assurance audit?
5. Which orchestration layer — fixed pipeline, adaptive loop, or external scheduler?

Read the cluster alignments to predict where effort is missing: a project with multi-agent coordination but no file-persistent context is likely under-invested on context services; one with formal tool registration but no ecosystem scope is paying integration cost without reach.

## When the Framework Under-Delivers

- **Single-script tools** — only one or two dimensions are meaningful; the archetype collapses to "lightweight tools" without informing design.
- **Pre-production prototypes** — co-occurrence patterns assume differentiated systems; early harnesses are not yet clustered.
- **In-house vertical harnesses** — the archetype is predetermined by the domain, so the framework adds vocabulary without decision support.

## Example

Reading two public harnesses through the dimensions:

**Harness A — a terminal coding agent**: single control loop (flat subagent), accumulated in-memory context with summarisation on threshold, typed tool registry exposed as a shell-like interface, permission prompts before destructive actions, adaptive orchestration. Archetype: balanced CLI framework. Expected co-occurrence gap: limited multi-agent coordination means no need for explicit context services, which matches its [single-context strategy](loop-strategy-spectrum.md).

**Harness B — a multi-agent research system**: hierarchical subagents with [orchestrator-worker](../multi-agent/multi-agent-topology-taxonomy.md) topology, file-persistent [progress files](../observability/trajectory-logging-progress-files.md) and hybrid per-agent context, plugin-style tool registration with MCP extensions, sandbox isolation and audit logging, external scheduler driving orchestration. Archetype: multi-agent orchestrator / enterprise. Co-occurrence checks pass: deep coordination paired with explicit context services; formal tool registration paired with ecosystem scope.

The dimensions frame the differences; the archetypes name the clusters.

## The 12-Dimension Scaffold Taxonomy (Single-Scaffold View)

For characterising one scaffold in depth, [source-code analysis of 13 open-source coding agent scaffolds](https://arxiv.org/abs/2604.03515) reduces the same harness layer to 12 dimensions grouped in three layers. Architecturally distinct systems produce identical surface capabilities — trajectory studies observe outputs without explaining differences — so the taxonomy makes the design choices comparable.

```mermaid
graph TD
    S[Coding Agent Scaffold] --> CA[Control Architecture]
    S --> TEI[Tool & Environment Interface]
    S --> RM[Resource Management]

    CA --> CA1[Loop topology]
    CA --> CA2[Planning strategy]
    CA --> CA3[Search / branching]
    CA --> CA4[Error recovery]

    TEI --> TEI1[Tool abstraction level]
    TEI --> TEI2[Environment access model]
    TEI --> TEI3[Feedback routing]
    TEI --> TEI4[Output typing]

    RM --> RM1[Context budget strategy]
    RM --> RM2[State persistence]
    RM --> RM3[Tool-call capping]
    RM --> RM4[Cost guardrails]
```

**Layer 1 — Control architecture** decides what to do next and when to stop. *Loop topology* is a spectrum: fixed pipelines run a predetermined sequence; adaptive loops react to tool output; MCTS scaffolds build a search tree with backtracking — Moatless Tools implements full MCTS with numeric reward and backpropagation ([arXiv:2604.03515](https://arxiv.org/abs/2604.03515)).

| Topology | Predictability | Compute | Best for |
|----------|---------------|---------|----------|
| Fixed pipeline | High | Low | Well-defined, repeatable tasks |
| Adaptive loop | Medium | Medium | Observation-reaction cycles |
| MCTS / search | Low | High | Unknown solution paths |

*Planning strategy* decides whether the scaffold reasons about future steps before acting ([planning-first emits a plan then executes](../workflows/plan-first-loop.md); interleaved adapts at the cost of inspectability). *Error recovery* ranges from aborting on first failure to retry loops, exception-specific handlers, and [rollback to checkpoints](exception-handling-recovery-patterns.md).

**Layer 2 — Tool and environment interface.** *Tool abstraction level* varies from direct shell (maximum flexibility, no boundary for testing) to typed registries that reject malformed calls and enable [reasoning/execution separation](cognitive-reasoning-execution-separation.md). *Environment access model* sets what the agent can observe and modify ([sandboxes give a recoverable surface](rollback-first-design.md)). *Feedback routing* controls where tool results go — returning all output to context is simple but expensive; routing large outputs to disk with a summary preserves budget ([Anthropic: Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).

**Layer 3 — Resource management** handles the bounded resources of a model-in-a-loop. *Context budget strategy* decides what enters context and when it is pruned (see [Loop Strategy Spectrum](loop-strategy-spectrum.md)). *State persistence* decides what survives between iterations — in-memory state is lost on failure, file-backed state enables resumption via [progress files](../observability/trajectory-logging-progress-files.md) and [feature list files](../instructions/feature-list-files.md). *Tool-call capping* and *cost guardrails* bound unbounded loops per session, per tool, or per cost.

Scaffold architectures **resist discrete classification** ([arXiv:2604.03515](https://arxiv.org/abs/2604.03515)): 11 of 13 agents analysed compose multiple loop primitives rather than implementing one. Treat dimensions as continuous scales — ask "where does this scaffold sit on the control strategy spectrum?" rather than "is this a pipeline or an agent?" Reading three open-source scaffolds through the control layer: **[Agentless](https://arxiv.org/abs/2604.03515)** runs a 10-stage pipeline of independent scripts linked by JSONL on disk — predictable, auditable, cheap, but degrades when reproduction needs exploration; **SWE-agent** runs a single ReAct loop over a typed tool registry and restricted shell — more robust to unexpected paths, higher per-run cost; **Moatless Tools** runs full MCTS — strongest on open-ended tasks, highest compute, hardest to debug when a bad branch dominates. The 12-dimension view adds overhead without value for single-script tools (no meaningful control architecture to classify) and retrospective audits (it tells you what was built, not whether the design was right).

## Key Takeaways

- Five dimensions — subagent architecture, context management, tool systems, safety mechanisms, orchestration — cover the non-LLM choices in an agent harness.
- Dimension choices cluster: coordination with context services, execution with governance, tooling with ecosystem. Single-axis upgrades under-perform the paired investment.
- Five archetypes (lightweight, CLI, multi-agent, enterprise, verticalised) are descriptive clusters derived from the 70-project corpus, not prescribed templates.
- The framework is most useful at ecosystem level; pair it with a finer-grained taxonomy when characterising a single scaffold.
- Rare-in-corpus signals are actionable: high-assurance audit is uncommon, so any project claiming it should be verified, not assumed.

## Related

- [Agent Harness: Initializer and Coding Agent](agent-harness.md)
- [Harness Engineering](harness-engineering.md)
- [Harness Hill-Climbing: Eval-Driven Iterative Improvement of Agent Harnesses](harness-hill-climbing.md)
- [Runtime Scaffold Evolution: Agents That Build Tools](runtime-scaffold-evolution.md)
- [Cognitive Reasoning vs Execution: A Two-Layer Agent Architecture](cognitive-reasoning-execution-separation.md)
- [Managed vs Self-Hosted Harness](managed-vs-self-hosted-harness.md)
- [Loop Strategy Spectrum](loop-strategy-spectrum.md)
- [Multi-Agent Topology Taxonomy](../multi-agent/multi-agent-topology-taxonomy.md)
  - long-form
