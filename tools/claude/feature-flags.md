---
title: "Claude Code Feature Flags and Environment Variables"
description: "Claude Code environment variables use a three-tier naming convention (ENABLE_, DISABLE_, CLAUDE_CODE_) that signals each flag's stability and risk profile."
aliases:
  - "Claude Code environment variables"
  - "Claude Code feature flags"
  - "Claude Code env vars"
tags:
  - agent-design
  - cost-performance
  - claude
---

# Claude Code Feature Flags and Environment Variables

> Claude Code exposes environment variables that control model selection, context handling, tool concurrency, and observability — each prefixed with a naming convention (`ENABLE_*`, `DISABLE_*`, `CLAUDE_CODE_*`) that signals its stability and risk profile.

## The Three-Tier Naming Convention

Claude Code uses a naming pattern that signals each variable's risk profile ([settings docs](https://code.claude.com/docs/en/settings)):

| Prefix | Meaning | Signal |
|--------|---------|--------|
| `ENABLE_*` | Opt-in to experiments | Not default — expect rough edges |
| `DISABLE_*` | Opt-out of defaults | Default, suppressible |
| `CLAUDE_CODE_*` | Behavior parameters | Stable — safe to tune |

The pattern mirrors progressive-exposure feature flagging: new capabilities ship behind `ENABLE_*` before flipping to default.

## Performance and Model Control

