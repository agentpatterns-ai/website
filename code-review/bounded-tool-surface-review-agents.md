---
title: "Bounded Tool Surfaces for Code Review Agents"
term: "Bounded Tool Surface"
description: "Cap what each review tool can return and make file-to-criteria dispatch deterministic — a precision and cost win that costs recall, so apply it where a human reads the comments."
aliases:
  - bounded-output review tools
  - constrained tool surface review
  - deterministic review dispatch
tags:
  - code-review
  - testing-verification
  - cost-performance
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-11
maturity: emerging
---

# Bounded Tool Surfaces for Code Review Agents

> Capping what a review agent's tools can return, and fixing which files get which criteria, raises review precision and cuts cost while lowering recall.

Give a review agent a general-purpose shell and it will read as much of the repository as it can reach. That freedom is where precision goes. Replace the shell with tools that each return a bounded amount of text, and decide outside the model which files get reviewed against which criteria, and the result is measurable and lopsided.

## When to bound the reviewer

Bound the tool surface when a human is the first reader of the comments and the review budget is real. On AACR-Bench, a bounded-tool reviewer scored 33.90% precision against 7.23% for the same Claude-4.6-Opus backend driven by Claude Code, at 385K tokens versus 5,664K and 1m23s versus 13m06s ([arXiv:2608.09290v1](https://arxiv.org/abs/2608.09290v1)). Across six backends the paper reports 5–15 times fewer tokens at 1.3–2.2 times the SEM-F1 score ([arXiv:2608.09290v1](https://arxiv.org/abs/2608.09290v1)).

Recall moves the other way. The same comparison gives recall of 20.00% for the bounded system against 28.90% for Claude Code, and that ordering holds in most of the six backends tested ([arXiv:2608.09290v1](https://arxiv.org/abs/2608.09290v1)). So this is the right architecture when a wrong comment is the expensive error, and the wrong one when a missed defect is.

## The three seams to make deterministic

Determinism goes at chosen points in the pipeline, leaving the judgement inside each file probabilistic.

### Dispatch

Resolve review criteria from a fixed precedence chain (ad-hoc, project-level, user-global, built-in) and assign each changed file to its criteria outside the model, filtering by extension, include and exclude patterns, and size. Files above 80% of the context window are dropped rather than partially read. The same pull request then produces the same file and criterion pairs on every run ([arXiv:2608.09290v1](https://arxiv.org/abs/2608.09290v1)).

### Tool output

Each per-file subagent gets six tools with hard ceilings: `file_read` at 500 lines per call, `file_find` at 100 results, `code_search` at 100 matches with a 10-second timeout, plus a diff reader, a comment writer, and a termination signal. The loop stops after 30 iterations ([arXiv:2608.09290v1](https://arxiv.org/abs/2608.09290v1)). The same narrowing applied to a coding agent is a [single execute_code tool](../tool-engineering/restrict-coding-agent-to-execute-code.md), where solve rate holds and only cost moves.

### Comment filtering

A separate reflector reads each proposed comment against the diff alone, without the exploration history, and deletes any comment the diff contradicts. It keeps comments that reference context beyond the diff, and it never writes new ones ([arXiv:2608.09290v1](https://arxiv.org/abs/2608.09290v1)).

## Why it works

Unbounded tool output makes each observation an unpredictable size, so context fills at a rate the loop cannot plan for and quality falls off inside the [dumb zone](../context-engineering/context-window-dumb-zone.md). The loop compresses, and the model starts reasoning about a summary of code it no longer holds, which is where comments stop being grounded in the file. The Claude Code baseline's 7.23% precision after 5,664K tokens is that failure priced out ([arXiv:2608.09290v1](https://arxiv.org/abs/2608.09290v1)). Capping each call makes per-turn context growth predictable, so a 30-iteration loop finishes with the actual file text still in context. Because the reflector sees only the diff and can only delete, a comment invented from context that was already dropped gets falsified instead of co-signed.

## When this backfires

- Cross-service defects. Evidence living past 100 search matches or 500 read lines is unreachable by construction. The recall drop is this cost showing up in the numbers.
- Recall-critical passes. Pre-release security audits price a miss far above a false positive. Augment Code argues that once software rather than a person reads the first pass, false positives get cheap while missed bugs still reach production, which makes recall the stronger goal at the scan layer ([Augment Code — Deep Code Review](https://www.augmentcode.com/guides/deep-code-review-recall-vs-precision)).
- Repositories with no written criteria. With nothing at the ad-hoc, project, or user tiers, dispatch falls back to built-in rules. The determinism survives; the relevance does not.
- Large files. A file over 80% of the context window is excluded outright, so a monolith gets zero coverage rather than partial coverage.
- Small diffs. Per-file fan-out plus a filtering pass is overhead a one-file typo never earns back.

The largest deployed counter-example runs the other way. GitHub moved Copilot code review to an exploratory agentic architecture and reports an [8.1% increase in positive developer feedback](https://github.blog/ai-and-ml/github-copilot/60-million-copilot-code-reviews-and-counting/) despite slower reviews. The OpenCodeReview paper also publishes no ablation ([arXiv:2608.09290v1](https://arxiv.org/abs/2608.09290v1)), so the credit split between bounded tools and the delete-only filter is unmeasured.

## Example

A system built on this shape exposes no shell. Rendering the paper's stated ceilings as a tool schema ([arXiv:2608.09290v1](https://arxiv.org/abs/2608.09290v1)):

```json
{
  "file_read":      { "args": ["path", "start_line", "end_line"], "max_lines": 500 },
  "file_find":      { "args": ["glob"],    "max_results": 100 },
  "code_search":    { "args": ["pattern"], "max_matches": 100, "timeout_s": 10 },
  "file_read_diff": { "args": ["path"],    "note": "precomputed diff of another changed file" },
  "code_comment":   { "args": ["path", "line", "body"] },
  "task_done":      { "args": [] }
}
```

A pull request touching twelve files fans out to twelve subagents. Each one receives its file plus the criteria the precedence chain resolved for that path, runs at most 30 tool calls, and emits comments through `code_comment`. Every comment then goes to the reflector with the diff and nothing else; the reflector drops the ones the diff refutes, and what remains is posted.

## Key Takeaways

- Bounding tool output is a precision and cost lever paid for in recall, so check which error your review gate optimizes against before adopting it
- Put determinism at the dispatch and filtering seams, and leave the per-file judgement to the model
- Concrete ceilings to start from: 500 lines per read, 100 search matches, a 10-second search timeout, 30 loop iterations
- A comment filter that can only delete, and that sees only the diff, removes hallucinated findings without adding new ones
- The evidence is a single preprint measuring all three seams together with no ablation, so treat the component split as unproven

## Related

- [Agentic Code Review Architecture](agentic-code-review-architecture.md) — the case for giving the reviewer tools at all; this page supplies the missing ceiling on how wide to open them
- [Reproduce-Before-Report Verification Gate](reproduce-before-report-verification-gate.md) — a verifier that builds evidence for a finding, where the reflector here only falsifies against the diff
- [Signal Over Volume in AI Review](signal-over-volume-in-ai-review.md) — the outcome this architecture buys, argued from deployment data
- [Tunable Effort Levels for Code Review Agents](tunable-review-effort.md) — exposing review depth as a per-PR dial instead of a fixed ceiling
- [Deterministic Guardrails Around Probabilistic Agents](../verification/deterministic-guardrails.md) — the same instinct applied to agent output rather than the agent's tool surface
