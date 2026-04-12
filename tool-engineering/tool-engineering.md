---
title: "Tool Engineering Principles for AI Agent Development"
description: "Design agent tools like APIs — with documentation, examples, edge-case handling, and mistake-proofing — not as boilerplate wrappers around existing functions"
aliases:
  - Tool Descriptions as Onboarding
  - Mistake-Proofing for Agent Tools
  - Poka-Yoke for Tool Design
tags:
  - agent-design
  - instructions
  - cost-performance
  - source:opendev-paper
---
# Tool Engineering

> Design agent tools like APIs — with documentation, examples, edge-case handling, and mistake-proofing — not as boilerplate wrappers around existing functions.

!!! info "Also known as"
    Tool Descriptions as Onboarding, Mistake-Proofing / Poka-Yoke

## Tools as the Agent's Interface to the World

Agent quality is bounded by tool quality. No prompt compensates for a tool interface the model cannot use reliably. Tool interface defects — wrong tool selection, incorrect parameters, misinterpreted output — are a recurring failure mode in agent loops.

Per [Anthropic's effective agents post](https://www.anthropic.com/engineering/building-effective-agents), tool design deserves the same investment as prompt engineering.

## Minimize Formatting Overhead

Inputs requiring precise formatting — exact line counts, complex escaping, specific delimiters — create failure surface. Design inputs to accept formats with strong model priors from training data (JSON, markdown, plain prose). Anthropic's guidance is explicit: avoid formatting "overhead such as having to keep an accurate count of thousands of lines of code, or string-escaping any code it writes" ([Building Effective Agents, Appendix 2](https://www.anthropic.com/engineering/building-effective-agents)).

The same applies to outputs: return formats the model can parse without counting characters or matching offsets.

## Comprehensive Documentation

Tool docstrings should include:

- What the tool does, stated plainly
- What each parameter accepts, including types and valid ranges
- At least one concrete example with real inputs and expected output
- Known edge cases and what happens when they occur

A model with no prior knowledge of your system forms its understanding entirely from the docstring. Write accordingly.

This works because LLMs reason over tool descriptions via in-context learning — the docstring is the model's only ground truth about what a tool does and how to call it correctly. A well-written docstring functions as a compact, always-present reference that shapes every tool invocation in the session.

## Poka-Yoke: Mistake-Proofing

Poka-yoke is the engineering practice of making errors structurally impossible or structurally obvious. Applied to tool design:

- Use parameter names that cannot be misread (`user_id` not `user`, `start_date` not `date`)
- Enumerate valid values rather than accepting free text where only specific values are valid
- Return structured errors that tell the model what went wrong and what to try instead — not generic failure messages
- Validate inputs and return early with a clear message rather than failing deep in execution

The goal is to make the correct call easier than the incorrect call.

## Independent Testing

Test tools independently before full agent integration. Observe how the model calls each tool in isolation: correct selection, correct parameters, correct output handling. Errors in full agent loops are ambiguous — prompt, tool, or interaction. Isolated testing surfaces tool-specific misuse patterns and eliminates one variable from loop-level failures.

## Tool Result Optimization

The preceding sections address tool *inputs*; this section addresses tool *outputs*. The OPENDEV paper reports ~54% reduction in peak context consumption through per-tool-type summarization and large output offloading ([Bui, 2025 §2.3.2](https://arxiv.org/abs/2603.05344)):

- **Per-type summarization**: file reads replaced with metadata (line count, character count), search results collapsed to match counts, directory listings reduced to item counts, command outputs truncated to line counts for longer outputs
- **Large output offloading**: results exceeding 8,000 characters written to session-specific scratch files with a 500-character preview — the agent can retrieve full output on demand without default context cost
- **Agent-aware truncation hints**: when output is offloaded, the truncation message includes a recovery hint tailored to the agent's capabilities (e.g., suggesting subagent delegation or incremental search)

Pre-computed summaries are reused during context compaction, avoiding redundant re-processing and improving both speed and quality of emergency compaction ([Bui, 2025 §2.3.2](https://arxiv.org/abs/2603.05344)). See also [Semantic Tool Output](semantic-tool-output.md) for complementary output formatting patterns.

## Example

The following shows a poorly designed tool definition contrasted with one that applies tool engineering principles — comprehensive documentation, poka-yoke parameter names, structured errors, and summarised output.

**Before: minimal wrapper with vague parameters**

```python
def search(query, type, limit):
    """Search the codebase."""
    results = _run_search(query, type, limit)
    return results  # returns raw list, potentially thousands of items
```

**After: engineered tool with documentation, validated inputs, and summarised output**

```python
def search_codebase(
    search_query: str,
    file_type: Literal["python", "typescript", "markdown", "all"],
    max_results: int = 20,
) -> dict:
    """
    Search source files by content pattern.

    Args:
        search_query: The literal string or regex pattern to find.
            Example: "class AuthMiddleware" or r"def \\w+_handler"
        file_type: Restrict matches to one file type, or "all" for every type.
        max_results: Maximum number of results to return (1–100). Defaults to 20.

    Returns:
        {
          "match_count": <int>,        # total matches found before truncation
          "returned": <int>,           # matches included in this response
          "results": [                 # list of up to max_results items
            {"file": <str>, "line": <int>, "snippet": <str>}
          ],
          "truncated": <bool>          # true when match_count > max_results
        }

    Edge cases:
        - Regex syntax errors return {"error": "invalid_regex", "detail": <str>}
        - Zero matches returns {"match_count": 0, "returned": 0, "results": [], "truncated": false}
        - Outputs exceeding 8 000 characters are written to .scratch/<session_id>/search_<n>.json;
          this response includes a "scratch_path" key and a 500-character preview.
    """
    if not 1 <= max_results <= 100:
        return {"error": "invalid_range", "detail": "max_results must be between 1 and 100"}
    try:
        raw = _run_search(search_query, file_type, max_results)
    except re.error as exc:
        return {"error": "invalid_regex", "detail": str(exc)}
    return _summarise(raw, max_results)
```

The docstring gives the model a concrete call example, documents every return key, and explains what happens on error — so the model can handle failure without guessing. The `file_type` enumeration eliminates free-text guessing. The structured error response tells the model exactly what to fix.

## When This Backfires

Tool engineering investment pays off when tools are reused across many agent sessions and workflows. It adds friction without payoff in these conditions:

- **Rapidly-changing interfaces**: when the tool's API contract is still unstable, heavyweight docstrings become maintenance debt — the description drifts from actual behavior, misleading the model more than a terse stub would.
- **One-off or exploratory scripts**: a tool called once in a single session does not need edge-case documentation or enumerated parameter values; the cost of engineering it outweighs the benefit.
- **Upstream documentation already exists**: if the tool wraps a well-documented external API the model has strong training priors for, a thin wrapper that exposes the native interface may outperform a custom docstring that introduces inconsistencies.

Apply the full pattern to stable, shared tools that are called repeatedly across agent runs. Apply minimal-viable documentation to throwaway or prototype tooling.

## Key Takeaways

- Tool quality bounds agent quality — no prompt compensates for a bad tool interface
- Minimize formatting overhead; prefer formats the model has strong priors for from training data
- Write comprehensive docstrings with examples and edge cases, not terse API references
- Apply poka-yoke: unambiguous parameter names, enumerated valid values, structured error messages
- Test tools independently before integration to surface model misuse patterns early
- Optimize tool results: summarize by type, offload large outputs, include agent-aware truncation hints for ~54% peak context reduction

## Related

- [Poka-Yoke for Agent Tools](poka-yoke-agent-tools.md) — deep dive on structural constraint patterns
- [Tool Description Quality](tool-description-quality.md)
- [Write Tool Descriptions Like Onboarding Docs](tool-descriptions-as-onboarding.md)
- [Consolidate Agent Tools](consolidate-agent-tools.md)
- [Token-Efficient Tool Design](token-efficient-tool-design.md)
- [Tool Minimalism and High-Level Prompting](tool-minimalism.md)
- [Advanced Tool Use: Scaling Agent Tool Libraries](advanced-tool-use.md)
- [Typed Schemas at Agent Boundaries](typed-schemas-at-agent-boundaries.md)
- [CLI Scripts as Agent Tools](cli-scripts-as-agent-tools.md)
- [Unix CLI as the Native Tool Interface](unix-cli-native-tool-interface.md)
- [Agent-Computer Interface (ACI)](agent-computer-interface.md) — tool design as a UX discipline
- [Machine-Readable Error Responses (RFC 9457)](rfc9457-machine-readable-errors.md) — structured errors for agent tool calls
- [MCP Server Design: Building Agent-Friendly Servers](mcp-server-design.md) — naming, schema design, and error handling for MCP-exposed tools
- [Self-Healing Tool Routing](self-healing-tool-routing.md) — cost-weighted routing and failure recovery for agent tool calls
