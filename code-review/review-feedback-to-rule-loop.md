---
title: "Review-Feedback-to-Rule Loop: Promoting Recurring PR Comments into Harness Rules"
term: "Review-Feedback-to-Rule Loop"
description: "Convert recurring code review comments into mechanical checks (a lint rule, an AST boundary check, or an evaluator rubric line) so the same comment never needs to be written twice."
tags:
  - code-review
  - instructions
  - testing-verification
  - workflows
  - tool-agnostic
  - harness-engineering
aliases:
  - recurring review comments to rules
  - promote review feedback to harness checks
last_reviewed: 2026-06-13
maturity: established
---

# Review-Feedback-to-Rule Loop: Promoting Recurring PR Comments into Harness Rules

> Promote a recurring review comment into a harness rule once it fires across 3+ PRs, then retire it when the hit count hits zero.

## When a comment becomes a signal

A recurring review comment is evidence of an unencoded invariant. The rule lives in one reviewer's head, and every PR pays the cost of re-deriving it. The promotion threshold (same comment across three or more PRs in a window) is load-bearing: one or two occurrences is a hypothesis, three or more is a pattern. The walkinglabs harness engineering curriculum encodes this loop as a first-class practice ([walkinglabs — review-feedback-to-rule](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/lectures/lecture-10-why-end-to-end-testing-changes-results/code/review-feedback-to-rule.md)).

## The loop

```mermaid
graph LR
    A[Recurring<br/>review comment] --> B[Categorise]
    B --> C[Encode as<br/>smallest enforceable check]
    C --> D[Write remediation<br/>text alongside]
    D --> E[Merge to harness]
    E --> F[Track hit count]
    F -->|Trends to zero| G[Retire]
    F -->|Still firing| E
```

### 1. Categorize the comment

Match the rule's placement to the comment's category. Promoting a semantic check to a regex linter is a category error. It fires on legitimate exceptions and erodes trust in the lint stack.

| Comment category | Encoding layer |
|---|---|
| Style or formatting | Linter rule (ESLint, Ruff, etc.) |
| Architectural boundary | AST/import check, dependency graph rule |
| Safety or correctness invariant | Pre-completion checklist entry, type or runtime check |
| Spec or contract violation | Evaluator rubric line, integration test |

### 2. Encode the smallest enforceable check

Pick the cheapest mechanism that fires deterministically. A one-line `ESLint` rule beats a multi-file AST plugin when both would work. Over-engineering adds maintenance cost that the retirement step cannot recover.

### 3. Write the remediation text

A rule that says `no fs in renderer` without saying what to do instead moves the bottleneck from review to comprehension. The source pairs the lint rule with explicit remediation: "Use the preload bridge" ([walkinglabs](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/lectures/lecture-10-why-end-to-end-testing-changes-results/code/review-feedback-to-rule.md)).

The shape that works:

```
ERROR: Service layer cannot import from UI layer.
  Move shared logic to a Provider in src/providers/,
  or restructure to keep UI-specific code in src/ui/.
  See docs/architecture/layer-rules.md for the dependency diagram.
```

That structure states what is wrong, what to do instead, and where the rationale lives. See [Feedback as Capability Equalizer](../patterns/agent-design/feedback-capability-equalizer.md) for why it works.

### 4. Track hit count and retire

Every rule has a finite shelf life. Refactors obviate boundaries, model upgrades eliminate failure modes, conventions solidify until no one would write the violation. Without retirement, the rule library accumulates dead weight and the priority-saturation failure mode of [standards as agent instructions](../instructions/standards-as-agent-instructions.md) kicks in: when every rule has equal weight, nothing signals priority and adherence degrades.

Periodic decay pairs this loop with [harness impermanence](../patterns/agent-design/harness-impermanence.md): rules whose hits trend toward zero are deletion candidates. Annotate each rule with its obsolescence condition, the observable signal that it has done its job. Where the rule fires on an agent reviewer, [dismissal reason capture](dismissal-reason-capture.md) supplies the sharper input: a per-rule split of dismissals into wrong versus correct-but-unwanted, which separates a rule to retire from a rule to narrow.

## Why mechanical enforcement beats repeated comments

