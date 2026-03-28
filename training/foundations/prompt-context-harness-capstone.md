---
title: "How the Four Agent Engineering Disciplines Compound"
description: "Agent output quality is a product of prompt, context, tool, and harness engineering. A zero in any factor zeros the result regardless of other investment."
tags:
  - training
  - context-engineering
  - agent-design
  - instructions
  - cost-performance
  - tool-agnostic
---
# How the Four Disciplines Compound

> Prompt engineering, context engineering, harness engineering, and tool engineering are not independent skills -- they multiply, and weakness in any one caps the value of the other three.

Agent output quality is a product, not a sum. Each of the four disciplines -- prompt engineering, context engineering, tool engineering, and harness engineering -- acts as a multiplier. A zero in any factor zeros the result, regardless of investment in the others. The implication: diagnosing which factor is the bottleneck matters more than improving any single factor in isolation.

---

## The Multiplication Model

Agent output quality follows a multiplication relationship:

```
Effective output = Prompt quality x Context design x Tool interface x Harness feedback
```

This is not metaphor. Each factor gates the next:

- A precise prompt in an empty context window produces hallucinated output. The model has nothing to ground against. ([Context engineering](../../context-engineering/context-engineering.md) addresses this: "the context window is the agent's entire world.")
- A well-structured context with vague instructions produces inconsistent output. The model has material but no constraint on how to use it. ([System prompt altitude](../../instructions/system-prompt-altitude.md) addresses this: prompts that are too vague give no real constraint.)
- A good prompt and rich context routed through a poorly designed tool interface produces malformed actions. The model knows what to do but cannot express it through the tool's parameters. ([Tool engineering](../../tool-engineering/tool-engineering.md) addresses this: "agent quality is bounded by tool quality.")
- All three working well without a harness produces output that requires manual verification of every result. The agent cannot self-correct. ([Harness engineering](../../agent-design/harness-engineering.md) addresses this: environment design determines whether agents succeed by default.)

The multiplication model explains why teams that invest in only one discipline hit ceilings. Doubling prompt quality when context design is poor yields marginal improvement. Investing in harness when tool interfaces are broken gives the agent better feedback on outputs it cannot produce correctly.

---

## Why Each Discipline Needs the Others

### Prompts without context drift

A well-crafted instruction in a system prompt occupies a fixed position. As the session runs, [attention decays](../../context-engineering/context-window-dumb-zone.md) -- tokens in the middle of a long context receive less weight than recent tool outputs. An instruction that worked at turn 3 may be functionally invisible by turn 30.

Context engineering compensates: [progressive disclosure](../../agent-design/progressive-disclosure-agents.md) keeps the active context lean, [compaction](../../context-engineering/context-compression-strategies.md) frees budget, and restating constraints in recent messages exploits the recency bias. Without these mechanisms, prompt quality has a half-life measured in conversation turns.

### Context without harness requires manual verification

A well-designed context window -- the right files loaded, the right instructions in position, the right tool outputs structured cleanly -- produces a high probability of correct output. Probability is not certainty.

[Harness engineering](../../agent-design/harness-engineering.md) converts probability into mechanical guarantee. Type checkers, linters, and test suites provide [backpressure](../../agent-design/agent-backpressure.md): the agent iterates until checks pass. Without a harness, every output requires a human to verify what the type system could have verified automatically. This is the [verification bottleneck inversion](../../human/rigor-relocation.md) -- agents produce code faster than teams can review it, and only mechanical enforcement scales.

### Tools determine the action space

The best instructions and the richest context are inert if the agent cannot act on them. Tool interfaces define what the agent can do, and [tool engineering](../../tool-engineering/tool-engineering.md) determines whether it can do those things reliably.

A tool with ambiguous parameter names causes selection errors. A tool that returns verbose, unstructured output [consumes context budget](../../context-engineering/context-engineering.md) that could carry reasoning. A tool without error remediation messages leaves the agent unable to recover from failures. These are not prompt problems or context problems -- they are tool interface problems, and no amount of instruction tuning compensates for them.

### Harness without prompts produces correct but wrong output

A comprehensive test suite and strict type system ensure the agent's code compiles and passes checks. They do not ensure the code solves the right problem. [Prompt altitude](../../instructions/system-prompt-altitude.md) provides the reasoning heuristics -- how to approach authentication code, when to flag missing requirements, which patterns to prefer. Harness catches mechanical errors; prompts shape intent.

