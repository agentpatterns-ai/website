---
title: "Belief Checks for Agent Harness Changes"
term: "Harness Belief Check"
description: "Change one harness component and the agent's reading of the task state can move while terminal success shows nothing, so compare the two readings on a matched pair."
tags:
  - testing-verification
  - evals
  - tool-agnostic
  - arxiv
aliases:
  - harness belief check
  - harness-induced belief divergence
  - belief diff across harnesses
last_reviewed: 2026-10-13
maturity: emerging
---

# Belief Checks for Agent Harness Changes

> Changing one harness component can move what the agent believes about the task state while terminal success shows nothing, so diff the beliefs.

A harness belief check compares what the agent takes the task state to be under two harnesses. The harnesses differ in exactly one component, and the task, the model and the seed stay fixed. The output is a difference between two configurations. One run on its own produces no score. You elicit a structured reading of task state, failure mode, known constraints and recommended next action from each side, then compare those fields one at a time.

Terminal success can be blind to the change. One study fixed the task, environment, base LLM, elicitation procedure, initial interaction record and random seed, and varied only the harness. It reports "substantial cross-harness belief divergence that is often invisible from terminal success alone and can propagate into different downstream actions" ([Yi and Song, arXiv:2607.04528v2](https://arxiv.org/abs/2607.04528v2)).

## When this check is executable

The result rests on a matched comparison, and so does the check. Three conditions decide whether you can run it.

- You can hold everything else still. The study fixes task, environment, base LLM, elicitation procedure, initial record and seed. If a release changes the gate and the log format together, a diff attributes the difference to neither.
- You change one component. The paper's harness is the tuple of observation, action, gating, repair and logging components, and an individual component is isolated only when the two harnesses differ in that component alone.
- The work has steps for a difference to develop over. The diagnostic tracks disagreement that carries forward, and a single-turn completion offers none.

Outside those conditions, [outcome grading](grade-agent-outcomes.md) is the instrument you have. It settles which of two solutions to one task is better. It cannot tell you what two harnesses did to the agent's reading of that task.

## Read the components, not the aggregate

The aggregate number is dominated by a floor. The paper splits its five field distances, each bounded to the 0-to-1 range, into an arrival half (constraints and recommended action) and a growth half (task state, failure mode and numeric forecasts). Arrival disagreement was already near its ceiling after a single rollout step, running from 0.994 to 0.999 at K=1 across all five mediated harnesses. In the long-horizon run the recommended-action distance alone sat at 1.000 at every horizon from K=1 to K=20 ([Yi and Song, arXiv:2607.04528v2](https://arxiv.org/abs/2607.04528v2)).

The growth half is what separated the harnesses. Against the raw reference, growth divergence under structured execution rose from 0.156 to 0.257 by K=5, while repair-heavy fell from 0.195 at K=1 to 0.134 at K=8. The authors put the reading plainly: "scalar stability does not imply component convergence".

The aggregate is also sensitive to how you weight it. Under three weight vectors, including a uniform one, the absolute scale and the middle of the ranking both moved; only the largest-divergence harness kept its place. A dashboard tile fed by this number will move for reasons that have nothing to do with the agent.

## After a gate fires, the intent survives

In the paper's risk-gated Terminal-Bench rollouts, 42 of 60 blocked high-risk steps were followed by a same-class risky proposal within three steps, a rate of 0.700. The authors read that as "showing that blocking execution does not necessarily eliminate the corresponding action tendency" ([Yi and Song, arXiv:2607.04528v2](https://arxiv.org/abs/2607.04528v2)).

Read the measurement for what it is: recommended actions in an elicited rollout, mapped to six coarse categories by one classifier applied across harnesses. No live environment executed them. The test it suggests is cheap either way. After a deny hook fires, grade the agent's next three proposed actions instead of stopping at the fact that the command did not run. The same study found action disagreement of 0.280 in the lowest growth-divergence quartile and 0.595 in the highest, over 840 matched step-level pairs. A belief gap and a behavior gap travel together.

## Why it works

The agent infers what happened from execution feedback and picks its next step from that inference. The harness produces the feedback. It decides which observations reach the model, which actions are gated, and whether a repair or a verification is shown. It also transforms the output. Change the mediation and the evidence changes, so the inference can change with it. The paper states the step directly: "The harness mediates this feedback, so changing the harness can change the agent's interpretation even when the task and base LLM remain fixed". It keeps the same hedge on what follows: "Because this belief informs subsequent reasoning, the difference can propagate into later decisions" ([Yi and Song, arXiv:2607.04528v2](https://arxiv.org/abs/2607.04528v2)). Gating is the clearest case. A raw harness "may expose the failure directly, whereas a risk-gated harness may prevent the command from executing and instead report that it was blocked". Those are different facts about the same intended action.

## When this backfires

- Tracked as a target rather than read as a diff. Exposing blocked, repaired, verified and shadow evidence raised measured growth divergence by 0.226 for repair-heavy and 0.216 for verification-selective at K=5. The alignment step then reduced it by at most 0.036: "Alignment may reduce view dependence, whereas evidence exposure may increase measured divergence" ([Yi and Song, arXiv:2607.04528v2](https://arxiv.org/abs/2607.04528v2)). A team paid to lower the number is paid to log less.
- Read as accuracy or calibration. The paper's self-consistency measure compares an early forecast against the same model's later imagined state. The authors rule the stronger reading out: "The result therefore provides evidence of changed internal consistency, not improved predictive accuracy or calibration." Under cost-aware execution the full intervention moved that AUROC from 0.174 to 0.428, a gain that leaves it below the 0.5 chance line.
- Trusting the report as a window on the computation. The elicited belief is text the model produces about itself, and stated reasoning can diverge from what drove the output: "CoT explanations can systematically misrepresent the true reason for a model's prediction" ([Turpin et al., arXiv:2305.04388v2](https://arxiv.org/abs/2305.04388v2)).
- Generalizing past the evidence. The paper did test transfer to SWE-bench Verified and Terminal-Bench and found that "harness-induced belief divergence persists across public benchmarks, but its dominant harness and belief component depend on the execution regime". The controlled benchmark is "a controlled coding benchmark with eight tasks spanning off-by-one errors, missing null checks, import cycles, and destructive-action traps", and "The evaluation crosses six harnesses, four rollout horizons, and three random seeds". The paper never names the base LLM, so none of it supports a claim about a specific model.
- Mistaking the rollout for a run. Algorithm 1 ends each step by extending the imagined record "without executing a new live benchmark action", so the trajectory is a forecast elicited from the model rather than observed behavior. What it diagnoses is the reading the harness produced.

## Key Takeaways

- A harness belief check is a diff between two configurations that differ in one component. Without a matched pair it measures nothing.
- Compare the individual fields. Constraint and next-action disagreement saturate immediately; the fields that move over the horizon are where the harness change shows up.
- After a gate denies an action, grade the next few proposals. In the paper's rollouts 42 of 60 blocks were followed by a same-class risky proposal within three steps.
- Never put this number on a target. Better instrumentation raises it, and the paper's own validity evidence stops short of accuracy or calibration.
- Treat the evidence base as a reason to run the check on your own harness rather than to import the figures. It is eight controlled HIBench-Code-v0 tasks plus SWE-bench Verified and Terminal-Bench subsets grouped by execution regime, with no named base LLM and elicited forecasts rather than live runs.

## Related

- [Grade Agent Outcomes, Not Execution Paths](grade-agent-outcomes.md) — the instrument this one complements, and the one that goes blind when the harness is the variable
- [Trajectory Decomposition](trajectory-decomposition-diagnosis.md) — stage-level diagnosis of an executed run, where this check reads an elicited forecast
- [Action-Class Decomposition for Tool-Calling Evals](action-class-decomposition-tool-calling-evals.md) — scoring which class of action was chosen, the measure the blocked-then-reproposed finding needs
- [Seed-Variance Reporting](seed-variance-reporting.md) — what to do when the quantity you are diffing moves with the seed
- [Model Rankings Reverse Across Agent Harnesses](../patterns/agent-design/model-rankings-reverse-across-harnesses.md) — the outcome-level version of the same dependence
