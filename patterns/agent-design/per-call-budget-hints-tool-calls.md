---
title: "Per-Call Budget Hints on Tool Invocations"
description: "Let the caller lift the reasoning or returned-token cap on individual tool calls — narrowly, when the call is infrequent and information-dense — rather than re-tuning the global default."
term: "Per-Call Budget Hints on Tool Invocations"
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
  - reliability
aliases:
  - token budget hint
  - per-call reasoning budget
  - opt-in extended tool reasoning
last_reviewed: 2026-06-12
maturity: adopted
---

# Per-Call Budget Hints on Tool Invocations

> Raise the reasoning or returned-token cap on one tool call, only when that call is infrequent and dense, rather than re-tuning the global default.

A coding agent's tool calls have uneven [cost-quality curves](../../token-engineering/cost-aware-agent-design.md). A grep returning ten matches needs no extra reasoning; a deep web search across a regulatory corpus does. A per-call budget hint flags one invocation as "spend more here" without raising the budget for every other call. It pays off only when the call is infrequent, information-dense, and the model or tool can spend the lifted ceiling productively. Applied uniformly, quality drops while cost rises.

## The three shapes the hint takes

The contract has settled on three shapes.

| Shape | Set as | Example |
|-------|--------|---------|
| Binary opt-in | `default` / `unlimited` | OpenAI Responses `web_search` tool: `return_token_budget: "unlimited"` ([OpenAI changelog 2026-05-11](https://developers.openai.com/api/docs/changelog), [web search tool guide](https://developers.openai.com/api/docs/guides/tools-web-search)) |
| Categorical tier | `low` / `medium` / `high` / `xhigh` | OpenAI `reasoning.effort` ([reasoning guide](https://developers.openai.com/api/docs/guides/reasoning)); Anthropic `effort` for adaptive thinking ([Anthropic effort docs](https://platform.claude.com/docs/en/build-with-claude/effort)) |
| Numeric ceiling | `budget_tokens: N` | Anthropic `thinking.budget_tokens` (deprecated on Sonnet 4.6, removed on Opus 4.7 in favor of adaptive `effort`) ([extended thinking docs](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)) |

The shapes are not interchangeable. The binary opt-in attaches to a tool definition and shapes what the tool returns. The categorical tier and numeric ceiling attach to the message and shape how much the model thinks between calls.

## When the hint pays off

Liu et al. ([2025](https://arxiv.org/abs/2511.17006)) raised tool-call budgets on web-search agents and found that simply enlarging the budget "fails to improve agent performance" because the agent lacks awareness of remaining resources and "quickly hits a performance ceiling." Three conditions must hold together:

- The call is infrequent. Routine high-volume tools — file read, grep, status checks — should run on the default. Lifting their ceiling compounds spend with no return.
- The call is information-dense. Deep web search, long-document analysis, and multi-page evaluation all gain when the answer's value scales with how much the tool examines before stopping.
- The model or tool can spend the headroom. OpenAI documents `return_token_budget` as applying only to GPT-5+ reasoning web search — not `web_search_preview`, Chat Completions search models, or non-reasoning search ([web search guide](https://developers.openai.com/api/docs/guides/tools-web-search)).

A useful default: apply the hint to the one or two calls a caller would name in a sentence, and leave the rest untouched.

## Why it works

Uniform global defaults misallocate compute. One `max_tokens` set high enough for the longest call inflates every short call; one set low enough truncates the longest. Per-call hints move the decision to the call site, where the caller knows whether this is a deep-research run or a routine lookup. Liu et al. ([2025, §3](https://arxiv.org/abs/2511.17006)) frame this as a resource-awareness problem: the hint sets the upper bound and an in-context budget tracker provides the spend signal; both are needed to allocate well within the lifted ceiling. OpenAI's binary `return_token_budget` is the simplest shape, but the causal structure is the same ([OpenAI changelog 2026-05-11](https://developers.openai.com/api/docs/changelog)).

## When this backfires

The pattern's failure surface is larger than its success surface.

- Routine high-frequency calls. A hint on a tool called dozens of times per session compounds into overspend with no quality benefit. "Lift ceiling for important calls" collapses to "lift ceiling for every call" the moment the caller's classifier is fuzzy.
- Higher reasoning is not monotonically better. Su et al. ([2026](https://arxiv.org/abs/2604.05404)) report that "trajectories with higher PTE [prefill-token-equivalent] costs tend to have lower reasoning correctness." Anthropic's Sonnet 4.6 guidance agrees: set effort explicitly to avoid unexpected latency, starting from `medium` ([Anthropic effort docs](https://platform.claude.com/docs/en/build-with-claude/effort)).
- Budget-blind tools. If the tool is a black box returning a fixed-shape result, the agent cannot spend the lifted ceiling intelligently — the hint affects what comes back, not how the agent uses it.
- Tier-name aliasing across models. OpenAI's `reasoning.effort: high` and Anthropic's `effort: high` are not equivalent — "the effort scale is calibrated per model, so the same level name does not represent the same underlying value across models" ([Claude Code model config](https://code.claude.com/docs/en/model-config#adjust-effort-level)). A multi-provider harness setting `effort: high` uniformly gets inconsistent spend.
- API-surface churn. Anthropic's removal of `budget_tokens` on Opus 4.7 ([extended thinking docs](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)) shows any numeric-budget surface is on a deprecation timer; categorical tiers are more portable.
- Misclassified callers. A caller who labels every research call "high-effort" — easy under prompt pressure to "be thorough" — converts the optional hint into a default, defeating the cost discipline it enables.

## Relation to adjacent patterns

| Pattern | Allocates | Set by | Per |
|---------|-----------|--------|-----|
| [Reasoning budget allocation](reasoning-budget-allocation.md) | Reasoning compute by phase | Caller | Workflow phase |
| [Heuristic effort scaling](heuristic-effort-scaling.md) | Agent counts and tool-call ceilings | System prompt | Task tier |
| [Interactive effort sliders](interactive-effort-sliders.md) | Reasoning tier | Human operator | Turn |
| [Dual-budget control](dual-budget-control-search-agents.md) | Remaining tool calls + tokens | Agent | Candidate action |
| Per-call budget hint (this page) | Returned-token or thinking-token ceiling | Caller (agent or harness) | Tool call |
| [Effort-aware hooks](../../tool-engineering/effort-aware-hooks.md) | Hook-side gate strictness | Hook | Tool call (read-side) |

The hint does not replace these; it composes with them. A reasoning sandwich allocates by phase, a heuristic scales effort by task tier, and a per-call hint lifts the ceiling on the one or two deepest invocations within that phase.

## Example

A research agent runs a sequence of tool calls during a regulatory analysis. Most are routine. One — a web search across a multi-document corpus — needs to inspect many pages without stopping at the OpenAI web-search tool's standard returned-token cap. The hint goes on that one call.

Before — global ceiling set conservatively, deep-research call truncates:

```python
response = client.responses.create(
    model="gpt-5.5",
    reasoning={"effort": "high"},
    tools=[{"type": "web_search"}],
    input="Research the economic impact of semaglutide on global healthcare systems...",
)
```

After — global ceiling kept conservative, deep call lifts its own ceiling:

```python
response = client.responses.create(
    model="gpt-5.5",
    reasoning={"effort": "xhigh"},
    tools=[
        {
            "type": "web_search",
            "return_token_budget": "unlimited",
        },
    ],
    input="Research the economic impact of semaglutide on global healthcare systems...",
)
```

The hint is set in the tool definition, not the message, so it scopes precisely to that tool invocation ([OpenAI web search guide](https://developers.openai.com/api/docs/guides/tools-web-search)). Every other call in the session continues to run on the default budget. For long-running multi-search tasks, the same call can be run in background mode (`background: true`).

The Anthropic equivalent for the reasoning-side hint, on a model that still supports manual mode:

```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=20000,
    thinking={"type": "enabled", "budget_tokens": 16000},
    messages=[{"role": "user", "content": "Plan the audit of the auth surface..."}],
)
```

On Opus 4.7, the equivalent is `thinking: {type: "adaptive"}` with `effort: "xhigh"` — the manual numeric budget returns a 400 error ([Anthropic extended thinking docs](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)). New code targeting current models should prefer the categorical tier over the numeric ceiling.

## Key Takeaways

- A per-call budget hint is a caller-side knob that lifts the reasoning or returned-token ceiling on a single tool invocation without raising the global default.
- The hint takes three shapes — binary opt-in, categorical tier, numeric ceiling — scoped to either the tool definition or the message. They are not interchangeable.
- The hint pays off only when the call is infrequent, information-dense, and the model or tool can spend the headroom productively ([Liu et al. 2025](https://arxiv.org/abs/2511.17006)).
- Higher is not monotonically better. Su et al. ([2026](https://arxiv.org/abs/2604.05404)) report that higher tool-integrated reasoning cost correlates with lower correctness; Anthropic's own guidance warns of overthinking on `effort: high`.
- Numeric-budget surfaces are on a deprecation timer. Anthropic removed `budget_tokens` on Opus 4.7 in favor of adaptive `effort` — categorical tiers are the more portable shape.
- Apply the hint to the top one or two calls in a session. Misclassified callers convert the optional hint into a default and defeat the cost discipline it was meant to enable.

## Related

- [Reasoning Budget Allocation: The Reasoning Sandwich](reasoning-budget-allocation.md) — per-phase budget allocation; the hint composes inside one phase.
- [Heuristic-Based Effort Scaling in Agent Prompts](heuristic-effort-scaling.md) — encodes the classifier that decides when to lift the ceiling.
- [Interactive Effort Sliders: Per-Turn Reasoning-Budget Controls](interactive-effort-sliders.md) — the human-operator-held variant of the same knob.
- [Dual-Budget Control for Search Agents](dual-budget-control-search-agents.md) — what the agent does inside a lifted ceiling: VOI-scored allocation per action.
- [Token-Efficient Tool Design: Tools That Don't Eat Your Context](../../token-engineering/token-efficient-tool-design.md) — the design-time counterpart on the tool-author side.
- [Effort-Aware Hooks: Reading the Reasoning Tier](../../tool-engineering/effort-aware-hooks.md) — hook-side read of the tier the caller set.
- [Cost-Aware Agent Design](../../token-engineering/cost-aware-agent-design.md) — the broader routing framing the hint slots into.
</content>
</invoke>
