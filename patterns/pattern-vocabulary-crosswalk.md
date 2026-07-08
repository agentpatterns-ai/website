---
title: "Agentic Pattern Vocabulary Crosswalk"
term: "Agentic Pattern Vocabulary Crosswalk"
description: "Map competing agentic-pattern vocabularies — Ng's four, Anthropic's five, Gulli's twenty-one, CoALA's three axes — onto this site's canonical pages so readers find coverage by whichever name they arrived with."
tags:
  - pattern
  - agent-design
  - tool-agnostic
  - long-form
aliases:
  - agent pattern terminology crosswalk
  - agentic design pattern mapping
last_reviewed: 2026-06-16
maturity: established
---

# Agentic Pattern Vocabulary Crosswalk

> Crosswalk that maps four agentic pattern vocabularies — Ng's four, Anthropic's five, Gulli's twenty-one, CoALA's three axes — to this site's canonical pages.

External readers and AI agents arrive with whichever vocabulary their source used — "Reflection" from Andrew Ng, "Orchestrator-Workers" from Anthropic, "Goal Setting" from Antonio Gulli, "structured action space" from CoALA. This crosswalk is a navigation aid that resolves each external term to the site's canonical page for the same concept. It is not a second authoritative definition of any pattern: every row leads with the link, and the body lives on the linked page.

For the cross-pattern trade-off view (token cost, latency, blast radius, verification cost), use the sibling [Pattern Selection Map](selection-map.md). For the broader cross-vendor terminology discussion (workflow vs agent vs assistant vs RAG pipeline), see [Agent Terminology Disambiguation](../agent-design/agent-terminology-disambiguation.md). For an Anthropic-only mapping with augmented-LLM context, see [Anthropic's Effective Agents Framework](../agent-design/anthropic-effective-agents-framework.md).

## How to read the tables

Each row gives the external term, a one-line scope-difference note (because the mappings are rarely 1:1), and the site's canonical page. A blank "Scope difference" cell means the external term and the site page name the same concept at the same scope. Coverage as of `last_reviewed`.

## Andrew Ng's four agentic design patterns

Andrew Ng's 2024 DeepLearning.AI series names four patterns that improve agentic-coding results across model families, drawing from a corpus of papers including AutoGen, ReAct, and ChatDev ([DeepLearning.AI — Agentic Design Patterns Part 1](https://www.deeplearning.ai/the-batch/how-agents-can-improve-llm-performance/); covered on-site at [Anthropic's Effective Agents Framework](../agent-design/anthropic-effective-agents-framework.md) and [Agent Terminology Disambiguation](../agent-design/agent-terminology-disambiguation.md)).

| Ng's pattern | Scope difference | This site's canonical page |
|---|---|---|
| Reflection | Ng frames reflection as a self-evaluation step inside an agent loop. The site splits this across a code-review-loop variant and a generator/critic split. | [Agent Self-Review Loop](../code-review/agent-self-review-loop.md), [Evaluator-Optimizer](../agent-design/evaluator-optimizer.md) |
| Tool Use | Ng treats tool use as a single pattern; the site decomposes it into tool design, advanced tool use, MCP, and skills. | [Advanced Tool Use](../tool-engineering/advanced-tool-use.md), [Tool Engineering](../tool-engineering/tool-engineering.md) |
| Planning | Ng's planning is a runtime "decompose first, then execute" loop; the site's [`plan-first-loop`](../workflows/plan-first-loop.md) is the workflow shape, while the cognitive split is a separate pattern. | [Plan-First Loop](../workflows/plan-first-loop.md), [Cognitive Reasoning vs Execution Separation](../agent-design/cognitive-reasoning-execution-separation.md) |
| Multi-Agent Collaboration | Ng treats multi-agent as one pattern; the site indexes it as a whole section organised by topology. | [Multi-Agent (section index)](../multi-agent/index.md), [Multi-Agent Topology Taxonomy](../multi-agent/multi-agent-topology-taxonomy.md) |

## Anthropic's five workflow patterns

Anthropic's 'Building Effective Agents' names five workflow patterns — control-flow defined in code — plus an autonomous-agent loop where the model owns control flow ([Anthropic — Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)). The full taxonomy mapping with augmented-LLM context lives at [Anthropic's Effective Agents Framework](../agent-design/anthropic-effective-agents-framework.md); the rows below are the navigation lookup.

