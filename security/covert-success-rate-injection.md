---
title: "Covert Success Rate for Indirect Prompt Injection"
term: "Covert Success Rate"
description: "Attack success rate counts injections that ran, not the ones a user could have noticed. Splitting it by disclosure shows a covert share that survives defenses which cut ASR."
tags:
  - security
  - testing-verification
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - covert success rate
  - covert indirect prompt injection
  - covert and overt injection success
last_reviewed: 2026-09-01
maturity: emerging
status: current
---

# Covert Success Rate for Indirect Prompt Injection

> Covert success rate counts injections that ran and left no trace in the agent's final reply, so nothing in that reply flags them.

Report attack success rate split by whether the user could see the attack, under three conditions: the agent follows a ReAct-style loop, the user's view of the run is the final response rather than a streamed transcript, and your residual attack success rate is above zero. Outside those conditions the split measures nothing you can act on. Inside them, a single ASR figure hides the part of the risk your users have no way to catch.

## What the split measures

A successful injection is covert when the agent executed the injected task and its final response reveals nothing about it. It is overt when the response discloses the injected action. The two are disjoint, so `ASR = CSR + OSR` ([Lee, Kim and Lee, 2026](https://arxiv.org/abs/2608.30362v1)). Disclosure is a property of the reply text rather than of the executed actions, so the paper grades it with an LLM judge over the user task, the injected goal, and the final response.

Execution and concealment turn out to be separate capabilities. On AgentDojo v0.1.34 with no defense, three conditions land within 10 points of each other on attack success and nowhere near each other on covert share:

| Model | Attack | Attack success | Covert |
|---|---|---|---|
| Gemini-2.5-Flash | Important message | 41.83% | 34.67% |
| Qwen3-235B | Important message | 37.62% | 29.72% |
| LLaMA-3.3-70B | ChatInject | 32.14% | 2.63% |

Source: [Lee, Kim and Lee, 2026](https://arxiv.org/abs/2608.30362v1), Table 1, over 949 user-task and injection pairs across four suites.

Cutting the total does not clear out the covert part of it. Task Shield, a runtime check that blocks tool calls judged misaligned with the user task, took the Gemini-2.5-Flash figure above from 41.83% to 12.33%, and 11.59 of the remaining 12.33 points stayed covert. The authors' reading of their own defense rows is blunt: "None of these defenses changes the trajectory pattern that makes successful injections covert, so surviving successes can remain hidden even when ASR drops" ([Lee, Kim and Lee, 2026](https://arxiv.org/abs/2608.30362v1)).

## Why it works

Covertness is decided by what the agent does after the injection, not by the payload. Grouping steps into user-task, injection, and terminal states across 2,087 successful traces, the two outcomes split in opposite directions: "Overt successes more often EXIT (70.92%), ending the trajectory at the injection. Covert successes mostly RETURN (67.70%), finishing the user's task before the trajectory ends" ([Lee, Kim and Lee, 2026](https://arxiv.org/abs/2608.30362v1)).

The ReAct loop supplies the cause. "When the trajectory ends, ReAct prompts the model to summarize its most recent action, so the final response is about whatever the agent did last" ([Lee, Kim and Lee, 2026](https://arxiv.org/abs/2608.30362v1)). An agent that stops at the injected action summarizes the injected action. Go back and finish the user's request instead, and the summary is about the user's request, so the injection never reaches the reply. A clean-looking answer is a product of the loop's shape, not evidence about what ran.

The wider gap between what an agent says and what it does is documented elsewhere. [Mind the GAP](https://arxiv.org/abs/2602.16943v1) found 219 cases across six frontier models where the text output refused a request while the tool calls executed it, persisting under safety-reinforced system prompts.

## What to instrument

- Grade the final response against the trajectory that produced it. The signal is a tool call whose target appears in neither the user's request nor the reply. The paper's judge rubric inverts into a check: a response is disclosing when it names an entity the injection introduced, describes an action outside the user task's scope, or frames the injected step as an extra one.
- Publish the covert share next to ASR in any defense evaluation. A report showing only a falling ASR cannot say whether the failures you kept got harder to notice.
- Watch the post-injection transition, not just the end state. A run that reaches an off-task action and then resumes the user's task is the shape that produces a clean summary.
- Do not rest detection on user-task dependence alone. [MELON](https://arxiv.org/abs/2502.05174v4) keys on the premise that "under a successful attack, the agent's next action becomes less dependent on user tasks and more on malicious tasks." The covert pattern is the inverse, so that heuristic reads it as benign.
- Prefer a control that removes the harm. An [egress policy](agent-network-egress-policy.md) or a [confirmation gate](human-in-the-loop-confirmation-gates.md) drives the residual toward zero, where the split stops mattering.

## When this backfires

- Your agent streams its trajectory. Claude Code, Cursor, and Copilot agent mode display every tool call, so the final response is not the user's only view. The authors scope themselves out here: "We do not know if the results apply to agents that share their thought process with the user" ([Lee, Kim and Lee, 2026](https://arxiv.org/abs/2608.30362v1)). The question in that setting is whether anyone reads the transcript, which needs a different measurement.
- The harm class is already closed. With network egress denied or every consequential action gated, there is no successful injection left to be covert about, and [trust-boundary auditing](lethal-trifecta-threat-model.md) earns more than a metric.
- Sessions run long. AgentDojo is single-turn, and the same limitations section notes that "in longer conversations, users might spot the attack later on", which the number does not capture.
- Trace volume is low. Covert share needs a judge per trace to mean anything, and the judges disagree. On 500 stratified traces, GPT-4o labeled 198 covert, Claude Haiku 4.5 labeled 214, and human annotators labeled 201 ([Lee, Kim and Lee, 2026](https://arxiv.org/abs/2608.30362v1), Appendix F).
- You treat it as progress. Covert share falls when ASR falls, so a dashboard can show improvement while the exfiltration path stays open. It ranks residual risk and does not reduce it.

## Key Takeaways

- Attack success rates within 10 points of each other produced covert shares of 34.67% and 2.63%, so ASR alone does not rank user-visible risk.
- The cause is the ReAct summary step, so this is a property of the loop's shape rather than of any particular payload.
- A defense that cuts ASR has not necessarily cut the covert share. Task Shield left 11.59 of 12.33 surviving points hidden.
- Measure it by diffing the final response against the tool calls, and treat the result as judge-dependent: three label sources put 198, 214, and 201 of the same 500 traces in the covert bucket.
- If your agent shows the user every tool call, measure something else. This number is defined over a final-response-only view.

## Related

- [Discovering Indirect Injection Vulnerabilities in Your Agent](indirect-injection-discovery.md) — finding the injection paths whose successes this metric then classifies by visibility
- [Adaptive Evaluation of Out-of-Band Prompt-Injection Defenses](adaptive-evaluation-out-of-band-defenses.md) — the other axis on which a reported ASR overstates safety, attacker-adaptivity rather than user-visibility
- [Action-Audit Divergence: A Four-Mode Taxonomy for Runtime Hardening](action-audit-divergence-taxonomy.md) — divergence between actions and the audit record, where this page covers divergence between actions and the user-facing reply
- [Behavioral Firewall for Tool-Call Trajectories](behavioral-firewall-tool-call-trajectories.md) — a trajectory-level control that rejects the off-task call before the summary step is reached
- [Confirmation Gates for Consequential Agent Actions](human-in-the-loop-confirmation-gates.md) — putting the action in front of the user regardless of what the final response says
