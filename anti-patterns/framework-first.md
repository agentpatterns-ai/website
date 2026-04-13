---
title: "Framework-First Agent Development: An AI Anti-Pattern"
description: "Starting with a high-level framework before understanding the raw LLM API adds abstraction layers that obscure failures and lock in architectural decisions."
tags:
  - agent-design
  - cost-performance
---
# Framework-First Agent Development

> Starting with a high-level framework (LangChain, CrewAI, AutoGen) before understanding the raw LLM API adds abstraction layers that obscure failures and lock in architectural decisions before requirements are clear.

## The Problem

Frameworks reduce boilerplate. They also hide the mechanics that matter when things go wrong. When an agent misbehaves in a framework-built system, the failure source is ambiguous: the prompt formatting, memory layer, tool routing, or framework error handling may each be contributing. The mechanism is hidden intermediate state — each abstraction layer transforms inputs and outputs without exposing them, so a single misbehavior requires traversing every layer to locate the source. An empirical study of agent developer practices found 42% of LangChain developers reported deeply nested abstractions hindered debugging efficiency, with some tracing a single change through seven layers of code structure ([Deng et al., 2024](https://arxiv.org/abs/2512.01939)). Debugging requires understanding the full abstraction stack, not just the code you wrote.

Per [Anthropic's effective agents post](https://www.anthropic.com/engineering/building-effective-agents), starting simple — often a single LLM call or a short chain — covers a surprising share of real use cases. The instinct to reach for a framework inverts the appropriate development order. LangChain's own analysis of [how to think about agent frameworks](https://blog.langchain.com/how-to-think-about-agent-frameworks/) acknowledges that once custom logic or unusual orchestration flows are needed, the abstraction becomes a ceiling rather than a foundation.

## What Gets Hidden

- **Prompt formatting** — frameworks modify prompts before sending them; the model receives something different from what you wrote
- **Context management** — frameworks decide what context to include; affects model behavior invisibly
- **Error handling** — framework retry and failure behavior may mask root causes

## When to Introduce a Framework

Introduce a framework when you have identified a specific capability gap the raw API cannot fill cleanly — complex stateful conversation management, standardized multi-agent handoffs, or ecosystem tool integration. "I don't want to write boilerplate" is not sufficient. Boilerplate you write is behavior you understand.

When adopting, read the framework's source code for the paths you rely on. Treating a framework as a black box is a maintenance risk.

## Signs You Have Adopted Too Early

- Debugging requires reading framework source to understand what prompt is sent
- Simple tasks require framework-specific abstractions that raw API calls would not
- The team cannot reproduce framework behavior with a direct API call

## When This Backfires

Framework-first development causes the most damage in these conditions:

- **Requirements are unknown** — locking in a framework's memory and routing model before you understand your data flow forces refactoring once real constraints emerge; the abstraction locks in the wrong decisions.
- **Team lacks framework internals knowledge** — when the first failure occurs (wrong tool selected, context truncated, unexpected retry), no one can read the framework source fast enough to diagnose it under production pressure.
- **Simple use case** — a single-turn Q&A or one-tool workflow routed through an agent executor adds latency, complexity, and failure surface for no capability gain; the framework's orchestration overhead exceeds its value.

The counterargument has merit: frameworks provide provider-agnostic interfaces and pre-built retry/error handling that save real time on complex multi-agent systems. Starting with LangGraph for a system that genuinely requires stateful graph orchestration is defensible — but that threshold is higher than most teams assume.

## Example

The following contrast shows the same tool-calling agent implemented first with LangChain, then directly with the Anthropic SDK. Both accomplish identical behaviour; the raw version makes the prompt and tool schema fully visible.

```python
# ❌ Framework-first: LangChain tool agent
from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """Return current weather for a city."""
    return f"Sunny, 22°C in {city}"

llm = ChatAnthropic(model="claude-opus-4-5")
prompt = ChatPromptTemplate.from_messages([("system", "You are a helpful assistant."), ("human", "{input}"), ("placeholder", "{agent_scratchpad}")])
agent = create_tool_calling_agent(llm, [get_weather], prompt)
executor = AgentExecutor(agent=agent, tools=[get_weather])
result = executor.invoke({"input": "What's the weather in Berlin?"})
# The actual prompt sent to Claude is hidden inside LangChain's formatting layer.
# A failure here could originate in the prompt template, the scratchpad injection,
# LangChain's tool-result formatting, or the model itself.
```

```python
# ✅ Raw API: identical behaviour, full visibility
import anthropic, json

client = anthropic.Anthropic()

tools = [{
    "name": "get_weather",
    "description": "Return current weather for a city.",
    "input_schema": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}
}]

messages = [{"role": "user", "content": "What's the weather in Berlin?"}]
response = client.messages.create(model="claude-opus-4-5", max_tokens=1024, tools=tools, messages=messages)

if response.stop_reason == "tool_use":
    tool_use = next(b for b in response.content if b.type == "tool_use")
    result = "Sunny, 22°C in Berlin"  # real impl would call an API
    messages += [{"role": "assistant", "content": response.content},
                 {"role": "user", "content": [{"type": "tool_result", "tool_use_id": tool_use.id, "content": result}]}]
    final = client.messages.create(model="claude-opus-4-5", max_tokens=1024, tools=tools, messages=messages)
    print(final.content[0].text)
```

Every step — the tool schema, the message array, the tool-result injection — is explicit. When the model misbehaves, the failure surface is a plain Python dict, not a framework abstraction stack.

## Key Takeaways

- Frameworks obscure failures by adding abstraction between your code and the model's input/output
- A single LLM call or short chain covers more use cases than expected
- Introduce frameworks only after identifying a specific gap the raw API cannot fill
- Read framework source code for paths you rely on — never treat it as a black box

## Related

- [Prompt Chaining](../context-engineering/prompt-chaining.md)
- [Separation of Knowledge and Execution](../agent-design/separation-of-knowledge-and-execution.md)
- [Comprehension Debt](comprehension-debt.md)
- [Abstraction Bloat](abstraction-bloat.md)
- [Cargo Cult Agent Setup](cargo-cult-agent-setup.md)
- [Demo-to-Production Gap](demo-to-production-gap.md)
- [Pattern Replication Risk](pattern-replication-risk.md)