| Anthropic pattern | Scope difference | This site's canonical page |
|---|---|---|
| Prompt chaining | | [Prompt Chaining](../context-engineering/prompt-chaining.md) |
| Routing | Anthropic names the classify-then-dispatch shape. The site's canonical page emphasises the cost-aware "cheapest model that solves it" variant. | [Parsimonious Agent Routing](../multi-agent/parsimonious-agent-routing.md) |
| Parallelization | Anthropic covers sectioning (independent subtasks) and voting (consensus). The site's `fan-out-synthesis` is the sectioning variant; voting is a separate pattern. | [Fan-Out Synthesis](../multi-agent/fan-out-synthesis.md), [Voting Ensemble Pattern](../multi-agent/voting-ensemble-pattern.md) |
| Orchestrator-workers | | [Orchestrator-Worker](../multi-agent/orchestrator-worker.md) |
| Evaluator-optimizer | | [Evaluator-Optimizer](../agent-design/evaluator-optimizer.md) |

For the autonomous-agent layer above these five workflows, see [Goal-Driven Autonomous Loop](../loop-engineering/goal-driven-autonomous-loop.md), [Loop Strategy Spectrum](../loop-engineering/loop-strategy-spectrum.md), and [Agentless vs Autonomous](../agent-design/agentless-vs-autonomous.md).

## Antonio Gulli's twenty-one agentic design patterns

Antonio Gulli's 'Agentic Design Patterns' book organizes 21 patterns across Core (8), Advanced (6), and Specialized (7) categories. A reference implementation in LangChain + Gemini covers all 21 ([`josephsenior/Agentic-Design-Patterns`](https://github.com/josephsenior/Agentic-Design-Patterns)). Coverage flags below: covered = at least one direct canonical page, partial = adjacent pages but no first-class treatment, gap = no direct coverage as of `last_reviewed`.

### Gulli's 8 Core patterns

| Gulli's pattern | Scope difference | This site's canonical page | Status |
|---|---|---|---|
| Prompt Chaining | | [Prompt Chaining](../context-engineering/prompt-chaining.md) | covered |
| Routing | Same scope difference as Anthropic's row above. | [Parsimonious Agent Routing](../multi-agent/parsimonious-agent-routing.md) | covered |
| Parallelization | Same scope difference as Anthropic's row above. | [Fan-Out Synthesis](../multi-agent/fan-out-synthesis.md) | covered |
| Reflection | Same scope difference as Ng's row above. | [Agent Self-Review Loop](../code-review/agent-self-review-loop.md) | covered |
| Tool Use | | [Advanced Tool Use](../tool-engineering/advanced-tool-use.md) | covered |
| Planning | | [Plan-First Loop](../workflows/plan-first-loop.md) | covered |
| Multi-Agent | | [Multi-Agent (section index)](../multi-agent/index.md) | covered |
| Memory Management | Gulli treats memory as one pattern; the site decomposes it into scope/temporal patterns and a CoALA-aligned taxonomy. | [Agent Memory Patterns](../agent-design/agent-memory-patterns.md), [CoALA Memory Taxonomy Classifier](../agent-design/coala-memory-taxonomy-classifier.md) | covered |

### Gulli's 6 Advanced patterns

| Gulli's pattern | Scope difference | This site's canonical page | Status |
|---|---|---|---|
| Learning and Adaptation | Gulli covers cross-task adaptation; the site's page focuses on layered continual learning across model and harness. | [Continual Learning Layers](../agent-design/continual-learning-layers.md) | covered |
| Model Context Protocol (MCP) | | [MCP Protocol](../standards/mcp-protocol.md) | covered |
| Goal Setting and Monitoring | | [Goal Monitoring and Progress Tracking](../agent-design/goal-monitoring-progress-tracking.md) | covered |
| Exception Handling and Recovery | | [Exception Handling and Recovery Patterns](../agent-design/exception-handling-recovery-patterns.md) | covered |
| Human-in-the-Loop | Gulli covers human-in-the-loop broadly; the site has a workflow page and a security-side confirmation-gates page. | [Human-in-the-Loop](../workflows/human-in-the-loop.md), [Human-in-the-Loop Confirmation Gates](../security/human-in-the-loop-confirmation-gates.md) | covered |
| Knowledge Retrieval (RAG) | Gulli treats RAG as a single pattern; the site's canonical RAG page frames it as on-demand / JIT context retrieval (and declares "RAG" an explicit alias). | [Retrieval-Augmented Agent Workflows](../context-engineering/retrieval-augmented-agent-workflows.md) | covered |

