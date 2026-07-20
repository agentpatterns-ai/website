---
title: "Rewriting a CLI Into a JSON Payload for Agents"
term: "JSON-Payload CLI Rewrite"
description: "Replacing a conventional CLI's flags with a single JSON input payload so agents call it more reliably does not measure as an improvement — args match or beat JSON on correctness and cost 4-11x less."
tags:
  - anti-pattern
  - cost-performance
  - tool-engineering
  - tool-agnostic
aliases:
  - JSON-payload CLI rewrite
  - JSON-only CLI for agents
  - rewriting a CLI for agents
last_reviewed: 2026-07-10
maturity: emerging
---

# Rewriting a CLI Into a JSON Payload for Agents

> Replacing a conventional CLI's flags with a single JSON payload does not make agents more reliable — it measures as cost with no correctness gain.

The anti-pattern is not offering JSON at all. It is replacing a working flag-and-argument interface with a JSON-input payload on the theory that agents call structured interfaces more reliably, then shipping the rewrite without running the one experiment that settles it: does a JSON-input CLI actually beat the conventional one on your own agent workload?

## The trap

The advice sounds right. Agents already think in an API's JSON schema, so a JSON-input CLI seems to remove a translation step and a class of wrong-flag-name errors ([Poehnelt, *You Need to Rewrite Your CLI for AI Agents*](https://justin.poehnelt.com/posts/rewrite-your-cli-for-ai-agents/)). A team re-plumbs the interface for agent consumers and expects higher success. Measured head to head, the rewrite buys nothing and costs a lot.

Microsoft's Agent Experience team built a synthetic CLI, `podctl`, that creates multi-service deployments from 30-plus values across three nesting levels, arrays, mixed types, and cross-references. They shipped it as [two separate binaries — one args-only, one JSON-only — so an agent could not prefer one on sight, then ran five runs per model per input mode through GitHub Copilot Chat across Claude Haiku 4.5, Sonnet 4.6, Sonnet 5, GPT-5.3-Codex, and MAI-Code-1-Flash](https://developer.microsoft.com/blog/dont-rewrite-your-cli-for-agents).

