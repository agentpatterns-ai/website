---
title: "Loud Failures, Quiet Failures: Tool Fault Detection"
term: "Loud and Quiet Tool Failures"
description: "Agents flag an explicit tool error 91.3% of the time but a well-formed wrong value only 58.8%. Validate outputs where they enter context, not in the prompt."
tags:
  - anti-pattern
  - agent-design
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - quiet tool failures
  - silent tool corruption detection
  - agent as output validator
last_reviewed: 2026-10-09
maturity: emerging
status: current
---

# Loud Failures, Quiet Failures: Tool Fault Detection

> Agents catch loud tool failures reliably but miss about 4 in 10 quiet ones, so the agent cannot be your only tool fault check.

## Scope of the evidence

The numbers come from one preprint: single author, one benchmark (BFCL multi-turn simulated environments), six small and mid-size models, 1,920 trials. The tool corruption was one of four typed faults: a number moved by 20 to 60 percent, a dropped list element, or a replaced field. Treat the figures as a measured gap in that setup, not as a rate for frontier models or real services ([Kraishan, arXiv:2610.10062v1](https://arxiv.org/abs/2610.10062v1)).

## The anti-pattern

A team treats the agent as the validator of its own tool results. The system prompt says to check each result, and the team picks a reasoning-tier model on the assumption that more deliberation means more caution. Neither step puts a check where a value enters the agent's context.

A loud fault returns an explicit error. A quiet fault returns a value of the same type and shape as the real one, altered so that its content is wrong: "a number moved by 20 to 60 percent, a list with an element dropped, a field replaced" ([Kraishan](https://arxiv.org/abs/2610.10062v1)).

## What the study measured

When a tool returned an explicit error, agents treated it as a problem in 91.3% of trials (n=936). When a tool returned a plausible wrong value, they did so in 58.8% of trials (n=374). The gap is 32.5 points. Both rates sit above the 26.8% at which agents reported a problem when the target call had succeeded ([Kraishan](https://arxiv.org/abs/2610.10062v1)). Under a loud fault, 4% of trials passed without the agent treating the result as a problem. Under corruption that figure was 39% ([Kraishan](https://arxiv.org/abs/2610.10062v1)).

Detection followed the error channel, not the fault's severity. Timeouts, a missing tool, and a renamed parameter landed within a point of each other (91.6%, 91.2%, 91.2%), although each needs a different next step ([Kraishan](https://arxiv.org/abs/2610.10062v1)).

Two other studies point the same way. ToolMaze reports the sharpest recovery drops under implicit semantic failures, with Perturbation Recovery Rate falling around 37% ([ToolMaze, arXiv:2606.05806v1](https://arxiv.org/abs/2606.05806v1)). Sun et al. found that models tend to overtrust tools, copying the incorrect output rather than ignoring the tool ([Sun et al., arXiv:2406.19228v1](https://arxiv.org/abs/2406.19228v1)).

## Why it works

An explicit error string needs no domain knowledge to read. The paper puts it this way: "Reading it takes no domain knowledge and no comparison against expectation, which is what noticing a corrupted value requires." The design supports this reading, since three loud faults with different remedies draw the same detection rate and the one fault with no error string drops 32 points ([Kraishan, §V-A](https://arxiv.org/abs/2610.10062v1)).

## Two common fixes that did not help

Reasoning variants noticed less than their instruct siblings. Pooled over 450 pairs, detection fell 9.3 points (p<.001) and replanning rose 10.4 points, with recovery unchanged (-2.4 points, p=.512). The author reads this as a hedged guess: deliberation "supports generating an alternative course of action more than it supports checking a returned value" ([Kraishan, §V-B](https://arxiv.org/abs/2610.10062v1)).

The evidence is thin. Only three pairs were tested, and the paper itself says "three pairs cannot establish a general property of reasoning models." Qwen's drop (-16.6 points) is significant after correction. Claude's (-6.2 points) holds on matched pairs but not when modeled over all fault trials. DeepSeek's (-4.0 points) is not significant. The thinking budget was fixed at 2,048 tokens ([Kraishan](https://arxiv.org/abs/2610.10062v1)).

A one-line system prompt, "after every tool call, briefly check whether the result is what you expected", did not move detection. The change was +0.6 points for the instruct model and +2.5 points for the reasoning variant, neither significant. The arm ran on one model family, so it does not settle prompting in general ([Kraishan](https://arxiv.org/abs/2610.10062v1)).

## What to do instead

1. Validate where a value enters the agent's context. The author's advice is to monitor tool outputs rather than only tool errors, because the failures agents miss are the ones error-rate dashboards also miss ([Kraishan](https://arxiv.org/abs/2610.10062v1)). For the mechanics of an external check, see [Outcome Monitors](../agent-design/outcome-monitors-recovery-affordances.md).
2. Do not choose a reasoning tier as a safety measure for tool faults. The paper's conclusion is that the choice "would not be supported by these data."
3. Score the agent's report as well as the final state. Corruption left recovery at 60.4%, within run-to-run variation, because a wrong value the agent reads changes what it reports, not what it does to the environment ([Kraishan](https://arxiv.org/abs/2610.10062v1)). A state-diff eval does not see that harm.
4. Compare faults against repeated clean runs. Two fault-free runs of the same model and task ended in the same state in 63.3% of trials, so a single clean run as the reference would have made three faults look harmful that stayed within ordinary variation ([Kraishan](https://arxiv.org/abs/2610.10062v1)).

## When this backfires

- Sun et al. found a short disclaimer raised accuracy by up to 30% for most models, which conflicts with the null prompt result here. The 2610.10062 author attributes the gap to task shape: their models judged one output on request, while the agents here had to notice an anomaly mid-task while carrying a plan. Small models in Sun et al. also skewed toward rejecting outputs, with high false positive rates ([Sun et al.](https://arxiv.org/abs/2406.19228v1)).
- AgentProcessBench found thinking models ahead of instruct siblings at locating errors when judging a trajectory, for example Qwen3-8B in reasoning mode at 6.1% higher StepAcc. That is offline judging, not in-loop noticing, but it blocks a general claim that reasoning models notice less ([AgentProcessBench, arXiv:2603.14465v2](https://arxiv.org/abs/2603.14465v2)).
- Read-only, low-consequence tools. A missed quiet fault changed the report here, not the environment, so validators on every lookup tool cost engineering time and clean-traffic false alarms for little state gain.
- Outputs with no checkable invariant. A plausible wrong string gives an external validator nothing to test. An outcome-monitor study measured 22% recall on corruption inside strings ([arXiv:2608.19303v1](https://arxiv.org/abs/2608.19303v1)).
- Detection is not recovery. Noticing was associated with recovery, but the association weakened once model was held fixed, and the author says the study cannot show detection is sufficient ([Kraishan](https://arxiv.org/abs/2610.10062v1)).

Agents treated 58.8% of quiet faults as a problem, against a 26.8% rate of reporting a problem when nothing was wrong, so quiet faults clear that baseline by 32.0 points. For low-stakes tools whose outputs the agent can cross-check against earlier context, that may be enough.

## Key Takeaways

- Agents treat an explicit error as a problem in 91.3% of trials and a well-formed wrong value in 58.8%.
- The measured detection gap is large, but it comes from one benchmark, one author, and six small to mid-size models.
- A reasoning tier and a "check each result" prompt were not shown to close the gap. Both claims rest on thin evidence and conflict with other studies.
- Missed corruption did not lower end-state recovery here. Score what the agent tells the user.
- Use repeated clean runs as the baseline for fault effects.

## Related

- [Outcome Monitors: Recovery Affordances for Tool Failures](../agent-design/outcome-monitors-recovery-affordances.md)
- [Retry, Switch, Abstain Recovery Policy](../agent-design/retry-switch-abstain-recovery-policy.md)
- [Silent Adoption of Corrupted Tool Returns by Agents](silent-adoption-of-corrupted-tool-returns.md)
- [Blind Tool Deference: Agents Parroting Callable Tools](blind-tool-deference.md)
- [Silent-Failure Mechanism Taxonomy in Production Agent Runtimes](silent-failure-mechanism-taxonomy.md)
