---
title: "Name-Only Path Routing: Finding Files Without an Index"
term: "Name-Only Path Routing"
description: "A model picking directories by name recovered 0.465 of gold files at eight candidates against 0.352 for FTS5. A flat pass over the same names scored higher."
tags:
  - context-engineering
  - tool-agnostic
  - rag
  - arxiv
aliases:
  - name-only directory routing
  - tree routing for code search
  - path-name file discovery
last_reviewed: 2026-10-02
maturity: emerging
---

# Name-Only Path Routing: Finding Files Without an Index

> Name-only path routing picks directories by name alone, and finds files a fixed lexical query ranks nowhere.

Name-only path routing hands a model the issue text plus a menu of child directory and file names, then walks into the children whose returned probability clears a threshold. It builds no index and reads no file contents. Across 82 audited issues from 11 repositories at pinned pre-fix commits, the walk recovered 0.465 of the files a fix touched within eight candidates. An in-memory SQLite FTS5 ranking reached 0.352 and a fixed full-issue `rg` replay 0.245 ([Bajaj, 2026](https://arxiv.org/abs/2609.35918v1)). The paired gain over FTS5 was +0.113, with a 95% repository-cluster bootstrap interval of 0.053 to 0.168.

## Conditions this holds under

The result is narrower than "routing beats grep".

- The comparison is one fixed query. Each lexical arm gets one non-adaptive shot, and the study "tests an issue's first fixed query, not an adaptive agent" ([Bajaj, 2026](https://arxiv.org/abs/2609.35918v1)). On a different task, repository-level code completion, a baseline where the model writes its own ripgrep commands "achieves performance comparable to sophisticated graph-based baselines" ([Better Call Grep, 2026](https://arxiv.org/abs/2601.23254v3)).
- The fix lands in one directory. The subgroup gain over FTS5 was +0.229 across 35 single-directory gold sets and +0.027 across 47 multi-directory sets ([Bajaj, 2026](https://arxiv.org/abs/2609.35918v1)). Holding several branches open is what routing does worst.
- Your own repository is one where it works. Routing beat FTS5 in nine of the 11, tied in one, and lost in one ([Bajaj, 2026](https://arxiv.org/abs/2609.35918v1)).
- File discovery is the thing measured. No issue was resolved in this study, and complete coverage of the annotated lines stayed rare after packing: "14/82 issues for tree, 8/82 for FTS5, 5/82 for rg, and 15/82 for fusion" ([Bajaj, 2026](https://arxiv.org/abs/2609.35918v1)).

## Why it works

The issue and the source code disagree about words. A bug report describes behavior; the code names identifiers. A full-text query built from that report "may match documentation, changelogs, tests, and unrelated implementation", while the directory structure "supplies an alternate route to candidate files" ([Bajaj, 2026](https://arxiv.org/abs/2609.35918v1)). Scoring path names scores a different signal from BM25 over file contents, so the two arms miss different files: routing found 61 gold-file occurrences absent from FTS5's top eight across 40 issues, and FTS5 found 34 absent from routing's.

What the hierarchy contributes is unproven. A flat control showed the same model every eligible path in bounded menus, with no directory hierarchy at all, and scored higher: "An exploratory flat path control reached 0.572 recall while using 24.6 model calls per issue, compared with 8.9 for routing" ([Bajaj, 2026](https://arxiv.org/abs/2609.35918v1)). The author says so directly: "The flat result rules out a claim that the hierarchy itself is shown to cause the original gain over lexical search." The flat control is not a clean ablation either, since it "used a different instruction and more calls than tree", roughly 2.8 times as many. What the two arms give is an operating point, not a causal split: flat scored +0.107 above routing at eight files, interval 0.017 to 0.224, for 24.6 model calls against 8.9.

## When this backfires

- Repositories where the walk simply does not work. VS Code scored 0.13 for both arms and Serverless lost to FTS5 at 0.16 against 0.23 ([Bajaj, 2026](https://arxiv.org/abs/2609.35918v1)). The paper does not say why; treat the gain as a property of the repository you measure.
- Latency-sensitive turns. Routing averaged 8.93 seconds and 8.89 model calls per issue, where an FTS5 query averaged 7.5 ms after an 894 ms index build ([Bajaj, 2026](https://arxiv.org/abs/2609.35918v1)). The paper's own verdict: "Its 8.93-second mean latency and model charge make a blanket replacement for FTS5 unattractive."
- Fusing the two candidate lists. Reciprocal-rank fusion raised mean recall to 0.491 but recovered fewer complete gold-file sets than routing alone, 23 against 25. "Rank fusion can displace a tree-selected gold file at a fixed limit; combining candidate lists is not free" ([Bajaj, 2026](https://arxiv.org/abs/2609.35918v1)). Keep both shortlists rather than merging them.
- Branches a name policy prunes. Five of 87 selected cases were dropped because gold paths sat outside the searchable-file policy, "including real source under directories named build" ([Bajaj, 2026](https://arxiv.org/abs/2609.35918v1)). A name-driven walk declines exactly those directories.
- Any claim about fixes shipped. Recall is not repair, and a framework that seeds candidates deterministically before letting an agent revise them does report the downstream number, raising the SWE-bench Lite resolution rate "from 44.00% to 52.33%" over the strongest baseline, with a Qwen3.5 35B repair model ([SemNav, 2026](https://arxiv.org/abs/2609.31176v1)).

## Example

The measured loop is reproducible without the authors' tooling ([Bajaj, 2026](https://arxiv.org/abs/2609.35918v1)). Each menu adds a `none_of_these` option, and the instruction given was:

> Choose the best route toward answer evidence. Directory options summarize descendants, so select a directory when a descendant could answer. Choose none only when the question is unrelated to every option.

The traversal parameters:

| Parameter | Value |
|---|---|
| Issue text shown per menu | First 500 characters |
| Descendant names per directory option | Up to 12, from at most 3 levels below |
| Child retention threshold | The larger of 0.01 and 0.01 times the best child |
| Model-call cap | 32 per issue |
| Time cap | 180 seconds per issue |
| Output | At most 16 ranked file paths |

Path rank is traversal order rather than a multiplied probability, and no issue hit either cap.

## Key Takeaways

- Routing buys +0.113 file recall over a fixed FTS5 query, interval 0.053 to 0.168, for 8.89 model calls and 8.93 seconds per issue. Decide against those two numbers, not the headline.
- Do not credit the hierarchy. A flat pass over every path scored higher, so the tree is an observed way to spend fewer calls and not a demonstrated cause of the gain.
- Run the two shortlists side by side. Rank fusion raised the mean and lost complete gold-file sets.
- Measure on your own repository first. The same method won nine repositories, tied one, and lost one.
- Nothing here says a fix lands sooner. Complete line coverage reached 14 of 82 issues at best, and issue resolution was never scored.

## Related

- [Lexical-First Retrieval for Agentic Search](../tool-engineering/lexical-first-retrieval-for-agentic-search.md) — the same question one axis over: when a tuned lexical index is enough, and what the agent loop has to do to make it so.
- [Symbol Ranking for Agent File Pickers](symbol-ranked-file-picker.md) — a third retrieval key for the same problem, paid for with an index this method does not need.
- [Repository Map Pattern](repository-map-pattern.md) — a prepared ranking of the repository, where this reads the live tree at query time and builds nothing.
- [Agent-Tuned Code Search](agent-tuned-code-search.md) — the delegated version, where a hosted tool runs the search loop and returns paths plus line ranges.
- [Retrieval Sufficiency Gate](retrieval-sufficiency-gate.md) — the check that follows file discovery, since finding the files is not the same as delivering the lines.