### Gulli's 7 Specialized patterns

| Gulli's pattern | Scope difference | This site's canonical page | Status |
|---|---|---|---|
| Inter-Agent Communication (A2A) | | [A2A Protocol](../standards/a2a-protocol.md) | covered |
| Resource-Aware Optimization | Gulli covers cost/latency optimisation generally; the site's coverage is the cost-aware-design page plus the routing page above. | [Cost-Aware Agent Design](../token-engineering/cost-aware-agent-design.md) | covered |
| Reasoning Techniques | Gulli covers chain-of-thought, ReAct, and tree-of-thoughts as reasoning patterns. The site treats reasoning as a cognitive-execution split plus a three-spaces decomposition. | [Cognitive Reasoning vs Execution Separation](../agent-design/cognitive-reasoning-execution-separation.md), [Three Reasoning Spaces](../agent-design/three-reasoning-spaces.md) | covered |
| Guardrails / Safety Patterns | Gulli covers safety as one pattern; the site has a four-layer taxonomy and a defence-in-depth page that decompose it further. | [Four-Layer Agent Security Taxonomy](../security/four-layer-agent-security-taxonomy.md), [Defense-in-Depth Agent Safety](../security/defense-in-depth-agent-safety.md) | covered |
| Evaluation and Monitoring | Gulli covers evaluation as one pattern; the site separates evaluator-as-pattern from eval-as-workflow. | [Evaluator-Optimizer](../agent-design/evaluator-optimizer.md), [LLM-as-Judge Evaluation](../workflows/llm-as-judge-evaluation.md) | covered |
| Prioritization | Gulli treats prioritization as next-action ranking; the site's page focuses on rank-vs-routing-vs-scheduling and dependency-aware signals. | [In-Agent Task Prioritization](../agent-design/in-agent-task-prioritization.md) | covered |
| Exploration and Discovery | Gulli frames exploration as a search-and-discover pattern; the site's coverage is the best-of-n delegation page and a discovery-only refactor workflow. | [Recursive Best-of-N Delegation](../multi-agent/recursive-best-of-n-delegation.md), [Discovery-Only Refactor Pass](../workflows/discovery-only-refactor-pass.md) | covered |

## CoALA's three axes

