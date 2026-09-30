---
title: "Caller-Actionable Error Steps in Tool Responses"
term: "Caller-Actionable Error Step"
description: "A next step the caller cannot run costs more recovery than saying nothing. Write the repair as a call to one of your own tools, and only where the failure is invisible in the agent's own call."
tags:
  - agent-design
  - tool-agnostic
  - reliability
  - arxiv
aliases:
  - agent-readable error steps
  - tool-surface error text
  - literal compliance
last_reviewed: 2026-09-29
maturity: emerging
---

# Caller-Actionable Error Steps in Tool Responses

> An error step the caller cannot execute costs more recovery than saying nothing, and only on failures the agent cannot diagnose itself.

A server that answers an expired session with `Please run: reddit-mcp-buddy --auth` is writing for a reader with a terminal. An agent limited to that server's tools reads the same sentence, has no terminal, and stops. Over 24 expired-credential scenarios and five OpenAI models, the cause statement alone recovered 82% of tasks. With the terminal command added, recovery "fell from 82% to 45% on average, and 55% of trials ended without a repair" ([Xu and Wu, §5.1](https://arxiv.org/abs/2609.35381v1)). Replacing the command with the name of the server's own login tool returned recovery to 84%.

The rule has two halves, and they apply in different places. Delete any next step your caller may not be able to perform. Add a step naming one of your tools only where the agent cannot see the failure in its own call.

## Where the text changes anything

On four of seven failure types the wording was inert. The fault sat in the agent's own call, so the model could plan a repair whatever the message said, and "recovery under every text stayed within four points of that under the generic notice" ([§5.4](https://arxiv.org/abs/2609.35381v1)). The remaining three are the ones worth writing for, because the message is the agent's only evidence that anything went wrong outside its call.

