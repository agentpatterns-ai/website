---
title: "Eval Strategy by Agent Generation: A Structure-to-Eval Locator"
term: "Eval Strategy by Agent Generation"
description: "Six structural levels of agent architecture each open an eval surface the prior level cannot see — pick eval scorers from current structure, not generation."
tags:
  - agent-design
  - evals
  - testing-verification
  - tool-agnostic
aliases:
  - six generations of AI agents
  - per-generation eval strategy
  - agent generation taxonomy
last_reviewed: 2026-06-12
maturity: adopted
---

# Eval Strategy by Agent Generation: A Structure-to-Eval Locator

> Each architectural addition opens a failure surface the prior eval cannot see — pick eval surface from current structure, not from the generation number.

The six-generation taxonomy of agent architectures (prompt → chain → ReAct loop → workflow graph → modern loop returns → harness) is a self-location tool, not a maturity ladder. Your eval surface must match the failure-mode surface of the underlying architecture, and each structural addition opens a new failure surface ([Braintrust](https://www.braintrust.dev/blog/six-generations-ai-agents)). The generation labels are shorthand for which structural additions you have made — they do not predict business value.

Use this page to locate your current system's eval surface, then route to the relevant technique page. Apply it when picking eval techniques, when debating whether to add `pass@k`/`pass^k`, span scoring, or branch coverage, or when you have inherited a wrong-generation eval surface (Gen-5 loops graded as Gen-3 single trajectories, Gen-4 graphs graded only end-to-end, Gen-6 harnesses with no peripheral checks).

## The six structural levels and their eval surfaces

The shape follows Braintrust's published taxonomy ([Braintrust](https://www.braintrust.dev/blog/six-generations-ai-agents)); column 1 names the structural addition and the generation number is shorthand:

| Structure (Gen) | Architectural addition | Failure surface introduced | Eval surface needed |
|---|---|---|---|
| Prompt (1) | One LLM call, no tools | Answer-quality only: hallucination, missing steps, poor prioritization | Curated golden set; relaxed-reference, factuality LLM-as-judge, coverage rubric, calibration, safety scorers |
| Chain (2) | Fixed retrieval + reasoning pipeline | Retrieval misses, parse errors cascade, end-to-end scores hide where the fault is | Stage-level scorers per step (schema validation, retrieval recall/precision, context-faithfulness) + answer-level scorers from Gen 1 |
| ReAct loop (3) | LLM as controller of a tool loop | Wrong tool selection, wrong arguments, infinite loops, premature stopping, unsafe actions | Trace-level: tool-selection accuracy, argument quality, trajectory similarity vs gold, termination quality, budget compliance, forbidden-tool checks |
| Workflow graph (4) | Explicit DAG/state-machine with typed state | Out-of-distribution incidents fall off the graph; node failures localizable; contract drift between nodes | Node-level unit tests, contract evals between nodes, branch and policy coverage partitioned by path |
| Modern loop returns (5) | Strong-model loop with budgets, no graph | Non-determinism on same input, cost blowups, single-trajectory expectations become false positives | Multi-trial `pass@k`/`pass^k`, span-level scoring, pairwise judges vs baseline, budgeted-success as headline metric |
| Harness (6) | Memory, sandbox, skills, tool discovery, policies | Context engineering errors, memory poisoning, tool-registry drift, sandbox misuse, policy gaps, production-only failures | Layered: smoke tests, offline trace evals, simulations of live environment, replays, shadow runs, online scoring on production traces |

The Sentinel SRE incident-response example in the source threads the same task — "checkout-service 5xx rate above 3% for 5 minutes" — through all six structures, making each addition concrete ([Braintrust](https://www.braintrust.dev/blog/six-generations-ai-agents)).

## Why it works

Each structural addition opens a class of failures the prior eval surface cannot see, so the eval surface grows with the structure. Intermediate state means end-to-end scoring hides which stage failed. A model-chosen tool path adds non-determinism, so two runs can reach the same answer through traces that differ in safety and cost. A graph adds branches you must prove you exercised. A strong-model loop adds variance that makes point estimates lie. A harness adds peripherals — memory, sandbox, registry, policy — each with its own failure modes ([Braintrust](https://www.braintrust.dev/blog/six-generations-ai-agents)).

The causal claim is structural, not generational: more structure means more failure surface, and the eval suite has to mirror that structure or you ship blind. The generation labels describe which additions you made. They do not say which additions you should make.

## How to use the locator

1. Inventory the structure you have, not the generation you want — tool calls, fixed pipeline versus model-chosen path, graph versus loop, peripherals like memory or sandbox.
2. Read off the eval surface from each row whose structure you have inherited, not just the top one — a Gen-4 system still needs Gen-2 retrieval recall on its `gather_evidence` node ([Braintrust](https://www.braintrust.dev/blog/six-generations-ai-agents)).
3. Apply the locator per component, not per system. A parser at Gen 2, an agent loop at Gen 5, and a harness wrapping both at Gen 6 each need their own eval surface at the same time.
4. Re-derive when you change structure, not when calendar time passes. Adding memory to a Gen-5 loop makes it Gen-6 and pulls in harness-level smoke tests, simulations, and online scoring.

## When this backfires

- Reading the taxonomy as a ladder. The Braintrust post warns the architecture is task-driven — Sentinel works at every generation ([Braintrust](https://www.braintrust.dev/blog/six-generations-ai-agents)) — and Anthropic is sharper: add complexity "only when it demonstrably improves outcomes" ([Anthropic](https://www.anthropic.com/engineering/building-effective-agents)). Teams that "upgrade" to Gen 6 because the harness reads as advanced pay a complexity tax for no benefit.
- Self-locating the system on a single generation. A "we are a Gen-5 shop" label hides the per-component reality and forces uniform eval choices onto components that need different ones — stage scoring for the parser, `pass^k` for the agent loop.
- Treating the workflow graph (Gen 4) as yesterday's pattern. The narrative presents Gen 5 as the swing once "models got good enough," but for teams on cheap or local models Gen 4 remains the destination. Reading the taxonomy chronologically pushes them toward an under-supported loop, or away from contract evals they still need.
- Loading single-prompt (Gen 1) tasks with later-generation scorers. Classification or extraction needs only answer-quality scorers. Adding Gen-2 retrieval recall or Gen-3 budget compliance buys nothing and adds maintenance cost.

## Key Takeaways

- The six-generation taxonomy is a structure-to-eval locator, not a maturity ladder.
- Eval surface must match the architectural failure surface — each structural addition opens failures the prior eval cannot see.
- Apply the locator per component, not per system; production systems mix structures.
- Some tasks correctly stay at a single-prompt structure forever — moving up the ladder is not the goal, as [agentless vs autonomous](agentless-vs-autonomous.md) argues empirically.
- When in doubt, default to Anthropic's framing — workflow vs agent, add complexity only when it demonstrably improves outcomes.

## Related

- [Agentic AI Architecture: From Prompt-Response to Goal-Directed Systems](agentic-ai-architecture-evolution.md) — sister structural framing; cognitive-execution separation as the boundary that makes the eval surface tractable
- [Scaffold Architecture Taxonomy for Coding Agents](harness-design-dimensions.md) — orthogonal three-layer taxonomy for the *scaffold* dimension; combine with this page for per-axis self-location
- [Agentless vs Autonomous: When Simple Beats Complex](agentless-vs-autonomous.md) — the empirical case against climbing the structural ladder unnecessarily
- [Agent Terminology Disambiguation for AI Coding Systems](agent-terminology-disambiguation.md) — distinguishes workflow, autonomous agent, RAG pipeline, and workflow engine — paired with the eval-locator to name what you have before grading it
- [Pass@k Metrics for AI Coding Agents](../verification/pass-at-k-metrics.md) — the Gen-5 metric; `pass^k` for consistency, `pass@k` for capability
- [Incident-to-Eval Synthesis](../verification/incident-to-eval-synthesis.md) — the Gen-5/Gen-6 production-to-eval flywheel referenced by the source ([Braintrust](https://www.braintrust.dev/blog/six-generations-ai-agents))
