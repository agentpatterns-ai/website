---
title: "Auditing an Instruction File for Interference Between Its Own Rules"
term: "Instruction File Interference Audit"
description: "Check an agent instruction file's rules against each other in pairs. Which interference findings are structural defects, which are maintenance debt, and what the compliance evidence rules out."
aliases:
  - prompt interference audit
  - instruction file self-audit
  - rule pair interference check
tags:
  - testing-verification
  - instructions
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-10
maturity: emerging
---

# Auditing an Instruction File for Interference Between Its Own Rules

> Check an instruction file's rules against each other in pairs. Act on pairs no choice satisfies and on precedence rules you own.

An interference audit reads an instruction file as a document rather than as instructions, splits it into blocks, and checks block pairs for rules that cannot both hold. Run it for the findings that fail whichever way the model leans: a pair where every available action violates something, or a write path whose destination has no field for what the write produces. Precedence rules you write are a third class, covered below. The rest is duplication and drift, which is maintenance work. The one factorial study that manipulated contradictions and measured compliance found no compliance effect from contradictions ([McMillan, 2026](https://arxiv.org/abs/2605.10039v1)).

The evidence is one preprint on three vendor prompts ([Mason, 2026](https://arxiv.org/abs/2603.08993v2)), with directed analysis on one of them.

## What the audit looks for

Arbiter classifies each block by modality (mandate, prohibition, guidance, information) and by the scope it governs, then evaluates pairs against five rules ([Mason, 2026](https://arxiv.org/abs/2603.08993v2), §3.2).

| Rule | What it catches |
|---|---|
| Mandate-prohibition conflict | One section requires a tool another forbids in the same context |
| Scope overlap redundancy | One constraint restated in two or three places with drifting wording |
| Priority marker ambiguity | Two rules reach the same situation with no stated precedence between them |
| Implicit dependency | A restriction in one mode leaves no legal route to a permitted action |
| Verbatim duplication | The same text copied to two locations |

Two of the five run as Python predicates with no model call, and pre-filtering on scope and modality cut Claude Code's 56 blocks "from approximately 15,680 evaluations to 100-200 relevant pairs". Most of what turned up needed no model either: "Of these 21 patterns, 20 (95%) were statically detectable - a compiler checking scope overlap and modality conflict would catch them without any LLM involvement." The one exception needed reasoning across sections, a plan mode that restricted file-editing tools while general policy prohibited doing file work through Bash.

## Which findings are worth acting on

Sort by whether a model has a legal move, not by the severity label the audit assigns.

Act on the pair when no choice complies. Gemini CLI carries an "Explain Before Acting" mandate requiring a sentence before every tool call, against a "Minimal Output" rule capping output under three lines and banning tool-use narration. "In any non-trivial task requiring multiple tool calls, simultaneous compliance is structurally impossible." No resolution heuristic saves this. The agent breaks a rule on every turn.

Act on it when written data has nowhere to land. Gemini CLI's history-compression prompt defines the schema that becomes the agent's only memory after compression, and that schema carries no field for what the `save_memory` tool stores. So "any preference stored via save\_memory is structurally guaranteed to be deleted during a compression event." Where the defect lives is the useful part: "The bug exists in the contract between them - a contract that was never written." Google independently filed and patched an infinite loop in that same compression system without adding the missing field.

Log the rest. Thirteen of Claude Code's 21 patterns were one constraint restated in two or three places: read-before-edit, no-emoji, prefer-dedicated-tools. All agreed at audit time, so they are drift risk rather than a current defect.

Precedence findings need an owner. All three prompts "define multiple authority sources - system instructions, configuration files, user messages, tool-injected context - without fully specifying how conflicts between them resolve." Actionable where you write the precedence rule, informational where the ambiguity sits between a vendor's prompt and your file. [Layered Instruction Scopes](../instructions/layered-instruction-scopes.md) covers the layout that makes precedence explicit.

## Why it works

Detection and execution want different positions in the file, and the running agent only ever holds one of them: "the heuristic that enables an LLM to navigate contradictory instructions is the same heuristic that prevents it from recognizing those instructions as contradictory" ([Mason, 2026](https://arxiv.org/abs/2603.08993v2), §5.2). Facing a mandate and its prohibition, the agent picks one and carries on, and "No error is raised. No warning is logged." The pair survives every session it governs. A pass that treats the file as a document has no conflict to resolve and can see it.

The pairs cluster where teams do. Claude Code's four critical contradictions all sat on one subsystem boundary, a general task-tracking mandate against the commit and PR workflows that forbid the same tool. The paper reads this as Conway's Law in a new medium (§5.1, citing Conway, 1968).

## When this backfires

- You are chasing a compliance bug. A factorial study across 1,650 Claude Code CLI sessions and 16,050 function-level observations manipulated contradictions in adjacent config files and found nothing: "The size and conflict nulls are supported by affirmative-null Bayes factors (BF10 between 0.05 and 0.10); the position and architecture nulls are failures to reject without Bayes-factor support" ([McMillan, 2026](https://arxiv.org/abs/2605.10039v1)). That is evidence for no effect, not a null waiting for more statistical power. Its target was a trivial annotation on two TypeScript codebases, and the authors bound the result to the conditions tested, so it does not reach the unsatisfiable pairs above. It does rule out the general claim. The lever it did measure was session length, roughly 5.6% lower odds of compliance per additional generated function. See [Configuration File Structure Does Not Drive Compliance](../instructions/configuration-file-structure-compliance-gap.md).
- The file is short and had one author. Codex CLI's 298-line prompt returned 15 findings, none rated alarming, against 116 findings and 12 alarming for Claude Code's 1,490 lines. The paper's verdict: "Codex's simplicity buys consistency. The prompt is the cleanest of the three." A sweep of a 200-line AGENTS.md returns scope-overlap minutiae.
- You run it as open-ended prompting. The rule definitions carry the work, which is what the 95% figure says. The open-ended half produced 152 findings, and version 2 withdrew both of version 1's claimed guards against fabrication: cross-model confirmation is impossible because each pass is told not to repeat prior findings, and "no per-finding verdict was written down, so no precision figure can be reported for the 152."
- The file changes daily. Prompt structure held constant within a version across 49 instrumented sessions, varying only in the injected environment block, so a per-version audit caches. A file edited every day needs the check wired into CI or skipped.
- You wanted the architecture guidance. The monolith, flat, and modular failure classes rest on one prompt per class: "The correlation is a hypothesis to be tested on further prompts per class, not an established relationship."

The stronger objection is to the artifact rather than the audit. Context files did not generally help: "providing context files does not generally improve task success rates, while increasing inference cost by over 20% on average" ([Gloaguen et al., 2026](https://arxiv.org/abs/2602.11988v3)). If a rule set earns no measured task-success gain, auditing its internal consistency improves a document nothing demonstrably depends on, and deleting rules is cheaper (the [instruction compliance ceiling](../instructions/instruction-compliance-ceiling.md) is the argument for that route). The audit survives that only for the unsatisfiable pairs and the write-with-no-destination case. These break a stated rule on every run whether or not the file helps. It is also static work. None of the sources reviewed here measures whether a conflict in the text predicts what the agent does. [Behavioral Preflight](behavioral-preflight-rule-replay.md) is the check that would.

## Example

Both triage buckets, drawn from the same table of 21 hand-labeled patterns on Claude Code v2.1.50 ([Mason, 2026](https://arxiv.org/abs/2603.08993v2), Appendix C).

Act on these four. All rated critical, all one shape: a task-tracking mandate ("use VERY frequently", "ALWAYS use") against commit and PR workflow prohibitions ("NEVER use TodoWrite"). In a commit context the agent must break one of them. Two blocks, one scope, opposite modalities, which the structural check finds without a model call.

Log this one. Read-before-edit appears in a general behavioral section, the Edit tool definition, and the Write tool definition, worded differently each time. Nothing is wrong today. The finding records that three copies will not stay in agreement.

Cost, for sizing a run of your own: $0.263 across three vendors, 15 passes, 26 API calls, $0.002 per finding (Appendix D, from OpenRouter billing). One of the 15 passes was billed through a subscription and is excluded, so the total is a lower bound. The paper's GitHub link is an unfilled `<org-or-user>` placeholder. It also names a Zenodo snapshot (DOI 10.5281/zenodo.18929834) that this page has not checked, so treat the five rules as the part you implement.

## Key Takeaways

- Triage on whether a legal move exists. A pair the model can resolve either way is maintenance; a pair with no compliant action is a defect on every run.
- The second actionable class is a write with no destination, where one rule stores data and another's schema has no field to carry it.
- Precedence gaps in rules you write are actionable. Gaps between a vendor prompt and your file are informational.
- Write the rules down before you run the check. 20 of 21 findings were statically detectable, and the open-ended half produced 152 findings with no precision figure.
- Do not reach for this when compliance is the symptom. Conflicts between adjacent config files carry an affirmative null across 1,650 sessions, and session length moved compliance instead.
- The audit is static. Nothing measured shows a conflict in the text predicts the agent's behavior, so pair it with a behavioral check.

## Related

- [Behavioral Preflight: Replay Tool-Call Rules Before Enforcing](behavioral-preflight-rule-replay.md) — the behavioral counterpart, scoring a rule against recorded runs instead of against its siblings
- [Policy File Validation: Catching Silent Non-Enforcement](../instructions/policy-file-validation.md) — the same fail-quiet problem in a machine-readable settings file, where the defect is a typo rather than a conflicting rule
- [Configuration File Structure Does Not Drive Compliance](../instructions/configuration-file-structure-compliance-gap.md) — the factorial study that bounds what this audit can claim
- [LLM Static Verification Against Natural-Language Requirements](llm-static-verification-natural-language-requirements.md) — checks code against a spec; this audit checks the spec against itself
- [Agent Extension Conflicts](../patterns/anti-patterns/agent-extension-conflicts.md) — the same interference across separately installed extensions rather than inside one file