---

## The Comparison Table

| | Prompt Engineering | Context Engineering | Tool Engineering | Harness Engineering |
|-|-------------------|-------------------|-----------------|-------------------|
| **Scope** | The user message and system instructions | Everything in the context window: instructions, tool outputs, conversation history, file contents | The interfaces agents use to act: tool definitions, parameter schemas, output formats | The development environment: type system, test suite, linters, CI pipeline |
| **When** | At the moment you ask or at session start | Before the session (instruction files, skills), during (tool results, steering), and across sessions (memory) | At design time -- before any agent session runs | Before any session -- baked into the codebase and toolchain |
| **Optimises for** | A good answer to this question | Consistent quality across all questions in this codebase | Reliable agent actions -- correct tool selection, correct parameters, parseable output | Agent self-correction -- the agent iterates until checks pass without human intervention |
| **Who does it** | The person asking | The team, via committed configuration files | The team, via tool definitions and MCP server design | The team, via tooling investments (types, tests, linters, hooks) |
| **Failure mode** | Bad answer to one question | Inconsistent results across sessions; [context pollution](../../anti-patterns/session-partitioning.md) dilutes attention | Wrong tool selected, malformed parameters, [verbose output consuming budget](../../tool-engineering/semantic-tool-output.md) | Agent cannot verify its own work -- every output requires manual review |
| **Durability** | Per-message | Per-repo, evolves with configuration | Per-tool, versioned with the tool definition | Permanent -- compounds across all agents, all sessions, all team members |

This table extends the comparison from the [Copilot context and workflows module](../copilot/context-and-workflows.md). The addition of tool engineering as a fourth column reflects a failure mode that the three-column model misses: agents that understand the task and have the right context but cannot execute because the tool interface is wrong.

---

## Diagnosing Failures by Discipline

When agent output is wrong, the fix depends on which factor is the bottleneck. Misdiagnosis wastes effort -- rewriting prompts when the problem is a missing test suite, or adding context when the tool interface is ambiguous.

| Symptom | Likely discipline | Diagnostic question |
|---------|------------------|-------------------|
| Agent ignores a specific instruction | Context | Is the instruction in a [high-attention position](../../context-engineering/attention-sinks.md)? Has the session accumulated enough history to push it into the [low-attention zone](../../context-engineering/context-window-dumb-zone.md)? |
| Agent follows instructions but produces wrong approach | Prompt | Is the instruction at the [right altitude](../../instructions/system-prompt-altitude.md) -- a reasoning heuristic, not a brittle case enumeration? |
| Agent understands the task but produces malformed actions | Tool | Does the tool interface have [clear parameter names, examples, and error messages](../../tool-engineering/tool-engineering.md)? |
| Agent produces plausible code that fails in unexpected ways | Harness | Does the codebase have [type coverage, test coverage, and linter rules](../../agent-design/harness-engineering.md) that would catch this class of error? |
| Agent output quality degrades over a long session | Context | Is the session suffering from [context rot](../../context-engineering/context-compression-strategies.md)? Start a fresh session with precisely loaded files. |
| Agent selects the wrong tool for the task | Tool | Are tool descriptions [distinct enough](../../tool-engineering/tool-engineering.md) for the model to differentiate? Do similar tools have overlapping docstrings? |
| Agent produces correct code that solves the wrong problem | Prompt | Did the [delegation contract](../copilot/context-and-workflows.md) specify success conditions and constraints, or only the goal? |

The diagnostic sequence: check harness first (is there mechanical feedback?), then context (is the right information loaded?), then tools (can the agent act?), then prompts (are the instructions well-formed?). This ordering reflects investment durability -- harness fixes persist permanently, prompt fixes last one message.

---

## The Investment Progression

Most teams follow a predictable sequence:

1. **Prompts first.** Individual developers write better messages. Results improve for that developer, that session. Nothing compounds.
2. **Context second.** Teams commit instruction files, configure progressive disclosure, manage context budgets. Results improve per-repo. Knowledge survives across sessions.
3. **Tools third.** Teams invest in tool descriptions, [MCP server design](../../tool-engineering/mcp-server-design.md), structured output, and [poka-yoke parameter design](../../tool-engineering/poka-yoke-agent-tools.md). Agent actions become reliable. The gap between "knows what to do" and "can do it" closes.
4. **Harness last.** Teams build [mechanical enforcement](../../agent-design/harness-engineering.md) -- custom linters, structural tests, CI gates. Agent output becomes self-verifying. The [verification bottleneck](../../human/rigor-relocation.md) breaks.

