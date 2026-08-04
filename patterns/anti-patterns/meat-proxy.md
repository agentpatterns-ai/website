---
title: "The Meat Proxy: Relaying Agent Output Without Reading It"
term: "Meat Proxy"
description: "A meat proxy forwards agent output to a colleague unread, so the receiver inherits the verification the sender skipped and cannot tell what was checked."
aliases:
  - meat proxying
  - AI relay without review
tags:
  - anti-pattern
  - human-factors
  - tool-agnostic
last_reviewed: 2026-08-04
maturity: emerging
---

# The Meat Proxy: Relaying Agent Output Without Reading It

> A meat proxy forwards agent output to a colleague without reading it, so the verification cost lands downstream under a human name.

A meat proxy pastes an agent's answer to a colleague — in Slack, under a pull request, in a group chat — without reading, understanding, or validating it first. Niklas Gruhn coined the term in August 2026 for people who "blindly copy and paste the output of AI systems to their peers" ([Willison, 2026](https://simonwillison.net/2026/Aug/3/dont-be-a-meat-proxy/)). The failure is the unread relay rather than the verbatim quote: forwarding a stack trace or an exact command is often what the receiver asked for.

## What it looks like

Gruhn's account is first-hand: he asks a question in Slack or leaves feedback under a merge request and gets back "Claude said: [giant response verbatim]" ([Gruhn, 2026](https://gruhn.me/blog/2026-08-03/)). He could prompt the model himself, faster, with context he controls.

The code-review version is sharper. Paste the ticket into a coding agent, never read the generated code, paste reviewer feedback back in, iterate until it merges. "That works. But who has done the implementation? The reviewers did, using Claude Code, and you as a meat proxy" ([Gruhn, 2026](https://gruhn.me/blog/2026-08-03/)).

## Why it works

The relay does not remove verification work. It moves that work downstream and adds a false signal that some of it already happened. Generation got cheap while verification did not, which leaves verification as the binding, human-limited stage ([SRLabs, 2026](https://srlabs.de/blog/ai-verification-bottleneck)). Because output under a colleague's name gives no indication of what was checked, the safe response is to check all of it, with worse context than the sender had.

That transferred cost is measurable. A September 2025 survey of 1,150 full-time US desk workers by BetterUp Labs and the Stanford Social Media Lab found 40% had received "workslop" — polished AI output that lacks substance — in the previous month, at roughly two hours per incident and about $186 per employee per month ([BetterUp Labs and Stanford Social Media Lab](https://www.betterup.com/workslop)).

## When this backfires

Gruhn's corrective is to "read it, understand it, validate it, and then write a response in your own words" ([Gruhn, 2026](https://gruhn.me/blog/2026-08-03/)). That rule is narrower than it sounds. Three cases make applying it worse than the relay:

- Verbatim is the payload. A stack trace, an exact command, a generated diff, an API signature, or a quoted citation has to travel unaltered.
- The receiver asked for the model's output. "What does Claude say about this?" requests the artifact, not a gloss on it.
- Automated handoffs. Agent pipelines relay structured output verbatim by design, and a human paraphrase in the middle is lossy.

The corrective is also cheap to fake. Paraphrasing without validating produces text with no AI label and a human byline, harder to discount than a tagged verbatim relay. Across 13 preregistered experiments, Schilke and Reimann found that disclosing AI use lowers trust in the discloser, mediated by perceived legitimacy ([Schilke and Reimann, 2025](https://www.sciencedirect.com/science/article/pii/S0749597825000172)). The incentive runs toward hiding provenance, so enforce validation rather than prose style: a review gate or a required-evidence field does that, a politeness norm does not.

## Example

Gruhn reports receiving this line, relayed to him verbatim from Claude ([Gruhn, 2026](https://gruhn.me/blog/2026-08-03/)):

> NATS control-plane events: stream leader election / R3 quorum re-form during pod churn.

His reaction: "Jesus. I had to lookup almost every word to make sense of this."

**Before** — the relay. The sender pastes the sentence. It may well be correct, but it is dense and detached from the question that was asked. The receiver now does the lookup the sender skipped, with no way to tell whether the sender confirmed that the sentence applies here at all.

**After** — the certificate. The sender does the lookup first, then writes: "The NATS cluster loses its stream leader when pods churn, and a three-replica quorum has to re-form before writes resume. That is the pause we are seeing." The content is the same, and the sentence itself now demonstrates that the sender understood it.

## Key Takeaways

- A meat proxy forwards agent output to a colleague without reading it; the receiver inherits the skipped verification, plus a human byline that conceals which parts were checked.
- Verification, not generation, is the human-limited stage, so an unread relay relocates the shortage rather than easing it ([SRLabs, 2026](https://srlabs.de/blog/ai-verification-bottleneck)).
- The receiver-side cost is measured: 40% of 1,150 surveyed US desk workers received AI "workslop" in a month, at roughly two hours per incident and $186 per employee per month ([BetterUp Labs and Stanford Social Media Lab](https://www.betterup.com/workslop)).
- Relaying verbatim is correct when the artifact is the point — stack traces, exact commands, agent-to-agent handoffs, or a direct request for the model's output.
- Enforce validation rather than prose style: an unvalidated paraphrase hides its provenance, and disclosure carries a measured trust penalty ([Schilke and Reimann, 2025](https://www.sciencedirect.com/science/article/pii/S0749597825000172)).

## Related

- [Agent-Laundered Bug Reports](agent-laundered-bug-reports.md) — the mirror direction, where a human observation is expanded by an LLM before filing rather than model output forwarded untouched
- [Comprehension Debt](comprehension-debt.md) — what unread output does to the person who accepted it, rather than to the colleague who receives it
- [Author-to-Reviewer Role Inversion in AI-Assisted Teams](../../human/author-to-reviewer-role-inversion.md) — the staffing shift that puts the receiver on the expensive side of every relay
- [Delegating Change Descriptions to the Agent](delegating-change-descriptions.md) — the same handoff failure inside a pull request description
- [Trust Without Verify](trust-without-verify.md) — accepting polished agent output as correct, the reflex that makes an unread relay feel safe to send
