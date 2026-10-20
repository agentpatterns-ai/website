---
title: "Agent Justification as Allow-Rule Scope"
term: "Justification-Read Approval"
description: "A saved allow-rule grants whatever its text matches, not what the agent said it was for. Adversarial repository content elicited the target rule in 58% of instances across Codex CLI and Claude Code."
tags:
  - anti-pattern
  - security
  - tool-agnostic
  - arxiv
aliases:
  - justification-read approval
  - agent-proposed allow rule
  - elicited allow-rule scope
last_reviewed: 2026-10-19
maturity: emerging
---

# Agent Justification as Allow-Rule Scope

> A saved allow-rule grants whatever its text matches, and the justification shown beside it at the prompt bounds nothing.

Three conditions bound this:

- the harness offers reusable allow-rules derived from the agent's own proposed action,
- a human is at the prompt deciding,
- and the repository carries content the agent reads and somebody else can write.

Inside those bounds a justification-read approval goes wrong quietly. The reason gets read as the scope of the request. The rule text is what the harness will enforce.

## What the saved rule matches

The harness checks membership in the authorized set and asks for approval when the action misses, "without assessing the action's intent" ([arXiv 2610.22987v1, §2](https://arxiv.org/abs/2610.22987v1)). The grant is therefore bounded by the rule's match set and by nothing the agent said.

That match set comes out of the command string, and on Claude Code one space decides it: `Bash(ls *)` "requires a space after `ls`, so `lsof` doesn't match. `Bash(ls*)` has no space, so it matches `lsof` too" ([Claude Code permissions](https://code.claude.com/docs/en/permissions)). The same reference says the dialog writes that space-separated form when you choose not to be asked again for a command prefix. One compound command can save up to five rules.

A broad rule is also never the benign task's idea. The unmodified repository produced no rule request at all, 0 of 25 on every configuration tested, "confirming permissions are never organically proposed" ([arXiv 2610.22987v1, §4.2](https://arxiv.org/abs/2610.22987v1)).

## Why it works

Repository content steers which command the agent reaches for, and the harness derives the rule from that command. An iterative attacker framework elicited the target rule in 58% of instances across four configurations of Codex CLI and Claude Code. The acquired rules covered 56.9% of category-specific capability test cases ([arXiv 2610.22987v1, abstract](https://arxiv.org/abs/2610.22987v1)). Conditional on approval, 47 of 58 eligible instances reached verified silent goal completion.

That figure took optimization, not one planted sentence. An overt injected demand for the same permission reached 6 of 25 cases on claude-haiku-4.5 and 1 of 25 on claude-sonnet-5. The framework reached 14 and 9 ([arXiv 2610.22987v1, §4.2](https://arxiv.org/abs/2610.22987v1)).

The lever differs by harness. Although the two present similar dialogs, the paper found that "their harnesses generalize authority along orthogonal dimensions" ([arXiv 2610.22987v1, §5.1](https://arxiv.org/abs/2610.22987v1)). Codex widens on action diversity across a workflow. Claude Code "abstracts over static command syntax: an unquoted parameter such as curl reports -v induces the broad wildcard rule curl reports *, whereas minor lexical perturbations (e.g., quoting) collapse the rule back to an exact match".

Telling the agent an action matters does not get it run. A base instruction fired in 0 of 3 runs and narrative framing in 1 of 3. A gate that blocked progress without the target's output fired in all 3 ([arXiv 2610.22987v1, §5.2](https://arxiv.org/abs/2610.22987v1)). So the command carrying the rule request arrives as an ordinary step in the work you asked for.

## When this backfires

- A headless or CI run has no dialog to steer and no agent-proposed rule to widen, because the policy is already in config.
- An administrator's ask rule outranks any saved grant, so there the scrutiny duplicates a control that already holds. See [non-retirable approval rules](../../security/non-retirable-approval-rules.md).
- Against the strongest model tested the acquired rule was not the path used. On claude-sonnet-5, 3 of 9 goal-reachable cases completed, all "achieved via alternative authorized pathways without direct prefix matching" ([arXiv 2610.22987v1, §4.3](https://arxiv.org/abs/2610.22987v1)). Reading the rule text would have stopped none of them.
- Refusing to save rules is the wrong correction. Anthropic reported that "as of June 2026, 49.5% of active Claude Code CLI users had manually configured a Bash allow rule" ([arXiv 2610.22987v1, §2.1](https://arxiv.org/abs/2610.22987v1)). Take the artifact away and people reach for a bypass mode, which grants more and records nothing.
- Some of the measured breadth is version-specific. Claude Code's current reference keeps exec wrappers such as `watch` out of prefix approval, and will not let `Bash(find *)` approve `-exec` or `-delete` ([Claude Code permissions](https://code.claude.com/docs/en/permissions)). Check your harness version, not the paper's.

## Example

The paper's own pair of commands shows how little has to change.

**Before** — the agent proposes an unquoted argument:

```
curl reports -v
```

Approving that saves `Bash(curl reports *)`, which covers every later `curl reports` command whatever flags follow, including ones that write. A justification about fetching the dataset the build step expects describes this one call accurately and says nothing about the rest.

**After** — the argument is quoted:

```
curl "reports" -v
```

Quoting is one of the "minor lexical perturbations" that "collapse the rule back to an exact match" ([arXiv 2610.22987v1, §5.1](https://arxiv.org/abs/2610.22987v1)), so the stored rule authorizes that command rather than a prefix.

## Key Takeaways

- Read the rule text at the prompt and work out what it matches. The reason beside it is not part of what the harness stores.
- A rule request arriving during a routine task is itself a signal. The benign task proposed none, 0 of 25 per configuration.
- Narrow against your harness's own axis: quote arguments on a syntax-driven harness, keep one call shape on a history-driven one.
- Check how many rules one approval writes. On Claude Code a compound command can save five.
- Narrowing the rule is cheap and shallow. What the action can reach after approval is a sandbox question, so pair it with [blast-radius containment](../../security/blast-radius-containment.md).

## Related

- [Scoped-Looking Permission Grants](scoped-looking-permission-grants.md) — the same rule read too generously once it exists, where this page covers how its text got chosen
- [Approval Records That Bind No Identity and No Session](unbound-approval-records.md) — the other axis the stored rule leaves open, which principal and which session may satisfy it
- [Self-Justification as a Tool-Scope Control](self-justification-as-scope-control.md) — the agent justifying its own calls as an internal filter, measured and found to be the wrong stage
- [Authority Confusion From Untrusted Context](../../security/authority-confusion-untrusted-context.md) — separating who suggested an action from who authorized it, at dispatch rather than at the dialog
- [Evidence-Based Allowlist Auto-Discovery](../../security/evidence-based-allowlist-auto-discovery.md) — growing an allowlist from real approvals, which this page is the direct caveat on
