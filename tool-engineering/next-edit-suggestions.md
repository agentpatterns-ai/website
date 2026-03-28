---
title: "Next Edit Suggestions Paradigm for AI Agent Development"
description: "A proactive editing paradigm where the AI predicts both where and what to edit next, sitting between reactive autocomplete and autonomous agent mode in the assistance spectrum."
tags:
  - context-engineering
---

# Next Edit Suggestions Paradigm

> A proactive editing paradigm where the AI predicts both *where* and *what* to edit next, sitting between reactive autocomplete and autonomous agent mode in the assistance spectrum.

## Three Paradigms of AI-Assisted Editing

AI code assistance operates across three distinct paradigms, each with different initiative and scope ([GitHub Docs, features overview](https://docs.github.com/en/copilot/get-started/features)):

| Paradigm | Initiative | Scope | Trigger |
|----------|-----------|-------|---------|
| **Autocomplete** | Reactive | Token/line at cursor | Keystroke |
| **Next Edit Suggestions (NES)** | Proactive | Edit at predicted location | Change pattern detection |
| **Agent mode** | Autonomous | Multi-file changes | Explicit instruction |

Autocomplete predicts what you type next at the cursor. NES predicts where you need to edit next and what the edit should be. Agent mode plans and executes multi-file changes autonomously.

## How NES Works

NES monitors your editing patterns and predicts subsequent related edits. When it identifies a likely next edit, a gutter arrow appears indicating the location. Pressing Tab navigates to the suggestion; pressing Tab again accepts it ([VS Code docs](https://code.visualstudio.com/docs/copilot/ai-powered-suggestions)).

The key distinction from autocomplete: NES predicts edits to *existing* code at *predicted* locations, not completions of the current line at the cursor position ([VS Code docs](https://code.visualstudio.com/docs/copilot/ai-powered-suggestions)).

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

Unlike autocomplete, which fires on every keystroke, NES must suppress suggestions when they would not help. Too many suggestions break focus; too few miss opportunities. The model must infer intent from local context and decide whether a suggestion would be helpful or disruptive ([GitHub blog](https://github.blog/ai-and-ml/github-copilot/evolving-github-copilots-next-edit-suggestions-through-custom-model-training/)).

The November 2025 release demonstrated this principle with measurable results ([GitHub blog](https://github.blog/ai-and-ml/github-copilot/evolving-github-copilots-next-edit-suggestions-through-custom-model-training/)):

| Metric | Change vs. Baseline |
|--------|-------------------|
| Acceptance rate | +26.5% |
| Shown rate | -24.5% |
| Hide rate | -25.6% |

Fewer suggestions shown, more accepted, fewer dismissed. Shorter prompts, reduced response length, and increased token caching contributed to these gains.

## Configuration

NES is available in public preview across VS Code, Xcode, and Eclipse ([GitHub changelog](https://github.blog/changelog/2025-02-06-next-edit-suggestions-agent-mode-and-prompts-files-for-github-copilot-in-vs-code-january-release-v0-24/)). Business and Enterprise users require admin opt-in to "Editor Preview Features." Configure NES behavior via VS Code settings such as `github.copilot.nextEditSuggestions.enabled` ([VS Code docs](https://code.visualstudio.com/docs/copilot/ai-powered-suggestions)).

## Pattern Implications

NES surfaces a general principle applicable beyond Copilot: effective AI assistance matches the appropriate level of initiative to the task at hand.

- **Autocomplete** works for forward-moving composition where the developer knows the direction.
- **NES** works for cascading edits where one change implies others the developer would make manually.
- **Agent mode** works for well-scoped tasks where the developer can specify the goal and verify the result.

Selecting the wrong paradigm creates friction. Using agent mode for a simple rename is overhead. Using autocomplete for a cross-file refactor requires the developer to visit each location manually. NES fills the gap: proactive enough to find related edit locations for you, constrained enough to suggest only the edit rather than taking autonomous action.

## Related

- [Agent Mode](../tools/copilot/agent-mode.md)
- [Agent Backpressure](../agent-design/agent-backpressure.md)
- [Codebase Readiness](../workflows/codebase-readiness.md)
- [Convenience Loops and AI-Friendly Code](../human/convenience-loops-ai-friendly-code.md)
