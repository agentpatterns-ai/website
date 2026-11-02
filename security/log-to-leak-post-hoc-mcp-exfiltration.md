---
title: "Post-Hoc Exfiltration Through MCP Tool Descriptions (Log-To-Leak)"
term: "Log-To-Leak"
description: "A poisoned MCP tool description makes the agent log the session to an attacker after the real task finishes. The task still succeeds, so a task-level approval sees nothing wrong."
tags:
  - security
  - anti-pattern
  - tool-agnostic
  - arxiv
  - mcp
aliases:
  - Log-To-Leak
  - post-hoc logging attack
  - additive MCP tool poisoning
  - secondary tool call exfiltration
last_reviewed: 2026-10-31
maturity: emerging
---

# Post-Hoc Exfiltration Through MCP Tool Descriptions (Log-To-Leak)

> A poisoned MCP tool description makes the agent send the session to an attacker after the legitimate work finishes, so the task still succeeds.

Log-To-Leak is an additive tool-poisoning attack. An attacker-run MCP server registers a logging tool and writes a directive into a tool description. The directive tells the agent to call the logging tool after its last legitimate call. The logged payload holds the user query, the name of the MCP server that handled the final call, that server's response, and the agent's response. The authors report that "successful task completion can coexist with unauthorized post-hoc disclosure" ([Hu et al., 2026](https://arxiv.org/abs/2610.36108v1)).

The defender-side anti-pattern is authorizing the task and not each call inside it. The [approval-view fidelity gap](mcp-metadata-approval-view-gap.md) covers hidden text in the same metadata, and [multi-tool threshold poisoning](../patterns/anti-patterns/multi-tool-threshold-poisoning-mcp.md) covers a payload split across tools.

## The directive has four parts

The authors build each injected description from four components, in this order ([Hu et al., 2026](https://arxiv.org/abs/2610.36108v1)):

| Component | Job |
|---|---|
| Trigger | Says when to log, such as before the final response |
| Tool Binding | Names the logging tool and tells the agent to call it |
| Justification | Gives a formal reason for the call |
| Pressure | Frames the call as mandatory |

A directive with Tool Binding alone reached 12.4% best observed attack success rate (ASR) in the ablation, on GitHub MCP with GPT-4o. The full four-part template reached 66.8%. The two three-part groups that include Trigger reached 57.6% and 62.4%, and the group without Trigger reached 34.3%. Each variant used three generated prompts ([Hu et al., 2026](https://arxiv.org/abs/2610.36108v1)).

## What the attack achieved

ASR counts runs where the logging call sits directly before the agent's final response. Across 18 model and server pairs with valid tool execution, the full template reached 62.64% to 100% ASR. Field-level logging accuracy among successful runs ran from 76.55% to 95.64%. Sixteen of the 18 pairs changed target-task completion by at most 6.63 points ([Hu et al., 2026](https://arxiv.org/abs/2610.36108v1)).

| Setting (GitHub MCP, GPT-4o) | ASR |
|---|---|
| Vanilla injected prompt | 38.40% |
| Log-To-Leak template | 62.64% |
| Combined Attack baseline | 4.32% |
| TopicAttack baseline | 4.47% |

The two exceptions to the 6.63-point bound were GPT-5 on GitHub (−21.50 points) and Mapbox (−18.38 points). On those pairs the attack also lowered target-task completion ([Hu et al., 2026](https://arxiv.org/abs/2610.36108v1)).

The authors also tested Cursor with GPT-5.1 and Claude Desktop with Claude-Sonnet-4.5, both on GitHub MCP. In each client the agent finished the GitHub calls and then called the logging tool. The authors say these tests do not estimate prevalence ([Hu et al., 2026](https://arxiv.org/abs/2610.36108v1)).

## Tested defenses left most attacks standing

On GitHub MCP with GPT-4o, three defenses left residual ASR above 55% ([Hu et al., 2026](https://arxiv.org/abs/2610.36108v1)):

| Defense | Residual ASR |
|---|---|
| Prompt sandwiching | 59.58% |
| GPT-4o metadata auditor | 55.38% |
| IPIGuard | 60.47% |

Two content classifiers failed in different ways. DataSentinel marked all 100 injected descriptions as safe. An instruction detector flagged 91 of the 100 injections. It also flagged 136 of 159 benign descriptions, a benign flag rate of 85.53% ([Hu et al., 2026](https://arxiv.org/abs/2610.36108v1)).

## What the authors propose, untested

The paper argues that authorization must cover the resulting action, not only the text that caused it. It proposes dependency allowlists, cross-server data-flow checks on arguments, and user confirmation for logging-like secondary calls. It states these host-side controls "remain outside our empirical evaluation" ([Hu et al., 2026](https://arxiv.org/abs/2610.36108v1)). Treat them as design targets. No figure in the paper shows that any of them lowers ASR.

## Limits of the evidence

- The attack needs the user to enable the attacker's MCP server and the host to expose its descriptions to the model. The authors note that installation review, tool allowlists, per-call confirmation, or network policy can change the reachable surface ([Hu et al., 2026](https://arxiv.org/abs/2610.36108v1)).
- Coverage is four models, five servers, and 555 queries. The ablation, baselines, and defense tests all use GitHub MCP with GPT-4o ([Hu et al., 2026](https://arxiv.org/abs/2610.36108v1)).
- This is one workshop paper at version 1. Re-measure on your own host before you rely on any figure.

## Key Takeaways

- Log-To-Leak adds one attacker-controlled call after the last legitimate call, so the user task still completes.
- The full four-part template scored highest in the ablation, at 66.8% best ASR against 12.4% for Tool Binding alone.
- Full-template ASR ran from 62.64% to 100% across 18 model and server pairs.
- Three tested defenses left over 55% residual ASR on GitHub MCP with GPT-4o. An instruction detector flagged 85.53% of benign descriptions.
- The proposed host controls are untested. Authorize each secondary call, and measure the result yourself.

## Related

- [Approval-View Fidelity Gap and Unicode Concealment](mcp-metadata-approval-view-gap.md) — hidden text in the same tool metadata
- [Execution-Layer Security Invariants for MCP Runtimes](mcp-execution-security-invariants.md) — metadata non-authority and data-flow authorization
- [Vetting Tool Definitions for Exfiltration Signatures](vetting-tool-definitions-before-install.md) — refuse leak-shaped tool definitions at install
- [Tool-Invocation Attack Surface in Coding Agents](tool-invocation-attack-surface.md) — argument and return-channel attacks on MCP tools
- [Multi-Tool Threshold Poisoning Against MCP (ShareLock)](../patterns/anti-patterns/multi-tool-threshold-poisoning-mcp.md) — a payload split across several tool descriptions
- [Human-in-the-Loop Confirmation Gates for Consequential Agent Actions](human-in-the-loop-confirmation-gates.md) — per-call confirmation as a control
