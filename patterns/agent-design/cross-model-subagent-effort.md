---
title: "Cross-Model Subagent Effort Resolution in Claude Code"
term: "Cross-Model Subagent Effort Resolution"
description: "A Claude worker on another model uses that model's saved effort or default. Check overrides and the running worker before assuming session effort carries over."
tags:
  - agent-design
  - cost-performance
  - claude
applies_to: "claude-code@2.1.317"
last_reviewed: 2026-11-06
status: current
maturity: emerging
---

# Cross-Model Subagent Effort Resolution in Claude Code

> Cross-model subagents resolve their default effort from their own model, so the parent's session setting does not establish every worker's reasoning level.

Cross-model effort resolution selects a worker's effort independently of the parent's session choice. Claude Code 2.1.317 changed subagents and teammates on another model to use that model's saved effort, or its default ([release notes](https://code.claude.com/docs/en/changelog#2-1-317)). The rule matters when a delegation changes models without naming effort.

## Defaults and overrides

The [model configuration reference](https://code.claude.com/docs/en/model-config#effort-level-of-subagents-and-teammates) distinguishes same-model inheritance from cross-model resolution. A worker without its own effort inherits the session level only on the main conversation's model.

Explicit settings still matter. `CLAUDE_CODE_EFFORT_LEVEL` overrides an invocation's `effort` parameter, which overrides the agent definition's `effort` field. The invocation parameter applies to non-fork subagents and persists on resume ([subagent effort reference](https://code.claude.com/docs/en/sub-agents#choose-an-effort-level)). An effort cap can lower the selected level ([model configuration](https://code.claude.com/docs/en/model-config#set-the-effort-level)).

The release note adds a model-dependent default; it does not replace this override chain. The separate `CLAUDE_CODE_SUBAGENT_EFFORT` default shipped in 2.1.316. The cited documentation does not fully place that variable against cross-model saved settings. Avoid inferring an order for their combination ([2.1.316 release notes](https://code.claude.com/docs/en/changelog#2-1-316)).

## Verify a mixed-model run

Use the following review procedure when changing a worker's model:

1. Record explicit effort settings and caps with the model change.
2. Inspect `/tasks` while the worker runs. Its row shows the model and any effort set for that worker ([subagent model reference](https://code.claude.com/docs/en/sub-agents#choose-a-model)).
3. Compare the worker's verified result and cost against the previous configuration before adopting the change.

Prefer an explicit agent-level effort when a repeatable worker needs a chosen level. Still check stronger overrides. A saved user preference is a poor experiment specification because the reviewed agent file does not contain it.

This page establishes configuration behavior, not a measured quality or cost gain. Treat model and effort as separate experiment inputs. Keep the task set fixed when testing either input.

## Key Takeaways

- Include resolved effort in the evidence for a model change.
- Check overrides before attributing a changed worker result to the new default.
- Test combinations involving the subagent effort default rather than filling gaps in the documented precedence chain.

## Related

- [Subagent Effort Floors](subagent-effort-floor.md) — a separate operator-set default
- [Administrative Effort Ceilings](administrative-effort-ceilings.md) — limits on selected effort
- [Effort as a Verification Dial](effort-as-verification-dial.md) — evaluating the work a reasoning budget buys
