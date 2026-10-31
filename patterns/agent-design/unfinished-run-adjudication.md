---
title: "The Outer Harness That Adjudicates an Unfinished Run"
term: "Unfinished-Run Adjudication"
description: "When an agent stops before finishing, a second loop reads its trajectory and returns retry, terminate, or escalate. It needs a stop trigger first, then the task specification and a staffed third verdict."
tags:
  - agent-design
  - tool-agnostic
  - arxiv
  - reliability
aliases:
  - unfinished-run adjudication
  - outer harness adjudication
  - retry, terminate, or escalate
  - trajectory adjudication after a stop
last_reviewed: 2026-10-15
maturity: emerging
status: current
---

# The Outer Harness That Adjudicates an Unfinished Run

> An outer harness reads a stopped agent's trajectory and returns one verdict of three: retry, terminate the job, or escalate to a human.

One precondition and three conditions decide whether an outer adjudicator earns its cost. The precondition is that the run must stop. Only 18% of failed trajectories in Zhao et al. terminate shortly after they become unrecoverable ([arXiv:2607.09510v1](https://arxiv.org/abs/2607.09510v1)), so cap steps or wall-clock time first.

The three conditions:

- The fleet produces more trajectories than anyone can read by hand.
- You can give the reader the task specification, not only the transcript.
- A person has capacity to take whatever the third verdict sends them. This is an inference from the design; no cited source tests it.

## The three verdicts

Third Moment Research puts a second model outside the agent and lets it decide the stopped run's fate. In OpenAI's case study, Third Moment runs Codex as a subagent inside an outer harness powered by GPT-6 Sol or GPT-6.1 Sol. When a task is left unfinished, the outer harness examines the trajectory and chooses to retry, terminate the job, or escalate to human review ([OpenAI, 2026](https://openai.com/index/third-moment-research)). The setup is quantitative research, with the Codex harness running inside a Dockerized environment. Company-wide, Third Moment reports 10,000 agents running at once on investigations of 36 to 48 hours ([OpenAI, 2026](https://openai.com/index/third-moment-research)).

Each verdict answers a different question about the stop. A loop that can only retry never asks the other two.

| Verdict | What the reader found | What it buys |
|---|---|---|
| Retry | The stop was recoverable, the goal still reachable | A run otherwise discarded |
| Terminate | The goal is unreachable from this state | The budget the run would keep spending |
| Escalate | The trajectory settles neither question | One wrong automatic decision avoided |

This page infers that retry and terminate are cheap and that each errs in the opposite direction: retry wastes budget on a lost run, and terminate discards a recoverable one. Escalate is the only verdict with a dependency outside the system.

## Why it works

This section argues by analogy. The paper below did not test a stopped-run adjudicator. Zhao and colleagues tested a prefix monitor, an independent Claude Sonnet 4.6 model that sees only part of a trajectory, on 2,659 prefixes from 600 trajectories (300 failed, 300 successful). It "reliably recognizes failure once it has occurred, flagging locked-in runs at 82% precision, but it lacks foresight". Its median lead time against the lock-in step is zero, and "only 3.7–8.7% of failures are flagged before lock-in, and overall real-time recall remains low (28.8% at best)" ([Zhao et al., arXiv:2607.09510v1](https://arxiv.org/abs/2607.09510v1)). The monitor recognized some failures after lock-in but rarely anticipated them. This page uses recognition after failure as motivation for a stopped-run reader. The paper does not estimate that reader's accuracy or compare retry, terminate, and escalate decisions. The same inference separates this pattern from [catching the failure inside the recovery window](failure-trajectory-recovery-window.md).

The reader has to be a separate process for a second reason, and it is the same reason a [drift judge sits outside the agent it watches](judge-advisor-split.md). An agent's claim of success is not trustworthy evidence that it succeeded. Fabricated success, where the agent "claims results or completion with fake evidence", appears in 26% of failed trajectories. 84% of it begins at or after the step where the run became unrecoverable. The authors conclude that "a claimed success cannot be trusted on its face, especially late in a trajectory" ([arXiv:2607.09510v1](https://arxiv.org/abs/2607.09510v1)). By this page's inference, re-prompting the inner agent puts the same question to the same context.

Give the adjudicator the goal as well as the transcript. Supplying that monitor with the task's requirements lifted overall recall from 18.2% to 28.8%, and recall on ignored-requirement failures from 3% to 22% ([arXiv:2607.09510v1](https://arxiv.org/abs/2607.09510v1)). A reader never given the requirement cannot see a failure that consists of violating it.

## When this backfires

- Judges accept runs that failed. Across 1,302 expert-reviewed web-agent trajectories and 12 LLM judges, "no judge achieves above 70% precision" ([Lù et al., arXiv:2504.08942v2](https://arxiv.org/abs/2504.08942v2)). At least 30% of runs labeled successful were failures. The paper's worked error is this pattern's own case: "the user requests the agent to buy cereal in VisualWebArena, but the agent stops after adding it to the cart. The judge erroneously identified the trajectory as successful, even though the agent missed an important detail in the instruction."
- The trajectory carries the failing agent's narrative. In the same study a judge "accepts the agent's thought process without realizing it opened the wrong page" ([arXiv:2504.08942v2](https://arxiv.org/abs/2504.08942v2)). Feed the reader observations and tool output, not only the inner agent's reasoning.
- Diagnosis errors occur in monitors. In Cadence's SWE-bench Lite failure breakdown, root-cause misdiagnosis is the most common monitor failure (76 of 284, 26.8%). That monitor guides code fixes, not retry-or-terminate decisions ([arXiv:2610.12269v1](https://arxiv.org/abs/2610.12269v1)).
- Most failed runs continue after lock-in. Only 18% of failed trajectories terminate shortly after becoming unrecoverable, and the other 82% continue executing ([arXiv:2607.09510v1](https://arxiv.org/abs/2607.09510v1)). A stop-triggered adjudicator cannot intervene during that continued execution. A step or wall-clock cap bounds the wait for adjudication.
- Small fleets can use direct human review. Third Moment reports 10,000 concurrent agents, but its account establishes no minimum fleet size for an adjudicator ([OpenAI, 2026](https://openai.com/index/third-moment-research)). Compare the added model cost with your own review workload.
- The deployment is unmeasured. The primary source gives no accuracy figure for the outer harness, no retry success rate, and no escalation volume. The only quantified gain it reports is a Codex optimization that cut a backtest from about 3 hours to 3 to 5 minutes, not anything the adjudicator did ([OpenAI, 2026](https://openai.com/index/third-moment-research)).

## Example

AgentRewardBench records a VisualWebArena run where the user requested a cereal purchase, but the agent stopped after adding cereal to the cart. The judge called that run successful ([Figure 3, arXiv:2504.08942v2](https://arxiv.org/abs/2504.08942v2)).

The task requirement and observed cart state expose the unfinished work. They do not establish whether checkout remains possible. This page uses the case to show what an adjudicator must inspect before choosing retry, terminate, or escalate. The study measured the success-judgment error; it did not test those three verdicts.

## Key Takeaways

- Treat an unfinished run as a disposition decision with three outcomes, not a retry loop. A supervisor that can only retry cannot end a job.
- Run the read after the stop, not during the run. A prefix monitor in one study flagged locked-in runs at 82% precision but caught under 9% of failures before lock-in. Applying that to a stopped-run adjudicator is this page's inference.
- Pass the task requirements into the adjudicator. Without them, recall on ignored-requirement failures measured 3%.
- Staff the escalate route before you ship it. By this page's inference, an unstaffed third verdict leaves the run unresolved.
- Calibrate your adjudicator against labeled failed runs before trusting its terminate verdict, because the best of 12 judges tested on AgentRewardBench stayed at or under 70% precision.

## Related

- [Agent Failure Trajectories and the Recovery Window](failure-trajectory-recovery-window.md) — the same dataset read for mid-run intervention, where the paper's monitor had zero median lead time before lock-in.
- [Retry, Switch, or Abstain: Supplying a Tool-Recovery Policy at Runtime](retry-switch-abstain-recovery-policy.md) — the in-agent version of the choice, triggered by a tool failure rather than by an unfinished task.
- [Verdict-Driven Inspection Cadence for Agent Monitors (Cadence)](verdict-driven-inspection-cadence.md) — how often a monitor should look while the run is still going.
- [Monitor or Wait: The Supervision Choice During Agent Execution](../../workflows/monitor-or-wait-during-agent-execution.md) — what a human gives up by leaving a run unwatched, which is what the adjudicator has to replace.
- [Premature Completion: Agents That Declare Success Too Early](../anti-patterns/premature-completion.md) — the failure mode that makes the inner agent's own completion claim unusable as the trigger.
