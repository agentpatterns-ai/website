---
title: "Exclude Dynamic System Prompt Sections for Cross-Machine Cache Sharing"
description: "Move per-machine context (cwd, OS, shell, memory paths) out of the Claude Code system prompt so identical fleet configurations share one prompt-cache entry across users and machines."
tags:
  - context-engineering
  - cost-performance
  - claude
last_reviewed: 2026-05-30
---

# Exclude Dynamic System Prompt Sections for Cross-Machine Cache Sharing

> Strip per-machine context from the Claude Code system prompt so SDK fleets and CI runners share one cached prefix across users and machines.

The Claude Code `claude_code` preset embeds per-session context — working directory, git-repo flag, platform, active shell, OS version, and auto-memory paths — directly in the system prompt ahead of your `append` text. The byte sequence is therefore different on every machine and every directory, and Anthropic's prompt cache requires a 100% identical prefix to hit ([Anthropic prompt caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)). Setting `excludeDynamicSections: true` (TypeScript) or `"exclude_dynamic_sections": True` (Python) moves the dynamic block into the first user message, leaving only the static preset and your `append` text in the system prompt so "identical configurations share a cache entry across users and machines" ([Anthropic SDK docs](https://code.claude.com/docs/en/agent-sdk/modifying-system-prompts#improve-prompt-caching-across-users-and-machines)).

## When to Enable It

The option pays back when several conditions hold together:

| Condition | Why it matters |
|---|---|
| Multiple SDK or CLI instances run the same `preset` + `append` configuration | Cross-machine cache sharing has nothing to amortize across when there is only one machine |
| The fleet runs in **one workspace** | Prompt caches are workspace-isolated since Feb 2026 ([Anthropic prompt caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)) |
| Total system + tool prefix exceeds the per-model cache minimum | 1,024 tokens on Sonnet 4/4.5 and Opus 4/4.1; 2,048 on Sonnet 4.6 and Haiku 3.5; 4,096 on Opus 4.5/4.6 and Haiku 4.5 ([Anthropic prompt caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)) |
| Per-machine context (cwd, OS, memory paths) is not central to the agent's task | The documented authority trade-off bites hardest on exactly that context |

The Claude Code CLI documentation gives a concise rule: "Use with `-p` for scripted, multi-user workloads" ([Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference)). CI runners, scheduled-batch jobs, and multi-tenant agent apps fit this shape; an interactive developer on a laptop does not.

## How to Enable It

