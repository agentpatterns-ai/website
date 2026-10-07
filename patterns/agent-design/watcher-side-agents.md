---
title: "Watcher Side Agents: Give the Second Agent a Trigger It Did Not Pick"
term: "Watcher Side Agent"
description: "A concurrent, read-only agent that writes notes to the operator costs attention rather than tokens. Only a rule-fired trigger lets it stay silent on a clean run, and four conditions decide whether it pays at all."
tags:
  - agent-design
  - claude
  - human-factors
aliases:
  - watcher side agent
  - side agent
  - operator-addressed watcher
applies_to: "claude-code@2.x"
last_reviewed: 2026-10-06
maturity: emerging
status: current
---

# Watcher Side Agents: Give the Second Agent a Trigger It Did Not Pick

> A watcher side agent is advisory, so it costs operator attention, and only a rule-fired trigger lets it stay silent on a clean run.

A watcher side agent runs beside the main session, reads what the main agent is doing, and writes notes to the operator. It does not do the task and it cannot change anything. Claude Code 2.1.287 shipped one on 1 October 2026 as "a built-in mod where a side agent watches your back and flags things you or Claude might miss", enabled with `/plugin enable cc-plugin-you-should-know@builtin` and limited to "first-party sessions with telemetry on" ([Claude Code changelog](https://code.claude.com/docs/en/changelog)).

Three properties separate it from a review agent. It is concurrent rather than downstream. It reads the live session rather than a diff. Its output is advisory, delivered as "a note above the prompt" ([Mods overview](https://code.claude.com/docs/en/plugins/mods/overview)). That note is the watcher's entire output, so what decides whether it pays is the value of the operator's attention, not the cost of the side agent's tokens.

## When it earns its cost

Four conditions, and the evidence supports the pattern only where all four hold.

Run it on a session long enough that you have stopped reading every turn. Anthropic scopes its own watcher that way, to one that "watches your back while Claude works on longer tasks" ([Mods overview](https://code.claude.com/docs/en/plugins/mods/overview)). LivePlan, which gates an advisor on trajectory rules, fires its stagnation rule after "seven consecutive steps in the same phase", a threshold taken from uninstrumented runs whose average maximum same-phase length was 5.64 steps on resolved instances and 7.61 on unresolved ones ([Liu et al., 2026, arXiv:2608.06701v1](https://arxiv.org/abs/2608.06701v1)). A run shorter than seven steps cannot trip it.

Give it a trigger it does not choose. This is the decision the whole pattern turns on.

Reserve it for defect classes with no checkable predicate. Where a predicate exists, write the gate: a gate refuses and a note does not.

Check that somebody is at the prompt. An unattended run closes the only channel the watcher has.

## Why it works

A watcher does not work by being independent. It is a second imperfect detector over the same material, and the honest mechanism is additive coverage: "Any two imperfect, non-identical detectors raise union recall mechanically; the observed unions in fact fall below both pooled and within-artifact independence reference values" ([Song, 2026, arXiv:2610.01471v1](https://arxiv.org/abs/2610.01471v1)). Across 900 review sessions on 30 artifacts carrying 150 planted errors, one same-model fresh-session review paired with one from a top-tier cross-model reviewer under information restriction matched 85 of 150 errors, against 64 of 150 for two same-model fresh-session reviews. That 14.0pp gain carries a 95% confidence interval of 6.7 to 22.0. Both are set-level recalls over run 1, conditional on that study's automated matcher.

An agent checking its own work is the extreme case of a near-identical detector, and this project measures it. `routine-prompts/backlog-pipeline.md` Step 4a exists because "The pipeline subagent audits a page it wrote, and it reads the page as it meant it." The recorded result: "Three consecutive runs sent 24 self-audit PASS pages to this step, and all 24 failed it, with 46 HIGH findings between them". Improving the producer did not close the gap. The same file records that the self-audit prompt was rewritten mid-run to name the defect class, that producers then fixed more such defects themselves, "and every page still failed here."

That is also why the trigger decides whether the pattern pays. Judging and advising pull against each other: "an advisor prompted to diagnose and provide corrective advice is incentivized to find a problem", and one may "surface a problem that does not exist and impose misleading advice that derails a run that was, in fact, on track" ([arXiv:2608.06701v1](https://arxiv.org/abs/2608.06701v1)). That advisor steered an executor rather than informing a person, so the carry-over to an operator-addressed note is an argument from the same incentive and not a second measurement. The incentive is the part that carries. A rule-fired watcher is asked what the operator should know given this specific signal, and nothing is an available answer to that. A standing watcher is asked whether anything is wrong, and nothing is not.

## When this backfires

A watcher with no gate on its own consultation produces notes on healthy runs. SAGE, a prior approach the LivePlan authors compare against, re-plans from a trajectory with no detection rule in front of it, and it "even underperforms the Vanilla run under DeepSeek-V3 and MiniMax-M2.5" ([arXiv:2608.06701v1](https://arxiv.org/abs/2608.06701v1)).

A watcher sharing the main agent's model inherits its blind spots. In the cross-model experiment, "we see no clear sign that changing the context alone changes which errors the model finds, whereas changing the model is accompanied by lower overlap" ([arXiv:2610.01471v1](https://arxiv.org/abs/2610.01471v1)). On that study's re-analysis of earlier data, after one baseline run of uncertain provenance was excluded, removing the generation conversation before review beat same-context self-review by 1.5pp in F1, which the author reports as not significant.

A second reader brings false positives of its own kind. Classifying every cross-model false positive in that study put 187 of 1,995 (9.4%) into a category of "model bias errors, where the reviewer flags issues based on its own training data rather than actual defects". The largest subcategory, 136 of those 187, involved "flagging generator-specific features or tools as non-existent". That classification was keyword-based and was not validated.

A watcher is also hard to audit and hard to switch off. "Mods aren't sandboxed", and one that approves tool calls "can approve one that an `ask` rule would prompt for, or that one of your own `PreToolUse` hooks blocked". Built-in mods sit outside the usual kill switches: "The settings and flags that stop installed mods, such as `disableAllHooks`, `--bare`, and `--safe-mode`, don't stop built-in mods." The same page lists four built-in mods whose source is public, and the watcher is not among them, so its implementation cannot be read ([Mods overview](https://code.claude.com/docs/en/plugins/mods/overview)).

## Example

The same watcher, two triggers.

### The standing question

Every ten turns, the side agent reads the transcript and is asked whether anything looks wrong. There is no input on which its answer is "nothing", because it was asked to find something. The note rate is therefore fixed by the polling interval rather than by the run, and a clean run and a drifting one produce the same number of notes.

### The rule-fired trigger

The side agent is consulted only when a deterministic signal fires. Real thresholds of this shape already exist. This repo's loop detector pauses on a fifth repeated edit to one region of a file (`.claude/AGENTS.md`), and LivePlan's monitor fires after seven consecutive steps in one phase and then holds a five-step cooldown before the advisor may be called again ([arXiv:2608.06701v1](https://arxiv.org/abs/2608.06701v1)). The cooldown is what stops a signal that stays true from producing a stream.

Note quality is the same in both designs. Only the second has a reachable state in which the correct output is silence.

## Key Takeaways

- Price a watcher in operator attention. Its notes block nothing, so the budget it spends is the one you cannot meter.
- Write the trigger before the prompt. A watcher with no firing rule has no state in which its correct output is silence, and silence is most of what you want from it.
- Count the notes a watcher produces on runs that turned out fine. That rate, not the quality of any single note, is what decides whether the operator keeps reading the region they appear in.
- Record a watcher's agreement as coverage, never as confirmation. Two readers of one transcript raise union recall; they do not corroborate each other.
- Budget for the second agent becoming the binding constraint, whichever resource is scarce where you run it. In an interactive session that resource is the operator's attention. In this project's unattended pipeline it was the fetch cap, which began stopping runs with most of the clock unspent after an independent audit stage was added: two measured runs dispatched 5 of 12 and 9 of 13 eligible backlog items, leaving 275 and 255 of 360 minutes unspent (`routine-prompts/backlog-pipeline.md`). That is evidence about which resource binds, not a measurement of what an interruption costs a person.

## Related

- [Splitting the Drift Judge from the Advisor (LivePlan)](judge-advisor-split.md) — the agent-addressed counterpart, where rule-gated advice steers the executor instead of informing the operator
- [Wink: Classifying and Auto-Correcting Coding Agent Misbehaviors](wink-agent-misbehavior-correction.md) — a concurrent observer that holds authority to inject corrections
- [Critic Agent Pattern](critic-agent-plan-review.md) — review placed before execution rather than beside it
- [When Does a Second Model Help in LLM Review](../../verification/cross-model-review-independence.md) — which model to pick once you have decided to pay for a second reader
- [Monitor or Wait: The Supervision Choice During Agent Execution](../../workflows/monitor-or-wait-during-agent-execution.md) — the operator-side stage a watcher is meant to make affordable
