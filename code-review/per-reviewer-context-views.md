---
title: "Per-Reviewer Context Views for Code Review Agents"
term: "Per-Reviewer Context Views"
description: "A context builder composes a dimension-scoped context prompt for each specialized review agent from repository structure and a dependency graph, instead of handing every reviewer the same diff."
tags:
  - code-review
  - multi-agent
  - arxiv
  - tool-agnostic
aliases:
  - "context builder for review agents"
  - "dimension-scoped review context"
last_reviewed: 2026-09-17
maturity: emerging
---

# Per-Reviewer Context Views for Code Review Agents

> A context builder gives each specialized review agent a view scoped to its own dimension, built from repository structure rather than the diff alone.

Most multi-agent review designs split the reviewers but share one context, so every agent gets the same diff. The per-reviewer arrangement puts a context builder in front of the agents. It collects the diff, the changed files, repository metadata, and structural relationships from a dependency index. Each reviewer then gets its own context prompt carrying only the slice it needs. A deployment at Ericsson built its reviewers this way. The developers who wrote the code confirmed 197 of 206 findings correct, an accuracy the authors report as approximately 96% ([arXiv:2609.15877v1](https://arxiv.org/abs/2609.15877v1)).

## When it applies

That result comes from one company, one language, and seven commits, so treat the following as entry conditions rather than a default.

- You already run more than one specialized reviewer. With one reviewer there is nothing to differentiate and the builder is overhead. [Committee Review Pattern](committee-review-pattern.md) covers the specialization layer this sits under.
- You have a structural index of the repository, or will build one. Ericsson's system queried a code knowledge graph of file-level imports, symbol definitions, library usage, and per-file fan-in/fan-out, exposed as an MCP server next to a GitLab one ([arXiv:2609.15877v1](https://arxiv.org/abs/2609.15877v1)). Without an index the builder can only forward the diff.
- Your reviewers have different information needs. At Ericsson the readability agent focused on local code structure and formatting, while the maintainability agent also received dependency and structural relationships ([arXiv:2609.15877v1](https://arxiv.org/abs/2609.15877v1)). Where two reviewers want the same context, merge them.

## Why it works

A reviewer holding only a diff has to guess at what the diff hides, starting with call sites and dependents. A plausible guess is what a hallucinated finding is made of. Supplying the surrounding structure before the agent reasons removes the guess, and the study's authors attribute their 4% incorrect rate to it: "Supplying agents with repository-specific information, rather than code change alone, appears to constrain their reasoning to what actually holds in the surrounding system" ([arXiv:2609.15877v1](https://arxiv.org/abs/2609.15877v1)).

Scoping the view per dimension does a second job. The authors describe the selective construction as aiming to "reduce prompt complexity while preserving the contextual information most relevant to each review dimension" ([arXiv:2609.15877v1](https://arxiv.org/abs/2609.15877v1)), so a maintainability agent's dependency graph does not compete for a readability agent's attention. Independent support for the first half: adding problem descriptions raised GPT-4o's code-correctness classification to 68.50% and Gemini 2.0 Flash's to 63.89%, and without them "performance declined" ([arXiv:2505.20206v1](https://arxiv.org/abs/2505.20206v1)).

## Rate correctness and importance separately

Accuracy alone will not tell you whether the context work paid off. Ericsson's five developer raters scored every finding twice, and the second score is the informative one: of the 197 correct findings, 65 (33%) were severe issues that must be fixed, 70 (36%) were issues that should be fixed, and 62 (31%) were minor or low-impact suggestions ([arXiv:2609.15877v1](https://arxiv.org/abs/2609.15877v1)). The same 206 findings support both "96% accurate" and "roughly a third of what it correctly reports is noise".

Rate a sample of your own reviewer's output the same way before tuning anything. A reviewer built to find every issue can post a low signal-to-noise ratio that resolution rates hide, a trade-off between issue resolution and spurious findings ([arXiv:2603.11078v1](https://arxiv.org/abs/2603.11078v1)).

## When this backfires

- No structural index exists. The builder degrades to forwarding the diff while still costing an orchestration component and a prompt-assembly step per agent. A code knowledge graph has to be built, deployed, and kept current.
- The orchestrator mis-assembles a view. "The orchestration is a single point of failure, as an error at any stage propagates to the final review, even when the individual agents reason correctly" ([arXiv:2609.15877v1](https://arxiv.org/abs/2609.15877v1)). A wrong context slice fails silently, because the agent reasons fluently over it either way.
- Your team has no triage habit for minor findings. Ericsson's seven commits produced 206 findings, near 30 per commit. Context improves what a finding says about the code, not whether anyone wanted it.
- The finding is correct and the choice was deliberate. Intentional design decisions are one of the two most prevalent reasons agent review comments go unresolved ([arXiv:2607.21997v2](https://arxiv.org/abs/2607.21997v2)). Repository context does not teach a reviewer which trade-offs the team already settled.
- You are outside the evaluated envelope. The authors ran no ablation, say the observations "provide feasibility evidence rather than controlled comparative proof", and note that single-LLM results may not generalize to other organizations or languages ([arXiv:2609.15877v1](https://arxiv.org/abs/2609.15877v1)).

## Example

Ericsson's builder fed two of its four reviewers different views of the same commit ([arXiv:2609.15877v1](https://arxiv.org/abs/2609.15877v1)):

```text
readability agent      <- diff, changed files, repo metadata
maintainability agent  <- diff, changed files, repo metadata,
                          dependency and structural relationships
```

Each agent carried its own prompt, tool permissions, and antipattern catalog as a skill document, and the four ran in parallel as sub-agents, each receiving only the path to the shared context document and the source files on disk. Every agent emitted findings in one fixed four-field shape:

```text
Antipattern Name | Location | Problem Description | Fix Suggestion
```

The orchestrator aggregated the four outputs into a single report. The authors call the output format part of the design rather than a presentation detail, because constraining findings to a strict format "made a systematic assessment of 206 issues feasible" ([arXiv:2609.15877v1](https://arxiv.org/abs/2609.15877v1)).

## Key Takeaways

- Split the context as well as the reviewers; a shared diff wastes the specialization you already paid for.
- The builder needs a structural index to be worth running. Budget for the graph, the server, and keeping both current.
- Treat the orchestrator as the risk. A mis-assembled context view produces fluent findings about a system that does not exist.
- Ask two questions of every sampled finding: is it true, and would you fix it. A 96% on the first says nothing about the second.
- Assume deliberate design choices will still get flagged, and route those to a dismissal path rather than a prompt fix.

## Related

- [Committee Review Pattern](committee-review-pattern.md) — the reviewer-specialization layer this context arrangement sits under
- [Agentic Code Review Architecture](agentic-code-review-architecture.md) — the pull-based alternative, where the reviewer fetches its own context instead of receiving a composed view
- [Bounded Tool Surfaces for Code Review Agents](bounded-tool-surface-review-agents.md) — capping what each review tool returns, the precision-for-recall trade on the same axis
- [Signal Over Volume in AI Review](signal-over-volume-in-ai-review.md) — what to do with the minor findings the importance axis exposes
- [Agentic Review Comment Acceptance](agentic-review-comment-acceptance.md) — acceptance measured in the wild, against which a 96% in-house accuracy figure should be read
