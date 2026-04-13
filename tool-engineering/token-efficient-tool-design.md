---
title: "Token-Efficient Tool Design: Tools That Don't Eat Your Context"
description: "Design tools so that each call injects the minimum tokens needed for the next agent decision — keeping context windows filled with signal, not noise."
aliases:
  - Tool Output Design
  - Semantic Tool Output
  - Agent-Friendly Output
tags:
  - context-engineering
  - cost-performance
---

# Token-Efficient Tool Design: Tools That Don't Eat Your Context

> Design tools so that each call injects the minimum tokens needed for the next agent decision.

!!! note "Also known as"
    Tool Output Design, Semantic Tool Output, Agent-Friendly Output. For the usability angle — designing tool outputs for semantic clarity and agent comprehension — see [Semantic Tool Output](semantic-tool-output.md).

## Tools as Context Injections

Every tool call produces output that enters the context window. A tool returning a 10,000-token API response when 200 tokens would suffice consumes 10% of a 100k context window on a single call. [Context engineering](../context-engineering/context-engineering.md) ([Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)) identifies tool design as a direct lever on context quality: the shape of tool output determines how much of the context window is signal versus noise.

The mechanism is attention dilution. Transformer self-attention computes pairwise relationships across every token — irrelevant tokens compete with relevant tokens for model focus. Research on long-context LLMs shows accuracy drops over 30% when target information is buried mid-context ("lost in the middle"). Oversized tool output places task-relevant fields in a sea of noise, degrading the model's ability to act on them correctly.

## Design Principles

### Return Only the Next Decision's Inputs

Ask: what does the agent need to know to decide what to do next? Return that, and nothing else. A tool checking CI status should return `"3 checks passed, 1 failed: lint"` — not the full CI API response with timestamps, metadata, and raw log output.

Structured output (JSON with named fields, or concise text) is easier for the agent to process than raw API dumps. Prefer IDs and summaries over full objects.

### Eliminate Functional Overlap

When two tools do similar things, the agent must reason about which to use before it can act. That reasoning consumes tokens and introduces error. Each tool should have a clear, non-overlapping scope. If two tools overlap, merge them or differentiate their purpose explicitly in their descriptions.

### Write Precise Descriptions

Tool names and descriptions are themselves context. An ambiguous description forces the agent to spend tokens resolving the ambiguity before invoking the tool. A precise description — what the tool does, when to use it, and what it returns — reduces that cost. See [Tool Selection Guidance](tool-description-quality.md) for how to write descriptions that prevent wrong tool choices.

### Cap Toolset Size

A large toolset is a reasoning tax. Before each call, the agent evaluates available tools and selects one. More tools means more evaluation tokens spent per decision. Keep the toolset to what the agent actually needs for its defined tasks. Remove tools that are rarely called or whose functionality is covered by another tool.

## Anti-Patterns

**Full API response passthrough.** The tool fetches a resource and returns the entire API response. The agent processes one field. The other 95% of the response is tokens burned on noise.

**Overlapping tools for search.** Two tools that both search — one for files, one for code — without a clear distinction produce agent hesitation. The agent tries both or picks arbitrarily, consuming context in the process.

**Toolset bloat.** A toolset of 30+ tools increases per-call reasoning cost. MCP tool metadata alone can add 30,000–60,000 tokens of overhead, consuming 25–30% of a 200k context window before any task work begins ([Lunar.dev](https://www.lunar.dev/post/why-is-there-mcp-tool-overload-and-how-to-solve-it-for-your-ai-agents)).

## Sizing Tool Output

A useful heuristic: the output of a tool call should fit in a paragraph. If it doesn't, consider whether:

1. The tool is returning too much (add filtering or summarisation)
2. The task genuinely requires that much information (in which case, load it once and structure it carefully)
3. The output should be written to a file rather than returned inline

## When This Backfires

Over-filtering introduces its own failure modes:

- **Edge cases silently dropped.** A summary that omits "unimportant" fields will eventually omit a field a rare-but-valid path needs. The agent cannot ask for data it doesn't know exists.
- **Abstraction breaks on schema change.** A bespoke summary layer tied to a specific response shape becomes a maintenance liability on every upstream API change.
- **Engineering overhead outweighs savings.** Building a custom summariser for a tool called once per session may cost more than the token savings justify.
- **Debugging is harder.** Diagnosing incorrect agent behaviour requires tracing through the summarisation layer as well as the agent's reasoning.

Apply this pattern where tools are called repeatedly in a loop, where output is consistently large, or where you have measured context pressure in production traces.

## Example

The before/after below shows a CI status tool refactored to return only what the agent needs to decide its next action.

**Before** — full API passthrough, ~400 tokens per call:

```python
def get_ci_status(run_id: str) -> dict:
    """Returns the full GitHub Actions run object."""
    response = requests.get(
        f"https://api.github.com/repos/org/repo/actions/runs/{run_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    return response.json()
    # Returns: id, name, head_branch, head_sha, status, conclusion,
    # workflow_id, check_suite_id, created_at, updated_at, run_started_at,
    # jobs_url, logs_url, artifacts_url, cancel_url, rerun_url,
    # previous_attempt_url, ... (40+ fields)
```

**After** — returns only the next decision's inputs, ~20 tokens per call:

```python
def get_ci_status(run_id: str) -> str:
    """Returns a one-line CI summary: pass/fail and which check failed.

    Use this to determine whether to proceed with a merge or investigate failures.
    Returns: e.g. '3 checks passed, 1 failed: lint' or 'all 4 checks passed'
    """
    response = requests.get(
        f"https://api.github.com/repos/org/repo/actions/runs/{run_id}/jobs",
        headers={"Authorization": f"Bearer {token}"},
    )
    jobs = response.json()["jobs"]
    failed = [j["name"] for j in jobs if j["conclusion"] == "failure"]
    passed = len(jobs) - len(failed)
    if failed:
        return f"{passed} checks passed, {len(failed)} failed: {', '.join(failed)}"
    return f"all {passed} checks passed"
```

The agent receives `"3 checks passed, 1 failed: lint"` and can immediately decide to run the lint fixer — no parsing, no discarding irrelevant fields.

## Key Takeaways

- Every tool response is a context injection — size it for the agent's next decision, not for completeness.
- Functional overlap between tools forces agent reasoning before action; eliminate it.
- Precise tool descriptions reduce selection cost; ambiguous ones increase it.
- Keep toolsets small: more tools means more tokens spent on selection per call.

## Related

- [Agent-Computer Interface (ACI)](agent-computer-interface.md) — token efficiency is one dimension of ACI design; the broader discipline covers affordances, constraints, feedback, and error prevention
- [Tool Selection Guidance](tool-description-quality.md)
- [CLI Scripts as Agent Tools: Return Only What Matters](cli-scripts-as-agent-tools.md)
- [Tool Minimalism and High-Level Prompting](tool-minimalism.md)
- [Consolidate Agent Tools](consolidate-agent-tools.md)
- [Advanced Tool Use: Scaling Agent Tool Libraries](advanced-tool-use.md)
- [Filesystem-Based Tool Discovery](filesystem-tool-discovery.md)
- [MCP Server Design: Building Agent-Friendly Servers](mcp-server-design.md) — applies the same token-efficiency principles at the MCP server boundary
- [Retrieval-Augmented Agent Workflows](../context-engineering/retrieval-augmented-agent-workflows.md)
- [Context Priming](../context-engineering/context-priming.md)
