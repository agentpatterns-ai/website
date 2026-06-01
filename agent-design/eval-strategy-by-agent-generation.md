---
title: "Eval Strategy by Agent Generation: A Structure-to-Eval Locator"
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
last_reviewed: 2026-05-27
---

# Eval Strategy by Agent Generation: A Structure-to-Eval Locator

> Each architectural addition opens a failure surface the prior eval cannot see — pick eval surface from current structure, not from the generation number.

The six-generation taxonomy of agent architectures (prompt → chain → ReAct loop → workflow graph → modern loop returns → harness) is a self-location tool, not a maturity ladder. **Eval surface area must match the failure-mode surface area of the underlying architecture**, and architecture introduces new failure surfaces by adding structure ([Braintrust](https://www.braintrust.dev/blog/six-generations-ai-agents)). The generation labels are descriptive shorthand for which structural additions you have made — they do not predict business value.

Use this page to locate your *current* system's eval surface, then route to the relevant technique page. Apply it when picking eval techniques, when debating whether to add `pass@k`/`pass^k`, span scoring, or branch coverage, or when you have inherited a wrong-generation eval surface (Gen-5 loops graded as Gen-3 single trajectories, Gen-4 graphs graded only end-to-end, Gen-6 harnesses with no peripheral checks).

## The Six Structural Levels and Their Eval Surfaces

The shape is taken from Braintrust's published taxonomy ([Braintrust](https://www.braintrust.dev/blog/six-generations-ai-agents)). Column 1 names the structural addition; the generation number is the shorthand:

| Structure (Gen) | Architectural addition | Failure surface introduced | Eval surface needed |
|---|---|---|---|
| Prompt (1) | One LLM call, no tools | Answer-quality only: hallucination, missing steps, poor prioritization | Curated golden set; relaxed-reference, factuality LLM-as-judge, coverage rubric, calibration, safety scorers |
| Chain (2) | Fixed retrieval + reasoning pipeline | Retrieval misses, parse errors cascade, end-to-end scores hide where the fault is | Stage-level scorers per step (schema validation, retrieval recall/precision, context-faithfulness) + answer-level scorers from Gen 1 |
| ReAct loop (3) | LLM as controller of a tool loop | Wrong tool selection, wrong arguments, infinite loops, premature stopping, unsafe actions | Trace-level: tool-selection accuracy, argument quality, trajectory similarity vs gold, termination quality, budget compliance, forbidden-tool checks |
| Workflow graph (4) | Explicit DAG/state-machine with typed state | Out-of-distribution incidents fall off the graph; node failures localizable; contract drift between nodes | Node-level unit tests, contract evals between nodes, branch and policy coverage partitioned by path |
| Modern loop returns (5) | Strong-model loop with budgets, no graph | Non-determinism on same input, cost blowups, single-trajectory expectations become false positives | Multi-trial `pass@k`/`pass^k`, span-level scoring, pairwise judges vs baseline, budgeted-success as headline metric |
| Harness (6) | Memory, sandbox, skills, tool discovery, policies | Context engineering errors, memory poisoning, tool-registry drift, sandbox misuse, policy gaps, production-only failures | Layered: smoke tests, offline trace evals, simulations of live environment, replays, shadow runs, online scoring on production traces |

The Sentinel SRE incident-response example in the source threads the same task — "checkout-service 5xx rate above 3% for 5 minutes" — through all six structures, making each addition concrete ([Braintrust](https://www.braintrust.dev/blog/six-generations-ai-agents)).

## Why It Works

Each structural addition opens a class of failures the prior eval surface cannot see. A single prompt has one surface — the answer; you grade the answer. A chain adds intermediate state, so end-to-end scoring hides which stage failed; you must grade each stage. A tool loop adds path non-determinism — two runs can produce the same report through wildly different traces, and one of those traces may be unsafe or unaffordable; you must grade the trajectory. A graph adds branches you have to prove you exercised. A loop with strong models adds variance, so point estimates lie and `pass^k` becomes the consistency metric customers actually experience. A harness adds peripherals — memory, sandbox, registry, policy — each with its own failure modes and interactions ([Braintrust](https://www.braintrust.dev/blog/six-generations-ai-agents)).

The causal claim is **structural, not generational**: more structure means more failure surface, and the eval suite has to mirror that structure or you ship blind. The generation labels are descriptive of *which* structural additions you made; they are not normative about which you *should* make.

## How to Use the Locator

1. **Inventory the structure you have**, not the generation you want. Does this component call a tool? Does it have a fixed pipeline or model-chosen path? Is there a graph, or just a loop? Are there peripherals (memory, sandbox)?
2. **Read off the eval surface** from the row that matches your structure. Add scorers from each row whose structure you have inherited — Gen 4 systems still need Gen 2 retrieval recall on their `gather_evidence` node ([Braintrust](https://www.braintrust.dev/blog/six-generations-ai-agents)).
3. **Apply per component, not per system.** A production system rarely sits at one structural level. A parser at Gen 2, an agent loop at Gen 5, and a harness wrapping both at Gen 6 each need their own eval surface concurrently.
4. **Re-derive when you change structure**, not when calendar time passes. Adding memory to a Gen-5 loop makes it Gen-6 and pulls in harness-level smoke tests, simulations, and online scoring as new requirements ([Braintrust](https://www.braintrust.dev/blog/six-generations-ai-agents)).

## When This Backfires

- **Reading the taxonomy as a ladder.** The Braintrust post itself warns the architecture is task-driven; Sentinel works at every generation ([Braintrust](https://www.braintrust.dev/blog/six-generations-ai-agents)). Anthropic's framework is sharper: "you should consider adding complexity *only* when it demonstrably improves outcomes" — generation labels do not predict business value ([Anthropic](https://www.anthropic.com/engineering/building-effective-agents)). Teams that "upgrade" to Gen 6 because the harness reads as advanced pay a complexity tax for no benefit.
- **Self-locating the *system* on a single generation.** Real systems mix structures per component — stage scoring (Gen 2) for the parser and `pass^k` (Gen 5) for the agent loop, simultaneously. A "we are a Gen-5 shop" label hides the per-component reality and pushes uniform eval choices onto components that need different ones.
- **Workflow-graph (Gen 4) treated as yesterday's pattern.** The Braintrust narrative presents Gen 5 as the pendulum swing once "models got good enough." For teams on cheap or local models, Gen 4 remains the right destination, not a way-station; reading the taxonomy chronologically may push teams toward an under-supported Gen-5 loop or away from contract evals they still need.
- **Single-prompt (Gen 1) tasks loaded with later-generation scorers.** Classification or extraction at Gen 1 needs only answer-quality scorers. Adding Gen 2 retrieval recall metrics or Gen 3 budget compliance to a single-prompt component buys nothing and adds eval-maintenance cost.

## Key Takeaways

- The six-generation taxonomy is a structure-to-eval locator, not a maturity ladder.
- Eval surface must match the architectural failure surface — each structural addition opens failures the prior eval cannot see.
- Apply the locator per component, not per system; production systems mix structures.
- Some tasks correctly stay at a single-prompt structure forever — moving up the ladder is not the goal.
- When in doubt, default to Anthropic's framing — workflow vs agent, add complexity only when it demonstrably improves outcomes.

## Related

- [Agentic AI Architecture: From Prompt-Response to Goal-Directed Systems](agentic-ai-architecture-evolution.md) — sister structural framing; cognitive-execution separation as the boundary that makes the eval surface tractable
- [Scaffold Architecture Taxonomy for Coding Agents](scaffold-architecture-taxonomy.md) — orthogonal three-layer taxonomy for the *scaffold* dimension; combine with this page for per-axis self-location
- [Agentless vs Autonomous: When Simple Beats Complex](agentless-vs-autonomous.md) — the empirical case against climbing the structural ladder unnecessarily
- [Agent Terminology Disambiguation for AI Coding Systems](agent-terminology-disambiguation.md) — distinguishes workflow, autonomous agent, RAG pipeline, and workflow engine — paired with the eval-locator to name what you have before grading it
- [Pass@k Metrics for AI Coding Agents](../verification/pass-at-k-metrics.md) — the Gen-5 metric; `pass^k` for consistency, `pass@k` for capability
- [Incident-to-Eval Synthesis](../verification/incident-to-eval-synthesis.md) — the Gen-5/Gen-6 production-to-eval flywheel referenced by the source ([Braintrust](https://www.braintrust.dev/blog/six-generations-ai-agents))
