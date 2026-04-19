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

Next Edit Suggestions watches edits in progress and predicts the next location and change, rather than waiting for the cursor to arrive. It fills the gap between line-level autocomplete (reactive, cursor-bound) and agent mode (autonomous, multi-file) ([GitHub Docs, features overview](https://docs.github.com/en/copilot/get-started/features)).

| Paradigm | Initiative | Scope | Trigger |
|----------|-----------|-------|---------|
| **Autocomplete** | Reactive | Token/line at cursor | Keystroke |
| **Next Edit Suggestions (NES)** | Proactive | Edit at predicted location | Change pattern detection |
| **Agent mode** | Autonomous | Multi-file changes | Explicit instruction |

## How NES Works

NES monitors editing patterns and predicts the next related edit. A gutter arrow marks the location; Tab navigates to it, Tab again accepts it. The key distinction from autocomplete: NES predicts edits to *existing* code at *predicted* locations, not completions at the cursor ([VS Code docs](https://code.visualstudio.com/docs/copilot/ai-powered-suggestions)).

### Core Use Cases

- **Error correction.** Typos, inverted conditionals, incorrect operators.
- **Intent propagation.** Rename `Point` to `Point3D` once, and NES suggests cascading updates across dependent code.
- **Refactoring assistance.** After pasting code, NES suggests style adjustments to match surrounding conventions ([VS Code docs](https://code.visualstudio.com/docs/copilot/ai-powered-suggestions)).

## Custom Model Architecture

NES does not use a general-purpose LLM. It runs a purpose-built, low-latency, task-specific model designed for real-time in-editor response — frontier models were "accurate but too slow for an in-editor experience" ([GitHub blog](https://github.blog/ai-and-ml/github-copilot/evolving-github-copilots-next-edit-suggestions-through-custom-model-training/)).

### Training on Editing Sessions, Not Code Snapshots

PR diffs were insufficient because they "show only the final state, not the intermediate edits." The team collected real editing session data from internal volunteers, capturing the temporal sequence of changes. A smaller volume of high-quality edit data produced better models than larger volumes of less curated data ([GitHub blog](https://github.blog/ai-and-ml/github-copilot/evolving-github-copilots-next-edit-suggestions-through-custom-model-training/)).

### Reinforcement Learning Refinement

Supervised fine-tuning teaches good edits but cannot explicitly penalize bad ones. The team applied reinforcement learning using a "large reasoning model with specific grading criteria" to help NES "better avoid generating bad edit suggestions when faced with out-of-distribution cases" ([GitHub blog](https://github.blog/ai-and-ml/github-copilot/evolving-github-copilots-next-edit-suggestions-through-custom-model-training/)).

## Knowing When Not to Suggest

NES must suppress suggestions that would not help — too many break focus; too few miss opportunities. The November 2025 release reported ([GitHub blog](https://github.blog/ai-and-ml/github-copilot/evolving-github-copilots-next-edit-suggestions-through-custom-model-training/)):

| Metric | Change vs. Baseline |
|--------|-------------------|
| Acceptance rate | +26.5% |
| Shown rate | -24.5% |
| Hide rate | -25.6% |

Fewer suggestions shown, more accepted, fewer dismissed.

## Configuration

NES is generally available in VS Code and Visual Studio, and in public preview for JetBrains IDEs ([GitHub changelog, Aug 2025](https://github.blog/changelog/2025-08-29-copilots-next-edit-suggestion-nes-in-public-preview-in-jetbrains/)) and for Xcode and Eclipse ([GitHub changelog, Nov 2025](https://github.blog/changelog/2025-11-18-github-copilot-next-edit-suggestions-nes-now-in-public-preview-for-xcode-and-eclipse/)). Business and Enterprise users require admin opt-in to "Editor Preview Features." In VS Code, toggle `github.copilot.nextEditSuggestions.enabled` ([VS Code docs](https://code.visualstudio.com/docs/copilot/ai-powered-suggestions)).

## Pattern Implications

NES surfaces a general principle: match the AI's initiative level to the task.

- **Autocomplete** works for forward-moving composition where the developer knows the direction.
- **NES** works for cascading edits where one change implies others the developer would make manually.
- **Agent mode** works for well-scoped tasks where the developer can specify the goal and verify the result.

Selecting the wrong paradigm creates friction: agent mode for a simple rename is overhead; autocomplete for a cross-file refactor requires visiting each location manually. NES fills the gap — proactive enough to find related edit locations, constrained enough to suggest only the edit rather than take autonomous action.

## When This Backfires

- **Exploratory sessions.** When the target shape of the code is unsettled, NES suggestions reflect a pattern that doesn't yet exist — noise rather than useful propagation.
- **Semantic refactors.** NES propagates syntactic patterns; it does not reason about semantic intent. Renaming a method whose callers need different argument signatures produces plausible-but-wrong suggestions.
- **Overloaded symbol semantics.** When a renamed symbol has different meanings in different contexts (e.g., `id` as both a DOM attribute and a database key), NES conflates the two.
- **Tab key conflict.** Tab-to-navigate and Tab-to-accept conflict with Tab-for-indentation habits and with snippet extensions, causing false acceptances during the learning period.
- **Admin friction.** Business and Enterprise orgs require admin opt-in to "Editor Preview Features" ([VS Code docs](https://code.visualstudio.com/docs/copilot/ai-powered-suggestions)), delaying availability in locked-down environments.

## Example

A developer renames a TypeScript interface property from `userId` to `accountId` in one file. NES detects the rename and places a gutter arrow at the next usage of `userId`. Tab jumps to the location; Tab again accepts the replacement. The developer continues Tab-Tab across function parameters, destructuring assignments, and JSDoc references — and, via the same gutter-arrow flow, through imported modules and test files — without manually searching for occurrences. Escape at any arrow dismisses that suggestion.

## Key Takeaways

- NES sits between autocomplete and agent mode: proactive enough to find related edit locations, constrained enough to suggest only the edit rather than act autonomously.
- It runs a purpose-built low-latency model, trained on editing sessions rather than PR diffs, and refined with RL to suppress unhelpful suggestions.
- Match the paradigm to the task: autocomplete for forward composition, NES for cascading edits, agent mode for well-scoped goals.
- NES is GA in VS Code and Visual Studio and in public preview for JetBrains, Xcode, and Eclipse — admin opt-in is required for Business/Enterprise orgs.

## Related

- [Agent Mode](../tools/copilot/agent-mode.md)
- [Agent Backpressure](../agent-design/agent-backpressure.md)
- [Codebase Readiness](../workflows/codebase-readiness.md)
- [Convenience Loops and AI-Friendly Code](../human/convenience-loops-ai-friendly-code.md)
