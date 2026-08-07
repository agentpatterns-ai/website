---
title: "Agent as Tool vs Handoff: Who Keeps the Conversation"
term: "Agent as Tool"
description: "Registering a specialist agent as a callable tool keeps the parent in control with a clean context window, while a handoff transfers the conversation."
tags:
  - agent-design
  - multi-agent
  - tool-agnostic
aliases:
  - Agent-as-a-Tool
  - AgentTool
  - agents as tools
  - delegate and return
last_reviewed: 2026-08-06
maturity: adopted
---

# Agent as Tool vs Handoff: Who Keeps the Conversation

> An agent registered as a tool runs in its own context and returns a result; a handoff gives the conversation away.

An agent-as-tool is a specialist agent registered on a parent agent as a callable tool. The parent invokes it with an input, the specialist runs to completion in its own context, and its answer comes back as a tool result. The parent keeps the conversation and decides what happens next. A handoff transfers control instead: the specialist becomes the active agent and answers the user itself ([OpenAI Agents SDK: Agent orchestration](https://openai.github.io/openai-agents-python/multi_agent/)).

Three SDKs ship the choice explicitly. OpenAI pairs `Agent.as_tool()` against handoffs. Google's ADK pairs `AgentTool` against sub-agent transfer, where "Agent A retains control and continues to handle future user input" in the first case and "is effectively out of the loop" in the second ([ADK: Agent-as-a-Tool](https://adk.dev/tools-custom/function-tools/#agent-tool)). Claude Code ships only the tool form, and its transcript shows the delegation as a tool-call row ([Claude Code: subagents](https://code.claude.com/docs/en/sub-agents)). A Towards Data Science write-up covers the same agents-as-tools composition outside the SDK documentation ([Using Agents as Tools](https://towardsdatascience.com/using-agents-as-tools/)).

## Conditions that make the tool form the right call

The pattern earns its cost under four conditions.

- The parent still has work to do with the answer. Use the tool form "when a specialist should help with a bounded subtask but should not take over the user-facing conversation" ([OpenAI Agents SDK](https://openai.github.io/openai-agents-python/multi_agent/)).
- The brief can be written completely without the parent's history. Each specialist needs "an objective, an output format, guidance on the tools and sources to use, and clear task boundaries" ([Anthropic: multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)).
- The specialist's intermediate output is noise, such as search results or file contents nobody references again ([Claude Code: subagents](https://code.claude.com/docs/en/sub-agents)).
- The work is read-heavy. Reads parallelize better than writes, because conflicting write decisions produce outputs that will not merge ([LangChain: how and when to build multi-agent systems](https://www.langchain.com/blog/how-and-when-to-build-multi-agent-systems)).

## What each form does to context

| | Agent as tool | Handoff |
|---|---|---|
| Who answers the user | The parent | The specialist |
| Child's starting context | Fresh; parent state is not inherited by default | The entire previous conversation |
| What crosses back | One result the parent acts on | Nothing; the specialist owns the turn |

The context row carries the difference. In the OpenAI SDK, "the parent run's conversation state is not inherited automatically," and sharing history means passing the same `session` to both runs ([Tools guide](https://openai.github.io/openai-agents-python/tools/#agents-as-tools)). On the handoff side, "the new agent takes over the conversation, and gets to see the entire previous conversation history" ([Handoffs guide](https://openai.github.io/openai-agents-python/handoffs/)).

## Why it works

The mechanism is a context-window boundary that comes as a default of the call. Claude Code states it plainly: "Each subagent starts with a fresh, isolated context window. It doesn't see your conversation history, the skills you've already invoked, or the files Claude has already read" ([Claude Code: subagents](https://code.claude.com/docs/en/sub-agents)). The specialist spends its dead ends, retries, and raw tool output inside a window the parent never pays for, and only the final result crosses back. Anthropic describes the same effect as compression, with subagents "operating in parallel with their own context windows" ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)). Cognition reaches it from the opposite direction while arguing against multi-agent designs generally: "all the subagent's investigative work does not need to remain in the history of the main agent, allowing for longer traces before running out of context" ([Cognition: Don't Build Multi-Agents](https://cognition.com/blog/dont-build-multi-agents)). Control follows from the same call shape, since a tool call returns to its caller.

## When this backfires

- Parallel write work with cross-cutting decisions. Two tool-agents editing one feature act on "conflicting assumptions not prescribed upfront," and the parent inherits an unmergeable pair ([Cognition](https://cognition.com/blog/dont-build-multi-agents)).
- Thin tool descriptions and thin briefs. The parent selects on the description alone and the child sees only the brief, so "without detailed task descriptions, agents duplicate work, leave gaps, or fail to find necessary information" ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)).
- A return value the parent cannot act on. When the useful output sits in the specialist's trace rather than its final message, the parent stalls or redoes the work. The `custom_output_extractor` argument exists for exactly this ([OpenAI Tools guide](https://openai.github.io/openai-agents-python/tools/#agents-as-tools)).
- Chatty, low-value subtasks. Every call pays a cold start, which is why Claude Code names latency as a reason to stay in the main conversation ([Claude Code](https://code.claude.com/docs/en/sub-agents)), and Anthropic measures multi-agent systems at "about 15× more tokens than chats" ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)). [The orchestrator's attention budget](orchestrator-attention-budget.md) works that cost through in full.
- Too many registered specialists. Each occupies a slot in the parent's tool list, and selection quality is sensitive to list depth: an adaptive policy held BFCL coverage at 90.3% against a 50-tool baseline's 90.8% while presenting about 7 tools ([Repantis et al., arXiv:2605.24660v2](https://arxiv.org/abs/2605.24660v2)).
- Domains where every agent needs the same context. "Most coding tasks involve fewer truly parallelizable tasks than research" ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)).

## Example

The OpenAI SDK turns a finished agent into a tool with one call, and the orchestrator then treats it like any other tool ([Tools guide](https://openai.github.io/openai-agents-python/tools/#agents-as-tools)):

```python
orchestrator_agent = Agent(
    name="orchestrator_agent",
    instructions=(
        "You are a translation agent. You use the tools given to you to translate. "
        "If asked for multiple translations, you call the relevant tools."
    ),
    tools=[
        spanish_agent.as_tool(
            tool_name="translate_to_spanish",
            tool_description="Translate the user's message to Spanish",
        ),
    ],
)
```

The orchestrator reads the returned translation and writes the reply. Wired as a handoff, the Spanish agent would answer the user directly and the orchestrator would drop out of the turn.

## Key Takeaways

- Pick by asking whether the specialist's output is the user-facing answer. If the parent still has to judge, combine, or narrate it, register the specialist as a tool.
- The context boundary is a documented default of the nested call, so treat any history the child needs as something you must pass deliberately.
- Write the tool description and the brief as the two interfaces they are; the parent selects on one and the child works from the other.
- Cap the blast radius with the affordances the SDK already gives you: `max_turns` for runaway nested runs, `custom_output_extractor` for results the parent cannot use, and a short tool list for reliable selection.

## Related

- [Forked vs Fresh Subagents: When to Inherit the Parent Conversation](../multi-agent/forked-vs-fresh-subagents.md) — the context-inheritance axis this page holds fixed
- [Agent Handoff Protocols: Passing Work Between Agents](../multi-agent/agent-handoff-protocols.md) — the contract to write once control does transfer
- [Agent Composition Patterns for Multi-Agent Workflows](agent-composition-patterns.md) — the structural shapes these delegations compose into
- [The Delegation Decision: When to Use an Agent vs Do It Yourself](delegation-decision.md) — whether to delegate at all, before choosing a form
- [Typed Schemas at Agent Boundaries for Multi-Agent Systems](../multi-agent/typed-schemas-at-agent-boundaries.md) — typing the input and result the tool form passes
