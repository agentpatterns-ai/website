---
title: "Agent-Tuned Code Search: Retrieval Built for the Loop"
term: "Agent-Tuned Code Search"
description: "An agent-tuned code search tool answers one task string with file paths and line ranges: a large latency win, a modest token win, bounded by index freshness."
tags:
  - context-engineering
  - tool-engineering
  - tool-agnostic
  - cost-performance
aliases:
  - agentic code search tool
  - code search for coding agents
  - agent-consumption code retrieval
last_reviewed: 2026-07-27
maturity: emerging
---

# Agent-Tuned Code Search: Retrieval Built for the Loop

> Agent-tuned code search runs its own search loop and hands the calling agent file paths and line ranges instead of a browsable results page.

Agent-tuned code search is a retrieval tool whose output contract is written for a coding agent rather than a human reader. You give it a task in natural language, it runs its own search loop across a repository, and it returns matching file paths and line ranges with a short note on what each one does ([Jarmak and Hartman, Sourcegraph](https://sourcegraph.com/blog/code-finder-fast-code-search-for-agents)). The calling agent reads a focused answer instead of spending turns opening files and backing out of dead ends.

## When this pays off

The pattern is conditional, not a default. Adopt it when all of these hold:

- Search latency is on your critical path. That is where the measured gap is largest.
- The agent works against committed code on an indexed revision. Hosted search indexes each repository's default branch; covering more needs an experimental setting capped at 64 additional branches ([Sourcegraph admin docs](https://sourcegraph.com/docs/admin/search)).
- The returned citations are tight enough to act on.
- Sending repository contents to a hosted service is acceptable. Code Finder is Beta, Sourcegraph Cloud only, and becomes credit-billable at general availability ([Sourcegraph changelog](https://sourcegraph.com/changelog/code-finder-beta)).

When any condition fails, the agent's own [repository-level retrieval](repository-level-retrieval-code-generation.md) or a local [indexed regex search](../tool-engineering/indexed-regex-search-agent-tools.md) is the cheaper answer.

## Read the benchmark on the right axis

Vendor benchmarks report time and cost together, and the two tell different stories. Sourcegraph ran file-finding tasks three ways, publishing results relative to Code Finder where lower is better ([Jarmak and Hartman](https://sourcegraph.com/blog/code-finder-fast-code-search-for-agents)):

| Approach | Time | Cost |
|---|---|---|
| Code Finder | 1.00x | 1.00x |
| Coding agent calling Sourcegraph MCP tools | 1.14x | 1.63x |
| Coding agent using local search | 2.19x | 1.32x |

The headline claim, "cost up to 40% less," is measured against the vendor's own general MCP tools, not against the agent's local grep. Against local search the cost ratio is 1.32x, so about a 24% saving, while the 2.19x figure is time. Against a competent local search loop the case is therefore mostly latency and only partly tokens.

Treat the numbers as directional. The methodology names neither the task count, the repositories, nor the agent model, and describes result quality only as "comparable" ([Jarmak and Hartman](https://sourcegraph.com/blog/code-finder-fast-code-search-for-agents)).

## Why it works

The mechanism is context compression across a tool boundary. A general coding agent carries a broad instruction set and a large context window into every search turn, so a single-purpose tool can search more directly and return a smaller, denser answer ([Jarmak and Hartman](https://sourcegraph.com/blog/code-finder-fast-code-search-for-agents)). Anthropic names the same causal chain for sub-agents generally: they "facilitate compression by operating in parallel with their own context windows, exploring different aspects of the question simultaneously before condensing the most important tokens," and token usage alone explains 80% of the variance in browsing-agent performance ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)).

Independent work confirms the mechanism on code exploration. FastContext routes exploration to a dedicated subagent that "issues parallel tool calls and returns concise file paths and line ranges as focused context." The largest savings "occur on SWE-QA, reaching 60.3% for GPT-5.4," with the explorer "accounting for only 2.1% of that total" cost ([Zhang et al., 2026](https://arxiv.org/abs/2606.14066)). The verbose intermediate state stays outside the solver's window.

## When this backfires

- Uncommitted or off-branch work. Default-branch indexing means the tool answers about a revision the agent is not editing ([Sourcegraph admin docs](https://sourcegraph.com/docs/admin/search)). Freshness matters most "when it comes to the model reading its own writes": an agent that searches for text it just wrote and does not find it "will often go into a wild goose chase, waste tokens" ([Cursor](https://cursor.com/blog/fast-regex-search)).
- Broad citations. When the explorer returns a loose candidate set, the solver verifies the repository itself instead of trusting the evidence. One FastContext case study measures read and search commands rising from 83 to 170 and main-agent tokens from 2,045.5k to 3,604.4k ([Zhang et al., 2026](https://arxiv.org/abs/2606.14066)).
- Unscoped delegation. A single free-text task string invites the scoping failures practitioners report for autonomous sub-agent delegation: omitted file paths, no verification of returned claims, and answers that "imply they read file content but demonstrably did not" ([claude-code#40339](https://github.com/anthropics/claude-code/issues/40339)).
- Small repositories. The 2.19x advantage is a ratio; where local search already returns in well under a second, a network hop plus a second model's inference is slower in absolute terms.
- Work needing shared context. Anthropic reports the delegated sub-agent architecture works poorly for domains that require all agents to share context or that carry many inter-agent dependencies, "such as most coding tasks" ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)).

## Example

The tool contract is the design. Sourcegraph's Code Finder exposes one required parameter, `task`, described as "The task or query to research and answer," and returns "a short summary followed by links to the relevant files and line ranges." It also declines broad cross-repository discovery, so the caller identifies the repository first ([Sourcegraph MCP docs](https://sourcegraph.com/docs/api/mcp)).

Two consequences follow. The caller cannot narrow the search with file globs or a revision, so scoping quality rests entirely on the task string. And because the tool returns citations rather than snippets, the agent still reads the files it is pointed at — the saving lands on the search phase, not the read phase.

## Key Takeaways

- Agent-tuned code search returns paths and line ranges for one task string, not a browsable results page ([Sourcegraph MCP docs](https://sourcegraph.com/docs/api/mcp)).
- Split the vendor benchmark by axis: 2.19x faster than local search, but only about 24% cheaper than it; the "40% less" figure compares against the vendor's own general MCP tools ([Jarmak and Hartman](https://sourcegraph.com/blog/code-finder-fast-code-search-for-agents)).
- The mechanism is context compression across a tool boundary, independently measured at 60.3% token reduction on SWE-QA for 2.1% explorer overhead ([Zhang et al., 2026](https://arxiv.org/abs/2606.14066)).
- Default-branch indexing is the binding constraint for an agent editing on a feature branch ([Sourcegraph admin docs](https://sourcegraph.com/docs/admin/search)).
- Citation precision decides the outcome: loose citations trigger re-verification and make the delegation net-negative on tokens ([Zhang et al., 2026](https://arxiv.org/abs/2606.14066)).

## Related

- [Repository-Level Retrieval for Code Generation](repository-level-retrieval-code-generation.md) — the retrieval layer this tool contract sits on top of.
- [Retrieval-Augmented Agent Workflows](retrieval-augmented-agent-workflows.md) — pulling context in at the moment it is needed, the general shape of in-loop retrieval.
- [Indexed Regex Search for Agent Tools](../tool-engineering/indexed-regex-search-agent-tools.md) — the index implementation beneath a hosted search tool, and its freshness problem.
- [Trained Repository Explorer Sub-Agent (FastContext)](../patterns/agent-design/fastcontext-trained-repository-explorer.md) — the locally served, trained variant of the same explorer contract.
- [Persistent Shared Search Sub-Agent](../patterns/multi-agent/persistent-search-subagent.md) — the multi-agent version, which deduplicates exploration across workers rather than compressing one agent's search.
- [Agent Retrieval Provenance as an Audit Control](../security/agent-retrieval-provenance.md) — the compliance case for scoped retrieval: the same citations that save tokens also form the audit trail of what the agent read.
