---
title: "Unattended Run Reporting: What the One Message Must Say"
term: "Unattended Run Reporting Contract"
description: "An unattended agent run needs a reporting contract: unreadable versus empty, quiet versus failed, posted versus maybe posted, and a cap at 3 to 5 times normal cost."
tags:
  - workflows
  - agent-design
  - claude
aliases:
  - unattended agent reporting
  - failing well when nobody is watching
  - agent automation reporting rules
last_reviewed: 2026-10-09
maturity: emerging
---

# Unattended Run Reporting: What the One Message Must Say

> An unattended run's posted message is the only output a human sees, so it must tell apart every state the run can end in.

An unattended agent run needs a reporting contract. The contract fixes which run states the destination message must distinguish and when the run may move its own state forward. Anthropic's reference build of a weekday Slack and GitHub "daily brief" on Claude Managed Agents states the design goal directly: "Most of the design is about failing well when nobody is watching" ([daily-brief README](https://github.com/anthropics/claude-quickstarts/tree/main/managed-agents/daily-brief)).

The contract applies when the run has a human reader at the end and the task is well defined enough to write its bookkeeping down. It does not cover which tasks belong on a schedule. The source post does not answer that question, and this page does not put an answer in Anthropic's mouth. For trigger choice, see [Loop Trigger Selection](../loop-engineering/loop-trigger-selection.md).

## The silent-run problem

