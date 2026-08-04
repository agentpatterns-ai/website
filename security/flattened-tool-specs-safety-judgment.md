---
title: "Flattened Tool Specs for Agent Safety Judgment (SafeKeep)"
term: "Flattened Tool Specifications"
description: "Judging a request against a flattened prose rendering of the tool spec, while executing against the schema, restores refusal signals the schema suppresses."
tags:
  - security
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - SafeKeep
  - dual-representation tool specifications
  - schema direction
last_reviewed: 2026-08-03
maturity: emerging
---

# Flattened Tool Specs for Agent Safety Judgment (SafeKeep)

> Judge the request against a prose rendering of the tool spec, then execute against the JSON schema the runtime needs.

Reach for this pattern when three conditions hold: your agent runs an open-weight or weakly aligned model, you can spend a second inference pass per request, and deterministic authorization already sits on the tool call. Under those conditions, judging the request in a separate context that renders tool specifications as plain prose, while the executing agent keeps its JSON schemas, raised the average refusal rate for harmful requests from 23.8% to 70.6% across four models ([Pan et al., 2026](https://arxiv.org/abs/2607.29254v1)).

## What the schema format costs

An aligned model carries refusal behavior along a linear direction in activation space, recoverable as the difference in mean hidden states between harmful and benign requests. On Llama3.1-8B-Instruct that direction separates harmful from benign requests at 0.927 AUROC in a chatbot setting. Adding schema-formatted tool specifications drops the separation to 0.740. Rendering the identical tools as flattened prose restores it to 0.885 ([Pan et al., 2026](https://arxiv.org/abs/2607.29254v1)).

Format drives that gap, not tool semantics. The authors compute a per-layer Schema Direction, the average hidden-state change from presenting one specification as schema instead of prose, and find it negatively aligned with the refusal direction at every layer, for harmful requests only. Activation steering that subtracts the Schema Direction raised refusal from 5.0% to 47.5% ([Pan et al., 2026](https://arxiv.org/abs/2607.29254v1)). That intervention is the causal test.

## How to apply it

Run two contexts against the same model.

1. Judgment context. Same agent instructions, tool specifications rendered as prose. The model answers whether the request is unsafe.
2. Execution context. Unchanged. An approved request reaches the original pipeline with its JSON schemas intact. Tool selection and argument generation are untouched.
3. Refusal path. On an unsafe verdict, block the tool call and prefill a refusal prefix so the model writes a request-specific refusal ([Pan et al., 2026](https://arxiv.org/abs/2607.29254v1)).

Flattening is mechanical: drop JSON syntax, reserved schema fields, nesting, type declarations, and required-field markers; keep the tool name, function signature, what the tool does, and what each argument means. The judge is the same model and needs neither fine-tuning nor access to internal activations, so the pattern applies to proprietary APIs as well as open weights ([Pan et al., 2026](https://arxiv.org/abs/2607.29254v1)).

## Why it works

Schema formatting compresses the harmful-benign separation before generation begins. That loss is visible at the first generated token, so the model starts writing with a weaker signal that the request should be refused ([Pan et al., 2026](https://arxiv.org/abs/2607.29254v1)). The pattern keeps that format out of the judging context while the execution context retains the schema the tool-calling API requires.

The control experiment carries the argument. SafeJudge, the identical two-stage pipeline judging against schemas, reached 6.2% refusal on Llama3.1-8B where the flattened variant reached 72.2% ([Pan et al., 2026](https://arxiv.org/abs/2607.29254v1)). Adding a judgment stage buys almost nothing. Changing the representation that judge reads is the intervention.

## When this backfires

- Your model is already strongly aligned. The lift shrinks as base alignment rises: Llama3.1-8B moved from 5.0% to 72.2% refusal, while GPT5.4-mini moved only from 38.6% to 57.4% ([Pan et al., 2026](https://arxiv.org/abs/2607.29254v1)).
- You treat it as a boundary control. Refusal averages 70.6% afterward and bottoms out at 57.4% ([Pan et al., 2026](https://arxiv.org/abs/2607.29254v1)), so roughly a third of harmful requests still reach execution. Anything that must not happen needs [deterministic policy evaluation at the tool call](mcp-runtime-control-plane.md).
- The harmful work arrives decomposed. The judge sees one request at a time and each sub-request of a [decomposed task](context-fractured-decomposition-attacks.md) is individually benign; decomposition drops refusal from about 90% to 2.5% on Claude Haiku ([DecompBench, 2026](https://arxiv.org/abs/2606.13994v1)).
- Execution authority, not format, is your dominant risk. A separate causal study names tool affordance as the primary driver of agent safety misalignment, reporting violation rates up to 85% once tool access is introduced ([Tool Affordance, 2026](https://arxiv.org/abs/2603.20320v1)). Reformatting a specification removes none of that authority.
- Latency or cost is tight, or your model is small. Every request pays an extra full-context forward pass, and the paper reports no latency, token, or cost figures. Valid benign output rates were also lower on small open models: 83.4% on Llama3.1-8B and 88.4% on Qwen3-8B against 100% on both proprietary models ([Pan et al., 2026](https://arxiv.org/abs/2607.29254v1)).
- You measure success by refusal rate. Adding safety language to a system prompt amplified fabricated policy refusals 15.6x, from 0.25% to 3.95% ([Guardrails as Scapegoats, 2026](https://arxiv.org/abs/2607.19449v1)), so a rising count is not by itself a safety gain. The judge is also the same model as the agent, so it adds no independent check against a jailbreak that already moves the agent.

## Example

A shell-executing tool, as the agent's runtime sees it:

```json
{
  "name": "run_command",
  "description": "Execute a shell command on the host.",
  "parameters": {
    "type": "object",
    "properties": {
      "command": { "type": "string", "description": "The command to run." },
      "timeout": { "type": "integer", "description": "Seconds before abort." }
    },
    "required": ["command"]
  }
}
```

The same tool, flattened for the judgment context:

```text
run_command(command, timeout)
Executes a shell command on the host machine.
  command: the shell command to run.
  timeout: how many seconds to wait before aborting.
```

The judge reads the second form; the agent executes against the first. Capability is identical, and only the surface of the safety decision changed.

## Key Takeaways

- The representation a model judges a tool in is separable from the representation the runtime executes against, and only the first moves refusal behavior.
- Audit what your safety judge actually reads. If it sees the same JSON the executor sees, the format is working against the decision.
- Budget the change as a rendering step, not a new component: the same two-stage pipeline reading schemas scored 6.2% refusal against 72.2% for the flattened one ([Pan et al., 2026](https://arxiv.org/abs/2607.29254v1)).
- Gains scale inversely with base alignment, so spend the extra pass where the model is weakest.
- Layer it above deterministic tool authorization. At a 70.6% average refusal rate it cannot be the control that stops a dangerous call.
- Do not report success as refusal rate alone; refusal counts rise for reasons that have nothing to do with safety ([Guardrails as Scapegoats, 2026](https://arxiv.org/abs/2607.19449v1)).

## Related

- [MCP Runtime Control Plane: Policy Evaluation Between Agent and Tool](mcp-runtime-control-plane.md) — the deterministic enforcement layer this pattern sits above rather than replaces
- [Security-Aware Tool Descriptions for MCP Servers (SpellSmith)](security-aware-tool-descriptions-mcp.md) — the other metadata-side lever on tool specifications, changing content instead of format
- [Destyling Untrusted Input as a Prompt Injection Defense](destyling-untrusted-input.md) — the same family of defense, changing an input's surface form to restore a representation-level safety signal
- [Tool-Invocation Attack Surface](tool-invocation-attack-surface.md) — the attacker's view of the same tool-specification channel
- [Context-Fractured Decomposition Attacks on Tool-Using Agents](context-fractured-decomposition-attacks.md) — the decomposition failure mode that request-level judging does not catch
