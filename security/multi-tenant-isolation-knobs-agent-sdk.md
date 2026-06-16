---
title: "Multi-Tenant Isolation Knobs for Shared-Container Agent SDK Hosting"
term: "Multi-Tenant Isolation Knobs"
description: "The specific set of Claude Agent SDK options and environment variables that neutralise each default settings-and-state input when one container serves multiple tenants."
tags:
  - security
  - claude
applies_to: "claude-code@2.x"
last_reviewed: 2026-06-03
maturity: adopted
---

# Multi-Tenant Isolation Knobs for Shared-Container Agent SDK Hosting

> Four Agent SDK knobs plus a per-tenant proxy-egress rule sever every default input that otherwise leaks one tenant's context into another.

The Claude Agent SDK's defaults are correct for single-tenant developer use and wrong for shared-container multi-tenant hosting. The SDK reads filesystem settings, `CLAUDE.md` files, a global config at `~/.claude.json`, and an auto-memory directory. In a shared container, each is a cross-tenant leakage vector. The fix is a small, named set of options applied on every `query()` call ([Hosting the Agent SDK — Multi-tenant isolation](https://code.claude.com/docs/en/agent-sdk/hosting#multi-tenant-isolation)).

## The Default Inputs That Leak

When you call `query()` without isolation options, the spawned `claude` CLI subprocess loads inputs from four locations, each able to hold prior-tenant data:

