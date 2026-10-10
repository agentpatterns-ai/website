---
title: "Boundary Laundering: Tool Output in Sub-Agent Briefs"
term: "Boundary Laundering"
description: "A tool result pasted into a sub-agent's brief reaches the child as trusted instruction, so per-agent CaMeL fails across the hop. Pass it as opaque data under an enforcing runtime."
aliases:
  - boundary laundering
  - tainted value in sub-agent instruction
  - multi-CaMeL message and variables split
tags:
  - security
  - agent-design
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-09
maturity: emerging
---

# Boundary Laundering: Tool Output in Sub-Agent Briefs

> A tool result written into a sub-agent's brief becomes the child's trusted instruction, even when every agent individually runs CaMeL.

Boundary laundering is the failure where untrusted data crosses an agent boundary inside the natural-language instruction and arrives as trusted input. The paper that names it finds that "CaMeL's guarantees do not compose" ([Peters-Gill et al., arXiv:2610.05640v1](https://arxiv.org/abs/2610.05640v1)). The fix, passing tool-derived values as opaque data the child fetches separately, carries a guarantee only under a runtime that enforces it. Without one, it lowers the authority the text arrives with and nothing more.

## When the guarantee applies

Read the scope before the mechanism, because the result is narrower than the headline.

- Every agent in the hierarchy runs [CaMeL-style control and data separation](camel-control-data-flow-injection.md), with a planner that never reads untrusted data.
- Agents form a tree. The authors leave DAG, cyclic, asynchronous, and peer-to-peer topologies "open for future work" ([arXiv:2610.05640v1](https://arxiv.org/abs/2610.05640v1)).
- An interpreter, not the parent model, rejects any brief that depends on tool output.

Ordinary coding-agent subagents meet none of these. A Claude Code subagent works from a delegation message the parent model composes: "Claude composes a delegation message that summarizes the task, and the subagent works from there" ([Claude Code sub-agents](https://code.claude.com/docs/en/sub-agents)). That message is the instruction channel the paper describes. The documentation describes no separate opaque-data channel and no taint tracking on the message.

## The attack

The paper builds a three-agent system: an Orchestrator, a SQL Agent, and a Notification Agent, each running CaMeL. A database row carries the injection. The SQL Agent keeps its plan, and so does the Orchestrator. The Orchestrator then writes a summary of the row into the f-string it passes to the Notification Agent as its instruction ([Section III-A](https://arxiv.org/abs/2610.05640v1)):

```python
f"Send this summary to Julie via Slack: {summarised_info}."
```

The paper explains why this works: "Because the Notification Agent treats this argument as its user instruction, the previously untrusted value is exposed to its PLLM as trusted input." The child's planner adds a `send_email` exfiltration step. In the paper's words, "although every constituent agent individually satisfies CFI, the system as a whole does not" ([arXiv:2610.05640v1](https://arxiv.org/abs/2610.05640v1)).

A proof sketch generalizes this. Under an expressivity assumption (any tool can be invoked, and any tool's output can feed a later call), a non-trivial system with one untrusted-return tool violates system-level control-flow integrity ([Section III-C](https://arxiv.org/abs/2610.05640v1)).

Per-agent CaMeL still stops attacks that need to hijack one specific agent. The OMNI-Leak attack, which needs the SQL agent itself to add a private-database call, scored 0% attack success, over 5 trials on one model ([Section III-B](https://arxiv.org/abs/2610.05640v1)). Every successful attack against individual-agent CaMeL in the benchmark was boundary laundering ([Section V-C1](https://arxiv.org/abs/2610.05640v1)).

## The channel split

Multi-CaMeL splits an agent-as-tool call into two arguments ([Section IV-A](https://arxiv.org/abs/2610.05640v1)):

- `message: str`, the trusted instruction shown to the child's planner.
- `variables: dict[str, Any]`, "a dictionary of opaque values that is passed to A_{j} without being directly exposed to its PLLM".

The split alone does nothing, and the paper says so: "this separation only provides the desired security guarantee if it is enforced at runtime." The interpreter enforces two rules ([Section IV-B](https://arxiv.org/abs/2610.05640v1)):

- Instruction-channel integrity: "The message argument of an agent-as-tool call must not depend on any tool output."
- Cross-agent provenance preservation: values passed in `variables` keep their capabilities and provenance across the boundary.

The authors state the general principle in one line: "crossing an agent boundary should not implicitly upgrade the trust status of information" ([Section VII](https://arxiv.org/abs/2610.05640v1)).

## Why it works

A CaMeL agent fixes its control flow from what its planner sees, and the planner sees only trusted input. In an agent-as-tool call the child treats the parent as its user, so any string the parent passes becomes the child's trusted input. If the string embeds a tool-derived value, untrusted data reaches a planner as instruction ([arXiv:2610.05640v1](https://arxiv.org/abs/2610.05640v1)). Multi-CaMeL breaks that path with dependency tracking in the interpreter. Each child's plan then depends only on trusted input, and expanding each plan recursively gives a system-level plan fixed by the original user instruction ([Section IV-C](https://arxiv.org/abs/2610.05640v1)). Model compliance plays no part in the guarantee.

## Measured results

The authors evaluated five models on MultiAgentDojo, their own multi-agent extension of AgentDojo, with 949 injected task instances per model and configuration. Mean attack success was 12.9% with no CaMeL, 0.2% with per-agent CaMeL, and 0.0% with multi-CaMeL ([Table III](https://arxiv.org/abs/2610.05640v1)). GPT-4.1 and Gemini 2.5 Pro still showed attacks at 0.5% and 0.4% under the split.

Treat these as a ceiling. The gain over per-agent CaMeL is 0.2 points on a fixed benchmark the authors built. The Table III caption warns that a 0% result "may reflect the attacks represented in the benchmark rather than immunity to stronger adaptive attacks" ([arXiv:2610.05640v1](https://arxiv.org/abs/2610.05640v1)).

Utility on AssetOpsBench (112 tasks) fell by 21.6 points on average under individual CaMeL. Multi-CaMeL added 3.2 points on average, and 0.85 points across the two strongest models, with confidence intervals that overlap for every model ([Section V-A2](https://arxiv.org/abs/2610.05640v1)). Most of the cost comes from CaMeL itself, not from the channel split.

## What to do without an enforcing runtime

No source documents an enforcing runtime in Claude Code, Copilot, or Cursor subagents, so the options are weaker. They lower exposure and promise nothing.

- Keep tool-derived text out of the delegation message. Pass a file path or ID and let the child read it.
- Strip egress and send tools from any child that handles untrusted content. Capability limits hold whatever text reaches the child's planner. The [per-agent capability store](per-agent-capability-scoping.md) is one way to apply them.
- Gate side effects behind [human confirmation](human-in-the-loop-confirmation-gates.md).

A path or ID still puts the injected text in the child's context through its own tool call. That gives no control-flow guarantee. The text arrives as a tool result instead of a user-turn instruction.

## When this backfires

- The child is a standard single-model agent. Fetching the value separately moves the text from the brief to a tool result, and the same model reads it in the same window.
- A prompt enforces the split ("pass tool-derived values via variables"). The paper puts the guarantee in the interpreter. A parent that interpolates anyway reopens the hole with no signal.
- The child must decide its next action from the data, such as "triage these emails and act on each one". A plan fixed before the data is seen cannot express that. Most utility failures come from "committing to a control-flow plan before observing runtime data" ([Section V-C2](https://arxiv.org/abs/2610.05640v1)).
- The sub-agent returns data for a nearby scope and the parent proceeds. The paper calls this unchecked scope substitution, since the parent's program was written before the response arrived.
- The topology is not a tree, or children keep state across calls. The protocol is unproven there.
- The attacker only needs a branch the plan already has. The paper concedes that "untrusted data can steer execution among existing branches, but cannot introduce new control-flow paths", which it calls branch steering ([Section IV-C](https://arxiv.org/abs/2610.05640v1)). The interpreter also misses some implicit dependencies ([Section VI-B1](https://arxiv.org/abs/2610.05640v1)). The base model does not block side channels such as timing or error behavior ([Operationalizing CaMeL, arXiv:2505.22852v1](https://arxiv.org/abs/2505.22852v1)).
- Tools lack documented return schemas. The planner must write parsing code before it sees the data, so the paper added full return schemas to every tool description.
- You deploy with policies. The multi-CaMeL evaluation ran with no security policies, so its utility figures are a best case. The LLMbda Calculus paper reports that enabling CaMeL's policy checks halves its utility ([arXiv:2602.20064v2](https://arxiv.org/abs/2602.20064v2)).

## Key Takeaways

- Audit every place a parent writes tool output into a sub-agent's brief. That string is the child's instruction channel.
- The `message` and `variables` split protects only when an interpreter rejects briefs that depend on tool output. A prompt that asks for the split is not enforcement.
- Without that runtime, pass references instead of pasted text and limit what the child can send, because the child will still read the content.
- Report the numbers with their limits: 0.0% mean attack success on a fixed benchmark, 3.2 points of extra utility cost, trees only.

## Related

- [Control/Data-Flow Separation for Prompt Injection Defense (CaMeL)](camel-control-data-flow-injection.md) — the single-agent defense this page extends across agent boundaries
- [Framing Subagent Returns So They Cannot Act as Instructions](subagent-return-framing.md) — the upward direction, child to parent
- [Per-Agent Capability Stores Beat One Task-Wide Allowlist](per-agent-capability-scoping.md) — capability limits that hold whatever reaches the child
- [Authority Confusion: Untrusted Context Must Not Authorize Side Effects](authority-confusion-untrusted-context.md) — untrusted text read as instruction
- [Action-Selector Pattern: LLM as Intent Decoder with Deterministic Execution](action-selector-pattern.md) — another design that limits what untrusted data can influence
