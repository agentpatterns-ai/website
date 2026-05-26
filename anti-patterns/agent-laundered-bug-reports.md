---
title: "Agent-Laundered Bug Reports"
description: "Running a bug report through an LLM before filing strips the load-bearing observation and replaces it with speculation that misleads downstream triage."
aliases:
  - slop issues
  - agent-reworded bug reports
tags:
  - anti-pattern
  - workflows
  - human-factors
---

# Agent-Laundered Bug Reports

> Running a human's first-hand bug observation through an LLM before filing strips the load-bearing fact and replaces it with confident speculation that misleads both maintainers and their downstream investigation agents.

## The Pattern

A contributor hits a problem, pastes the symptom into an LLM, and asks it to "write this up as a bug report". The LLM expands the observation into a full-shape report — speculative root cause, fake-minimal repro, suggested fix, analogies to "similar" code, broad lists of error classes that "might" be involved. The four pieces of information the maintainer actually needs — command run, expected outcome, actual outcome, exact error — are buried in agent-generated scaffolding or absent entirely.

Armin Ronacher, working on Pi, named the failure mode in May 2026: "issues that are 5% human and 95% clanker-generated ... typically prompted so badly that the conclusions produced are more often than not inaccurate but always full of confidence" ([Ronacher, 2026](https://lucumr.pocoo.org/2026/5/24/pi-oss/)). The issue looks more polished. It is harder to triage.

## Why It Works

LLMs produce confident, structured, plausible prose at the shape the prompt asks for. Given a short observation and asked for a bug report, the model fills the expected sections — root cause, repro steps, suggested fix — by generating tokens that look like each one. Each section is a hallucination relative to the user's actual evidence, framed in the model's confident voice ([Ronacher, 2026](https://lucumr.pocoo.org/2026/5/24/pi-oss/)).

The harm compounds when the maintainer hands the issue to their own coding agent: "Pi sees the wrong diagnosis too. It does not treat the issue body as a rumor. It treats it as evidence. It will happily go down the path that the issue already prepared for it" ([Ronacher, 2026](https://lucumr.pocoo.org/2026/5/24/pi-oss/)). The hallucination in step one becomes a trusted premise in step two — a [context poisoning](context-poisoning.md) cascade originating in the issue body.

## The Four-Line Format

Ronacher's prescribed mitigation pins the human voice in place ([Ronacher, 2026](https://lucumr.pocoo.org/2026/5/24/pi-oss/)):

1. I ran this command.
2. I expected this to happen.
3. This happened instead.
4. Here is the exact error or log.

Everything else — root cause guess, suggested fix, related-code analogies — goes in a follow-up comment, not the issue body. If the reporter does not know the root cause, they say so. If the only hard fact is one stack trace, the issue contains the stack trace and nothing else. The format leaves the LLM nothing to embellish: no "root cause" field for the model to fill with speculation.

## Example

**Before — agent-laundered with speculation:**

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

**After — four-line observation:**

```markdown
1. I ran `pi session inspect ~/.pi/sessions/2026-05-24-1430.log`
2. I expected the session summary to print.
3. Instead the command exited with status 134 and printed the trace below.
4. Stack trace:

   thread 'main' panicked at 'index out of bounds: the len is 0 but the index is 4'
   src/session/log.rs:182:9
```

The "before" form invents three speculative error classes, asserts a similarity to `BlobReader` the maintainer would have to disprove, and proposes a fix that contradicts the project's actual design ([Ronacher, 2026](https://lucumr.pocoo.org/2026/5/24/pi-oss/)). The "after" form preserves exactly the evidence and nothing else.

## When This Backfires

Stripping LLM assistance from the report is not always net-positive:

- **Non-native speakers and accessibility**: an LLM rewrite that improves clarity without inventing root causes is legitimate — if the submitter reads the output before filing. Treat the LLM as a typesetter, not a co-author.
- **AI bug-finding tooling that has matured**: Greg Kroah-Hartman reported in March 2026 that Linux kernel AI bug reports "went from junk to legit overnight"; one experiment yielded 60 problems with two-thirds correct patches ([The Register, 2026](https://www.theregister.com/2026/03/26/greg_kroahhartman_ai_kernel/)). That applies to AI-authored reports vetted by a skilled researcher — not to human reports laundered through an LLM unsupervised.
- **Issue templates that constrain the rewrite**: required fields ("Command run", "Expected", "Actual", "Error") leave the LLM no room for speculation.

The maintainer-side defence — telling the investigation agent to "not trust analysis written in the issue" — does not fully hold. Ronacher reports the agent still anchors on the issue's confident framing even with that guard in Pi's `/is` command ([Ronacher, 2026](https://lucumr.pocoo.org/2026/5/24/pi-oss/)). The fix has to happen upstream of the maintainer. Independent corroboration of the cost: Daniel Stenberg shut down curl's bug bounty in January 2026 after AI-laundered reports drove confirmed-vulnerability rates from ~1-in-6 down to 1-in-20 ([The Register, 2026](https://www.theregister.com/2026/01/21/curl_ends_bug_bounty/)); Linus Torvalds reported the Linux kernel security list became "almost entirely unmanageable" under similar pressure in May 2026 ([Tom's Hardware, 2026](https://www.tomshardware.com/software/linux/linus-torvalds-says-ai-bug-reports-have-made-the-linux-security-mailing-list-almost-entirely-unmanageable)).

## Key Takeaways

- Running a bug observation through an LLM before filing replaces the load-bearing fact with confident speculation that misleads both the maintainer and any downstream agent
- The maintainer's own investigation agent treats the issue body as evidence, not rumour, even when explicitly instructed otherwise
- Pin the observation in place with a four-line format: command run, expected outcome, actual outcome, exact error — anything else goes in a comment
- The harm is from unsupervised rewriting; LLM assistance is fine when the submitter reads and edits the output before filing

## Related

- [Context Poisoning](context-poisoning.md) — hallucinations in step one become trusted premises in step two; the same mechanic that turns an agent-laundered issue body into a wrong diagnosis
- [Comprehension Debt](comprehension-debt.md) — polished AI output crowds out direct human understanding of the underlying system
- [Continuous Triage](../workflows/continuous-triage.md) — maintainer-side triage workflow this anti-pattern degrades upstream of
- [Backlog Triage Skill](../workflows/backlog-triage-skill.md) — automated inbound-issue routing assumes the issue body is a faithful observation
- [Observation Contract Preservation](../agent-design/observation-contract-preservation.md) — the same discipline applied to tool outputs that downstream tools validate by exact bytes
