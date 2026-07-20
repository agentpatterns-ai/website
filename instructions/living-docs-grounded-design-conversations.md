---
title: "Living-Docs-Grounded Agent Design Conversations"
description: "Point the agent at current domain docs during the design Q&A — the interview anchors in shared vocabulary and surfaces doc drift in the same loop."
term: "Living-Docs-Grounded Agent Design Conversations"
tags:
  - instructions
  - context-engineering
  - tool-agnostic
aliases:
  - docs-grounded grill
  - q&a grounded in living docs
  - grill-with-docs pattern
last_reviewed: 2026-05-27
maturity: established
---

# Living-Docs-Grounded Agent Design Conversations

> Hand the agent your current domain glossary and architectural decision records during the design interview — the docs become both a question generator and a vocabulary checker, and stale entries surface as the conversation runs.

The technique applies under three conditions: the codebase has non-trivial domain vocabulary not already encoded by types, at least a thin `CONTEXT.md`-style glossary and `docs/adr/` set exists (or is created lazily during the session), and the change is large enough that wrong terminology will leak into code. Outside those conditions, anchoring an interview in prose docs adds cost without value or propagates stale definitions into the new design ([Gloaguen et al., 2026](https://arxiv.org/abs/2602.11988); [MemU, *Context Drift Causes 65% of Enterprise AI Agent Failures*](https://memu.pro/blog/ai-context-drift-enterprise-agent-memory)).

## How the pattern differs from sibling techniques

Four agent-facing patterns touch design conversations and domain language. They differ in when the docs enter the loop:

| Pattern | Docs role | When |
|---------|-----------|------|
| [Grill Me](../patterns/agent-design/grill-me-technique.md) | None | Pre-implementation interview, no domain anchor |
| Living-docs-grounded Q&A (this page) | Read live; updated inline | During the interview, before any plan exists |
| [Ubiquitous Language for AI Plans](ubiquitous-language-for-ai-plans.md) | Read at planning time | After Q&A, when the plan is being authored |
| [Interactive Clarification](../patterns/agent-design/interactive-clarification-underspecified-tasks.md) | None | When the agent detects an information gap during execution |

Matt Pocock's `/grill-with-docs` skill puts the second row into practice ([Pocock, *grill-with-docs SKILL.md*](https://github.com/mattpocock/skills/blob/main/skills/engineering/grill-with-docs/SKILL.md)). Pocock made docs-anchored interrogation his default ideation entry point in April 2026 — `/domain-model` "replaces /grill-me, integrates some DDD concepts and adds docs & ADR's during discussions" ([@mattpocockuk](https://x.com/mattpocockuk/status/2045110469426323900)).

## The artifact contract

Three files participate; the skill creates them lazily and keeps them short ([Pocock, *grill-with-docs SKILL.md*](https://github.com/mattpocock/skills/blob/main/skills/engineering/grill-with-docs/SKILL.md)):

| Artifact | Purpose during the interview |
|----------|------------------------------|
| `CONTEXT.md` | Glossary for one bounded context — the agent's vocabulary check |
| `docs/adr/` | Architectural decisions the agent re-reads so it stops re-proposing rejected options |
| `CONTEXT-MAP.md` | Cross-context index — only when multiple bounded contexts share the repo |

`CONTEXT.md` is purely a glossary, not a spec. The agent updates it inline as terms resolve — "don't batch these up — capture them as they happen" ([DeepWiki: *Aligning Plans with Docs*](https://deepwiki.com/mattpocock/skills/7.1-aligning-plans-with-docs-(grill-with-docs))). The ADR set is gated by the three-condition test (hard to reverse, surprising without context, real trade-off) so it does not accumulate noise.

## Why it works

The mechanism has two independently sourced legs.

Rigor comes first. Eric Evans' original ubiquitous-language argument: when prose, plans, and code share names, terminology collisions surface at design time as conflicts instead of at implementation time as bugs ([Fowler, *Ubiquitous Language*](https://martinfowler.com/bliki/UbiquitousLanguage.html)). Grounding the interview rather than the plan moves collision detection one step earlier — the agent challenges new terms against the glossary before any plan is drafted ([DeepWiki: *Aligning Plans with Docs*](https://deepwiki.com/mattpocock/skills/7.1-aligning-plans-with-docs-(grill-with-docs))).

Drift detection comes second. The agent uses docs as both a question generator — probing where the change touches existing concepts — and a consistency checker — flagging when the developer's answer uses a different word than the glossary. The same loop surfaces glossary entries that no longer match the code ([DeepWiki: *Aligning Plans with Docs*](https://deepwiki.com/mattpocock/skills/7.1-aligning-plans-with-docs-(grill-with-docs))). One session yields three outputs (resolved terminology, detected doc drift, surfaced design gaps) where Grill Me yields one.

The root cause this addresses is widely reported: AI coding agents amplify whatever vocabulary they receive, collapsing business terms into framework terms unless a formalised domain language constrains them ([Brown, *AI Coding Assistants and the Erosion of Ubiquitous Language*](https://dev.to/dbrown/ai-coding-assistants-and-the-erosion-of-ubiquitous-language-301a); [Rezki, *Solving AI Agent Ambiguity with DDD's Ubiquitous Language*](https://earezki.com/ai-news/2026-05-21-your-agent-keeps-using-that-word-/)).

## When this backfires

The technique fails — sometimes silently — under four conditions.

- Docs are systematically stale: a glossary or ADR set untouched for six months in a fast-moving codebase becomes a vector for context drift, the failure mode MemU's 2026 enterprise survey ranks as the dominant agent-deployment killer ([MemU, *Context Drift Causes 65% of Enterprise AI Agent Failures*](https://memu.pro/blog/ai-context-drift-enterprise-agent-memory)). The interview is grounded in obsolete terms and the developer spends it refuting docs instead of designing.
- Docs are too thin: a `CONTEXT.md` with three entries gives the agent fragments to extrapolate from. It invents domain terms that sound like they belong — the "follows instructions even when wrong" dynamic Gloaguen et al. observed with auto-generated context files ([Gloaguen et al., 2026](https://arxiv.org/abs/2602.11988); covered in [Evaluating AGENTS.md](evaluating-agents-md-context-files.md)).
- Domain is already encoded in types: Rust enums, TypeScript discriminated unions, or a tight Pydantic schema enforce vocabulary at compile time. A prose glossary adds a looser second source of truth that can disagree with the strict one. The agent must pick and may pick wrong.
- Compliance over signal: the [instruction compliance ceiling](instruction-compliance-ceiling.md) bites. A 50-term glossary makes the agent recite every term back, drowning the design signal. Keep the artifact lazy and short — Pocock's skill creates files only when the first term resolves ([Pocock, *grill-with-docs SKILL.md*](https://github.com/mattpocock/skills/blob/main/skills/engineering/grill-with-docs/SKILL.md)).

Gloaguen quantifies the upside ceiling: human-written context files lifted success only ~4% on the AGENTbench suite at a 19% inference-cost premium ([Gloaguen et al., 2026](https://arxiv.org/abs/2602.11988)). The Q&A-grounded variant earns its keep when the conditions above hold; it does not justify itself in greenfield projects or scripts.

## Example

A team adopts the `/grill-with-docs` skill on a video-platform codebase. A developer describes a feature: "add pitches to standalone videos." The agent reads `CONTEXT.md` before asking its first question:

```text
CONTEXT.md defines:
  Standalone Video: video with lessonId IS NULL

Your change introduces "pitches" attached to standalone videos.
Resolve before we proceed:
  (a) Sub-term: "Pitched Standalone Video" / "Unattached Standalone Video"
  (b) New top-level: "Pitched Video" as sibling of "Standalone Video"
  (c) Rename: "Standalone Video" is the wrong concept and pitches replace it
```

The developer picks (a); the agent updates `CONTEXT.md` inline with the two sub-terms during the same turn ([DeepWiki: *Aligning Plans with Docs*](https://deepwiki.com/mattpocock/skills/7.1-aligning-plans-with-docs-(grill-with-docs))). A later question — "what happens when a pitched standalone video is deleted?" — produces a hard-to-reverse decision (`ON DELETE RESTRICT`) that earns an ADR, so the next session does not re-litigate `ON DELETE CASCADE` ([Pocock, *grill-with-docs SKILL.md*](https://github.com/mattpocock/skills/blob/main/skills/engineering/grill-with-docs/SKILL.md)).

The same session surfaces a year-old glossary entry — `Lesson Video` is still defined as `mediaType = 'lesson'` but the code now uses `kind = 'lesson_video'`. The agent flags the mismatch; the developer pairs the workflow with the [Instruction File Fact-Checker](../workflows/instruction-file-fact-checker.md) to close drift outside the interview.

## Key Takeaways

- Anchor the *interview*, not just the plan, in living docs — that is what makes the pattern distinct from `ubiquitous-language-for-ai-plans.md` and from undirected `grill-me`.
- Keep the artefact contract small: a glossary, an ADR set gated by three conditions, and an optional cross-context index — created lazily during the session, not pre-written ([Pocock, *grill-with-docs SKILL.md*](https://github.com/mattpocock/skills/blob/main/skills/engineering/grill-with-docs/SKILL.md)).
- One session yields three outputs — resolved terminology, detected doc drift, surfaced design gaps — where Grill Me alone yields one.
- The pattern is Qualified, not universal: it earns its cost only when domain vocabulary is non-trivial, docs are kept fresh, and types do not already enforce the language. Outside those conditions, expect Gloaguen-style cost-without-value or MemU-style drift propagation.

## Related

- [Ubiquitous Language for AI Plans](ubiquitous-language-for-ai-plans.md)
- [Grill Me: Developer-Initiated Plan Interrogation](../patterns/agent-design/grill-me-technique.md)
- [Interactive Clarification for Underspecified Tasks](../patterns/agent-design/interactive-clarification-underspecified-tasks.md)
- [Evaluating AGENTS.md: When Context Files Hurt More Than Help](evaluating-agents-md-context-files.md)
- [Scheduled Instruction File Fact-Checker](../workflows/instruction-file-fact-checker.md)
