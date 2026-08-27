---
title: "Symbol Ranking for Agent File Pickers"
term: "Symbol-Ranked File Picker"
description: "Rank @ mention candidates by the symbols a file defines, not only by filename similarity. Worth the index dependency in large repositories, useless outside them."
tags:
  - context-engineering
  - tool-engineering
  - claude
aliases:
  - symbol-ranked file suggestion
  - symbol ranking for at mentions
  - retrieval key for file pickers
applies_to: "claude-code@2.x"
last_reviewed: 2026-08-23
maturity: emerging
---

# Symbol Ranking for Agent File Pickers

> Ranking file-picker candidates by the symbols each file defines resolves queries that name a function or type, which filename similarity cannot.

A file picker that fuzzy-matches filenames can only answer path-shaped queries. Type the name of a function instead and there may be no filename to match at all: `@resolve_virtual_path` returned nothing in the Monty codebase, while symbol search resolved it to its defining file ([Sourcegraph, 2026](https://sourcegraph.com/blog/claude-code-file-picker-symbol-ranking)). Adding symbol definitions as a second ranking signal covers that query shape.

## When this pays off

Adopt it only where all four conditions hold:

- Basenames collide. In a small or flat repository the default picker already lands the right file.
- Your language's symbols reach the index. Rust `macro_rules!` macros are absent from Sourcegraph's, so `@defer_drop` never resolves ([Sourcegraph, 2026](https://sourcegraph.com/blog/claude-code-file-picker-symbol-ranking)).
- The code is indexed and reachable. Private repositories need a Sourcegraph instance plus `CLAUDE_SG_ENDPOINT`, `SRC_ENDPOINT`, and `SRC_ACCESS_TOKEN` — "You need both endpoint variables, not one" ([Sourcegraph, 2026](https://sourcegraph.com/blog/claude-code-file-picker-symbol-ranking)). The token now goes out "only when `SRC_ENDPOINT` matches the endpoint actually being called", after an earlier build sent an instance token to sourcegraph.com. Without them there is no symbol tier at all.
- You still select files by hand. Cursor's guidance for the uncertain case is the opposite: "If you're not sure which files matter, skip it — Agent finds relevant files through its own search" ([Cursor](https://cursor.com/docs/agent/prompting)).

## What the wrong key looks like

Fuzzy path matching "asks whether every character of your query appears somewhere in the path, in order" ([Sourcegraph, 2026](https://sourcegraph.com/blog/claude-code-file-picker-symbol-ranking)). Walking `crates/monty/src/run.rs` against `os.rs` finds the `o` in "monty" and the `s` in "src", then the extension. It is a legitimate match and the wrong file.

Sourcegraph reports two symptoms in the Monty codebase, and they need different fixes. Querying `@os.rs` returned 15 irrelevant results, among them `run.rs`, `lib.rs`, and `repl.rs`, while two real `os.rs` files existed — but symbol ranking is not what repairs that one. Re-run with the symbol channel off, both real files rank 1 and 2 "from filename scoring alone. Turning symbols on changes that list not at all" ([Sourcegraph, 2026](https://sourcegraph.com/blog/claude-code-file-picker-symbol-ranking)). That was a path-scoring problem, and better filename matching is the whole fix.

The second symptom is the one this page is about. `@resolve_virtual_path` and `@dropguard` return zero results either way, because neither query is a subsequence of the path it should return. Symbol ranking resolves them to `path_security.rs` and `heap_traits.rs`. The author is careful about the scope: "That's the case for indexing symbols, and it's a narrower case than 'the picker is bad.'" ([Sourcegraph, 2026](https://sourcegraph.com/blog/claude-code-file-picker-symbol-ranking))

Users hit the same wall independently. A January 2026 report against Claude Code v2.1.15 described having to "scroll through a long list and pick the right one with the arrow keys" despite a correct partial filename match. It was closed as not planned ([claude-code#20065](https://github.com/anthropics/claude-code/issues/20065)).

## Why it works

The mechanism is a mismatch between the match predicate and the query distribution, and swapping the key closes it. A subsequence test over paths has near-unbounded recall and almost no precision, because paths carry directory names, an extension, and repeated common letters. Once accidental matches dominate the candidate set, the only signal left to rank on is character position, which says nothing about what a file contains. And a query naming a symbol carries no path information for the predicate to accept correctly in the first place.

Scoring on symbol definitions restores the missing signal, and logarithmic tier separation keeps it safe: "the tiers sit far enough apart that no stack of weak signals ever outranks a strong one" ([Sourcegraph, 2026](https://sourcegraph.com/blog/claude-code-file-picker-symbol-ranking)). An exact basename still wins outright and skips the network entirely.

Symbol is a genuinely distinct retrieval key rather than one vendor's framing. VS Code Copilot Chat exposes code symbols as a `#`-mention type separate from files, though scoped to open editors: "To reference a symbol, make sure to open the file containing the symbol in the editor first" ([VS Code docs](https://code.visualstudio.com/docs/copilot/chat/copilot-chat-context)). Cursor's documented mention types cover files, folders, terminals, chats, git diffs, and the browser, with no symbol type ([Cursor](https://cursor.com/docs/agent/prompting)).

## When this backfires

- Freshly moved code. The symbol half is only as fresh as the index behind it, and the hook "intersects symbol hits against `git ls-files` so you're never offered a file you don't have". When Monty refactored `heap.rs` into `heap/mod.rs`, the index still carried the old path: "Stale path, dropped, empty list." You get the filename half until the index catches up ([Sourcegraph, 2026](https://sourcegraph.com/blog/claude-code-file-picker-symbol-ranking)).
- Symbols with no single home. "A trait method with thirty near-identical overrides has no single defining file, so no scoring signal can pick one for you" ([Sourcegraph, 2026](https://sourcegraph.com/blog/claude-code-file-picker-symbol-ranking)).
- Queries an exact basename already answers. "Sometimes it does nothing at all, and that's correct." `@value` returns the same four paths either way, because `value.rs` and `value.ts` win on exact basename and skip the symbol channel by design; "`git ls-files` order decides" between them ([Sourcegraph, 2026](https://sourcegraph.com/blog/claude-code-file-picker-symbol-ranking)).
- Silent degradation. When the index misses a construct, the picker falls back to filename ranking and reports nothing about the gap.
- Query egress. Prefixes shorter than four characters never go over the wire, which means everything longer does ([Sourcegraph, 2026](https://sourcegraph.com/blog/claude-code-file-picker-symbol-ranking)). That is a new disclosure surface for private code.
- Single-source evidence. Every number on this page is self-reported by a code-search vendor, measured on one 1,139-file Rust repository, with the 19,000-file monorepo figure a projection rather than a measurement ([Sourcegraph, 2026](https://sourcegraph.com/blog/claude-code-file-picker-symbol-ranking)).

## Example

Claude Code exposes the seam as a settings key. Sourcegraph's Apache-2.0 ranking hook installs to `~/.claude/file-suggestion` and registers under `fileSuggestion`, which replaces the built-in picker with an external command ([Sourcegraph, 2026](https://sourcegraph.com/blog/claude-code-file-picker-symbol-ranking)):

```json
{
  "fileSuggestion": {
    "type": "command",
    "command": "~/.claude/file-suggestion"
  }
}
```

Sourcegraph's implementation blends filename and symbol signals into one score per candidate ([Sourcegraph, 2026](https://sourcegraph.com/blog/claude-code-file-picker-symbol-ranking)):

| Signal | Weight |
|---|---|
| Exact basename match | 1,000,000 |
| Symbol name matches exactly | 100,000 |
| Symbol name starts with query | 5,000 |
| Symbol name contains query | 800 |
| Definition rather than re-export | +200 |
| File touched in last 25 commits | +50 |

Keystroke latency is the budget this has to fit. Sourcegraph measured a warm p95 of 11.12ms and p50 of 9.32ms over 200 subprocess spawns against a 15ms target, with ranking itself under 1ms across 1,139 files and a 66ms cold start from git operations. Symbol results are cached to disk per four-character prefix, and "anything shorter than four characters never goes over the wire at all" ([Sourcegraph, 2026](https://sourcegraph.com/blog/claude-code-file-picker-symbol-ranking)).

## Key Takeaways

- Better ranking inside the wrong key cannot fix a picker; changing the key can. Symbol-shaped queries have no filename to score against.
- Treat the vendor's benchmarks as directional. One Rust repository, one implementation, no independent replication.
- Test index coverage before adopting: query a symbol you know exists in each construct your language uses, and check it resolves.
- Weigh the disclosure cost against the convenience. Query prefixes of four characters or more reach the index host, one fetch per four-character prefix rather than one per keystroke.
- If you rarely `@`-mention files, the cheaper fix is to name the symbol in the prompt and let the agent search.

## Related

- [Semantic Context Loading](semantic-context-loading.md) — querying a codebase through Language Server Protocol symbols, the same retrieval key applied to the agent's own navigation rather than the picker.
- [Repository Map Pattern](repository-map-pattern.md) — ranking symbols by graph importance to fill a token budget, where this ranks them to answer one query.
- [Agent-Tuned Code Search](agent-tuned-code-search.md) — the delegated version of the same trade: a hosted index buys latency and costs freshness.
- [Indexed Regex Search for Agent Tools](../tool-engineering/indexed-regex-search-agent-tools.md) — the local index alternative, and the staleness problem any index inherits.
- [Lexical-First Retrieval for Agentic Search](../tool-engineering/lexical-first-retrieval-for-agentic-search.md) — the same question one layer up: which retrieval mechanism the query shape actually calls for.
