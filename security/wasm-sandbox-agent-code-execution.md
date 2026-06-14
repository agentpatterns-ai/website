---
title: "In-Process WebAssembly Sandboxes for Agent-Generated Code"
term: "In-Process WebAssembly Sandboxes"
description: "Embed a WebAssembly runtime inside your Python or JavaScript application to execute agent- or LLM-generated code with CPU and memory caps, no filesystem or network by default, and explicit host-function interop."
tags:
  - security
  - tool-agnostic
aliases:
  - WASM sandbox for agent code
  - WebAssembly code execution sandbox
last_reviewed: 2026-06-08
maturity: established
---

# In-Process WebAssembly Sandboxes for Agent-Generated Code

> Run untrusted agent-generated code inside a WebAssembly runtime embedded in the host process — deny-by-default I/O, fuel-bounded CPU, capped memory, host-function interop.

## When This Pattern Fits

WebAssembly fills the **in-process** slot in the sandbox-runtime trade-space ([containers vs microVMs vs OS-level isolators](sandbox-runtime-comparison.md)): no container daemon, no hypervisor, no separate process — the sandbox is a library the host application instantiates. It applies when a Python or JavaScript application needs to execute agent- or LLM-generated code without a container runtime, on targets that cannot or should not run Docker / a hypervisor (developer laptops, edge nodes, hosted SaaS workers), and where the threat model is "buggy or compromised guest code", not a hostile tenant with hardware access (see *When This Backfires*).

