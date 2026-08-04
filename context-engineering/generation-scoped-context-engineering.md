---
title: "Re-Auditing Context Engineering Across Model Generations"
description: "Context-engineering best practices are model-generation-dependent; a capability jump lets you delete guardrails the new model no longer needs, while keeping the security-critical constraints that stay load-bearing."
term: "Generation-Scoped Context Engineering"
tags:
  - context-engineering
  - instructions
  - claude
aliases:
  - generation-scoped context engineering
  - context engineering per model generation
applies_to: "claude-code@2.x"
last_reviewed: 2026-07-25
maturity: emerging
---

# Re-Auditing Context Engineering Across Model Generations

> Context engineering best practices expire as a model generation improves; a capability jump is the cue to re-audit and delete the guidance the model outgrew.

A system prompt encodes assumptions about one model generation's failure modes. When the model improves, those assumptions stop holding and the guardrails built on them turn from help into friction. Anthropic removed "over 80% of Claude Code's system prompt for models like Claude Opus 5 and Claude Fable 5 with no measurable loss on our coding evaluations". The capability jump made most of the scaffolding obsolete ([Anthropic — The new rules of context engineering for Claude 5 generation models](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models)). Re-auditing guidance on every generation hop, and deleting what the model has outgrown, is now part of maintaining an agent.

## The reversals a capability jump triggers

Anthropic names six former best practices that became myths on the newer models. Read each as a prompt to check your own context ([Anthropic — The new rules of context engineering](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models)):

- Rules to judgment. The old prompt said "default to writing no comments." The new one says "Write code that reads like the surrounding code: match its comment density, naming, and idiom." A capable model reads the room; a blanket rule fires wrongly on the cases it did not anticipate. See [Instruction Polarity](../instructions/instruction-polarity.md) and [System Prompt Altitude](../instructions/system-prompt-altitude.md).
- Examples to interface design. For tool usage, "giving examples actually constrains them to a certain exploration space." Design expressive parameters instead: a Todo status modeled as an enum of `pending`, `in_progress`, `completed` tells the model how to use the tool without boxing it in.
- Everything upfront to progressive disclosure. Verification and code review moved out of the system prompt into skills the agent loads when needed, and deferred-loading tools expand their schema only after the agent searches for them. Prefer a tree of files loaded at the right time over a monolithic instruction file. See [Discoverable vs Non-Discoverable Context](discoverable-vs-nondiscoverable-context.md).
- Repetition to single tool descriptions. Older models needed the same guidance in the system prompt and the tool description; the newer ones do not. Put tool instructions in the tool description and delete the duplicate.
- Manual memory to auto-memory. Claude Code now saves relevant memories automatically instead of relying on hand-written CLAUDE.md entries, so the file stays lightweight.
- Simple specs to rich references. The model handles higher-fidelity references than a markdown plan: an HTML mockup, a test suite, a function to port, or a rubric a verifier agent grades against. See [HTML as an Agent Output Format](../instructions/html-as-output-format.md).

Claude Code ships tooling for the audit itself: "We've put these best practices in `claude doctor`; use the command /doctor in Claude Code to rightsize your skills, and CLAUDE.md files" ([Anthropic — The new rules of context engineering](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models)).

## Why it works

A guardrail in a system prompt is compensation for a specific generation's deficit. Older models wrote wrong comments without a "no comments" rule and attended more to the end of the context window than the start, so the rules earned their tokens. A capability jump lifts the model past the threshold the guardrail compensated for, and the guardrail flips from net benefit to net cost. It becomes a directive the model must reconcile against everything else before acting: Anthropic's own transcripts showed "several conflicting messages in a single request like 'leave documentation as appropriate,' or 'DO NOT add comments'," which the model "must think more carefully about" before deciding ([Anthropic — The new rules of context engineering](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models)). This is the right-altitude idea from Anthropic's [context-engineering guidance](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) moving over time. The correct altitude of a prompt rises as the model improves, so guidance that was correctly specific last generation is over-specified this one.

## When this backfires

Deleting constraints is the wrong move under several conditions:

- A weaker or older model. The reversals are scoped to "more advanced models." On a Sonnet-class, Haiku-class, prior-generation, or non-Anthropic model that still needs the scaffolding, stripping it regresses output because the guardrail was covering a real gap.
- Security- and injection-critical constraints. Anthropic keeps these: skills should avoid over-constraint "except in highly important areas" ([Anthropic — The new rules of context engineering](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models)). A proactive model can autonomously take destructive actions, and prompt injection remains unsolved, so deleting a "never run destructive commands" line removes a control, not friction ([OWASP via Help Net Security — prompt injection still drives most agentic AI failures](https://www.helpnetsecurity.com/2026/06/11/owasp-prompt-injection-ai-security-failures/)).
- No regression eval. Anthropic deleted 80% because their coding evals stayed flat. Without an eval set a team cannot tell whether a deletion lost behavior, and the "no measurable loss" claim covers coding tasks, not every safety-critical edge case.
- Audited or change-controlled prompts. A prompt pinned by a compliance or security sign-off cannot be stripped on a model hop without re-running the audit, and that cost dominates the token saving.

The examples reversal is narrower than it sounds: it targets tool-usage examples, not few-shot examples in general. Anthropic's context-engineering guide still recommends "a set of diverse, canonical examples" for shaping behavior ([Anthropic — Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)). Delete the examples that constrain tool exploration, not the canonical ones that define correct behavior.

## Example

The comment rule shows the whole pattern in one edit ([Anthropic — The new rules of context engineering](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models)):

Before, a guardrail written for a prior generation:

```text
In code: default to writing no comments. Never write multi-paragraph
docstrings or multi-line comment blocks — one short line max.
```

After, the same goal delegated to judgment:

```text
Write code that reads like the surrounding code: match its comment
density, naming, and idiom.
```

Same intent, half the words, and it stops firing wrongly on the complex algorithm or public API where multi-line documentation was correct. The security-critical lines in the same prompt stay untouched.

## Key takeaways

- Context-engineering guidance is generation-scoped; a capability jump is the trigger to re-audit and delete what the model has outgrown, not a one-time cleanup.
- Test each guardrail against the current model: if it no longer makes the mistake the rule guards against, the rule has become a conflicting directive competing with newer instructions, not a safeguard, so delete it.
- The six reversals — rules to judgment, examples to interfaces, upfront to progressive disclosure, repetition to single descriptions, manual to auto-memory, simple specs to rich references — are a re-audit checklist, not a demand to delete everything.
- Keep the security- and injection-critical constraints, keep guardrails for weaker models, and only delete against a regression eval that confirms no loss.

## Related

- [Reducing System-Prompt Token Bloat in Coding Agents](system-prompt-bloat-reduction.md) — the measurement step that finds what to delete before you delete it.
- [Discoverable vs Non-Discoverable Context](discoverable-vs-nondiscoverable-context.md) — the progressive-disclosure rule: only keep what the model cannot find for itself.
- [Prompt-Rewrite Discipline on Cross-Generation Model Migration](../instructions/prompt-rewrite-on-cross-generation-migration.md) — the process wrapper for the rewrite this audit feeds into.
- [Prompt Debt: Hand-Tuning Natural-Language Prompts as Technical Debt](../patterns/anti-patterns/prompt-debt.md) — the slow-accumulation cousin; this page is the generation-jump trigger to pay it down.
- [Instruction Polarity: Positive Rules Over Negative](../instructions/instruction-polarity.md) — why blanket NEVER rules misfire once the model can reason from intent.
