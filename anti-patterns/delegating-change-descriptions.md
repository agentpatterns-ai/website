---
title: "Delegating Change Descriptions to the Agent"
term: "Delegated Change Descriptions"
description: "Letting the agent write the whole PR or commit description restates the diff and drops the intent a reviewer needs — keep the why human-authored."
aliases:
  - AI-written change descriptions
  - AI-authored change descriptions
tags:
  - anti-pattern
  - human-factors
  - workflows
  - tool-agnostic
last_reviewed: 2026-07-10
maturity: adopted
---

# Delegating Change Descriptions to the Agent

> Letting the agent write the whole PR or commit description restates the diff and drops the intent a reviewer needs — keep the why human-authored.

Handing the agent the entire change description is a false economy. A model that writes a PR or commit message from the diff can only restate what the diff already shows. It has no channel to the intent behind the change, which is the context a reviewer relies on most. So keep the description human-authored even when the code is agent-written: the agent may draft what changed, but why it changed has to come from you.

Kenton Varda put a moratorium on AI-written change descriptions across his team after finding them "worse than useless" for review — "outlining details of the code that could easily be seen by looking at the code, but omitting the higher-level framing needed to understand broadly what the code is doing" ([Simon Willison, quoting Kenton Varda](https://simonwillison.net/2026/Jul/8/kenton-varda/)). The output looks thorough, which is why teams reach for it, but thorough diff-restatement adds length without adding intent.

This differs from [PR description style as a lever](../code-review/pr-description-style-lever.md), which tunes description structure to raise merge rates. That is about how the description is shaped; this is about what you must not delegate. As agents author more code, the change description becomes one of the few places human intent survives the handoff to a reviewer ([zknill](https://zknill.io/posts/commit-message-intent/)).

## Why the diff can't carry intent

Rationale is private information. It lives in your head, or once in the originating issue or prompt, and it never enters the diff. A model conditioned only on the diff can restate the diff and nothing more, so it fills the description with fluent summary that reads as complete but tells a reviewer nothing new. The split works because the two halves have different sources: what changed is recoverable from the diff and safe to draft, while why it changed must be supplied by the human.

The cost is measurable, not cosmetic. In a study of 23,247 agent-authored pull requests, those whose descriptions diverged from the code were accepted 28.3% of the time against 80.0% for aligned descriptions, and took 55.8 hours to review against 16.0 — a 3.5-times increase — after controlling for code complexity ([arXiv:2601.04886](https://arxiv.org/abs/2601.04886)). Reviewers lean on the description to judge a change, so one that carries no intent slows the judgment and erodes trust.

## When this backfires

The rule to keep descriptions human-authored is not absolute. Full AI drafting is fine, and insisting on a human-written why is ceremony, in these cases:

- Mechanical, low-intent changes — dependency bumps, lockfile updates, formatting-only diffs — where the reason is self-evident and there is no why to convey.
- Solo or inner-source repos with no external reviewer, where the only reader of the description already holds the intent.
- High-throughput autonomous pipelines, where a per-PR human-authored mandate reinstates the human bottleneck the automation removed; capture intent once at the originating issue instead.

The structure of an AI-drafted description still helps: structured, agent-produced descriptions correlate with higher reviewer engagement and merge rates ([arXiv:2602.17084](https://arxiv.org/abs/2602.17084)). The fix is not to ban the agent from the description, but to source the why from the human and let the agent draft the what.

## Example

**Before — description restates the diff, drops the why:**

```markdown
## Summary
- Added a `retries` parameter to `fetch_config()`
- Wrapped the request in a `for` loop with exponential backoff
- Updated three call sites to pass `retries=3`
```

A reviewer can read all of this from the diff. Nothing explains why retries were needed.

**After — human supplies intent, agent may draft the change list:**

```markdown
## Why
Config fetches were failing intermittently during deploys when the
config service restarts, taking down unrelated jobs. This adds bounded
retries so a transient restart no longer fails the whole run.

## What changed
- `retries` parameter on `fetch_config()`, default 3, exponential backoff
- Call sites updated to opt in
```

## Key Takeaways

- A description written from the diff can only restate the diff; intent is off-diff information the model never receives.
- Keep the why human-authored even when the code is agent-written — the agent may draft what changed.
- Unfaithful descriptions drop PR acceptance from 80.0% to 28.3% and triple review time in a 23,247-PR study ([arXiv:2601.04886](https://arxiv.org/abs/2601.04886)).
- Full AI drafting is fine for mechanical changes, solo repos, and high-volume pipelines where intent is self-evident or captured upstream.

## Related

- [PR Description Style as a Lever for Agent PR Merge Rates](../code-review/pr-description-style-lever.md) — tuning description structure for merge rate, distinct from what not to delegate
- [Author-to-Reviewer Role Inversion in AI-Assisted Teams](../human/author-to-reviewer-role-inversion.md) — why the description is where intent crosses the human-to-reviewer boundary
- [Comprehension Debt](comprehension-debt.md) — the understanding gap that widens when intent is not written down
- [Agent-Laundered Bug Reports](agent-laundered-bug-reports.md) — a sibling failure where an LLM pass strips the load-bearing human observation