The substrate works because WebAssembly was designed for executing untrusted code: bytecode has no syscalls, all I/O is routed through host-supplied imports, and the type system is verified at load time. The runtime ships as a maintained PyPI package ([wasmtime](https://pypi.org/project/wasmtime)) with binary wheels — no toolchain build required.

## The Four Controls

A usable WASM sandbox composes four runtime-enforced controls. The names below match the [wasmtime](https://docs.wasmtime.dev/) API; engines like wasmer expose the same shapes.

### CPU Bound — Fuel or Epochs

Wasmtime offers two interruption mechanisms ([Interrupting Wasm Execution](https://docs.wasmtime.dev/examples-interrupting-wasm.html)):

- **Fuel** — `config.consume_fuel(true)` plus `store.set_fuel(N)`. Each instruction consumes fuel; exhaustion raises `Trap::OutOfFuel`. **Deterministic** — same program with same fuel traps at the same instruction. Trade-off: higher per-instruction overhead than epochs, and fuel units do not translate cleanly to wall-clock time ([Simon Willison's notes](https://simonwillison.net/2026/Jun/6/micropython-in-a-sandbox/): "the units are hard to reason about").
- **Epochs** — `config.epoch_interruption(true)` plus a host-side timer that increments the epoch. Around 10% guest slowdown per the docs. **Non-deterministic** — wall-time based; the same input may trap at different points across runs.

Fuel for reproducibility (eval suites, replays); epochs for production wall-clock budgets.

### Memory Cap

Wasmtime exposes per-store memory limits as a first-class option. Without an explicit cap a loop like `s = ""; while True: s += "longer"` exhausts host memory; with a cap, the guest traps inside the runtime ([reproduced in Willison's CLI demo](https://simonwillison.net/2026/Jun/6/micropython-in-a-sandbox/#try-it-yourself)).

### Filesystem and Network — Deny by Default

WebAssembly has no ambient I/O. WASI capabilities (file descriptors, network sockets) must be explicitly handed to the instance at construction. The default posture is **no filesystem and no network** — a stronger default than [dual-boundary sandboxing](dual-boundary-sandboxing.md), where both boundaries must be configured to be enforced.

### Host-Function Interop

The escape hatch is explicit host imports. Each function the guest can call is registered on the embedder side; everything else is unreachable. Per the [Wasmtime security contract](https://docs.wasmtime.dev/security-what-is-considered-a-security-vulnerability.html): "Use of a WASI resource without having been given the associated WASI capability" is a security vulnerability — the embedder, not the guest, decides what gets exposed.

## Persistent Interpreter State

A naive WASM-Python embedding starts a fresh interpreter per call, losing variables and imports. The persistent-session technique runs the guest interpreter in a host thread that blocks on a `__session_next__()` host function, feeds successive code blocks through `eval()`, and returns results via `__session_result__()`. Variables stay resident across calls without restarting the WASM module ([implementation walkthrough](https://simonwillison.net/2026/Jun/6/micropython-in-a-sandbox/#building-the-first-version)). The same shape applies to QuickJS-in-WASM where a code-execution tool wants REPL-like persistence inside an isolated session.

## Why It Works

WebAssembly was designed as an abstract machine for untrusted code: no syscalls in the bytecode, I/O routed through host-supplied imports, and a verified-at-load-time type system that prevents memory corruption inside the guest. Per the [Wasmtime security policy](https://docs.wasmtime.dev/security-what-is-considered-a-security-vulnerability.html): "Anything that undermines the Wasm execution sandbox is a security vulnerability" — including denial-of-service via uninterruptible loops and user-controlled memory exhaustion. That contract makes the runtime owners, not the embedding application, responsible for closing escape and exhaustion paths.

The substrate beats V8-in-Python alternatives because browser JS engines, while battle-tested, are not designed for easy embedding; most V8-in-Python projects "are infrequently maintained and come with warnings not to use them with completely untrusted code" ([Willison, 2026](https://simonwillison.net/2026/Jun/6/micropython-in-a-sandbox/)).

## When This Backfires

- **Hostile-multi-tenant production on shared hardware.** A wasmtime CVE in the VMM, compiler backend, or WASI layer becomes a same-host escape across tenants. [GHSA-2r75-cxrj-cmph](https://github.com/bytecodealliance/wasmtime/security/advisories) (May 2026) — a WASI `path_open(TRUNCATE)` bypass of `FilePerms::WRITE` — is the reminder. Hostile-tenant workloads warrant a hypervisor boundary (Firecracker microVMs) rather than in-process isolation.
- **Workloads needing the full CPython ecosystem.** MicroPython runs a small subset of the standard library. Pyodide handles more of CPython but is documented as "browser or Node.js" only on the server side ([Pyodide guidance, Oct 2024](https://github.com/pyodide/pyodide/discussions/5145)); server-side embedders cannot use it today.
- **Alpha reference implementations.** The motivating package — [micropython-wasm](https://github.com/simonw/micropython-wasm) — is self-described as alpha and "vibe-coded"; the author "deliberately slapped an alpha release version on it" and is "not ready to recommend it to anyone who isn't willing to take a significant risk." Adopt the **pattern**, not this specific package, for anything load-bearing. Wait for an audited implementation or accept the maturity risk explicitly.
- **Wall-clock CPU budgets without measurement.** Fuel is deterministic per program but not per wall-time. Teams needing wall-clock bounds layer epoch interruption on top of fuel, or run calibration sweeps before fixing a budget.
- **Agents reasoning around the substrate.** No runtime stops a capable agent from finding alternative execution paths through host functions you expose ([the sandbox illusion](https://www.manifold.security/blog/the-sandboxing-illusion-how-to-isolate-agents)). Audit the host-function surface as carefully as the sandbox itself.

## Example

A Python application embeds MicroPython-in-WASM via [`micropython-wasm`](https://github.com/simonw/micropython-wasm) (alpha — illustrative of the API shape, not a production recommendation):

```python
from micropython_wasm import MicroPythonSession

with MicroPythonSession() as session:
    print(session.run("x = 10\nprint(x)").stdout)
    print(session.run("x += 5\nprint(x)").stdout)
    print(session.run("print(x * 2)").stdout)
```

Each `session.run()` executes inside the WASM sandbox; variables persist across calls via the host-function session protocol. A runaway loop traps out instead of hanging the host:

```
$ uvx micropython-wasm -c 's = ""; while True: s += "longer"'
micropython-wasm: guest exited with code 1
```

The host sees a clean error; the host process is unaffected. The same pattern applies to a JavaScript-guest sandbox (QuickJS-in-WASM) embedded in a Node.js agent harness.

## Key Takeaways

- WASM is the in-process substrate slot in the sandbox-runtime trade-space — distinct from containers, microVMs, and OS-level isolators
- Four runtime-enforced controls compose the sandbox: CPU (fuel or epochs), memory cap, deny-by-default WASI, explicit host imports
- Fuel is deterministic but not wall-clock; epochs are wall-clock but non-deterministic — pick per workload, or layer them
- Persistent interpreter state across calls is a host-function-mediated session pattern, not a WASM-level feature
- Not a fit for hostile-multi-tenant workloads on shared hardware — hypervisor isolation (microVMs) remains the right floor there
- Reference implementations in 2026 are alpha; adopt the pattern, audit the host-function surface, and watch for a production-grade embedder before staking high-stakes workloads on it

## Related

- [Sandboxed Coding Environments: Containers vs MicroVMs vs OS-Level Isolators](sandbox-runtime-comparison.md)
- [Dual-Boundary Sandboxing](dual-boundary-sandboxing.md)
- [Docker sbx Adoption for Coding Agents](docker-sbx-adoption.md)
- [Subprocess PID Namespace Sandboxing in Claude Code](subprocess-pid-namespace-sandboxing.md)
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md)
