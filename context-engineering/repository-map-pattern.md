---
title: "Repository Map Pattern: AST + PageRank for Dynamic Code"
term: "Repository Map Pattern"
description: "Parse source files with tree-sitter, rank symbols by PageRank, then binary-search fit the most relevant entries into the agent's token budget."
aliases:
  - repo map
  - repomap
  - aider repo map
tags:
  - context-engineering
  - agent-design
  - tool-agnostic
  - rag
last_reviewed: 2026-05-27
maturity: established
---

# Repository Map Pattern: AST + PageRank for Dynamic Code Context

> Parse source files with tree-sitter to extract structural symbols, rank them by graph importance, then binary-search fit the most relevant entries into the agent's available token budget.

## The orientation problem

In a large codebase, directory listings, file samples, and keyword greps waste tokens on low-signal content. The agent needs to know which functions exist, which classes matter, and how they connect — not implementation details.

The repository map pattern builds a weighted structural overview fitted to a token budget.

## Three-layer mechanism

The pattern runs in three stages: parse, rank, then fit.

```mermaid
graph LR
    A[Source Files] -->|tree-sitter| B[AST Symbols]
    B -->|reference graph| C[PageRank Scores]
    C -->|binary search| D[Token-Fitted Map]
    D --> E[Agent Context]
```

### 1. Parse: tree-sitter AST extraction

Tree-sitter parses source into ASTs and extracts structural elements: function signatures, class definitions, method names, and call signatures. Unlike full file reads, this captures what exists without loading implementation bodies.

| Feature | ctags | tree-sitter |
|---------|-------|-------------|
| Output | Symbol names only | Full function signatures |
| Installation | External tool required | Bundled via `py-tree-sitter-languages` |
| Language support | Varies | 33+ languages |
| Structural depth | Flat symbol list | Nested AST with scope |

