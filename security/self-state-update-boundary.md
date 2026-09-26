---
title: "An Explicit Update Boundary for Agent Self-State"
term: "Self-State Update Boundary"
description: "OS controls that fully block writes to an agent's memory, instructions and config also block its legitimate self-updates, so the update needs a separate decision."
aliases:
  - self-state update boundary
  - authorized-update boundary for agent state
  - trusted update broker for agent memory
tags:
  - security
  - agent-design
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-21
maturity: emerging
---

# An Explicit Update Boundary for Agent Self-State

> A file the agent may legitimately write cannot be protected by a rule that decides on the write alone.

Sort the agent's persistent state by whether the agent has a legitimate reason to write each part, then protect the two halves differently. Parts the agent never updates get kernel-enforced immutability. Parts it does update need a second authorization step that runs on something other than the write, because a deny rule cannot tell the agent's own update from an attacker's.

Self-state is the memory, instruction and configuration files that shape what the agent does next. Chen and colleagues define it by function rather than filename: a file belongs to self-state when changing it can influence the agent's future decisions, tool use, or retained knowledge ([arXiv:2607.17986v2](https://arxiv.org/abs/2607.17986v2)). Once an injected instruction compromises the agent, corrupting those files needs no privilege escalation. The agent already has the write bit. The authors read it as the confused-deputy problem, with the twist that the object the deputy writes is its own future decision context.

## Sort the roles before choosing a control

Not every self-state file is written by the agent. The paper separates roles the agent must update in normal operation, such as episodic memory, from roles that "may be updated only under particular workloads or operator-approved workflows" ([arXiv:2607.17986v2](https://arxiv.org/abs/2607.17986v2)).

For a role the agent never writes, immutability is the whole control. A six-operation replay against `MEMORY.md` found that inode immutability (`chattr +i`), AppArmor and Landlock each blocked all six paths with no bypass ([arXiv:2607.17986v2](https://arxiv.org/abs/2607.17986v2), Table 7).

Clearing the write bit is a weaker control than it looks. In the same replay a self-owned `0444` file blocks direct write, append and truncate, and leaves three paths open: rename-over and unlink, which the writable parent directory permits, and chmod-then-write, which the agent's ownership permits. Root ownership closes the chmod path and still leaves rename-over and unlink. A barrier tested only against direct writes measures the attack its author thought of.

## Why it works

A deny rule fails on the writable half for a structural reason, not a tuning one. An access-control policy decides on the input it receives, which in this evaluation is the current operation's principal, object, operation kind and observable metadata. A legitimate memory append and an attacker-induced one can agree on all four, and then "a policy restricted to that current operation input assigns the pair the same decision" ([arXiv:2607.17986v2](https://arxiv.org/abs/2607.17986v2)). The authors scope that to the policy interface rather than to every OS-hosted defense. Their measurement shows it: the three configurations that blocked every mutation path also rejected the paired authorized update.

Separating the pair therefore requires giving the decision an input it does not have — the state's logical role, the task in flight, or whether the agent is in a sanctioned update phase. Moving the check to content screening does not supply that input either. A four-stage write-time screening pipeline reaching 0.832 recall on indirect prompt injection rejected 0 of 360 poisoned memories, because telling a false assertion from a true one "generally requires external grounding beyond the text being screened" ([arXiv:2608.21230v1](https://arxiv.org/abs/2608.21230v1)). Watching the host hits the same wall from the other side. Of nine detectors, the noisiest full-coverage one flagged 58 of 60 natural runs, while the two that held false positives to 3 of 60 produced a decision on only 23 of 55 attacks ([arXiv:2607.17986v2](https://arxiv.org/abs/2607.17986v2), Table 8).

## Example

The boundary does not have to live in the kernel. A Claude Code `PreToolUse` hook fires before a tool call and can return a `permissionDecision` of `"deny"` to block it ([hooks reference](https://code.claude.com/docs/en/hooks)). Match on the instruction and config paths, then consult a variable the agent has no way to set:

```bash
#!/usr/bin/env bash
# PreToolUse on Write|Edit. Denies unless the session was LAUNCHED with the toggle.
path=$(jq -r '.tool_input.file_path // ""')
case "$path" in
  */CLAUDE.md|*/AGENTS.md|*/.claude/*) ;;
  *) exit 0 ;;
esac
[ "${ALLOW_SELF_STATE_EDIT:-}" = "1" ] && exit 0
jq -n '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",
  permissionDecisionReason:"self-state edit requires an out-of-band toggle"}}'
```

The agent cannot export that variable into its own running process, so the authorization has to arrive before the session starts. An injected session writing the same bytes, to the same path, under the same user, is denied.

## When this backfires

- The agent has no legitimate write path to that role. Immutability already covers every tested operation, and a broker is one more trusted component to write and protect for no gain.
- The boundary is a human prompt on a role the agent updates routinely. Across the paper's clean workloads the median session changed one self-state object, with profile means from 0.15 to 2.09. A prompt at that rate lands in the rubber-stamping regime described under [human-in-the-loop confirmation gates](human-in-the-loop-confirmation-gates.md).
- The boundary is a permission bit rather than a separate principal. Rename-over and unlink stay open, so the file can still be replaced.
- Backups are treated as the boundary. Protected storage did survive an attack that destroyed agent-reachable backups, but every restore in the isolation matrix discarded the one legitimate post-snapshot update, and the authors leave recovery-point selection unresolved ([arXiv:2607.17986v2](https://arxiv.org/abs/2607.17986v2)).
- The deployment is not Linux or is containerized. The authors expect the tradeoff to carry to macOS and Windows, but not the measured coverage, false-positive rates or recovery costs.

## Key Takeaways

- Self-state is defined by influence on future behavior, not by filename, so the inventory includes session logs and runtime config as well as the persona file.
- Immutability and an update boundary are answers to different questions. Pick per role, not per agent.
- Detection does not rescue a missing boundary. No detector in the evaluation was strong on both attack coverage and specificity against ordinary agent activity.
- An out-of-band toggle is the cheapest form of the boundary, because the agent cannot supply its own authorization.

## Related

- [Gate Agent Writes to Executable Config Files as Privileged Actions](gate-agent-writes-to-executable-config.md) — the same write-site gate for project build config that grants code execution.
- [Enforced Versus Advisory Controls](enforced-versus-advisory-controls.md) — why the boundary has to be evaluated by the runtime rather than stated in the agent's context.
- [Human-in-the-Loop Confirmation Gates](human-in-the-loop-confirmation-gates.md) — the placement rules that keep an approval step out of the rubber-stamping regime.
- [Recall-Before-Send Memory Poisoning Detection](recall-before-send-memory-poisoning-detection.md) — a detection rule for the read side, after a poisoned memory has landed.
- [Blast Radius Containment](blast-radius-containment.md) — bounding what a compromised agent reaches once a write does get through.
