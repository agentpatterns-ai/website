---
title: "Plan Mode for Knowledge Artifacts"
description: "Use plan mode as a forcing function for PRDs, strategy memos, and architectural briefs — where errors hide in reviewer fatigue and first-draft anchoring is expensive."
tags:
  - context-engineering
  - workflows
  - human-factors
  - claude
---

# Plan Mode for Knowledge Artifacts

> The plan is the work: for PRDs, strategy memos, and architectural briefs, freezing direction in a reviewed plan before any prose is generated compounds the gains plan mode already delivers for code.

Plan mode's value on knowledge artifacts is higher than on code, not lower. Prose errors do not fail a test suite — they hide in reviewer fatigue, anchor downstream readers on the first draft, and only surface after someone has already built on a wrong assumption. Hannah Stulberg, who runs her PM workflow through this pattern, states the thesis plainly: "The plan is not overhead. The plan is the work" ([Gupta × Stulberg](https://www.news.aakashg.com/p/claude-code-team-os)). The default failure mode is under-planning — letting the agent generate a first draft and then trying to correct it, instead of investing the time to get direction right before any prose is produced.

## Why Knowledge Artifacts Suffer More

Two mechanisms documented in the LLM behavioral literature compound for prose:

- **Action bias.** LLMs exhibit excessive switching and bias toward taking an action each round ([Maini, Goldstone & Tiganj, 2026, arXiv:2604.02578](https://arxiv.org/abs/2604.02578)). Stulberg translates the same finding to the tool surface: "Claude's bias for action is removed" once plan mode is engaged ([source](https://www.news.aakashg.com/p/claude-code-team-os)).
- **Reflection-before-production.** Structured self-reflection significantly improves LLM problem-solving performance (p < 0.001) ([Renze & Guven, 2024, arXiv:2405.06682](https://arxiv.org/abs/2405.06682)). Plan mode forces a reflect-then-act decomposition before any token of output is generated.

For code, a failing test catches a misread intent. For a PRD or strategy memo, no such gate exists — the reader is the gate, and the reader is fatigued. The reflection pass has to happen before the draft.

## Activating Plan Mode

Shift+Tab cycles Normal → Auto-Accept → Plan; the status bar reads `⏸ plan mode on` when active. Equivalent entry points: `claude --permission-mode plan`, the `/plan` command, or `"defaultMode": "plan"` in `.claude/settings.json` ([Claude Code common workflows](https://code.claude.com/docs/en/common-workflows#use-plan-mode-for-safe-code-analysis)). Press **Ctrl+G** to open the pending plan in your editor before accepting it — the concrete edit-before-drafting step.

## The Plan-Mode Posture

For knowledge artifacts, the plan-mode gate replaces first-draft generation with three disciplined moves:

- **Parallel research subagents.** For long-form docs, one agent reading forty context files and writing the draft loses to a fan-out where "each agent writes to a temp file" and "the orchestrating agent compiles the final document from temp files" ([source](https://www.news.aakashg.com/p/claude-code-team-os)). The plan enumerates the subagent tasks; execution happens after acceptance.
- **`AskUserQuestion` to push back on framing.** Plan mode uses `AskUserQuestion` verbatim to gather requirements and clarify goals before proposing a plan ([common workflows](https://code.claude.com/docs/en/common-workflows#use-plan-mode-for-safe-code-analysis)). Stulberg inverts the default use: "invite Claude to push my thinking … use the ask-user-question tool to push me on my thinking and help me consider other angles" ([source](https://www.news.aakashg.com/p/claude-code-team-os)). The agent is a thinking partner, not a producer.
- **Self-verification clauses in the plan.** Commit the plan to require cited sources, linkable URLs, and a named audience before prose is generated. Plan mode is a prompt wrapper, not a sandbox — Armin Ronacher's teardown shows the read-only constraint is enforced via system reminders, not technical gating ([Ronacher, 2025](https://lucumr.pocoo.org/2025/12/17/what-is-plan-mode/)). The reminders still cover the author who would otherwise under-specify.

## When NOT to Use

Plan mode is a ritual tax when the artifact is shorter than the plan would be, or when write-to-think iteration is the point:

- **Short or templated artifacts.** Standup updates, single-page memos, fixed-template postmortems. Anthropic's own caveat: if you "could describe the diff in one sentence, skip the plan" ([best practices](https://code.claude.com/docs/en/best-practices)).
- **High-iteration exploratory drafts.** Discovery writing where the author is working out what they think — plan mode freezes direction before the thinking has happened.
- **Strong outline discipline.** Practitioners already writing tight structured prompts can capture most of the same benefit with a plain markdown plan file on disk — Armin Ronacher prefers this for control ("I feel like I'm more in control of that experience if I have a file on disk somewhere that I can see, that I can read, that I can review, that I can edit before actually acting on it") while explicitly acknowledging that plan mode's end-of-plan user prompt is UX his approach does not replicate ([Ronacher, 2025](https://lucumr.pocoo.org/2025/12/17/what-is-plan-mode/)).
- **Known friction modes.** Users have requested an opt-out because automatic plan-mode entry interrupts workflows and lacks a configuration switch ([claude-code#30042](https://github.com/anthropics/claude-code/issues/30042)). Separate bug reports document plan mode breaking the CLI message-routing path ([#29725](https://github.com/anthropics/claude-code/issues/29725)) and context auto-compaction re-entering plan mode without user request ([#29956](https://github.com/anthropics/claude-code/issues/29956)).

## When the Recommendation Backfires

Plan-mode-for-PRDs underperforms a write-to-think workflow under three specific conditions:

- **Fast-moving discovery.** When the author is still working out what the artifact even is, an over-specified plan freezes direction before the thinking has happened — every accepted plan becomes a constraint on learning the next iteration would have surfaced.
- **Low-fidelity orchestrator synthesis.** Parallel research subagents only pay off if the orchestrator faithfully composes their temp-file outputs. When subagents return overlapping or contradictory findings and the orchestrator silently picks one, the plan-mode posture produces a confidently-wrong synthesis that single-agent reading would have surfaced as ambiguity.
- **Plan-file drift after acceptance.** A plan committed at hour zero becomes stale by hour twenty as the customer evidence shifts, the metrics resolve differently, or scope contracts. Without a supersession discipline ([plan files as resumable artifacts](plan-files-resumable-artifacts.md)), the accepted plan keeps anchoring the draft against reality the author has already moved past.

## Example

Stulberg's PRD workflow: Shift+Tab twice to enter plan mode, then have the agent dispatch parallel research subagents across `product/customers/` call notes, relevant metrics queries in `analytics/`, and prior PRDs in `product/specs/`. Each subagent writes a summary to a temp file. The orchestrator compiles findings and uses `AskUserQuestion` to surface the tensions — gaps in the customer evidence, metrics that contradict the hypothesis, prior decisions that constrain scope. Ctrl+G opens the proposed plan in the editor; the author edits the target audience, adds self-verification clauses ("cite a customer call for each user-need claim"), and accepts. Only then does the agent exit plan mode and draft the PRD ([source](https://www.news.aakashg.com/p/claude-code-team-os)). The plan file itself is committed under `product/specs/` and reused on the next PRD — the plan-as-artifact is covered in [plan files as resumable artifacts](plan-files-resumable-artifacts.md).

## Key Takeaways

- On knowledge artifacts, plan mode's forcing function matters more than on code: there is no failing test, only a fatigued reader.
- The mechanism is action-bias suppression plus reflect-before-produce — externally validated, not tool-specific magic.
- The plan-mode posture is parallel research, `AskUserQuestion` as a pushback tool, and self-verification clauses — not a modal UI ritual.
- Skip it for short, templated, or exploratory drafts; for strong-outline authors, a plain markdown plan file reproduces the benefit.
- Plan mode is a prompt wrapper. The value comes from the decomposition, which is portable — the Claude-specific mode just automates the habit.

## Related

- [Team OS](index.md) — the framework this page is part of
- [Cross-functional knowledge artifacts](cross-functional-artifacts.md) — the PRD/strategy-memo framing this pattern feeds into
- [Plan files as resumable artifacts](plan-files-resumable-artifacts.md) — the persisted artifact plan mode produces
- [Self-explanation loop](self-explanation-loop.md) — the reflection mechanism plan mode also engages
- [Plan mode](../../workflows/plan-mode.md) — the atomic workflow page
- [Plan-first loop](../../workflows/plan-first-loop.md) — the iteration shape and its backfire conditions
- [Strategy over code generation](../../human/strategy-over-code-generation.md) — why the author's leverage has shifted to the plan
- [Critic agent plan review](../../agent-design/critic-agent-plan-review.md) — a different mechanism (dual-model review) for the same goal
