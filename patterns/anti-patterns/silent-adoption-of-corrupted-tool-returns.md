---
title: "Silent Adoption of Corrupted Tool Returns by Agents"
term: "Silent Adoption of Corrupted Tool Returns"
description: "Agents often adopt wrong tool returns over answers they already had, notice the conflict, and still warn the user in only a small share of final answers."
tags:
  - testing-verification
  - tool-agnostic
  - anti-pattern
  - arxiv
aliases:
  - tool return overreliance
  - corrupted return adoption
  - silent conflict adoption
last_reviewed: 2026-09-30
maturity: emerging
status: current
---

# Silent Adoption of Corrupted Tool Returns by Agents

> Agents adopt wrong tool returns over answers they could give correctly alone, and they rarely tell the user about the conflict.

## The anti-pattern

An agent adopts a tool return that is wrong, and the user never learns the return was in doubt. The harness treats the tool channel as ground truth. At most, the system prompt asks the agent to verify. Neither step produces a warning when a return conflicts with what the model already knows.

The best measure is the override rate: how often the agent adopts a corrupted return on an item it answers correctly without the tool (at least 2 of 3 no-tool runs correct). Yang et al. tested 14 models with three tools: web search, an LLM sub-agent, and a code executor. Under P1 corruption, where the injected value is plausible, mean override rate reaches 56.4% in Search, 26.8% in Sub-Agent, and 33.5% in Code Executor ([Yang et al., arXiv:2609.05587v2](https://arxiv.org/abs/2609.05587v2)). The paper's reading: "corrupted returns frequently displace answers the models can produce correctly."

## Conditions that decide the risk

The risk depends on the tool channel and on how believable the wrong value is.

- Plausible values. P1 for Search uses a real value that was once correct or is easily confused with the gold answer. Mean adoption exceeds one third for every tool under P1 and stays above one tenth under P2, where the injected answer is unrelated ([Yang et al.](https://arxiv.org/abs/2609.05587v2)). Adopting a formerly correct value is sometimes reasonable, which is why override rate is the better headline.
- Sub-agent reports. On QuALITY, the adoption rate reaches 94.7% and the override rate reaches 91.9% for a false claim in a delegated reading report ([Yang et al.](https://arxiv.org/abs/2609.05587v2)). Coding assistants that delegate to sub-agents use this channel.
- Tool chains. Across two tool combinations, mean task accuracy falls from 98.4-98.8% with correct returns to 19.8-26.2% when both tools are corrupted (6 models, 54 tasks) ([Yang et al.](https://arxiv.org/abs/2609.05587v2)).
- Frontier models. GPT-5.4, Claude Sonnet 5, Claude Opus 4.8, and Grok 4.6 each show a P1 adoption rate of roughly half, with override rates of 33.3-40.0%. That result comes from a prespecified 90-item subset with one run per condition, so the intervals are wide ([Yang et al.](https://arxiv.org/abs/2609.05587v2)).

Model scale gives conflicting evidence. Yang et al. report that "larger models generally have lower adoption rates, but this advantage does not hold across all tools." [Blind Tool Deference](blind-tool-deference.md) cites Wang and Vemuri, who found the opposite trend on a GNN tool. The two setups differ, so treat scale as no reliable fix.

## Noticing without warning

The agent often detects the conflict. The two Qwen models mention a conflict in 87.9-96.0% of adopting Code Executor runs. Gemini-3.1-flash-lite mentions a conflict in 62.8% of its available Search summaries, "yet none of the corresponding final answers warns the user" ([Yang et al.](https://arxiv.org/abs/2609.05587v2)). Only Qwen exposes full reasoning traces. GPT and Gemini expose reasoning summaries.

Warnings are rare overall. Across Search and Code Executor, they appear in 4.2% of final answers, and one model (Muse) drives most of that. Excluding Muse gives 1.5%. The 4.2% pools both tools. The Search-only pooled rate is 5.3% with Muse included ([Yang et al., Appendix D.1 and Table 14](https://arxiv.org/abs/2609.05587v2)).

## Why it happens

Detection happens but does not change the output. In three open models, probes separate corrupted from correct returns in Code Executor runs, with AUROCs of 0.997, 0.993, and 1.000 ([Yang et al., §5.4](https://arxiv.org/abs/2609.05587v2)). Models also make more tool calls after a corrupted return. The default agent loop has no step that turns that internal signal into a changed answer or a user-facing warning.

Confidence explains part of adoption. ClashEval found that a model adopts retrieved content more often when it is less confident in its first response, and less often as the content deviates further from the truth ([ClashEval, arXiv:2404.10198v3](https://arxiv.org/abs/2404.10198v3)). Neither paper explains why a noticed conflict fails to reach the final answer, so this page offers no cause for that step.

## What mitigations measure

Prompt-level fixes move adoption by a few points. The numbers are 6-model means under P1 corruption.

| Mitigation | Effect on adoption | Cost |
|---|---|---|
| Verify prompt (re-check conflicting returns with more tool calls) | Search 75.4% to 70.0%, Sub-Agent 39.0% to 35.2%, Code Executor 40.2% to 30.4% | Accuracy with correct returns is largely kept |
| Compare prompt (check returns against prior knowledge) | Lowest adoption in Search and Sub-Agent | Accuracy with correct returns falls: Search 94.2% to 90.9%, Sub-Agent 68.1% to 63.7% |
| Low reliability label on search results | Lowest mean adoption, and lower than Plain for all six models | Adoption stays high, for example Qwen3-30B 81.9% to 78.0% |
| Post-training recipes tested | No reliable gain | "widely used post-training recipes fail to teach models to resist corrupted returns while retaining performance with correct ones, at least at the scales tested" |

Source for the table: [Yang et al., §5.1 to §5.3](https://arxiv.org/abs/2609.05587v2).

## Applying it in a harness

Put the fix in the output contract and the tool set, not only in the prompt.

1. Require the final answer to state any conflict between a tool return and the agent's own knowledge or another source.
2. Add a source that does not share an upstream with the first. A re-query of the same search index or the same sub-agent returns the same error.
3. Ask sub-agents to return evidence with each claim, and check the claims that decide the answer.
4. Keep a deterministic gate such as tests or CI after the agent for work that has one.

[Exception Handling and Recovery Patterns](../agent-design/exception-handling-recovery-patterns.md) covers failures the agent can see. It does not cover a return that looks fine and is wrong.

## When this backfires

Cross-checking every return costs more than it saves in several cases.

- Deterministic verified tools such as a compiler, type checker, test runner, or formatter. The paper's Code Executor corruption is synthetic: it rewrites real outputs, for example replacing every number in the captured stdout. It measures trust in the tool channel, not how often real interpreters fail.
- Fast-changing facts where the tool is the only current source. The Compare result shows the cost: the instruction "may encourage agents to question even reliable tool information".
- Stale or biased memory. Xie et al. find that models given both supportive and contradictory evidence "show a strong confirmation bias" and "tend to cling to their parametric memory" ([Xie et al., arXiv:2305.13300v4](https://arxiv.org/abs/2305.13300v4)). A cross-check against memory can reject correct data.
- No second source in scope. "Verify" then means more calls to the same tool.
- A cheap downstream gate. If CI or a reviewer checks the final result, per-call verification repeats work for a small gain.
- A prompt as the whole defense. After the Verify prompt, Search adoption is still 70.0%.

The paper also states its limits: results may change with API model retirement, stochastic outputs, and shifts in search results over time ([Yang et al., Reproducibility statement](https://arxiv.org/abs/2609.05587v2)).

## Key Takeaways

- Judge overreliance by override rate. Under P1 corruption, agents replaced answers they could give correctly 56.4% of the time in Search.
- The 4.2% warning rate pools Search and Code Executor and falls to 1.5% without one model. It is not a web-search figure.
- Agents often notice the conflict and still do not tell the user.
- Sub-agent reports and chained tools carry the highest measured risk.
- Prompts give small gains, and a distrust prompt costs accuracy when returns are right. Add an independent source and a disclosure requirement.

## Related

- [Blind Tool Deference](blind-tool-deference.md) - deference to a tool that returns correct output, and the scale result that conflicts with this page
- [Unsignalled Tool Failure](unsignalled-tool-failure-envelope.md) - a tool that returns success around an unusable payload
- [Trusting Tool Error Messages as Implicit Authority](tool-error-implicit-authority.md) - the same trust on the error stream
- [Exception Handling and Recovery Patterns](../agent-design/exception-handling-recovery-patterns.md) - recovery for failures the agent can observe
- [Trust Without Verify](trust-without-verify.md) - the operator-side counterpart
