---
title: "Lock-State Safeguards for Desktop-Controlling Agents"
description: "Four mechanisms — short-lived authorization, covered displays, relock on local input, and manual-unlock fallback — bound an agent's authority to drive a user's logged-in desktop while the user is away."
tags:
  - security
  - agent-design
  - tool-agnostic
aliases:
  - locked-session computer use safeguards
  - desktop agent lock-state safeguards
last_reviewed: 2026-05-27
status: current
---

# Lock-State Safeguards for Desktop-Controlling Agents

> Bound a desktop-controlling agent along four axes — time, visibility, presence, recovery — so failure on any single axis is contained by the others.

## The Threat Shape

A desktop-controlling agent — Codex driving Mac apps, a browser-use harness, an RPA bridge — holds the user's own session credentials and operates the machine the user just locked. Four failure modes follow:

- A long-lived authorisation outlives the operator's attention window; a captured token replays after the task ends.
- An uncovered display leaks whatever the agent surfaces to anyone walking past.
- A user returning mid-task finds an already-privileged agent acting under their identity.
- An agent in an ambiguous state (network drop, repeated permission denial, unexpected dialog) that retries silently leaves the desktop half-controlled.

The Codex 2026-05-21 release names four safeguards that close all four: "short-lived authorization, covered displays, relock on local input, and manual-unlock fallback" ([Codex changelog, 2026-05-21](https://developers.openai.com/codex/changelog)). The pattern generalises to any "agent drives the human's machine" surface.

## The Four Axes

### Short-Lived Authorisation (Time Axis)

The Codex docs describe the authorisation as "short-lived and scoped to the current unlock attempt" ([Codex computer use docs](https://developers.openai.com/codex/app/computer-use#locked-use)). A leaked or replayed token expires before the threat can use it. The window is per-turn, not per-session.

Two design choices follow:

- **Default-deny on expiry**: when the window closes mid-task, the agent does not auto-renew. The next action either succeeds with a fresh authorisation or terminates to the manual-unlock fallback.
- **No refresh on the agent's own activity**: refresh tokens must be tied to operator presence (a connected, trusted client), not agent liveness, otherwise any task extends the window indefinitely.

### Covered Displays (Visibility Axis)

Codex "covers every display while the desktop is temporarily unlocked" ([Codex computer use docs](https://developers.openai.com/codex/app/computer-use#locked-use)). Coverage protects against passive shoulder-surfing and against the user's own screen-share software capturing the unlocked session.

This is the weakest axis — a soft defence. It does not protect against a co-located adversary who lifts the cover, photographs the screen, or reads what flickers during the coverage transition.

### Relock on Local Input (Presence Axis)

Codex's docs are explicit: "If Codex detects local keyboard or pointer input, it relocks the Mac and pauses automatic unlock until you unlock it manually" ([Codex computer use docs](https://developers.openai.com/codex/app/computer-use#locked-use)). The axis serves two purposes:

- **User-presence signal**: the returning operator does not have to think about ejecting the agent — touching the keyboard or trackpad does it.
- **Adversarial-takeover defence**: a local attacker who interacts with the partially-active session triggers the relock instead of inheriting the agent-driven keyboard.

The pause-until-manual-unlock is load-bearing. Without it the agent could re-acquire control the moment the user steps away again.

### Manual-Unlock Fallback (Recovery Axis)

When the agent's state becomes ambiguous — denied permission, network drop, unexpected dialog — it surfaces back to the human rather than retry. The Codex docs frame this negatively: "Codex denies the unlock and asks you to unlock manually if needed" ([Codex computer use docs](https://developers.openai.com/codex/app/computer-use#locked-use)). The shape matches [Confirmation Gates for Consequential Agent Actions](human-in-the-loop-confirmation-gates.md) but engaged on failure paths. A confused agent that retries silently can blunder into write actions or credential prompts; one that terminates to a manual unlock cannot.

## Why It Works

Each axis is independent. The pattern works because a single failure on any one axis is contained by the other three: time, visibility, presence, and recovery cover orthogonal failure modes, and the agent's authority collapses unless all four hold. This is defense-in-depth applied to a single principal — the same shape as [Defense-in-Depth Agent Safety](defense-in-depth-agent-safety.md) and the per-task scoping in [Treat Task Scope as a Security Boundary](task-scope-security-boundary.md), but applied to the narrow case of a logged-in human session that an agent is borrowing. The Codex docs make the design intent explicit: locked use is "not a general-purpose remote-unlock path for your Mac" ([Codex computer use docs](https://developers.openai.com/codex/app/computer-use#locked-use)) — the authorisation is the smallest that lets the use case work, and every safeguard exists to keep it from growing larger.

## When This Backfires

The four mechanisms compose well but each has known failure modes worth naming.

- **Display-cover bypass**: a system-modal dialog, focus-stealing notification, or full-screen accessibility overlay that draws above the cover defeats the visibility axis. The cover is a process-level mask, not a hardware-level one.
- **Lock-state spoofing**: a malicious local process that pretends the machine is still locked when it is not tricks the safeguard logic. The mechanism trusts the OS lock state — that trust is broken on a compromised host.
- **Input-detection race**: relock-on-input has non-zero detection latency. An attacker with physical access who acts during the relock interval reads what the agent had just surfaced. The window is short but not zero.
- **Fallback fatigue**: a confused or adversarially steered agent that repeatedly prompts for manual unlock conditions the user to approve without reading. Confirmation gates against rubber-stamping — see [Confirmation Gates for Consequential Agent Actions](human-in-the-loop-confirmation-gates.md) — apply here.
- **Screen-share collision**: a user who joins a video call while the agent is mid-task may share-screen before the cover engages, leaking session contents to call participants. The cover protects against local observers, not against software the user invites in.

A reasonable alternative architecture sidesteps all four mechanisms: run the agent in an isolated VM or service account with its own credentials, so it never borrows the user's session. That choice is better for sensitive workloads (admin consoles, financial dashboards). Lock-state safeguards are the right pattern when (a) the alternative is no automation at all, (b) the data on screen is the user's own, and (c) the operator wants the agent to act with their identity rather than a delegated one.

## Example

Codex 2026-05-21 ships the canonical implementation. The release notes name the four mechanisms in a single sentence: "Codex scopes locked use to active, trusted computer use turns and includes safeguards such as short-lived authorization, covered displays, relock on local input, and manual-unlock fallback" ([Codex changelog, 2026-05-21](https://developers.openai.com/codex/changelog)).

The implementation choices behind each safeguard ([Codex computer use docs](https://developers.openai.com/codex/app/computer-use#locked-use)):

| Axis | Codex implementation |
|------|---------------------|
| Time | "The authorization window is short-lived and scoped to the current unlock attempt." |
| Visibility | "Codex covers every display while the desktop is temporarily unlocked." |
| Presence | "If Codex detects local keyboard or pointer input, it relocks the Mac and pauses automatic unlock until you unlock it manually." |
| Recovery | "Codex denies the unlock and asks you to unlock manually if needed." |

The scope statement — "not a general-purpose remote-unlock path for your Mac" — is the design contract every implementation of this pattern should make explicit. The authorisation exists for one narrowly-scoped capability, not as a backdoor into the lock screen.

## Key Takeaways

- A desktop-controlling agent is a single principal that holds the user's session credentials while the user is away — four independent axes (time, visibility, presence, recovery) bound that authority.
- Short-lived authorisation expires per-turn, not per-session, and never auto-refreshes on the agent's own activity.
- Display coverage is a soft defence; it stops shoulder-surfing, not determined local attackers.
- Relock on local input must pause auto-unlock until manual recovery — without the pause, the agent re-takes control the next time the user steps away.
- Manual-unlock fallback engages on ambiguous failure paths to prevent silent degradation into a half-controlled state.
- For sensitive workloads, a separate VM or service account is often the better alternative — these safeguards fit the consumer-desktop case where the agent must act as the user.

## Related

- [Defense-in-Depth Agent Safety](defense-in-depth-agent-safety.md) — the broader pattern these four axes instantiate for a single principal
- [Confirmation Gates for Consequential Agent Actions](human-in-the-loop-confirmation-gates.md) — the recovery axis is a confirmation gate on the failure path
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md) — narrows what a successful breach of any single axis can affect
- [Treat Task Scope as a Security Boundary](task-scope-security-boundary.md) — per-turn authorisation scoping is task-scope thinking applied to lock state
- [Heartbeat-Bound Hierarchical Credentials](heartbeat-bound-hierarchical-credentials.md) — credential lifetime bounded to operator presence rather than agent liveness
