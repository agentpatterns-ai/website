---
title: "Memory-File Influence Disclosure: Passing Tests Do Not Clear a Malicious CLAUDE.md"
term: "Memory-File Influence Disclosure"
description: "In one study, malicious memory files moved secure-completion rates by -8 to +6 points with no pattern, while agents differed in whether the final message named the file."
tags:
  - security
  - instructions
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - malicious CLAUDE.md
  - memory file attack surface
  - memory-file disclosure
last_reviewed: 2026-10-31
maturity: emerging
status: current
---

# Memory-File Influence Disclosure: Passing Tests Do Not Clear a Malicious CLAUDE.md

> A malicious memory file did not reliably weaken generated code, but agents differ in whether they tell the developer the file shaped the patch.

Coding agents load project memory files such as `CLAUDE.md` at the start of every session and treat them as trusted guidance. Anyone who can change one, for example through a pull request, steers the agent without touching the developer's prompt. The study here finds a review problem, not an exploit rate.

## What the study measured

[de Moura, Güler and Noller](https://arxiv.org/abs/2610.38521v1) crafted two malicious memory files for each of 12 CWE classes. The qualified variant presents removing a defensive check as best practice. The forceful variant demands it. They ran 36 tasks drawn from the 318 in SecRepoBench, with and without the files.

| Agent | Models |
|---|---|
| Claude Code 2.1.308 | Claude Sonnet 5.5 |
| OpenCode 2.1.1 | Qwen 3.8 27B, DeepSeek V4.1 Flash |

Source: [de Moura, Güler and Noller](https://arxiv.org/abs/2610.38521v1), Section IV.

## Two results

The security effect was small and inconsistent. The files "changed the rate of secure completions by −8 to +6 percentage points, with no consistent pattern across agents or variants." Four of the six measured shifts were increases. A malicious file therefore sometimes coincided with more secure code ([de Moura, Güler and Noller](https://arxiv.org/abs/2610.38521v1), Section V). Do not read this study as a successful attack.

Disclosure differed by agent. Claude Code named the file in about two thirds of its sessions, in the final message and in its reasoning. OpenCode, with both models, rarely named it in the final message but named it far more often in its reasoning trace. The paper gives no percentages for OpenCode ([de Moura, Güler and Noller](https://arxiv.org/abs/2610.38521v1), Section V). The developer reads the final message. A reasoning trace that names the file does not help someone who never opens it.

The authors warn that passing tests and silence about the file do not establish harmlessness ([de Moura, Güler and Noller](https://arxiv.org/abs/2610.38521v1)).

## Flagging the file does not protect the code

Some agents called the file an attack and still wrote the vulnerable code. The paper counts 18 sessions whose reasoning calls the file an attack, whatever the completion looks like. In those sessions security fell against baseline in three and rose in two ([de Moura, Güler and Noller](https://arxiv.org/abs/2610.38521v1), Section V). The authors' reading: "calling it an attack does not by itself protect the code." An agent's suspicion is a signal to read, not a control.

## What to do with it

These steps are this page's recommendations, not findings of the paper.

- Review a memory-file change like a code change. It is an input to every later patch. A [code-owner rule](gate-agent-writes-to-executable-config.md) on `CLAUDE.md`, `AGENTS.md`, and similar files puts a human in front of the edit.
- Do not accept a green test run as clearance. The study's oracle detected only the targeted weakness, so other vulnerabilities go unseen.
- Read the reasoning trace, not just the final message, when a patch removes a check, widens a permission, or skips validation. For OpenCode in this study, that is where the file showed up.
- Diff against a run without the file when a memory-file change merges and a security-relevant patch follows. The study's own design is that comparison.
- Move the control out of the model. A [dispatch-layer check](authority-confusion-untrusted-context.md) does not depend on the agent reporting its own influences.

## Where this fits

Other memory pages cover [dormant payloads](trojan-hippo-memory-attack.md), [forged reasoning traces](forged-reasoning-trace-memory-attack.md), and [poisoned skills](skill-supply-chain-poisoning.md). These channels use untrusted tool calls, decision histories, and registries. This page covers the reviewability of one channel, the repository's own instruction file. [Covert success rate](covert-success-rate-injection.md) makes a parallel point for injected tool content: the final reply is a weak witness of what shaped the work.

## When this backfires

- The finding is one benchmark with a single run per condition. The authors "cannot show statistical significance of the obtained results."
- The tasks are 36 C and C++ tasks from fast-running repositories. The authors state the results do not cover other languages or large projects.
- The OSS-Fuzz-based tasks may have appeared in training data.
- The single-file, single-commit setup favors the attacker, and the authors make no claim about how often such attacks occur in real repositories.
- Your agent streams its full transcript and your reviewers read it. Then the final-message gap matters less.

## Key Takeaways

- The malicious memory files shifted secure-completion rates by -8 to +6 percentage points with no consistent pattern, so the study shows no reliable attack.
- Claude Code named the file in about two thirds of sessions. OpenCode rarely named it in the final message, so the developer's view differs by agent.
- Passing tests plus a final message that omits the file is not evidence the file was harmless.
- An agent that calls the file an attack can still write vulnerable code: in 3 of 18 such sessions security fell against baseline.
- Treat memory-file edits as reviewed inputs, and read the reasoning trace when a patch weakens a check.

## Related

- [Dormant Memory Payloads Triggered by Sensitive Topics (Trojan Hippo)](trojan-hippo-memory-attack.md) — an untrusted tool call plants the payload, where here the repository's own file carries it
- [Forged Reasoning Trace Attacks on Agent Memory (FARMA)](forged-reasoning-trace-memory-attack.md) — a second memory channel, where the poison is a forged decision history
- [Authority Confusion: Untrusted Context Must Not Authorize Side Effects](authority-confusion-untrusted-context.md) — the dispatch-layer control that does not rely on agent self-report
- [Skill Supply-Chain Poisoning](skill-supply-chain-poisoning.md) — the registry channel for the same trust in agent-loaded documents
- [Covert Success Rate for Indirect Prompt Injection](covert-success-rate-injection.md) — the same gap between what ran and what the final reply says
- [Gate Agent Writes to Executable Config Files as Privileged Actions](gate-agent-writes-to-executable-config.md) — gating the write site of config an agent trusts
- [CLAUDE.md Convention for Structuring Agent Instructions](../instructions/claude-md-convention.md) — what the file is for when it is not hostile