The result was one-sided. [Every args profile hit perfect correctness across all five runs for every model; JSON matched only on the three strongest models, and Haiku 4.5 produced just 2 of 5 correct deployments in JSON mode](https://developer.microsoft.com/blog/dont-rewrite-your-cli-for-agents). On cost, [JSON ran 4x to 11x more per task — GPT-5.3-Codex at $0.05 for args against $0.54 for JSON, Haiku 4.5 at $0.03 against $0.23](https://developer.microsoft.com/blog/dont-rewrite-your-cli-for-agents). Their summary: JSON never improved correctness and always increased cost.

## Why it works

Conventional flags match or beat a JSON input payload for two compounding reasons. First is pretraining alignment: models have seen far more flag-and-argument CLI usage, man pages, and `--help` text than any one project's bespoke JSON-input interface, so args are a higher-alignment action space — the same mechanism behind treating the [Unix CLI as the native tool interface](../../tool-engineering/unix-cli-native-tool-interface.md). Second is the shell-escaping tax: emitting a valid JSON string inside a shell command means nested quoting and escaping, which is error-prone and token-heavy. Microsoft isolated that cost by holding model, payload, and correctness fixed and varying only the shell — for Sonnet 4.6 the args-versus-JSON gap was [9x on PowerShell but collapsed to 1.5x on Bash, "same model, same payload, same correctness"](https://developer.microsoft.com/blog/dont-rewrite-your-cli-for-agents). The escaping, not the structure, is the cost driver; the extra tokens and reasoning to assemble the payload produce the 4-11x per-task price with no correctness return.

One distinction bounds the finding: input versus output. This measures JSON the agent must hand-construct as input. Machine-readable JSON output the tool emits stays worth shipping — a separate lever ([Designing for Agent Consumers](../../tool-engineering/designing-for-agent-consumers.md)) that carries no escaping tax because the agent reads it rather than writes it.

## When this backfires

The advice here — keep the conventional interface — is itself wrong when the caller or the environment removes the cost that makes the rewrite lose. A first-class JSON input path earns its place when:

- The caller is a program, not an agent. A pipeline or batch job that generates payloads deterministically never pays the agent-construction tax, so Microsoft keeps JSON acceptable for [programmatic use or batch operations](https://developer.microsoft.com/blog/dont-rewrite-your-cli-for-agents) — just not as a replacement for args.
- The target shell is Bash, not PowerShell. Escaping is cheap enough there that the cost multiple falls to roughly 1.5x; the penalty is small, though there is still no correctness upside to chase.
- A frontier model is guaranteed. The correctness gap appeared only on the weakest model tested; the three strongest matched args, so pinning a capable model removes the accuracy risk while leaving the 4-11x cost.
- The spec genuinely exceeds flag ergonomics. Very large nested configuration is conventionally passed as a config file, not an inline JSON string argument — the file sidesteps the shell-escaping tax that drives the measured cost.

Outside those conditions the real levers are cheaper than a rewrite: better discoverability, clearer help text, and [machine-readable error responses](../../tool-engineering/rfc9457-machine-readable-errors.md) that let an agent recover from a bad conventional call.

## Example

The study's `podctl` had the shape `services[].resources.cpu.request`. In JSON-only form the agent must build and escape that whole tree as one string argument (the anti-pattern):

```bash
podctl deploy --spec '{"services":[{"name":"api","resources":{"cpu":{"request":"500m"}}},
{"name":"web","resources":{"cpu":{"request":"250m"}}}]}'
# Measured: matches args on correctness only on the strongest models; 4-11x the cost per task
```

The args-only form maps each value to a flag, with no payload to escape:

```bash
podctl deploy --service api --cpu-request 500m \
              --service web --cpu-request 250m
# Measured: 5/5 correctness on every model tested, 4-11x cheaper per task
# Keep --spec available for batch/programmatic callers — just don't remove the flags.
```

Only a head-to-head run on the real workload catches that the rewrite adds cost without buying correctness ([Microsoft AX](https://developer.microsoft.com/blog/dont-rewrite-your-cli-for-agents)).

## Key Takeaways

- Replacing a flag-and-argument CLI with a JSON input payload for agents measured as pure cost: args hit 5/5 correctness on every model tested and cost 4-11x less per task, while JSON matched only on the strongest models.
- The mechanism is pretraining alignment plus a shell-escaping tax — the args-versus-JSON cost gap fell from 9x on PowerShell to 1.5x on Bash at identical correctness, so the escaping, not the structure, drives the cost.
- JSON output the tool emits still earns its place; the finding is about JSON input the agent must hand-construct and escape.
- Keep a JSON path only for batch or programmatic callers, Bash-only targets, or specs beyond flag ergonomics — and run the experiment before re-plumbing the interface.

## Related

- [Cheaper-Per-Token Model Upgrades That Cost More Per Task](cheaper-per-token-costlier-per-task.md) — the sibling anti-pattern from the same Microsoft AX measurement series; both turn on running the experiment before trusting an intuitive change.
- [Unix CLI as Native Tool Interface](../../tool-engineering/unix-cli-native-tool-interface.md) — the pretraining-alignment argument for conventional CLI as the agent's action space, which this page shows JSON input does not improve on.
- [Designing for Agent Consumers (Agent Experience)](../../tool-engineering/designing-for-agent-consumers.md) — the discipline whose real levers (discoverability, help text, structured errors and output) beat an input-format rewrite.
- [CLI-First Skill Design](../../tool-engineering/cli-first-skill-design.md) — where JSON belongs on a CLI: as adaptive output and an option for programmatic callers, not a replacement for args.
- [Token Preservation Backfire](token-preservation-backfire.md) — another case where an intuitively helpful instruction to an agent produced measured cost without the intended benefit.
