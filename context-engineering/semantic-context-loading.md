---
title: "Semantic Context Loading: Language Server Plugins for Agents"
description: "Query codebases through Language Server Protocol semantics — symbol lookup, reference finding, type navigation — rather than reading raw files"
aliases:
  - JIT Context
  - LSP-backed context loading
  - semantic code navigation
tags:
  - context-engineering
  - cost-performance
  - agent-design
---

# Semantic Context Loading: Language Server Plugins for Agents

> Query codebases through Language Server Protocol semantics — symbol lookup, reference finding, type navigation — rather than reading raw files.

!!! info "Also known as"
    [Retrieval-Augmented Agent Workflows](retrieval-augmented-agent-workflows.md), [Context Hub](context-hub.md), JIT Context, RAG

## The Problem with File-Based Context Loading

The default agent approach to understanding a codebase is file reading: open a file, scan for relevant content, repeat. This loads everything in the file — imports, unrelated functions, comments, boilerplate — regardless of what the agent actually needs. A 500-line module loaded to find one function signature consumes all 500 lines of context.

## Semantic Queries as an Alternative

Language Server Protocol (LSP) is the interface that powers IDE features like "Go to Definition" and "Find All References." An agent with access to LSP-backed tools can make targeted queries instead of reading files:

- `findSymbol("AuthService")` — returns the definition location and signature
- `findReferences("AuthService")` — returns all call sites
- `getTypeHierarchy("User")` — returns parent and child types

Each query returns exactly the relevant symbols, not the full file contents. The token cost is proportional to the result, not to the file size.

## Serena: LSP for Agents

Serena is an MCP server that exposes LSP capabilities to Claude Code agents [unverified — Serena is described as an MCP server with LSP integration, but its exact API surface and supported languages are not verified against official documentation]. It allows agents to navigate codebases using semantic queries rather than file reads. The pattern applies to any LSP-compatible tooling, not just Serena — what matters is the capability, not the specific implementation.

Agents using LSP-backed tools can answer questions like:

- Where is this type defined?
- What implements this interface?
- What calls this function?

without loading any file into context until they have a specific location to read.

## Comparison with Native Indexing

Tools like GitHub Copilot and Cursor implement their own codebase indexing that approximates semantic lookup [unverified — the internal mechanisms of Copilot's and Cursor's codebase indexing are not publicly documented in detail]. The distinction matters:

| Approach | How It Works | When It Helps |
|----------|-------------|---------------|
| File reading | Load file, parse manually | Small files, simple structures |
| Native indexing | Tool's built-in semantic search | When available and configured |
| LSP-backed queries | Direct semantic protocol | Precise navigation, large codebases |

LSP-backed queries are most valuable when the codebase is large, the agent's task requires cross-file navigation, and an LSP server is already configured for the language in use.

## Trade-offs

**Setup cost.** LSP-backed tools require a running language server. Not all languages have mature LSP implementations, and not all repos are configured for LSP. The tooling layer is more complex than file reading.

**Precision vs. breadth.** Semantic queries retrieve exactly what is requested. If the agent doesn't know the right symbol name or doesn't know what it's looking for, it may miss relevant context that a file scan would surface. Semantic loading works best when the agent has a clear target — a specific function, type, or reference — rather than an exploratory task.

**Language coverage.** LSP quality varies by language. TypeScript, Python, Go, and Rust have strong LSP implementations. Less common languages may have limited or no LSP support.

## Example

The following shows the contrast between file-based and LSP-backed context loading for the same navigation task using Serena's MCP tools in Claude Code.

**File-based approach** — loads the entire module to find one function signature:

```bash
# Agent reads the full file to locate AuthService
# A 400-line module is loaded entirely into context
cat src/auth/auth_service.py
```

**LSP-backed approach** — queries only the relevant symbol:

```
# Agent calls Serena's find_symbol tool
mcp__plugin_serena_serena__find_symbol: {"symbol_name": "AuthService", "path": "src/"}
```

The LSP query returns the class definition, its constructor signature, and public method names — not the full file. For a 400-line module, this might return 20–30 lines of directly relevant symbols instead of the complete source.

Chaining queries for cross-file navigation avoids loading any intermediate files:

```
# Find all callers of AuthService without reading every file that might import it
mcp__plugin_serena_serena__find_referencing_symbols: {
  "symbol_name": "AuthService",
  "path": "src/"
}
```

This returns call sites across the codebase with their file paths and line numbers. The agent can then read only the specific lines it needs — rather than every file that might reference `AuthService`.

## Key Takeaways

- LSP-backed tools let agents retrieve symbols, references, and type hierarchies instead of reading entire files, reducing context consumption proportionally.
- The approach is most effective for large codebases with clear navigation targets; exploratory tasks still benefit from file reading.
- Setup requires a running language server; LSP quality and coverage vary by language.
- The same pattern applies to any LSP-compatible tooling — the capability (semantic queries) matters more than the specific tool.

## Related

- [Context Budget Allocation](context-budget-allocation.md)
- [Retrieval-Augmented Agent Workflows](retrieval-augmented-agent-workflows.md)
- [Token-Efficient Tool Design](../tool-engineering/token-efficient-tool-design.md)
- [Context Priming](context-priming.md)
- [Seeding Agent Context: Breadcrumbs in Code](seeding-agent-context.md)
- [Repository Map Pattern](repository-map-pattern.md)
- [Layered Context Architecture](layered-context-architecture.md)
- [Discoverable vs. Non-Discoverable Context](discoverable-vs-nondiscoverable-context.md)
- [Context Compression Strategies](context-compression-strategies.md)
- [Context Engineering](context-engineering.md)
- [Observation Masking](observation-masking.md)
- [Phase-Specific Context Assembly](phase-specific-context-assembly.md)
- [Prompt Compression](prompt-compression.md)
- [Repository-Level Retrieval for Code Generation](repository-level-retrieval-code-generation.md)
- [Structured Domain Retrieval](structured-domain-retrieval.md)
- [MCP: The Open Protocol Connecting Agents to External Tools](../standards/mcp-protocol.md)