The option lives on the preset object form and is silently ignored when `systemPrompt` is a custom string ([Anthropic SDK docs](https://code.claude.com/docs/en/agent-sdk/modifying-system-prompts#improve-prompt-caching-across-users-and-machines)).

=== "TypeScript SDK"

    ```typescript
    import { query } from "@anthropic-ai/claude-agent-sdk";

    for await (const message of query({
      prompt: "Triage the open issues in this repo",
      options: {
        systemPrompt: {
          type: "preset",
          preset: "claude_code",
          append: "Label issues by component and severity.",
          excludeDynamicSections: true
        }
      }
    })) {
      // ...
    }
    ```

=== "Python SDK"

    ```python
    from claude_agent_sdk import query, ClaudeAgentOptions

    async for message in query(
        prompt="Triage the open issues in this repo",
        options=ClaudeAgentOptions(
            system_prompt={
                "type": "preset",
                "preset": "claude_code",
                "append": "Label issues by component and severity.",
                "exclude_dynamic_sections": True,
            },
        ),
    ):
        ...
    ```

=== "CLI"

    ```bash
    claude -p --exclude-dynamic-system-prompt-sections "triage open issues"
    ```

**Version floor**: `@anthropic-ai/claude-agent-sdk` v0.2.98+ (TypeScript) or `claude-agent-sdk` v0.1.58+ (Python) ([Anthropic SDK docs](https://code.claude.com/docs/en/agent-sdk/modifying-system-prompts#improve-prompt-caching-across-users-and-machines)).

## Why It Works

Anthropic prompt caching is keyed on byte-exact prefix match: "Cache hits require 100% identical prompt segments, including all text and images up to and including the block marked with cache control" ([Anthropic prompt caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)). When the `claude_code` preset inlines the working directory, OS version, and auto-memory paths into the system prompt, the byte sequence differs across every machine and every directory — so two sessions that share the same preset and `append` text still produce two different system-prompt hashes and two cache misses. Moving the dynamic block into the first user message leaves the system prompt as `<preset> + <append>` only — byte-identical across the fleet — and the workspace-shared cache covers every machine running that configuration ([Anthropic SDK docs](https://code.claude.com/docs/en/agent-sdk/modifying-system-prompts#improve-prompt-caching-across-users-and-machines)). The dynamic context still reaches Claude; it now sits one level lower in the message hierarchy.

CLAUDE.md content is unaffected — the SDK injects it into the conversation as project context, not into the system prompt, so its caching behaviour is independent of this flag ([Anthropic SDK docs](https://code.claude.com/docs/en/agent-sdk/modifying-system-prompts#improve-prompt-caching-across-users-and-machines)).

## When This Backfires

- **Single-machine interactive use.** One developer running Claude Code on one laptop has no fleet effect to capture. The cache write is amortized across a single user's session, and per-machine context is at its most useful in the system prompt where it carries full authority. The option is engineering for engineering's sake.
- **Custom `systemPrompt` string.** The option is silently ignored when `systemPrompt` is a custom string rather than the preset object form ([Anthropic SDK docs](https://code.claude.com/docs/en/agent-sdk/modifying-system-prompts#improve-prompt-caching-across-users-and-machines)); the CLI flag has the same restriction — "ignored when `--system-prompt` or `--system-prompt-file` is set" ([Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference)). Teams that have already replaced the preset get nothing.
- **Heterogeneous fleet.** Per-tenant `append` text, per-tenant tool definitions, or per-tenant model IDs each fork the prefix and refragment the cache. The flag moves only the documented dynamic sections; everything else must already be identical.
- **Cross-workspace deployments.** Prompt caches are workspace-isolated since Feb 2026 ([Anthropic prompt caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)). A multi-tenant product that gives each customer its own workspace cannot share caches between tenants regardless of this flag.
- **Environment-sensitive agents.** Anthropic documents the trade-off directly: "Instructions in the user message carry marginally less weight than the same text in the system prompt, so Claude may rely on them less strongly when reasoning about the current directory or auto-memory paths" ([Anthropic SDK docs](https://code.claude.com/docs/en/agent-sdk/modifying-system-prompts#improve-prompt-caching-across-users-and-machines)). The trade-off may have widened on Claude Opus 4.5/4.6, which Anthropic describes as "more responsive to the system prompt than previous models" ([Anthropic prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/system-prompts)).
- **Sub-minimum prefixes.** If the system prompt sits below the per-model cache floor, no cache writes occur and `excludeDynamicSections` cannot conjure savings that pricing arithmetic forbids ([Anthropic prompt caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)).

## Example

A scheduled GitHub Actions job that runs Claude Code across 50 self-hosted runners, each in a different working directory, to triage open issues every hour.

**Before** — default preset, per-runner cwd in the system prompt:

```yaml
# .github/workflows/triage.yml
- name: Triage issues
  run: |
    claude -p "Triage open issues in this repo. Label by component and severity."
```

Every runner produces a different system-prompt byte sequence (different `cwd`, sometimes different OS or memory paths), so the workspace cache holds 50 distinct entries. Each turn pays a cache write on a cold runner.

**After** — dynamic sections moved into the first user message:

```yaml
# .github/workflows/triage.yml
- name: Triage issues
  run: |
    claude -p --exclude-dynamic-system-prompt-sections \
      "Triage open issues in this repo. Label by component and severity."
```

All 50 runners produce one system-prompt prefix. The first runner pays the cache write; the other 49 hit the workspace-shared cache entry. The cwd, OS, and memory paths still reach Claude in the first user message; the model has marginally less weight to rely on for environment-aware tool calls (`Bash`, `Read`) — observe and accept the trade-off, or pin the working directory explicitly in your `append` text if the agent needs strong cwd grounding.

## Key Takeaways

- The Claude Code preset embeds per-machine context (cwd, git flag, platform, shell, OS version, memory paths) in the system prompt, fragmenting the prompt cache across every machine and directory.
- `excludeDynamicSections: true` (SDK) and `--exclude-dynamic-system-prompt-sections` (CLI) move that block into the first user message so identical configurations share one workspace-level cache entry.
- The option requires the preset object form (no effect when `systemPrompt` is a custom string), the `@anthropic-ai/claude-agent-sdk` v0.2.98+ or `claude-agent-sdk` v0.1.58+ floor, and a single workspace for cross-machine sharing.
- Anthropic documents one trade-off: instructions in user messages carry marginally less weight than in the system prompt — accept it when fleet cache reuse matters more than maximally authoritative environment context.
- The option pays nothing for single-developer interactive use, custom-prompt agents, heterogeneous fleets, or multi-workspace deployments.

## Related

- [Prompt Cache Economics](prompt-cache-economics.md)
- [Static Content First for Cache Hits](static-content-first-caching.md)
- [Extended Prompt Cache TTL for Long Agent Sessions](extended-prompt-cache-ttl.md)
- [Prompt Caching as Architectural Discipline](prompt-caching-architectural-discipline.md)
- [Dynamic System Prompt Composition](dynamic-system-prompt-composition.md)
