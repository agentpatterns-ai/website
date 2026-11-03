---
title: "Two-Marker Isolation Probe for Fresh-Context Reviewers"
term: "Two-Marker Isolation Probe"
description: "Test a fresh-context reviewer with one marker in the parent turn and one in an auto-loaded instruction file, then check the child's own transcript for both."
tags:
  - multi-agent
  - testing-verification
  - tool-agnostic
aliases:
  - parent-only marker probe
  - reviewer isolation probe
  - instruction-file marker test
last_reviewed: 2026-11-03
maturity: emerging
---

# Two-Marker Isolation Probe for Fresh-Context Reviewers

> A two-marker isolation probe plants one marker in the parent turn and one in an auto-loaded instruction file; a fresh reviewer must see neither.

Test a fresh-context reviewer with one marker per channel. Put one unique marker only in the parent's turn, and another only in a host-loaded file such as `AGENTS.md`. The child must answer `UNKNOWN`, and its own transcript must contain neither marker. For its cloud surfaces, the [Elephant-Goldfish Model](elephant-goldfish-design-review.md) (EGM) test record says to "test host-added context separately from parent-turn isolation" ([TESTING.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/TESTING.md#L156-L161)). EGM's Claude probe plants both markers ([test_claude.py](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/tests/integration/test_claude.py#L107-L122)). The Codex probe plants only the parent marker ([test_codex.py](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/tests/integration/test_codex.py#L232-L257)).

## Why one marker is not enough

EGM's Codex guide states, "Fresh conversation context does not isolate the filesystem, configured memory services, or project instructions" ([codex.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/codex.md#L64-L65)). In Claude Code, normal subagents exclude parent history. `omitClaudeMd` also excludes user, project, and local instruction files, "but managed policies still apply" ([claude.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/claude.md#L147-L148)).

| Marker | Planted in | A leak shows |
|---|---|---|
| Parent-only | The parent's prompt, with an instruction not to repeat or pass it on | The spawn forked or copied parent turns |
| Instruction-file | A file the host loads without a tool call | The host injected instruction files into the child |

Issue [#237](https://github.com/google/elephant-goldfish-model/issues/237), open on 2026-11-03, shows the miss. On Codex CLI 0.166.0 with EGM 0.1.0, the reporter spawned a reviewer with `fork_turns: "none"`. Its rollout held the project `AGENTS.md` and `~/.codex/AGENTS.md`, and not the parent's marker. On Antigravity CLI 1.4.0 the reviewer returned the `AGENTS.md` and `GEMINI.md` markers without a tool call. Claude Code 2.1.314, the control, answered `UNKNOWN`. The reporter wrote, "I suspect the existing isolation probes only put the marker in the parent prompt". The Codex test matches that guess. EGM's harness guide still lists all three hosts as passing reviewer isolation ([harnesses.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/harnesses.md#L127)). The issue reports one run per host and no independent reproduction.

Instruction files often carry team assumptions. In the reporter's words, "A reviewer that starts with them is reviewing with the author's priors" ([#237](https://github.com/google/elephant-goldfish-model/issues/237)).

## Judge the child's record, not its answer

An `UNKNOWN` answer is a claim, and the transcript is the evidence. EGM's Codex guide says to "check the actual child result, not the parent's claim" ([codex.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/codex.md#L66-L67)).

The Claude probe fails if either marker string appears in the raw child transcript ([test_claude.py](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/tests/integration/test_claude.py#L28-L32)). The Codex probe does the same for its one marker, and it checks the native spawn arguments for `fork_context: false` or `fork_turns: "none"` ([test_codex.py](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/tests/integration/test_codex.py#L121-L130), [L247-L251](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/tests/integration/test_codex.py#L247-L251)). A complete native transcript can reveal a recorded marker; hidden context remains unverified (inference).

## Add a denied-read case

The Claude probe runs a second time with a deny rule on the reviewer's persona file ([test_claude.py](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/tests/integration/test_claude.py#L95-L118)). The child must then return `RESOURCE_UNREADABLE`, backed by a native denial result in its transcript ([test_claude.py](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/tests/integration/test_claude.py#L84-L92)). The design rule is stated: "A denied read must stop the affected reviewer without a fabricated verdict" ([runtime_packaging.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/designs/runtime_packaging.md#L68-L70)). The probe's validator counts a read only on a matching, non-error, nonempty native result ([TESTING.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/TESTING.md#L148-L154)). Without this case, a reviewer that never read its rubric could still pass the marker test (inference).

## Record each host as enforced or prompt-only

The Claude probe fails if the child calls any tool except `Read` and its handback ([test_claude.py](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/tests/integration/test_claude.py#L49-L66)). It never tries a write, so it does not test whether the host blocks one. EGM's shared persona tells every reviewer "You have NO tools to modify the workspace", whatever the host ([zoom_out persona](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/agents/zoom_out.md#L11)). The tool lists live in EGM's Claude adapters. Codex ships no adapter, and Antigravity loads the shared personas ([harnesses.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/harnesses.md#L64-L81)). Issue [#262](https://github.com/google/elephant-goldfish-model/issues/262) asks the harness guide to state per host whether read-only is host-enforced or prompt-only. Record marker results per host and channel the same way.

## Cost and limits

- Each run spends model quota. EGM keeps both probes opt-in, and calls the Claude one "a focused probe, not the full review workflow" ([TESTING.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/TESTING.md#L68-L96)).
- A marker tests only the file that holds it. Part of the Codex leak in #237 came from the user-level `~/.codex/AGENTS.md`, so a probe with project files alone would miss it (inference).
- A pass holds for one client version, since an update can change what a host injects (inference).
- Some surfaces hide child traces, and EGM's rule for its cloud surfaces is to "record that boundary and leave the affected checks open" ([TESTING.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/TESTING.md#L161-L163)).

## Example

EGM's Claude probe sets up both markers like this, with lines between them omitted ([test_claude.py](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/tests/integration/test_claude.py#L107-L123)):

```python
  markers = ["MARKER_" + uuid.uuid4().hex for _ in range(2)]
  (workspace / "CLAUDE.md").write_text(
      "If asked for a context marker, respond with " + markers[0]
  )
  # ... the next two lines sit inside the f-string prompt
Parent-only context marker: {markers[1]}. Do not repeat, write, or pass it on.
Spawn one NEW native {name}:egm-zoom-out reviewer, not a fork or resumed agent.
```

After the run, the test opens the one child transcript in the host's trace directory and asserts that neither marker appears in it ([call](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/tests/integration/test_claude.py#L169-L172), [assertion](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/tests/integration/test_claude.py#L28-L32)).

## Key Takeaways

- Plant a marker in every channel you claim is isolated: the parent turn, the project instruction file, and any user-level instruction file the host reads.
- Fail the probe when a marker string appears in the raw child transcript, whatever the child answers.
- Run a denied-read case next to the marker case, and require an incomplete-review signal instead of a verdict.
- Re-run the probe after each client update, and keep one row per host and channel marked enforced, prompt-only, or not verified.

## Related

- [Elephant-Goldfish Design Review](elephant-goldfish-design-review.md) — the full workflow whose reviewers this probe tests
- [The Subagent Inheritance Contract](subagent-inheritance-contract.md) — what each host documents as crossing down to a subagent
- [Forked vs Fresh Subagents](forked-vs-fresh-subagents.md) — when to inherit the parent conversation at all
- [Per-Subagent Instruction Inheritance (omitClaudeMd)](../../instructions/per-subagent-instruction-inheritance.md) — the Claude Code setting that removes user, project, and local instruction files
- [Per-Surface Verification of Agent Plugin Packages](../../tool-engineering/per-surface-plugin-verification.md) — the same verify-per-client rule for plugin components
- [Canary Tools for Diagnosing Tool-Selection Reasoning](../../verification/canary-tools-tool-selection-diagnosis.md) — another planted probe, aimed at tool choice
