---
title: "Confirmation Gates for Consequential Agent Actions"
description: "Mandatory human confirmation checkpoints before irreversible agent actions to catch injection-driven misbehavior before it causes real harm."
aliases:
  - Confirmation Gates
  - Human-in-the-Loop Approval Gates
tags:
  - agent-design
  - human-factors
---
# Human-in-the-Loop Confirmation Gates for Consequential Agent Actions

> Inject mandatory confirmation checkpoints before irreversible or high-stakes actions so humans can catch injection-driven misbehavior before it causes real harm.

!!! info "Also known as"
    Confirmation Gates, Human-in-the-Loop Approval Gates. For the broader pattern on where and how to place human oversight in agent pipelines, see [Human-in-the-Loop Placement](../workflows/human-in-the-loop.md).

## Why Confirmation Gates Exist

Well-scoped agents with tight instructions can still be successfully injected. A confirmed injection that passes all model-level defenses will proceed unless a human has the opportunity to review the specific action before it's committed.

Confirmation gates turn a fully autonomous failure into a recoverable near-miss. This is the last line of defense in a [defense-in-depth](defense-in-depth-agent-safety.md) approach to agent security. [Source: [Prompt Injections](https://openai.com/index/prompt-injections/)]

## Identifying Consequential Actions

The first design step: enumerate which of your agent's actions are consequential. The common categories:

- **Send**: email, message, notification, form submission
- **Purchase/transact**: payments, subscriptions, API requests with billing implications
- **Delete**: files, records, branches, resources
- **Share**: publishing, permissions changes, external forwarding
- **Modify auth**: credential rotation, permission grants

For each action type, determine: if a successful injection caused this action to be taken, what is the worst-case outcome? Gate the actions where that outcome is unacceptable.

## What to Surface at Confirmation

At confirmation time, show the exact action and exact data — not a summary. Summaries can obscure injection artifacts that are visible in raw form.

For an email action, surface:

- The exact recipient address (not "the requester" — show the email)
- The exact subject and body text
- The exact attachments

An injected email that says "forward to attacker@external.com" is immediately visible when the recipient field is shown verbatim. It may not be visible in a summary that says "forwarding to a contact."

Make it easy to say no. A confirmation UX that buries the rejection option or auto-approves on timeout works against its own purpose. [Source: [Prompt Injections](https://openai.com/index/prompt-injections/)]

## Watch Mode for High-Stakes Contexts

For sensitive contexts (banking, medical records, access control), the confirmation model changes. Rather than approving individual actions at the end, require the user to observe the agent working in real time — "watch mode."

Watch mode means the user sees each tool call as it happens, with the option to pause or abort at any point. This provides higher assurance at the cost of requiring more sustained attention. [Source: [Prompt Injections](https://openai.com/index/prompt-injections/)]

## Logging Confirmed and Rejected Actions

Log all confirmed and rejected actions at the gate with:

- The full action and data
- The timestamp
- Whether it was confirmed or rejected

Anomalous confirmation patterns — unusually high rejection rates, repeated similar rejections, rejections at unusual times — may indicate active attacks or model behavior that the prompt-level defenses missed.

The log is independent of the agent's session transcript, which may be truncated, corrupted, or not retained.

## Placement in the Defense Stack

Confirmation gates are not a substitute for other defenses — they are the last layer in a stack:

1. Narrow task instructions that constrain the action space
2. Least privilege permissions that limit what actions are possible
3. Prompt injection detection or filtering
4. Confirmation gates for the remaining consequential action set

Gates placed too early (gating on every minor action) create alert fatigue. Gates placed at the right level cover the irreversible and high-stakes actions where the cost of a mistake exceeds the cost of the interruption.

## When This Backfires

- **Confirmation fatigue**: High gate frequency causes reviewers to rubber-stamp without evaluation. Adversaries can exploit this deliberately — flooding the approval queue is classified as threat T10 in Rippling's 2025 Agentic AI Security guide. [Source: [The Agent Approval Fatigue Problem](https://molten.bot/blog/agent-approval-fatigue/)]
- **Lies-in-the-Loop attacks**: Injected content manipulates how the confirmation dialog renders — pushing dangerous commands out of view or exploiting Markdown rendering — so the user approves an action that appears safe. Demonstrated against Claude Code and Copilot Chat in 2025. [Source: [Bypassing AI Agent Defenses With Lies-In-The-Loop](https://checkmarx.com/zero-post/bypassing-ai-agent-defenses-with-lies-in-the-loop/)]
- **Headless pipelines**: Background jobs and server-side agents cannot pause for interactive review; gates either block execution or are bypassed by design.
- **Injections that mimic legitimate actions**: A well-crafted injection within normal operating parameters may pass review because it resembles an expected action.

Mitigations: limit gates to the genuinely irreversible subset, constrain dialog rendering, validate that the approved operation matches what was shown, and use out-of-band confirmation for the highest-stakes actions.

## Example

The following Python snippet shows a confirmation gate implemented before an agent sends an email. The gate surfaces the exact recipient, subject, and body — not a summary — so that an injected recipient address is immediately visible.

```python
import sys

def confirm_send_email(to: str, subject: str, body: str) -> bool:
    """Confirmation gate: surfaces exact action data before committing."""
    print("=" * 60)
    print("PENDING ACTION: Send Email")
    print(f"  To      : {to}")
    print(f"  Subject : {subject}")
    print(f"  Body    :\n{body}")
    print("=" * 60)
    answer = input("Confirm send? [y/N]: ").strip().lower()
    return answer == "y"

# Agent-proposed action
recipient = "attacker@external.com"   # ← injection artifact visible verbatim
subject   = "Fwd: Q3 financial model"
body      = "Please find the attached spreadsheet."

if not confirm_send_email(recipient, subject, body):
    print("Action rejected. Aborting.")
    sys.exit(0)

send_email(recipient, subject, body)
```

Because the recipient is shown verbatim, `attacker@external.com` is immediately visible to the reviewer — a summary that said "forwarding to the requester" would have concealed it. The gate defaults to rejection (`[y/N]`), making it easy to say no without extra effort.

## Key Takeaways

- Identify the consequential actions in your agent (send, purchase, delete, share, modify auth) and gate each one
- Surface the exact action and data at confirmation time — summaries can obscure injection artifacts
- Make rejection easy; a UX that defaults to approval undermines the gate's purpose
- Use watch mode for high-sensitivity contexts where action-by-action observation is warranted
- Log all confirmed and rejected actions for audit; anomalous patterns may indicate active attacks

## Related

- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md)
- [Explicit, Narrow Task Instructions to Reduce Injection Susceptibility](task-scope-security-boundary.md)
- [Guarding Against URL-Based Data Exfiltration](url-exfiltration-guard.md)
- [Prompt Injection: A First-Class Threat to Agentic Systems](prompt-injection-threat-model.md)
- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md)
- [Close the Attack-to-Fix Loop](close-attack-to-fix-loop.md)
- [Code Injection Defence in Multi-Agent Pipelines](code-injection-multi-agent-defence.md)
- [Enterprise Agent Hardening](enterprise-agent-hardening.md)
- [Designing Agents to Resist Prompt Injection](prompt-injection-resistant-agent-design.md)
- [Action Selector Pattern](action-selector-pattern.md)
- [Indirect Injection Discovery](indirect-injection-discovery.md)