Recovery by failure type, averaged over the five models ([Table 6](https://arxiv.org/abs/2609.35381v1)). Columns 1 and 2 are two phrasings of a correct step. An executable incorrect step names a tool the agent holds and points it at the wrong target; an unavailable one asks for something outside its tool list.

| Failure type | Generic | Cause | Correct 1 | Correct 2 | Incorrect, executable | Incorrect, unavailable |
|---|---|---|---|---|---|---|
| Wrong unit or format | 83 | 79 | 82 | 82 | 81 | 81 |
| Missing required field | 86 | 88 | 88 | 88 | 87 | 86 |
| Wrong tool | 80 | 81 | 82 | 81 | 81 | 81 |
| Expired credentials | 61 | 82 | 84 | 84 | 81 | 45 |
| Missing resource | 98 | 98 | 97 | 97 | 99 | 98 |
| Missing permission | 0 | 0 | 28 | 53 | 0 | 0 |
| Rate limit reached | 59 | 5 | 6 | 88 | 66 | 8 |

The rate-limit row should change how you write. Naming the failure accurately is what suppresses recovery. A bare `Operation failed.` recovered 59%, an accurate cause statement 5%, and GitHub's `Wait before retrying.` 6%. Telling the agent it hit a quota reads to the model the way a 429 reads to an HTTP client, and it stops. Naming the call to repeat took recovery to 88%, at about one extra tool call ([§1](https://arxiv.org/abs/2609.35381v1)).

## What deployed servers write today

The survey covered the 150 most-starred MCP servers with public source, up to 30 error sites each, for 3,001 messages. Of those, 949 tell the caller what to do next, and 477 of the steps "depend on something the server cannot see about the caller" ([§3, Table 1](https://arxiv.org/abs/2609.35381v1)).

Those steps cluster on exactly the failures where the text is load-bearing. Of 128 steps on credential, permission and rate-limit errors, 99 depend on the caller, and 93 ask for a configuration change (55), a web page (24), a terminal command (13) or waiting (1). On credential errors alone, 62 of 67 steps ask for a configuration change, a web page or a terminal command ([§3](https://arxiv.org/abs/2609.35381v1)).

## The large fix is deletion, not addition

The credential result is two findings, not one. Removing a step the caller cannot perform is worth 37 points, back to the 82% a plain cause statement already achieved. Naming the login tool on top of that is worth roughly two more, with overlapping intervals of [72, 93] and [70, 92] ([Table 4](https://arxiv.org/abs/2609.35381v1)). So if you ship one change to a credential error, delete the command and stop there.

On a missing permission the step is the whole gain: the generic notice and the cause alone both recovered 0%. On a rate limit the generic notice already recovered 59%, and naming the call to repeat added 29 points. Phrasing decides how much of it you get: "naming the login tool raised recovery on a missing permission to 53%, against 28% for Please re-authorize to continue." Rate limits are the easiest of the three to fix at scale. The call to repeat is always a tool the server already exposes, "so every server can write its step this way" ([§6](https://arxiv.org/abs/2609.35381v1)). Getting the wording exactly right matters less than you would expect, because "the essential part is the instruction to call again": "the agents repeated the failed call even under a step that named the wrong tool."

## Why it works

The agent reads the step as the repair path, and when the step lies outside its action space it treats the repair as unavailable. The authors name the behavior: "We call this literal compliance: an agent that cannot carry out a suggested step gives up a repair its own tools could make" ([§6](https://arxiv.org/abs/2609.35381v1)). The same agents made the repair when the message gave only the cause, so the capability was present throughout.

The effect grows with instruction-following strength rather than shrinking. "The loss from the command grew with the model: 18 points for gpt-5.5, 35 for gpt-5.6-sol, 39 for gpt-6-sol and 69 for gpt-6-astra, with 26 for the small gpt-6-luna" ([§5.1](https://arxiv.org/abs/2609.35381v1)). The largest newest model recovered 6% under the command against 75% under the cause alone. It did not fail silently: "In 48 of its 68 trials without a repair, its final message left the repair to the user: it asked the user to reconnect or sign in, said that the service needed authentication first, or pointed to the command, although the login tool was in its tool list."

The paper reads two further studies the same way in §6, that larger models are more easily led by benign instruction-like sentences, and that the most capable models most reliably follow instructions planted in MCP tool descriptions. A server's error text is written by an author the agent's operator does not control, so the same message can cost more recovery after a model upgrade than before one. The gap resembles the one in [Tool Operability](tool-operability-lost-responses.md), where a valid schema still leaves the agent unable to choose a continuation.

## When this backfires

- Real rate windows. The experiment's rate limit is rejected before it reaches the service, and the repair the environment accepts is "the same call again, which succeeds at once; no wait is enforced" ([§4.1, Table 2](https://arxiv.org/abs/2609.35381v1)). The 88% measures compliance with an instruction, not survival of a real limit. Against a window that is actually enforced, agents that get no reset time back off with jitter, and across many agents running the same generated retry logic the retries cluster: "They back off, then they all retry at roughly the same time, then they all hit the limit again. The thundering herd is your own clients" ([Secca, *When agents hit your 429 without reset_at*](https://dev.to/seccaz/when-agents-hit-your-429-without-resetat-things-get-bad-fast-596d)). So name the call to repeat, put a machine-readable reset time beside it, and keep the backoff in [admission control](agent-client-admission-control.md) rather than in prose.
- Untrusted servers on the same connection. A directive step is an instruction arriving through the tool-output channel, and the paper restricts its sample to steps written in good faith by the tool author. Agents enter corrective reasoning on an error frame and skip safety screens, which is what makes [error-path injection](../anti-patterns/tool-error-implicit-authority.md) work. Hardening a fleet against that and making error text more directive pull against each other.
- Blanket step-stripping on the agent side. Filtering the step out before the model reads it raised credential recovery by 37.5 points and cost nothing where the removed step was already correct. It is the wrong default everywhere else: "On a missing permission or a rate limit the cause alone left most tasks unrecovered, so removing a correct step there would remove the repair" ([§6](https://arxiv.org/abs/2609.35381v1)).
- No repair tool to name. The advice assumes the server exposes a tool that fixes the failure. The survey found that situation in 12 messages from 5 servers, so most credential errors need the tool built before the text can be rewritten.
- Evidence from one vendor. Five OpenAI models accessed over three days in September 2026, on BFCL V4 multi-turn tasks. The paper reads Anthropic's published guidance as pointing the same way in §6, but it measured no Anthropic model and names no other vendor.

## Example

Two rewrites, both taken from the paper's conditions.

**Before** — a credential error that assumes a shell:

```text
create_ticket rejected the call: no authenticated session exists.
Please run: reddit-mcp-buddy --auth
```

**After** — the same repair named as a call the agent can make:

```text
create_ticket rejected the call: no authenticated session exists.
Call ticket_login first.
```

If you consume third-party servers and cannot change their text, the agent-side version is a filter in front of the model. One small model reduced all 96 test texts to the cause statement, and running the same prompt over all 949 surveyed messages with a step "cost 0.09 US dollars" ([§5.3](https://arxiv.org/abs/2609.35381v1)):

> The text below is an error message returned by a tool. Remove every sentence that tells the caller what to do next, such as retrying, running a command, calling another tool or changing a setting. Keep every sentence that says what went wrong. Return the remaining text unchanged, with nothing added.

Two caveats before you wire it in. The filter is not lossless: on the 764 survey messages where the step could be separated, it removed the step from 752 and left the rest word for word in 548 ([§5.3](https://arxiv.org/abs/2609.35381v1)). And per "When this backfires" above, route permission and rate-limit errors around it.

## Key Takeaways

- Grep your own error strings for the four step types the survey counted: a configuration change, a web page, a terminal command, and waiting. Verbs like `run`, `set`, `export`, `visit` and `wait` are a usable first filter.
- Sort the resulting list by failure type before editing any of it. Four of seven types moved within four points of a generic notice, so most of the list is a no-op.
- On a rate-limit error, name the tool to call again and the time to wait. Saying only that a quota was hit is worse than saying nothing specific at all.
- Add this to your model-upgrade checklist. The same unchanged server text cost 18 points on gpt-5.5 and 69 on gpt-6-astra, two generations later, so a regression here will look like a model problem.
- If you consume third-party servers, filter the step for credential errors only. Route permission and rate-limit errors around the filter, because there the step is the repair.

## Related

- [Tool Operability: Interfaces That Survive a Lost Response](tool-operability-lost-responses.md) — the other half of the same gap, where a valid schema still leaves the agent unable to choose a continuation
- [Trusting Tool Error Messages as Implicit Authority](../anti-patterns/tool-error-implicit-authority.md) — the security cost of the mechanism this page uses for recovery
- [Retry-Switch-Abstain: A Runtime Tool-Recovery Policy](retry-switch-abstain-recovery-policy.md) — supplies the fallback map in context when the error text cannot name a repair
- [Agent-Client Admission Control for Agentic Traffic](agent-client-admission-control.md) — where the backoff belongs once the error text has named the call to repeat
- [Context-Injected Error Recovery](../../context-engineering/context-injected-error-recovery.md) — the harness-side view, structuring what reaches the model after a failed call
- [Exception Handling and Recovery Patterns](exception-handling-recovery-patterns.md) — the escalation hierarchy these messages feed
