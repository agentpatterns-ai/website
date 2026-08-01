---
title: "Token-Efficient Tool Design: Tools That Don't Eat Your Context"
term: "Token-Efficient Tool Design"
description: "Design tools so that each call injects the minimum tokens needed for the next agent decision — keeping context windows filled with signal, not noise."
aliases:
  - Tool Output Design
  - Agent-Friendly Output
tags:
  - token-engineering
  - tool-engineering
  - cost-performance
  - tool-agnostic
last_reviewed: 2026-06-13
maturity: established
---

# Token-Efficient Tool Design: Tools That Don't Eat Your Context

> Design tools so that each call injects the minimum tokens needed for the next agent decision.

Learn it hands-on with [Tool-Call Cost & Latency Budgeting](https://learn.agentpatterns.ai/tool-engineering/cost-and-latency-budgeting/), a guided lesson with quizzes.

!!! note "Also known as"
    Tool Output Design, Semantic Tool Output, Agent-Friendly Output. For the usability angle — designing tool outputs for semantic clarity and agent comprehension — see [Semantic Tool Output](../tool-engineering/semantic-tool-output.md).

## Tools as context injections

Every tool call produces output that enters the context window. A tool that returns a 10,000-token API response when 200 tokens would do consumes 10% of a 100k context window on a single call. [Context engineering](../context-engineering/context-engineering.md) ([Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)) treats tool design as a direct control on context quality. The shape of tool output sets how much of the context window is signal and how much is noise.

The mechanism is attention dilution. Transformer self-attention computes pairwise relationships across every token, so irrelevant tokens compete with relevant ones for the model's focus. [Liu et al. (2023)](https://arxiv.org/abs/2307.03172) find that accuracy drops sharply on multi-document QA when the target document sits in the middle of a long context rather than the beginning or end, the "lost in the middle" effect. Oversized tool output buries task-relevant fields in noise and degrades the model's ability to act on them correctly.

## Design principles

### Return only the next decision's inputs

Ask what the agent needs to know to decide what to do next. Return that, and nothing else. A tool that checks CI status should return `"3 checks passed, 1 failed: lint"`, not the full CI API response with timestamps, metadata, and raw log output.

Structured output (JSON with named fields, or concise text) is easier for the agent to process than raw API dumps. Prefer IDs and summaries over full objects.

### Eliminate functional overlap

When two tools do similar things, the agent has to reason about which one to use before it acts. This is the case for [consolidating overlapping tools](../tool-engineering/consolidate-agent-tools.md). That reasoning consumes tokens and introduces error. Give each tool a clear, non-overlapping scope. If two overlap, merge them or set their descriptions apart explicitly.

### Write precise descriptions

Tool names and descriptions are themselves context, scored for selection clarity in [Tool Selection Guidance](../tool-engineering/tool-description-quality.md). An ambiguous description forces the agent to spend tokens resolving the ambiguity before it invokes the tool. A precise description reduces that cost: say what the tool does, when to use it, and what it returns. See [how to write descriptions that prevent wrong tool choices](../tool-engineering/tool-description-quality.md).

### Cap toolset size

A large toolset is a reasoning tax. Before each call, the agent reviews the available tools and picks one, so more tools means more evaluation tokens per decision. Keep the toolset to what the agent needs for its defined tasks. Remove tools that are rarely called or whose work is covered elsewhere.

## Anti-patterns

Full API response passthrough. The tool fetches a resource and returns the entire API response. The agent uses one field. The other 95% of the response is tokens burned on noise.

Overlapping tools for search. Two tools that both search, one for files and one for code, with no clear distinction make the agent hesitate. The agent tries both or picks one at random, and spends context either way.

Toolset bloat. A toolset of 30 or more tools raises the per-call reasoning cost. A typical multi-server MCP setup can consume about 55,000 tokens in tool definitions alone, before any task work begins ([Anthropic](https://www.anthropic.com/engineering/advanced-tool-use)).

## Sizing tool output

A useful heuristic is that tool output should fit in a paragraph. If it does not, consider whether:

1. The tool returns too much, so add filtering or summarization.
2. The task genuinely needs that much information, in which case load it once and structure it carefully.
3. The output should be written to a file rather than returned inline.

## When this backfires

Over-filtering introduces its own failure modes:

- Edge cases silently dropped: a summary that omits "unimportant" fields will eventually omit a field a rare-but-valid path needs. The agent cannot ask for data it does not know exists.
- Abstraction breaks on schema change: a bespoke summary layer tied to a specific response shape becomes a maintenance burden on every upstream API change. [Semantic Tool Output](../tool-engineering/semantic-tool-output.md) shapes the result at the source instead.
- Engineering overhead outweighs savings: building a custom summarizer for a tool called once per session may cost more than the token savings justify.
- Debugging is harder: diagnosing wrong agent behavior means tracing through the summarization layer as well as the agent's reasoning.

Apply this pattern where tools are called repeatedly in a loop, where output is consistently large, or where you have measured context pressure in production traces.

## Example

The before/after below shows a CI status tool refactored to return only what the agent needs to decide its next action.

Before, a full API passthrough at about 400 tokens per call:

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

After, returning only the next decision's inputs at about 20 tokens per call:

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

## FAQ

**Why does oversized tool output hurt beyond the raw token count?**

The mechanism is attention dilution. Transformer self-attention computes pairwise relationships across every token, so irrelevant tokens compete with relevant ones for the model's focus. [Liu et al. (2023)](https://arxiv.org/abs/2307.03172) find accuracy drops sharply on multi-document QA when the target document sits in the middle of a long context rather than at either end.

**How large should a single tool response be?**

A useful heuristic is that it should fit in a paragraph. If it does not, work through three options: the tool returns too much and needs filtering or summarization; the task genuinely needs that much information, in which case load it once and structure it carefully; or the output belongs in a file rather than inline in the context window.

**When is a custom summarization layer not worth building?**

When the tool is called once per session, the engineering overhead can cost more than the token savings justify. Filtering also drops edge-case fields the agent cannot ask for because it does not know they exist, couples a bespoke summary to a response shape that changes upstream, and adds a layer to trace when debugging wrong behavior. Apply it where output is consistently large.

## Key Takeaways

- Every tool response is a context injection — size it for the agent's next decision, not for completeness.
- Functional overlap between tools forces agent reasoning before action; eliminate it.
- Precise tool descriptions reduce selection cost; ambiguous ones increase it.
- Keep toolsets small: more tools means more tokens spent on selection per call — the discipline of [Tool Minimalism](../tool-engineering/tool-minimalism.md).

## Related

- [Agent-Computer Interface (ACI)](../tool-engineering/agent-computer-interface.md) — token efficiency is one dimension of ACI design; the broader discipline covers affordances, constraints, feedback, and error prevention
- [Tool Selection Guidance](../tool-engineering/tool-description-quality.md)
- [CLI Scripts as Agent Tools: Return Only What Matters](../tool-engineering/cli-scripts-as-agent-tools.md)
- [Tool Minimalism and High-Level Prompting](../tool-engineering/tool-minimalism.md)
- [Consolidate Agent Tools](../tool-engineering/consolidate-agent-tools.md)
- [Advanced Tool Use: Scaling Agent Tool Libraries](../tool-engineering/advanced-tool-use.md)
- [Filesystem-Based Tool Discovery](../tool-engineering/filesystem-tool-discovery.md)
- [MCP Server Design: Building Agent-Friendly Servers](../tool-engineering/mcp-server-design.md) — applies the same token-efficiency principles at the MCP server boundary
