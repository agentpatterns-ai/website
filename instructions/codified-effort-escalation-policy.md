---
title: "Codified Effort and Escalation Policy in the Instruction File"
term: "Codified Effort Policy"
description: "Encode a default-cheap, escalate-on-evidence effort and model-routing policy in CLAUDE.md or AGENTS.md so the cheap path is the default and survives context switches."
tags:
  - instructions
  - cost-performance
  - tool-agnostic
aliases:
  - codified effort and escalation policy
  - default-cheap effort policy
  - escalate-on-evidence routing policy
last_reviewed: 2026-07-03
maturity: adopted
---

# Codified Effort and Escalation Policy in the Instruction File

> Write the default-cheap, escalate-on-evidence effort and model-routing rule into the instruction file so the cheap path is the default, not an operator's per-task choice.

A codified effort policy is a written rule in your instruction file that makes the cheap path the default and escalates only on evidence. The lever is the file, not per-task willpower. When a cheaper, near-flagship model lands, switching the default captures part of the saving; writing the rule into the harness captures the rest, because it then applies on every task without anyone remembering to.

## What to encode

Three rules, written once into `CLAUDE.md`, `AGENTS.md`, or the settings file:

- Match effort to task. Default to a middle effort level, drop to the lowest for formatting, renames, and boilerplate, and reserve the top level for hard debugging, multi-file refactors, and architecture. Claude Code exposes `low`, `medium`, `high`, `xhigh`, and `max`, where lower effort is faster and cheaper and higher effort reasons deeper ([Claude Code — model configuration](https://code.claude.com/docs/en/model-config)). Set the default with `effortLevel` in the settings file, or per-agent with `effort` frontmatter. This generalizes: Copilot [custom agents](../training/copilot/model-selection.md) pin a model in `.agent.md` frontmatter, so the rule can live in any tool's config surface.
- Escalate on evidence, not habit. Name the trigger — escalate after N failed verification runs, or when a cheap model's partial trajectory shows it thrashing. A written trigger beats per-task judgment, and it composes with runtime routing like [trajectory-conditioned escalation](../patterns/agent-design/trajectory-conditioned-model-escalation.md).
- Default cheap, spend on proof. The cheap model and effort level run first; the strong path is the exception the rule forces you to justify, not the reflex.

## The high-effort trap

Reaching for the top effort level is a signal to check, not a default. `max` runs with no constraint on token spending ([Claude Code — model configuration](https://code.claude.com/docs/en/model-config)), and reasoning tokens are billed and add latency in proportion to length. Continuous maximum effort scored 53.9% against 63.6% for uniform-high reasoning on Terminal Bench 2.0, losing to timeouts ([LangChain, 2026](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)). When a cheaper model needs its highest effort to match a flagship, the flagship at moderate effort may be both cheaper and better — so treat the reach for `max` as the prompt to re-check routing, not the answer. Raising effort only pays where the model has headroom below its ceiling and the failure is a reasoning failure ([Mehta, 2026](https://arxiv.org/abs/2607.02436)); it is otherwise the [reasoning-overuse](../patterns/anti-patterns/reasoning-overuse.md) anti-pattern.

## Why it works

A rule in the instruction file is re-applied by the harness on every turn and session, so the cheap default holds without the operator remembering it after a context switch. Effort settings persist across sessions and instruction files are re-read after compaction ([Claude Code — model configuration](https://code.claude.com/docs/en/model-config)), while per-task judgment does not survive handoffs — the same durability argument behind [convention over configuration](convention-over-configuration.md). The escalate-on-evidence half works because task difficulty is trajectory-dependent and not recoverable from the description alone: conditioning the model choice on observed failure is provably never worse than a fixed a-priori choice, and strictly better when the cheap attempt is informative ([SWE-Router, arxiv 2607.00053](https://arxiv.org/abs/2607.00053)).

## When this backfires

- No cheap-solvable tail. If every task needs the flagship, the cheap-first pass is pure overhead; default to the strong model instead.
- No observable escalation signal. Design docs and prose reviews give the rule nothing to key on — cascade-style escalation needs binary feedback like tests or types ([model selection and routing](../training/copilot/model-selection.md)).
- Rework outruns the saving. A cheap model's "almost right" output can cost more in retries than one clean frontier call ([getunblocked, 2026](https://getunblocked.com/blog/model-routing-coding-agents/)).
- Latency-sensitive loops. The cheap attempt plus escalation adds serial latency an interactive user feels.
- Stale policy. A tier table that routes hard work down thrashes; the rule is only as good as its last self-test.

## Validate on your own tasks

Published benchmarks do not predict your codebase's outcomes — a short side-by-side on your own representative tasks tells you which task types can safely route down more reliably than any leaderboard ([model preference fallacy](../fallacies/model-preference-fallacy.md)). Encode what the self-test proves, then re-test when the model roster changes.

## Example

A minimal policy block in `CLAUDE.md` or `AGENTS.md` that the harness applies on every task:

```markdown
## Model and effort policy
- Default effort: `medium`. Drop to `low` for formatting, renames, and boilerplate.
- Raise to `high` or `xhigh` only for multi-file refactors, hard debugging, or architecture.
- Escalate to the flagship model after 2 failed verification runs (tests, lint, types) — not before.
- Reaching for `max` is a review trigger: first check whether the flagship at `high` is cheaper and better.
```

The block names the default, the escalation trigger, and the high-effort review check, so the cheap path is enforced by the file instead of the operator. Tune the tiers to what your own self-test proves, not to a published benchmark.

## Key takeaways

- Codify the effort and escalation rule in the instruction file; the durable win is that the harness re-applies it every task, surviving compaction and handoffs.
- Match effort to task, default cheap, and escalate on a named evidence trigger — a written rule beats per-task judgment because difficulty is not readable from the description alone.
- The high-effort trap: `max` on a cheaper model can cost more and score worse than a flagship at moderate effort — treat the reach for `max` as a routing check, not a default.
- Raising effort pays only where the model has headroom and the failure is a reasoning failure; otherwise it is reasoning overuse.
- Validate route-down decisions on your own representative tasks, then re-test on every model-roster change.

## Related

- [Heuristic-Based Effort Scaling in Agent System Prompts](../patterns/agent-design/heuristic-effort-scaling.md) — encode per-tier effort ceilings for multi-agent work; the complement that sizes effort from task cues
- [Reasoning Effort Over Tool Scaffolding for First-Try Reliability](../patterns/agent-design/reasoning-effort-over-tool-scaffolding.md) — evidence that the effort dial, not extra tools, moves first-try reliability
- [Trajectory-Conditioned Model Escalation (SWE-Router)](../patterns/agent-design/trajectory-conditioned-model-escalation.md) — the runtime escalation signal a codified "escalate on evidence" rule points to
- [Convention Over Configuration for Agent Workflows](convention-over-configuration.md) — the broader case for encoding decisions into the harness so agents follow patterns rather than re-decide
- [Indiscriminate Structured Reasoning](../patterns/anti-patterns/reasoning-overuse.md) — the failure mode when effort is spent past the point it helps
- [Advisory Prompts Distilled from Reasoning Traces](advisory-prompts-from-reasoning-traces.md) — what the cheap, reasoning-off branch of this policy can and cannot recover through the prompt alone
