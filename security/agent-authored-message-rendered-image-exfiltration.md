---
title: "Agent-Authored Messages as a Deferred Exfiltration Channel"
description: "An auto-fetching renderer downstream of an agent's message-authoring tool acts as deferred egress, closing the lethal trifecta without any direct network grant."
aliases:
  - rendered image exfiltration
  - agent-authored message exfiltration
  - composite-tool egress
tags:
  - security
  - agent-design
  - tool-agnostic
  - long-form
last_reviewed: 2026-06-12
maturity: established
---

# Agent-Authored Messages as a Deferred Exfiltration Channel

> An auto-fetching renderer downstream of an agent's authoring tool acts as deferred egress — closing the lethal trifecta without a network grant.

An agent without a network tool is not a closed-egress agent. If it can author messages on a surface whose renderer auto-fetches external resources, the renderer performs egress on the user's behalf. The lethal trifecta closes through *composition*, not a single tool grant.

## The Composite-Egress Mechanism

The lethal trifecta normally treats external communication as a tool the agent invokes directly ([Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md)). The agent-authored-message pattern manufactures the third leg by chaining two non-egress tools:

1. The agent invokes an internal "send message" tool with no network access of its own.
2. The message embeds external resource references (markdown images, `<img>` tags, link previews).
3. A downstream renderer — email client, chat surface, feed UI — auto-fetches them when a user or scheduled task opens the message.
4. The attacker's server logs the request and any data in the query string.

This matches [URL Exfiltration Guard](url-exfiltration-guard.md) — the URL carries the data — except the renderer performs the fetch, not the agent process.

## The Copilot Cowork Incident