| Variable | Effect | Default |
|----------|--------|---------|
| `CLAUDE_CODE_EFFORT_LEVEL` | Adaptive reasoning level: `low`, `medium`, `high` | `auto` ([env-vars docs](https://code.claude.com/docs/en/env-vars)) |
| `MAX_THINKING_TOKENS` | Extended-thinking budget (used when adaptive is off) | Model-dependent |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | Cap on output tokens per response | Model default ([env-vars docs](https://code.claude.com/docs/en/env-vars)) |
| `CLAUDE_CODE_SUBAGENT_MODEL` | Force a specific model for sub-agents | Latest ([env-vars docs](https://code.claude.com/docs/en/env-vars)) |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | Pin the Sonnet version | Latest Sonnet ([model config docs](https://code.claude.com/docs/en/model-config)) |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | Pin the Opus version | Latest Opus |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | Pin the Haiku version | Latest Haiku |

Pin model versions on Bedrock, Vertex AI, or Foundry — alias resolution otherwise shifts when Anthropic releases new models ([model config docs](https://code.claude.com/docs/en/model-config)).

### modelOverrides

The `modelOverrides` setting (v2.1.73) maps picker entries to custom provider model IDs, decoupling the UI from routing ([settings docs](https://code.claude.com/docs/en/settings)). Combined with `ANTHROPIC_DEFAULT_*_MODEL`, it gives enterprise teams full control over which model serves each picker slot.

## Context and Memory

| Variable | Effect | Default |
|----------|--------|---------|
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | Auto-compaction threshold (1-100) | 95% ([settings docs](https://code.claude.com/docs/en/settings)) |
| `CLAUDE_CODE_DISABLE_AUTO_MEMORY` | Disable auto MEMORY.md persistence | Enabled |
| `CLAUDE_CODE_DISABLE_1M_CONTEXT` | Remove 1M-context models from picker | Enabled ([model config docs](https://code.claude.com/docs/en/model-config)) |
| `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING` | Revert to fixed `MAX_THINKING_TOKENS` budget | Adaptive |
| `ENABLE_CLAUDE_CODE_SM_COMPACT` | Session memory compaction (undocumented) | Disabled |

Opus 4.6 and Sonnet 4.6 support 1M context via the `context-1m-2025-08-07` beta header ([Anthropic models page](https://docs.anthropic.com/en/docs/about-claude/models)); long-context pricing applies above 200K. Set `CLAUDE_CODE_DISABLE_1M_CONTEXT` to suppress 1M models from the picker.

## Agent and Workflow

| Variable | Effect | Default |
|----------|--------|---------|
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | Enable agent teams | Disabled ([settings docs](https://code.claude.com/docs/en/settings)) |
| `CLAUDE_CODE_PLAN_MODE_REQUIRED` | Auto-set when spawning teammates; flags [Plan Mode](../../workflows/plan-mode.md) read-only | Auto-set |
| `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR` | Reset to project dir after each bash command | Not set ([env-vars docs](https://code.claude.com/docs/en/env-vars)) |
| `ENABLE_LSP_TOOL` | LSP integration: goToDefinition, findReferences, hover, documentSymbol, getDiagnostics | Disabled ([issue #15619](https://github.com/anthropics/claude-code/issues/15619), [ClaudeLog](https://claudelog.com/faqs/what-is-lsp-tool-in-claude-code/)) |

The LSP tool requires the marketplace plugin (`/plugin marketplace add Piebald-AI/claude-code-lsps`) plus a language server binary ([ClaudeLog](https://claudelog.com/faqs/what-is-lsp-tool-in-claude-code/)). See [Semantic Context Loading](../../context-engineering/semantic-context-loading.md) for how LSP-backed tools enable semantic queries.

## Tool Configuration

| Variable | Effect | Default |
|----------|--------|---------|
| `CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY` | Max concurrent tool executions | 10 ([env vars gist](https://gist.github.com/unkn0wncode/f87295d055dd0f0e8082358a0b5cc467)) |
| `BASH_MAX_OUTPUT_LENGTH` | Max bash output chars (middle-truncated) | Not specified ([env-vars docs](https://code.claude.com/docs/en/env-vars)) |
| `CLAUDE_CODE_GLOB_TIMEOUT_SECONDS` | Glob timeout | 20s (60s on WSL) |

## Observability

| Variable | Effect | Default |
|----------|--------|---------|
| `CLAUDE_CODE_ENABLE_TELEMETRY` | Enable OTEL collection (required before exporters) | Disabled ([settings docs](https://code.claude.com/docs/en/settings)) |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTEL endpoint for traces, metrics, logs | Not set |
| `OTEL_LOG_USER_PROMPTS` | Include user prompts in OTEL logs | Disabled ([env vars gist](https://gist.github.com/unkn0wncode/f87295d055dd0f0e8082358a0b5cc467)) |
| `OTEL_LOG_TOOL_CONTENT` | Include tool content in OTEL logs | Disabled |

## Setting Variables

Set variables in `settings.json` under the `env` key ([settings docs](https://code.claude.com/docs/en/settings)), or per-session: `CLAUDE_CODE_EFFORT_LEVEL=low claude`. For fleet distribution, see the [managed settings drop-in](managed-settings-drop-in.md); [`--bare` mode](bare-mode.md) reads the same env block in CI.

## When the Prefix Taxonomy Breaks Down

The prefix signal is a heuristic, not a contract — Anthropic's [settings docs](https://code.claude.com/docs/en/settings) do not define a formal naming policy. Do not rely on the prefix alone to infer stability:

- **Exceptions.** `MAX_THINKING_TOKENS`, `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`, `BASH_MAX_OUTPUT_LENGTH`, and the `OTEL_*` family carry no tier prefix but are as load-bearing as any stable knob.
- **Undocumented `ENABLE_*`.** Flags like `ENABLE_CLAUDE_CODE_SM_COMPACT` are absent from the official reference; name, defaults, and behavior can change without a deprecation window.
- **Promotion churn.** Experimental flags that graduate to default are sometimes renamed or folded into `settings.json` fields — pinning a specific `ENABLE_*` in a managed drop-in can silently stop working after an upgrade. Treat the [release notes](https://github.com/anthropics/claude-code/releases) as authoritative, not the prefix.

## Example

A `settings.json` for a cost-conscious team deploying through Bedrock, with telemetry enabled and context compaction tuned:

```json
{
  "env": {
    "CLAUDE_CODE_EFFORT_LEVEL": "low",
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "80",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "claude-sonnet-4-20250514",
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_EXPORTER_OTLP_ENDPOINT": "http://localhost:4317"
  },
  "modelOverrides": {
    "sonnet": "arn:aws:bedrock:us-east-1:123456789:inference-profile/sonnet-4"
  }
}
```

`CLAUDE_CODE_EFFORT_LEVEL=low` reduces reasoning depth for routine tasks. `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=80` compacts earlier, keeping context from saturating. The model pin prevents silent upgrades when Anthropic ships a new Sonnet.

## Related

- [Claude Code Sub-Agents](sub-agents.md)
- [Claude Code Agent Teams](agent-teams.md)
- [Claude Code Hooks Lifecycle](hooks-lifecycle.md)
- [Claude Code Extension Points](extension-points.md)
- [Claude Code Session Scheduling](session-scheduling.md)
- [OpenTelemetry for Agent Observability](../../standards/opentelemetry-agent-observability.md)
- [Cost-Aware Agent Design](../../agent-design/cost-aware-agent-design.md)
