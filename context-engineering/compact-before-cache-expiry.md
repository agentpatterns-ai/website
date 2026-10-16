---
title: "Compact Before Cache Expiry, Not at Context Pressure"
term: "Idle Compaction"
description: "Claude Code compacts an idle 200K+ token conversation before its one-hour prompt cache expires. Learn the five firing conditions, the scope limits, and when to turn it off."
aliases:
  - idle compaction
  - compact before cache expiry
  - cache-expiry compaction
tags:
  - context-engineering
  - cost-performance
  - claude
last_reviewed: 2026-10-15
maturity: emerging
---

# Compact Before Cache Expiry, Not at Context Pressure

> Claude Code compacts an idle conversation just before its prompt cache expires, while the prefix is still cheap to read.

Idle compaction compacts an idle conversation shortly before its prompt cache expires, so the next message reprocesses a summary instead of the full history. Claude Code 2.1.299 describes it this way: "a 200K+ token conversation left idle for about 54 minutes is compacted before its one-hour prompt cache expires, so your next message doesn't reprocess it all" ([changelog](https://code.claude.com/docs/en/changelog)). The saving depends on five conditions, and it trades detail for cost.

## When it fires

Idle compaction is on by default only when all five conditions hold ([settings reference](https://code.claude.com/docs/en/settings-reference#idlecompaction)):

- Session: you are in an interactive terminal session.
- Prompt cache: the conversation is on the one-hour prompt cache TTL.
- Feature flags: Claude Code can fetch feature flags from Anthropic.
- Size: the context has reached the token threshold, 200,000 by default.
- Idle time: about 54 minutes have passed since the last request, and your computer is awake.

Two of these limit the scope more than they first appear.

- 1M window only, at the default. A 200K-window conversation auto-compacts before it reaches 200,000 tokens, so it never qualifies until you lower `CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS`. Values below 100000 are raised to 100000 ([settings reference](https://code.claude.com/docs/en/settings-reference#change-the-idle-compaction-threshold)).
- One-hour TTL only. Claude Code requests that TTL by default only on a Claude subscription within plan usage. With an API key or a cloud provider, you must set `promptCacheTtl` to `1h` ([prompt caching](https://code.claude.com/docs/en/prompt-caching#which-ttl-each-request-gets)).

## Why it works

Compaction is a request that sends the whole history plus a summarization instruction. While the cache is warm, "that request reads your prefix from the cache, so a mid-session `/compact` costs a fraction of what the context size suggests and spends most of its time generating the summary." After a longer break, "the summarization request reprocesses the full history as uncached input" ([prompt caching](https://code.claude.com/docs/en/prompt-caching)). Idle compaction moves the shrink step to the last moment the prefix is cheap to read.

Worked example, from the [Opus 5.5 prices](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#pricing) ($4 base input, $8 one-hour cache write, $0.20 cache hit, per million tokens) for an API-key user on a 500K-token conversation. Returning at 70 minutes with no compaction rewrites 500K tokens at $8 per million, which is $4.00. Compacting at about 54 minutes reads the prefix for $0.10, plus the summary output. The docs give no summary size, so that output cost is unknown.

## Version history

- 2.1.286: the behavior appears, with "no opt-out and no warning" ([anthropics/claude-code#98747](https://github.com/anthropics/claude-code/issues/98747)).
- 2.1.290: the `idleCompaction` setting and the threshold variable arrive. On earlier versions, turn off `autoCompactEnabled` to stop it.
- 2.1.299: the changelog entry describes the feature (dated October 14, 2026).

`"idleCompaction": false` in settings.json turns it off, and `DISABLE_AUTO_COMPACT` turns it off along with auto-compaction ([settings reference](https://code.claude.com/docs/en/settings-reference#idlecompaction)).

## When this backfires

- You return between minute 54 and minute 60. The cache was still warm, so compaction lost detail for no saving.
- You never return. The summarization call is spent on a conversation nobody reads.
- The work depends on exact detail. One user had working context replaced by a summary in 7 of about 20 parallel sessions overnight: "the context is the valuable part, and a cache re-read is a cost I'd gladly pay to keep it" ([#98747](https://github.com/anthropics/claude-code/issues/98747)). Another saw compactions at 209K to 783K tokens on a 1M window ([#101616](https://github.com/anthropics/claude-code/issues/101616)).
- Your laptop sleeps at minute 54. The docs require the computer to be awake, so the cache expires with no compaction.
- You rely on hooks. #98747 found no documentation that `PreCompact` fires for idle compaction, and through 2.1.289 the trigger was logged as `manual`, which hid the cause. Version 2.1.290 changed it to `auto`.
- The feature needs feature flags fetched from Anthropic ([settings reference](https://code.claude.com/docs/en/settings-reference#idlecompaction)), so the version number does not tell you whether it is on. One reporter on 2.1.292 guessed "a server-side rollout rather than something introduced in one release" ([#101616](https://github.com/anthropics/claude-code/issues/101616)).

Anthropic says compaction is lossy: "whatever the summary leaves out is no longer in Claude's context" ([sessions](https://code.claude.com/docs/en/sessions#resume-from-a-summary)). A collaborator replied that "we need to get to the place where a compaction is less disruptive" ([#98747](https://github.com/anthropics/claude-code/issues/98747)). The figures here are Claude Code's own.

## Key Takeaways

- Check the five conditions before you expect idle compaction: terminal session, one-hour TTL, feature flags, token threshold, 54 idle minutes with the computer awake.
- API-key and cloud-provider users never see it until they set `promptCacheTtl` to `1h`.
- Keep it for sessions you resume to start new work. Set `"idleCompaction": false` for sessions you resume in full detail.
- The 500K-token example saves about $3.90 minus the summary cost, and only when you return after expiry.

## Related

- [Prompt Cache Keepalive for Agent Pauses](prompt-cache-keepalive-agent-pauses.md) — keep the cache warm instead of shrinking the prefix
- [Prompt Caching: Architectural Discipline for Agents](prompt-caching-architectural-discipline.md) — choosing a TTL by session shape
- [Scoring a Compaction Policy on Latency and Billed Cost](compaction-policy-latency-and-cost.md) — judging a compaction setting by its bill
- [Manual Compaction Strategy for Dumb Zone Mitigation](manual-compaction-dumb-zone-mitigation.md) — compacting at a natural break yourself
