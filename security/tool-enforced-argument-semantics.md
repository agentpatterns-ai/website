---
title: "Enforce a Tool's Documented Argument Limits in the Tool"
term: "Tool-Enforced Argument Semantics"
description: "The orchestrator checks a tool call's shape, never its meaning, so a documented argument limit stays unenforced until the tool's own code checks it."
tags:
  - security
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - tool-enforced argument semantics
  - semantic security bug
  - schema-valid arguments are untrusted
last_reviewed: 2026-10-13
maturity: emerging
status: current
---

# Enforce a Tool's Documented Argument Limits in the Tool

> A tool call that satisfies the schema can still break what the tool's description promised, and the schema is all the orchestrator checked.

Tool-enforced argument semantics means checking, inside a tool's own code, every security property the tool's documentation implies about its arguments. That property is normally absent from the schema: a string described as a path inside the workspace implies containment that `"type": "string"` cannot express. A call that breaks such a property while passing the schema is a semantic security bug, one of the "executions that satisfy a tool's syntactic interface but violate a security property implied by its documented semantics" ([ToFu, arXiv:2610.13651v1](https://arxiv.org/abs/2610.13651v1)).

## Two conditions before this applies to you

The first is write access. You can act on this where you author, vendor, or fork the tool. A team that installs a third-party MCP server cannot add a containment check to somebody else's `read_file`, and its remaining controls sit at the boundary: narrowing what the agent may reach, gating calls before dispatch, sandboxing execution. For that team the useful half of this page is its premise. Assume no tool enforces its own description.

The second is observability at the tool boundary. A single call has to be able to show the violation. Roughly a fifth of the servers that only static baselines caught had properties no runtime event exposes. The authors list these as permissive CORS configurations, incorrect sanitizing regular expressions, and filesystem races, and call "better suited to static analysis than single-input fuzzing" ([ToFu, arXiv:2610.13651v1](https://arxiv.org/abs/2610.13651v1)).

## What the orchestrator establishes

An orchestration layer renders tool metadata for the model, parses the reply into a structured call, and dispatches it. Structure is the whole of what it establishes, so "Conformity to a tool-call schema therefore does not establish the trustworthiness of the resulting request" ([ToFu, arXiv:2610.13651v1](https://arxiv.org/abs/2610.13651v1)). The researchers show this with an attack they call Repeat-After-Me, where text shaped like the orchestrator's own tool-call format is reproduced by the model and then parsed as a genuine call. They report the behavior on six orchestration layers (LangGraph, MAF, ADK 2.0, AutoGen, Strands, CrewAI). One transcript is published, on LangGraph 1.2.0 driving llama3.1:8b through Ollama at temperature 0 against two stub tools with a refuse-anything-dangerous system prompt. The call executes on a turn whose visible message is empty, and the refusal text arrives only after the tool has returned ([ToFu, arXiv:2610.13651v1](https://arxiv.org/abs/2610.13651v1)).

## Why it works

The tool is the only component holding both halves of the contract. The orchestrator holds the schema and the description but not the sink. The model holds neither. Inside the tool, the promise about an argument and the operation that could break it run in the same process, with nothing left to defer to: on LangGraph's prebuilt tool node, "nothing between the model's output and the tool checks whether the call should run" ([ToFu, arXiv:2610.13651v1](https://arxiv.org/abs/2610.13651v1)). Enforcement anywhere else has to reconstruct what the orchestrator already discarded.

The contract is also mechanical enough to derive automatically: the descriptions already written for the model let checks and oracles "be specialized to individual tool arguments" ([ToFu, arXiv:2610.13651v1](https://arxiv.org/abs/2610.13651v1)).

## What the measurement covers

The evidence is one fuzzing campaign over open-source Python and JavaScript MCP servers from the MCPCorpus dataset. The denominator is 273 servers in which at least one tool returned success on an adversarial input. The result is 253 reproducible bugs in 118 of them. Manual review had removed 103 candidates as not vulnerable and 152 as duplicates. Read 118 of 273 as a rate over servers a fuzzer could run, not over the ecosystem: the authors prepared 482 and lost the difference to servers that "require external credentials or backends, or crash on startup". Those 273 servers held 3405 extracted tools, and "only a subset of these tools could be successfully exercised during analysis" ([ToFu, arXiv:2610.13651v1](https://arxiv.org/abs/2610.13651v1)).

Three classes carry 237 of the 253: 115 reflected output, 64 path traversal, 58 log injection. The rest are 7 SSRF, 5 data exfiltration, 3 OS command injection, and 1 leftover temporary file. None of it needed a crash to find, and among the 508 candidates before review, 182 were cases where "the input violated a semantic security constraint yet the tool reported successful execution" ([ToFu, arXiv:2610.13651v1](https://arxiv.org/abs/2610.13651v1)). Alongside the missing enforcement the authors name a second habit, the one to check your own code for: "many tools implicitly rely on the LLM to sanitize inputs" ([ToFu, arXiv:2610.13651v1](https://arxiv.org/abs/2610.13651v1)).

## When this backfires

Validating without specializing buys a triage queue. Turning on all 74 of the framework's checks for every tool produced 960 reports of which 47 were real, 4.9%, and on the tools only that configuration flagged, "over 90% of the reports are false" ([ToFu, arXiv:2610.13651v1](https://arxiv.org/abs/2610.13651v1)). A generic input filter stapled across every argument is not the cheap version of this.

Verification is where the cost lands, and it is human work. Clearing a candidate meant reading the server to find its intent, because a script runner that runs a script is behaving correctly ([ToFu, arXiv:2610.13651v1](https://arxiv.org/abs/2610.13651v1)).

Static baselines flag a similar number of servers. A plain Claude Sonnet 5 code audit flagged 119 of the 273 servers against ToFu's 118, and CodeQL flagged 95. The authors say "no baseline is directly comparable with ToFu's semantic bug detection goal" and "A larger static count therefore does not indicate an input-reachable bug that ToFu missed; it measures code hygiene or capability, which runtime fuzzing does not target" ([ToFu, arXiv:2610.13651v1](https://arxiv.org/abs/2610.13651v1)). The paper does not report verifying the baseline flags, and they overlap ToFu on 71 and 56 servers. Static passes find properties a single call cannot show, so they do not replace semantic checking, and the reverse holds too.

The study measures missing enforcement, not the value of adding it. Its four research questions cover sanitizer applicability, bug detection, fuzzing effectiveness, and a component ablation, so this recommendation rests on the mechanism and the prevalence, not on a measured reduction in harm ([ToFu, arXiv:2610.13651v1](https://arxiv.org/abs/2610.13651v1)).

## Example

The authors report four servers that affected their own evaluation host while being fuzzed. One deleted files outside its workspace, one followed a fuzzed path outside its vault, one terminated terminal sessions it did not own, and one spawned processes without limit ([ToFu, arXiv:2610.13651v1](https://arxiv.org/abs/2610.13651v1)). They present these as the reason to run a tool fuzzer in a sandbox, and that is the first thing to take from them. The second is the shape of each limit: a workspace, a vault, a session you own, a process count.

Each of those limits wants its own check, and none of them is a type. Two are path containment against different roots, so resolve the path and compare it to the root the description names. One is ownership, so match the session identifier against the ones this caller holds. One is a budget, so count the children already spawned. A JSON schema expresses none of that, which is the paper's point that "there is no universal sanitizer even for inputs sharing the same primitive type" ([ToFu, arXiv:2610.13651v1](https://arxiv.org/abs/2610.13651v1)).

## Key Takeaways

- Treat your tool's description as the specification you owe the caller. Anything it promises about an argument needs a line of code behind it, because nothing upstream will supply one.
- Derive the check from what the argument means, not from its type. Two string arguments can need a containment test and a destination allowlist respectively, and no single sanitizer covers both.
- Keep static review alongside this. Non-executing reviews flagged similar numbers of servers, a count the paper says measures code hygiene or capability, and they catch the properties a single call cannot show.
- Budget for triage, not only for the checks. The all-checks configuration ran at the same throughput and returned mostly false reports, so the expensive part is deciding which findings are real.
- If you cannot change the tool, invert the lesson. Assume the tool enforces nothing it documents, and put the containment somewhere you do control.

## Related

- [Security-Aware Tool Descriptions for MCP Servers (SpellSmith)](security-aware-tool-descriptions-mcp.md) — the description-side stopgap for a risky tool, which positions itself as a layer over code-level validation rather than a replacement
- [Closed-World Tool Call Resolution Before the Permission Gate](closed-world-tool-call-resolution.md) — the rung before this one, where a call is matched to a real tool at all
- [Hybrid Deterministic + Semantic Authorization for Agent Tool Calls](hybrid-deterministic-semantic-tool-authorization.md) — what to build at the boundary when the tool implementation is somebody else's
- [Improper Output Handling: Validate Agent Output Before Downstream Use](improper-output-handling-downstream-sinks.md) — the same untrusted-input discipline applied on the return path
- [Execution-Layer Security Invariants for MCP Runtimes](mcp-execution-security-invariants.md) — named runtime invariants for the MCP execution path these checks sit inside
- [Tool-Invocation Attack Surface](tool-invocation-attack-surface.md) — the attacker's side of the same boundary, where a malicious tool steers argument generation rather than an honest tool failing to check it
