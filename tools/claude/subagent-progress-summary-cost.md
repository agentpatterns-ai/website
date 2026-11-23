---
title: "Claude Code Subagent Progress Summaries: What They Cost"
description: "From v2.1.327, Claude Code writes subagent progress summaries from short notes in terminal sessions. What each release covers, what the changelog leaves out, and the variable that turns them off."
tags:
  - claude
  - agent-design
  - cost-performance
applies_to: "claude-code@2.x"
last_reviewed: 2026-11-23
status: current
---

# Claude Code Subagent Progress Summaries: What They Cost

> In terminal sessions, Claude Code now writes subagent progress summaries from short notes, not the whole conversation, and one environment variable turns them off.

Three changelog entries between v2.1.327 and v2.1.330 say that, in terminal sessions, subagent progress summaries are written from short notes and use "far fewer tokens" ([changelog](https://code.claude.com/docs/en/changelog)). Each entry covers a different route to the model. The entries give no figure for the saving, and the costs page does not list progress summaries under background token usage as of November 23, 2026 ([costs](https://code.claude.com/docs/en/costs.md#background-token-usage)).

## Which releases cover which route

| Release | Date | Route the entry names | What the entry says |
|---------|------|-----------------------|---------------------|
| v2.1.327 | November 17, 2026 | Amazon Bedrock, Google Vertex AI and Microsoft Foundry | Written "from short notes, not the whole conversation, using far fewer tokens" |
| v2.1.328 | November 19, 2026 | The Anthropic API | Written "by the default small fast model from short notes, also with telemetry off, using far fewer tokens" |
| v2.1.330 | November 20, 2026 | A Claude apps gateway | Written "from short notes instead of the whole conversation, using far fewer tokens" |

Source for all three rows: [changelog](https://code.claude.com/docs/en/changelog). Each entry is limited to "terminal sessions". The entries do not mention other surfaces.

## What the entries leave open

- Only the v2.1.328 entry names the model that writes the summary. The other two entries do not say which model writes it on their routes.
- The "short notes" have no stated contents or length.
- The entries give neither a token count nor a percentage.
- Where a summary shows up for you is unstated, so check what you lose before you turn them off.

The environment variables reference describes a Haiku-class model for background tasks ([environment variables](https://code.claude.com/docs/en/env-vars.md)). The v2.1.328 entry does not say that "the default small fast model" is that model.

## The summaries are separate requests

The v2.1.323 entry for the off switch speaks of "subagent progress summaries and the requests that write them" ([changelog](https://code.claude.com/docs/en/changelog)). The summary is its own request. Session recap, idle compaction and prompt suggestions are the background uses the costs page lists, and the page does not name progress summaries ([costs](https://code.claude.com/docs/en/costs.md#background-token-usage)).

Earlier entries also changed how these requests run. The v2.1.128 entry fixed summaries "missing the prompt cache (~3× `cache_creation` reduction)". The v2.1.318 entry changed summaries on Bedrock, Vertex, Foundry or with telemetry off, so that "on a cold prompt cache, one can now wait up to 5 minutes for the subagent's pending response" ([changelog](https://code.claude.com/docs/en/changelog)).

## Turn them off

Set `CLAUDE_CODE_DISABLE_AGENT_PROGRESS_SUMMARIES` to `1`:

```bash
export CLAUDE_CODE_DISABLE_AGENT_PROGRESS_SUMMARIES=1
```

The v2.1.323 entry says this turns off "subagent progress summaries and the requests that write them", and that the variable is "available since 2.1.318" ([changelog](https://code.claude.com/docs/en/changelog)). The environment variables reference does not list it as of November 23, 2026 ([environment variables](https://code.claude.com/docs/en/env-vars.md)). Only `1` is named as a value, and other values go unmentioned.

## Upgrade past the v2.1.327 effort regression

v2.1.328 fixed a regression from v2.1.327. Effort could be turned off for a subagent's model for the rest of the session if "Bedrock, Google Cloud's Agent Platform or Foundry refused its progress summary's effort setting" ([changelog](https://code.claude.com/docs/en/changelog)). The entry's wording shows that the summary request carries its own effort setting. Run `claude --version` to check your release.

## Measure on your own setup

Measure the saving yourself, because the changelog gives none. Run the same subagent-heavy task with the variable set and unset, and compare token totals. The [costs page](https://code.claude.com/docs/en/costs.md) covers cost tracking.

## Key Takeaways

- The change landed per route: v2.1.327 for Bedrock, Vertex and Foundry, v2.1.328 for the Anthropic API, v2.1.330 for a Claude apps gateway. Each entry names terminal sessions and no other surface.
- The entries state no saving and name the writing model only for the Anthropic API. Measure before you count on a figure.
- Summaries are separate requests that the costs page does not list as background usage.
- `CLAUDE_CODE_DISABLE_AGENT_PROGRESS_SUMMARIES=1` stops the summaries and their requests, and the env-vars reference does not list it.
- On Bedrock, Vertex or Foundry, v2.1.327 could turn off a subagent model's effort for the session when the provider refused the summary's effort setting. v2.1.328 fixes it.

## Related

- [Claude Code Sub-Agents for Delegating Complex Tasks](sub-agents.md)
- [Claude Code Subagent Model Fallback: What Carries Down](subagent-fallback-carry-over.md)
- [Cost-Aware Agent Design](../../token-engineering/cost-aware-agent-design.md)
- [Harness Token Economics](../../token-engineering/harness-token-economics.md)