The post opens on the failure it targets: agent automations "can lose access to a source without anyone noticing or fail to follow our preferences" ([Building effective agent automations](https://claude.dev/blog/building-effective-agent-automations/)). A run that starts on schedule and posts a tidy message can still be wrong, because the reader has no way to see what the agent could not do.

## The post's six rules

The post by Lance Martin and CJ Avilla (2026-10-08) closes with six rules ([claude.dev](https://claude.dev/blog/building-effective-agent-automations/)):

1. Read each source from a bookmark, not a fixed time window.
2. Report a failed read as unreadable, never as a quiet day.
3. Re-check every item right before posting.
4. Count a post as sent only when Slack confirms it, then update bookmarks and ledger.
5. Re-read your preferences every run, from a store the agent cannot edit.
6. Give the agent read-only access wherever it only reads, and cap what each run can spend.

The rules carry no platform terms. The controls that enforce them in the reference build (vault credentials, mounted memory stores, `budget_reached`, deployment run records) belong to Managed Agents. No source checked for this page shows equivalents in Copilot or Cursor automations, so treat the rules as portable and the controls as one platform's implementation.

## What the message must distinguish

Each rule makes the destination carry one more state.

### Unreadable versus empty

A missing source looks like an empty one. In the reference build, if an MCP server is down or its token has expired, "the run still starts, just without that server's tools", and the agent reports "nothing new" because it sees nothing from that source. The prescribed behavior is to keep that source's bookmark where it is, write the brief from the other sources, and end it with one line naming what it could not read ([claude.dev](https://claude.dev/blog/building-effective-agent-automations/)).

Slack adds a second trap. It answers HTTP 200 whether or not a call worked, so a response counts only if its body says `"ok": true` ([agent.md](https://github.com/anthropics/claude-quickstarts/blob/main/managed-agents/daily-brief/agents/daily-brief/agent.md)).

### Deliberate quiet day versus failure

Silence must be a decision the run records. Step 6 of agent.md reads: "If there is nothing to report and every source was read, say so in one line; if the preferences allow silence, post nothing and go to step 8 as a deliberate quiet day" ([agent.md](https://github.com/anthropics/claude-quickstarts/blob/main/managed-agents/daily-brief/agents/daily-brief/agent.md)).

### Posted versus maybe posted

The post counts as sent only if Slack returns `"ok": true` and a message timestamp. The agent updates the ledger and bookmarks only after that confirmation. If the result is unclear, it marks the run "maybe posted" and changes nothing else ([claude.dev](https://claude.dev/blog/building-effective-agent-automations/)). Both wrong guesses cost something. If the agent records a post that never landed, "the bookmarks move on and those items are never reported." If it posts again out of doubt, readers get the same brief twice.

### Bookmark and ledger instead of a time window

A fixed window such as "the last 24 hours" leaves a gap after a late run and repeats items after an early one ([claude.dev](https://claude.dev/blog/building-effective-agent-automations/)). Lateness is normal. Managed Agents applies jitter of up to 15% of the interval between runs, with a maximum of 9 minutes, and skips wall-clock times that do not exist on a spring-forward day ([scheduled deployments](https://platform.claude.com/docs/en/managed-agents/scheduled-deployments)). The reference build reads each source from ten minutes before its bookmark and skips any item whose ID is already in the ledger with an unchanged state ([agent.md](https://github.com/anthropics/claude-quickstarts/blob/main/managed-agents/daily-brief/agents/daily-brief/agent.md)).

## The number to set: a cap at 3 to 5 times a normal run

The post gives one figure a reader can act on: "Start at three to five times the cost of a normal run, then tighten it as you see real numbers" ([claude.dev](https://claude.dev/blog/building-effective-agent-automations/)). In the authors' tests a busy day cost about $1.50 on Claude Opus 5 and about $1.00 on Claude Sonnet 5, and a run that found every source unreadable cost $0.15 to $0.30. The shipped cap is $5.00 per run. The README notes the tests ran before the default model moved to Claude Sonnet 5.5, so remeasure on your own model ([README](https://github.com/anthropics/claude-quickstarts/tree/main/managed-agents/daily-brief)).

A run that hits its cap pauses instead of failing, so a cap set too low "looks like a brief that went quiet." The cap can also overshoot by one request: a session capped at 50 cents can pause with a cost of 53 ([Managed Agents budgets](https://platform.claude.com/docs/en/managed-agents/budgets)).

## Why it works

An unattended run has one human-facing output, the destination message. Any state that message cannot show is lost. The post names the concrete paths: a down server removes tools without stopping the run, Slack returns 200 on failure, and a capped run goes quiet ([claude.dev](https://claude.dev/blog/building-effective-agent-automations/)). Each rule adds one state to the message and ties the agent's own bookkeeping to what reached the reader, so a retry neither loses items nor repeats them.

An independent study of a production system found the same pattern. Over eight weeks it documented 22 incidents. In them the LLM "actively transforms the error into fluent, plausible narrative content delivered to the user", a behavior the authors call fail-plausible ([arXiv 2606.14589v1](https://arxiv.org/abs/2606.14589v1)). That is one system, so read it as support for the premise and not as a rate.

## When this backfires

- Platform-level silence. A budget pause and a failed trigger both produce nothing in the channel, and the agent cannot report either. The README says to "check the deployment's runs in the Console if a brief goes missing" ([README](https://github.com/anthropics/claude-quickstarts/tree/main/managed-agents/daily-brief)). Triggers fail when an environment resource is archived or session creation is rate limited, and each attempt writes a deployment run record ([scheduled deployments](https://platform.claude.com/docs/en/managed-agents/scheduled-deployments)). Monitor those records from outside the agent.
- Prompt rules guarding against the model's own blindness. Rules 2 and 4 depend on the same model noticing the failure, and the fail-plausible finding says it may not. Prefer platform signals where you have them.
- A destination with no confirmation signal, such as email or a webhook that returns 200 regardless. The "posted only on confirmation" rule has nothing to read, so every run ends as "maybe posted."
- An outage followed by a bookmark read. The window then covers every missed day in one run, which raises context and cost and can hit the cap, which pauses the run silently.
- Rare-signal tasks. A run that finds every source unreadable still costs $0.15 to $0.30 ([README](https://github.com/anthropics/claude-quickstarts/tree/main/managed-agents/daily-brief)). For a check that rarely finds anything, a deterministic poll plus a notification costs less.
- Code could own the bookkeeping. A short script can store a high-water mark, check Slack's `ok` field, write the ledger, and exit non-zero on an auth error, which an existing cron monitor already catches. The model then handles only selection and summary. Anthropic's earlier guidance favors this split for well-defined tasks: workflows "offer predictability and consistency for well-defined tasks" ([Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)). The reference build keeps the bookkeeping in prompt instructions, and the README concedes the destination restriction "is a prompt rule."

## Credentials replace approval gates

No one is present to approve a tool call. MCP toolsets default to `always_ask`, and "an unattended run would wait for ever on an approval nobody gives", so the read-only GitHub token is what keeps the run safe ([agent.md](https://github.com/anthropics/claude-quickstarts/blob/main/managed-agents/daily-brief/agents/daily-brief/agent.md)). The post states the limit: "A planted instruction can still change what the brief says, including through the notes the agent keeps between runs. It can't write to GitHub or edit your rules" ([claude.dev](https://claude.dev/blog/building-effective-agent-automations/)).

## Key Takeaways

- The posted message is the contract. It must separate unreadable from empty, quiet from failed, and posted from maybe posted.
- Move bookmarks and the ledger only after the destination confirms the post.
- Start the per-run cap at 3 to 5 times a normal run, and expect a low cap to look like silence.
- The in-agent rules cannot see a budget pause or a failed trigger. Watch deployment run records from outside.
- Where the task is well defined, consider moving the bookkeeping into code and leaving selection to the model.

## Related

- [Run Status vs Task Status Confusion](../patterns/anti-patterns/run-status-vs-task-status-confusion.md)
- [Silent-Failure Mechanism Taxonomy](../patterns/anti-patterns/silent-failure-mechanism-taxonomy.md)
- [Loop Trigger Selection](../loop-engineering/loop-trigger-selection.md)
- [Cloud-Scheduled Routines vs Local Session Scheduling](../tools/claude/cloud-scheduled-routines.md)
- [Continuous AI](continuous-ai.md)
