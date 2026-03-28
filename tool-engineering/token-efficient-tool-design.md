---
title: "Token-Efficient Tool Design: Right-Sizing Tool Output"
description: "Design tools so that each call injects the minimum tokens needed for the next agent decision. Tool Output Design, Semantic Tool Output, Agent-Friendly Output"
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

Every tool call produces output that enters the context window. A tool returning a 10,000-token API response when 200 tokens would suffice consumes 10% of a 100k context window on a single call. [Anthropic's context engineering guidance](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) identifies tool design as a direct lever on context quality: the shape of tool output determines how much of the context window is signal versus noise.

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

**Toolset bloat.** A toolset of 30+ tools increases per-call reasoning cost. Agents in complex tasks may spend more tokens on tool selection than on the task itself [unverified — depends on model and toolset design].

## Sizing Tool Output

A useful heuristic: the output of a tool call should fit in a paragraph. If it doesn't, consider whether:

1. The tool is returning too much (add filtering or summarisation)
2. The task genuinely requires that much information (in which case, load it once and structure it carefully)
3. The output should be written to a file rather than returned inline

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

## Unverified Claims

- Agents with 30+ tools may spend more tokens on tool selection than on the task itself `[unverified — depends on model and toolset design]`

## Related

- [Tool Selection Guidance](tool-description-quality.md)
- [CLI Scripts as Agent Tools: Return Only What Matters](cli-scripts-as-agent-tools.md)
- [Tool Minimalism and High-Level Prompting](tool-minimalism.md)
- [Consolidate Agent Tools](consolidate-agent-tools.md)
- [Poka-Yoke for Agent Tools](poka-yoke-agent-tools.md)
- [Advanced Tool Use: Scaling Agent Tool Libraries](advanced-tool-use.md)
- [Filesystem-Based Tool Discovery](filesystem-tool-discovery.md)
- [Retrieval-Augmented Agent Workflows](../context-engineering/retrieval-augmented-agent-workflows.md)
- [Context Priming](../context-engineering/context-priming.md)
