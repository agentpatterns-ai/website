---
title: "Next Edit Suggestions Paradigm for AI Agent Development"
description: "A proactive editing paradigm where the AI predicts both where and what to edit next, sitting between reactive autocomplete and autonomous agent mode in the assistance spectrum."
aliases:
  - NES
  - next-edit completions
tags:
  - context-engineering
---

# Next Edit Suggestions Paradigm

> A proactive editing paradigm where the AI predicts both *where* and *what* to edit next, sitting between reactive autocomplete and autonomous agent mode in the assistance spectrum.

## Three Paradigms of AI-Assisted Editing

Next Edit Suggestions is a proactive editing mode: it watches your edits in progress and predicts the next location and change you will need to make, rather than waiting for you to position your cursor and type. This fills the gap between line-level autocomplete (reactive, cursor-bound) and agent mode (autonomous, multi-file). AI code assistance operates across three distinct paradigms, each with different initiative and scope ([GitHub Docs, features overview](https://docs.github.com/en/copilot/get-started/features)):

| Paradigm | Initiative | Scope | Trigger |
|----------|-----------|-------|---------|
| **Autocomplete** | Reactive | Token/line at cursor | Keystroke |
| **Next Edit Suggestions (NES)** | Proactive | Edit at predicted location | Change pattern detection |
| **Agent mode** | Autonomous | Multi-file changes | Explicit instruction |

## How NES Works

NES monitors your editing patterns and predicts the next related edit. A gutter arrow indicates the location; pressing Tab navigates to it, pressing Tab again accepts it ([VS Code docs](https://code.visualstudio.com/docs/copilot/ai-powered-suggestions)).

The key distinction from autocomplete: NES predicts edits to *existing* code at *predicted* locations, not completions at the cursor ([VS Code docs](https://code.visualstudio.com/docs/copilot/ai-powered-suggestions)).

### Core Use Cases

**Error correction.** Typos, inverted conditionals, incorrect operators. NES detects the error pattern and suggests the fix at the right location ([VS Code docs](https://code.visualstudio.com/docs/copilot/ai-powered-suggestions)).

**Intent propagation.** Rename `Point` to `Point3D` in one location, and NES suggests cascading updates throughout dependent code. The edit intent propagates from a single change to all affected locations ([VS Code docs](https://code.visualstudio.com/docs/copilot/ai-powered-suggestions)).

**Refactoring assistance.** After pasting code, NES suggests style adjustments to match surrounding conventions. Variable renames, formatting alignment, and pattern consistency across related code sections ([VS Code docs](https://code.visualstudio.com/docs/copilot/ai-powered-suggestions)).

## Custom Model Architecture

NES does not use a general-purpose LLM. It runs a purpose-built, low-latency, task-specific model designed for real-time in-editor response. General frontier models were "accurate but too slow for an in-editor experience" ([GitHub blog](https://github.blog/ai-and-ml/github-copilot/evolving-github-copilots-next-edit-suggestions-through-custom-model-training/)).

### Training on Editing Sessions, Not Code Snapshots

PR diffs were insufficient for training because they "show only the final state, not the intermediate edits." The team collected real editing session data from internal volunteers, capturing the temporal sequence of changes rather than just before/after states. A smaller volume of high-quality edit data produced better models than larger volumes of less curated data ([GitHub blog](https://github.blog/ai-and-ml/github-copilot/evolving-github-copilots-next-edit-suggestions-through-custom-model-training/)).

### Reinforcement Learning Refinement

Supervised fine-tuning teaches good edits but cannot explicitly penalize bad ones. The team applied reinforcement learning using a "large reasoning model with specific grading criteria" to identify qualities of unhelpful suggestions. This helps NES "better avoid generating bad edit suggestions when faced with out-of-distribution cases" ([GitHub blog](https://github.blog/ai-and-ml/github-copilot/evolving-github-copilots-next-edit-suggestions-through-custom-model-training/)).

## Knowing When Not to Suggest

NES must suppress suggestions that would not help — too many break focus; too few miss opportunities. The model infers intent from local context to decide whether a suggestion would be helpful or disruptive ([GitHub blog](https://github.blog/ai-and-ml/github-copilot/evolving-github-copilots-next-edit-suggestions-through-custom-model-training/)).

The November 2025 release demonstrated this principle with measurable results ([GitHub blog](https://github.blog/ai-and-ml/github-copilot/evolving-github-copilots-next-edit-suggestions-through-custom-model-training/)):

| Metric | Change vs. Baseline |
|--------|-------------------|
| Acceptance rate | +26.5% |
| Shown rate | -24.5% |
| Hide rate | -25.6% |

Fewer suggestions shown, more accepted, fewer dismissed.

## Configuration

NES is available in VS Code ([GitHub changelog](https://github.blog/changelog/2025-02-06-next-edit-suggestions-agent-mode-and-prompts-files-for-github-copilot-in-vs-code-january-release-v0-24/)). Business and Enterprise users require admin opt-in to "Editor Preview Features." Configure NES behavior via the VS Code setting `github.copilot.nextEditSuggestions.enabled` ([VS Code docs](https://code.visualstudio.com/docs/copilot/ai-powered-suggestions)).

## Pattern Implications

NES surfaces a general principle: match the AI's initiative level to the task.

- **Autocomplete** works for forward-moving composition where the developer knows the direction.
- **NES** works for cascading edits where one change implies others the developer would make manually.
- **Agent mode** works for well-scoped tasks where the developer can specify the goal and verify the result.

Selecting the wrong paradigm creates friction. Using agent mode for a simple rename is overhead. Using autocomplete for a cross-file refactor requires visiting each location manually. NES fills the gap: proactive enough to find related edit locations, constrained enough to suggest only the edit rather than taking autonomous action.

## When This Backfires

- **Exploratory sessions.** When the developer doesn't yet know what the code should look like, NES suggestions may reflect a pattern that doesn't exist — producing noise rather than useful propagation.
- **Semantic refactors.** NES propagates syntactic patterns; it does not understand semantic intent. Renaming a method whose callers need different argument signatures produces plausible but wrong suggestions.
- **Divergent intent.** Two changes sharing surface similarity but different purpose (e.g., `count` in two unrelated loops) cause NES to suggest the second change incorrectly. Dismissing it adds interruption.
- **Editor availability.** NES is currently a VS Code feature. Teams on other editors must use agent mode or manual multi-location edits instead.

## Example

A developer renames a TypeScript interface property from `userId` to `accountId` in one file. NES detects the rename pattern and places a gutter arrow at the next usage of `userId` in the same file. Pressing Tab jumps to that location; pressing Tab again accepts the suggested replacement `accountId`. The developer continues pressing Tab to navigate and accept each cascading change across the file — function parameters, destructuring assignments, JSDoc references — without manually searching for each occurrence.

For cross-file propagation, the same Tab-Tab workflow applies: NES surfaces usages in imported modules or test files as gutter arrows, navigating the developer to each location in turn. The developer retains full control — pressing Escape at any arrow dismisses that suggestion without accepting it.

Configuration: enable with `"github.copilot.nextEditSuggestions.enabled": true` in VS Code settings. The feature is on by default for individual accounts; Business and Enterprise require admin opt-in to Editor Preview Features.

## When This Backfires

**IDE coverage is limited.** NES is available in VS Code, Xcode, and Eclipse. Developers using JetBrains IDEs, Neovim, or Emacs get no NES support regardless of Copilot subscription tier.

**Business/Enterprise admin friction.** NES requires admin opt-in to "Editor Preview Features" for Business and Enterprise orgs. Teams in security-sensitive or locked-down environments may wait weeks for enablement, making NES unavailable when needed.

**Tab key conflict.** The Tab-to-navigate, Tab-to-accept interaction conflicts with Tab-for-indentation habits and with snippets or other extensions that use Tab. Developers with strong Tab muscle memory from non-Copilot workflows report false acceptances during the learning period.

**Overloaded symbol semantics.** When a renamed symbol has different meanings in different contexts (e.g., `id` used as both a DOM attribute and a database key), NES may suggest cascading updates that conflate the two. The model infers intent from local edit patterns; it cannot distinguish semantically distinct uses of the same identifier.

**Suggestion noise during exploratory edits.** When a developer is actively exploring a refactor — making and undoing changes to evaluate an approach — NES fires suggestions on every intermediate edit. This can create visual noise and interrupt the exploratory flow before intent is settled.

## Related

- [Agent Mode](../tools/copilot/agent-mode.md)
- [Agent Backpressure](../agent-design/agent-backpressure.md)
- [Codebase Readiness](../workflows/codebase-readiness.md)
- [Convenience Loops and AI-Friendly Code](../human/convenience-loops-ai-friendly-code.md)
