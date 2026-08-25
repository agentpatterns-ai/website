---
title: "Symptom-First Bug Triage for Agent Code"
term: "Symptom-First Bug Triage"
description: "A measured corpus of 1,268 LLM agent bugs puts 57.1% in the agent core and maps two observable symptoms onto specific components, giving single-agent framework codebases a debugging order instead of a guess."
tags:
  - testing-verification
  - agent-design
  - observability
  - arxiv
  - tool-agnostic
aliases:
  - effect-to-component bug localization
  - agent component bug triage
last_reviewed: 2026-08-20
maturity: emerging
status: current
---

# Symptom-First Bug Triage for Agent Code

> A measured agent bug corpus maps a few observable failure symptoms onto the component most likely to hold the defect.

## When this applies

The corpus is 1,268 annotated bug reports from Stack Overflow, GitHub, and Hugging Face forums, covering agents built with seven frameworks (LangChain, LangChain-js, LangGraph, LlamaIndex, CrewAI, AutoGen, Semantic Kernel) plus custom implementations ([arxiv 2601.15232v3](https://arxiv.org/abs/2601.15232v3)). The distributions below are the Stack Overflow half: 951 retained posts, each labeled independently by two annotators who reached Cohen's kappa of 0.93 to 1.00 on bug type, root cause, effect, and component. The Hugging Face set has no reported distribution; it evaluates the study's automated labeler.

Use the order when all three hold:

- You are debugging one agent, not a group of coordinating agents.
- The agent is built on one of the mainstream agent frameworks the corpus indexes (LangChain, LangChain-js, LangGraph, LlamaIndex, CrewAI, AutoGen, Semantic Kernel) or a comparable model-plus-tools-plus-memory structure.
- The failure has no stack trace. Crashes are 60.6% of observed effects on Stack Overflow and already name a file and a line.

## Where the bugs sit

Each bug carries the component that originated it: agent core, planning, memory, or tools, plus Other for defects outside the agent and Unknown where the annotators could not tell. The agent core holds 57.1% of Stack Overflow bugs, followed by tools, and it carries more than half of every bug type except initialization and resource limitation bugs ([arxiv 2601.15232v3](https://arxiv.org/abs/2601.15232v3)).

Two symptoms localize further than that baseline:

| Observed effect | Share of Stack Overflow bugs | Reported component |
|---|---|---|
| Crash | 60.6% | not reported |
| Incorrect output | 16.6% | not reported |
| Empty response | 3.7% | not reported |
| Tool ignored | 2.2% | not reported |
| Stateless interaction | 1.6% | memory in 53.33% of cases |
| Indeterminate loop | 0.9% | planning in 66.7% of cases |

## The triage order

1. The agent loops and will not terminate. Read the planning component first.
2. The agent answers the current turn with no recollection of earlier ones. Read the memory layer first.
3. Anything else with no stack trace. Start in the agent core, on the base rate above.
4. An import fails, a signature moved, or version pins conflict. Treat it as a dependency problem before reading agent code. Requirement violation causes 61.88% of API bugs, and the paper's recommendation is a lock file rather than a code change ([arxiv 2601.15232v3](https://arxiv.org/abs/2601.15232v3)).

Incorrect control flow (14.4%) and requirement violation (14.1%) are the two leading root causes, so steps 3 and 4 cover most of what the symptom shortcuts miss.

## Why it works

The mechanism turns on what you can observe for free. Assigning a bug type or a root cause means reading the code; assigning an effect means reading the output you already have. The study makes that split explicit: "While identifying bug types and root causes from the output alone is difficult, determining effects is comparatively easier ... observed effects can serve as useful indicators for bug localization" ([arxiv 2601.15232v3](https://arxiv.org/abs/2601.15232v3)). The effect is therefore the only label available at the moment of failure, and the study measures where each one leads. The mapping holds where the symptom is definitionally tied to one component's job, since a run that never terminates is a control-flow property. It collapses toward the base rate for symptoms any component can produce, which is why the study reports a pointer for only these two.

## When this backfires

- Multi-agent systems. MAST classifies multi-agent failures into system design issues, inter-agent misalignment, and task verification, categories that do not decompose into one agent's components ([arxiv 2503.13657v3](https://arxiv.org/abs/2503.13657v3)). Attributing a failure to a responsible agent and step "is difficult due to long-horizon interactions and tightly coupled agent behaviors" ([arxiv 2607.07989v1](https://arxiv.org/abs/2607.07989v1)).
- Stacks outside the corpus. Posts were gathered by searching seven named frameworks, so the corpus is framework-centric rather than language-scoped: JavaScript is measured and shrinking ("14.56% of bugs reported in 2023 coming from JavaScript, dropping to 7.30% in 2025") while C# grows "from 2.63% to 5.11%". What sits outside is an agent on no named framework — a direct vendor SDK call — not a particular language.
- Thin evidence behind the two shortcuts. Indeterminate loop and stateless interaction are 0.9% and 1.6% of Stack Overflow effects, a handful of posts out of 951, with no confidence interval reported.
- No competing component distribution exists to weigh this against. The same group's 37-instance runtime benchmark looks like one, but its tools share is a curation choice, not a measurement: the authors "ensured that the component where the bug occurred spans across all four components of LLM agents, with a maximum of 19 out of 37 bugs occurring in the tools" ([arxiv 2604.17699v1](https://arxiv.org/abs/2604.17699v1)), written up in [LLM Agent Bug Fix Taxonomy](agent-bug-fix-taxonomy.md). A designed cap on a deliberately spanning benchmark says nothing about where agent bugs concentrate.
- Pinned, mature codebases. Requirement violation is reported as less common on GitHub, where finished projects fix their library versions, so step 4 shrinks once you pin.

## Key Takeaways

- Ask what the agent did wrong before asking which file is wrong; the symptom is the only label you get without reading code
- Two symptoms carry a measured pointer: a non-terminating run points at planning, an amnesiac run points at memory
- Absent a pointer, open the agent core first, but treat 57.1% as a prior about where to look rather than a diagnosis
- Version churn is a separate track from component triage, and a lock file closes more of it than debugging does
- The order is scoped to single-agent framework code, and coordination failures need [trajectory-level diagnosis](trajectory-decomposition-diagnosis.md) instead

## Related

- [LLM Agent Bug Fix Taxonomy](agent-bug-fix-taxonomy.md) — The fix-pattern half from the same research group, and the source of the competing tools-first answer
- [Agent Debugging](../observability/agent-debugging.md) — The diagnostic sequence to run once triage has named a component
- [Completion Failure Taxonomy](completion-failure-taxonomy.md) — The equivalent empirical split for code completion failures
- [Trajectory Decomposition Diagnosis](trajectory-decomposition-diagnosis.md) — Per-stage attribution for failures that no single component owns
- [Symptom-Reduction-as-Root-Cause](symptom-reduction-as-root-cause.md) — Why a symptom that stops appearing is not proof the cause is gone