Anthropic separates the modes explicitly: "Unlike CLAUDE.md instructions which are advisory, hooks are deterministic and guarantee the action happens" ([Claude Code best practices](https://code.claude.com/docs/en/best-practices)). The distinction holds for review comments versus lint rules. A reviewer's eye is probabilistic; a mechanical check fires every time. LangChain's harness changes lifted Terminal Bench 2.0 from 52.8% to 66.5%, with self-verification among the high-impact components ([LangChain](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)); mechanical pre-merge checks are the human-team analogue.

## What this is not

This differs from [learned review rules](learned-review-rules.md): the Cursor Bugbot pattern adjusts the reviewer's behavior by extracting rules from accept and reject signals. This loop promotes the invariant out of the reviewer entirely, into the lint stack, checklist, or evaluator rubric. The two compose. Bugbot tunes reviewer defaults; this loop drains high-frequency comments before they reach review.

It also differs from [incident-to-eval synthesis](../verification/incident-to-eval-synthesis.md), which converts production failures into regression tests. The trigger and the enforcement layer differ. And where a comment is semantic rather than mechanically checkable (a design-judgment call no lint rule can express), the counterpart move is [accumulated behavioral rules](../workflows/accumulated-behavioral-rules.md): keep the correction as a loaded instruction the agent self-checks, rather than promoting it to a deterministic check.

## Example

A team's reviewer leaves the same comment on six PRs over two weeks: "This handler swallows the database error. Re-throw or wrap it with context — silent failures here cause the on-call to chase ghosts."

The trigger fires (6 ≥ 3). Categorize it: this is a safety and correctness invariant, not a style point. An AST check is the wrong choice here, because the violation is semantic: whether the handler "swallows" the error depends on what the catch block does with it. A pre-completion checklist line is the right layer.

Add to `.claude/checklists/pre-merge.json`:

```json
{
  "id": "ERR01",
  "severity": "HIGH",
  "check": "Every catch block in src/handlers/ either re-throws, logs at error level, or wraps the error with context. Empty or comment-only catch blocks fail.",
  "remediation": "Re-throw the error, wrap it with `new HandlerError(message, { cause: err })`, or log via `ctx.logger.error({ err }, 'handler failed')` before returning a 5xx. See docs/architecture/error-handling.md."
}
```

Six weeks later, the on-call dashboard shows no silent-handler-failure incidents and the rule's hit count has stayed at zero for the last fifteen PRs. Retirement candidate: the convention has stuck; the rule has done its job. Either delete it or move it to a lower-severity advisory log.

## When this backfires

- Premature promotion: encoding after one or two occurrences freezes a hypothesis as a rule. Suppression comments proliferate and the rule's signal degrades.
- Wrong enforcement layer: a semantic check forced into a regex linter fires on every legitimate exception; get the layer wrong and the rule becomes the new recurring noise source.
- Remediation text omitted or stale: a rule without "what to do instead" is a finger-wag, not the [structured remediation](../patterns/agent-design/feedback-capability-equalizer.md) that closes the loop. Developers and agents both stall, suppress, or copy-paste workarounds.
- No retirement discipline: the lint stack accumulates. Adherence degrades as instruction volume grows: context rot means models recall earlier rules less accurately as context fills ([Anthropic context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)). Priority saturation makes individual rules unreliable.

## Key Takeaways

- Log each occurrence with a link to its PR as it happens; reconstructing the count later turns the three-or-more threshold into a guess.
- Watch suppression comments as a signal: a rule that needs frequent overrides sits at the wrong layer. Move a safety-layer violation to a [pre-completion checklist](../verification/pre-completion-checklists.md) instead of suppressing it in a linter.
- Write the remediation text before the check. If you cannot state the fix in one line, the check is not ready to encode.
- The same logic applies upstream: a CLAUDE.md rule the agent keeps missing is itself a promotion candidate, not just a repeated PR comment.
- A hit count trending to zero over many PRs is retirement evidence; one quiet PR is not. Retire on the trend, not a single data point.

## Related

- [Learned Review Rules](learned-review-rules.md) — adjacent automation: the reviewer agent extracts rules from accept/reject signals
- [Deferred Standards Enforcement via Review Agents](deferred-standards-enforcement.md) — where post-hoc-checkable standards live once promoted out of CLAUDE.md
- [Feedback as Capability Equalizer](../patterns/agent-design/feedback-capability-equalizer.md) — why structured remediation text outperforms raw error output
- [Pre-Completion Checklists](../verification/pre-completion-checklists.md) — one of the encoding layers for promoted rules
- [Incident-to-Eval Synthesis](../verification/incident-to-eval-synthesis.md) — the production-failure analogue of this review-time loop
- [Harness Impermanence](../patterns/agent-design/harness-impermanence.md) — the retirement discipline that keeps promoted rules from accumulating
- [Standards as Agent Instructions](../instructions/standards-as-agent-instructions.md) — the priority-saturation failure mode that retirement prevents
- [Enforcing Agent Behavior with Hooks](../instructions/enforcing-agent-behavior-with-hooks.md) — deterministic enforcement layer for promoted rules
