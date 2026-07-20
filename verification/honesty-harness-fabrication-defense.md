---
title: "Defense-in-Depth Against Coding Agent Fabrication (Honesty Harness)"
term: "Defense-in-Depth Against Coding Agent Fabrication"
description: "Four uncorrelated layers that reduce coding-agent fabrication: instruction-level honesty rules, verify-before-write, real-time hooks that feed output back, and a fact-checker subagent with external tools."
tags:
  - testing-verification
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - fabrication harness
  - layered defense against agent hallucination
last_reviewed: 2026-06-07
maturity: established
---

# Defense-in-Depth Against Coding Agent Fabrication (Honesty Harness)

> Four uncorrelated checks — honesty rules, verify-before-write, hooks that feed output back, and an external-tool fact-checker — make coding-agent fabrication rare.

## When the four-layer harness pays off

The harness adds setup, latency, and operational surface. It earns that cost only under specific conditions:

- The model sits in the fabrication-vulnerable mid-band. Code LLMs hallucinate packages in roughly 5.2% of commercial generations and 21.7% of open-source generations across 576,000 prompts ([Spracklen et al., 2024 — arXiv:2406.10279](https://arxiv.org/abs/2406.10279)). Frontier models verify internally, so the harness adds cost without benefit there, just as [premature completion mitigations do](../patterns/anti-patterns/premature-completion.md).
- The codebase is large enough that a full CI run is slower than per-edit checks. Layer 3 only beats "trust the model, verify in CI" when each verification round is cheap relative to the round-trip cost.
- Both training and human reaction support honest abstention. Standard binary scoring "rewards answering over honestly expressing uncertainty" ([Wen et al., 2024 — arXiv:2407.18418](https://arxiv.org/html/2407.18418v2)), and punitive responses to "I don't know" re-train confident guessing within the session.
- A fact-checker subagent can hold at least one external oracle: an LSP, a type checker, a doc lookup, or test execution. Without one, intrinsic self-correction degrades performance ([Huang et al., 2023 — arXiv:2310.01798](https://arxiv.org/abs/2310.01798)).

Outside these conditions, upgrading the model or relying on CI catches more fabrication for less work.

## Layer 1 — honesty rules in instructions

Place "verify before claiming a symbol exists", "say I haven't verified this", and "don't claim build or test success you didn't run" inside the first ~50 lines of the instruction file. Anthropic's own docs warn that "bloated CLAUDE.md files cause Claude to ignore your actual instructions" ([Best practices for Claude Code](https://code.claude.com/docs/en/best-practices)). Use emphasis ("IMPORTANT", "YOU MUST") sparingly. It costs attention budget, and over-use cancels the signal.

## Layer 2 — verify before write

Read the definition, grep the symbol, or check the dependency manifest before using it. Mark skipped verification inline with an `UNVERIFIED:` comment so reviewers can grep for it. Prefer plan mode for multi-file work — Anthropic recommends planning when "the change modifies multiple files" but explicitly skipping it when "you could describe the diff in one sentence."

LSP integration converts symbol existence from a probabilistic guess into a deterministic lookup, the same shift behind [phantom symbol detection](phantom-symbol-detection.md). Grep handles broad exploration, and LSP handles symbol-level confirmation. Most production coding agents have converged on this layered retrieval pattern.

## Layer 3 — real-time hooks that feed output back

Run the type-checker and linter on `PostToolUse`, and run tests on `Stop`. The load-bearing detail is that hook output must flow back into the session so the agent sees the failure and self-corrects. Anthropic's docs describe the closed loop directly: "Claude does the work, runs the check, reads the result, and iterates until the check passes" ([Best practices](https://code.claude.com/docs/en/best-practices)). Hooks that log silently to a file instead of stderr defeat the layer.

Implement the gate as a hook, not a prompt instruction. Prompts compete for attention as context fills, while hooks execute at the system level regardless of what the model remembers — the mechanism documented in [Pre-Completion Checklists](pre-completion-checklists.md). Set a maximum-block count. Anthropic's own Stop hook ends the turn after 8 consecutive blocks to avoid the over-verification spiral.

## Layer 4 — independent fact-checker subagent

A read-only reviewer in a fresh context examines the diff before commit. The independence is structural: Anthropic notes that a subagent reviewer "sees only the diff and the criteria you give it, not the reasoning that produced the change, so it evaluates the result on its own terms" ([Best practices](https://code.claude.com/docs/en/best-practices)).

The reviewer must hold external tools. Intrinsic self-correction — re-reasoning without an oracle — overturns 21.9% of correct GPT-4o code solutions and 28.3% of correct GPT-3.5 solutions to wrong answers ([Liu et al., 2024 — arXiv:2412.14959](https://arxiv.org/abs/2412.14959)). A fact-checker without LSP, doc lookup, or test execution shares the original agent's prior and either rubber-stamps fabrications or invents new ones.

Constrain the reviewer to correctness gaps. Anthropic's caution is explicit: "A reviewer prompted to find gaps will usually report some, even when the work is sound, because that is what it was asked to do… tell the reviewer to flag only gaps that affect correctness or the stated requirements."

## Why it works

The four layers catch different fabrication classes through different signals, so an error must survive uncorrelated checks to reach the commit. Layer 1 shifts the prior over the agent's next token by surfacing verify-or-decline early in the system prompt — Claude's training puts honesty as "a core aspect of Claude's ethical character" ([Anthropic, Claude's Constitution](https://www.anthropic.com/constitution)), and the placement effect amplifies it. Layer 2 displaces the fabricating computation with a deterministic lookup before the symbol enters generated output. Layer 3 routes type-checker and test output back into the LLM's reading context, so the next token is conditioned on real failure text. Layer 4 uses fresh-context independence plus external tools to catch what the first three missed.

The harness is risk reduction, not elimination. LangChain reported moving Terminal Bench 2.0 from 52.8% to 66.5% with self-verification bundled into other harness changes ([LangChain, 2025](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)) — a large lift, far from zero failures.

## Signals it is working

- The agent asks before adding dependencies instead of importing speculatively
- Code comments cite `file:line` for existing definitions, not paraphrases
- The type checker and linter stop surfacing fabrications because Layer 3 catches them inline
- The fact-checker subagent reports specific symbol-existence or test-execution failures, not stylistic preferences

## When this backfires

- Strong-model deployments: frontier models (Claude Opus 4.6, GPT-5) show near-zero premature termination and lower hallucination rates, so Layer 3 and Layer 4 add cost without measurable benefit ([Premature Completion](../patterns/anti-patterns/premature-completion.md)).
- Overloaded Layer 1: a CLAUDE.md past the ~150 instruction ceiling drops compliance across all rules, including the honesty ones. Honest abstention has to compete with style, workflow, and project conventions for attention.
- Silent Layer 3: hook output that writes to a log file instead of stderr never enters the session. The agent never sees the failure and never self-corrects.
- Pure-reasoning Layer 4: a fact-checker without LSP, type checker, doc lookup, or test execution re-reasons against the draft and overturns correct code 22–28% of the time ([Liu et al., 2024](https://arxiv.org/abs/2412.14959)).
- Layer 4 scope creep: a reviewer trained for thoroughness flags gaps that do not affect correctness, so the implementing session burns turns chasing them and may regress (Anthropic explicit warning).
- Layer 2 over-applied to trivial edits: requiring "read the definition before using" on a typo or rename is friction without value. Skip plan mode and Layer 2 for single-sentence diffs.
- Punitive reactions to "I don't know": the abstention license is partly a human commitment. Sessions where confident-but-wrong is praised and "uncertain" is corrected train the agent, through in-session pattern matching, toward confident guessing.

## Example

This repository dogfoods Layer 3. The `.claude/settings.json` registers a `Stop` hook running `.claude/hooks/pre-completion-check.sh`, which dispatches a task-type checklist (lint changed pages, check meta tags, run nav sync) before the agent can declare done. The script's findings flow back through stderr — Claude reads them in the next turn and re-runs the failing check.

A worked Layer 4 sketch for the same repo:

```markdown
---
name: validate-claims
description: Read-only fact-checker. Re-verifies cited URLs and symbol claims in the diff against external sources. Invoke before commit on content edits.
model: sonnet
tools: [Read, Grep, Bash, WebFetch]
---
# Validate Claims
Read the diff. For every URL: WebFetch and confirm the source supports the
claim. For every named symbol or file: grep the working tree to confirm it
exists. Report VERIFIED / WRONG / UNVERIFIABLE per claim. Do not edit files.
```

The reviewer holds external tools: WebFetch for source verification, and Bash plus Grep for symbol existence. Without those, Liu et al.'s overcorrection risk applies. The Copilot equivalent is the [Copilot coding agent's pre-PR self-review](../code-review/agent-self-review-loop.md), which runs code review, security scanning, and dependency checks before opening the PR. The structural shape is the same — fresh context, scoped tools, gate before commit.

## Key Takeaways

- The four-layer harness is risk reduction, not elimination — frame and measure it that way.
- Layer 1 fails when instruction files exceed the ~150 rule budget; rule the honesty section first or convert it to a hook.
- Layer 3's load-bearing detail is that hook output flows back to the agent — silent hooks change nothing.
- Layer 4 must hold external tools (LSP, type checker, doc lookup, tests) or it overturns correct code via the Huang–Liu self-correction failure.
- The "I don't know" license is partly a human commitment; punitive reactions to abstention re-train confident guessing within the session.

## Related

- [Premature Completion](../patterns/anti-patterns/premature-completion.md) — the failure mode this harness remediates
- [Context Poisoning](../patterns/anti-patterns/context-poisoning.md) — when an early hallucination becomes a downstream premise the harness must intercept
- [Pre-Completion Checklists](pre-completion-checklists.md) — the Layer 3 mechanism in detail, including over-verification spiral conditions
- [Phantom Symbol Detection](phantom-symbol-detection.md) — the deterministic-lookup form of Layer 2 for API migration
- [Layered Accuracy Defense](layered-accuracy-defense.md) — the same defense-in-depth idea applied to content pipelines instead of coding agents
- [Hooks for Enforcement vs Prompts for Guidance](../instructions/hooks-vs-prompts.md) — why Layer 3 belongs in hooks, not the system prompt
- [Agent Self-Review Loop](../code-review/agent-self-review-loop.md) — Layer 4 as practised in Copilot's pre-PR review
</content>
</invoke>
