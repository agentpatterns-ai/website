---
title: "One-Shot Permission Answers for Out-of-Directory Reads"
term: "One-Shot Permission Answer"
description: "Claude Code's allow-and-ask-again answer in auto mode clears one read outside the working directories; the saved alternative on the same prompt clears every later one too."
tags:
  - agent-design
  - claude
  - human-factors
  - arxiv
aliases:
  - allow once permission answer
  - non-persisting permission grant
  - Yes but ask again next time
last_reviewed: 2026-10-13
maturity: emerging
status: current
---

# One-Shot Permission Answers for Out-of-Directory Reads

> One permission answer clears the read in front of you. The saved answer on the same prompt clears every read outside the working directories.

A one-shot permission answer runs the action the prompt names and saves no rule. Claude Code added one to auto mode's prompt before a read outside the working directories in version 2.1.284. Pick "Yes, but ask again next time" and "the read runs, nothing is saved, and the next read outside the working directories prompts again" ([Permission modes](https://code.claude.com/docs/en/permission-modes#first-read-outside-the-working-directories)). It is the right answer under three conditions: a person is at the prompt, the crossing is unusual, and no narrower grant covers the path. Where crossings are routine, scope the directory instead.

## The four answers

In auto mode, while `permissions.blockReadsOutsideWorkingDirectories` is off, the prompt fires the first time Claude uses Read, Grep, or Glob on a path outside the working directories. Its four answers vary on two things: whether the read runs, and whether your answer outlives it ([Permission modes](https://code.claude.com/docs/en/permission-modes#first-read-outside-the-working-directories)).

| Answer | The read | What it leaves behind |
|---|---|---|
| Yes, and keep allowing any reads outside the working directories | Runs | "Claude Code records your answer so the prompt doesn't appear again" |
| Yes, but ask again next time | Runs | Nothing |
| No, and ask again next time | Refused | Nothing |
| No, and block reads outside the working directories from now on | Refused | `permissions.blockReadsOutsideWorkingDirectories` set to `true` in user settings, refusing such reads "in every later session and every permission mode" |

Version 2.1.284 added the second row to a prompt that already existed ([Claude Code changelog](https://code.claude.com/docs/en/changelog#2-1-284)). The changelog lists it as an addition to the existing prompt; the other three answers either save a broad allow, refuse, or refuse and set a block. The same release started interactive terminal and VS Code sessions in auto mode when no permission mode is configured, so the auto-mode prompt now arrives unasked.

## Why it works

The saved allow is wider than the evidence the prompt showed. The question is asked about one path; the answer that persists covers "any reads outside the working directories" ([Permission modes](https://code.claude.com/docs/en/permission-modes#first-read-outside-the-working-directories)).

Claude Code offers a save option "only when the prompt can show you everything they would allow, so a rule you save from a prompt covers only what its option named" ([Configure permissions](https://code.claude.com/docs/en/permissions)). Here the option names a boundary, not a path, so the saved rule is accurate about its reach and still unbounded. The one-shot answer is the only one whose scope equals what you read on screen. It exists for a boundary grant and not for a Bash command, whose saved rule covers the command string the prompt displayed.

One study measured the trade. Per-action approval blocked 59.6% of agent overreach against 39.6% for rules written in advance, and cost 18.0 runtime prompts against 10.9, across 113 participants in three conditions ([Yan, 2026](https://arxiv.org/abs/2608.27443v1)). Deciding per call protects more and costs more. The study states its own limit: it analyzed "113 participants without professional software backgrounds", and its focus is everyday tasks "rather than developers using coding agents (e.g., Codex or Claude Code)". Take the direction, not the figures.

## When this backfires

- A toolchain that lives outside the working directories. A vendored dependency tree, a sibling repo, or a language runtime crosses the boundary all day. Adding the directory with `/add-dir` or `permissions.additionalDirectories` grants one directory rather than everything past the boundary ([Configure permissions](https://code.claude.com/docs/en/permissions)).
- Unattended runs. "The prompt doesn't appear in non-interactive `-p` runs or background sessions; reads there run as before" ([Permission modes](https://code.claude.com/docs/en/permission-modes#first-read-outside-the-working-directories)). A team that calls this answer its control over out-of-boundary reads has none in the runs nobody watches.
- Repetition. Users approve 93% of permission prompts already ([Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)), and a prompt answered the same way every time collects that reflex. The fatigue mechanism and its cost are covered in [Approval Gate Granularity in Agent Pipelines](approval-gate-granularity.md); the within-reviewer decay under repeat exposure is in [Reviewer Habituation in Agent PR Review](../../code-review/reviewer-habituation-decay.md).
- Reading it as containment. The answer bounds later reads. This file's contents already entered the context, and auto mode's injection probe adds a warning rather than blocking content ([Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)).
- A path that should never be read. "No, and ask again next time" asks again forever. The durable refusal is the setting the fourth answer writes for you.
- Auditability. Saving nothing records nothing. A permanent Bash or WebFetch approval is saved to `.claude/settings.local.json` ([Configure permissions](https://code.claude.com/docs/en/permissions)); a hundred one-shot allows live only in a transcript.

## Example

A repository whose Python runtime sits at `/usr/lib/python3.12` crosses the boundary on its first dependency read. "Yes, but ask again next time" clears that read and leaves the prompt armed, which is the correct answer once. By the third crossing in an hour the answer is neither prompt option:

```bash
/add-dir /usr/lib/python3.12
```

Files in an added directory "follow the same permission rules as the original working directory" ([Configure permissions](https://code.claude.com/docs/en/permissions)). One directory opens and the boundary holds everywhere else, which is the part the saved allow would have given away.

## Key Takeaways

- At the prompt, pick "Yes, but ask again next time" for a one-off read. Pick the saved allow only when you accept every path outside the working directories.
- Check the mode first. The prompt exists in auto mode only; in other modes, scope access with `/add-dir` or `permissions.additionalDirectories`.
- Treat the study figures as direction only. Its participants were not developers ([Yan, 2026](https://arxiv.org/abs/2608.27443v1)).
- It raises reviewer load, and the transcript is the only record that the read was allowed.
- Count crossings per hour. A third crossing means scope the directory with `/add-dir`.

## Related

- [Six-Shape Approval Response Taxonomy](approval-response-taxonomy.md) — the same persistence knob one layer down, as `updatedPermissions` on the Agent SDK's `canUseTool` callback
- [Approval Gate Granularity in Agent Pipelines](approval-gate-granularity.md) — the bundling axis; a saved answer is class bundling, and this prompt's class is the whole boundary
- [Ask-Everything Permission Policies Protect Less than Per-Action Approval](../anti-patterns/ask-everything-permission-policies.md) — the measured comparison between standing rules and deciding per call
- [Action-Class Permission Gates Leave Task Fit and Reversibility to the Human](action-class-permission-gates.md) — what the prompt does not tell you about the action it names
- [Evidence-Based Allowlist Auto-Discovery for Agents](../../security/evidence-based-allowlist-auto-discovery.md) — the opposite direction, turning repeated approvals into persistent rules
