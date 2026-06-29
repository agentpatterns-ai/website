---
title: "Encoding Product-Design Taste into Agent Context"
term: "Encoding Product-Design Taste"
description: "Encode product-design conventions as observable decisions, mode-routed skill files, and explicit coverage gaps so generated UI is conventionally correct — paired with structural enforcement, never instead of it."
aliases:
  - Teaching Agents Product Design
  - Product-Design Skill Files
tags:
  - instructions
  - context-engineering
  - tool-agnostic
last_reviewed: 2026-06-28
maturity: emerging
---

# Encoding Product-Design Taste into Agent Context

> Encoded product-design decisions steer agents inside the design space that tokens and lint already enforce — not a replacement for them.

Coding agents produce functional UI but default to generic styling because the team's product decisions — spacing scales, component choices, copy voice — live in Slack, Figma, and review comments. The fix is to treat product decisions like code: keep them in the repo, review changes against them, and make them available to every agent there ([Vercel, 2026-06-25](https://vercel.com/blog/teaching-agents-product-design-at-vercel)).

## When This Works — Three Preconditions

The technique applies when:

1. Structural rails exist first. Design tokens, a typed component library, and lint rules already prevent non-token colors, unauthorised components, and off-scale spacing. Encoded conventions steer inside the allowed space; they do not replace the wall ([PairCoder, 2026](https://paircoder.ai/blog/enforcement-not-prompts/)).
2. Decisions are observable. Every rule names a checkable form — `"Destructive actions use Verb + Noun"`, `"Selects with 2-3 static options are Radio buttons"`. Adjective-only guidance ("clear, polished") is not verifiable; this is the failure the technique exists to avoid ([Vercel, 2026-06-25](https://vercel.com/blog/teaching-agents-product-design-at-vercel)).
3. The surface is reused. Repeatedly-extended product surfaces amortise the authoring cost; a solo prototype does not.

If any precondition fails, skip the skill file and invest in tokens, lint, or component coverage first.

## What to Encode and Where

Vercel's `.agents/skills/product-design/` skill is the reference shape, separating judgment from execution ([Vercel, 2026-06-25](https://vercel.com/blog/teaching-agents-product-design-at-vercel)):

- `product-judgment.md` — workflow, user intent, mode resolution.
- `interface-quality.md` — visual implementation standards (spacing, hierarchy, component choice).
- `copy.md` — language conventions and voice.
- Surface-specific guidance — per-area files for decisions that do not generalise.
- `exemplars/pr-{name}.md` — shipped decisions worth repeating, linked to the establishing PR.
- `coverage-gaps.md` — areas the team has *not* decided about, so the agent does not pattern-match into a gap and invent policy.

The skill loads conditionally; persistent repository instructions (CLAUDE.md / AGENTS.md) tell the agent when to read it, which files to load, and which surfaces to skip.

## Mode-Based Routing

A single design skill loaded for every UI prompt produces scope creep: the agent reviews when asked to implement, rewrites copy when asked to harden. Vercel routes the skill into modes resolved from the user verb and artifact ([Vercel, 2026-06-25](https://vercel.com/blog/teaching-agents-product-design-at-vercel)):

| User verb / artifact | Mode | Loaded slice |
|---|---|---|
| "design", "explore" | Shape | product-judgment + surface guidance |
| "build", "implement" | Implement | interface-quality + exemplars |
| "review", "audit" | Review | all references + coverage-gaps |
| "rewrite copy" | Copy | copy.md only |
| "harden", "polish" | Harden | interface-quality + recent exemplars |

The `SKILL.md` directs: `"Resolve the mode from the user's verb and artifact before acting"`. Mode routing matches loaded context to the task's failure mode — the same principle behind [example-driven instructions](example-driven-vs-rule-driven-instructions.md) applied at the rule level.

## Specifying Taste

Observable constraints beat abstract adjectives. The decision-form that works is a checkable predicate the agent can self-verify:

- Good: `"Destructive actions use Verb + Noun"` — the agent can scan its output and check.
- Bad: `"Buttons should be clear"` — no operationalised meaning for "clear".

The DESIGN.md practitioner pattern ([Naya Moss](https://nayamoss.com/how-i-use-ai/teach-ai-agents-design-system)) captures the same shape at a smaller scale: a single Markdown file at repo root describing palette, typography, spacing, and usage rules, referenced from the project instruction file. Mode-routing and coverage-gap layers differentiate the Vercel-shape skill from a flat DESIGN.md.

Design tokens (`bg-card`, `text-foreground`, `space-4`) are the structural complement: the agent cannot pick a non-token color because there is no color choice to make ([Naya Moss](https://nayamoss.com/how-i-use-ai/teach-ai-agents-design-system)). The skill names *which* token to use; the token system enforces *that* a token is used.

## Verification — Three Layers

Encoded conventions are worth nothing without checks. Vercel runs three, weakest to strongest enforcement ([Vercel, 2026-06-25](https://vercel.com/blog/teaching-agents-product-design-at-vercel)):

1. Deterministic lint — encode patterns as ESLint rules. Vercel's example: flagging a Select with 2-3 static options and suggesting Radio buttons. This is where [guardrails beat guidance](guardrails-beat-guidance-coding-agents.md) — the rule cannot be ignored under context compaction.
2. Evals on fixtures — score before/after fixtures with holdouts, separating rule-correctness from shipped-code similarity. Conflating the two hides regressions.
3. Rendered verification — `"Verify the real surface… never claim visual verification from code alone"`. The agent checks loading states, responsive variants, keyboard navigation, and extreme-content behavior before claiming done.

## When This Backfires

- No structural rails. Adopting the skill before tokens, lint, or a component library exists produces a well-instructed agent that still ships generic UI — rules drop first under context compaction ([PairCoder, 2026](https://paircoder.ai/blog/enforcement-not-prompts/)). Encoded conventions cannot stop the agent from inventing a one-off color; tokens can.
- Adjective-only guidance. A skill of "clear, polished, intuitive" is uncheckable. It occupies context budget for no behavioral lift.
- Positive-directive bloat. On SWE-bench, positive directives individually degraded success while negative constraints helped — and random rules helped as much as expert-curated ones ([Zhang et al., 2026](https://arxiv.org/abs/2604.11088)). Treat encoded design as steering, not ceremony.
- Coverage-gap blindness. Without an explicit `coverage-gaps.md`, the agent extrapolates from the nearest exemplar into undecided domains — silence becomes accidental policy ([Vercel, 2026-06-25](https://vercel.com/blog/teaching-agents-product-design-at-vercel)).
- Small surface, throwaway work. Solo prototypes and single-route internal tools do not amortise authoring and maintenance cost.

## Why It Works

Encoded conventions narrow the agent's generation distribution to forms the team has decided about. The mechanism rests on two legs that structural enforcement alone does not deliver: observable rules give the agent a contract it can check against its own output before claiming done ([Vercel, 2026-06-25](https://vercel.com/blog/teaching-agents-product-design-at-vercel)); exemplars and coverage gaps cover workflow shape, copy voice, and surface judgment that lint cannot express. Mode routing keeps the loaded slice small enough that the contract survives context compaction — the same lift [domain-specific system prompts](domain-specific-system-prompts.md) get from worked examples in a specific domain.

## Key Takeaways

- Encoded design works when paired with design tokens and lint — not as a replacement for them.
- Observable, checkable rules ("Destructive actions use Verb + Noun") beat adjective-only guidance.
- Split the skill by concern (judgment, interface quality, copy) and route loading by user verb and artifact.
- Capture coverage gaps explicitly so silence is not mistaken for permission.
- Verify in three layers: deterministic lint, evals on before/after fixtures with holdouts, mandatory rendered checks.

## Related

- [Example-Driven vs Rule-Driven Instructions](example-driven-vs-rule-driven-instructions.md) — when concrete exemplars outperform abstract rules; the same trade-off applies to design taste.
- [Domain-Specific System Prompts with Concrete Examples](domain-specific-system-prompts.md) — worked examples in instructions produce consistent agent behavior in a specific domain; design taste is a domain.
- [Guardrails Beat Guidance: Rule Design for Coding Agents](guardrails-beat-guidance-coding-agents.md) — negative constraints individually help; positive directives individually hurt — informs which design rules to encode.
- [Enforcing Agent Behavior with Hooks](enforcing-agent-behavior-with-hooks.md) — the structural-rails complement: lint and hooks forbid what the skill cannot.
- [Encode Project Conventions in Distributed AGENTS.md Files](agents-md-distributed-conventions.md) — the broader pattern of encoding team conventions; design taste is one slice.
