---
title: "Request Shaping to Cut Wasted Agent Turns"
term: "Request Shaping"
description: "Naming the target, stating the stop condition, and bounding exploration cuts agent-side retrieval — but only until the agent has what it needs, after which more specification adds tokens without removing work."
tags:
  - token-engineering
  - cost-performance
  - claude
  - arxiv
aliases:
  - shaping requests to coding agents
  - prompt shape as a cost lever
applies_to: "claude-code@2.x"
last_reviewed: 2026-07-27
maturity: emerging
---

# Request Shaping to Cut Wasted Agent Turns

> Phrasing that replaces agent-side retrieval with prompt-side facts cuts turns and tokens; phrasing that only adds detail does not.

Request shaping pays when the words you add remove work the agent would otherwise do. Naming the file it must edit, stating the check that means "done", and bounding exploration each substitute a few prompt tokens for an unbounded number of retrieved ones. Adding constraints the agent already has does not, and on complex tasks it can make the output worse.

## When shaping pays

Shaping pays when the agent would otherwise search. Anthropic names the contrast directly: "Vague requests like 'improve this codebase' trigger broad scanning. Specific requests like 'add input validation to the login function in auth.ts' let Claude work efficiently with minimal file reads" ([Manage costs effectively](https://code.claude.com/docs/en/costs)).

It stops paying once the agent has enough to act. Beyond that point every added clause is tokens on every turn with no retrieval removed. The measured version of this line comes from a study of 60 requirements across three tasks and 8,400 model-and-prompt combinations. An optimizer that selected which requirements to state, rather than stating all of them, gained 3.8% accuracy while cutting token usage 43% against baseline prompts ([What Prompts Don't Say](https://arxiv.org/abs/2505.13360v3)). Selection is the lever, not volume.

## Four moves that replace retrieval

Name the target. Point at the file, function, or symbol instead of describing where it lives. Claude Code reads an `@`-referenced file before responding, and pasted images, given URLs, and piped data work the same way ([Best practices for Claude Code](https://code.claude.com/docs/en/best-practices)).

State the stop condition. Anthropic's framing: "Claude stops when the work looks done. Without a check it can run, 'looks done' is the only signal available, and you become the verification loop" ([Best practices](https://code.claude.com/docs/en/best-practices)). Their before-and-after pairs `"implement a function that validates email addresses"` with a version that lists the test cases and ends "run the tests after implementing". Each correction round you avoid is a full-context turn you do not pay for.

Bound exploration. Unscoped investigation is a named failure pattern: "You ask Claude to 'investigate' something without scoping it. Claude reads hundreds of files, filling the context." The documented fixes are to scope the investigation or push it into a [subagent](../tools/claude/sub-agents.md) whose reads never enter your window ([Best practices](https://code.claude.com/docs/en/best-practices)).

State the constraint the agent would otherwise discover by trial. Leaving a requirement implicit is fragile rather than free: models satisfy an unspecified requirement to better than 98% accuracy in only 41.1% of cases, and unspecified requirements are almost twice as likely to regress by more than 20% across a model update ([What Prompts Don't Say](https://arxiv.org/abs/2505.13360v3)).

## Why it works

The agentic loop is autoregressive over one growing context, so retrieval cost compounds. Anything the agent reads to resolve an under-specified request stays in the window, and "Claude Code sends your full conversation with every message" ([Manage costs effectively](https://code.claude.com/docs/en/costs)). An unscoped request is therefore multiplicative, not additive: it triggers file reads, those reads become permanent context, and every later turn re-pays for them.

Attention scarcity is the second half. Transformers require "every token to attend to every other token across the entire context. This results in n² pairwise relationships for n tokens", so "as the number of tokens in the context window increases, the model's ability to accurately recall information from that decreases" ([Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)). Anthropic frames the budget that follows as finding "the smallest possible set of high-signal tokens that maximize the likelihood of some desired outcome". Retrieval spends that budget on bytes you did not choose; the prompt spends it on bytes you did.

## When this backfires

- Exploratory work in unfamiliar code. Naming files you guessed at anchors the agent on the wrong ones. Anthropic carves this out: vague prompts are useful "when you're exploring and can afford to course-correct" ([Best practices](https://code.claude.com/docs/en/best-practices)).
- Tasks whose specification is already redundant. Across 10 models, removing a single explicit constraint cost 11.8% pass@1 on HumanEval but only 0.9% on LiveCodeBench, where descriptions, constraints, formats, and examples overlap ([When Prompt Under-Specification Improves Code Correctness](https://arxiv.org/abs/2604.24712v1)).
- Precise wording that primes the wrong solution. In the same study the fail-to-pass and pass-to-fail ratio was near balanced at 0.89 for under-specification, because "domain-specific vocabulary, identifier names, and constraint lines prime models toward memorized but incorrect solutions". Constraint removal fixed incorrect input parsing in 39% of the cases where it helped ([arxiv 2604.24712](https://arxiv.org/abs/2604.24712v1)).
- One-line changes. Front-loading has its own cost: "Plan mode is useful, but also adds overhead… If you could describe the diff in one sentence, skip the plan" ([Best practices](https://code.claude.com/docs/en/best-practices)).
- Sessions dominated by a different driver. Opus left as the default, a session never cleared, repeated cache misses, or agent teams that "use approximately 7x more tokens than standard sessions when teammates run in plan mode" all outweigh phrasing ([Manage costs effectively](https://code.claude.com/docs/en/costs)). Measure before you tune wording — see [Token-Cost Profiling for Always-On Workflows](token-cost-profiling-always-on-workflows.md).

## Example

Two requests for the same fix, taken from Anthropic's documented before-and-after pair ([Best practices for Claude Code](https://code.claude.com/docs/en/best-practices)).

Before, the agent must locate the bug and decide when it is fixed:

```text
fix the login bug
```

After, with the symptom, likely location, and stop condition supplied:

```text
users report that login fails after session timeout. check the auth flow
in src/auth/, especially token refresh. write a failing test that
reproduces the issue, then fix it
```

The second request removes three units of agent work: the search for which subsystem owns login, the guess at which failure mode users hit, and the judgment call about whether the fix landed. It costs two extra sentences. The first request pays for whatever scan of `src/` the agent chooses, keeps that scan in context for the rest of the session, and leaves you to notice if the fix is wrong.

Note what the second version does not do. It does not restate the project's test framework, naming conventions, or error-handling rules — those already reach the agent through CLAUDE.md, which Claude Code loads at the start of every conversation ([Best practices](https://code.claude.com/docs/en/best-practices)). Repeating them per request is the added-detail half of shaping, and it buys nothing.

## Key Takeaways

- Shape a request to remove agent-side retrieval, not to add detail — detail the agent already has costs tokens on every turn
- Name the target, state the stop condition, bound exploration, and state constraints the agent would otherwise find by trial
- Retrieval cost compounds because the full conversation is re-sent every turn, and attention degrades as the window grows ([Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents))
- Selecting which requirements to state beat stating all of them by 3.8% accuracy at 43% fewer tokens ([What Prompts Don't Say](https://arxiv.org/abs/2505.13360v3))
- On richly-specified tasks, removing a constraint cost only 0.9% pass@1 and helped about as often as it hurt ([arxiv 2604.24712](https://arxiv.org/abs/2604.24712v1))
- Check the bigger levers first — model choice, session hygiene, and team size move more than phrasing

## Related

- [Context Priming: Pre-Loading Files for AI Agent Tasks](../context-engineering/context-priming.md) — the harness-side counterpart: load files before the task instead of naming them in the request
- [Prompt Compression](../context-engineering/prompt-compression.md) — raising signal per token in a fixed instruction set, rather than deciding what the request must carry
- [Context Budget Allocation](../context-engineering/context-budget-allocation.md) — the budget this technique spends against, across all context sources
- [Token Preservation Backfire](../patterns/anti-patterns/token-preservation-backfire.md) — the failure mode when trimming the request goes too far
- [Token-Cost Profiling and Reduction for Always-On Agentic Workflows](token-cost-profiling-always-on-workflows.md) — measure where spend actually goes before tuning phrasing
- [Probe-Run Calibration for Predicting Agent Token Spend](probe-run-cost-calibration.md) — how much your own task's cost moves with phrasing, measured rather than assumed
- [Deliberation-Inducing Cues That Multiply Reasoning Cost](../patterns/anti-patterns/deliberation-inducing-prompt-cues.md) — the phrasings that inflate reasoning tokens rather than retrieval turns
