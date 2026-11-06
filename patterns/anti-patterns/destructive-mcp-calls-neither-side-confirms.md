---
title: "Destructive MCP Tool Calls Where Neither Side Confirms"
term: "Neither-Side-Confirms Gap"
description: "Most MCP server and host defaults leave destructive-call confirmation to the other side. In sampled destructive tool and open-source app pairs, 60.7% run without human approval by default."
tags:
  - anti-pattern
  - security
  - tool-agnostic
  - arxiv
  - mcp
aliases:
  - MCP destructive tool approval gap
  - split confirmation in MCP
  - fail-open MCP elicitation
last_reviewed: 2026-11-05
maturity: emerging
status: current
---

# Destructive MCP Tool Calls Where Neither Side Confirms

> Under default settings, 60.7% of sampled destructive MCP tool and open-source app pairs run without human approval.

The anti-pattern is assuming that the other end of an MCP connection asks a human before a destructive call. The specification says there "SHOULD always be a human in the loop with the ability to deny tool invocations" but leaves the mechanism to applications ([MCP specification, Tools](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)). A server can annotate a tool or ask through elicitation, and the host decides whether to prompt. Measured from source code, "60.7% of pairs have no enforced human approval by default" across sampled destructive tools and 25 open-source applications ([arXiv:2611.02527v1](https://arxiv.org/abs/2611.02527v1)).

## When the gap applies

The figures describe default code paths, not your deployment. The authors list the exits: "operators can enable confirmation, users can choose “always allow”" ([arXiv:2611.02527v1](https://arxiv.org/abs/2611.02527v1)). Three settings put you inside the measured case:

- You build an agent on an SDK and add MCP servers without an approval option. The paper reports that "every SDK we examined ships with approval off" ([arXiv:2611.02527v1](https://arxiv.org/abs/2611.02527v1)).
- You run a server whose destructive tools rely on an annotation, a confirm flag, or elicitation that falls back when the host cannot ask.
- Your host is open source. Adding seven closed-source applications, Claude Code and Cursor among them, "lowers the applications share to 47.5%" ([arXiv:2611.02527v1](https://arxiv.org/abs/2611.02527v1)).

## What each side does by default

On the server side, "an estimated 90% of destructive tools (95% CI 82–95) have no server-side confirmation" in a 1,000-repository sample of the official registry. Most servers that do elicit still run without a human: "Of these 168, 130 still run when the host cannot relay the question", 100 of them by falling back to a flag the model can set ([arXiv:2611.02527v1](https://arxiv.org/abs/2611.02527v1)).

On the host side, "Of 41 popular open-source hosts and agent SDKs, 32 have no approval step by default". The annotation rarely matters: for 39 of the 41 hosts, "a destructive hint changed nothing on the coded path" ([arXiv:2611.02527v1](https://arxiv.org/abs/2611.02527v1)).

The live runs show what this costs under injection. A read-only tool returned a planted instruction to delete a second note, and "four of five low-cost models executed an injected deletion in 479 of 960 runs". On the flag server, "models set confirm=true themselves even when the injected text did not name it" ([arXiv:2611.02527v1](https://arxiv.org/abs/2611.02527v1)).

## Why it works (each side assumes the other)

"Most defaults on each side leave confirmation to the other." Some server authors who fail open say they expect hosts to gate destructive calls, and SDKs leave approval to application authors by design ([arXiv:2611.02527v1](https://arxiv.org/abs/2611.02527v1)). The server cannot fix this alone, because "The server cannot see whether the host prompted". A model-settable flag does not close the gap either. The threat model is a model that may be injected or misread the task, so "a flag the model sets itself does not count" as confirmation ([arXiv:2611.02527v1](https://arxiv.org/abs/2611.02527v1)).

## What to put in its place

Put the approval in the host or the application you control. The paper's counterfactual puts the fix there: if hosts "prompted for every tool not annotated read-only or non-destructive, the unapproved share of these pairs would fall to 5.4%; universal elicitation support would leave 56.7%" ([arXiv:2611.02527v1](https://arxiv.org/abs/2611.02527v1)).

- Prompt unless the tool is annotated safe. Treat annotations as hints from a server you trust, since clients "MUST consider tool annotations to be untrusted unless they come from trusted servers" ([MCP specification, Tools](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)).
- Skip only read-only tools if you distrust non-destructive annotations. Read-only annotations must still come from a trusted server. That stricter rule "also catches tools that wrongly declare destructiveHint=false, at the cost of more prompts" ([arXiv:2611.02527v1](https://arxiv.org/abs/2611.02527v1)).
- On a server you write, refuse rather than proceed when the host cannot elicit. The authors' alternative is to "return a preview without acting" ([arXiv:2611.02527v1](https://arxiv.org/abs/2611.02527v1)).

## When this backfires

More prompts are a weak human decision. In Claude Code, "in practice users accept 93% of them anyway" ([Anthropic](https://www.anthropic.com/engineering/claude-code-auto-mode)). The paper counts presence only: "We count whether a blocking human decision exists, not whether users read it". For flagged tools adjudicated non-destructive, the host-side rule also raises the share of pairs that prompt, which "would rise from 32.5% to 82.6% for applications" ([arXiv:2611.02527v1](https://arxiv.org/abs/2611.02527v1)).

Three more conditions limit the fix ([arXiv:2611.02527v1](https://arxiv.org/abs/2611.02527v1)):

- A headless run has no one to answer a prompt. Headless Codex CLI refused all three variants of the test tool, which is the safe result and also a stopped pipeline.
- A wrong server annotation defeats the annotation rule. The residual 5.4% are exactly those pairs, and adding tools the extractor missed raises it to at least 10.6% across all hosts.
- Universal server fail-closed costs the opposite way. Across all hosts, 79.4% of pairs would end in a refusal. That includes "14.4% of all pairs in which the host prompts and the user approves, but the server refuses because it cannot see that approval".

The injection evidence is narrow as well: "the injection runs used five low-cost models" ([arXiv:2611.02527v1](https://arxiv.org/abs/2611.02527v1)).

## Example

The OpenAI Agents SDK lets a local MCP server take `require_approval`. A callable form receives "the original MCP SDK `Tool`, including `tool.annotations`" ([OpenAI Agents SDK](https://openai.github.io/openai-agents-python/mcp/)).

**Before — approval left to the server:**

```python
async with MCPServerStdio(
    name="filesystem",
    params={"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "./workspace"]},
) as server:
    ...
```

**After — the application asks for every tool not marked read-only:**

```python
def needs_approval(run_context, agent, tool) -> bool:
    hints = tool.annotations
    return not (hints is not None and hints.readOnlyHint is True)

async with MCPServerStdio(
    name="filesystem",
    params={"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "./workspace"]},
    require_approval=needs_approval,
) as server:
    ...
```

Use this rule only when you trust the server's read-only annotations. The callable decides per tool, not per call. The SDK documents that it "does not receive the specific call's arguments or call ID" ([OpenAI Agents SDK](https://openai.github.io/openai-agents-python/mcp/)).

## Key Takeaways

- Name the component on your call path that blocks a destructive MCP call. If the answer is the other side, nothing blocks it.
- Configure approval through your SDK or host. The paper finds dedicated approval options in seven SDKs, general pre-call hooks in five, and neither in four ([arXiv:2611.02527v1](https://arxiv.org/abs/2611.02527v1)).
- Read a `confirm` argument as model input. An injected model sets it.
- Weigh the prompt volume. Users accept most prompts, so a prompt on every call buys less review than its count suggests.

## Related

- [Human-in-the-Loop Confirmation Gates for Consequential Agent Actions](../../security/human-in-the-loop-confirmation-gates.md) — the general gate this page shows is missing on most default MCP paths
- [MCP Elicitation: Servers Requesting Structured Input Mid-Task](../../tool-engineering/mcp-elicitation.md) — the server-side request that only reaches a human when the host relays it
- [Judging MCP Capability Readiness by Client Adoption](../../tool-engineering/mcp-capability-readiness.md) — writing the degradation path for clients that lack elicitation
- [Ask-Everything Permission Policies Protect Less than Per-Action Approval](ask-everything-permission-policies.md) — what happens to approval quality when prompts multiply
- [Treating an MCP Tool's Contract as Its Sandbox](mcp-contract-as-filesystem-sandbox.md) — a second MCP control that each side assumes the other enforces
