---
title: "Delivery-Bound Tool Authorization: When Progressive Discovery Becomes Access Control"
term: "Delivery-Bound Tool Authorization"
description: "Deferring a tool's schema hides it. The boundary exists only when the server that delivered the capability refuses the call, and the guard rather than the role scoping supplies the guarantee."
aliases:
  - delivery-bound authorization
  - progressive skill discovery as access control
  - role-scoped capability delivery
tags:
  - security
  - agent-design
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-28
maturity: emerging
---

# Delivery-Bound Tool Authorization: When Progressive Discovery Becomes Access Control

> Progressive tool discovery becomes access control only when the server that delivered a capability also refuses calls outside it.

Many harnesses defer tool definitions to save context, then call the result least privilege in a security review. That holds only once a refusal happens somewhere the model cannot reach. Stettler et al. built the coupled version, with one MCP server that teaches a role and executes its tools. They measured it against a flat tool list and a multi-agent split over 13 scenarios and six models ([arXiv:2609.28693v1](https://arxiv.org/abs/2609.28693v1)). The evidence is a white paper by the Skilder team, whose product it evaluates, run against a simulated authorization layer, not the shipped server. Read the design result; discount the product framing.

## Conditions that have to hold first

- A catalog above roughly 30 tools. The discovery sequence costs tokens before it saves any, and the paper puts the crossover at about 30 tools ([arXiv:2609.28693v1](https://arxiv.org/abs/2609.28693v1)). At 225 tools a single customer lookup used 9,084 tokens under progressive delivery and 51,330 under flat injection. That curve is one run per configuration, on one model, and "without prompt caching" by the authors' own account, so treat the gap as an upper bound.
- A model pool validated on the discovery protocol. Two of six models failed it often: "Qwen 3.5 (53/100) and Ministral 3 14B (61/100) fail multi-step learn more often than they fail the router" ([arXiv:2609.28693v1](https://arxiv.org/abs/2609.28693v1)). Haiku 4.5 and Gemma 4 31B each scored 100/100 on the same total.
- Room for three round-trips. Discovery "consistently needs more wall-clock time (9–12s vs. 3–5s) because it makes three sequential round-trips to the model" ([arXiv:2609.28693v1](https://arxiv.org/abs/2609.28693v1)). The overhead is fixed, so short tasks pay most.

## What the boundary actually is

The check runs at call time, not at schema time. The agent must learn a role first, then asks the server to run a domain tool through `call_tool`, and "Calls to unlearned tools return ACCESS DENIED with the list of available tools" ([arXiv:2609.28693v1](https://arxiv.org/abs/2609.28693v1)). Hiding the definition is a side effect. The refusal is the control.

The measured guarantee carries its own scope. No unauthorized call or "parameter violation (e.g., a spending-limit breach) executed", but that sentence covers only trials "when models completed discovery and issued a governed call" ([arXiv:2609.28693v1](https://arxiv.org/abs/2609.28693v1)). A model that never reached the router was never tested by it.

## Why it works

A tool schema and a prompt-level policy both get resolved inside the model's context, where they compete with the task. The paper states the failure plainly: "prompt instructions are not access controls: tool-using agents can be induced to take harmful actions despite instructions to the contrary" ([arXiv:2609.28693v1](https://arxiv.org/abs/2609.28693v1)). Binding the check to the delivery path removes the second list. The server that serves the skill also runs the call, so no allowlist can drift from the schema the model saw. OWASP names the general form: "Separate decision-making from execution. The agent can propose an action, but a policy service or execution component should independently validate scope, privilege, and approval state before execution" ([OWASP AI Agent Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html)). That independent validation is the causal ingredient; role packaging is how the capability arrives.

## When this backfires

- You mistake the scoping for the guard. The paper's own ablation separates them. Adding a sequence rule to a plain flat tool list, with no roles at all, reached the same zero: "premature execution falls to 0/30 for both flat+gateway and enforced Skilder" ([arXiv:2609.28693v1](https://arxiv.org/abs/2609.28693v1)). That flat gateway also scored best end-to-end, 27/30 against 24/30. Role membership stops out-of-role tools and nothing else.
- An in-role tool gets used wrongly. A $500 per-call ceiling held in 60 of 60 trials while nine of those trials still issued an unwanted in-limit partial refund. The ceiling bounded the damage. It did not produce the right workflow.
- The model reads your policy as an attack. Opus 4.7 "treats role-embedded policy as injection" ([arXiv:2609.28693v1](https://arxiv.org/abs/2609.28693v1)). In the recorded run it told the customer it was ignoring "manipulative instructions" that were the company's resolution ladder.
- You expected a behavioral win. On the governance theme the multi-agent baseline scored higher than role delivery, 96.7% against 90.4%. Ordinary-task parity also drops, 198/240 against 229/240 flat, which the authors attribute to "protocol cost (the extra learn steps), not a governance leak".
- You are reading a product claim. Section 6.3 is explicit: "Harness, not a product changelog. The simulated authorization layer implements the role design under test" ([arXiv:2609.28693v1](https://arxiv.org/abs/2609.28693v1)). Domain tools returned fixtures.

## Key Takeaways

- Ask where the refusal happens. If the answer is that the tool is absent from the prompt, you have a context optimization and no boundary ([arXiv:2609.28693v1](https://arxiv.org/abs/2609.28693v1)).
- Add the guard before the scoping. A sequence rule over a flat tool list removed every premature execution and scored best end-to-end in the same experiment.
- Check the catalog size first. Below roughly 30 tools the protocol costs tokens, runs 9-12s against 3-5s, and buys a boundary a gateway would have supplied anyway.
- Test your model against the discovery sequence, not only against the router. The spread across six models ran from 53/100 to 100/100.
- Keep workflow policy out of the role text. The $500 ceiling the platform checked held 60/60, while Opus 4.7 read the role's resolution-ladder instructions as a prompt injection and skipped them.

## Example

Two harnesses defer the same 225 tool schemas. In the first, the model sees only a `search_tools` result and calls `process_refund` by name. The harness runs any name it receives, so the deferral hid the schema and blocked nothing.

In the second, one MCP server teaches the Tier 1 Support role and runs `call_tool`. The model asks for `process_refund` before it learns the role. The server answers ACCESS DENIED with the list of available tools, and the call never runs ([arXiv:2609.28693v1](https://arxiv.org/abs/2609.28693v1)). The refusal happens where the model cannot edit it.

## Related

- [Enforced Versus Advisory Controls in LLM-Native IDEs](enforced-versus-advisory-controls.md) — the general sort this page applies to one interface: where a safeguard gets evaluated decides whether it binds
- [MCP Runtime Control Plane: Policy Evaluation Between Agent and Tool](mcp-runtime-control-plane.md) — the gateway shape that the paper's own ablation shows is doing the work
- [Per-Agent Capability Stores Beat One Task-Wide Allowlist](per-agent-capability-scoping.md) — the same least-privilege goal split across sub-agents instead of across roles in one thread
- [Intent-Governed Tool Authorization for AI Agents (IGAC)](intent-governed-tool-authorization.md) — narrowing the manifest per request rather than per learned role
- [MCP alwaysLoad: Classifying Servers as Eager or Just-in-Time](../tool-engineering/mcp-eager-vs-jit-loading.md) — the context-budget side of the same deferral decision, with no security claim attached
