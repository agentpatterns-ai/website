---
title: "MCP-vs-CLI Cost Ratios Are a Property of the Scaffolding"
term: "Scaffolding-Bound Interface Cost"
description: "Paired MCP-to-CLI cost ratios span 0.43x to 29x across agent scaffoldings, so a multiplier borrowed from another benchmark cannot size the saving in your harness."
aliases:
  - MCP CLI cost multiplier portability
  - scaffolding-bound interface cost
  - borrowed MCP cost ratio
tags:
  - tool-engineering
  - cost-performance
  - tool-agnostic
  - mcp
  - arxiv
last_reviewed: 2026-08-11
maturity: emerging
---

# MCP-vs-CLI Cost Ratios Are a Property of the Scaffolding

> A published MCP-versus-CLI cost multiplier describes the scaffolding it was measured on, and the same comparison inverts under a different scaffolding.

A cost ratio between MCP tool access and CLI tool access describes one agent scaffolding rather than the two interfaces. Across one fixed software task run on seven scaffoldings and five models, thirteen strictly paired MCP-to-CLI ratios spanned 0.43x to 29x, with outliers on both sides ([Alier Forment et al., arXiv:2608.08654v1](https://arxiv.org/abs/2608.08654v1)). A ratio under 1.0 is a pairing where MCP came out cheaper. Read a quoted multiplier as a report about someone else's harness, and measure the delta in yours before migrating tool access to chase it.

## The conditions this applies under

Three conditions decide whether the finding changes anything for you.

- The scaffolding is yours to vary. On a managed or consumer-tier agent the orchestration layer is vendor-controlled, so the interface is the only lever you hold and there is nothing to re-measure. See [managed vs self-hosted harness](../patterns/agent-design/managed-vs-self-hosted-harness.md).
- Cost is the axis you are deciding on. Where a credential has to stay outside the agent's context, the [auth boundary settles the choice](mcp-auth-isolation-vs-cli-selection.md) whatever the token arithmetic says.
- Your work resembles the measured task, which was six operations against a private git repository ([Alier Forment et al., arXiv:2608.08654v1](https://arxiv.org/abs/2608.08654v1)).

## Measure the delta in your own harness

Run the same task under your scaffolding twice, once with the MCP server attached and once with no server attached anywhere, and price both runs. That number is the only ratio that describes your setup.

Then verify what the agent actually did. Agents frequently ignored the interface they were assigned, so a comparison that does not check real behavior measures an unknown mixture of the two ([Alier Forment et al., arXiv:2608.08654v1](https://arxiv.org/abs/2608.08654v1)). The authors confirmed completion by inspecting repository state rather than trusting the agent's self-report, which is the check to copy.

Track spend on failed runs as its own line. The two interfaces separated on the cost of failure and not on its frequency: 12.9 per cent of the money spent on MCP runs bought no completed work, against 2.2 per cent on CLI runs, while failures were equally common under both in the original runs and their repetitions ([Alier Forment et al., arXiv:2608.08654v1](https://arxiv.org/abs/2608.08654v1)). A pass-rate comparison hides that gap entirely.

## Why it works

Agent bills are input-dominated and conversation history is prepended on every call, so per-turn overhead the scaffolding adds compounds through the whole loop instead of being paid once. Swapping only the orchestration layer around a fixed model cut blended cost per task 41 per cent, from $0.21 to $0.12, across six foundation models ([Sayed Ali et al., arXiv:2607.06906v1](https://arxiv.org/abs/2607.06906v1)). Whether tool schemas sit in the standing prompt is itself a scaffolding configuration decision, which is why one nominal comparison yields ratios two orders of magnitude apart. The scaffolding term is large enough to swamp the interface term: a 27-billion-parameter model running locally varied 139x in cost across scaffoldings while completing the task under all of them ([Alier Forment et al., arXiv:2608.08654v1](https://arxiv.org/abs/2608.08654v1)).

## When this backfires

- Short loops with a large attached catalog. When a run takes a handful of turns and dozens of tool definitions sit in the standing prompt, schema cost approaches a fixed floor and the interface does dominate that run. Attaching fewer servers is the cheaper move, and [tool minimalism](tool-minimalism.md) gets you there without a benchmark.
- The headline still favors CLI in absolute terms. Two of the seven scaffoldings ship no MCP support, completed every run over the CLI alone, and were 5.0x to 28x cheaper than the five that support MCP ([Alier Forment et al., arXiv:2608.08654v1](https://arxiv.org/abs/2608.08654v1)). A team that skips the measurement and defaults to the CLI will usually land somewhere reasonable.
- Those cheapest configurations had no MCP server attached anywhere, so some of that gap is simply the absence of schemas in context. Scaffolding and interface are not cleanly separated in the headline comparison, and the paper is at v1 with no full-text rendering to check the per-scaffolding tables against.
- Self-hosted inference. The 139x spread comes from a locally run model, where the marginal token price that makes "cheaper" meaningful is close to zero.
- Measurement is not free. Two priced runs plus behavior verification cost engineering time, and below a few thousand agent runs a month the borrowed default may be worth its inaccuracy.

## Example

The verification step is the part most published comparisons skip. After each run, ask the repository what happened instead of reading the agent's summary, and count tool calls in the transcript to find out which interface the run really used.

```bash
# Did the operations actually land? Ask the repository.
git -C ./target-repo log --oneline -6
git -C ./target-repo ls-remote --heads origin

# Which interface did this run use? Count tool_use blocks by name.
jq -r 'select(.type == "tool_use") | .name' run.jsonl | sort | uniq -c
```

A run that reports success while the log shows four commits is a failure that a self-report comparison scores as a pass. A run assigned to the MCP arm whose tool calls are mostly shell invocations belongs in neither arm.

## Key Takeaways

- Paired MCP-to-CLI cost ratios ran from 0.43x to 29x across scaffoldings on one fixed task, so the multiplier is not a property of the interface ([Alier Forment et al., arXiv:2608.08654v1](https://arxiv.org/abs/2608.08654v1)).
- Price the same task under your own scaffolding with and without the server attached; that is the only ratio that applies to you.
- Verify which interface the agent actually used from end state, because agents frequently ignore the one they were assigned.
- Failure frequency was equal across interfaces while wasted spend was not, at 12.9 per cent against 2.2 per cent, so track failed-run cost as a separate line.
- The evidence is one paper, one task, thirteen paired ratios, and a configuration confound in the headline comparison. Treat the magnitudes as directional.

## Related

- [Auth-Isolation as the MCP-vs-CLI Selection Heuristic](mcp-auth-isolation-vs-cli-selection.md) — the non-cost axis of the same decision, where the credential boundary settles it regardless of token arithmetic
- [Unix CLI as the Native Tool Interface for AI Agents](unix-cli-native-tool-interface.md) — the case for the CLI side of this comparison, which this page declines to size with a borrowed number
- [Harness-Controlled Token Economics](../token-engineering/harness-token-economics.md) — the mechanism behind the scaffolding term, measured against the model rather than the tool interface
- [Cross-Framework Signal Semantics](../verification/cross-framework-signal-semantics.md) — the same principle one domain over: re-measure a borrowed rule in your own harness before adopting it
- [Head-to-Head Evaluation of Competing MCP Servers](../verification/head-to-head-mcp-server-evaluation.md) — the fixed-configuration method for running the paired comparison this page prescribes
- [Building Custom Agents from Substrate to Production](../workflows/agents-all-the-way-down-methodology.md) — the companion methodology from the same author team ([arXiv:2606.11869](https://arxiv.org/abs/2606.11869))
