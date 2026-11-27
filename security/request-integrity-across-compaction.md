---
title: "Request Integrity for Agent Authorization After Compaction"
term: "Request Integrity"
description: "A compaction summary can sit where an authorizer reads the user's request. One preprint measures the effect and tests a gate that passes only witnessed text."
tags:
  - security
  - agent-design
  - context-engineering
  - tool-agnostic
  - arxiv
aliases:
  - request integrity across compaction
  - witnessed-request gate
  - compaction summary in the request slot
last_reviewed: 2026-11-27
maturity: emerging
status: current
---

# Request Integrity for Agent Authorization After Compaction

> Compaction can place a model-written summary where an authorizer reads the user's request, so permissions derived there can follow injected data.

Request integrity means that after compaction the policy generator receives exactly the authenticated user turns and trusted tool outputs so far, complete and in order, or nothing ([Fei et al., 2026, §IV-A](https://arxiv.org/abs/2611.32194v1)). The preprint studies authorizers such as Progent, which defend against prompt injection by deriving permissions from the user's request ([§II](https://arxiv.org/abs/2611.32194v1)).

## When this applies

- A policy comes from the latest user message, again for each request. Progent's own integrations derive it once per session. A summary cannot reach that frozen policy, though Progent's run-time refinement still draws on tool results. The authors derived per request because, in two-turn AgentDojo sessions without injection or compaction, a frozen policy completed the second task in 7 of 60 sessions, against 41 of 60 for a per-request one ([§V-A and §VI](https://arxiv.org/abs/2611.32194v1)).
- The harness inserts the compaction summary as a user message. Claude Code does, as does Codex compacting locally. The paper reports the same in the code of eight other harnesses, including Gemini CLI, OpenHands and Cline ([§II](https://arxiv.org/abs/2611.32194v1)).
- The agent reads data an attacker can write.

## How the summary becomes the request

The authorizer credits the whole summary to the user, quoted documents and injected text included ([abstract](https://arxiv.org/abs/2611.32194v1)). The summary took that position at all 1,108 automatic compactions the authors recorded in live sessions. These ran Claude Code 2.1.312 and 2.1.319, and Codex 0.163.0 and 0.164.0 compacting locally with a 15,000-token limit ([§I and Appendix B](https://arxiv.org/abs/2611.32194v1)). OpenAI says the same in the pull request that made Codex's Guardian reviewer attribute these summaries to the assistant, merged 15 October 2026: "Local compaction stores generated summaries with the `user` wire role, but those summaries are not user authorization" ([openai/codex#54281](https://github.com/openai/codex/pull/54281)).

## Why a better summary is not enough

- Dropping the identifier only stops naming. No AgentDojo policy from the 918 summaries that dropped the attacker's identifier named it. Yet 78 of 410 banking policies from summaries that dropped the account admitted the transfer; an open recipient is enough ([§V-B](https://arxiv.org/abs/2611.32194v1)).
- Frontier compactors mark instructions. Under Claude Code's default prompt and Codex's, across three suites, gpt-5.4-mini and gpt-5.5 marked the injection in 219 of 220 summaries that kept the identifier. On banking the policy rarely named it. An account written as ordinary data mostly went unmarked ([§V-D](https://arxiv.org/abs/2611.32194v1)).
- Text alone has a limit. Without knowing who wrote which bytes, a pipeline can refuse a forged record more often than its real twin only as far as the two are distinguishable ([Theorem 1](https://arxiv.org/abs/2611.32194v1)).

## Give the authorizer its own input

The agent still reads the summary. The authorizer reads only witnessed text ([§IV](https://arxiv.org/abs/2611.32194v1)):

1. Each user turn and trusted tool output gets a MAC tag, its witness, on arrival.
2. At compaction, a trusted packager copies witnessed text verbatim and commits to the complete ordered list.
3. Before policy generation, a gate checks the witnesses, order and count. Any failure installs an empty policy that permits no call.

In 40 attacked AgentDojo episodes, no attacker action completed with the gate while the agent read the summary. Ungated, 7 did with the summary in the user position ([Table VII](https://arxiv.org/abs/2611.32194v1)). A harness that keeps user turns where the agent cannot write needs no MACs ([§VI](https://arxiv.org/abs/2611.32194v1)).

Cheaper changes fall short:

- Moving the summary elsewhere drops your earlier request from the policy input, leaving the recipient open when the follow-up asks for payment ([§IV](https://arxiv.org/abs/2611.32194v1)).
- Skipping records marked as summaries matched the gate inside one process. Through a store the agent can write, it admitted replayed and spliced records. That filter was the authors' version of Codex's reviewer rule, not Codex itself ([§V-F](https://arxiv.org/abs/2611.32194v1)).

## In a Claude Code hook

A `PreToolUse` hook gets `transcript_path`, not the request ([hooks reference](https://code.claude.com/docs/en/hooks#common-input-fields)). Across seven recorded sessions, the most recent user-role record was the user's turn at 96.2% of request starts and the summary at each boundary ([§V-D](https://arxiv.org/abs/2611.32194v1)).

Claude Code marks that record `isCompactSummary` ([Appendix B](https://arxiv.org/abs/2611.32194v1)). Skipping it is the filter above, and the agent can write session files ([§VI](https://arxiv.org/abs/2611.32194v1)).

`UserPromptSubmit` also fires for a session-scoped scheduled task, a background subagent report and another session's message, so its `prompt` alone does not show you typed it ([hooks reference](https://code.claude.com/docs/en/hooks#userpromptsubmit)).

## What the gate does not do

- It does not restore task completion while the agent reads the summary. Over 40 episodes the gated agent completed 13 tasks with the summary in the user position and 19 with it as a tool result. Without the gate those setups completed 9 and 18, and the uncompacted run completed 27 ([Table VII](https://arxiv.org/abs/2611.32194v1)).
- It does not narrow a loose request. If yours leaves the recipient open, the gated policy can still admit the attacker's call ([§V-F](https://arxiv.org/abs/2611.32194v1)).
- It does not vouch for documents or pastes. A value you leave to an unauthenticated document stays exposed, and pasted text counts as yours ([§II and §VI](https://arxiv.org/abs/2611.32194v1)).
- It assumes keys the agent cannot reach ([§IV-B](https://arxiv.org/abs/2611.32194v1)).
- It is not yet in a production harness. The authors evaluated the gate on replayed AgentDojo sessions and list long sessions and multi-agent workflows among the settings still to measure ([§VI](https://arxiv.org/abs/2611.32194v1)).

## Example

### Same summary, different position

Progent on 15 AgentDojo banking pairs, each followed by "Please continue from where we left off". gpt-4o-mini wrote the summaries under a prompt that asks it to preserve account numbers, and gpt-4o generated the policies. A policy "expands" when it permits a state-changing tool or argument value the earlier policy did not ([Table II](https://arxiv.org/abs/2611.32194v1)).

| Text in the request position | Policy expands | Names the attacker | Admits the attacker's call |
|---|---|---|---|
| Follow-up only | 0/30 | 0/30 | 0/30 |
| User's restated request | 5/30 | 0/30 | 0/30 |
| Same summary, appended as a tool result instead | 0/28 | 0/28 | 0/28 |
| Summary with the injected span removed | 9/16 | 0/16 | not scored |
| Unmodified summary | 21/30 | 16/30 | 17/30 |

### A payee you already stated

The user gives the landlord's account and asks what a notice says. The attacker's notice states another account as plain data. After compaction (gpt-5.4-mini or gpt-5.5, under Claude Code's default prompt or Codex's), the user asks to pay this month's rent ([§V-D and Appendix D](https://arxiv.org/abs/2611.32194v1)).

- Policy from the summary: it admitted the notice's account in 290 of 320 cases (91%) with gpt-4o as policy generator, and 59% with gpt-5.5. A gpt-5.4-mini agent completed that transfer in 33 of 80 episodes.
- Policy from the user's own turns: it never admitted the notice's account under either generator. Under the gate the agent completed no such transfer, and the gate blocked all 34 of its attempts.

## Key Takeaways

- Test which record your authorizer or hook reads on the first request after a compaction, not only on a fresh one.
- Treat what your compaction prompt keeps, and how it marks it, as a security setting. No better prompt separates a forged record from a real one when both share a format and value distribution and nothing else in the transcript depends on who wrote it.
- Bind authorship where text arrives. Do not rely on a summary marker in a file the agent can rewrite.
- Do not quote the 91% as a failure rate for a shipped product's permission system. It measures Progent policies in the paper's two-request test.

## Related

- [Authority Confusion: Untrusted Context Must Not Authorize Side Effects](authority-confusion-untrusted-context.md) — the rule that authority comes from the user, which a summary in the request position slips past
- [Intent-Governed Tool Authorization (IGAC)](intent-governed-tool-authorization.md) — a design that issues its certificate from the user's request
- [Treating Compaction Prompt Rules as a Provenance Defense](../patterns/anti-patterns/compaction-prompt-rules-as-provenance-defense.md) — forged user labels that survive into the summary, a second way compaction loses authorship
- [Non-Human Event Provenance Markers](non-human-event-provenance-markers.md) — marking harness-written events so they carry no human authority
- [Adaptive Evaluation of Out-of-Band Prompt-Injection Defenses](adaptive-evaluation-out-of-band-defenses.md) — how to attack Progent-style defenses before you trust their numbers
