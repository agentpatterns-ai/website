---
title: "Per-Call Egress Confirmation for User-Identifying Values"
term: "Per-Call Egress Confirmation"
description: "A host allowlist approves the request and never the payload. Claude Code 2.1.317 added a check that asks before a web or shell call sends the user's account email out."
aliases:
  - value-keyed egress check
  - payload-level egress confirmation
  - per-call identity egress prompt
tags:
  - security
  - agent-design
  - claude
applies_to: "claude-code@2.x"
last_reviewed: 2026-11-03
maturity: emerging
---

# Per-Call Egress Confirmation for User-Identifying Values

> A per-call egress confirmation matches an outbound call's arguments against values the harness knows identify the user, then asks before the call goes out.

Claude Code 2.1.317 shipped one on 3 November 2026: "Added a check that asks before a web or shell tool call sends your account email address to the network" ([Claude Code changelog](https://code.claude.com/docs/en/changelog#2-1-317)). A host-only rule leaves the payload unrestricted. Claude Code also supports exact-command rules and wildcard rules; their coverage depends on the pattern ([permission rules](https://code.claude.com/docs/en/permissions#permission-rule-syntax)).

## Conditions that make it worth the interruption

Use these conditions to assess where a per-call check adds to [a destination rule](agent-network-egress-policy.md).

- The harness already holds the value. Claude Code already emits the account email as a telemetry attribute: it "Added `user.email` and `user.groups` to the telemetry Claude Desktop and Cowork send through a Claude apps gateway, matching terminal sessions" ([Claude Code changelog](https://code.claude.com/docs/en/changelog#2-1-265)). That provides a known value to check. The changelog does not specify the matching algorithm.
- The destination is already approved. Check whether that approval also constrains the payload.
- Somebody can answer during the run. A prompt nobody sees is no control.

## Why it works

A standing permission rule can cover many calls. Claude Code documents host-specific WebFetch rules and Bash patterns whose wildcards match arbitrary text ([permission rules](https://code.claude.com/docs/en/permissions#permission-rule-syntax)). A host-only rule cannot distinguish two payloads sent to that host. A separate per-call check can ask about the data leaving in each call.

The content exists only once the argument is written, which is the earliest a check can read it. CaMeL gives the general form: it "uses a notion of a capability to prevent the exfiltration of private data over unauthorized data flows by enforcing security policies when tools are called" ([Debenedetti et al., arXiv:2503.18813v2](https://arxiv.org/abs/2503.18813v2)). The Claude Code changelog documents an email-specific prompt. It does not establish whether the check uses literal matching or provenance tracking.

Claude Code shipped the advisory version of this rule first. Version 2.1.234, on 17 August 2026, said "Claude is now told to use your account email only to identify you, and not to send it to unrelated services unless you ask" ([Claude Code changelog](https://code.claude.com/docs/en/changelog#2-1-234)). The per-call check followed 78 days later. [The two classes of control](enforced-versus-advisory-controls.md) are not interchangeable.

## When this backfires

- Literal matching alone would miss a value split across requests. On a different surface, months before this check, Anthropic restricted Claude's `web_fetch` to "exact URLs that the user has entered themselves or that were returned from its companion `web_search` tool", and Ayush Paul still got identity out. Their honeypot told the agent "you'll need to navigate through the website letter by letter to find the user's profile", and "They were able to extract the user's name, home location city and the name of their employer" ([Simon Willison, 15 July 2026](https://simonwillison.net/2026/Jul/15/claude-web-fetch-exfiltration/)). The sequence encoded the value across requests. This illustrates a limit of whole-value matching, not a tested bypass of the later Claude Code check. Encoded values also challenge [checks that must recognize the secret in outbound bytes](framing-gap-exfiltration-defenses.md).
- Warning design affects user response. Akhawe and Felt used browser telemetry "to observe over 25 million warning impressions in situ". Users bypassed "a tenth of Mozilla Firefox's malware and phishing warnings". Chrome SSL warnings were the exception: users "continued through 70.2% of Google Chrome's SSL warnings". The authors conclude that warnings can work and attribute variation to the warning's user experience ([USENIX Security 2013](https://www.usenix.org/conference/usenixsecurity13/technical-sessions/presentation/akhawe)). These browser results do not measure agent prompts or establish a prompt-frequency effect.
- Headless runs have nobody to ask. A scheduled agent either stops at the prompt or answers it automatically, and an automatic answer is a log line. [Confirmation gates](human-in-the-loop-confirmation-gates.md) share this limit.
- Stronger data-flow enforcement can reduce task completion. CaMeL's full data-flow version completed 77% of AgentDojo tasks with provable security, against 84% for an undefended system ([arXiv:2503.18813v2](https://arxiv.org/abs/2503.18813v2)). Those results measure CaMeL, not the Claude Code email check; they do not establish its capability cost.
- Documented coverage is narrow. The [2.1.317 entry](https://code.claude.com/docs/en/changelog#2-1-317) names the account email. It makes no coverage claim for session tokens, machine names, or repo paths. Do not treat an unprompted call as proof that its payload is safe.

## Example

This schematic example assumes a host-only allowlist and a separate literal email check. It does not specify Claude Code's matching algorithm:

```bash
# Host and binary are both on the allowlist
curl https://api.example.com/v1/status

# Same approval, same host; the argument now carries the user's identity
curl "https://api.example.com/v1/register?contact=alice@corp.com"
```

A host-keyed rule returns the same verdict for both, because the host did not change. A value-keyed check reads the second argument, finds the account email it stores, and stops to ask.

## Key Takeaways

- Gate the argument, not only the destination, where the harness already stores the value a call might carry.
- Revisit documented coverage whenever the harness gains a new identity attribute.
- Test whether users understand the prompt and reject unwanted disclosures. Measure prompt frequency separately; the browser study does not establish its effect.
- Keep a destination rule underneath it. A literal payload match alone does not cover split or encoded values.
- Treat the control as unmeasured. The changelog states the behavior and gives no figure for how often the check fires.

## Related

- [Guarding Against URL-Based Data Exfiltration in Agentic Workflows](url-exfiltration-guard.md)
- [Agent Network Egress Policy: Admin-Controlled Domain Allow/Deny](agent-network-egress-policy.md)
- [Human-in-the-Loop Confirmation Gates for Consequential Agent Actions](human-in-the-loop-confirmation-gates.md)
- [Enforced Versus Advisory Controls in LLM-Native IDEs](enforced-versus-advisory-controls.md)
- [Control/Data-Flow Separation for Prompt Injection Defense (CaMeL)](camel-control-data-flow-injection.md)
