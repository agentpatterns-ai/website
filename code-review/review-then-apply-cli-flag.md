---
title: "Review-Then-Apply CLI Flag for In-Process Auto-Fix"
description: "The same code-review command that scores findings also writes the patch — safe only with a calibrated rubric and a clean-tree guard."
tags:
  - code-review
  - workflows
  - claude
  - tool-agnostic
aliases:
  - review-then-apply CLI flag
  - in-process review auto-fix
last_reviewed: 2026-05-27
---

# Review-Then-Apply CLI Flag for In-Process Auto-Fix

> A review-then-apply CLI flag runs the review pass and writes the patch in one invocation — safe only with a calibrated rubric and clean tree.

## When This Applies

Three conditions must hold before the pattern is safe to wire in:

- **The rubric is calibrated on template-shaped findings.** Claude Code's `/code-review --fix` ([2026-05-27 changelog](https://code.claude.com/docs/en/changelog)) targets "reuse, simplification, and efficiency suggestions" — classes where the fix has a known shape (`extract helper`, `remove unused`, `inline expression`). Apply against a freshly tuned heuristic with no false-positive baseline imports an unknown error rate as a working-tree mutation.
- **The working tree is clean, or the flag refuses.** The established precedent is `cargo fix`, which errors on a dirty tree and requires explicit `--allow-dirty` / `--allow-staged` / `--allow-no-vcs` flags ([Cargo documentation summarised on DeepWiki](https://deepwiki.com/rust-lang/cargo/9.2-code-fixing)). Without that guard the apply step destroys the recoverable state needed to inspect or revert the patch.
- **Design-judgment findings are out of scope.** Design disagreements are the dominant failure mode for unmerged agentic PRs (10 of 32 qualitatively analysed in [arxiv:2602.19441](https://arxiv.org/abs/2602.19441)). A `--fix` invocation that surfaces "extract this into a service" and then writes the extraction has converted a judgment call into a fait accompli.

Outside these conditions the convenience is net-negative versus the two-step read-report → adjudicate flow it collapses.

## The Primitive

The same agent run that scores the diff also writes the corrected version. Claude Code's `/code-review --fix` ships this shape at the CLI-tool tier; `/simplify` is an alias that invokes `/code-review --fix` directly ([Claude Code 2026-05-27 changelog](https://code.claude.com/docs/en/changelog)). The architectural move is the same one `cargo clippy --fix` ships for compiler-class lints ([Clippy usage docs](https://doc.rust-lang.org/stable/clippy/usage.html)) and that LSP code actions ship for editor-tier refactors via `codeAction/resolve` ([LSP 3.17 specification](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/)).

The CLI-flag variant is distinct from the dialog-mediated variants this site already covers: [Review-Then-Implement Loop](review-then-implement-loop.md) covers Copilot's "Implement suggestion" two-step UI dialog, and [Direct-Apply Review Comments](direct-apply-review-comments.md) covers cloud-agent commit-push flows where classification stays human. In the CLI-flag variant the same process produces and applies — there is no separate dispatch surface.

## Why It Works

Review-fix latency is dominated by per-finding context switches: read the finding, locate the code, simulate the change, write the patch, save. When N findings share a template, the per-finding cost amortises against a single rubric evaluation. Collapsing review and apply into one process removes the context switch entirely — the agent already has the file open, the parse tree built, and the candidate fix in memory. This is the same amortisation argument that makes [Batched Suggestion Application](batched-suggestion-application.md) work, applied one tier higher: there the batch is the unit of human adjudication; here the rubric is.

The keystroke saving is small. The load-bearing claim is that the review and apply steps can share state safely — that the rubric's confidence on a finding transfers without re-inspection to confidence on the patch.

## When This Backfires

- **Uncalibrated rubric** — Without a false-positive baseline, `--fix` lands wrong patches at the same speed as right ones. The empirical floor for AI suggestion quality is the [arxiv:2603.15911](https://arxiv.org/abs/2603.15911) finding that AI suggestions on 278,790 PRs were adopted at 16.6% versus 56.5% for humans, with "over half of unadopted suggestions from AI agents either incorrect or addressed through alternative fixes" — a meaningful fraction should not be applied at all.
- **Cross-cutting findings that look local** — A "simplification" of a shared utility looks line-local but mutates global behaviour when summed across callers. The same blind spot [diff-based review](diff-based-review.md) carries, amplified when no per-finding human read intervenes.
- **No idempotency contract** — Re-running `--fix` on a clean tree should be a no-op. If the rubric is non-deterministic across runs the second invocation undoes or re-edits the first, producing unstable diffs and defeating the rollback story.
- **Auto-routing of intent** — The published intent-classifier ceiling is 59.3% on a 1,828-comment dataset ([arxiv:2307.03852](https://arxiv.org/abs/2307.03852)). Wiring `--fix` to consume an unfiltered finding stream imports that 40% error rate as a write-side cost.
- **Reviewer model drift between invocations** — Two runs of the same `--fix` command against the same diff may produce different patches if the underlying model or rubric shifts. Without a pinned version "the fix" is not a reproducible artifact.

## Example

A maintainer runs `/simplify` on a feature branch with three uncommitted hunks. The invocation collapses to `/code-review --fix` ([Claude Code 2026-05-27 changelog](https://code.claude.com/docs/en/changelog)) and proceeds in one of two ways:

**Calibrated rubric on a clean tree** — the working tree has no uncommitted changes, the diff under review is the just-merged feature, and the rubric is the published reuse / simplification / efficiency one. The agent identifies three unused imports, one duplicated helper, and one expression that can be inlined. It writes the patch in a single pass. Re-running `/simplify` returns no findings — the second invocation is a no-op. The maintainer reviews the resulting diff as one commit.

**Uncalibrated rubric on a dirty tree** — the same command runs against a branch with three uncommitted hunks the maintainer is mid-edit on, and the rubric is a freshly tuned heuristic with no false-positive history. The agent writes a patch that "simplifies" a guard the maintainer added two minutes earlier for a reason that is not yet in the source. The original diff is gone; the maintainer must reconstruct it from memory. The convenience saved at most a minute; the recovery costs more.

The difference between the two runs is not the command. It is the calibration of the rubric and the state of the tree before the apply step.

## Key Takeaways

- The CLI-flag variant collapses review and apply into one process — the rubric's confidence on a finding must transfer without re-inspection to confidence on the patch.
- Three pre-conditions are load-bearing: calibrated rubric on template-shaped findings, VCS-clean working tree (or a flag that refuses), design findings out of scope.
- The cargo precedent is the safety contract: refuse to mutate a dirty tree without an explicit override, and require VCS to be present.
- Idempotency is the rollback proxy — re-running `--fix` on a clean tree must be a no-op, otherwise the rubric is not stable enough to trust.
- The pattern lives one tier in from `/code-review` (review-only) and one tier in from the dialog-mediated apply flows — it earns its place when the rubric calibration and tree state are both checked, and not before.

## Related

- [Review-Then-Implement Loop](review-then-implement-loop.md) — the dialog-mediated two-step variant where a human clicks `Implement suggestion` before the apply step runs
- [Direct-Apply Review Comments](direct-apply-review-comments.md) — the cloud-agent variant where the apply step pushes a commit to the existing PR branch
- [Batched Suggestion Application](batched-suggestion-application.md) — cluster-construction rules that govern which findings are template-shaped enough to apply in bulk
- [Agent Self-Review Loop](../agent-design/agent-self-review-loop.md) — the broader self-review-then-fix loop the CLI-flag variant compresses into a single invocation
- [Signal Over Volume in AI Review](signal-over-volume-in-ai-review.md) — the rubric-calibration discipline that determines whether `--fix` is safe to wire in
