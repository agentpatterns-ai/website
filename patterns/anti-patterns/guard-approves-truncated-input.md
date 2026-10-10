---
title: "A Guard Hook Approves the Truncated Input It Was Handed"
term: "Truncated-Input Approval"
description: "A policy gate handed a silently cut input rules on the fragment, and the harness applies the verdict to the whole call. Error-triggered fail-closed switches never fire."
tags:
  - anti-pattern
  - agent-design
  - testing-verification
  - claude
aliases:
  - guard approves truncated input
  - silent input truncation in a guard
  - fail-open on partial input
last_reviewed: 2026-10-09
maturity: emerging
---

# A Guard Hook Approves the Truncated Input It Was Handed

> A policy gate that receives a cut-short input rules on the fragment, and the harness applies the verdict to the whole call.

A guard approves when its rules find no match in the input it received. When that input was silently cut, "no match" covers two cases: clean content, and content the guard never saw. The approve path cannot tell them apart unless something outside the inspected content says the input is partial.

Claude Code 2.1.295 (2026-10-08) fixed one instance. Its changelog reads: "Fixed a mod's hook being handed a deeply nested tool input cut short with no error, so a guard could pass content it never saw" ([Claude Code changelog](https://code.claude.com/docs/en/changelog)). Mods are plugins that arrived in 2.1.287 ("Added Claude Mods: plugins may now modify deeper behavior"), and the entry does not mention settings `PreToolUse` command hooks. The fix is dated and narrow. The defect class is not.

## When it applies

The pattern matters when all of these hold:

- The hook or gate makes a policy decision: it allows or denies the call. A formatter, logger, or cost-tracking hook that works on a cut input does little harm.
- The agent, or an attacker steering it, controls the size or nesting depth of the input.
- The harness gives the guard no completeness signal, or the guard does not check the one it has.
- No later layer, such as a sandbox, a deny rule, or egress control, already blocks the dangerous outcome.

## How it differs from a truncated rules file

[Graceful Tool Output Truncation](../../tool-engineering/graceful-tool-output-truncation.md) covers the rules: for security-critical reads, a silently truncated rules file is the same as a missing rules file. This page covers the other input. The subject being judged is cut while the rules are intact. A team that applied the rules-file guidance still has this hole.

## Why the usual fail-closed controls miss it

Each fail-closed control a reader already knows triggers on an error.

- A settings command hook that exits with code 1 is a non-blocking error, and the hooks reference says: "If your hook is meant to enforce a policy, use `exit 2`." ([Claude Code hooks](https://code.claude.com/docs/en/hooks)).
- Claude Code 2.1.295 added `onFailure: "block"`, so a command or HTTP hook that cannot start, times out, or exits with an unexpected code blocks the action ([Claude Code changelog](https://code.claude.com/docs/en/changelog)).
- A mod hook that fails is skipped. The docs tell the author to add a `.catch` error handler to fail closed ([React to events with a mod](https://code.claude.com/docs/en/plugins/mods/events)). That handler fires on a throw, a timeout, or a wrong-shaped answer.

A hook handed a truncated input does none of those things. It starts, finishes in time, and returns a well-formed allow. That is why the changelog names "no error" as the defect.

Claude Code marks some of its own cuts. It middle-truncates long `PostToolUseFailure` error strings around a `... [N characters truncated] ...` marker ([Claude Code hooks](https://code.claude.com/docs/en/hooks)). A marked cut gives the hook something to act on. The 2.1.295 cut gave nothing.

The changelog does not say what replaced the silent cut. The mods reference documents no limit on tool-input depth or size and no truncation signal on the event input ([mods reference](https://code.claude.com/docs/en/plugins/mods/reference)). Whether Claude Code now passes the full input, raises an error, or denies is undocumented, so a guard author cannot assume any of the three.

## The same shape outside agents

AWS WAF inspects only a prefix of a request body. For Application Load Balancer the prefix is the first 8 KB. For CloudFront and API Gateway it is the first 16 KB by default, adjustable up to 64 KB. With the `Continue` option, "AWS WAF will inspect the request component contents that are within the size limits." Outside the console, `Continue` is the default ([AWS WAF oversize components](https://docs.aws.amazon.com/waf/latest/developerguide/waf-oversize-request-components.html)).

Attackers use this. The nowafpls Burp plugin pads a request with junk data, because of this behavior: "When the request is padded with this junk data, the WAF will process up to X kb of the request and analyze it, but everything after the limits of the WAF will pass straight through." ([assetnote/nowafpls](https://github.com/assetnote/nowafpls)). The payload goes after the cut.

AWS differs from the Claude Code case in one way. It documents the limit and gives each rule an oversize-handling choice, and it recommends blocking requests that go over the limit ([AWS WAF oversize components](https://docs.aws.amazon.com/waf/latest/developerguide/waf-oversize-request-components.html)).

A review bot that reads a pull request through the GitHub REST API sits in between. The files endpoint caps the list at 3000 files and returns 30 per page by default ([GitHub REST: pulls](https://docs.github.com/en/rest/pulls/pulls)). The pull request object also carries a `changed_files` count, so the bot has a completeness check available. A bot that never compares that count with the files it read has the same hole. Commit diffs can drop content too: "Diffs with binary data will have no patch property." ([GitHub REST: commits](https://docs.github.com/en/rest/commits/commits)).

CWE-636 names the general weakness, falling back to a less secure state on an error ([CWE-636](https://cwe.mitre.org/data/definitions/636.html)). Silent truncation is a step worse. No error condition exists, so there is nothing to fail closed on.

## Guard against it

1. Compare a count or size the harness reports with what the guard received, wherever the harness reports one. The pull request `changed_files` field is an example. If the two differ, deny.
2. Where the harness gives no completeness signal, measure the input before ruling. Refuse any input nested or sized beyond the depth the guard was tested at.
3. Add an independent check at a lower layer, such as a sandbox or a deny rule, so a blind guard does not decide alone. This matters most when the cut happens before the guard runs, because a depth check inside the guard then sees a shallower object and passes it.
4. Build the test case at the cut depth. A working guard and a half-blind guard both return "allow" on the benign majority of calls, so sampled traffic cannot separate them. Construct a payload nested past the point where truncation begins and assert that the guard denies it.
5. Give legitimate large inputs an explicit allow path, for example a narrow rule for a known generator that writes big files.

## Why it works

An approve path that has only a match test cannot separate "inspected and clean" from "inspected the part that fit". AWS WAF shows the mechanism: under `Continue` it inspects the contents within the size limits, and the rule's verdict then applies to the whole request ([AWS WAF oversize components](https://docs.aws.amazon.com/waf/latest/developerguide/waf-oversize-request-components.html)). The attacker controls input size, so they can place the payload beyond the cut, and nowafpls automates that ([assetnote/nowafpls](https://github.com/assetnote/nowafpls)). A reported count, or a size or depth precheck, adds the missing information to the decision, so the guard can deny on partial input instead of ruling on it. The cause inside Claude Code, such as a serialization limit at a worker boundary, is undocumented.

## When this backfires

Denying on partial input has a price, and both AWS and Claude Code made it opt-in.

- A guard that denies every large legitimate payload stalls the agent. Examples are a big `Write`, a long multi-file edit, and a deeply nested MCP argument. Users then switch the guard off, which removes its coverage on the calls it handled well. AWS tells operators to add rules that explicitly allow only the legitimate oversize requests ([AWS WAF oversize components](https://docs.aws.amazon.com/waf/latest/developerguide/waf-oversize-request-components.html)). Without that allow path, the fix costs more than the hole.
- Claude Code proceeds by default on most hook errors and makes the fail-closed path (`exit 2`, `onFailure: "block"`) opt-in ([Claude Code hooks](https://code.claude.com/docs/en/hooks)). For a formatter or a logging mod, letting a cut input through is the right call.
- When a sandbox or an OS-level control already blocks the dangerous outcome, a second fail-closed guard adds false positives and no new coverage.
- Where the harness cuts silently and offers no signal, as mods did before 2.1.295, advice to check completeness does nothing from inside the hook. Only an independent lower-layer check helps.

The research found no source that argues for approving partial input as a security choice. The objections concern availability cost.

## Key Takeaways

- A gate handed a cut input cannot tell "clean" from "never seen" unless the harness marks the input as partial.
- `exit 2`, `onFailure: "block"`, and a mod `.catch` all trigger on errors, so silent truncation passes them.
- Claude Code 2.1.295 fixed the mods case without documenting the replacement behavior, so do not assume it now errors.
- Test at the cut depth. Sampled traffic passes both a working guard and a blind one.
- Fail closed only on guards that make policy decisions, and give large legitimate inputs an explicit allow path.

## Related

- [Graceful Tool Output Truncation](../../tool-engineering/graceful-tool-output-truncation.md)
- [Enforcing Agent Behavior with Hooks](../../instructions/enforcing-agent-behavior-with-hooks.md)
- [Decoding Harness Attack Surface](../../security/decoding-harness-attack-surface.md)
- [Parser Versus Shell Permission Evasion](../../security/parser-versus-shell-permission-evasion.md)
- [Hostname Allowlist TLS Blind Spot](../../security/hostname-allowlist-tls-blind-spot.md)
- [Approval Records That Bind No Identity and No Session](unbound-approval-records.md)