The progression is natural but suboptimal. Harness engineering has the highest durability -- a linter rule catches a dependency violation in every session, for every agent, for every team member. The earlier you invest in harness, the more the other three disciplines compound against a reliable verification base.

The [compound engineering workflow](../../workflows/compound-engineering.md) formalises this: the Compound step encodes learnings as repository artifacts (instruction files, linter rules, test cases) that persist across sessions. Each cycle strengthens the harness, which makes the next cycle's prompts and context more effective.

---

## Decision Framework: Where to Invest Next

| If you observe... | Invest in... | Because... |
|-------------------|-------------|-----------|
| Good results for one developer, inconsistent across the team | Context engineering -- shared instruction files, progressive disclosure | Per-developer prompt skill does not scale; committed configuration does |
| Consistent instructions but agents still produce wrong code | Harness engineering -- type coverage, test coverage, linter rules | The agent has no way to verify its own output |
| Agents understand tasks but take wrong actions | Tool engineering -- better descriptions, parameter design, error messages | The tool interface is the bottleneck, not the agent's understanding |
| All infrastructure in place but edge cases slip through | Prompt engineering -- [altitude calibration](../../instructions/system-prompt-altitude.md), domain-specific heuristics | Mechanical checks catch known classes; prompts shape reasoning about novel cases |
| Long sessions degrade despite good setup | Context engineering -- [session hygiene](../../context-engineering/context-compression-strategies.md), compaction, fresh sessions for complex tasks | Context rot is a context management problem, not a prompt or harness problem |

---

## Exercise: Classify and Fix

Take the last three agent failures your team encountered. For each:

1. Identify the primary discipline: prompt, context, tool, or harness.
2. Identify whether a secondary discipline contributed (e.g., a prompt problem amplified by poor context positioning).
3. Propose a fix in the identified discipline. Assess its durability: does it fix one session (prompt), one repo (context/tool), or all future sessions (harness)?
4. If the fix is a prompt change, ask: could this be a linter rule instead? If yes, the harness fix is more durable.

The pattern that emerges from this exercise is consistent: most teams attribute failures to prompts, but most durable fixes live in harness and context.

---

## Key Takeaways

- Agent output quality is a product of four factors -- a zero in any one zeros the result, regardless of investment in the others.
- Diagnose failures by discipline before fixing them. The symptom determines the factor; the factor determines the fix.
- Harness engineering has the highest durability. A linter rule persists across all sessions, agents, and team members. A prompt fix lasts one message.
- The natural progression (prompts, context, tools, harness) is suboptimal. Investing in harness earlier makes every subsequent prompt and context investment more effective.
- Context engineering makes prompts land -- position, recency, and budget determine whether instructions receive attention.
- Tool engineering determines the action space -- agents cannot do what the tool interface does not support.
- The [compound engineering workflow](../../workflows/compound-engineering.md) closes the loop: each cycle's learnings become the next cycle's harness, context, and tool improvements.

## Related

**Preceding modules**

- [Prompt Engineering](prompt-engineering.md) -- system prompt altitude, polarity, compliance ceiling
- [Context Engineering](context-engineering.md) -- context window mechanics, attention, compression
- [Harness Engineering](harness-engineering.md) -- repo legibility, mechanical enforcement, backpressure
- [Tool Engineering](tool-engineering.md) -- tool descriptions, schema design, MCP, skill authoring

**Complementary module**

- [Eval Engineering](eval-engineering.md) -- measuring agent quality across sessions and over time, above the runtime harness layer

**Source pages**

- [Context Engineering](../../context-engineering/context-engineering.md) -- the foundational discipline
- [Harness Engineering](../../agent-design/harness-engineering.md) -- environment design for agent reliability
- [Tool Engineering](../../tool-engineering/tool-engineering.md) -- tool interface design principles
- [System Prompt Altitude](../../instructions/system-prompt-altitude.md) -- calibrating instruction specificity
- [Rigor Relocation](../../human/rigor-relocation.md) -- where engineering discipline moves when agents write code
- [Compound Engineering](../../workflows/compound-engineering.md) -- the learning loop that connects all four disciplines
- [Copilot: Context Engineering & Agent Workflows](../copilot/context-and-workflows.md) -- the three-column comparison table this module extends
