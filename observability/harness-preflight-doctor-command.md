---
title: "Harness Preflight Doctor Command for Agent Diagnostics"
term: "Harness Preflight Doctor Command"
description: "A doctor command validates an agent harness's runtime environment — auth, MCP, config, tools, version drift — and reports problems before work starts."
tags:
  - observability
  - agent-design
  - tool-agnostic
  - harness-engineering
last_reviewed: 2026-06-02
maturity: established
---

# Harness Preflight Doctor Command for Agent Diagnostics

> A doctor command runs one deterministic preflight pass over a harness's auth, MCP, config, tools, and version drift, reporting broken preconditions before work starts.

Related lesson: [The Four Failure Modes](https://learn.agentpatterns.ai/observability/the-four-failure-modes/) covers this concept in a hands-on lesson with quizzes.

A harness preflight doctor command is a diagnostics subcommand. It validates an agent harness's runtime environment in one deterministic pass. It reports each misconfigured precondition with a clear message before work begins. It mirrors the `brew doctor` and `flutter doctor` pattern: scan the environment, name what is broken, and leave the fix to the operator ([Flutter troubleshoot install](https://docs.flutter.dev/install/troubleshoot)).

## What a doctor command checks

Five environment-validity classes recur across shipping implementations:

| Check class | What it validates | Failure it catches up front |
|---|---|---|
| Auth / login | Credentials present, valid, and scoped for the session | Expired token, wrong account, missing scope |
| MCP / tool reachability | Configured MCP servers resolve and respond; required vs. optional distinguished | Unreachable server, unresolvable stdio command, missing executable permission |
| Config validity | Config file parses and conforms to the expected schema | Malformed config, invalid keys, oversized instruction files |
| Tool availability | Required binaries and toolchains are on PATH | Missing CLI the agent will reach for mid-run |
| Version / update drift | Installed harness version vs. latest; install consistency | Stale binary, mixed install sources, available update |

Codex's `codex doctor` (CLI 0.131.0, 2026-05-18) groups its report into Environment, Configuration, Updates, Connectivity, and Background Server sections, with a Notes block promoting anomalies such as available updates and optional-MCP issues ([Codex changelog](https://developers.openai.com/codex/changelog); [openai/codex PR #22336](https://github.com/openai/codex/pull/22336)). Claude Code's `/doctor` runs "an automated check of your installation, settings, MCP servers, and context usage" in one pass ([Claude Code troubleshooting](https://code.claude.com/docs/en/troubleshooting)).

## Run it before the harness boots

The diagnostics must run even when the harness itself will not start. Claude Code makes this explicit: "If `claude` won't start at all, run `claude doctor` from your shell instead" ([Claude Code troubleshooting](https://code.claude.com/docs/en/troubleshooting)). A diagnostics path that only runs inside a healthy session cannot diagnose the unhealthy ones. So the doctor is a standalone, shell-invocable command. It depends as little as possible on the runtime it inspects.

## Why it works

Preflight diagnostics work because they move failure detection earlier. They replace a confusing failure deep inside a long, expensive run with a cheap, deterministic, up-front check that names the problem. A misconfigured environment that surfaces mid-run appears as a confusing tool error many steps in. By then context and tokens are spent, and the fault is tangled up in the agent's reasoning. A doctor command collapses the whole environment-validity question into one pass. Its output names the broken precondition and how to fix it. Codex pairs a grouped report with a Notes block that surfaces anomalies first ([openai/codex PR #22336](https://github.com/openai/codex/pull/22336)). The same idea powers `brew doctor` and `flutter doctor`, where deterministic precondition validation is cheaper and clearer than diagnosing the fault from its downstream symptom ([Flutter troubleshoot install](https://docs.flutter.dev/install/troubleshoot)).

This is the proactive complement to reactive failure attribution. The [five-failure-layers diagnostic](../patterns/agent-design/five-failure-layers-diagnostic.md) and [agent debugging](agent-debugging.md) classify a failure after it happens. A doctor command tests the execution-environment preconditions before the run, so the most mechanical class of failure never reaches the agent.

## When this backfires

- Superficial checks mask real failure: a doctor that reports "MCP reachable, auth valid, config parses" can still miss a server that returns garbage, a token that lacks the needed scope, or a config that is valid but wrong. That false green light suppresses the suspicion that would otherwise drive investigation. The Kubernetes security audit named this directly: a superficial health check provides a false sense of safety ([kubernetes/kubernetes #81141, TOB-K8S-009](https://github.com/kubernetes/kubernetes/issues/81141)).
- Diagnostic-context divergence: the doctor validates the operator's local shell, but the agent runs in a cloud sandbox, CI runner, or container with different environment, secrets, and network reach. A green local report gives false confidence about a different runtime. Flutter's own tooling shows the same problem, where `flutter doctor` reports differently from the terminal versus the editor extension ([flutter/flutter #28084](https://github.com/flutter/flutter/issues/28084)).
- Check-set staleness: when the harness adds a new required tool or config key but the doctor's check list is not updated, the command passes while the real prerequisite is missing. The diagnostics drift behind the runtime they claim to validate.
- Stable solo setups: on a fixed local install where auth and MCP rarely change, the preflight step never finds anything and adds latency with no payoff. The benefit that justifies it, catching drift before a long autonomous run, never accrues.

## Key Takeaways

- A harness doctor command validates auth, MCP/tool reachability, config schema, tool availability, and version drift in one deterministic preflight pass.
- The causal benefit is relocating failure detection upstream: a cheap, legible, named precondition failure beats diagnosing the same fault from a mid-run symptom.
- Expose it as a standalone, shell-invocable command so it can diagnose a harness that will not even boot — Claude Code's `claude doctor` and Codex's `codex doctor` both do this.
- It complements, not replaces, reactive failure attribution: preflight catches environment faults before the run; layer diagnostics catch what slips through.
- Guard against the false-green trap — a passing doctor only certifies the checks it runs, in the context it runs them, against a check list someone keeps current.

## Related

- [Five-Failure-Layers Diagnostic](../patterns/agent-design/five-failure-layers-diagnostic.md) — reactive post-failure attribution; the doctor command is its proactive complement at the execution-environment layer
- [Agent Debugging](agent-debugging.md) — diagnosing bad agent output after the fact, which a preflight check reduces the surface for
- [Session Initialization Ritual](../patterns/agent-design/session-initialization-ritual.md) — startup orientation over project state; the doctor command validates harness-environment validity instead
- [Cloud-Agent Session Bootstrap](../patterns/agent-design/cloud-agent-session-bootstrap.md) — the install/start lifecycle whose preconditions a doctor command verifies
- [Agent Observability: OTel, Cost Tracking, and Trajectory Logging](agent-observability-otel.md) — runtime observability for failures the preflight check cannot anticipate
