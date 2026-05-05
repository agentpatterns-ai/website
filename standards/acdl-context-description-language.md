---
title: "ACDL: A Language for Describing Agentic LLM Contexts"
description: "ACDL is a notation for specifying how an LLM agent's context is assembled and evolves across interaction steps — roles, time indices, namespaces, and control flow as a precise, renderable spec."
tags:
  - standards
  - context-engineering
  - tool-agnostic
aliases:
  - Agentic Context Description Language
  - context description language
---

# ACDL: A Language for Describing Agentic LLM Contexts

> ACDL is a notation for specifying how an LLM agent's context is assembled and evolves across interaction steps — published with a parser, web renderer, VS Code extension, and Claude Code skill at acdlang.org.

## What ACDL Is

The Agentic Context Description Language (ACDL) is a formal language for specifying the structure and dynamics of LLM input contexts. It was introduced by Peleg Pelc, Kaminka, and Goldberg in [arxiv:2605.01920](https://arxiv.org/abs/2605.01920) (May 2026) under a CC-BY 4.0 licence, with tooling at [acdlang.org](http://www.acdlang.org).

The motivating gap, in the authors' words: context construction "is typically conveyed through informal prose, ad hoc diagrams, or direct inspection of code, none of which precisely capture how a prompt evolves across interaction steps or how two context representation strategies differ" ([abstract](https://arxiv.org/abs/2605.01920)).

The paper's empirical lever: "even small variations in how a basic ReAct agent's context is assembled lead to measurable differences in agent performance" ([§1](https://arxiv.org/html/2605.01920)). If macro-structure moves benchmark numbers, it deserves a notation.

## Core Constructs

ACDL captures a prompt's architecture independent of its content. The constructs documented in [the paper](https://arxiv.org/html/2605.01920):

| Construct | Purpose |
|-----------|---------|
| Role messages | Sequences labelled `S` (System), `U` (User), `A` (Assistant), `T` (Tool) |
| Time indices | `@T` for the current step, `@t` for iteration over past steps, `@T.I` for substeps |
| Namespaces | `env` (environment), `sys` (system state), `resp` (LLM responses) |
| Control flow | `ForEach`, `If`/`ElseIf`/`Else`, `Switch`/`Case` |
| Functions | Computed content — retrieval, summarisation, compaction |
| Templates | `ALL_CAPS` placeholders for variable content |
| Fragments | Reusable string or role blocks |
| Mark blocks | Numbered annotations referenced from surrounding prose |

Specifications render as block diagrams: roles become labelled columns, the vertical axis is time, loops collapse and expand, conditional branches fork. Diagrams can be hand-drawn on a whiteboard or written in formal syntax and rendered to PDF/PNG.

The paper documents several real systems in ACDL: ReAct variants, the MINT benchmark agent, OpenCode, OpenClaw, the Gemini agent that played Pokemon Blue, and DeepSeek-V4 ([§4–5](https://arxiv.org/html/2605.01920)). Each shows how two superficially similar systems differ at the architectural level — the kind of difference informal prose hides.

## Tooling

The [acdlang.org](http://www.acdlang.org) site ships:

- A web editor and visualiser that renders `.acdl` to PDF or PNG
- A VS Code extension with syntax highlighting and live rendering
- A Claude Code skill for authoring inside an agent session
- Language documentation and example specifications

The paper notes the resources are open and welcome contributions ([§6](https://arxiv.org/html/2605.01920)).

## When to Use It

ACDL earns its keep when the audience for an agent's architecture is broader than the team that wrote it:

- **Cross-team handoffs** — passing an agent system to a team or vendor that cannot read the original code
- **Papers and RFCs** — published artifacts that must stay intelligible without the implementation
- **Comparing variants** — ablations across ReAct, ReWOO, or Plan-and-Execute that need to show what actually differs
- **Prompt-restructure reviews** — diffing one architecture against another when the source diff is dominated by content changes

## When This Backfires

The notation overhead has to be earned. ACDL backfires in three conditions:

- **Solo or small-team projects**: when the same person reads and writes the prompt, the spec is parallel work nobody consults. An `.acdl` file alongside the implementation becomes a liability the moment it drifts.
- **Rapid iteration tempo**: any restructure invalidates the spec. Teams iterating multiple times a day let `.acdl` files rot, recreating the informal-prose problem the language is meant to solve. The same drift problem affects any specification that lives outside the implementation.
- **Content-dominated agents**: when most context volume is dynamic tool output — long file contents, retrieval results, search dumps — ACDL's macro structure is a thin layer over content the language deliberately abstracts away. The hard engineering happens inside `resp` values ACDL does not describe.

The paper flags two structural limitations the language does not yet handle ([§7](https://arxiv.org/html/2605.01920)):

- Agents whose state mutates *within* a single context construction; ACDL assumes state is immutable during construction.
- Multi-agent systems with desynchronised clocks against shared mutable state; the current workaround — explicit clock synchronisation — the authors call "inelegant."

The authors commit to addressing both in future versions.

## Example

A minimal ACDL block for a ReAct loop, paraphrased from the paper's [Figure 1 walkthrough](https://arxiv.org/html/2605.01920):

```
S: SYSTEM_INSTRUCTIONS
U: TASK_DESCRIPTION

ForEach step in @t:
  A: resp[step].thought
  A: resp[step].action
  T: env.tool_output(resp[step].action)

A: resp[@T].final_answer
```

The architecture is explicit: a system message, a user task, a loop over past steps where each iteration has a thought, an action, and a tool result, and a final answer at the current step. A second ReAct variant that interleaves thoughts after tool outputs becomes a different ACDL block — the diff is the order of role messages inside the `ForEach`, not a paragraph of prose.

## Key Takeaways

- ACDL is a notation for the architecture of an agent prompt, not its content
- Its constructs (roles, time indices, namespaces, control flow) capture the structural choices that move benchmark numbers
- Tooling is shipped today: web editor, VS Code extension, Claude Code skill, examples
- The value is conditional — cross-team and cross-paper communication earn it back; solo high-iteration work usually does not
- Two structural limitations remain: in-construction mutation and multi-agent clock desynchronisation

## Related

- [Context Engineering: The Discipline of Designing Agent Context](../context-engineering/context-engineering.md)
- [Phase-Specific Context Assembly](../context-engineering/phase-specific-context-assembly.md)
- [Dynamic System Prompt Composition](../context-engineering/dynamic-system-prompt-composition.md)
- [Layered Context Architecture](../context-engineering/layered-context-architecture.md)
- [Turn-Level Context Decisions](../context-engineering/turn-level-context-decisions.md)
- [Agent Definition Formats: How Tools Define Agent Behavior](agent-definition-formats.md)
- [AGENTS.md: A README for AI Coding Agents](agents-md.md)
