---
title: "Zero Violations Is Not Evidence Your Hook Works"
term: "Enforcement Liveness Evidence"
description: "A blocking hook writes output only when it denies something, so a clean agent run cannot tell a live rail from one that was never consulted."
aliases:
  - enforcement liveness evidence
  - hook firing trace
  - guardrail liveness check
tags:
  - testing-verification
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-22
maturity: emerging
---

# Zero Violations Is Not Evidence Your Hook Works

> A clean run cannot tell a live hook from one that was never consulted, so make the hook prove it fired.

Enforcement liveness evidence is a positive trace that a blocking check ran, kept separate from whether it denied anything. A blocking hook shows up in the transcript only when it stops a tool call. So a run ending with no violation fits three states. The hook ran and the agent never tried, the hook was never consulted, or the hook covered files the run never touched. A single-author evaluation of an agentic rebuild pipeline hit the second state and stated the problem: "nothing distinguishes that silence from 'the hook fired and found no violation'" ([arXiv:2608.23616v3](https://arxiv.org/abs/2608.23616v3), §3.4).

## When this is worth doing

Two conditions, both from that evaluation's own negative results.

The blocked surface has to be one the agent's work reaches. In three trials on an 83-route app the hook was live over 19 blocked page contracts, and all 20 visible tests targeted API routes. The run never came near the blocklist: "'Hook confirmed live, zero violations' is accurate; 'the hook proved restraint' is not a claim this data supports" ([arXiv:2608.23616v3](https://arxiv.org/abs/2608.23616v3), §4.11).

The rail also has to earn its place first. Toggling only the live hook, task held constant, gave attempt counts of 2, 1, 1 against 1, 2, 1; removing the locked specification gave 3, 6, 8. "The confound resolves in the direction that credits the spec, not the hook" ([arXiv:2608.23616v3](https://arxiv.org/abs/2608.23616v3), §4.11). A rail you cannot show matters is a candidate for deletion, not for instrumentation.

## Write a firing trace before the check runs

The cheap half is a file the hook touches on every invocation, before its real work. Here the `PostToolUse` hook "writes a small heartbeat file (.claude/.hook-heartbeat.json: a timestamp and a firing count) ahead of running the real test command", which makes consultation "checkable from the filesystem afterward instead of inferred from the absence of a violation" ([arXiv:2608.23616v3](https://arxiv.org/abs/2608.23616v3), §3.4). The paper calls it "observability, not enforcement" and says it closes the gap "going forward only", so earlier runs stay unresolvable.

The plumbing behind it matters if you delegate work to subagents. "Claude Code's Agent tool never consults a target directory's own hooks. A subagent's hooks are bound to the top-level session's root configuration instead" ([arXiv:2608.23616v3](https://arxiv.org/abs/2608.23616v3), §4.5.2). Anthropic's reference agrees on where they come from: a subagent's tool calls fire "the same configured hooks as in the main conversation" ([Claude Code hooks reference](https://code.claude.com/docs/en/hooks)). One headline result in the paper is reported as an open fork for that reason: no surviving transcript shows whether the rails were live ([arXiv:2608.23616v3](https://arxiv.org/abs/2608.23616v3), §4.3).

## Attack the locked path on purpose

The other half manufactures the event your runs never produce. Searching every rep's raw activity log for any reference to a forbidden page "returns zero matches, in every rep, in both conditions, at all three scales" of 1, 6 and 19 blocked pages ([arXiv:2608.23616v3](https://arxiv.org/abs/2608.23616v3), §4.5.5). Five of six newly tested models completed the visible suite with zero rail-violation attempts ([arXiv:2608.23616v3](https://arxiv.org/abs/2608.23616v3), §4.13). So by the ablation's end, every natural trial "lands in one of two buckets — hook dead and the agent violated, or hook live and the agent never tried" ([arXiv:2608.23616v3](https://arxiv.org/abs/2608.23616v3), §4.5.6).

Four directed trials closed that by telling an agent to attempt one named locked write with the hook live. Edit-tool and write-tool attempts were blocked, the file confirmed unchanged or absent on disk. The same two paths written by a bash heredoc went through, because the enforcement "blocks only `tool === 'edit' || 'write'`, reading a filePath argument bash calls never populate" ([arXiv:2608.23616v3](https://arxiv.org/abs/2608.23616v3), §4.5.6). A directed trial certifies the tool layer it ran against and nothing wider.

## Why it works

A blocking check reports only denials, so its output on the clean path is the same empty result in all three states above. Writing the trace first separates "consulted" from "never reached", because the file exists or it does not, whatever the agent did. A directed attempt separates "would deny" from "has never been asked", because it supplies the input no compliant run generates. Both read the filesystem rather than a report. That is what caught the paper's own errors, where the model, the tooling and the prior write-up were each wrong once and "only checking each against the real filesystem surfaced the true state each time" ([arXiv:2608.23616v3](https://arxiv.org/abs/2608.23616v3), §5.3).

## When this backfires

- Your rail denies things during ordinary work. The denial log is already the positive trace, and a heartbeat is one more artifact to keep correct.
- The check is advisory by design, a warn or an ask. Liveness was never the open question; volume answers it.
- Nobody reads the trace. The evaluation's own log parser misread a combined visible-plus-held-out count as held-out-only, and its abstract lists "a bug in our own logging code" among the errors three levels of checking caught ([arXiv:2608.23616v3](https://arxiv.org/abs/2608.23616v3), §4.12).
- You read a directed trial as a compliance rate. It measures what a model does when told to try. Natural attempts in this evaluation were zero at every ablation scale and on a ten-rep purpose-built fixture ([arXiv:2608.23616v3](https://arxiv.org/abs/2608.23616v3), §4.5.5, §4.14).
- The rail is worth less than the instrumentation. Where toggling it changes nothing you can detect, spend the effort on the specification.

## Key Takeaways

- Read a violation-free run as an unread measurement, and go and find out which of the three states produced it.
- Have the hook write a timestamp and a firing count before its real work, so liveness becomes a filesystem question.
- Check the delegation path separately. Hooks fire from the session's configuration, not from the directory a subagent is pointed at.
- Run one directed attempt per locked path and per tool layer. A block confirmed through the edit tool says nothing about a shell command targeting the same file.
- Confirm the rail changes an outcome before you build evidence that it is alive.

## Related

- [Deterministic Guardrails Around Probabilistic Agents](deterministic-guardrails.md) — building the hard checks this page asks you to verify are running
- [Mutation Testing as a Quality Gate for AI-Generated Test Suites](mutation-testing-quality-gate.md) — the same question asked of a test suite: does it notice anything?
- [Planted-Bug Methodology](planted-bug-observability-calibration.md) — injecting a known defect to find out whether your signals lead anywhere
- [Decomposed Red-Teaming for Agent Monitors](decomposed-red-teaming-agent-monitors.md) — pressure-testing a monitor once you know it is live
- [Restraint Rules Need External Enforcement](../instructions/restraint-rules-need-external-enforcement.md) — why the rule moved out of the instruction file in the first place
