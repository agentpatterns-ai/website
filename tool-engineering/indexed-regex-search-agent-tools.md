---
title: "Indexed Regex Search for Agent Tools"
description: "Back an agent's regex search tool with a trigram or suffix-array index so query latency stays bounded as the repository and agent fleet grow, at the cost of index freshness and infra."
tags:
  - tool-engineering
  - context-engineering
  - tool-agnostic
---

# Indexed Regex Search for Agent Tools

> Back an agent's regex search tool with a pre-built text index so query latency stays bounded on large repositories, at the cost of freshness machinery and index infrastructure.

## The Harness-Level Bottleneck

Agents use regex search constantly. `ripgrep`-style scans walk every file in the tree, so wall-clock time grows with repository size. Cursor's engineering team measured `rg` invocations on large enterprise monorepos "routinely" taking more than 15 seconds, and frames regex search as "one of the few Agent operations whose latency scales with the size and complexity of the code being worked on" ([Cursor: Fast regex search](https://cursor.com/blog/fast-regex-search)). Below a few hundred thousand files this is invisible; above it, search becomes a dominant tax on every agent turn — multiplied by the number of agents running in parallel.

## The Pattern

Build a text index once, then answer regex queries against it instead of scanning the full tree. Two mechanisms are in production use.

### Trigram Inverted Indexes

Split every document into overlapping 3-character sequences and store, for each trigram, the list of documents containing it. At query time, decompose the regex into an AND/OR tree of required trigrams, intersect posting lists for a candidate set, then run the regex engine on just that set ([Russ Cox: Regular Expression Matching with a Trigram Index](https://swtch.com/~rsc/regexp/regexp4.html)). Most real regex queries contain a literal substring of at least three characters, which reduces to a small set of trigrams; posting-list intersection is linear in the shortest list. Reference implementations: [google/codesearch](https://github.com/google/codesearch) and [sourcegraph/zoekt](https://github.com/sourcegraph/zoekt).

### Suffix Arrays

Concatenate the corpus into one string and build a sorted array of all its suffixes. Binary search answers substring and character-class queries against the array in logarithmic time ([Nelson Elhage: Regular expression search with suffix arrays](https://blog.nelhage.com/2015/02/regular-expression-search-with-suffix-arrays/)). The tradeoff is build cost: updates require reconstructing the array over the entire corpus, so suffix arrays suit single-machine, read-mostly indexes (Elhage's [livegrep](https://livegrep.com/search/linux) indexes the Linux kernel this way) and do not scale to frequently-edited monorepos ([Cursor](https://cursor.com/blog/fast-regex-search)).

### Refinements That Matter at Scale

A plain trigram index produces posting lists too long for frequent trigrams. Two production refinements address this:

- **Probabilistic quadgrams** (GitHub's Project Blackbird): store a bloom filter alongside each posting encoding the character that follows the trigram, yielding effectively "3.5-gram" precision without quadgram storage cost ([Cursor](https://cursor.com/blog/fast-regex-search)).
- **Sparse n-grams** (Cursor): extract variable-length n-grams chosen deterministically by a weight table that scores rare character pairs higher than common ones, reducing posting-list lookups at query time ([Cursor](https://cursor.com/blog/fast-regex-search)).

## The Freshness Problem

An index only helps if it reflects the agent's current writes. A stale index that misses a symbol the agent just wrote returns a falsely empty result, and the model may conclude the symbol does not exist and loop ([Cursor](https://cursor.com/blog/fast-regex-search)). Cursor anchors the base index to a git commit and layers uncommitted edits on top so "the model reading its own writes" still works. Any indexed search tool intended for active agent loops needs an equivalent incremental-update path.

## When the Opposite Wins

Claude Code rejects pre-built indexes for code search. Boris Cherny (Anthropic, Claude Code lead): "Early versions of Claude Code used RAG + a local vector db, but we found pretty quickly that agentic search generally works better. It is also simpler and doesn't have the same issues around security, privacy, staleness, and reliability" ([HN](https://news.ycombinator.com/item?id=43164253)). A Claude engineer in the same thread: "In our testing we found that agentic search outperformed \[it\] by a lot, and this was surprising." Claude Code pairs Glob, Grep, and Read and lets the model drive exploration rather than querying a pre-built structure ([Vadim Nicolai: Claude Code Doesn't Index Your Codebase](https://vadim.blog/claude-code-no-indexing)).

This counter-result targets *vector* indexes more than deterministic trigram indexes, but it still constrains the choice: indexed regex search is worth the infra when repository scale forces it, not by default.

## Apply When

- Enterprise-scale or monorepo codebases where `ripgrep` routinely exceeds the interactive latency budget ([Cursor](https://cursor.com/blog/fast-regex-search)).
- Multi-agent fleets sharing a workspace, where every agent pays the search cost and a shared index amortises the scan.
- Harnesses where regex calls dominate the tool-call distribution and are the critical path for the agent's next step.

## Skip When

- Repos small enough that `ripgrep` on local SSD returns sub-second — the index build and freshness machinery exceed the savings.
- Single-agent interactive workflows where freshness requirements outpace any reasonable update cycle.
- Environments where an on-disk or remote index widens the attack surface beyond the working tree itself ([HN: Boris Cherny](https://news.ycombinator.com/item?id=43164253)).

## Example

A trigram decomposition of `func (s *Server) Handle` against a corpus yields required trigrams including `fun`, `unc`, `Ser`, `erv`, `rve`, `ver`, `Han`, `and`, `ndl`, `dle`. The index intersects those posting lists, producing a candidate set of perhaps a few dozen files out of a million. The regex engine then runs only on those candidates. Plain `ripgrep` over the same corpus scans every file regardless of relevance. The mechanism is walked through in detail in [Russ Cox's article](https://swtch.com/~rsc/regexp/regexp4.html).

## Key Takeaways

- Regex search is a harness-level bottleneck at monorepo scale: latency grows with repo size, multiplied by agent concurrency.
- Trigram inverted indexes and suffix arrays both reduce full-corpus scans to candidate-set scans; trigram indexes scale to write-heavy workspaces, suffix arrays do not.
- Production refinements (probabilistic quadgram masks, sparse n-grams) address the posting-list-length problem that kills naive trigram indexes at large scale.
- Index freshness is the core engineering cost: an agent that edits files and then queries must read its own writes.
- Claude Code's documented evaluation of agentic search vs. indexed retrieval is the strongest counter-evidence that indexing is not universally the right call.

## Related

- [Token-Efficient Tool Design](token-efficient-tool-design.md)
- [Filesystem-Based Tool Discovery](filesystem-tool-discovery.md)
- [Repository Map Pattern](../context-engineering/repository-map-pattern.md)
- [Repository-Level Retrieval for Code Generation](../context-engineering/repository-level-retrieval-code-generation.md)
- [Semantic Context Loading](../context-engineering/semantic-context-loading.md)
- [Retrieval-Augmented Agent Workflows](../context-engineering/retrieval-augmented-agent-workflows.md)
