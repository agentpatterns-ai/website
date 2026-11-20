---
title: "Truthful Error Notes for Compacted AI Agent Histories"
term: "Truthful Error Note"
description: "A truthful note beside a preserved error raised agent recovery 15.2 points; recording the fix as done while the world held the error cut it 6.4 points."
tags:
  - context-engineering
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - truthful correction note
  - record-world mismatch
last_reviewed: 2026-11-19
maturity: emerging
---

# Truthful Error Notes for Compacted AI Agent Histories

> In one two-model study, recording an error as fixed while the world still held it lowered recovery; a truthful note raised it.

When compaction, repair, or handoff rewrites an agent's history, write a record that matches the world. On AgentCE-Bench, a truthful note beside a preserved error raised recovery from 50.57% to 65.78% (+15.20 pp, against a matched neutral note). The same correct value recorded as the agent's own completed action lowered recovery from 50.13% to 43.70% (-6.43 pp, against the unedited record). Both come from 319 frozen states, two receiver models, and 2,552 continuations, with the wrong value still committed in every arm ([Pakhomov et al., 2026](https://arxiv.org/abs/2611.14654v1), §4.2, §5.1). The note was built from oracle ground truth, and the authors say "We tested one flipped receipt and one appended note, not a compaction or handoff policy" (§6).

This page adds a condition to [Error Preservation in Context](error-preservation-in-context.md): a visible error does not help if the history also says it is resolved.

## What the four arms changed

Recovery is the share of the first three outstanding slots holding the correct value at the end (§4.1).

| Arm | What the history holds | Recovery |
|-----|------------------------|----------|
| Unedited | The original call and receipt | 50.13% |
| Neutral note | The original plus a content-free note matched in role, placement, and length | 50.57% |
| Truthful note | The original plus a user-role note naming the wrong call, the correct value, and the standing wrong state | 65.78% |
| Falsified action | The agent's own call and receipt rewritten to assert the correct value was set | 43.70% |

Crossing the comparators shifts each effect by under half a point (+15.65 pp and -6.87 pp, §5.1).

## The world sets the sign

AppWorld holds the record fixed and varies the world: 65 task families, 1,040 continuations, a 30-step budget, the same two receivers (§4.3). A success receipt lowered whole-task success from 45.38% to 28.46% when the write was absent from the database. It raised success from 38.46% to 48.85% when the write was present (§5.4). A "done" record helps when the world agrees. The +27.31 pp interaction has wide intervals and is read for sign only.

The mismatch also arises unprompted: of 1,074 AgentCE-Bench source episodes that called done, 393 left a wrong value that the agent's own receipt had confirmed as set (§3).

## What the paper does not explain

The paper gives no mechanism. It rules out copying, because a record that shows the correct value should come out ahead and finished 6.43 pp behind (§5.2). Two readings stay open: the record as a map of remaining work, and a role effect favoring a user-role note (§1). Under the map reading, a "done" mark drops that work from the plan.

## When this backfires

- The gain is local. Of the +15.20 pp, +11.57 pp fell at the slot the note names (Table 1). On 47 states whose error lay outside the scored slots, the pooled effect was unresolved: claude-sonnet-5 -10.64 pp, gpt-5.5 +7.80 pp (Appendix H.2).
- The note needs a verified correct value, and a bare error flag with no replacement was unresolved (§5.6). A deployed summarizer may lack it.
- Wording moves the result: a note with only the correct value gained +11.70 pp, the full note +16.46 pp (§5.6).
- Truth and channel are confounded: the note is a user-role message, the falsified edit the agent's own call (§6).
- Self-conditioning evidence points the other way: models err more when their context holds earlier errors ([Sinha et al., 2025](https://arxiv.org/abs/2509.09677v3)). Pakhomov et al. answer that this was shown on "injected histories with no environment, so record and world stay entangled" (§2).
- Models below about 1.7B parameters copy a preserved call string back ([Verbatim Failure Records](../patterns/anti-patterns/verbatim-failure-records.md)).

## What to do

1. Before the compactor or handoff writer records a step as completed, re-read what the step changed: file contents, a diff, a test result, a database row.
2. Write "done" only if that check passes. Otherwise keep the original failed call and receipt, and append a user-role note. The note names the wrong action, gives the verified correct value if you hold one, and states that the wrong state is still in effect, as in the Example.
3. Score the summarizer offline: restore frozen mid-task states, let a receiver continue under each summary style, and compare outcomes (§7).

## Example

The paper's truthful note for one AgentCE-Bench state, from Appendix J.2:

```
Retrospective correction (oracle-verified; this note was authored by the pipeline from detector ground truth, not generated by the agent as self-reflection). At message index 264 the assistant issued set_slot(row=2, col=4, id=C1795); the tool response at message index 265 accepted it. That assignment is incorrect: the verified correct id for (row 2, col 4) is C4801. At this checkpoint the current solution records id C1795 at (row 2, col 4), so its consequence remains in effect until the assignment is corrected.
```

The fields are the call, the wrong value, the verified value, and the standing consequence. A coding harness would fill them from its own tool names and checks.

## Key Takeaways

- Match the record to the world before the compactor writes it. The harm in this study came from a record that claimed a fix the world did not hold.
- A "done" record helps when the world agrees, so the check on the world decides which summary to write.
- The evidence covers two receivers and one appended note. Test your own compaction policy on restored states before relying on it.

## Related

- [Error Preservation in Context](error-preservation-in-context.md)
- [Context-Injected Error Recovery](context-injected-error-recovery.md)
- [The Handoff Tax: What a Receiving Model Should Inherit](handoff-tax-model-switch-context.md)
- [Per-Type Retention Policy for Agent Compaction](per-type-retention-under-compaction.md)
- [Probing an Agent's Completion Claim in a Disposable Fork](../verification/completion-claim-probe.md)
- [Recovery as a Separate Eval Axis](../verification/recovery-as-separate-eval-axis.md)
- [Verbatim Failure Records in Small-Model Agent Transcripts](../patterns/anti-patterns/verbatim-failure-records.md)
- [Experience Rot After Silent Tool Changes in AI Agents](../patterns/anti-patterns/experience-rot-silent-tool-changes.md)
