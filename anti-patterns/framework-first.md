---
title: "Framework-First Agent Development: An AI Anti-Pattern"
term: "Framework-First Agent Development"
description: "Starting with a high-level framework before understanding the raw LLM API adds abstraction layers that obscure failures and lock in architectural decisions."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
  - anti-pattern
last_reviewed: 2026-06-12
maturity: established
---

# Framework-First Agent Development

> Framework-first agent development reaches for LangChain or CrewAI before the raw LLM API, adding abstraction layers that obscure failures and lock in architecture early.

## The problem

Frameworks reduce boilerplate. They also hide the mechanics that matter when things go wrong, a cost related to [abstraction bloat](abstraction-bloat.md). When an agent misbehaves in a framework-built system, the failure source is unclear: prompt formatting, the memory layer, tool routing, or error handling may each be at fault. The cause is hidden intermediate state. Each layer transforms inputs and outputs without showing them, so one misbehavior makes you traverse every layer to find the source. An empirical study of agent developer practices across ten frameworks found that developers must navigate multiple abstraction layers, and that frameworks like LangChain take significant expertise to debug ([Wang et al., 2025](https://arxiv.org/abs/2512.01939)). To debug, you must understand the full abstraction stack, not just the code you wrote.

Per [Anthropic's effective agents post](https://www.anthropic.com/engineering/building-effective-agents), starting simple — often a single LLM call or a short chain — covers a surprising share of use cases. The instinct to reach for a framework inverts the right development order. LangChain's own analysis of [how to think about agent frameworks](https://blog.langchain.com/how-to-think-about-agent-frameworks/) admits that once you need custom logic or unusual orchestration flows, the abstraction becomes a ceiling rather than a foundation.

## What gets hidden

- Prompt formatting: frameworks change prompts before sending, so the model receives something different from what you wrote
- Context management: frameworks decide what context to include, changing behavior invisibly
- Error handling: framework retry and failure behavior can mask root causes

## When to introduce a framework

Introduce a framework once you have found a specific capability gap the raw API cannot fill cleanly. Examples include complex stateful conversation management, standardized multi-agent handoffs, or third-party tool integration. "I don't want to write boilerplate" is not enough. Boilerplate you write is behavior you understand.

## Signs you have adopted too early

- You have to read framework source to understand what prompt is sent
- Simple tasks need framework-specific abstractions that raw API calls would not
- The team cannot reproduce framework behavior with a direct API call

## When this backfires

Framework-first development causes the most damage in these conditions:

- Requirements are unknown: locking in a framework's memory and routing model before you understand your data flow forces a refactor once real constraints emerge. The abstraction locks in the wrong decisions.
- The team lacks framework internals knowledge: when the first failure happens (wrong tool selected, context truncated, unexpected retry), no one can read the framework source fast enough to diagnose it under production pressure — the [comprehension debt](comprehension-debt.md) of code you did not write.
- The use case is simple: a single-turn question-and-answer or one-tool workflow routed through an agent executor adds latency, complexity, and failure surface for no capability gain. The orchestration overhead exceeds its value.

The counterargument has merit. Frameworks provide provider-agnostic interfaces and pre-built retry and error handling that save time on complex multi-agent systems. Starting with LangGraph for a system that genuinely needs stateful graph orchestration is defensible, but that threshold is higher than most teams assume.

## Example

The contrast below shows the same tool-calling agent built first with LangChain, then directly with the Anthropic SDK. Both produce identical behavior, but the raw version makes the prompt and tool schema fully visible.

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
