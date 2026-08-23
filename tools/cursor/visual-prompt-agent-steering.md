---
title: "Visual-Prompt Agent Steering (Cursor Design Mode)"
description: "Direct a coding agent by clicking, multi-selecting, or sketching on a running UI — when the spatial-intent payoff beats the trade-offs in review, multimodal reasoning, and prompt-injection surface."
tags:
  - cursor
  - agent-design
aliases:
  - cursor design mode
  - visual prompt steering
  - canvas design mode
applies_to: "cursor@3.x"
last_reviewed: 2026-06-13
status: current
---

# Visual-Prompt Agent Steering (Cursor Design Mode)

> Click, multi-select, or sketch on a running UI to direct a coding agent — collapsing multi-turn text clarification into one spatially-grounded instruction.

Visual-prompt agent steering is the active form of multimodal direction: you point at the running product (or a canvas) and the agent receives element identity plus a rendered screenshot as one instruction unit. Cursor's Design Mode is the first mainstream implementation. The technique generalizes to any harness taking a `(selector, screenshot, intent)` tuple.

## When visual beats text

The technique applies when spatial intent is the load-bearing signal: layout, component placement, visual relationships, "match this to that". Text encodes those referents lossily. One Cursor Design Mode click plus "make this match" replaces a paragraph. If the text version would need DOM ancestors, pixel offsets, or siblings to be unambiguous, point instead.

For non-spatial work, the visual surface has no referent. Keep those in text.

## What the agent receives

