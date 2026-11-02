---
title: "Browser Credential Handoff: Human Takes the Window at the Auth Wall"
term: "Browser Credential Handoff"
description: "At a login or two-factor wall, the agent hands its live browser window to the person. LangChain says the password then stays out of model messages and traces."
aliases:
  - browser handoff to human
  - human-takes-the-window login
  - agent browser auth handoff
tags:
  - security
  - agent-design
  - human-factors
  - tool-agnostic
last_reviewed: 2026-10-31
maturity: emerging
---

# Browser Credential Handoff: Human Takes the Window at the Auth Wall

> In a browser handoff, the person types the password into the live window. No chat message or agent typing call carries it.

A browser agent at a login wall or a two-factor prompt has three choices. It can stop. It can ask the person to paste the password into chat. It can hand the live browser window to the person.

The third option is a credential boundary. The secret goes from the person's keyboard to the website, and no chat message or agent typing call carries it.

LangChain's Managed Deep Agents v0.10 ships this as a tool. Its post states the case: "Most browser agents stop at a login wall or a two-factor prompt. With `browser_handoff`, the agent hands the window to you instead, so your password never ends up in the model's messages or traces" ([LangChain, Managed Deep Agents v0.10](https://www.langchain.com/blog/managed-deep-agents-browser-use-and-asynchronous-subagents)). Treat that product as one dated implementation of the pattern.

## How the handoff works

The browser toolset has four tools ([LangChain](https://www.langchain.com/blog/managed-deep-agents-browser-use-and-asynchronous-subagents)):

| Tool | What it does |
|---|---|
| `browser_snapshot` | Reads the page's accessibility tree and assigns element IDs |
| `browser_run` | Navigates and interacts, through JavaScript or batches of actions against snapshot IDs |
| `browser_screenshot` | Captures the page, optionally saving the image to the sandbox |
| `browser_handoff` | Gives a person control of the browser window |

The first three form the [element-addressed action space](../patterns/agent-design/browser-as-agent-action-space.md). The fourth takes the agent out of the loop.

The flow, per the [LangSmith browser use docs](https://docs.langchain.com/langsmith/python/managed-deep-agents-browser-use):

1. The agent calls `browser_handoff(reason)` and states why it needs the person.
2. The client shows a link to the remote browser and a Hand back button. The call returns immediately, so the agent can do other work.
3. "While you control the window, the agent's browser tools cannot act on it."
4. The person signs in, then selects Hand back. The agent inspects the current page to check whether login succeeded, then continues.

The link expires after 15 minutes. The docs state: "expiry ends the handoff but does not prove that the website task is complete". Verify completion on the page.

## Why the boundary holds

The model sees tool calls and tool results. The docs tell the person to enter credentials "directly on the website, not in chat". The agent's browser tools cannot act on the window meanwhile. By this reasoning, the password reaches the site with no agent tool call to carry it. LangChain makes the stronger claim that it also stays out of traces. The Limits section notes that no source tests that claim. A password typed in chat can land in the transcript, in a trace exporter, and in platform logs.

This is the goal of [sandbox credential masking](sandbox-credential-masking.md) and a [scoped credentials proxy](scoped-credentials-proxy.md), reached by a different route. Those controls hide a stored secret from the model. A handoff never gives the secret to the agent's side. It also covers a two-factor prompt that needs the person's device.

## Limits to design around

- The link is a bearer capability. "Keep handoff links private: anyone with a valid link can control the browser" ([LangSmith docs](https://docs.langchain.com/langsmith/python/managed-deep-agents-browser-use)).
- The session stays authenticated afterward. The handoff keeps the password out of the model's channel but does not limit what the agent does with the session. The [lethal trifecta](lethal-trifecta-threat-model.md) risk of a logged-in, driven browser applies in full, so gate consequential actions with [confirmation gates](human-in-the-loop-confirmation-gates.md).
- Session reuse widens reach. With `scope="user"`, a person's logins carry across their conversations. The docs state: "Browser scope controls session reuse; it is not a password vault" ([LangSmith docs](https://docs.langchain.com/langsmith/python/managed-deep-agents-browser-use)).
- Page content can still leak. The docs warn to "avoid exposing secrets in page content that the agent can later inspect" ([LangSmith docs](https://docs.langchain.com/langsmith/python/managed-deep-agents-browser-use)). A snapshot of an account page can put personal data in context.
- The docs do not say what the model sees during the handoff. They do not describe how snapshots or screenshots around the handoff are handled. Neither source includes an independent test of the "never in traces" claim. Check your own trace exports before you rely on it for regulated data.

## When to use it

Use a handoff when three things hold. The task needs a site with no API. The login involves a secret you keep out of transcripts. A person can reach the link within its window.

Skip it when the agent runs unattended. A login cannot complete without a person at the window. For unattended work, use a [scoped, short-lived credential](scoped-credentials-proxy.md). If the action needs fresh authorization from the person rather than a login, see [proof of presence](proof-of-presence-step-up-authentication.md).

## Example

The LangSmith docs describe the Studio login flow. A card reads "The agent needs you in the browser". The person controls the page until they select Hand back ([LangSmith docs](https://docs.langchain.com/langsmith/python/managed-deep-agents-browser-use)).

## Key Takeaways

- Hand the live window to the person at a login or two-factor wall. LangChain says the password then stays out of the model's messages and traces.
- Treat the handoff link as a bearer credential: anyone holding it controls the browser, and it expires after 15 minutes.
- Hand-back leaves an authenticated session in the agent's hands. Scope what it may do next and gate irreversible actions.
- Verify the login on the page after hand-back. Link expiry does not prove the sign-in succeeded.
- The vendor docs leave what the model sees during a handoff unstated. Test your own traces before trusting the guarantee.

## Related

- [Browser as Agent Action Space](../patterns/agent-design/browser-as-agent-action-space.md) — the snapshot, run, and screenshot loop that the handoff interrupts.
- [Live Browser as Agent Context Channel](../context-engineering/live-browser-context-channel.md) — why a logged-in session widens the injection surface.
- [Proof of Presence: Re-Authenticating for Agent Actions](proof-of-presence-step-up-authentication.md) — fresh authorization for an action, as against credential entry.
- [Sandbox Credential Masking](sandbox-credential-masking.md) — hiding stored secrets from the model.
- [Scoped Credentials Proxy](scoped-credentials-proxy.md) — the unattended alternative when no person can take the window.
- [Human-in-the-Loop Confirmation Gates](human-in-the-loop-confirmation-gates.md) — gating consequential actions after hand-back.
- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md) — the risk a logged-in driven browser closes.
