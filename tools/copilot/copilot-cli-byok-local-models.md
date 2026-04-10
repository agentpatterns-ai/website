---
title: "Copilot CLI BYOK and Local Model Support"
description: "Use any OpenAI-compatible provider, Azure OpenAI, or Anthropic with Copilot CLI — or run fully local models for air-gapped and cost-controlled workflows."
tags:
  - copilot
  - cost-performance
  - workflows
aliases:
  - Copilot CLI bring your own key
  - Copilot CLI local models
  - Copilot CLI offline mode
---

# Copilot CLI BYOK and Local Model Support

> Connect Copilot CLI to your own model provider — Ollama, Azure OpenAI, Anthropic, or any OpenAI-compatible endpoint — for cost control, data residency compliance, and fully air-gapped workflows.

Released April 7, 2026, Copilot CLI BYOK lets you replace GitHub-hosted model routing with your own provider ([GitHub Changelog](https://github.blog/changelog/2026-04-07-copilot-cli-now-supports-byok-and-local-models)). Configuration is four environment variables.

## Configuration

Set these variables before launching `copilot` ([GitHub Docs](https://docs.github.com/copilot/how-tos/copilot-cli/customize-copilot/use-byok-models)):

| Variable | Required | Description |
|---|---|---|
| `COPILOT_PROVIDER_BASE_URL` | Yes | Base URL of your provider's API endpoint |
| `COPILOT_MODEL` | Yes | Model identifier (or use `--model` flag) |
| `COPILOT_PROVIDER_TYPE` | No | `openai` (default), `azure`, or `anthropic` |
| `COPILOT_PROVIDER_API_KEY` | No | API key — omit for unauthenticated local endpoints |

## Supported Providers

**OpenAI-compatible (Ollama, vLLM, Foundry Local, OpenAI):**

```shell
export COPILOT_PROVIDER_BASE_URL=http://localhost:11434
export COPILOT_MODEL=llama3.2
```

**Azure OpenAI:**

```shell
export COPILOT_PROVIDER_BASE_URL=https://YOUR-RESOURCE.openai.azure.com/openai/deployments/YOUR-DEPLOYMENT
export COPILOT_PROVIDER_TYPE=azure
export COPILOT_PROVIDER_API_KEY=YOUR-AZURE-API-KEY
export COPILOT_MODEL=YOUR-DEPLOYMENT-NAME
```

**Anthropic:**

```shell
export COPILOT_PROVIDER_TYPE=anthropic
export COPILOT_PROVIDER_BASE_URL=https://api.anthropic.com
export COPILOT_PROVIDER_API_KEY=YOUR-ANTHROPIC-API-KEY
export COPILOT_MODEL=claude-opus-4-5
```

## Offline Mode

`COPILOT_OFFLINE=true` disables telemetry and restricts the CLI to communicate only with the configured provider ([GitHub Changelog](https://github.blog/changelog/2026-04-07-copilot-cli-now-supports-byok-and-local-models)). Combined with a local Ollama instance, this enables fully air-gapped workflows.

**Important caveat**: isolation is only complete when `COPILOT_PROVIDER_BASE_URL` also points to a local or on-prem endpoint. A remote URL sends prompts and code context over the network to that provider regardless of offline mode ([GitHub Docs](https://docs.github.com/copilot/how-tos/copilot-cli/customize-copilot/use-byok-models)).

## GitHub Authentication

GitHub login is optional when using BYOK. With only provider credentials, the full local agentic experience runs without a Copilot subscription. Adding GitHub authentication re-enables `/delegate`, GitHub Code Search, and the GitHub MCP server ([GitHub Changelog](https://github.blog/changelog/2026-04-07-copilot-cli-now-supports-byok-and-local-models)).

## Model Requirements

Any model must support **tool calling** and **streaming**. A 128k context window is recommended for complex tasks. All built-in sub-agents (explore, task, code-review) inherit the provider configuration automatically — there is no per-agent routing ([GitHub Changelog](https://github.blog/changelog/2026-04-07-copilot-cli-now-supports-byok-and-local-models)).

## Trade-offs

| Consideration | Detail |
|---|---|
| Capability ceiling | Local models have lower reasoning quality than hosted frontier models for complex tasks |
| Single provider | Only one provider config is active at a time — no native multi-provider routing per task |
| Failure handling | Invalid config surfaces actionable errors; the CLI never silently falls back to GitHub-hosted models |
| Discovery | `copilot help providers` prints quick setup instructions in-terminal |

## Example

Air-gapped compliance scenario: a financial services team must keep all code on-premises.

```shell
# Pull a capable local model
ollama pull llama3.2

# Configure Copilot CLI for local-only operation
export COPILOT_PROVIDER_BASE_URL=http://localhost:11434
export COPILOT_MODEL=llama3.2
export COPILOT_OFFLINE=true

# Launch — no GitHub auth required, no external network calls
copilot
```

The team loses access to `/delegate` and GitHub MCP server but gains full data-residency compliance. For tasks requiring stronger reasoning, swapping `COPILOT_MODEL` and `COPILOT_PROVIDER_BASE_URL` to a hosted provider (without `COPILOT_OFFLINE`) routes those sessions externally while preserving the same CLI experience.

## Key Takeaways

- Four env vars configure any OpenAI-compatible provider, Azure OpenAI, or Anthropic
- `COPILOT_OFFLINE=true` restricts network to the configured provider — full isolation requires a local provider URL
- GitHub auth is optional; adding it re-enables cloud features like `/delegate` and GitHub MCP
- All built-in sub-agents inherit provider config; per-task routing requires managing env vars externally
- Invalid provider config surfaces clear errors — no silent fallback to GitHub-hosted models

## Related

- [Copilot CLI Agentic Workflows](copilot-cli-agentic-workflows.md)
- [Cloud-Local Agent Handoff](../../workflows/cloud-local-agent-handoff.md)
- [Blast Radius Containment](../../security/blast-radius-containment.md)
- [MCP Integration](mcp-integration.md)
