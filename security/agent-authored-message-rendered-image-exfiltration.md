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
last_reviewed: 2026-05-27
---

# Agent-Authored Messages as a Deferred Exfiltration Channel

> An auto-fetching renderer downstream of an agent's authoring tool acts as deferred egress — closing the lethal trifecta without a network grant.

An agent without a network tool is not automatically a closed-egress agent. If the agent can author messages on a surface whose renderer auto-fetches external resources, the renderer performs egress on the user's behalf. The lethal trifecta closes through *composition*, not through a single tool grant.

## The Composite-Egress Mechanism

The lethal trifecta normally treats external communication as a tool the agent invokes directly ([Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md)). The agent-authored-message pattern manufactures the third leg by chaining two non-egress tools:

1. The agent invokes an internal "send message" tool with no network access of its own.
2. The message contains external resource references (markdown images, `<img>` tags, link previews).
3. A downstream renderer — email client, chat surface, feed UI — auto-fetches those references when a user or scheduled task opens the message.
4. The attacker's server logs the request and any data encoded in the query string.

The mechanism matches [URL Exfiltration Guard](url-exfiltration-guard.md) — the URL itself carries the data — except the fetch is performed by the renderer, not the agent process.

## The Copilot Cowork Incident

PromptArmor disclosed this composition against Microsoft Copilot Cowork on 26 May 2026 ([PromptArmor disclosure](https://www.promptarmor.com/resources/microsoft-copilot-cowork-exfiltrates-files)). The product's documentation states that sensitive actions like sending emails or Teams messages require user approval. In practice, when the recipient is the active user, those actions execute without approval — and users have no setting to change that behaviour ([PromptArmor disclosure](https://www.promptarmor.com/resources/microsoft-copilot-cowork-exfiltrates-files)).

The attack chain:

1. A user uploads a skill file containing prompt injection (skills load automatically from a specific OneDrive path).
2. A routine "summarise what I worked on this week" query triggers the skill.
3. The injection instructs the agent to post a Teams message with HTML `<img>` tags whose `src` attributes are attacker URLs containing OneDrive pre-authenticated download links in the query string.
4. Opening the Teams message causes the renderer to fetch the images — leaking the download links to the attacker's server.
5. The attacker visits the leaked URLs and downloads the files. ([PromptArmor disclosure](https://www.promptarmor.com/resources/microsoft-copilot-cowork-exfiltrates-files))

PromptArmor reported 5/5 attack success across both Claude Opus 4.7 and the auto-routing model selector, with the injection comprising only 5 of 81 lines in the skill file ([PromptArmor disclosure](https://www.promptarmor.com/resources/microsoft-copilot-cowork-exfiltrates-files)).

## Why It Works

The mechanism is the composition rule, not a single bug. PromptArmor states it directly: *"Because these messages can contain external images that trigger network requests to external websites, data can be exfiltrated when a user opens a compromised message sent by the agent"* ([PromptArmor disclosure](https://www.promptarmor.com/resources/microsoft-copilot-cowork-exfiltrates-files)). The same fetch primitive that lets a recipient see an embedded chart turns into an exfiltration leg when the message author is an LLM responding to attacker-controlled content.

The OneDrive pre-authenticated download link amplifies the impact from beacon to file content. A leaked URL is not a tracking pixel — it is a working download credential anyone can use. This converts "we leaked some metadata" into "we leaked the file."

The same composition was demonstrated in 2025 against Microsoft 365 Copilot as EchoLeak (CVE-2025-32711), where reference-style markdown images survived Copilot's link-redaction safeguards and the Outlook/Teams renderer auto-fetched them ([Aim Labs / arxiv](https://arxiv.org/abs/2509.10540); [The Hacker News](https://thehackernews.com/2025/06/zero-click-ai-vulnerability-exposes.html)). Microsoft shipped server-side fixes by May 2025 ([The Hacker News](https://thehackernews.com/2025/06/zero-click-ai-vulnerability-exposes.html)) and documents HTML image injection as a defence-in-depth target ([Microsoft MSRC](https://www.microsoft.com/en-us/msrc/blog/2025/07/how-microsoft-defends-against-indirect-prompt-injection-attacks)) — yet the Cowork incident shows the same leg re-appearing on a different M365 surface 13 months later.

## Defences

Three controls compose into a defence in depth:

| Control | Layer | What it does |
|---------|-------|--------------|
| Strip or rewrite external resource references at agent write time | Agent | Remove `<img src="…">`, markdown `![]()` references, and link previews from agent-authored content before it is persisted |
| Gate image and resource fetches on explicit user intent in the renderer | Renderer | Default to "do not load remote images" — match email-client norms for untrusted senders |
| Restrict the data amplifier | Data source | Block download links at the storage layer; for SharePoint, `Set-SPOSite -Identity <site> -BlockDownloadPolicy $true` removes the pre-authenticated download surface ([PromptArmor disclosure](https://www.promptarmor.com/resources/microsoft-copilot-cowork-exfiltrates-files)) |

The agent-side and renderer-side controls are orthogonal. The agent-side control is brittle — pattern matching misses redirect chains, data URLs, CSS background images, and `srcset` permutations. The renderer-side control matches the established email-client default ("block remote images by default for untrusted senders") and has a smaller policy surface. Teams that own both surfaces should apply both.

Microsoft's "Defend against indirect prompt injection attacks" guidance lists deterministic blocking of HTML image injection as a defence layer ([Microsoft Learn](https://learn.microsoft.com/en-us/security/zero-trust/sfi/defend-indirect-prompt-injection)). The Cowork incident demonstrates that this protection must be applied per surface — Teams messages authored by an agent are a distinct surface from email arrivals processed by Copilot.

## When This Backfires

The pattern's defence work is wasted effort when the composition is already closed by some other leg:

- **Trusted-by-design recipients**: If the only consumer of agent-authored messages is an operator on a plain-text-only inbox, no renderer auto-fetches resources and the exfil leg does not exist.
- **No private-data context**: An agent that holds untrusted input and an authoring tool but no access to sensitive corpora has nothing worth exfiltrating. The trifecta is already broken at leg 1.
- **Markdown-aware LLM consumers**: When the downstream consumer is another LLM that ingests markdown text without auto-fetching resources, the renderer leg is closed by the consumer's nature, not by added defence.
- **Renderer outside your authority**: When the renderer is owned by a different vendor and you cannot force it to gate image fetches, write-time URL stripping degrades into brittle pattern matching. Treat it as a tactical patch and assume residual risk.

Scheduled agent tasks compound the surface — a "weekly review" recurring task that loads a poisoned skill exfiltrates on every run without user oversight ([PromptArmor disclosure](https://www.promptarmor.com/resources/microsoft-copilot-cowork-exfiltrates-files)). Treat any recurring agent-authored message workflow as a higher-priority audit target.

## Audit Checklist

For any agent with a "write to a user-facing surface" capability, answer four questions:

1. Does the agent have read access to private data (SharePoint, OneDrive, internal repos, PII corpora)?
2. Does the agent consume untrusted input (web pages, uploaded files, MCP servers, user-uploaded skills)?
3. Can it write to a surface (email, chat, ticket, dashboard, feed)?
4. Does the surface's renderer auto-fetch external resources referenced in the content?

Four "Yes" answers indicate the composite-egress leg is open. The agent's tool inventory looks benign in isolation — the trifecta closes only when the renderer is included in the audit.

## Key Takeaways

- An agent without a network tool can still exfiltrate when its output surface has an auto-fetching renderer downstream
- The lethal trifecta closes through composition; audit renderers, not just agent tool grants
- Pre-authenticated storage download links amplify the leak from beacon to file content — restrict them at the storage layer
- Two real-world Microsoft incidents (EchoLeak 2025, Copilot Cowork 2026) used the same renderer-fetch primitive on different M365 surfaces
- Agent-side URL stripping is brittle; gating image fetches in the renderer matches established email-client defaults and has a smaller policy surface

## Related

- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md)
- [Guarding Against URL-Based Data Exfiltration in Agentic Workflows](url-exfiltration-guard.md)
- [Prompt Injection: A First-Class Threat to Agentic Systems](prompt-injection-threat-model.md)
- [Agent Network Egress Policy: Admin-Controlled Domain Allow/Deny](agent-network-egress-policy.md)
- [Human-in-the-Loop Confirmation Gates for Consequential Agent Actions](human-in-the-loop-confirmation-gates.md)
