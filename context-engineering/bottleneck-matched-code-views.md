---
title: "Matching the Code View to the Task Bottleneck"
term: "Bottleneck-Matched Code Views"
description: "Structural code maps (AST, call graph, dependencies, doc search) cut agent tokens when localization is the bottleneck. Once the patch or test decides the task, success gains narrow."
aliases:
  - bottleneck-matched code representations
  - task-matched repository views
tags:
  - context-engineering
  - tool-agnostic
  - arxiv
last_reviewed: 2026-11-10
maturity: emerging
---

# Matching the Code View to the Task Bottleneck

> In one controlled study, structural code views helped a coding agent most when localization was the bottleneck, and less when patch or test writing was.

Choose the repository view an agent gets by asking which step limits the task. Sepidband et al. gave Claude Code with Haiku 4.5 on-demand MCP maps built from abstract syntax trees, call graphs, module dependencies, documentation, or all four. The maps cut tokens and raised recall when localization was the hard part. Success gains narrowed or reversed when the decisive step was patch or test authoring ([Sepidband et al., 2026](https://arxiv.org/abs/2611.07286v1)).

## When a structural view pays off

The study compared each map against a raw-tool baseline (Read, Edit, Write, Grep, Glob, Bash) on four task families, one run per task ([Sepidband et al., 2026](https://arxiv.org/abs/2611.07286v1)):

| Task (benchmark) | Success vs baseline | Tokens vs baseline | Wall time vs baseline |
|---|---|---|---|
| Fault localization (LinuxFLBench) | recall@10 0.757–0.829 vs 0.717 | 25–39% fewer | Up: 82–106 s vs 67 s |
| Program repair (SWE-bench Pro) | 44.3–50.6% vs 49.0% resolved | 17–26% fewer | Down: 194–209 s vs 269 s |
| Security patching (SecBench) | Call graph 34.3% vs 28.9%; AST 25.3% | Fewer for four of five maps | Up: 136–290 s vs 66 s |
| Test generation (SWT-bench) | 37.9–47.8% vs 44.7% | More for every map | Up: 170–201 s vs 161 s |

Localization gains do not carry over to repair. On SWE-bench Pro the dominant loss for every map was "correct localization, wrong patch": the map found the gold-patch files and the agent wrote a wrong fix ([Sepidband et al., 2026](https://arxiv.org/abs/2611.07286v1)).

## Match the view to the bug shape

The paper's trajectory analysis of fault localization and security patching ties each single-relation map to the bug shape it helps, and to where it fails ([Sepidband et al., 2026](https://arxiv.org/abs/2611.07286v1)):

| Evidence in the task | View that helped | Where it failed |
|---|---|---|
| Report names the faulty function | AST (containment edges map the symbol to its file) | Root cause sits in a structurally distant file |
| Symptom in one function, fault in a caller or callee | Call graph | Fault reached by a non-call path, such as firmware loading |
| Crash stack in the prompt (security patching) | Call graph | Real fix is a caller-side format invariant |
| Report names an API, function, or call site | Dependency map | Architecture files outside the import cluster |
| Plain-language report matching code comments | Documentation search | Crash-only report with no matching terms |

The authors found raw search stronger for "occurrence enumeration, new-file creation, and config edits". They conclude that "Raw search remains useful for exact strings and non-code artifacts, while structural views are most useful when code relations guide localization" ([Sepidband et al., 2026](https://arxiv.org/abs/2611.07286v1)).

More relations do not always help. Of the 18 SecBench cases the call-graph map solved and the hybrid map did not, the hybrid run edited the same file in 14 and still failed the patch. The authors read this as the extra context making the execution path less prominent ([Sepidband et al., 2026](https://arxiv.org/abs/2611.07286v1)).

## Why it works

The token saving comes from read displacement. In the paper's words, "the map returns relevant code bodies inline, so the agent treats them as already read and avoids many source-file reads" ([Sepidband et al., 2026](https://arxiv.org/abs/2611.07286v1)). On LinuxFLBench the baseline averaged 8.4 reads, 6.0 greps, and 9.5 shell calls per task. The map agents made 8.5 to 13.1 map calls and at most 1.1 native reads.

That saving lasts only while localization reads dominate the trajectory. After the crash frame or test target is found, the agent still has to read and edit. Map payloads then add to native browsing. On SecBench and SWT-bench, more instances used more tokens than fewer, except with the call graph on SWT-bench ([Sepidband et al., 2026](https://arxiv.org/abs/2611.07286v1)).

## When this backfires

- Writing decides the task. On SWT-bench the call graph lost 6.8 points, and every map used more tokens and more time ([Sepidband et al., 2026](https://arxiv.org/abs/2611.07286v1)).
- Latency is the budget. Wall time rose for every map on three of four benchmarks, up to 290 s against a 66 s baseline on SecBench ([Sepidband et al., 2026](https://arxiv.org/abs/2611.07286v1)).
- The target is easy to find. On easy fault-localization cases, map overhead was the main source of extra tokens. In one LinuxFLBench case the documentation map used 27.7 times the baseline's tokens on a file the report named outright ([Sepidband et al., 2026](https://arxiv.org/abs/2611.07286v1)).
- Fewer calls do not mean a lower bill. An independent practitioner test of the CodeGraph MCP server on the Hono repository cut tool calls by 55%, but cost rose 6.8%. On narrow lookups, cost rose 20–43%, because "each structural lookup loads a big chunk of graph context that costs more in cached tokens than the grep round-trips it replaces" ([Guo, 2026](https://dev.to/harrisonsec/i-tested-codegraph-on-hono-the-tool-call-savings-reproduce-the-cost-savings-dont-389p)). That test ran 4 repeats on one repository.
- The agent ignores an optional tool. A [deterministic anchoring](deterministic-anchoring.md) study reported that with an optional call-graph tool, "the agent typically relied on plain grep instead" ([Lin et al., 2026](https://arxiv.org/abs/2606.26979v2)). The Sepidband treatment added usage steering and, on repair, a hook that forced one map query before native reads. The authors state that reduced native reads "are not effects of the data structure alone" ([Sepidband et al., 2026](https://arxiv.org/abs/2611.07286v1)).

The evidence has limits. It covers one model (Haiku 4.5 at low effort) and one run per instance. Its token counts also exclude map construction and other one-time setup ([Sepidband et al., 2026](https://arxiv.org/abs/2611.07286v1)).

## Key Takeaways

- Attach a structural map server for bug localization; expect fewer tokens and slower runs.
- For repair, a map lowers token spend without moving resolution, so judge it on cost, not success.
- For test generation, start without a map: no view raised success by more than 3.1 points, and all cost more tokens.
- Pick a call graph when the prompt carries a stack trace, and documentation search when the report is in plain language.
- If you add a map tool, steer or hook the agent into using it, and measure cost per task rather than tool calls.

## Related

- [Repository Map Pattern](repository-map-pattern.md) — building a token-fitted AST map the agent reads up front
- [Deterministic Anchoring](deterministic-anchoring.md) — injecting static call-graph facts for run-to-run stability
- [Semantic Context Loading](semantic-context-loading.md) — querying code through language-server semantics
- [Repository-Level Retrieval for Code Generation](repository-level-retrieval-code-generation.md) — cross-file retrieval from dependency graphs and ASTs
- [Symbol Ranking for Agent File Pickers](symbol-ranked-file-picker.md) — ranking candidate files by the symbols they define