Selecting an element gives the agent two complementary signals: element identity ("xpath, the component, attributes, computed styles, props from the fiber tree") and spatial context, a viewport screenshot capturing layout and surrounding elements ([Cursor — Design Mode, 2026-06-05](https://cursor.com/blog/design-mode)). Identity alone cannot say "match the spacing of the sibling card". The screenshot alone leaves the agent guessing which DOM node to edit. Each modality covers the other's blind spot, the property [app-window snapshots](../../context-engineering/app-window-snapshot-context.md) exploit for passive capture.

## Three multimodal patterns, one site

Three interaction shapes have shipped against AI coding harnesses, easy to conflate.

| Pattern | Direction | Surface | Example |
|---|---|---|---|
| Visual-prompt steering (this page) | Human → agent | Click / multi-select on running UI | Cursor Design Mode |
| App-window snapshot | Human → agent (passive) | Hotkey capture of any window | Codex Appshots ([page](../../context-engineering/app-window-snapshot-context.md)) |
| Interactive canvas output | Agent → human | Agent renders a chart or diagram | Cursor canvases, Claude Artifacts ([page](../../patterns/agent-design/interactive-canvas-outputs.md)) |

They share a substrate but differ in direction and cost.

## Cursor's implementation

Design Mode launched in Cursor 3.0 on 2026-04-02 as the Agents Window's browser-annotation overlay. Shortcuts: `⌘+Shift+D` toggles; `Shift+drag` selects an area; `⌘+L` adds an element to chat; `⌥+click` adds to input ([Cursor changelog 3.0](https://cursor.com/changelog/3-0)). Two June 2026 expansions extend it:

- Canvas Design Mode (2026-06-04): Design Mode now works inside agent-generated canvases, so annotate-and-target guides edits to dashboards and artifacts ([Cursor changelog](https://cursor.com/changelog)).
- Multi-select and voice (2026-06-05): clicking two or more elements gives the agent "the selected elements, their code, the surrounding layout, and the visual relationships on the page". Voice narrates edits and queues the next instruction without waiting ([Cursor — Design Mode](https://cursor.com/blog/design-mode)).

Cursor pairs it with Composer 2.5, "both fast and strong at interface work" ([Cursor — Design Mode](https://cursor.com/blog/design-mode)).

## Why it works

Spatial intent is a multi-dimensional referent that text encodes lossily. The dual signal, identity (xpath/component/computed-style/fiber-tree props) plus a screenshot, collapses the multi-turn "describe → clarify → re-describe" loop into one grounded instruction. Identity anchors where to edit. The screenshot anchors what good looks like ([Cursor — Design Mode](https://cursor.com/blog/design-mode)), the argument validated for screenshot-plus-accessibility-tree capture in [GUI agent research](https://arxiv.org/html/2507.03730v1).

## When this backfires

- Non-spatial tasks. The visual surface has no referent for renaming a function, restructuring a query, or changing an algorithm — clicking is overhead.
- Async or PR-bound review. The sketch does not travel into the pull request. Reviewers reconstruct intent from the diff, not the prompt, so the most expressive form of the instruction is lost — the same review-surface split the [Interactive Canvas Outputs page](../../patterns/agent-design/interactive-canvas-outputs.md) documents for outputs.
- Multimodal-reasoning failure regimes. For precise spatial reasoning — alignment, perspective, depth ordering — multimodal LLMs misread layout via the projection bottleneck, answering by semantic co-occurrence rather than the scene. Failures include instance merging and perspective-taking errors ([Spatial Reasoning in MLLMs, arxiv 2511.15722](https://arxiv.org/abs/2511.15722)).
- Indirect prompt injection via the captured visual. Third-party content in the page (an ad, comments, a webview) can carry hidden adversarial text the MLLM treats as instructions. Image-based injection reaches up to 64% attack success under stealth constraints, and no tested defense fully eliminates it ([Image-based Prompt Injection, arxiv 2603.03637](https://arxiv.org/abs/2603.03637v1); [Multimodal prompt injection, arxiv 2509.05883](https://arxiv.org/html/2509.05883v1)).
- Image-token budget pressure. Voice-narrated sequential edits stack viewport screenshots into one thread. Image tokens can dominate context before the agent reads its first instruction ([app-window snapshot — image-token cost](../../context-engineering/app-window-snapshot-context.md)).
- Accessibility-disadvantaged authors. Visual-pointing interfaces structurally exclude screen-reader users. Visual-prompt steering cannot be the only steering channel.

## Example

A developer is iterating on a dashboard card whose padding looks wrong next to a sibling card.

Without visual-prompt steering — a text instruction:

```
In src/components/MetricCard.tsx, reduce the inner padding on the card
wrapper so its vertical rhythm matches StatsCard. I think StatsCard
uses py-4 px-6 — match those. Also the title spacing looks tight.
```

The agent guesses which padding is wrong, may pick the wrong sibling, and "title spacing looks tight" is ambiguous without the screenshot.

With visual-prompt steering (Cursor Design Mode):

1. `⌘+Shift+D` toggles Design Mode in the running browser.
2. `⌥+click` the misaligned `MetricCard`, then `⌥+click` the reference `StatsCard` (multi-select).
3. Type "match the second card's vertical rhythm and tighten the title gap to half its current value."

The agent receives both elements' identity (component, computed styles, fiber-tree props) plus the screenshot showing the visual relationship. It locates `MetricCard.tsx` and `StatsCard.tsx`, reads the current padding tokens, and proposes a diff. The instruction names intent. The visual surface carries the spatial referent.

## Key Takeaways

- Visual-prompt steering directs an agent by pointing at a running UI; the agent receives element identity plus a rendered screenshot as one instruction unit
- The technique pays off when spatial intent is the load-bearing signal and adds friction when the change is non-spatial
- Cursor Design Mode is today's reference implementation; multi-select and Canvas Design Mode (June 2026) extend it beyond browser elements
- The technique sits alongside interactive canvas *outputs* and passive window-snapshot *capture* — the active-direction variant of multimodal interaction
- Trade-offs cluster around PR-bound review, multimodal spatial reasoning failures, image-based prompt injection, image-token budget pressure, and accessibility — text must remain a first-class channel

## Related

- [Cursor 3 Agents Window](agents-window.md) — the surface Design Mode lives inside; the original overlay shipped here in Cursor 3.0
- [App-Window Snapshot as Agent Context](../../context-engineering/app-window-snapshot-context.md) — the passive-capture sibling: hotkey-bound window snapshot rather than intentional annotation
- [Interactive Canvas Outputs](../../patterns/agent-design/interactive-canvas-outputs.md) — the agent-as-author variant of canvas interaction; same substrate, opposite direction
- [Live Browser as Agent Context Channel](../../context-engineering/live-browser-context-channel.md) — the channel Design Mode uses to read the running app
- [Prompt Injection Threat Model](../../security/prompt-injection-threat-model.md) — the indirect-injection surface multimodal capture opens
