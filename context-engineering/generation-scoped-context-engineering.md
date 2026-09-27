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
last_reviewed: 2026-09-26
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

## Running the prompt-audit command

Treat every finding from this audit as a proposal, not a verdict. The report grades each finding by confidence, and a diff sits beside it for you to accept or reject hunk by hunk; nothing changes on its own.

Two commands run some form of this audit, and no source confirms they run the same procedure. Claude Code 2.1.283, released September 25, 2026, "Added `/doctor prompt-audit` (also `/checkup prompt-audit`) to audit your CLAUDE.md files, skills, agents and commands for prompting patterns written for older models" ([Claude Code changelog](https://code.claude.com/docs/en/changelog#2-1-283)). A separate subcommand shipped first, in Claude Code 2.1.221 on August 4, 2026: "Added a `prompt-audit` subcommand to the `claude-api` skill for auditing prompts and tool descriptions for patterns written for older models" ([Claude Code changelog](https://code.claude.com/docs/en/changelog#2-1-221)). Claude Code's commands reference documents that second form: "Run `prompt-audit` to flag instructions written for older models in your prompts, skills, and tool descriptions and propose fixes as a diff" ([Claude Code commands reference](https://code.claude.com/docs/en/commands)). Its `/doctor` row names no `prompt-audit` subcommand at all. Do not assume `/doctor prompt-audit` runs the `claude-api` skill's published procedure below; no source states that it does. The `/doctor` row's own description does match the shape: it reports findings and asks for confirmation before it changes anything.

Anthropic's published procedure for the `claude-api` skill's audit sets a keep-list, so a line matching a pattern table is not an automatic deletion candidate ([anthropics/skills — prompt-audit.md, commit 3337550](https://github.com/anthropics/skills/blob/33375500bcea98d610eb30ce10ac4e59b89c390d/skills/claude-api/shared/prompt-audit.md)):

- Scoped emphasis: "Emphasis is not banned; it is a tested, scoped fix for one demonstrably underweighted instruction, not a first-draft register."
- A single end-of-prompt recap: "Deliberate recap is not padding. A single end-of-prompt restatement of the few key constraints is a known, reasonable pattern; the anti-pattern is scattered duplication."
- Trigger and routing text, because "skills currently under-trigger." The audit flags shouting in a prompt's body, not in text that decides whether a skill fires.
- Exact scripts for fragile operations, because prescriptive text is correct for "destructive commands, auth flows, compliance steps."
- A prohibition whose failure still happens: "prohibitions against current, demonstrated failures stay."
- Duplication that still works: "working redundancy is not cruft."

Findings carry a confidence grade: "High - documented in current Claude docs or errors on the target model. Medium - consistent, widely-observed behavior (e.g. example over-indexing). Low - heuristic or idiom-dating; flag, don't edit." A low grade stays in the report and drops out of the diff.

A high grade is not proof a cut is safe. The procedure calls a removal a hypothesis: "Probe behavior, not self-report ... Asking the model whether it needs an instruction is not a measurement." Test a contested change on a scratch copy before and after, one change at a time when the stakes are high, and check who else reads the exact line before you delete it: "Check out-of-band dependencies before deleting. Grep the wider system for the exact prompt text first - classifiers, tests, and log parsers sometimes match on prompt strings."

Re-run the audit on model changes, not on a calendar: "Re-audit at every model release. Prompts are per-model artifacts; a line that is load-bearing on one generation is cruft on the next."

An independent practitioner who repeated the exercise on an operational repository reported "an 11% cut on one repository, not an 80% one, and a set of findings that had almost nothing to do with byte counts" ([Digital Applied — We Cut Our AI Agent Instruction Files](https://www.digitalapplied.com/blog/ai-agent-instruction-file-audit-what-we-cut)). A file built mostly from redundant documentation carries a large cut. One built mostly from hard-won operational knowledge carries a small one, and pruning either to hit a fixed percentage would destroy the valuable part first. "Dated" is not a fixed judgment across models, either: independent research found that "newer GPT models exhibit diminishing or even negative marginal gains from structured prompting... whereas Qwen models continue to benefit substantially from Few-Shot and CCoT" ([Rudyk et al., arXiv:2608.24641v1](https://arxiv.org/abs/2608.24641v1)). A line this audit flags as cruft for the target Claude model can stay load-bearing for a different model family reading the same shared file, such as AGENTS.md.

The 2.1.283 release also widened what the report leads with, beyond prompting patterns: "stale paths, stale commands and contradicting instruction files now lead the report" ([Claude Code changelog](https://code.claude.com/docs/en/changelog#2-1-283)). That check now overlaps [Scheduled Instruction File Fact-Checker](../workflows/instruction-file-fact-checker.md), which verifies instruction-file claims against the codebase on its own schedule.

## Why it works

A guardrail in a system prompt is compensation for a specific generation's deficit. Older models wrote wrong comments without a "no comments" rule and attended more to the end of the context window than the start, so the rules earned their tokens. A capability jump lifts the model past the threshold the guardrail compensated for, and the guardrail flips from net benefit to net cost. It becomes a directive the model must reconcile against everything else before acting: Anthropic's own transcripts showed "several conflicting messages in a single request like 'leave documentation as appropriate,' or 'DO NOT add comments'," which the model "must think more carefully about" before deciding ([Anthropic — The new rules of context engineering](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models)). This is the right-altitude idea from Anthropic's [context-engineering guidance](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) moving over time. The correct altitude of a prompt rises as the model improves, so guidance that was correctly specific last generation is over-specified this one.

OpenAI reports the same reversal on its own generation hop, which puts a second vendor on the mechanism. Instructions that pushed a previous model to check its work now overshoot: "Previous models needed encouragement to run tests and check their work. GPT-6 Astra does that on its own, so the same instructions can lead to unnecessary testing" ([OpenAI — Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)). Boundary language ages the same way. The same post warns that a rule about where to stop can bind harder than intended, because "Astra could take it too seriously and may stop work where you'd actually be happy for it to continue."

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
- [Scheduled Instruction File Fact-Checker for Accuracy](../workflows/instruction-file-fact-checker.md) — the neighboring drift axis: factual claims against the live codebase, rather than prose aging against the model.
- [Prompt Debt: Hand-Tuning Natural-Language Prompts as Technical Debt](../patterns/anti-patterns/prompt-debt.md) — the slow-accumulation cousin; this page is the generation-jump trigger to pay it down.
- [Instruction Polarity: Positive Rules Over Negative](../instructions/instruction-polarity.md) — why blanket NEVER rules misfire once the model can reason from intent.
