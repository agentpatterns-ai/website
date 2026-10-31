---
title: "Path-Only File Mentions: Deferring @ Expansion"
term: "Path-Only File Mentions"
description: "Claude Code 2.1.299 can hand Claude the paths of @ file mentions instead of their contents. The gain is window occupancy rather than billing, and a skipped read reports nothing."
aliases:
  - deferred file mention expansion
  - CLAUDE_CODE_DISABLE_FILE_MENTIONS
  - path-only @ mentions
tags:
  - context-engineering
  - claude
  - arxiv
last_reviewed: 2026-10-17
maturity: emerging
---

# Path-Only File Mentions: Deferring @ Expansion

> Handing Claude the path of an `@` file mention instead of the file's contents defers the load to the agent's own read decision.

Consider switching expansion off when large mentioned files crowd later evidence out of a long session. First check whether you can detect missed reads in the output. Leave expansion on if you cannot. A mention is a human saying a file matters, and the flag converts that certainty into a decision the agent can get wrong.

Claude Code 2.1.299 added the control ([Claude Code changelog, October 14, 2026](https://code.claude.com/docs/en/changelog#2-1-299)). Setting `CLAUDE_CODE_DISABLE_FILE_MENTIONS` to `1` stops the harness "from expanding `@` mentions of files and directories. Claude instead gets the mentioned paths with a note to read them using its file tools" ([Claude Code environment variables](https://code.claude.com/docs/en/env-vars)). Two constraints come with it. The variable is "Ignored in project and local settings", so a repository cannot turn it on for contributors, and it "Requires Claude Code v2.1.299 or later".

| Mode | What reaches the model | How to get it |
|---|---|---|
| Default | The file's contents, expanded at prompt-build time | Set nothing |
| Path plus instruction | The mentioned paths and a note to read them | `CLAUDE_CODE_DISABLE_FILE_MENTIONS=1` |
| Path as text | The mention as plain text, with no expansion | `CLAUDE_CODE_DISABLE_ATTACHMENTS=1` |

The third mode comes from a different variable, which disables "attachment processing" so that mentions "are sent as plain text instead of being expanded into file content" ([Claude Code environment variables](https://code.claude.com/docs/en/env-vars)). The documentation describes plain-text mentions without specifying whether this mode adds a read instruction.

## Why it works

The window is an attention budget before it is a bill. Anthropic states the constraint plainly: "Every new token introduced depletes this budget by some amount, increasing the need to carefully curate the tokens available to the LLM" ([Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)). Du and colleagues measured the cost across 5 models on math, question answering and coding, with retrieval held perfect: "even when models can perfectly retrieve all relevant information, their performance still degrades substantially (13.9%–85%) as input length increases but remains well within the models' claimed lengths" ([Du et al., arXiv:2510.05381v1](https://arxiv.org/abs/2510.05381v1)). The drop survived replacing the irrelevant tokens with whitespace, so inert length is still costly length.

A path is a short string, and moving its expansion to tool-call time means the file occupies the window only once the agent commits to it. Claude Code already works this way elsewhere: "CLAUDE.md files are naively dropped into context up front, while primitives like glob and grep allow it to navigate its environment and retrieve files just-in-time" ([Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)). The flag extends it to the one load a person triggers.

## When this backfires

- The mention was small and deliberate. Fetching a file the user named on purpose costs a round trip and returns the bytes expansion would have supplied. Anthropic names that cost itself: "runtime exploration is slower than retrieving pre-computed data" ([Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).
- The agent never reads the path. Agent Retrieval Bench logged agent trajectories, and even with interactive exploration "the logged agents never touch any gold file on 35.2% of OpenAI strict-context samples and 27.2–29.3% of Codex samples" ([Qin and Xie, arXiv:2607.24882v1](https://arxiv.org/abs/2607.24882v1)). In its 45-sample closed-tool pilot, preloading the gold bytes raised any-gold contact from 0.5111 to 1.0000 and "raises final File F1 by 0.3115". A read the agent skips produces an answer, not an error.
- The window is not your constraint. Anthropic prices reads of a cached prompt prefix at "0.1 times the base input tokens price", and 0.05x on Claude Opus 5.5 and Claude Sonnet 5.5 ([Anthropic prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)). Cache hits reduce the repeat input charge, so the accuracy argument has to carry the decision.
- The mention carries the task statement. A spec referenced by path is the material the model works from, so a skipped read loses requirements rather than background.
- Several mentions, and the comparison is the job. Read one path and not the other, and the output is half grounded with nothing marking which half.

Anthropic declines to settle the choice in general: "the most effective agents might employ a hybrid strategy, retrieving some data up front for speed, and pursuing further autonomous exploration at its discretion. The decision boundary for the 'right' level of autonomy depends on the task" ([Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).

## Key Takeaways

- The flag buys window occupancy, so check your cache-hit rate before reaching for it. On a healthy cache the resident bytes were never costing full price each turn.
- Measure the sizes of the files your team actually mentions and their contribution to window occupancy.
- Account for retrieval latency when you expect the agent to read every mentioned file. Deferred expansion adds a tool call before those bytes arrive.
- Measure the skip, because nothing else will. Count the turns where a mentioned path never appears in a file-read call.
- Configure the variable in user or managed settings on v2.1.299 or later. Claude Code ignores it in project and local settings.

## Related

- [Static-Context Tool Residence: Two Overrides on Hit Rate](static-context-tool-residence.md) — the same preload-or-fetch decision applied to tool definitions
- [Choosing a Skill Loading Method for Agents](skill-loading-method-selection.md) — the decision applied to skills, where the harness picks rather than the person
- [Prompt Caching: Architectural Discipline for Agents](prompt-caching-architectural-discipline.md) — why the repeat cost of a resident mention is smaller than it looks
- [Discoverable vs Non-Discoverable Context for Agents](discoverable-vs-nondiscoverable-context.md) — the test for what belongs in context up front
- [@import Composition Pattern for Agent Instruction Files](../instructions/import-composition-pattern.md) — the other `@path` surface, expanded at session start rather than per prompt
