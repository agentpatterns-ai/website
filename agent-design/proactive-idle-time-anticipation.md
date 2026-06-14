---
title: "Proactive Idle-Time Anticipation (ProAct)"
term: "Proactive Idle-Time Anticipation"
description: "Use idle time between user turns to prefetch likely next needs from dialogue history and persistent memory — only when need chains are predictable."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
  - memory
  - arxiv
  - long-form
aliases:
  - proactive agent prefetching
  - inter-turn idle-time anticipation
  - anticipatory agent architecture
last_reviewed: 2026-06-02
maturity: emerging
---

# Proactive Idle-Time Anticipation (ProAct)

> Anticipation of likely next user needs runs during idle wall-clock between turns, using dialogue history and persistent memory to direct speculative prefetching.

Proactive idle-time anticipation runs a future-state predictor over recent dialogue and persistent memory during the wall-clock between user turns, value-scores candidate needs, and spends a bounded search budget acquiring evidence before the user asks. The technique only outperforms a reactive baseline when the dialogue admits predictable need chains, the idle window is long enough for delivery before the next turn, dollar cost is not the binding constraint, and the deployment context tolerates the privacy posture of speculative memory reads ([Hu et al., arXiv:2605.25971](https://arxiv.org/abs/2605.25971)).

## When This Applies

Four conditions must hold together before the pattern earns back its speculative compute. If any fails, run a reactive baseline and route the saved budget into [reasoning budget allocation](reasoning-budget-allocation.md).

- **Predictable need chains in the dialogue.** ProAct models scenarios with a hidden user-needs graph whose nodes carry `predictable_after` dependencies; it scored 0.447 Anticipation Recall versus 0.020 for an undirected baseline ([arXiv:2605.25971](https://arxiv.org/abs/2605.25971)). Without structure to predict against — single-shot Q&A, scattershot topic-hopping — there is nothing to anticipate.
- **Persistent memory exists and is trustworthy.** The predictor decomposes future needs from user profiles, entity facts, summaries, and prior artifacts. No memory degenerates the predictor to dialogue-only extrapolation; stale memory injects wrong predictions confidently. See [agent memory patterns](agent-memory-patterns.md) for the substrate.
- **Idle wall-clock exceeds the predict-acquire-deliver loop.** Anticipation pays off only if the artifact lands before the next turn. In 82 of 200 scenarios recall improved without reducing user effort because predictions arrived too late ([arXiv:2605.25971](https://arxiv.org/abs/2605.25971)).
- **Latency dominates dollar cost.** Directed Idle consumed **111.8k active tokens per scenario** versus 0 for Reactive, at 687s vs 265s wall-clock. The paper treats the search budget as "an operating point that balances efficiency gains against compute cost, rather than as a parameter to maximize" ([arXiv:2605.25971](https://arxiv.org/abs/2605.25971)).

## How It Works

Two modules run during the idle window, sharing memory as state ([arXiv:2605.25971](https://arxiv.org/abs/2605.25971)). **Future-State Prediction** generates candidate needs through three channels — local prediction from recent turns, related expansion from profile and stored facts, and memory-gap augmentation when stored knowledge is stale — then confidence-filters and deduplicates them. **Idle-Time Acquisition and Delivery** value-scores each candidate by `S(z) = wr·rz + wg·gz + wv·vz + wτ·τz` (relevance, knowledge gap, incremental value, timeliness); candidates above threshold θval spend search budget on retrieval, and a delivery policy routes each artifact via `push` (notify now), `queue` (integrate next turn), or `store` (silent memory write).

```mermaid
graph TD
    U[User turn N] --> M[Memory + dialogue history]
    M --> P[Future-State Predictor]
    P -->|candidates| V[Value gate<br>composite score above threshold]
    V -->|above threshold| A[Acquire evidence<br>bounded search budget]
    A --> D{Delivery policy}
    D -->|push| N[User notification]
    D -->|queue| Q[Ready for turn N+1]
    D -->|store| M
    M --> U2[User turn N+1]
```

This is the inter-turn sibling of [idle-time speculative planning](idle-time-speculative-planning.md): that technique speculates *plans* between tool dispatch and observation *inside* one [agent turn](agent-turn-model.md); this one speculates *user needs* between turns. They compose, each filling a different idle window.

## Why It Works

Idle time between turns is underutilised compute: the inference budget is paid regardless of whether tokens are generated. The accuracy lift comes from converting that slack into *directed* speculation — needs resolved before the next turn are skipped by the simulator, reducing `User Effort` and `T100` (turns to full must-have coverage). Removing the predictor (Undirected Idle, matched token budget) beats Reactive by only 0.9% on T100 versus Directed Idle's 14.1% — direction is the load-bearing component, not raw compute ([arXiv:2605.25971](https://arxiv.org/abs/2605.25971)). The 28.1% hallucination reduction comes from memory-gap augmentation: when a candidate need exposes incomplete stored knowledge, the agent grounds the next answer in acquired evidence rather than confabulating.

## When This Backfires

The pattern is Qualified, not a default. Five failure modes recur in the paper's own evaluation ([arXiv:2605.25971](https://arxiv.org/abs/2605.25971)).

- **Proactive context competes with the reactive answer.** In 3% of scenarios (6/200) Directed Idle scored *smaller* must-have coverage than Reactive; the museum-conservation case (Table 13) drops to 50% versus Reactive's 100%, T100 worsening from 6 to 11 turns — the artifact crowds the response budget.
- **Precision-recall decoupling.** In 82 scenarios recall improved without reducing User Effort: the prediction was correct but landed after the user already asked. Anticipation that doesn't beat the next turn is pure cost.
- **Low-value push pressure.** Scaling the search budget to k=16 lifted recall to 0.432 while User Effort gains flat-lined and unhelpful pushes increased, altering trajectories negatively.
- **Cost-bound deployments on metered APIs.** 111.8k extra tokens per scenario at GPT-4o rates is real money for a 14.8% T100 win. Pair with [cost-aware agent design](cost-aware-agent-design.md) to confirm latency, not dollar cost, binds.
- **Privacy posture incompatible with speculative memory reads.** The authors flag under Broader Impacts that "persistent memory and future-need prediction can create privacy risks if applied to real user histories, especially if systems infer sensitive needs or monitor behavior without clear consent." Clinical, financial, and legal deployments need consent, retention, and access-log controls first.

The paper caveats the headline result as well: "These results come from a closed-world synthetic benchmark, so they should be read as controlled evidence rather than a deployment guarantee in open-world personal assistants." Real deployments need user controls, rate limits, and monitoring.

## Reported Gains

On ProActEval (200 scenarios, 40 domains, GPT-4o assistant and simulator, GPT-4o-mini judge), Directed Idle versus Reactive ([arXiv:2605.25971](https://arxiv.org/abs/2605.25971)):

| Metric | Reactive | Directed Idle | Delta |
|--------|----------|---------------|-------|
| T100 (turns to full must-have coverage) | baseline | −14.8% | improvement |
| User Effort (explicit user questions) | baseline | −11.7% | improvement |
| Hallucination Rate | baseline | −28.1% | improvement |
| Anticipation Recall | 0 | 0.447 | 703 / 1,572 predictable needs anticipated |
| Active tokens per scenario | 0 | 111.8k | cost |
| Wall-clock per scenario | 264.8s | 687.2s | longer |

Anticipation Recall comparison against the prior baseline ProactiveAgent (Lu et al., 2024; [arXiv:2410.12361](https://arxiv.org/abs/2410.12361)): 0.447 versus 0.020. The 22× gap isolates the contribution of directed prediction over undirected proactive task initiation.

## Example

The ProAct reference implementation runs three evaluation conditions against the same 200 ProActEval scenarios — useful for ablating whether idle compute or *directed* idle compute is doing the work ([AgentACE-AI/ProAct on GitHub](https://github.com/AgentACE-AI/ProAct)).

```bash
# .env
OPENAI_API_KEY=sk-...
SERPER_API_KEY=...    # optional, for web search during acquisition
JINA_API_KEY=...      # optional, for content fetching

# Run the three evaluation conditions against a single scenario
python experiments/run_scenario.py \
  --scenario scenarios/personal_life/scenario_007.json \
  --condition baseline       # Reactive — no idle compute
python experiments/run_scenario.py \
  --scenario scenarios/personal_life/scenario_007.json \
  --condition blind          # Undirected idle — search without prediction
python experiments/run_scenario.py \
  --scenario scenarios/personal_life/scenario_007.json \
  --condition full-single-idle  # Directed idle — full ProAct
```

The three conditions ablate the load-bearing component: `baseline` measures the reactive floor, `blind` measures the value of idle compute *without* direction, and `full-single-idle` measures the value of *directed* idle compute. The 0.9%-vs-14.1% T100 gap between `blind` and `full-single-idle` is what tells you the predictor (not the search budget) is what's earning the latency win ([arXiv:2605.25971](https://arxiv.org/abs/2605.25971)).

## Key Takeaways

- Idle time between user turns is wasted compute on a reactive harness; ProAct converts it into directed prefetching of likely next needs from dialogue history and persistent memory.
- The accuracy lift is causal — needs anticipated and resolved before the next turn skip explicit user questions — but only when the dialogue admits predictable need chains and the idle window is long enough for delivery.
- Direction is the load-bearing component: idle compute *without* the future-state predictor barely beats Reactive (0.9% T100 gain) while idle compute *with* the predictor lifts T100 by 14.1%.
- The technique is Qualified, not a default: skip when need chains aren't predictable, idle windows are short, dollar cost is the binding constraint, or the privacy posture forbids speculative memory reads. In 3% of evaluated scenarios proactive context competed with the reactive answer and *worsened* coverage.
- Compose with [agent memory patterns](agent-memory-patterns.md) (the prediction substrate) and [idle-time speculative planning](idle-time-speculative-planning.md) (the intra-turn sibling that fills a different idle window).

## Related

- [Idle-Time Speculative Planning for ReAct Agents](idle-time-speculative-planning.md) — intra-turn idle-time technique; speculates plans between tool dispatch and observation while this page speculates needs between user turns
- [Asynchronous Agent I/O and Speculative Tool Calling](asynchronous-agent-io-and-speculative-tools.md) — speculative tool dispatch at the FSM/tool boundary for real-time agents; complementary idle-time mechanism at the tool-call layer
- [Background Todo Agent](background-todo-agent.md) — another pattern that offloads work to a different idle channel — bookkeeping rather than anticipation
- [Agent Memory Patterns: Learning Across Conversations](agent-memory-patterns.md) — the persistent-memory substrate the predictor reads from
- [Cost-Aware Agent Design: Route by Complexity, Not Habit](cost-aware-agent-design.md) — the cost-routing discipline that decides whether the 111.8k speculative tokens per scenario are worth spending
