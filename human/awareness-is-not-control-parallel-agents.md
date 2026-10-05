---
title: "Awareness Is Not Control in Parallel Agent Supervision"
term: "Awareness-Control Gap"
description: "Parallel-agent supervision tooling raised throughput and cue awareness in a 16-person study that detected no gain in control, intervention success, or trust."
aliases:
  - awareness-control gap
  - abstraction tension
  - supervision without steering
tags:
  - human-factors
  - tool-agnostic
  - multi-agent
  - arxiv
last_reviewed: 2026-10-01
maturity: emerging
status: current
---

# Awareness Is Not Control in Parallel Agent Supervision

> Knowing which parallel agent needs you is not knowing how to steer it; one study raised the first and detected no gain in the second.

A supervision surface for parallel agents (plan view, run logs, status dashboard) buys attention routing. It tells you which session finished, hit an error, is waiting on a question, or is stuck — the four intervention cues one such prototype surfaced ([Long et al., 2026](https://arxiv.org/abs/2609.33113v1)). It does not thereby hand you the implementation-level picture you need to judge whether a running agent is doing the right thing. One controlled study separated the two and found the first moved sharply while the second did not move detectably.

## The conditions behind the finding

The evidence is a single design probe, so state the conditions before the numbers. Long and colleagues interviewed 14 developers about running concurrent agent sessions, derived five supervisory practices they call PILOT (Planning, Isolating, Logging, Observing, Triaging), and built ParallelPilot to externalize them. They then ran a counterbalanced within-subjects study with 16 developers against a GitHub Copilot baseline ([Long et al., 2026](https://arxiv.org/abs/2609.33113v1)).

Four conditions bound what the result means:

- Two 20-minute coding blocks on six pre-specified tickets. The authors note "the short blocks may underestimate context-recovery costs and overestimate developers' ability to retain session state."
- No condition required code review, pull requests, or merges. The authors state "we did not directly measure verification accuracy or implementation-level understanding."
- The comparison tests the whole package and "does not isolate the contributions of individual components," so shipping only the dashboard does not reproduce what was measured.
- Fifteen of the 16 participants rated themselves beginners or somewhat experienced at parallel agent work.

## What moved and what did not

The measures in the top five rows moved. The top four cleared Benjamini-Hochberg correction for multiple comparisons. The fifth, at q=.057, missed the paper's q<.05 cutoff but points the same way. The bottom three did not move detectably, on self-report at N=16.

| Post-condition measure (1–7 unless noted) | Baseline | ParallelPilot | p |
|---|---|---|---|
| Tickets per minute (logged) | 0.272 | 0.445 | .003 |
| Max concurrent agents (observed) | 2.31 | 3.25 | .002 |
| I noticed when agents finished or needed me | 3.63 | 6.19 | <.001 |
| I had a clear picture of overall progress | 3.44 | 6.06 | <.001 |
| I knew what each agent was working on (q=.057, borderline) | 4.00 | 5.06 | .044 |
| My interventions redirected the agent | 3.94 | 4.13 | .603 |
| I felt in control of the agents | 3.94 | 4.31 | .414 |
| I trusted the output | 4.50 | 4.69 | .261 |

Participants "achieved 63% higher throughput, completing 0.445 vs. 0.272 tickets per minute," and 14 of 16 preferred the tool to their current setup ([Long et al., 2026](https://arxiv.org/abs/2609.33113v1)). That figure belongs to the tool condition on this task set rather than to adopting the five practices by hand, and it carries the authors' own ceiling caveat: "participants who completed all six tasks before the block ended could not demonstrate additional throughput."

Read those last three rows as non-detections. Sixteen participants cannot rule out a small effect, and the paper claims only the weaker thing: "we did not detect corresponding improvements in perceived control and intervention success." Asked which condition made output easier to verify, 9 participants reported no difference, 4 preferred the tool, and 3 preferred the baseline.

## Why it works

Manual bookkeeping was doing two jobs, and the surface replaced one. Two participants told the authors that switching between sessions to check progress was also how they rebuilt their model of each session: "every time they context-switch between sessions to check on progress, they reinforce their memory by reconstructing and scrutinizing what each agent is working on and how far it has progressed." With an automatically updated overview and markdown files available, "some participants described reconstructing session state less often." One called it "giving up my internal representation." Another said "[with ParallelPilot,] I [ended up] not thinking as hard." The authors read the pattern as an overview that "supported awareness without necessarily preserving the detailed familiarity needed for intervention" ([Long et al., 2026](https://arxiv.org/abs/2609.33113v1)).

The two needs also call for different artifacts. A status card answers whether a session is blocked. Judging whether an unblocked session is on the right track "may require implementation-level evidence beyond summary-oriented progress reports," which a summary by construction does not carry. So the paper's design recommendation targets the exit rather than the overview: "abstraction should support not only an overview but also re-engagement: a clear path from summarized status to the code, decisions, and evidence needed for judgment."

I would treat that as the entry condition. Earn the dashboard by first building the short path from a status card back to the diff and the session transcript.

## When this backfires

- Where progress files, per-task logs, and worktrees already carry session state, there is less awareness left to gain and the same familiarity to lose. The study measured its gain against hand tracking: the baseline let participants "plan with the coding assistant, open multiple sessions, create worktrees, and maintain notes."
- On work where judging the approach dominates finishing the ticket, the gain does not transfer. The study's tasks were scoped tickets with acceptance criteria and no review step.
- Someone who never built the mental model by hand has none to externalize, and the overview becomes their only representation of the work. The study's population sits at this end: all but one rated themselves beginners or somewhat experienced.
- One surface at one level of detail covers every task on the board. The authors argue the abstraction level "should be specified per task rather than fixed per tool," because a schema change and a syntax fix "warrant different defaults."

The counter-case is strong and the paper makes it. No control measure fell, and all of them sat near the midpoint of the scale in both conditions, so the baseline was not delivering control either. The claim here is about what a supervision surface is evidence for. Build the surface.

## Example

The prototype put four cues on a card: "completion, errors, questions, and being stuck." Two triage paths follow, one for a session a cue covers and one for a session it does not.

A cue fires. In the interviews, two of those four were the ones developers lost by hand: requests for clarification and errors "were also the signals participants most reliably missed." Moving them onto a card is the gain the study measured, with cue awareness rising from 3.63 to 6.19 of 7.

No cue fires. The session is not stuck, has not errored, and has asked nothing. It is committing steadily toward the wrong design. None of the four cues covers that, and the authors grant the limit: their cues "may not capture the full range of real-world intervention needs." Catching it means reading the diff, recovering why you scoped the ticket that way, and checking it against the sessions sharing a file with it. The dashboard gave you none of that.

The second path is the one to instrument. Count the keystrokes from a status card to the diff of the session it describes.

## Key Takeaways

- Cue awareness and intervention capability are separate measures, and one controlled study moved the first without moving the second.
- Those control results are non-detections at N=16, not a proven absence; the 63% throughput figure is the tool condition on six short tickets, with a ceiling on the task set.
- Two participants described manual tracking as what rebuilt their model of each session, and the authors read the pattern the same way: with an overview available, some participants reconstructed session state less often.
- Build the path from a status card back to the diff and the transcript first. The overview is cheap once that path exists.
- Keep building supervision surfaces. Stop reading one as evidence that oversight happened.

## Related

- [Monitor or Wait: The Supervision Choice During Agent Execution](../workflows/monitor-or-wait-during-agent-execution.md) — the same split inside one agent's run, where watching buys an early stop and leaving it running gives that up
- [Developer as CPU Scheduler: Attention Management with Parallel Agents](attention-management-parallel-agents.md) — how to allocate the attention a dashboard reroutes rather than creates
- [Tiled Agent Layout: Supervising Parallel Agents Through Dedicated Panes](../workflows/tiled-agent-layout.md) — the screen-layout version of the same limit, from practitioner accounts rather than a controlled study
- [Judgment Relocation: Where Human Decisions Land in an Agent Factory](judgment-relocation.md) — the four conditions that decide whether a relocated decision is real, comprehension among them
- [Criticality and Containment: Scoping Which Agent Code You Read](criticality-containment-oversight-scope.md) — which agent-written internals you still have to open once you accept that a summary is not oversight
