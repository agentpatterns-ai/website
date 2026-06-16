---
title: "Stale AI Configuration Artifacts (Context Rot)"
term: "Stale AI Configuration Artifacts"
description: "Treating CLAUDE.md, AGENTS.md, and .cursorrules as set-and-forget documentation leaves stale code references that mislead the agent — 23% of repos in one study."
tags:
  - anti-pattern
  - instructions
  - context-engineering
  - tool-agnostic
  - arxiv
last_reviewed: 2026-06-13
maturity: emerging
---

# Stale AI Configuration Artifacts (Context Rot)

> AI configuration files drift out of sync with the code they describe; the agent loads stale guidance as authoritative context and confabulates around the gap.

CLAUDE.md, AGENTS.md, and `.cursorrules` are documentation — they describe code elements, paths, and conventions to a downstream reader, and they decay the same way every other documentation artifact decays as code evolves around them. Treude & Baltes (June 2026) call this drift **context rot** and show that an off-the-shelf README/wiki consistency checker, retargeted at AI configuration files in **356 repositories**, flagged stale code element references in **23%** of them ([arxiv 2606.09090](https://arxiv.org/abs/2606.09090)).

## Disambiguation

"Context rot" is overloaded in 2026 practitioner writing. This page is the artifact-drift sense from Treude & Baltes ([arxiv 2606.09090](https://arxiv.org/abs/2606.09090)) — config files going stale as code moves underneath them. The unrelated usage — output quality degrading as the context window fills with conversation history — is a different phenomenon ([Morph LLM](https://www.morphllm.com/context-rot)), covered under [The Infinite Context](infinite-context.md).

## The Pattern

Developers seed a project with CLAUDE.md or AGENTS.md early — often via `/init` — listing real paths, function names, conventions, and architectural rules. The file is treated as one-time setup. Code then evolves: files get renamed, modules move, helpers get deleted. Nothing in the toolchain notices the configuration no longer matches the repository — the file is plain Markdown, not code, not tested, not type-checked.

## Why It Fails

The agent loads the artifact at session start and treats it as authoritative context. When a referenced file no longer exists at the claimed path, two failure modes dominate ([Code Coin Cognition](https://codecoincognition.substack.com/p/your-claudemd-is-lying-to-your-ai)):

- **Confabulation.** The agent reasons as if the stale reference were current — importing a deleted helper, calling a renamed function, or extending a refactored module shape that no longer exists.
- **Token waste.** The agent searches for the missing artifact, fails, and burns turns explaining why it cannot find what the config promised.

Severity compounds because a stale reference in a README is read by a human who notices; a stale reference in CLAUDE.md shapes every downstream agent decision silently.

## Why It Works (the remediation mechanism)

The Treude & Baltes contribution is mechanistic: AI configuration artifacts are *functionally* documentation, so the consistency tooling studied for decades against READMEs, code comments, API docs, and architecture descriptions applies unchanged when retargeted at the new file glob ([arxiv 2606.09090](https://arxiv.org/abs/2606.09090)). Existing checkers parse code element references out of the artifact and verify each still resolves against the current codebase — failing CI on a stale reference the same way a unit test fails on a broken contract. The 23%-of-356-repos result is the load-bearing evidence the technique transfers.

## When This Backfires

Consistency checking adds cost — CI minutes, false-positive triage, ownership friction — and the value depends on what the artifact contains:

- **Minimal pointer-style configs.** A CLAUDE.md that is a 30-line pointer table with zero direct code references has nothing to drift. Stripping references can beat policing them — [Evaluating AGENTS.md](../instructions/evaluating-agents-md-context-files.md) finds that auto-generated, code-reference-heavy context files reduce success rates while adding cost, so minimisation is mechanistically compatible.
- **Pre-stabilisation prototypes.** When the codebase reshapes weekly, the config will be wrong before any check completes; defer authoring until structure settles.
- **Solo or short-lived repos.** The silent-failure mode of a stale CLAUDE.md depends on the author no longer remembering current code shape. On a solo project the author has the state in head and the agent's confusion surfaces in the conversation.
- **Tool loaders that filter the file.** If the agent only reads a subset (matching headings, size-capped prefix), checker findings on the unloaded portion are theatrical — the agent never saw the stale reference.

## Example

**Before — set-and-forget config file with stale references:**

```markdown
# CLAUDE.md
- Auth lives in `src/auth/jwt.ts`. Use `verifyToken()` for session checks.
- Run integration tests with `pnpm test:int`.
- Database migrations live in `db/migrations/` — add files numbered sequentially.
```

Six weeks later: `src/auth/` was rewritten as `src/identity/`, `verifyToken()` was renamed `validateSession()`, the package manager switched to `bun`, and the migrations directory moved to `infra/migrations/`. The file still ships unchanged. The next agent session calls a function that no longer exists and runs a test command that no longer resolves.

**After — code-element references treated as a consistency contract:**

The shape Treude & Baltes apply in [the paper](https://arxiv.org/abs/2606.09090) is a CI step that parses code element references out of the configuration artifact, verifies each resolves against the current codebase, and fails the build on a miss — the same mechanism a README/wiki consistency checker uses, retargeted at the `CLAUDE.md` / `AGENTS.md` file glob. The fix when the check fails is mechanical: rename the references when the code moves, before the agent ever loads the stale file. The paper validates this shape against 356 repos; an in-project implementation is a small parser plus an existence check, not a new tool category.

## Key Takeaways

- CLAUDE.md and AGENTS.md are documentation; they decay like documentation. The empirical rate is 23% of repos in a 356-repo sample carrying stale code element references ([arxiv 2606.09090](https://arxiv.org/abs/2606.09090)).
- Existing README/API-doc consistency checkers retarget cleanly at AI configuration artifacts — the underlying problem is decades old.
- "Context rot" is overloaded — this page is about artifact drift, not in-context-window attention degradation; do not conflate them.
- Minimisation is a complementary remediation: configs that contain no code references cannot rot; consider stripping over policing where the file is verbose for no compliance gain.

## Related

- [Evaluating AGENTS.md: When Context Files Hurt More Than Help](../instructions/evaluating-agents-md-context-files.md) — empirical evidence that verbose code-reference-heavy context files already trade success for cost; rot compounds the cost without recovering the success.
- [CLAUDE.md Convention for Structuring Agent Instructions](../instructions/claude-md-convention.md) — the artifact this page describes the failure mode of.
- [Context Poisoning: When Hallucinations Become Premises](context-poisoning.md) — the downstream failure once the stale reference enters reasoning as a premise.
- [The Infinite Context](infinite-context.md) — the *other* meaning of "context rot" the lede disambiguates against.
- [Pattern Replication Risk](pattern-replication-risk.md) — the related compounding failure where agents propagate whatever they find in the repo, stale references included.