| Input | Default location | Why it leaks across tenants |
|---|---|---|
| User/project/local settings, `CLAUDE.md`, rules, skills, hooks | `~/.claude/`, `<cwd>/.claude/`, and every parent directory up to repo root | Loaded whenever `settingSources` is omitted — equivalent to `["user", "project", "local"]` ([claude-code-features](https://code.claude.com/docs/en/agent-sdk/claude-code-features)) |
| Global config | `~/.claude.json` | Always read regardless of `settingSources` ([What settingSources does not control](https://code.claude.com/docs/en/agent-sdk/claude-code-features#what-settingsources-does-not-control)) |
| Auto memory | `~/.claude/projects/<project>/memory/` | Loaded into the system prompt regardless of `settingSources` ([Auto memory](https://code.claude.com/docs/en/memory#auto-memory)) |
| Working directory | The application process's `cwd` | Inherited by every subprocess unless `cwd` is passed on each call ([Hosting the Agent SDK — The subprocess model](https://code.claude.com/docs/en/agent-sdk/hosting#the-subprocess-model)) |

The hosting docs are explicit: "Do not rely on default `query()` options for multi-tenant isolation. Because the inputs above are read regardless of `settingSources`, an SDK process can pick up host-level configuration and per-directory memory." ([What settingSources does not control](https://code.claude.com/docs/en/agent-sdk/claude-code-features#what-settingsources-does-not-control))

## The Knob Set

Each knob severs one input pathway. Apply all four on every `query()` call, plus a per-tenant proxy egress rule:

| Knob | Surface | What it neutralises |
|---|---|---|
| `settingSources: []` (TS) / `setting_sources=[]` (Py) | `query()` option | Blocks filesystem-loaded settings, `CLAUDE.md`, rules, skills, hooks ([Control filesystem settings](https://code.claude.com/docs/en/agent-sdk/claude-code-features#control-filesystem-settings-with-settingsources)) |
| `CLAUDE_CONFIG_DIR=<per-tenant>` | `env` | Relocates `~/.claude.json` to a per-tenant path; otherwise tenants share one global config ([What settingSources does not control](https://code.claude.com/docs/en/agent-sdk/claude-code-features#what-settingsources-does-not-control)) |
| `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` | `env` | Disables the auto-memory loader; required separately because auto-memory bypasses `settingSources` ([Hosting the Agent SDK — Multi-tenant isolation](https://code.claude.com/docs/en/agent-sdk/hosting#multi-tenant-isolation)) |
| `cwd: <per-tenant>` | `query()` option | Overrides the subprocess's default inheritance of the application's working directory ([Hosting the Agent SDK — The subprocess model](https://code.claude.com/docs/en/agent-sdk/hosting#the-subprocess-model)) |
| Per-tenant egress rules (distinct outbound IPs, credentials, domain allowlists) | Proxy / network layer | Prevents a compromised tenant exfiltrating through another tenant's outbound policy ([Hosting the Agent SDK — Multi-tenant isolation](https://code.claude.com/docs/en/agent-sdk/hosting#multi-tenant-isolation)) |

`CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` is the non-obvious one: empty `settingSources` looks complete but auto-memory loads anyway, listed as a separate bypass-table row ([What settingSources does not control](https://code.claude.com/docs/en/agent-sdk/claude-code-features#what-settingsources-does-not-control)).

## Why It Works

The mechanism is *input-pathway severance*. Every leakage channel is named in Anthropic's hosting docs, and every knob removes exactly one: empty `settingSources` short-circuits the filesystem walk, `CLAUDE_CONFIG_DIR` relocates `~/.claude.json`, `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` disables the auto-memory loader, and per-tenant `cwd` overrides default inheritance. Per-tenant proxy egress closes the network leg the SDK cannot reach: the agent never holds tenant-specific outbound credentials, so a compromised session cannot use a sibling's allowlist ([Securely deploying AI agents — The proxy pattern](https://code.claude.com/docs/en/agent-sdk/secure-deployment#the-proxy-pattern)). The knobs compose published API surface, not inferred behaviour.

## When This Backfires

These knobs are layer-7 settings-and-state hygiene. They do not substitute for kernel-level isolation, and they harm single-tenant workflows.

- **Mutually-hostile tenants with kernel-escape budget**: containers share the host kernel, and kernel exploits (Dirty Pipe, GameOver(lay), CVE-2025-23266) defeat every SDK knob at once. Use [gVisor, Firecracker, or dedicated containers](https://code.claude.com/docs/en/agent-sdk/secure-deployment#isolation-technologies) when tenants can run arbitrary code.
- **Managed policy settings on the host**: these load regardless of `settingSources` ([What settingSources does not control](https://code.claude.com/docs/en/agent-sdk/claude-code-features#what-settingsources-does-not-control)). The knob set does not override tenant-specific managed policy — remove the managed settings file or run each tenant on a host without it.
- **Single-tenant developer use**: empty `settingSources` strips out `CLAUDE.md`, project skills, and project hooks, breaking the legitimate workflow. Scope this knob set to multi-tenant hosting; do not generalise it.
- **Proxy-bypassing libraries**: per-tenant egress only works if all outbound traffic transits the proxy. Libraries that ignore `HTTPS_PROXY` (e.g., Node.js `fetch()` before Node 24's `NODE_USE_ENV_PROXY=1`) defeat the network leg ([Securely deploying AI agents — Traffic forwarding](https://code.claude.com/docs/en/agent-sdk/secure-deployment#traffic-forwarding)).
- **`SessionStore` mirrors transcripts only**: it does not mirror `CLAUDE.md` or working-directory artifacts ([Hosting the Agent SDK — Session and state persistence](https://code.claude.com/docs/en/agent-sdk/hosting#session-and-state-persistence)). Persisting tenant state across restarts needs a per-tenant volume strategy; bind every persistence surface to the same tenant ID.

## Example

The four SDK-level knobs applied together on a TypeScript `query()` call. `env` replaces the subprocess environment in TypeScript, so the inherited `process.env` must be spread to keep `PATH` and `ANTHROPIC_API_KEY` reachable ([Hosting the Agent SDK — Multi-tenant isolation](https://code.claude.com/docs/en/agent-sdk/hosting#multi-tenant-isolation)):

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

declare const prompt: string;
declare const tenantDir: string;   // /work/tenant-<id>
declare const configDir: string;   // /var/lib/claude-config/tenant-<id>

for await (const message of query({
  prompt,
  options: {
    cwd: tenantDir,
    settingSources: [],
    env: {
      ...process.env,
      CLAUDE_CONFIG_DIR: configDir,
      CLAUDE_CODE_DISABLE_AUTO_MEMORY: "1",
    },
  },
})) {
  // handle message
}
```

The Python form is structurally identical; `ClaudeAgentOptions(env=...)` merges on top of the inherited environment instead of replacing it ([Hosting the Agent SDK — Multi-tenant isolation](https://code.claude.com/docs/en/agent-sdk/hosting#multi-tenant-isolation)).

Verify isolation at runtime with a smoke test from one tenant's session: read `~/.claude.json`, list `~/.claude/projects/`, or read a known sibling-tenant path. A correctly configured tenant sees only its own `configDir` contents and an empty auto-memory directory. Run the test on every deploy — defaults-by-trust silently fail-open.

## Key Takeaways

- The Agent SDK loads four input categories — filesystem settings, global config, auto memory, and inherited `cwd` — that leak across tenants in a shared container ([Hosting the Agent SDK — Multi-tenant isolation](https://code.claude.com/docs/en/agent-sdk/hosting#multi-tenant-isolation)).
- `settingSources: []` is necessary but not sufficient: global config and auto memory bypass it and need their own knobs (`CLAUDE_CONFIG_DIR`, `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`) ([What settingSources does not control](https://code.claude.com/docs/en/agent-sdk/claude-code-features#what-settingsources-does-not-control)).
- Per-tenant `cwd` on every `query()` call is required — the subprocess otherwise inherits the application's working directory.
- Per-tenant egress rules at the proxy close the network leg; the SDK cannot enforce this itself ([Securely deploying AI agents](https://code.claude.com/docs/en/agent-sdk/secure-deployment)).
- The knob set is layer-7 hygiene. It does not substitute for kernel-level isolation; use dedicated containers or microVMs when tenants are mutually hostile.

## Related

- [Agent Network Egress Policy: Admin-Controlled Domain Allow/Deny](agent-network-egress-policy.md) — The harness-enforced domain policy primitive that the per-tenant egress rule composes with at the proxy layer
- [Per-Server MCP Environment Scoping for Credential Isolation](mcp-server-credential-isolation.md) — The same default-deny posture applied to MCP server credentials; complements the per-tenant env isolation here
- [Subprocess PID Namespace Sandboxing in Claude Code](subprocess-pid-namespace-sandboxing.md) — Process-tree isolation for Bash subprocesses spawned inside an agent session; covers the orthogonal process-isolation layer
- [Scoped Credentials via Proxy Outside the Agent Sandbox](scoped-credentials-proxy.md) — Keep tenant credentials outside the agent boundary entirely; the proxy pattern referenced for per-tenant egress credentials
- [Tenant Model Policy: Organization-Scoped Rules for AI Model Selection](../agent-design/tenant-model-policy.md) — The model-routing layer of per-tenant policy; sits above the settings-and-state isolation covered here
