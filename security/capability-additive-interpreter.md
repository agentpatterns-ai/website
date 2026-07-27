---
title: "Capability-Additive Code Interpreters for Untrusted Agent Code"
term: "Capability-Additive Code Interpreter"
description: "Run agent-written orchestration code in an in-process interpreter that starts with zero authority and bridges in each capability deliberately, so the blast radius is what you added, not what you forgot to remove."
aliases:
  - additive-capability interpreter
  - code interpreter as agent sandbox
  - in-process capability interpreter
tags:
  - security
  - agent-design
  - tool-agnostic
last_reviewed: 2026-07-01
maturity: emerging
---

# Capability-Additive Code Interpreters for Untrusted Agent Code

> Start the interpreter with zero ambient authority and bridge in each capability deliberately, so untrusted orchestration code is contained by construction, not by clawback.

Agents increasingly write and run code to orchestrate work — dispatching subagents in a loop instead of one tool call at a time ([Lovell, LangChain, 2026](https://www.langchain.com/blog/running-untrusted-agent-code-without-a-sandbox)). Because prompt injection is unsolved, that agent-written code must be treated as untrusted. A capability-additive interpreter constrains it without a full computer-shaped sandbox: the runtime starts with nothing, and every powerful action is bridged in through the harness with explicit limits. The pattern meets three requirements — execution isolation, capability isolation, and durable pauses.

## The additive model inverts sandbox security

A traditional sandbox starts computer-shaped — a filesystem, dependencies, a shell — so its security work is subtractive: you begin with broad capability and claw it back. A code interpreter starts with nothing. "Out of the box it can't read a file, make a network request, or install a dependency. All it has is the language... Everything more powerful is bridged in deliberately through the harness" ([LangChain, 2026](https://www.langchain.com/blog/running-untrusted-agent-code-without-a-sandbox)).

The two directions fail differently. Subtractive hardening fails open on the one capability you forgot to remove. Additive capability fails closed — the interpreter cannot reach anything you did not hand it. This is the same grant-not-clawback contrast that separates broad-then-narrow permissions from [least-privilege blast-radius containment](blast-radius-containment.md).

## Execution isolation without leaving the process

The interpreter still needs a hard boundary against the host. WebAssembly supplies it in-process: agent code runs in a sandboxed VM with its own linear memory, so it "can't dereference pointers into the host process, so it can't read or corrupt memory it wasn't handed" ([LangChain, 2026](https://www.langchain.com/blog/running-untrusted-agent-code-without-a-sandbox)). LangChain runs QuickJS — a small C JavaScript engine — compiled to WASM, keeping the trusted surface inside the boundary small. The same isolation model backs untrusted-code platforms at AWS, Shopify, and Figma ([LangChain, 2026](https://www.langchain.com/blog/running-untrusted-agent-code-without-a-sandbox)).

The WASM substrate — fuel or epoch CPU bounds, memory caps, deny-by-default I/O, explicit host imports — is covered in [in-process WebAssembly sandboxes for agent-generated code](wasm-sandbox-agent-code-execution.md). This page is the design philosophy that sits on top of that substrate.

## Bridged capabilities carry explicit limits

Because the harness owns each bridge, it also owns the limits. The clearest example is calling subagents from interpreter code: instead of a process manager, the agent gets a function with a narrow contract, and "because we own that bridge, we also set its limits: how many subagents can run at once, and how many a single call can spawn" ([LangChain, 2026](https://www.langchain.com/blog/running-untrusted-agent-code-without-a-sandbox)).

Which bridges are safe to combine follows Meta's Agents Rule of Two: until prompt injection is reliably detected, an agent should satisfy no more than two of process untrusted input, access sensitive data, or change state and communicate externally ([Meta, 2025](https://ai.meta.com/blog/practical-ai-agent-security/)). The additive model makes the rule enforceable — each capability is a deliberate grant you can count — but it does not enforce the rule for you. Materializing each grant as a revocable, subgoal-scoped handle is the stricter version of the same discipline ([PORTICO](revocable-resource-effect-capabilities.md)).

## Durable pauses

A production agent must stop and wait for a human before a risky action, and that approval can return hours or days later, after the agent has left the process. Because QuickJS runs inside WASM, the harness pauses the program itself: it serializes the interpreter's linear memory to durable state, and on resume restores the snapshot and feeds the result back into the call that was waiting. "The program sees only an async call that took a while to return" ([LangChain, 2026](https://www.langchain.com/blog/running-untrusted-agent-code-without-a-sandbox)). This turns [human-in-the-loop approval](human-in-the-loop-confirmation-gates.md) into a first-class control rather than a blocking hack.

## Why it works

The pattern is contained by two structural properties, not by trusting the model. WASM's separate linear memory plus load-time verification means guest code cannot reach host memory regardless of what it does — execution isolation holds structurally ([LangChain, 2026](https://www.langchain.com/blog/running-untrusted-agent-code-without-a-sandbox)). And because the interpreter starts with zero ambient authority, every capability passes through a harness-owned bridge where the limit is set, so the blast radius is bounded by construction. Neither property depends on the model behaving.

## When this backfires

The interpreter is a lighter alternative for orchestration code, not a universal replacement for a sandbox.

- Hostile multi-tenant on shared hardware. Because the interpreter is in-process, a WASM-runtime or JIT-compiler bug becomes a same-host escape into the harness that holds your credentials ([WASM sandbox-escape CVE-2023-6699](https://www.ameeba.com/blog/cve-2023-6699-sandbox-escape-vulnerability-in-webassembly-wasm-in-v8-javascript-engine/)). Hostile tenants need a full remote container or microVM, which [workload-keyed sandbox selection](workload-keyed-sandbox-selection.md) routes to.
- General code execution, not orchestration. Work that needs a real filesystem, dependency installs, a shell, or the full standard library does not fit a runtime that starts with nothing.
- A careless bridge re-opens the trifecta. One bridge that grants sensitive-data read and external write while untrusted content is in context violates the Rule of Two through the additive model, not despite it ([Meta, 2025](https://ai.meta.com/blog/practical-ai-agent-security/)).
- Language mismatch. The interpreter runs JavaScript through QuickJS; orchestration that must be Python with CPython semantics does not get it inside the boundary.
- Immature runtime. LangChain's `quickjs-rs` and `langchain-quickjs` are self-described experimental ([LangChain, 2026](https://www.langchain.com/blog/running-untrusted-agent-code-without-a-sandbox)); load-bearing use means auditing the bridge surface, or waiting for a hardened implementation.

## Example

A Deep Agents workflow lets the model write a short JavaScript program that fans out subagents, rather than issuing one dispatch tool call at a time ([LangChain, 2026](https://www.langchain.com/blog/introducing-dynamic-subagents-in-deep-agents)). The program runs in an interpreter with zero ambient authority — no filesystem, no network — and the only bridge it can reach is a `spawnSubagent` function. The harness caps that bridge: a bound on concurrent subagents and a bound on how many any single call can spawn.

An injected instruction that tells the code to read `~/.ssh/id_rsa` or POST to an attacker host finds no filesystem and no network bridge to call — the capability was never added. If the program pauses for a human to approve a spend, the harness snapshots the interpreter's linear memory and resumes it when approval returns, even a day later.

## Key Takeaways

- A capability-additive interpreter starts with zero authority and bridges in each action deliberately, so the blast radius is what you added, not what you forgot to remove.
- It inverts the subtractive sandbox: additive capability fails closed, subtractive hardening fails open on the forgotten permission.
- WebAssembly supplies execution isolation in-process — separate linear memory means guest code cannot reach host memory — with QuickJS as the small engine inside the boundary.
- Harness-owned bridges carry explicit limits, such as caps on concurrent subagents; Meta's Rule of Two decides which bridges are safe to combine.
- Durable pauses come free from running QuickJS in WASM: serialize the linear memory, resume the paused call after human approval.
- It is a lighter alternative for orchestration code, not a replacement — hostile-tenant, general-code, or Python-semantics workloads still need a full remote sandbox.

## Related

- [In-Process WebAssembly Sandboxes for Agent-Generated Code](wasm-sandbox-agent-code-execution.md) — the WASM substrate mechanics (fuel, memory caps, WASI) this design sits on top of
- [Workload-Keyed Sandbox Selection for Agent-Generated Code](workload-keyed-sandbox-selection.md) — when to route to a full remote container instead of an in-process interpreter
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md) — the same grant-not-clawback discipline at the permission layer
- [Revocable Resource-and-Effect Capabilities for Coding Agents (PORTICO)](revocable-resource-effect-capabilities.md) — the stricter form: each bridged capability as a revocable subgoal-scoped handle
- [Selective Network Access in Agent Sandboxes: The `allowNetwork` Pattern](selective-network-sandbox-mode.md) — the subtractive counterpart, where a boundary is lifted rather than added
- [Human-in-the-Loop Confirmation Gates for Consequential Agent Actions](human-in-the-loop-confirmation-gates.md) — the approval step durable pauses make first-class
