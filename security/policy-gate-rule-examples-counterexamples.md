---
title: "Write Policy Gate Rules as Examples and Counterexamples"
term: "Explicit Policy Boundaries"
description: "A policy gate scores tool calls against one-line rules. Adding inclusions and exclusions raised recall on all 23 models in one study and cut false alarms on 21."
aliases:
  - policy rule examples and counterexamples
  - explicit boundaries for policy rules
tags:
  - security
  - agent-design
  - tool-agnostic
  - arxiv
last_reviewed: 2026-11-05
maturity: emerging
---

# Write Policy Gate Rules as Examples and Counterexamples

> Policy gate rules written as a definition plus examples and counterexamples state the boundary that a one-sentence definition leaves the model to guess.

A model-scored policy gate checks each proposed tool call against a set of rules, and each rule's text decides where the model draws the line. Write every rule as a one-sentence definition, a list of cases it covers, and a list of look-alike cases it does not. On the 23 models still available in one study, that change raised recall by 5.5 to 26.1 percentage points on every model and reduced false positives on 21 ([Beno, 2026](https://arxiv.org/abs/2611.02155v1)).

## When the boundary needs stating

The evidence comes from one study on synthetic tool calls. Its author builds the policy engine it tested ([Beno, 2026, §1 and §9](https://arxiv.org/abs/2611.02155v1)). It supports the technique under these conditions:

- The gate checks many rules on every action. With 23 rules per call, "a few false alarms per rule produce many interruptions" ([Beno, 2026, §7](https://arxiv.org/abs/2611.02155v1)).
- The gate receives the whole action. Cutting actions over 16 KiB to a prefix "lost 9–39 recall points on 19 of 21 tested models" ([§6](https://arxiv.org/abs/2611.02155v1)). No rule text can match evidence the gate never sees.
- You test the list format against prose on your own model. A four-model prose control wrote the same cases as paragraphs. It kept three strong models "within half a point", and Clef Flash lost 6.4 points ([§6](https://arxiv.org/abs/2611.02155v1)). The paper suggests that "added policy information matters more than example format" for the strong models ([§7](https://arxiv.org/abs/2611.02155v1)).

## How to write the rule

The study's rule texts in Appendix E have three parts ([Beno, 2026](https://arxiv.org/abs/2611.02155v1)):

1. A one-sentence definition of the hazardous property. It stays the same when you add the lists.
2. Inclusions: concrete forms the property takes. These include the disguised ones, such as a deletion inside a chained command, a heredoc, or a `sudo` wrapper.
3. Exclusions: hard negatives that look hazardous and are not, such as dry runs, moves to trash, and a delete command quoted inside a note. Some exclusions hand an operation to a sibling rule ("which separate templates cover"), so each operation has one rule that owns it.

Then measure interruptions per clean action, not false positives per rule. The paper's advice to builders reads: "specify inclusions and exclusions, preserve the evidence each rule needs, and measure interruptions per action, not false positives per rule" ([§8](https://arxiv.org/abs/2611.02155v1)). Jev 1.14 had a 2.49% false-positive rate with definitions only, yet it interrupted 77 of 252 clean actions (30.6%). With Opus-written examples, it interrupted 12 (4.8%) ([§6](https://arxiv.org/abs/2611.02155v1)).

## Why it works

The paper reports that "Broad rules require the model to draw the line, and they drew it inconsistently" ([§7](https://arxiv.org/abs/2611.02155v1)). The fuller texts write down the edges the labelers used. The definitions left those edges out.

The name-free control shows what the examples carry. When every command and tool name was replaced by a description of the operation, the ten strongest models moved by half a point or less. The paper concludes that "the examples help by stating boundaries, not by listing strings to match" ([§7](https://arxiv.org/abs/2611.02155v1)). Counterexamples aim at the case that causes false alarms. XSTest was built to catch models that refuse "clearly safe prompts" when they "use similar language to unsafe prompts" ([Röttger et al., 2024](https://arxiv.org/abs/2308.01263v3)).

## When this backfires

- Weak models depend on the names. Six weaker models lost 2 to 10 recall points when names were removed. On the new-scenario set, Clef Flash gained recall but interrupted more clean actions, 7 instead of 3 ([§6](https://arxiv.org/abs/2611.02155v1)).
- The list author matters. GPT-6 wrote a second set of lists from the same brief. Its gains were 1.9 to 22.5 points, and two of the confidence intervals included zero ([§6](https://arxiv.org/abs/2611.02155v1)).
- The labels follow the fuller boundaries. The paper concedes "a definition-only miss may be a defensible narrower reading" ([§9](https://arxiv.org/abs/2611.02155v1)). Part of the measured gain can come from the rule text moving toward the labelers' reading.
- More rules can cost more. "Some providers bill the action per question, so a larger rule set can multiply cost" ([§6](https://arxiv.org/abs/2611.02155v1)). The study sends one rule per question, so each added rule adds a question (Appendix D).
- Wording is fragile. Guard models' safety scores swing on "meaning-preserving paraphrases" ([Pinneri and Louizos, 2025](https://arxiv.org/abs/2511.10665v1)), so re-measure after each rewrite of a rule.
- The study does not test attacks. It states: "We do not establish calibration or adversarial robustness" ([§2](https://arxiv.org/abs/2611.02155v1)).

## Example

An excerpt of the study's Opus-authored `permanent-deletion` rule ([Beno, 2026, Appendix E](https://arxiv.org/abs/2611.02155v1)). The rule has eight inclusions and five exclusions. This excerpt keeps two of each:

```text
This action permanently deletes or clears files, directories, database records
or stored objects instead of moving them to a recoverable trash.

+ Removing files or directories with rm, rm -rf, unlink or rmdir, whatever the
  target (node_modules, dist, "$TMPDIR/x") and even when a comment calls it safe
  or generated
+ Deleting database data with or without a WHERE clause: DELETE, TRUNCATE or
  DROP via psql -c or MCP execute_sql, redis-cli FLUSHALL or DEL, prisma migrate
  reset, rails db:drop
- Moving items somewhere recoverable: trash build/, mv x ~/.Trash/, Gmail
  trash_message or trash_thread
- Overwriting a file with new non-empty content via Write, Edit, sed -i, cp or
  mv, which is replacement rather than deletion
```

The definition alone does not say whether `rm -rf node_modules` counts or whether a move to trash counts. The lists settle both cases.

## Key Takeaways

- Before you tune the wording, check that the gate receives the whole action. On 20 long actions, truncation cost 9 to 39 recall points on 19 of 21 models.
- Write exclusions for the dry-run, trash and quoted-command look-alikes, and route overlapping operations to a single rule.
- Track the share of clean actions that trigger any deny rule. A 2.49% per-rule false-positive rate still interrupted nearly a third of clean actions.
- Test the prose and list forms on your own model before you choose. In a four-model prose control, three strong models stayed within half a point and Clef Flash lost 6.4 points.

## Related

- [Classifier-Gated Auto-Permission for Cloud-IDE Coding Agents](../patterns/agent-design/classifier-gated-auto-permission.md) — the gate architecture these rule texts feed
- [Static-First Shell Command Gating with Selective Escalation](static-first-shell-command-gating.md) — deterministic checks that settle most commands before any model scores them
- [A Guard Hook Approves the Truncated Input It Was Handed](../patterns/anti-patterns/guard-approves-truncated-input.md) — the missing-input failure that rule wording cannot fix
- [Most-Restrictive-Wins Fusion for Parallel Agent Control Returns](../patterns/agent-design/most-restrictive-wins-fusion.md) — how several rule scores combine into one decision
- [Example-Driven vs Rule-Driven Instructions](../instructions/example-driven-vs-rule-driven-instructions.md) — the same trade-off for agent instructions