PromptArmor disclosed this composition against Microsoft Copilot Cowork on 26 May 2026 ([PromptArmor disclosure](https://www.promptarmor.com/resources/microsoft-copilot-cowork-exfiltrates-files)). Cowork's documentation says sensitive actions like sending emails or Teams messages require user approval, but when the recipient is the active user they execute without approval — and users cannot change that behaviour.

The attack chain:

1. A user uploads a skill file carrying prompt injection (skills load automatically from a specific OneDrive path).
2. A routine "summarise what I worked on this week" query triggers the skill.
3. The injection makes the agent post a Teams message with HTML `<img>` tags whose `src` attributes are attacker URLs carrying OneDrive pre-authenticated download links in the query string.
4. Opening the message fetches the images, leaking the download links to the attacker, who then visits them and downloads the files. ([PromptArmor disclosure](https://www.promptarmor.com/resources/microsoft-copilot-cowork-exfiltrates-files))

PromptArmor reported 5/5 attack success across both Claude Opus 4.7 and the auto-routing model selector, the injection comprising only 5 of 81 lines in the skill file ([PromptArmor disclosure](https://www.promptarmor.com/resources/microsoft-copilot-cowork-exfiltrates-files)).

## Why It Works

The mechanism is the composition rule, not a single bug. PromptArmor states it directly: *"Because these messages can contain external images that trigger network requests to external websites, data can be exfiltrated when a user opens a compromised message sent by the agent"* ([PromptArmor disclosure](https://www.promptarmor.com/resources/microsoft-copilot-cowork-exfiltrates-files)). The fetch primitive that lets a recipient see an embedded chart becomes an exfiltration leg when the author is an LLM responding to attacker-controlled content.

The OneDrive pre-authenticated download link amplifies the impact from beacon to file content: a leaked URL is not a tracking pixel but a working download credential anyone can use, turning leaked metadata into a leaked file.

The same composition appeared in 2025 against Microsoft 365 Copilot as EchoLeak (CVE-2025-32711), where reference-style markdown images survived Copilot's link-redaction safeguards and the renderer auto-fetched them ([Aim Labs / arxiv](https://arxiv.org/abs/2509.10540); [The Hacker News](https://thehackernews.com/2025/06/zero-click-ai-vulnerability-exposes.html)). Microsoft shipped server-side fixes by May 2025 and documents HTML image injection as a defence-in-depth target ([Microsoft MSRC](https://www.microsoft.com/en-us/msrc/blog/2025/07/how-microsoft-defends-against-indirect-prompt-injection-attacks)) — yet Cowork shows the same leg reappearing on a different M365 surface 13 months later.

## Defences

Three controls compose into a defence in depth:

| Control | Layer | What it does |
|---------|-------|--------------|
| Strip or rewrite external resource references at write time | Agent | Remove `<img src="…">`, markdown `![]()` references, and link previews before content is persisted |
| Gate resource fetches on explicit user intent | Renderer | Default to "do not load remote images" — match email-client norms for untrusted senders |
| Restrict the data amplifier | Data source | Block download links at the storage layer; for SharePoint, `Set-SPOSite -Identity <site> -BlockDownloadPolicy $true` removes the pre-authenticated download surface ([PromptArmor disclosure](https://www.promptarmor.com/resources/microsoft-copilot-cowork-exfiltrates-files)) |

The two controls are orthogonal. The agent-side control is brittle — pattern matching misses redirect chains, data URLs, CSS background images, and `srcset` permutations. The renderer-side control matches the email-client default and has a smaller policy surface, so teams owning both surfaces should apply both. Microsoft lists deterministic blocking of HTML image injection as a defence layer ([Microsoft Learn](https://learn.microsoft.com/en-us/security/zero-trust/sfi/defend-indirect-prompt-injection)) — but Cowork shows it must be applied per surface: agent-authored Teams messages are distinct from email arrivals Copilot processes.

## When This Backfires

The defence work is wasted when the composition is already closed by another leg:

- **Trusted-by-design recipients**: if the only consumer is an operator on a plain-text inbox, no renderer auto-fetches resources and the exfil leg does not exist.
- **No private-data context**: an agent with untrusted input and an authoring tool but no sensitive corpora has nothing worth exfiltrating — the trifecta is broken at leg 1.
- **Markdown-aware LLM consumers**: when the consumer is another LLM that ingests markdown without auto-fetching resources, the renderer leg is closed by the consumer's nature.
- **Renderer outside your authority**: when another vendor owns the renderer and you cannot force it to gate fetches, write-time stripping degrades into brittle pattern matching — a tactical patch with residual risk.

Scheduled tasks compound the surface: a "weekly review" task that loads a poisoned skill exfiltrates on every run without oversight ([PromptArmor disclosure](https://www.promptarmor.com/resources/microsoft-copilot-cowork-exfiltrates-files)). Treat any recurring agent-authored message workflow as a higher-priority audit target.

## Audit Checklist

For any agent that can write to a user-facing surface, four "Yes" answers mean the composite-egress leg is open:

1. Read access to private data (SharePoint, OneDrive, internal repos, PII)?
2. Consumes untrusted input (web pages, uploaded files, MCP servers, skills)?
3. Can write to a surface (email, chat, ticket, dashboard, feed)?
4. Does that surface's renderer auto-fetch referenced external resources?

The tool inventory looks benign in isolation — the trifecta closes only when the renderer is in the audit.

## Key Takeaways

- An agent without a network tool can still exfiltrate when its output surface has an auto-fetching renderer downstream
- The lethal trifecta closes through composition; audit renderers, not just agent tool grants
- Pre-authenticated storage download links amplify the leak from beacon to file content — restrict them at the storage layer
- Two Microsoft incidents (EchoLeak 2025, Copilot Cowork 2026) used the same renderer-fetch primitive on different M365 surfaces
- Agent-side URL stripping is brittle; gating fetches in the renderer matches email-client defaults and has a smaller policy surface

## Related

- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md)
- [Guarding Against URL-Based Data Exfiltration in Agentic Workflows](url-exfiltration-guard.md)
- [Prompt Injection: A First-Class Threat to Agentic Systems](prompt-injection-threat-model.md)
- [Agent Network Egress Policy: Admin-Controlled Domain Allow/Deny](agent-network-egress-policy.md)
- [Human-in-the-Loop Confirmation Gates for Consequential Agent Actions](human-in-the-loop-confirmation-gates.md)