([Aider blog: Building a better repository map with tree-sitter](https://aider.chat/2023/10/22/repomap.html))

### 2. Rank: PageRank on the reference graph

Source files become nodes in a directed graph. Edges connect files that share symbol references. PageRank with personalization scores each node: files being edited get higher weight, heavily-referenced symbols rank higher, and the result favors task-relevance over sheer size.

PageRank works here because importance propagates through the call graph. A function referenced by 20 files outranks a helper called once, and symbols referenced by important symbols gain higher scores in turn. BM25 and recency weighting lack this property — the top-ranked symbols surface the architectural spine without any query. ([Aider repo map docs](https://aider.chat/docs/repomap.html))

### 3. Fit: binary search to token budget

The `get_ranked_tags_map()` method binary-searches for the most ranked tags that fit within `max_map_tokens` (default: 1,024), targeting within 15% of budget. Fewer files in context expands the map; more files shrinks it. The agent always gets the most important symbols that fit.

([RepoMapper](https://github.com/pdavis68/RepoMapper))

## What a repository map looks like

At different token budgets, the same codebase produces different levels of detail:

```
# ~200 tokens: top-level structure only
src/auth/auth_service.py
  class AuthService
    def authenticate(user_id, token)
    def refresh_token(token)
src/models/user.py
  class User
    def validate()

# ~800 tokens: expanded with secondary files
src/auth/auth_service.py
  class AuthService
    def authenticate(user_id: str, token: str) -> AuthResult
    def refresh_token(token: str) -> TokenPair
    def revoke_session(session_id: str) -> None
src/auth/middleware.py
  class AuthMiddleware
    def process_request(request) -> Response
src/models/user.py
  class User
    def validate() -> bool
    def to_dict() -> dict
src/models/session.py
  class Session
    def is_expired() -> bool
```

Higher budget: more files with full type annotations. Lower budget: only the most-referenced symbols.

## Benchmark impact

Aider's system reached a then-SOTA 26.3% resolve rate on SWE-bench Lite, with 70.3% correct file identification. The map helps the agent locate where to change before deciding what to change. The SWE-bench post credits the repo map but does not isolate its contribution in an ablation; the figure reflects the full Aider stack. ([Aider SWE-bench blog post](https://aider.chat/2024/05/22/swe-bench-lite.html))

## Alternative approaches

Codebase orientation strategies:

| Approach | Mechanism | Best when |
|----------|-----------|-----------|
| Repository map (tree-sitter + PageRank) | Pre-computed structural index | Large, stable codebases; agent needs cross-file orientation |
| Agentic search (Claude Code) | On-demand Glob, Grep, Read | Frequent changes; freshness matters more than structure |
| Vector embeddings (Cursor, Windsurf) | Semantic similarity search | Natural-language queries against code |

Claude Code skips indexing and uses agentic search — early RAG experiments showed agentic search performed better. ([Vadim's blog: Claude Code Doesn't Index Your Codebase](https://vadim.blog/claude-code-no-indexing)) Cursor and Windsurf use vector stores with re-ranking. ([Mike Mason: AI Coding Agents in 2026](https://mikemason.ca/writing/ai-coding-agents-jan-2026/))

## MCP server availability

The pattern ships as standalone MCP servers, so any tool can use it:

- [RepoMapper](https://github.com/pdavis68/RepoMapper) — Aider's repo map logic as an MCP server; any MCP-compatible agent can request a token-fitted map.
- [mcp-server-tree-sitter](https://github.com/wrale/mcp-server-tree-sitter) — AST-based symbol extraction, dependency graphs, and complexity analysis as MCP tools.
- [Serena](https://github.com/oraios/serena) — LSP-based approach for symbol-level navigation and editing.

## Example

Adding RepoMapper as an MCP server in Claude Code's configuration:

```json
// .mcp.json
{
  "mcpServers": {
    "repomapper": {
      "command": "npx",
      "args": ["-y", "repomapper-mcp"]
    }
  }
}
```

Once configured, the agent can request a token-fitted map before making changes:

```
User: Fix the authentication bug in the login flow.

Agent: I'll start by requesting a repository map to understand the codebase structure.

[calls repomapper.get_repo_map with max_tokens=1024]

Result:
  src/auth/auth_service.py
    class AuthService
      def authenticate(user_id: str, token: str) -> AuthResult
      def refresh_token(token: str) -> TokenPair
  src/auth/middleware.py
    class AuthMiddleware
      def process_request(request) -> Response
  src/models/user.py
    class User
      def validate() -> bool

Agent: The map shows AuthService.authenticate and AuthMiddleware.process_request
are the most-referenced auth symbols. I'll read those files first.
```

The map consumed 87 tokens instead of the ~12,000 tokens that reading all source files would require. The agent identified the right entry points without scanning the full codebase.

## When this backfires

- Rapidly-changing codebases: the map is recomputed per session but not per edit. In a monorepo with thousands of commits per day, the parsed AST can be stale within minutes; Claude Code's on-demand agentic search is a better fit because it queries the live filesystem.
- Heavy metaprogramming: codebases that generate classes or functions at runtime (Rails `method_missing`, Python metaclasses, macro-heavy Rust) produce AST symbols that do not reflect runtime structure; PageRank over those symbols misleads rather than orients.
- Small or flat codebases: a repo with fewer than ~20 files gains nothing from the ranking step — reading all source files fits inside a standard context window and provides richer implementation detail than signatures alone.
- Large repos with huge token budgets: if the agent context window is already large enough to hold most of the codebase directly, the compression step introduces truncation risk for no gain.

## Key Takeaways

- Tree-sitter extraction + PageRank ranking + binary-search fitting produces a weighted structural overview for any token budget.
- The map adapts dynamically: expands with few files in context, shrinks with many.
- Three codebase orientation approaches (structural indexing, agentic search, vector embeddings) — choose by codebase size and change frequency.
- RepoMapper and mcp-server-tree-sitter make the pattern available to any MCP-compatible agent.

## Related

- [Semantic Context Loading](semantic-context-loading.md)
- [Context Compiler](context-compiler.md)
- [Retrieval-Augmented Agent Workflows](retrieval-augmented-agent-workflows.md)
- [Pre-Execution Codebase Exploration](../workflows/pre-execution-codebase-exploration.md)
- [Context Budget Allocation](context-budget-allocation.md)
- [Token-Efficient Tool Design](../token-engineering/token-efficient-tool-design.md)
- [Context Priming](context-priming.md)
- [Seeding Agent Context: Breadcrumbs in Code](seeding-agent-context.md)
- [Layered Context Architecture](layered-context-architecture.md)
- [Phase-Specific Context Assembly](phase-specific-context-assembly.md)
- [MCP: The Open Protocol Connecting Agents to External Tools](../standards/mcp-protocol.md)
- [Repository-Level Retrieval for Code Generation](repository-level-retrieval-code-generation.md)
- [Context Compression Strategies](context-compression-strategies.md)
- [Prompt Compression](prompt-compression.md)