CoALA (Cognitive Architectures for Language Agents) is a peer-reviewed conceptual framework that organizes language agents along three axes ([arxiv:2309.02427](https://arxiv.org/abs/2309.02427); on-site at [Cognitive Architectures for Language Agents (CoALA)](../frameworks/coala-cognitive-architecture-language-agents.md)). Each axis has its own canonical page.

| CoALA axis | Scope difference | This site's canonical page |
|---|---|---|
| Memory (four types: working, episodic, semantic, procedural) | The CoALA classifier page does the missing-slot diagnostic; the broader memory-patterns page covers the scope/temporal choices. | [CoALA Memory Taxonomy Classifier](../agent-design/coala-memory-taxonomy-classifier.md), [Agent Memory Patterns](../agent-design/agent-memory-patterns.md) |
| Action space (internal vs external) | | [CoALA Structured Action Space](../agent-design/coala-structured-action-space.md) |
| Decision-making loop (propose → evaluate → select → act) | The CoALA page frames the loop as an orchestration vocabulary, not a runtime prescription. | [CoALA Decision-Making Loop](../agent-design/coala-decision-making-loop.md) |

## Why it works

Practitioners arrive at agent-pattern material with the vocabulary their training, vendor docs, or community catalog used — and that vocabulary rarely matches the mechanism-organized vocabulary a build-out composes. The mechanism is cognitive offloading of the cross-vocabulary lookup step, the same one the sibling [OWASP LLM Top 10 (2025) Agent Security Crosswalk](../security/owasp-llm-top-10-2025-agent-crosswalk.md) documents: "Practitioners arrive at security material with the vocabulary their training, compliance reviews, and tooling use… A crosswalk closes the gap by giving readers a stable mapping from the framework names they searched to the mechanism-organised pages…" Without the crosswalk, a reader arriving with one vocabulary (Ng's "Reflection", say) cannot find the site's coverage because the site indexes patterns by mechanism (`agent-self-review-loop`, `evaluator-optimizer`) and by topology (`multi-agent/orchestrator-worker`), not by external taxonomy names. The crosswalk also captures the GEO disambiguation-hub surface and avoids duplicate `idea` issues being filed for patterns the site already covers under different names.

The shape is deliberate: leading every row with the scope-difference note and the link — not with a definition in the site's own words — protects the canonicality contract (`.claude/rules/canonicality.md`) that reference trees own each concept. The page summarizes and links; it does not restate.

## When this backfires

A crosswalk is a discovery aid, not a recommendation engine, and four failure modes make it actively misleading if treated as one.

- 1:1 mapping fallacy. Reading the tables as drop-in equivalences ("Ng's Reflection = Anthropic's Evaluator-Optimizer = Gulli's Reflection") loses the scope differences that the per-row notes flag. A 2025 paper argued "agent" is "diluted beyond utility" and proposed multidimensional characterization rather than single definitions ([arxiv:2508.05338](https://arxiv.org/abs/2508.05338), cited on-site at [Agent Terminology Disambiguation](../agent-design/agent-terminology-disambiguation.md)); the same dilution affects pattern names. Use the rows for navigation, then read each linked canonical page for the actual mechanism and trade-offs.
- Coverage flag staleness. Pattern pages get renamed, deprecated, or split over time. The "gap" / "covered" status flags are dated by `last_reviewed`; a flag that read "covered" in 2026-06 may be wrong six months later. The full-audit pipeline refreshes the date on every per-page audit, but a reader landing here years later should treat coverage as a snapshot, not a current index.
- Vocabulary churn outpaces refresh. Gulli's 21-pattern catalog is a 2025 snapshot. A future edition (or a competing 21-pattern catalog) may rename or re-split patterns. Anthropic's framework expanded from a December 2024 blog post to a 2025 eBook with case studies and skills coverage ([eBook landing](https://resources.anthropic.com/building-effective-ai-agents)). The crosswalk anchors to a specific snapshot per `last_reviewed`; treat it as that snapshot.
- Restatement creep. If a future edit adds a paragraph defining "Reflection" or "Routing" on this page in the site's own words, the crosswalk has crossed the line from navigation to a second authoritative definition — the canonicality defect [#7736](https://github.com/agentpatterns-ai/content/issues/7736) names. Keep every row as a link plus a one-line scope difference; the body lives on the linked page.

## Key Takeaways

- A vocabulary crosswalk maps external taxonomy names to canonical site pages so readers find coverage by whichever name they arrived with; it is navigation, not a competing taxonomy.
- Ng's four (Reflection, Tool Use, Planning, Multi-Agent), Anthropic's five (chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer), Gulli's 21 (Core/Advanced/Specialized), and CoALA's three axes (memory, action, decision-loop) all map cleanly onto this site's mechanism-organised pages with documented scope differences.
- All 21 of Gulli's patterns are covered on the site as of `last_reviewed`, with scope differences noted per row (e.g., Memory decomposed across memory-patterns and CoALA-classifier; RAG mapped to the canonical Retrieval-Augmented Agent Workflows reference).
- Every row leads with the canonical page link plus a one-line scope-difference note — there is no definition of any pattern in this page's own words, by design.
- For pattern *trade-offs* (token cost, latency, blast radius), pair this crosswalk with the sibling [Pattern Selection Map](selection-map.md); for cross-vendor *terminology* (workflow vs agent vs assistant), pair it with [Agent Terminology Disambiguation](../agent-design/agent-terminology-disambiguation.md).

## Related

- [Pattern Selection Map](selection-map.md) — trade-off matrix sibling to this crosswalk; same `docs/patterns/` parent, orthogonal lens (cost/latency/blast radius rather than vocabulary mapping)
- [Anthropic's Effective Agents Framework](../agent-design/anthropic-effective-agents-framework.md) — full per-pattern treatment for Anthropic's five workflows plus the augmented-LLM layer; this crosswalk links to it for the Anthropic column rather than reproducing it
- [Agent Terminology Disambiguation](../agent-design/agent-terminology-disambiguation.md) — names eight overlapping *term*-level definitions (workflow vs agent vs assistant vs RAG); orthogonal to this page's *pattern*-level mapping
- [Cognitive Architectures for Language Agents (CoALA)](../frameworks/coala-cognitive-architecture-language-agents.md) — the source page for the three-axis framing the CoALA column above maps to
- [OWASP LLM Top 10 (2025) Agent Security Crosswalk](../security/owasp-llm-top-10-2025-agent-crosswalk.md) — same crosswalk shape applied to the security taxonomy; the structural reference for this page
