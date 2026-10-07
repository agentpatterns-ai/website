---
title: "Harness-Enforced Stopping on Judged-Useless Tool Results"
term: "Enforced Integration Step"
description: "Agents call a failing source's results useless 97-100% of the time and keep querying it. Count the run in harness code and remove every action but finish."
tags:
  - agent-design
  - tool-agnostic
  - reliability
  - arxiv
aliases:
  - enforced integration step
  - run-length stop rule
  - judged-useless stop gate
  - stopping on consecutive useless results
last_reviewed: 2026-10-06
maturity: emerging
status: current
---

# Harness-Enforced Stopping on Judged-Useless Tool Results

> An agent that judges its results useless and keeps querying will not stop on that judgment until the harness counts the run and acts.

Count the consecutive results the agent judges useless, and when the count hits your threshold, remove every action except finish. Across seven agents in a retrieval environment with injected source failures, letting the harness take that step was the only tested condition under which stopping tracked the evidence for every model ([Zhang et al., arxiv:2610.06191v1](https://arxiv.org/abs/2610.06191v1)). Writing the same rule into the prompt does not substitute. Stated in words, "only Llama-3.1-8B and Qwen3-32B follow it, and only partly".

Two routes get the judgment to the harness. The paper's instrument asks the agent a one-word question, USEFUL or USELESS, "on a scratch copy of the conversation that the agent never sees again", so the trajectory is untouched. The cheaper route reads the judgment out of the reasoning the agent already writes, with a keyword reader ([2610.06191v1](https://arxiv.org/abs/2610.06191v1)). Either way the counter lives in your code, not in the model's head.

## When this is worth building

Three conditions decide it:

- The tool fails silently. It answers with a 200 and well-formed text that does not help, so an error-counting breaker never trips. When your failures are timeouts and 5xx instead, [Agent Circuit Breaker](agent-circuit-breaker.md) already covers the case and needs no judgment signal at all.
- Answering from what the agent already holds beats spending the rest of the budget. The gain tracks that: on FEVER fact verification, where a coin flip scores half, the rule raised mean success by +0.129 to +0.201, against +0.026 to +0.097 on multi-hop question answering ([2610.06191v1](https://arxiv.org/abs/2610.06191v1)).
- You can fit the threshold. The paper's five was set on 100 development questions against sources that recover after at most three failures. Copy the mechanism, not the number.

## The agent hands you the signal and ignores it

The study records judgment, belief and action separately at each step. The judgment is reliable: "Every model whose judgments we recorded calls a failing source's results useless 97-100% of the time." The action does not follow it. "After their own judgments have called five results in a row useless, five of the seven answer on at most 7% of questions." Unaided Qwen3-8B answered on 1 of 292.

Caution is not paying off. For the 7-8B models "answering at that point succeeds 15-17% of the time and continuing at most 7%", an exploratory result. Forced to answer at that same point, Claude Haiku 4.5 "is right on 114 of the 284 questions where this happens, whereas on its own it answers only one of them" ([2610.06191v1](https://arxiv.org/abs/2610.06191v1)).

## What telling the agent more does

Delta below is the paper's time-matched contrast: the chance of answering at a fixed step after an unbroken run of useless-judged results, minus the chance at that step when the latest result was judged useless but an earlier one useful. Zero means the clock or the deadline drives the stop; positive means the evidence does.

| Told the agent | What changed | Delta |
|---|---|---|
| It may answer from memory | Qwen3-8B stops earlier, answering before any real result on 55% of questions whose source recovers after three failures | -0.32 |
| The budget, with a counter | On a failing source, 51-79% of answers land on the last action; double the budget and they move from the eighth action to the sixteenth for no gain | stays negative |
| The stopping rule in words | Two of four open models follow it, partly | +0.09, +0.08 against +0.37, +0.33 enforced |
| A price of 0.05 per call | The 7-8B models still answer at the deadline, no better than the budget alone | negative |
| The running count of useless judgments | Agents do not stop on the count | -0.14 to -0.24 (three 7-8B models) |

Figures from test300 in [2610.06191v1](https://arxiv.org/abs/2610.06191v1); the running-count row is exploratory. The enforced rule, by contrast, answers at the same action under either budget.

## Why it works

The paper rules out the three cheaper explanations one at a time, which is what makes the mechanism specific. Perception is intact at 97-100% accuracy. Belief is not the cause: beliefs "point in different directions across models, and actions do not follow them", with Llama-3.1-8B answering at only 32 of 595 decision points where its own reports favored answering now. Nor is missing information, since permission, the budget, the rule in words, a per-call price and the running count each move when the agent stops without changing what it stops on.

What is left is the step that turns an accumulated run into an act. Hand that step to the harness and mean success rises by +0.026 to +0.097 for the four open models and Claude Haiku 4.5, and the stopping point stays put when the budget doubles. In a hazard model, each further useless judgment moves an unaided 7-8B agent's chance of answering by -0.02 to -0.01, and by +0.15 to +0.17 under the enforced rule. The authors read it as a run-length test in "the spirit of sequential testing". One control separates this from the idea that forcing a stop helps anyway: against a random signal that says useless equally often but at random steps, "the enforced rule wins by 0.011 to 0.029 (Holm-significant), so the timing of the signal matters" ([2610.06191v1](https://arxiv.org/abs/2610.06191v1)).

## When this backfires

- Your sources recover late, or fail on topic. The threshold is fitted to a recovery distribution you cannot see in production, and when recovery comes later, "the rule can give up just before it". Judgment accuracy also falls to 84-97% on distractor paragraphs and 76-97% on pages stripped of their supporting facts, so the gate's input degrades where real tools fail.
- You are buying accuracy. Mostly you are not. A stated budget matches or exceeds the enforced rule on the three 7-8B models: "the budget condition matches or exceeds the enforced rule's success on several models, so success alone cannot show what stopping responds to". The gate buys a stopping point that holds when the budget changes, plus the calls you stop spending. With a fixed budget and cheap calls, that is not worth a threshold to maintain.
- The judgment calls get billed. The rule "makes three to five judgment calls per question, which would put it below the budget condition if they were charged like tool calls". Reading the judgment out of the agent's own reasoning costs nothing and holds success within 0.01 on Llama-3.1-8B and the Qwen3 models, but it "does not help Qwen2.5-7B, which rarely states a judgment".
- Your agent already stops too early. Qwen2.5-7B's failure is the opposite one: the gate alone moved it from .192 to .237, while the budget and the gate together reached .375. Diagnose the direction first.
- Answering early is not free. Parametric knowledge "can be stale or wrong", so the authors argue for making the abandon decision explicit and measurable, not for trusting memory ([2610.06191v1](https://arxiv.org/abs/2610.06191v1)).
- The agent's judgment may not be the signal worth paying for. A detector that just counts shared content words "does about as well as the agent", on the paper's own exploratory comparison, and both [HALT](https://arxiv.org/abs/2608.02009v3) and [evidence-carrying termination](https://arxiv.org/abs/2608.23623v1) report results from signals the agent never supplies.

## Example

The transferable part is the measurement, because a success score cannot tell these policies apart. An agent that stops at a fixed step, one that waits for the deadline and one that stops on accumulated evidence can all score alike, and they diverge only when conditions change. So test the stop, not the score: hold the step fixed and check whether the chance of answering rises with the run of results the agent judged useless. The authors state it as a rule for evaluators: "Evaluations should not infer evidence-driven stopping from success, which a deadline also yields" ([2610.06191v1](https://arxiv.org/abs/2610.06191v1)).

The cheap version in your own harness is a budget-doubling probe. Run the agent against a source you have broken on purpose, once at the normal call budget and once at twice it. If the median answering step moves with the budget, your agent is stopping on the deadline, and whatever judgment it logged along the way changed nothing.

## Key Takeaways

- Count the run in harness code, not in the prompt. Every prompt-level cue tested moved the stopping point without changing what it responds to.
- Log the agent's per-result judgment before you build anything. It is the signal the gate needs, you probably already have it in the reasoning trace, and reading it there costs nothing.
- Justify the gate on a stopping point that survives a budget change, not on accuracy. If your budget is fixed and your calls are cheap, a stated budget is the cheaper buy.
- Fit the threshold to your own sources' recovery behavior, and re-fit it when they change. Five was fitted to sources recovering within three failures.
- Check the direction of your failure first. An agent that already answers too early needs a budget floor, not a gate.
- Probe with a doubled budget before and after. A stopping point that moves with the deadline is not reading the evidence.

## Related

- [Agent Circuit Breaker](agent-circuit-breaker.md) — the same gate for loud failures, counting errors instead of relevance judgments
- [Retry-Switch-Abstain: A Runtime Tool-Recovery Policy](retry-switch-abstain-recovery-policy.md) — the prompt-side counterpart that supplies a fallback map in context, whose "the policy could live below the model" caveat this measures
- [Silent Adoption of Corrupted Tool Returns by Agents](../anti-patterns/silent-adoption-of-corrupted-tool-returns.md) — the same notice-without-acting gap for returns that are wrong rather than useless
- [Dual-Budget Control for Search Agents: VOI Scoring Per Action](dual-budget-control-search-agents.md) — scores the next action by value of information, where this only decides when to stop
- [Informed Abstention as a Tool-Boundary Runtime Gate](informed-abstention-tool-boundary-gate.md) — blocks before execution on a static precondition, not on accumulated evidence
