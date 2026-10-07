---
title: "Attributing a Changed Tool Call to the Model (Intent-Execution Correspondence)"
term: "Intent-Execution Correspondence"
description: "A hop between the model and the shell can rewrite a correct command. The trajectory holds only the text the model sent, so the failure gets filed against the model."
tags:
  - anti-pattern
  - tool-agnostic
  - arxiv
aliases:
  - intent-execution correspondence
  - changed tool call attribution
  - tool call rewritten before execution
last_reviewed: 2026-10-06
maturity: emerging
---

# Attributing a Changed Tool Call to the Model (Intent-Execution Correspondence)

> A hop between the model and the shell can rewrite a correct command, and the trajectory holds only the text the model sent.

One condition decides whether this applies to you. A command passed to a non-interactive shell as a single argument arrives as written: on Linux, Yang et al. recorded no change across "all 1,779 calls of 4 harnesses, 4,012 calls of 9 developers, and 161,214 held-out Codex calls" ([arXiv:2610.04375v1](https://arxiv.org/abs/2610.04375v1)). Calls change where something handles the text first: a Windows host wrapper, a layer typing into an interactive shell, a harness that splits and rejoins the command, or `/bin/sh` resolving to dash ([arXiv:2610.04375v1](https://arxiv.org/abs/2610.04375v1)).

## The trap

Where that condition holds, the harness rewrites correct commands and the tool result says nothing. Through Claude Code's Bash launch on Windows, "12.0% of the 7,491 exposed Bash calls change", where exposed means a heredoc, a backslash pair, or at least 1,000 characters ([arXiv:2610.04375v1](https://arxiv.org/abs/2610.04375v1)). The wrapper merges backslash pairs, and "the wrong action runs without any reported error for 535 of the 663 such calls that ran before IntAct" ([arXiv:2610.04375v1](https://arxiv.org/abs/2610.04375v1)). Anthropic's own tracker carries the mechanism as an open bug ([anthropics/claude-code#98733](https://github.com/anthropics/claude-code/issues/98733)).

Misattribution is what costs you engineering time. A judge reading the trajectory sees the agent's command and an error naming that command, so it files the failure against the model. On 102 human-labeled production failures, 56 of them caused by the path, "the all-at-once judge attributes 97 of the 102 failures to the LLM" ([arXiv:2610.04375v1](https://arxiv.org/abs/2610.04375v1)). The agent misreads its own run the same way, reporting 665 of 949 failed runs as completed, "a false-confirmation rate of 70.1%" ([arXiv:2610.04375v1](https://arxiv.org/abs/2610.04375v1)).

## Why it works

A hop changes a call by parsing its text, so more escaping cannot fix it. "More quotes or escapes only move the change to the next parse, whereas an unparsed channel leaves the hop nothing to change" ([arXiv:2610.04375v1](https://arxiv.org/abs/2610.04375v1)). The repair is therefore a change of channel: a file the shell sources, an argument vector, or standard input. The paper's Claude Code mod sources a file for any command over 200 characters or carrying a heredoc or backslash pair, at a median 4 ms per call ([arXiv:2610.04375v1](https://arxiv.org/abs/2610.04375v1)). The bug reporter does the same by hand with the Write tool.

Fixing the attribution needs no new tooling. Re-parse the text you sent, with execution disabled, using the interpreter that receives it: "Text that does not parse was incorrect when emitted, a generation error" ([arXiv:2610.04375v1](https://arxiv.org/abs/2610.04375v1)). Text that parses and still errors points at the path, not the model.

## When this backfires

- Your harness hands the command to a non-interactive shell as one argument. That is the measured zero-change case, so hardening the channel buys nothing.
- The call is not exposed: no heredoc, no backslash pair, under 1,000 characters. Of those calls, "in the replay no Bash call outside this set changes" ([arXiv:2610.04375v1](https://arxiv.org/abs/2610.04375v1)), so routing all of them through a file buys a cost and no correctness. The released forms "add 2.1 to 396 ms per call" ([arXiv:2610.04375v1](https://arxiv.org/abs/2610.04375v1)).
- The change lands at the target parser, where no channel helps. Of 30 injected changes, "IntAct restores every call of the first 4 hops and refuses the 13 at the target parser" ([arXiv:2610.04375v1](https://arxiv.org/abs/2610.04375v1)). For those 13 the whole fix is refusing the call.
- The rewrite sits upstream of your permission check. "A repair that rewrites a call must leave the harness's permission rules judging the original call, as the mod does" ([arXiv:2610.04375v1](https://arxiv.org/abs/2610.04375v1)). Rewrite before the allowlist and you have moved a security boundary.
- You reach for the prompt-level fix, where the two studies disagree. QuoteBench found that disclosing the boundary recovers 30.4 to 60.7 points for six of eight configurations ([arXiv:2608.13547v1](https://arxiv.org/abs/2608.13547v1)); the correspondence measurement recorded one model falling "from 50 pairs to 36" under a disclosed boundary ([arXiv:2610.04375v1](https://arxiv.org/abs/2610.04375v1)). Measure it on your own path first.

## Example

The bug report gives a reproduction on Windows with Git Bash ([anthropics/claude-code#98733](https://github.com/anthropics/claude-code/issues/98733)). The transcript records two and four backslashes; `od` shows what bash received.

**Before — the shell receives half the backslashes:**

```bash
printf '%s\n' 'two:a\\b' 'four:a\\\\b' | od -c
# 0000000   t   w   o   :   a   \   b  \n   f   o   u   r   :   a   \   \
# 0000020   b  \n
```

Single quotes do not help, and neither does a quoted heredoc: "This happens even inside single quotes and inside a quoted heredoc" ([anthropics/claude-code#98733](https://github.com/anthropics/claude-code/issues/98733)). The reporter's fix changes the channel instead of the escaping.

**After — the content goes through the file tools:**

```text
Write  t.txt   content: two:a\\b
Read   t.txt   two backslashes, as sent
```

"The Write tool is not affected: the same content written with Write keeps every backslash" ([anthropics/claude-code#98733](https://github.com/anthropics/claude-code/issues/98733)).

## Key Takeaways

- Ask what your harness does to the command text before the shell sees it. On Terminal-Bench reference solutions written for Bash, dash stops 5 at `set -o pipefail`, and "zsh, the default shell of macOS, silently changes 5" ([arXiv:2610.04375v1](https://arxiv.org/abs/2610.04375v1)).
- A shell failure in a trajectory is not evidence about the model. Re-parse the sent text with the receiving interpreter before you tune a prompt or swap a model.
- Retries hide the cost rather than removing it. In the production sessions each path-caused call that finally succeeded cost "3.9 times the tokens of one clean request" ([arXiv:2610.04375v1](https://arxiv.org/abs/2610.04375v1)).
- When no channel can carry a call, refusing it beats running a different action, because the silent case gives the agent nothing to notice.

## Related

- [Rewriting a CLI Into a JSON Payload for Agents](cli-json-payload-rewrite.md) — names the shell-escaping tax as a measured cost driver; this page covers what that escaping does to a call in transit.
- [Permission Modes as a Defense Against a Tampered Response Path (Response-Path Control Gap)](response-path-control-gap.md) — the same seam under a hostile router rather than an unmodified harness.
- [Destructive-Failure Mechanism Attribution by Mitigation Owner (ClayBuddy Three)](destructive-failure-mechanism-attribution.md) — routes a failure to its mitigation owner; a changed call is the harness-error bucket with a concrete discriminator.
- [Verify-Gated Completion as Admission Control](../multi-agent/verify-gated-completion-admission-control.md) — a read-only check on the completion claim, which is what a 70.1% false-confirmation rate argues for.
- [Unix CLI as the Native Tool Interface for AI Agents](../../tool-engineering/unix-cli-native-tool-interface.md) — the single `run(command)` design whose reliability depends on the launch underneath it.
