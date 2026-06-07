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
last_reviewed: 2026-06-03
status: current
---

# Lock-State Safeguards for Desktop-Controlling Agents

> Bound a desktop-controlling agent along four axes — time, visibility, presence, recovery — so failure on any single axis is contained by the others.

## The Threat Shape

A desktop-controlling agent — Codex driving Mac apps, a browser-use harness, an RPA bridge — holds the user's session credentials and operates the machine the user just locked. Four failure modes follow: a long-lived authorisation outlives the operator's attention and a token replays after the task ends; an uncovered display leaks what the agent surfaces; a returning user finds an already-privileged agent acting under their identity; and an agent in an ambiguous state retries silently into a half-controlled desktop.

The Codex 2026-05-21 release names four safeguards that close all four: "short-lived authorization, covered displays, relock on local input, and manual-unlock fallback" ([Codex changelog, 2026-05-21](https://developers.openai.com/codex/changelog)). It generalises to any agent-drives-the-machine surface.

## The Four Axes

### Short-Lived Authorisation (Time Axis)

The Codex docs describe the authorisation as "short-lived and scoped to the current unlock attempt" ([Codex computer use docs](https://developers.openai.com/codex/app/computer-use#locked-use)). A leaked token expires before the threat can use it; the window is per-turn, not per-session. Two choices follow:

- **Default-deny on expiry**: the agent does not auto-renew — the next action takes fresh authorisation or terminates to the manual-unlock fallback.
- **No refresh on agent activity**: refresh is tied to operator presence, not agent liveness, or any task extends the window indefinitely.

### Covered Displays (Visibility Axis)

Codex "covers every display while the desktop is temporarily unlocked" ([Codex computer use docs](https://developers.openai.com/codex/app/computer-use#locked-use)). Coverage protects against shoulder-surfing and screen-share software capturing the session. It is the weakest axis — a soft defence that does not stop a co-located adversary who lifts the cover or photographs the screen.

### Relock on Local Input (Presence Axis)

Codex's docs are explicit: "If Codex detects local keyboard or pointer input, it relocks the Mac and pauses automatic unlock until you unlock it manually" ([Codex computer use docs](https://developers.openai.com/codex/app/computer-use#locked-use)). This serves two purposes:

- **User-presence signal**: the returning operator ejects the agent by touching the keyboard or trackpad.
- **Adversarial-takeover defence**: a local attacker who interacts with the session triggers the relock instead of inheriting the agent-driven keyboard.

The pause-until-manual-unlock is load-bearing — without it the agent re-acquires control the moment the user steps away.

### Manual-Unlock Fallback (Recovery Axis)

When the agent's state becomes ambiguous — denied permission, network drop, unexpected dialog — it surfaces back to the human rather than retrying: "Codex denies the unlock and asks you to unlock manually if needed" ([Codex computer use docs](https://developers.openai.com/codex/app/computer-use#locked-use)). The shape matches [Confirmation Gates for Consequential Agent Actions](human-in-the-loop-confirmation-gates.md), engaged on failure paths: a confused agent retrying silently can blunder into write actions or credential prompts; one that terminates to a manual unlock cannot.

## Why It Works

The axes are independent: a failure on any one is contained by the other three, and the agent's authority collapses unless all four hold. This is [defense-in-depth](defense-in-depth-agent-safety.md) applied to a single principal — the [task scope](task-scope-security-boundary.md) is a logged-in human session the agent is borrowing. The Codex docs make the intent explicit: locked use is "not a general-purpose remote-unlock path for your Mac" ([Codex computer use docs](https://developers.openai.com/codex/app/computer-use#locked-use)) — the authorisation is the smallest that works.

## When This Backfires

The four mechanisms compose well but each has a known failure mode:

- **Display-cover bypass**: a system-modal dialog or full-screen overlay drawn above the cover defeats the visibility axis — the cover is a process-level mask, not a hardware one.
- **Lock-state spoofing**: a malicious local process that pretends the machine is still locked tricks the safeguard logic, which trusts the OS lock state — broken on a compromised host.
- **Input-detection race**: relock-on-input has non-zero latency, so an attacker with physical access acting during the relock interval reads what the agent just surfaced.
- **Fallback fatigue**: an agent that repeatedly prompts for manual unlock conditions the user to approve without reading — [confirmation-gate](human-in-the-loop-confirmation-gates.md) rubber-stamping defences apply here.
- **Screen-share collision**: a user who joins a video call mid-task may share-screen before the cover engages, leaking the session to call participants.

A reasonable alternative sidesteps all four: run the agent in an isolated VM or service account with its own credentials, so it never borrows the user's session — better for sensitive workloads. Lock-state safeguards fit when the alternative is no automation at all, the data on screen is the user's own, and the operator wants the agent to act with their identity, not a delegated one.

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
