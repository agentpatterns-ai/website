---
title: "Claude Code Subagent Model Fallback: What Carries Down"
description: "From v2.1.330 a subagent's model fallback carries over to the no-model agents and forks it starts. What the changelog says, what it leaves open, and how to check each agent's model."
tags:
  - claude
  - agent-design
  - cost-performance
applies_to: "claude-code@2.x"
last_reviewed: 2026-11-22
status: current
---

# Claude Code Subagent Model Fallback: What Carries Down

> From v2.1.330, a subagent's fallback model also applies to the forks and no-model agents it starts.

The v2.1.330 changelog (November 20, 2026) records the change in one line: "Changed a subagent's model fallback to carry over: agents with no model and forks it then starts run on the fallback, and the agents they start use its Bedrock region" ([changelog](https://code.claude.com/docs/en/changelog)). The sub-agents and model configuration pages do not describe the carry-over as of November 22, 2026.

## What the entry names

The entry names two groups that follow a subagent onto its fallback model: agents with no model set, and forks. Agents they start "use its Bedrock region". The entry does not say whether "its" means the subagent or the fallback. Agents that have a model set go unnamed, and the entry does not say what a pinned model does when its parent is on a fallback.

Both named groups already take their model from the parent. For a nested subagent, the sub-agents page lists three cases that run on the parent's model: a subagent with `model: inherit` or no `model` field, the built-in Explore, Plan, and general-purpose subagents, and a fork ([sub-agents](https://code.claude.com/docs/en/sub-agents.md#which-model-a-nested-subagent-runs-on)). A fork's model is the same as its parent conversation's ([sub-agents](https://code.claude.com/docs/en/sub-agents.md#how-forks-differ-from-other-subagents)).

When more than one source sets a model, Claude Code uses the first of these ([sub-agents](https://code.claude.com/docs/en/sub-agents.md#choose-a-model)): the per-invocation `model` parameter, the `model` field in the subagent's definition, the `CLAUDE_CODE_SUBAGENT_MODEL` variable, then the parent's model. The entry does not place the carry-over in that order. It does not say whether `CLAUDE_CODE_SUBAGENT_MODEL` still applies to an agent with no `model` field. It does not mention the first three, which are where you pin a model.

## How a subagent gets onto a fallback

The entry says "a subagent's model fallback" without saying which fallback. The docs describe three ways a subagent can leave its model:

| Path | What happens to the subagent | Source |
|------|------------------------------|--------|
| Fallback chain | When a request fails over, Claude Code tries the configured models in order and the subagent continues on the one that accepts the request. The session's model is unchanged. | [Model configuration](https://code.claude.com/docs/en/model-config.md#which-entries-claude-code-tries) |
| Flagged request (safety classifier) | If a fallback model is available and the "Switch models when a message is flagged" choice in `/config` is "Switch automatically" or unset, the request re-runs on the fallback. With "Ask each time", the subagent fails (from v2.1.318). | [Model configuration](https://code.claude.com/docs/en/model-config.md#subagents-switch-or-fail-without-asking) |
| Allowlist blocks the model | For a blocked family alias, on providers that support it, the newest permitted version of that family. Otherwise `CLAUDE_CODE_SUBAGENT_MODEL` if set, then the parent's model. | [Sub-agents](https://code.claude.com/docs/en/sub-agents.md#when-an-allowlist-blocks-a-subagent-model) |

You set the chain with the `fallbackModel` setting or the `--fallback-model` flag. A chain holds at most three models after duplicates are removed ([model configuration](https://code.claude.com/docs/en/model-config.md#fallback-model-chains)). For subagents, the chain applies from v2.1.247 ([model configuration](https://code.claude.com/docs/en/model-config.md#which-entries-claude-code-tries)).

The changelog does not say which of the three the carry-over covers. Test the path you rely on.

## Bedrock region

The entry says the agents a carried-over agent starts "use its Bedrock region". The Bedrock page documents these region inputs:

- Claude Code resolves the region from `AWS_REGION`, then `AWS_DEFAULT_REGION`, then the active AWS profile's `region`, then `us-east-1`.
- `ANTHROPIC_SMALL_FAST_MODEL_AWS_REGION` overrides the region for the small/fast model. On Bedrock it has no effect without `ANTHROPIC_DEFAULT_HAIKU_MODEL` or the deprecated `ANTHROPIC_SMALL_FAST_MODEL`.

Source: [Amazon Bedrock](https://code.claude.com/docs/en/amazon-bedrock.md). The entry does not say which of these "its Bedrock region" means. Run `/status` to see the resolved region, and confirm where nested agents send requests.

## Check which model each agent ran on

- While a subagent runs, `/tasks` names its model on the subagent's row. This needs v2.1.242 or later ([sub-agents](https://code.claude.com/docs/en/sub-agents.md#check-a-subagents-model)).
- When a subagent finishes on a fallback, its report opens with `⚠ This agent switched to <model> because its earlier model could not be used.` ([sub-agents](https://code.claude.com/docs/en/sub-agents.md#api-errors-in-subagents)).
- Claude Code does not confirm the chain at startup, and `/status` does not display it ([model configuration](https://code.claude.com/docs/en/model-config.md#fallback-model-chains)).

## When a fork needs a different model

A fork's model is its parent's. Setting `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` leaves forks on their parent's model too ([sub-agents](https://code.claude.com/docs/en/sub-agents.md#run-every-subagent-on-one-model)). From v2.1.330, a fork started by a subagent on a fallback runs on that fallback ([changelog](https://code.claude.com/docs/en/changelog)).

For work that needs a specific model, use a non-fork subagent, which follows the subagent model order above. Test it under a parent on a fallback, because the entry does not cover that case.

## Choose the chain for the agents it starts

If the carry-over covers the fallback chain, one chain entry can set the model of every no-model agent and fork that the failing subagent starts. Pick entries you would accept for those agents. The entry does not say which model the agents they start run on, only that they use "its Bedrock region".

## Key Takeaways

- From v2.1.330, agents with no model and forks that a subagent on a fallback starts run on the fallback.
- The entry names no agent with a model set. Pin a model where a step must not follow the fallback, and test.
- The entry does not say which fallback paths it covers, or which Bedrock region setting "its Bedrock region" means.
- Check each agent's model with `/tasks` and the report's `⚠ This agent switched` line. The chain is not shown at startup.
- From v2.1.330, a fallback on the parent subagent decides a fork's model, and `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` does not move a fork off its parent's model.

## Related

- [Claude Code Sub-Agents for Delegating Complex Tasks](sub-agents.md)
- [Forked vs Fresh Subagents](../../patterns/multi-agent/forked-vs-fresh-subagents.md)
- [The Subagent Inheritance Contract: What Crosses Down](../../patterns/multi-agent/subagent-inheritance-contract.md)
- [Recursive Sub-Agent Delegation Depth](../../patterns/multi-agent/recursive-sub-agent-delegation-depth.md)
- [Model Switch Lifecycle Hooks](../../tool-engineering/model-switch-lifecycle-hooks.md)
- [Exception Handling and Recovery Patterns](../../patterns/agent-design/exception-handling-recovery-patterns.md)
