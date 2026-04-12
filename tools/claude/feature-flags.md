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

Claude Code uses a naming pattern that communicates the risk profile of each variable ([settings docs](https://code.claude.com/docs/en/settings)):

| Prefix | Meaning | Signal |
|--------|---------|--------|
| `ENABLE_*` | Opt-in to experimental features | Not yet default — expect rough edges |
| `DISABLE_*` | Opt-out of default behaviors | Default but optional — suppress without removing |
| `CLAUDE_CODE_*` | Configure behavior parameters | Stable knobs — safe to tune |

This mirrors feature flag best practices in production systems: progressive exposure of new capabilities without forcing changes to existing workflows.

## Performance and Model Control

| Variable | Effect | Default |
|----------|--------|---------|
| `CLAUDE_CODE_EFFORT_LEVEL` | Adaptive reasoning level: `low`, `medium`, `high` | `auto` ([env-vars docs](https://code.claude.com/docs/en/env-vars)) |
| `MAX_THINKING_TOKENS` | Extended thinking token budget (used when adaptive thinking is disabled) | Model-dependent |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | Cap on output tokens per response | Model default ([env-vars docs](https://code.claude.com/docs/en/env-vars)) |
| `CLAUDE_CODE_SUBAGENT_MODEL` | Force a specific model for sub-agent operations | Latest available ([env-vars docs](https://code.claude.com/docs/en/env-vars)) |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | Pin the Sonnet model version | Latest Sonnet ([model config docs](https://code.claude.com/docs/en/model-config)) |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | Pin the Opus model version | Latest Opus ([model config docs](https://code.claude.com/docs/en/model-config)) |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | Pin the Haiku model version | Latest Haiku ([model config docs](https://code.claude.com/docs/en/model-config)) |

Pin model versions when deploying through Bedrock, Vertex AI, or Foundry — without pinning, alias resolution changes when Anthropic releases new models ([model config docs](https://code.claude.com/docs/en/model-config)).

### modelOverrides

The `modelOverrides` setting (v2.1.73) maps model picker entries to custom provider model IDs, decoupling the UI from the underlying routing ([settings docs](https://code.claude.com/docs/en/settings)). Combined with `ANTHROPIC_DEFAULT_*_MODEL` for version pinning, it gives enterprise teams full control over which model serves each picker slot.

## Context and Memory

| Variable | Effect | Default |
|----------|--------|---------|
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | Auto-compaction trigger threshold (1-100) | 95% ([settings docs](https://code.claude.com/docs/en/settings)) |
| `CLAUDE_CODE_DISABLE_AUTO_MEMORY` | Disable automatic MEMORY.md persistence | Enabled ([settings docs](https://code.claude.com/docs/en/settings)) |
| `CLAUDE_CODE_DISABLE_1M_CONTEXT` | Remove 1M token context window models from picker | Enabled ([model config docs](https://code.claude.com/docs/en/model-config)) |
| `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING` | Revert to fixed thinking budget via `MAX_THINKING_TOKENS` | Adaptive enabled ([model config docs](https://code.claude.com/docs/en/model-config)) |
| `ENABLE_CLAUDE_CODE_SM_COMPACT` | Enable session memory compaction (undocumented experimental flag) | Disabled |

Opus 4.6 and Sonnet 4.6 support 1M token context via the `context-1m-2025-08-07` beta header ([Anthropic models page](https://docs.anthropic.com/en/docs/about-claude/models)). Long-context pricing applies above the standard 200K threshold. Use `CLAUDE_CODE_DISABLE_1M_CONTEXT` to suppress 1M models from the picker.

## Agent and Workflow

| Variable | Effect | Default |
|----------|--------|---------|
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | Enable agent teams for multi-agent coordination | Disabled ([settings docs](https://code.claude.com/docs/en/settings)) |
| `CLAUDE_CODE_PLAN_MODE_REQUIRED` | Auto-set by Claude Code when spawning teammates; indicates [Plan Mode](../../workflows/plan-mode.md) is active (read-only) | Auto-set ([settings docs](https://code.claude.com/docs/en/settings)) |
| `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR` | Reset to project directory after each bash command | Not set ([env-vars docs](https://code.claude.com/docs/en/env-vars)) |
| `ENABLE_LSP_TOOL` | Enable Language Server Protocol integration (goToDefinition, findReferences, hover, documentSymbol, getDiagnostics) | Disabled ([GitHub issue #15619](https://github.com/anthropics/claude-code/issues/15619), [ClaudeLog](https://claudelog.com/faqs/what-is-lsp-tool-in-claude-code/)) |

The LSP tool requires the marketplace plugin (`/plugin marketplace add Piebald-AI/claude-code-lsps`) plus a language server binary ([ClaudeLog](https://claudelog.com/faqs/what-is-lsp-tool-in-claude-code/)). See [Semantic Context Loading](../../context-engineering/semantic-context-loading.md) for how LSP-backed tools enable semantic codebase queries.

## Tool Configuration

| Variable | Effect | Default |
|----------|--------|---------|
| `CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY` | Maximum concurrent tool executions | 10 ([env vars gist](https://gist.github.com/unkn0wncode/f87295d055dd0f0e8082358a0b5cc467)) |
| `BASH_MAX_OUTPUT_LENGTH` | Maximum bash output characters (middle-truncated) | Not specified ([env-vars docs](https://code.claude.com/docs/en/env-vars)) |
| `CLAUDE_CODE_GLOB_TIMEOUT_SECONDS` | Glob operation timeout | 20s (60s on WSL) ([env vars gist](https://gist.github.com/unkn0wncode/f87295d055dd0f0e8082358a0b5cc467)) |

## Observability

| Variable | Effect | Default |
|----------|--------|---------|
| `CLAUDE_CODE_ENABLE_TELEMETRY` | Enable OpenTelemetry data collection (required before configuring exporters) | Disabled ([settings docs](https://code.claude.com/docs/en/settings)) |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OpenTelemetry exporter endpoint for traces, metrics, and logs | Not set |
| `OTEL_LOG_USER_PROMPTS` | Include user prompts in OTEL logs | Disabled ([env vars gist](https://gist.github.com/unkn0wncode/f87295d055dd0f0e8082358a0b5cc467)) |
| `OTEL_LOG_TOOL_CONTENT` | Include tool content in OTEL logs | Disabled ([env vars gist](https://gist.github.com/unkn0wncode/f87295d055dd0f0e8082358a0b5cc467)) |

## Setting Variables

Set variables persistently in `settings.json` under the `env` key ([settings docs](https://code.claude.com/docs/en/settings)), or per-session via shell: `CLAUDE_CODE_EFFORT_LEVEL=low claude`.

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

`CLAUDE_CODE_EFFORT_LEVEL=low` reduces reasoning depth for routine tasks. `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=80` triggers compaction earlier, keeping the context window from saturating. The model pin prevents silent upgrades when Anthropic releases a new Sonnet version.

## Related

- [Claude Code Sub-Agents](sub-agents.md)
- [Claude Code Agent Teams](agent-teams.md)
- [Claude Code Hooks Lifecycle](hooks-lifecycle.md)
- [Claude Code Extension Points](extension-points.md)
- [Claude Code Session Scheduling](session-scheduling.md)
- [OpenTelemetry for Agent Observability](../../standards/opentelemetry-agent-observability.md)
- [Cost-Aware Agent Design](../../agent-design/cost-aware-agent-design.md)
