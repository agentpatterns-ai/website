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

## What It Is

Semantic context loading is a retrieval pattern where the agent queries a codebase through Language Server Protocol (LSP) operations — symbol lookup, reference finding, type hierarchy — instead of reading whole files. Each query returns only the requested symbol's definition, signature, or call sites, so token cost scales with the result, not the file size.

## The Problem with File-Based Context Loading

The default agent approach is file reading: open a file, scan, repeat. This loads imports, unrelated functions, comments, and boilerplate regardless of what the agent needs. A 500-line module loaded to find one function signature consumes all 500 lines of context.

## Semantic Queries as an Alternative

LSP powers IDE features like "Go to Definition" and "Find All References." An agent with LSP-backed tools can issue targeted queries:

- `findSymbol("AuthService")` — returns the definition location and signature
- `findReferences("AuthService")` — returns all call sites
- `getTypeHierarchy("User")` — returns parent and child types

## Serena: LSP for Agents

Serena is an open-source MCP server that provides semantic code retrieval and editing tools across 40+ languages via a language server backend ([github.com/oraios/serena](https://github.com/oraios/serena)). The pattern applies to any LSP-compatible tooling — what matters is the capability, not the specific implementation.

Agents using LSP-backed tools can answer: where is this type defined? what implements this interface? what calls this function? — without loading any file into context until they have a specific location to read.

## Comparison with Native Indexing

GitHub Copilot and Cursor implement their own codebase indexing that approximates semantic lookup. Copilot combines a semantic index over repository files with text search and symbol tracing ([VS Code Copilot workspace context docs](https://code.visualstudio.com/docs/copilot/workspace-context)); Cursor's internal mechanism is not publicly documented.

| Approach | How It Works | When It Helps |
|----------|-------------|---------------|
| File reading | Load file, parse manually | Small files, simple structures |
| Native indexing | Tool's built-in semantic search | When available and configured |
| LSP-backed queries | Direct semantic protocol | Precise navigation, large codebases |

LSP-backed queries are most valuable when the codebase is large, the task requires cross-file navigation, and an LSP server is already configured for the language.

## Trade-offs

**Setup cost.** LSP-backed tools need a running language server; not all repos are configured for one, and the tooling layer is more complex than file reading.

**Precision vs. breadth.** Semantic queries return exactly what is asked for. If the agent doesn't know the right symbol or is exploring blindly, it may miss context a file scan would surface. Semantic loading works best with a clear target.

**Language coverage.** TypeScript, Python, Go, and Rust have strong LSP implementations; less common languages may have limited or no support.

**Protocol-level critique.** LSP was designed for editors, not agents. Armin Ronacher argues LSP forces agents to chain many atomic calls (open file, calculate offset, request definition, parse URI, extract snippet) and that agents often skip LSP entirely when working from doc snippets or ad-hoc reads ([A Language For Agents](https://lucumr.pocoo.org/2026/2/9/a-language-for-agents/)). The LSAP project layers higher-level agent-native operations on top of LSP to avoid this overhead ([github.com/lsp-client/LSAP](https://github.com/lsp-client/LSAP)). Treat LSP-backed retrieval as a floor — wrappers like Serena or LSAP-style protocols carry most of the benefit.

## Example

Contrast between file-based and LSP-backed context loading for the same navigation task using Serena's MCP tools in Claude Code.

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
