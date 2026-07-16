---
title: "Match Tool Instructions to the Agent Workflow"
term: "Workflow-Matched Instructions"
description: "Better tools do not improve an agent unless the prompt encodes how the task's workflow gathers information — match instructions to the workflow, not the tools."
aliases:
  - "Workflow-Matched Tool Instructions"
  - "Workflow-Matched Instructions"
tags:
  - instructions
  - code-review
  - cost-performance
  - tool-agnostic
last_reviewed: 2026-07-16
maturity: emerging
---

# Match Tool Instructions to the Agent Workflow

> Swapping in better tools does not improve an agent unless its instructions encode how the task's workflow actually gathers information.

Tool quality does not transfer to agent quality on its own. An agent's behavior comes from how its instructions tell it to use the tools, so upgrading the tools while leaving the prompt unchanged can make the agent worse. Match the instructions to how the task is actually done, then let the better tools carry it.

## Better tools, worse reviews

GitHub migrated Copilot code review to the shared Unix-style toolset that powers the Copilot CLI — `grep`, `glob`, and `view`, replacing older custom tools. The tools were better maintained and more capable, but the benchmark result was negative: "the cost of reviews was higher and fewer issues were being caught." [Source: [Better tools made Copilot code review worse](https://github.blog/ai-and-ml/github-copilot/better-tools-made-copilot-code-review-worse-heres-how-we-actually-improved-it/)]

The tools were not the problem. The instructions were: "The instructions were giving the agent the wrong instincts to do an efficient and effective review." The prompts, tuned for a CLI assistant, told the agent to explore broadly — "search broadly, guess likely paths, read broadly, find more things to search, and carry that extra context forward." That browse-first loop suited open-ended CLI work but not a review that starts from a diff.

The fix rewrote the prompt to a diff-anchored, narrow-first workflow: "Start from the diff. Narrow first with `grep` and `glob`; read exact evidence with `view`." That shifted the agent "from 'browse, read, search again' to 'ask, narrow, read, decide,'" and cut "roughly 20% lower average review cost" while "maintaining the same review quality." [Source: [Better tools made Copilot code review worse](https://github.blog/ai-and-ml/github-copilot/better-tools-made-copilot-code-review-worse-heres-how-we-actually-improved-it/)]

## Why it works

Generic explore-broadly instructions make the agent accumulate context the task does not need. It searches wide, guesses paths, reads broadly, and carries that context forward, spending tokens and diluting attention without catching more issues. Workflow-matched instructions anchor the agent to the task's real information path, so tool calls land on relevant evidence instead of expanding the search. GitHub's traces showed the agent "making a similar number of tool calls, but spending more of them on relevant evidence instead of repeatedly expanding the search." [Source: [Better tools made Copilot code review worse](https://github.blog/ai-and-ml/github-copilot/better-tools-made-copilot-code-review-worse-heres-how-we-actually-improved-it/)] A better `grep` does not change when the agent decides to grep versus read — only the instructions encode that decision.

This is the same lever as [tool minimalism and high-level prompting](../tool-engineering/tool-minimalism.md), from the opposite direction: there the fix was fewer tools, here the tools were better and more numerous, and the lever was still the instructions, not the tool count.

## Applying it

- Encode the task's information path, not a generic exploration loop. For diff-anchored review that means narrow-first — search with `grep`/`glob`, then read with `view` — because the diff already names what to investigate.
- Read tool traces, not just final scores. The regression was invisible in end metrics and only showed up per call: did the agent narrow first or read broadly, did it batch independent searches, did it read only when it had a reason. [Source: [Better tools made Copilot code review worse](https://github.blog/ai-and-ml/github-copilot/better-tools-made-copilot-code-review-worse-heres-how-we-actually-improved-it/)]
- Re-tune instructions when you swap tools. Shared tools "scale when the instructions and benchmarks match the job" — inherited prompts carry the instincts of the product they were written for.

## When this backfires

Matching the workflow does not always mean narrowing. The technique fails when applied as a fixed rule rather than a fit to the task:

- Exploratory workflows want the opposite. A CLI assistant has "no single diff anchor" and users who "may change direction over multiple turns," so broad exploration is part of the job. [Source: [Better tools made Copilot code review worse](https://github.blog/ai-and-ml/github-copilot/better-tools-made-copilot-code-review-worse-heres-how-we-actually-improved-it/)] The same `grep`, `glob`, and `view` tools want wider instructions here, not narrower ones.
- No trace or eval infrastructure hides the mismatch. The regression never appeared in final metrics; a team without per-tool traces cannot detect the mismatch or confirm the fix held quality.
- Over-fitting to one task shape reintroduces brittleness. Encoding a rigid step-by-step sequence for a single workflow variant is the failure [system prompt altitude](system-prompt-altitude.md) warns against — match the shape of the workflow, not one instance of it.

## Example

**Before** — CLI-tuned instructions inside a code-review agent:

```text
Explore the repository to understand the change. Search broadly for
related code, read the files you find, and follow references until you
have enough context to review the pull request.
```

**After** — instructions matched to the review workflow:

```text
Start from the diff. Formulate specific review questions from the changed
lines. Narrow first with grep and glob to locate evidence; read exact
line ranges with view only once you know what to read. Batch independent
searches. Do not load context the diff does not point you toward.
```

The tools are identical in both versions. Only the encoded workflow changed — and that change cut review cost about 20% at equal quality. [Source: [Better tools made Copilot code review worse](https://github.blog/ai-and-ml/github-copilot/better-tools-made-copilot-code-review-worse-heres-how-we-actually-improved-it/)]

## Key Takeaways

- Tool quality does not transfer to agent quality — behavior comes from how the instructions tell the agent to use the tools.
- Better tools with workflow-mismatched instructions can raise cost and lower detection at the same time.
- Match instructions to the task's real information path: diff-anchored review wants narrow-first search then read; an exploratory assistant wants broad exploration.
- Tool traces, not final metrics, reveal the mismatch — inspect whether the agent narrows before it reads.
- Re-tune instructions whenever you swap the toolset; inherited prompts carry the instincts of the product they were written for.

## Related

- [Tool Minimalism and High-Level Prompting](../tool-engineering/tool-minimalism.md) — the same instructions-over-tools lever, from the fewer-tools direction
- [Agentic Code Review Architecture With Tool-Calling](../code-review/agentic-code-review-architecture.md) — the tool-calling review architecture this regression occurred within
- [System Prompt Altitude: Specific Without Being Brittle](system-prompt-altitude.md) — how to match a workflow's shape without over-fitting one variant
- [Diff-Based Review Over Output Review](../code-review/diff-based-review.md) — why the diff is the right anchor for review instructions
- [Prompt-Rewrite Discipline on Cross-Generation Model Migration](prompt-rewrite-on-cross-generation-migration.md) — re-tuning inherited prompts, including tool descriptions, when the substrate changes
