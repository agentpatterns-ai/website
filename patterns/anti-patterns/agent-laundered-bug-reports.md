---
title: "Agent-Laundered Bug Reports"
description: "Running a bug report through an LLM before filing strips the load-bearing observation and replaces it with speculation that misleads downstream triage."
term: "Agent-Laundered Bug Reports"
aliases:
  - slop issues
  - agent-reworded bug reports
tags:
  - anti-pattern
  - workflows
  - human-factors
  - tool-agnostic
last_reviewed: 2026-06-12
maturity: established
---

# Agent-Laundered Bug Reports

> An agent-laundered bug report runs a first-hand observation through an LLM before filing, swapping the load-bearing fact for confident speculation that misleads maintainers.

## The pattern

A contributor pastes a symptom into an LLM and asks it to "write this up as a bug report". The LLM expands it into a full report — a speculative root cause, a fake-minimal repro, a suggested fix, and error classes that "might" be involved. The four pieces the maintainer needs are buried or missing.

Armin Ronacher named the failure mode in May 2026: "issues that are 5% human and 95% clanker-generated ... typically prompted so badly that the conclusions produced are more often than not inaccurate but always full of confidence" ([Ronacher, 2026](https://lucumr.pocoo.org/2026/5/24/pi-oss/)). The result looks polished and is harder to triage.

## Why it works

LLMs produce confident, plausible prose in the shape the prompt asks for. Asked for a bug report, the model fills the expected sections with tokens that look the part. Each token is a hallucination next to the user's actual evidence ([Ronacher, 2026](https://lucumr.pocoo.org/2026/5/24/pi-oss/)).

The harm compounds when the maintainer hands the issue to their coding agent: "It does not treat the issue body as a rumor. It treats it as evidence" and "will happily go down the path that the issue already prepared for it" ([Ronacher, 2026](https://lucumr.pocoo.org/2026/5/24/pi-oss/)). The step-one hallucination becomes a trusted step-two premise — a [context poisoning](context-poisoning.md) cascade.

## The four-line format

Ronacher's fix pins the human voice in place ([Ronacher, 2026](https://lucumr.pocoo.org/2026/5/24/pi-oss/)):

1. I ran this command.
2. I expected this to happen.
3. This happened instead.
4. Here is the exact error or log — pasted verbatim, like the `src/session/log.rs:182:9` trace in the example below.

Everything else — the root-cause guess, the suggested fix, related-code analogies — goes in a follow-up comment, not the issue body. The format leaves the LLM no "root cause" field to fill, the field [Ronacher, 2026](https://lucumr.pocoo.org/2026/5/24/pi-oss/) shows it otherwise stuffs with confident speculation.

## Example

Before — agent-laundered with speculation:

```markdown
## Bug: SessionLog reader crashes on malformed input

### Root Cause Analysis
The crash appears to stem from a missing defensive check in `SessionLog::read_record()`.
Similar patterns in `BlobReader` use a try/except guard around the deserialization
path. The reader may also be vulnerable to several other error classes:
- UTF-8 decode failures on legacy logs
- Integer overflow in length-prefixed frames
- Pointer aliasing in the mmap path

### Suggested Fix
Add a tolerant reader that catches deserialization errors and returns a Result type.

### Repro (minimal)
Create a session log with a truncated header and attempt to read it.
```

After — four-line observation:

```markdown
1. I ran `pi session inspect ~/.pi/sessions/2026-05-24-1430.log`
2. I expected the session summary to print.
3. Instead the command exited with status 134 and printed the trace below.
4. Stack trace:

   thread 'main' panicked at 'index out of bounds: the len is 0 but the index is 4'
   src/session/log.rs:182:9
```

The "before" form invents three error classes, asserts a `BlobReader` similarity the maintainer must disprove, and proposes a fix that contradicts the project's design ([Ronacher, 2026](https://lucumr.pocoo.org/2026/5/24/pi-oss/)). The "after" form keeps the evidence and nothing else.

## When this backfires

Stripping LLM assistance is not always net-positive:

- Accessibility and non-native speakers: an LLM rewrite that improves clarity without inventing root causes is legitimate — if the submitter reads the output before filing. Treat the LLM as a typesetter, not a co-author.
- Matured AI bug-finding tooling: Greg Kroah-Hartman reported in March 2026 that Linux kernel AI bug reports "went from junk to legit overnight"; one experiment yielded 60 problems with two-thirds correct patches ([The Register, 2026](https://www.theregister.com/2026/03/26/greg_kroahhartman_ai_kernel/)). That applies to AI-authored reports vetted by a skilled researcher — not to human reports laundered unsupervised.
- Constraining issue templates: required fields ("Command run", "Expected", "Actual", "Error") leave the LLM no room for speculation.

The maintainer-side defense — telling the agent to "not trust analysis written in the issue" — does not fully hold; Ronacher reports the agent still anchors on the issue's framing even with that guard in Pi's `/is` command ([Ronacher, 2026](https://lucumr.pocoo.org/2026/5/24/pi-oss/)). Daniel Stenberg shut down curl's bug bounty in January 2026 after AI-laundered reports drove confirmed-vulnerability rates from about 1-in-6 to 1-in-20 ([The Register, 2026](https://www.theregister.com/2026/01/21/curl_ends_bug_bounty/)); Linus Torvalds called the kernel security list "almost entirely unmanageable" in May 2026 ([Tom's Hardware, 2026](https://www.tomshardware.com/software/linux/linus-torvalds-says-ai-bug-reports-have-made-the-linux-security-mailing-list-almost-entirely-unmanageable)).

## Key Takeaways

- Laundering an observation through an LLM swaps the load-bearing fact for confident speculation that misleads the maintainer and any downstream agent
- The maintainer's investigation agent treats the issue body as evidence, not rumour, even when told otherwise
- Pin the observation with a four-line format — command, expected, actual, exact error — and put everything else in a comment
- The harm is unsupervised rewriting; LLM assistance is fine when the submitter reads and edits the output first

## Related

- [Context Poisoning](context-poisoning.md) — hallucinations in step one become trusted premises in step two; the same mechanic that turns an agent-laundered issue body into a wrong diagnosis
- [Comprehension Debt](comprehension-debt.md) — polished AI output crowds out direct human understanding of the underlying system
- [Continuous Triage](../../workflows/continuous-triage.md) — maintainer-side triage workflow this anti-pattern degrades upstream of
- [Backlog Triage Skill](../../workflows/backlog-triage-skill.md) — automated inbound-issue routing assumes the issue body is a faithful observation
- [Observation Contract Preservation](../agent-design/observation-contract-preservation.md) — the same discipline applied to tool outputs that downstream tools validate by exact bytes
- [The Meat Proxy: Relaying Agent Output Without Reading It](meat-proxy.md) — the opposite direction of the same handoff: model output forwarded to a human untouched, instead of a human observation expanded by a model
