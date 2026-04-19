---
title: "The Advisor Strategy: Frontier Model as Strategic Advisor"
description: "Pair a cost-effective executor model with a frontier advisor that provides strategic guidance on hard decisions — within a single API call, no orchestration required."
tags:
  - agent-design
  - cost-performance
  - claude
aliases:
  - advisor strategy
  - frontier model advisor
  - opus advisor pattern
---

# The Advisor Strategy: Frontier Model as Strategic Advisor

> Pair a cost-effective executor model with a frontier advisor that provides strategic guidance on hard decisions — within a single API call, no orchestration required.

## The Pattern

Most agent turns are mechanical — reading files, running commands, writing code. A few require strategic reasoning: choosing an architecture, recovering from a dead end, verifying completeness. Running a frontier model on every turn wastes compute; running only a cheap model misses the critical decisions.

The advisor strategy separates these concerns at the API level. A cost-effective executor (Sonnet or Haiku) handles end-to-end tool use; when facing a hard decision, it consults a frontier advisor (Opus) that reads the full transcript and returns strategic guidance. Anthropic's [`advisor_20260301` tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool) implements this server-side within a single `/v1/messages` request — no decomposition logic, no extra round-trips.

```mermaid
sequenceDiagram
    participant U as User
    participant E as Executor (Sonnet/Haiku)
    participant A as Advisor (Opus)

    U->>E: Task
    E->>E: Tool calls (read, search, write)
    E->>A: Consult on hard decision
    A-->>E: Strategic guidance (400-700 tokens)
    E->>E: Continue execution with advice
    E->>U: Result
```

## How It Works

The executor decides when to call the advisor, like any other tool. The server runs a separate inference pass on the advisor with the executor's full transcript (system prompt, tool definitions, prior turns). The advisor returns strategic guidance as text — its thinking blocks are dropped, and it never calls tools or produces user-facing output. The executor resumes, informed by the advice.

## API Integration

Add the advisor to `tools` alongside your existing tools. The beta header `advisor-tool-2026-03-01` is required ([API docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool)):

```python
response = client.beta.messages.create(
    model="claude-sonnet-4-6",          # executor
    max_tokens=4096,
    betas=["advisor-tool-2026-03-01"],
    tools=[
        {
            "type": "advisor_20260301",
            "name": "advisor",
            "model": "claude-opus-4-6",  # advisor
            "max_uses": 3,               # per-request cap
        },
        # ... your other tools
    ],
    messages=[...],
)
```

| Parameter  | Type    | Default   | Purpose |
|-----------|---------|-----------|---------|
| `type`     | string  | required  | Must be `"advisor_20260301"` |
| `model`    | string  | required  | Advisor model ID — billed at this model's rates |
| `max_uses` | integer | unlimited | Per-request cap on advisor calls |
| `caching`  | object  | off       | Advisor-side prompt caching; breaks even at ~3 calls per conversation |

The advisor must be at least as capable as the executor; check [API docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool) for the current supported pairs.

## Benchmark Results

From [Anthropic's announcement](https://claude.com/blog/the-advisor-strategy):

| Configuration | Benchmark | Result | Cost Impact |
|--------------|-----------|--------|-------------|
| Haiku + Opus advisor | BrowseComp | 41.2% vs 19.7% solo (+109%) | 85% cheaper than Sonnet alone |
| Sonnet + Opus advisor | SWE-bench Multilingual | +2.7pp over Sonnet solo | -11.9% cost per agentic task |

The Haiku configuration doubles standalone performance while costing 85% less than Sonnet — though scoring 29% lower than Sonnet solo. Near-Sonnet quality at Haiku prices.

## When to Consult the Advisor

The advisor pays off on decisions with high downstream cost if wrong. Anthropic's [recommended timing](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool) for coding:

1. **After initial exploration** — once the executor understands the problem, consult before committing to an approach.
2. **When stuck** — errors recurring, approach not converging.
3. **Before declaring done** — make the deliverable durable first (write the file, commit the change), then consult for a final review.

## Cost Controls

Advisor tokens bill at Opus rates; executor tokens at executor rates. Savings come from the advisor producing only short strategic guidance, not the full output ([API docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool)).

- **Per-request cap**: set `max_uses` to limit advisor calls per request.
- **Conversation-level cap**: track client-side. At the ceiling, remove the advisor from `tools` and strip `advisor_tool_result` blocks from history.
- **Output compression**: a conciseness instruction ("respond in under 100 words, enumerated steps") cut advisor output 35-45% in Anthropic's internal testing.
- **Effort pairing**: Sonnet at medium [effort](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool) + Opus advisor matches Sonnet at default effort.

## When This Backfires

Each consultation is a second inference pass at Opus rates. A single strong model is better when ([API docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool)):

- **The executor consults often.** Frequent advisor calls shift the token mix toward Opus rates and can exceed Opus solo cost.
- **Every turn needs frontier capability.** Uniformly hard tasks offer no mechanical turns to offload; the executor adds latency without covering cheap ground.
- **Single-turn Q&A or pass-through routing.** No plan to form.
- **Latency budgets are tight.** Each call pauses the executor stream while Opus runs — fine for background agents, painful for interactive chat.
- **Priority Tier is only on the executor.** It does not cascade to the advisor, so advisor calls fall back to standard capacity and rate-limit independently.

## Relationship to General Patterns

An API-native implementation of established patterns:

- **[Cognitive reasoning vs execution separation](cognitive-reasoning-execution-separation.md)** — advisor as reasoning layer, executor as execution layer, boundary enforced server-side.
- **[Cost-aware agent design](cost-aware-agent-design.md)** — model routing by complexity without manual cascade logic.
- **[Reasoning budget allocation](reasoning-budget-allocation.md)** — the reasoning sandwich via selective advisor calls rather than per-phase model switching.

## Key Takeaways

- The advisor strategy pairs a cost-effective executor with a frontier advisor consulted only on hard decisions — no orchestration code required.
- A single API call handles the full flow: the executor invokes the advisor like any other tool, and the server manages context routing.
- Haiku + Opus advisor more than doubles standalone BrowseComp performance at 85% less cost than Sonnet alone.
- Cap advisor calls with `max_uses` (per-request) and client-side tracking (per-conversation) to control spend.
- Call the advisor after exploration, when stuck, and before declaring done — skip it on mechanical turns.

## Related

- [Cognitive Reasoning vs Execution: A Two-Layer Agent Architecture](cognitive-reasoning-execution-separation.md)
- [Cost-Aware Agent Design](cost-aware-agent-design.md)
- [Reasoning Budget Allocation](reasoning-budget-allocation.md)
- [Heuristic-Based Effort Scaling](heuristic-effort-scaling.md)
- [Evaluator-Optimizer Pattern](evaluator-optimizer.md)
- [Agent Turn Model](agent-turn-model.md)
