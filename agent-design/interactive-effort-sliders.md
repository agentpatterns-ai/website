---
title: "Interactive Effort Sliders: Per-Turn Reasoning-Budget Controls"
description: "Expose reasoning budget as an interactive, per-turn operator control — the third option alongside static effort config and heuristic effort scaling."
tags:
  - agent-design
  - cost-performance
aliases:
  - interactive effort slider
  - per-turn reasoning budget control
---

# Interactive Effort Sliders: Per-Turn Reasoning-Budget Controls

> Expose reasoning budget as an interactive, per-turn operator control — the third option alongside static effort config and heuristic effort scaling.

## The Primitive

An interactive effort slider lets an operator dial reasoning budget between turns without re-launching the session or re-priming context. Claude Code v2.1.111 (2026-04-16) introduced this form: running `/effort` with no arguments opens a slider with arrow-key navigation and Enter to confirm ([Claude Code changelog](https://code.claude.com/docs/en/changelog)). The same control surface appears in the `/model` picker, where left/right arrow keys move the effort slider while a model is highlighted ([model configuration](https://code.claude.com/docs/en/model-config#adjust-effort-level)).

Three operator inputs share the same semantics but differ in contract:

| Option | Who decides | When decided |
|--------|-------------|--------------|
| Static effort config | Operator (once) | Session start via `--effort`, `settings.effortLevel`, or `CLAUDE_CODE_EFFORT_LEVEL` |
| [Heuristic effort scaling](heuristic-effort-scaling.md) | Agent | Per query, based on system-prompt tier classification |
| Interactive slider | Operator (live) | Per turn, mid-session |

The slider occupies the third slot: human judgment on live task difficulty, not policy set in advance and not agent self-classification.

## Levels and Fallback

Opus 4.7 exposes five levels — `low`, `medium`, `high`, `xhigh`, `max`; Opus 4.6 and Sonnet 4.6 expose four (no `xhigh`) ([model configuration](https://code.claude.com/docs/en/model-config#adjust-effort-level)). Setting a level the active model does not support silently falls back to the highest supported level at or below the target — `xhigh` runs as `high` on Opus 4.6.

`low`, `medium`, `high`, and `xhigh` persist across sessions. `max` applies only to the current session unless set via `CLAUDE_CODE_EFFORT_LEVEL`, because `max` has no cap on token spend ([model configuration](https://code.claude.com/docs/en/model-config#adjust-effort-level)). Precedence: environment variable overrides configured level overrides model default; skill or subagent frontmatter `effort:` overrides the session level but not the environment variable.

## Why It Works

Effort levels control adaptive reasoning — the model decides per-step whether and how much to think based on task complexity ([model configuration](https://code.claude.com/docs/en/model-config#adjust-effort-level)). Task difficulty is unevenly distributed across turns in a human-in-the-loop session: planning and verification benefit from deeper reasoning while mechanical edits do not. LangChain's Terminal Bench 2.0 experiments quantified this asymmetry — an `xhigh-high-xhigh` reasoning sandwich reached 66.5% completion, uniform high reached 63.6%, and uniform maximum reached only 53.9% because of agent timeouts ([LangChain: Improving Deep Agents with Harness Engineering](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)).

The slider lets an operator apply that same asymmetry reactively rather than architecturally. Before an interactive form existed, an operator who spotted a hard turn mid-session had to quit and relaunch with `--effort`, losing session context. Runtime adjustment collapses that friction.

## When the Slider Pays Off

- **Tasks with sharply uneven difficulty across turns** — an exploratory debug that hits one deep reasoning moment in a stream of routine edits.
- **Human-in-the-loop sessions** — an operator who can see the task form and match compute to observed difficulty.
- **Turn-level cost steering** — when the budget is operator-held rather than pre-allocated, the slider is the direct control.

## When It Backfires

**Long-horizon autonomous runs.** No operator is present turn-by-turn, so the slider's core value — human judgment on live difficulty — is unavailable. [Heuristic effort scaling](heuristic-effort-scaling.md) or phase-based [reasoning budget allocation](reasoning-budget-allocation.md) fit better.

**Cost-governed team deployments.** Interactive adjustment breaks cost predictability because two operators solving similar problems at different slider positions produce diverging spend. Pin `effortLevel` in managed settings when session cost modeling matters more than per-turn ergonomics.

**Anchoring on the last setting.** Persistence across sessions is documented for `low`, `medium`, `high`, and `xhigh` ([model configuration](https://code.claude.com/docs/en/model-config#adjust-effort-level)). An operator who ratchets up for one hard turn and forgets to ratchet back silently over-spends on subsequent routine turns.

**Over-spending early on capped tiers.** Pro, Max, and Team Premium plans can hit usage thresholds that auto-fallback Opus to Sonnet ([model configuration](https://code.claude.com/docs/en/model-config#default-model-setting)). Dialling `max` on opening turns can degrade session capability before the hardest step arrives; `max` is documented as "prone to overthinking" ([model configuration](https://code.claude.com/docs/en/model-config#adjust-effort-level)).

**Eval reproducibility.** If evals need a fixed effort level for run-to-run comparability, slider optionality becomes a drift source. Lock the level via `CLAUDE_CODE_EFFORT_LEVEL` — the environment variable has highest precedence ([model configuration](https://code.claude.com/docs/en/model-config#adjust-effort-level)).

## Audit and Cost Implications

Cost-per-turn becomes operator-controlled rather than policy-controlled. An operator watching one session can hold total spend directly, but the audit trail lives in transient UI interactions rather than a static config value. For enterprise deployments where billing attribution or compliance matters, pin `effortLevel` in managed settings so the slider is effectively read-only ([model configuration](https://code.claude.com/docs/en/model-config)).

## Example

A debugging session on Opus 4.7 uses the slider to match compute to observed difficulty:

```
# session starts at xhigh (Opus 4.7 default)
> investigate why the auth middleware drops the session cookie on /callback

# routine grep and read turns — dial down to conserve budget
/effort medium
> read src/middleware/auth.ts and src/routes/callback.ts

# model suggests a plausible fix, but the test suite still fails
# this is the hard turn — dial up
/effort max
> the cookie is set in the response but missing on the next request.
  walk through the full request lifecycle and find where it gets dropped.

# fix landed, verification phase
/effort xhigh
> write a regression test that fails without the fix
```

The operator matches slider position to turn type: `medium` for reads, `max` for the root-cause investigation, `xhigh` for verification. The same session with a fixed `xhigh` would have spent more on the read turns; with a fixed `high` it might have missed the cross-layer reasoning on the hard turn.

## Key Takeaways

- Interactive `/effort` is the third operator input alongside static config and heuristic scaling — the one supplying live human judgment.
- Opus 4.7 adds `xhigh` between `high` and `max` and is the default on Opus 4.7 across plans ([model configuration](https://code.claude.com/docs/en/model-config#adjust-effort-level)).
- `low`, `medium`, `high`, `xhigh` persist across sessions; `max` is session-scoped unless set via `CLAUDE_CODE_EFFORT_LEVEL`.
- Precedence: environment variable > configured level > model default; frontmatter `effort:` overrides session but not env var.
- Failure modes: long-horizon autonomy, team cost governance, anchoring, early over-spend on capped tiers, eval drift. Pin via managed settings or environment variable when those dominate.
- Running `max` throughout degrades completion rate (53.9% vs. 66.5% for the `xhigh-high-xhigh` sandwich on Terminal Bench 2.0) — unconstrained slider-up is not a free win ([LangChain](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)).

## Related

- [Heuristic-Based Effort Scaling in Agent Prompts](heuristic-effort-scaling.md) — the agent-driven alternative: system-prompt tiers decide effort rather than the operator
- [Reasoning Budget Allocation: The Reasoning Sandwich](reasoning-budget-allocation.md) — phase-based allocation (plan, execute, verify) as the architectural alternative to runtime dialling
- [Cost-Aware Agent Design: Route by Complexity, Not Habit](cost-aware-agent-design.md) — the broader cost-routing context where effort sits alongside model selection
- [Steering Running Agents](steering-running-agents.md) — companion primitive for mid-session operator input on direction rather than compute
- [Agent Turn Model](agent-turn-model.md) — the turn abstraction that makes per-turn controls meaningful
- [The Think Tool](think-tool.md) — mid-stream reasoning checkpoint; complementary to extended-thinking budget
