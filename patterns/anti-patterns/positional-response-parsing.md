---
title: "Positional Response Parsing: Reading content[0].text"
term: "Positional Response Parsing"
description: "Reading content[0].text breaks when a thinking-default model puts a thinking block first. The bug passes trivial tests, so parse by block type instead."
tags:
  - agent-design
  - testing-verification
  - tool-agnostic
  - anti-pattern
aliases:
  - content[0].text
  - first-block response parsing
  - positional content indexing
last_reviewed: 2026-10-04
maturity: emerging
---

# Positional Response Parsing

> Positional response parsing reads a model reply by index, such as `content[0].text`, and breaks when a reasoning model puts a thinking block first.

## The pattern

Positional response parsing is reading the model's text from a fixed index in the response, usually `response.content[0].text`. The Messages API returns `content` as an ordered list of typed blocks, and thinking blocks come before the text they lead to ([Anthropic, Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking)). The API documents block types. It does not document block positions.

The habit was safe while models ran with thinking off by default, because block 0 was then the text. That default has changed. With no `thinking` field, Claude Opus 5.5, Opus 5, Sonnet 5.5, Sonnet 5, Fable 5.1, Mythos 5.1, Fable 5 and Mythos 5 run adaptive thinking, and so does Mythos Preview. Opus 4.8, Opus 4.7, Opus 4.6, Sonnet 4.6, Opus 4.5, Sonnet 4.5 and Haiku 4.5 run with thinking off ([Anthropic, Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking)).

## When the pattern is a bug

The pattern is a bug on thinking-default models, and on any code that will move to one. On a model with thinking off and no `thinking` field, `content[0].text` still returns the text. Nothing breaks until someone changes the model ID.

The Sonnet 5.5 migration guide says which code is exposed: "Code that ran without thinking needs all three items. Code from Claude Sonnet 5 likely has the first two." Reading content blocks by `type` is the first item ([Anthropic, Sonnet 5.5 migration guide](https://platform.claude.com/docs/en/models/sonnet-5-5/migration-guide)). The Opus 5.5 guide names `content[0].text` as well ([Anthropic, Opus 5.5 migration guide](https://platform.claude.com/docs/en/models/opus-5-5/migration-guide)).

## Why it fails

Adaptive thinking decides per request whether to think. The Steering thinking page says "No level guarantees a thinking block on every request" and "A simple factual question may get a direct response with no thinking block at all" ([Anthropic, Steering thinking](https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost)). So the index of the first text block changes from one call to the next.

That makes the defect easy to ship. A smoke test with a trivial prompt gets a text-only reply and passes. A harder prompt gets a thinking block first, and the read fails. The amd/gaia project logged this on one prompt: for `say OK`, `claude-opus-5` returned block types `['thinking', 'text']` and `claude-sonnet-5` returned `['text']` ([amd/gaia #3884](https://github.com/amd/gaia/issues/3884)).

In the Python SDK the failure is a crash. `ThinkingBlock` declares `signature`, `thinking` and `type`, and has no `text` field ([anthropic-sdk-python](https://github.com/anthropics/anthropic-sdk-python/blob/main/src/anthropic/types/thinking_block.py)). The deepeval project reported the result: "the API returns `content=[ThinkingBlock, TextBlock, ...]`, and `ThinkingBlock` has no `.text`. Every metric evaluation using that judge then dies with an `AttributeError`." ([confident-ai/deepeval #2946](https://github.com/confident-ai/deepeval/issues/2946)). The HTTP call still returns 200, so the gaia report says the failure is "easy to mistake for a caller's bug" ([amd/gaia #3884](https://github.com/amd/gaia/issues/3884)).

Both reports come from eval and judge code. A judge that parses the first block breaks inside the harness meant to catch regressions.

The trap is not specific to one vendor. OpenAI's Responses API documents that the `output` array often holds more than one item, such as tool calls and reasoning items, so the text is not safe to assume at `output[0].content[0].text`. Its SDKs offer an `output_text` property that aggregates all text outputs ([OpenAI, Text generation](https://developers.openai.com/api/docs/guides/text)).

## The fix

Select blocks by `type`, and join every text block. Joining matters because "Responses may now include multiple text blocks where each text block can contain a claim that Claude is making and a list of citations that support the claim" ([Anthropic, Citations](https://platform.claude.com/docs/en/build-with-claude/citations)). A first-match fix still truncates a cited answer. The loop in the Sonnet 5.5 launch post reads each block by type for the same reason: "The loop reads each block by type because Sonnet 5.5 thinks by default, so a response can begin with a thinking block, and code that reads content[0].text breaks." ([claude.dev](https://claude.dev/blog/building-with-claude-sonnet-5-5/)).

Three cases need three shapes:

- Display or parse: join the text of every block whose `type` is `"text"`.
- Streaming: the Opus 5.5 migration guide names "a stream handler that treats the first `content_block_start` event as text" as a break of its own. Branch on the block type when handling stream events ([Anthropic, Opus 5.5 migration guide](https://platform.claude.com/docs/en/models/opus-5-5/migration-guide)).
- Replay in a tool loop: send the whole assistant turn back unchanged. Filtering on `block.type == "thinking"` alone silently drops `redacted_thinking` blocks and breaks the multi-turn protocol ([Anthropic, Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking)).

Turning thinking off does not reliably restore the old shape. Opus 5.5 returns a 400 for `"disabled"`. Sonnet 5.5 also rejects `"disabled"`, and accepts `between_tools` only at `high` effort or below. With tools, the progress updates between calls still come back as thinking blocks ([Anthropic, Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking), [claude.dev](https://claude.dev/blog/building-with-claude-sonnet-5-5/)).

## Example

**Before — index assumes the text is block 0:**

```python
response = client.messages.create(model=MODEL, max_tokens=1024, messages=messages)
data = json.loads(response.content[0].text)  # AttributeError when block 0 is a ThinkingBlock
```

**After — select by type and join:**

```python
def reply_text(message) -> str:
    return "".join(b.text for b in message.content if b.type == "text")

response = client.messages.create(model=MODEL, max_tokens=1024, messages=messages)
data = json.loads(reply_text(response))
```

In a tool loop, append `response.content` to the history as it is. Do not pass it through `reply_text`.

## How to detect it

A live test against the API cannot be trusted to find this bug, because adaptive thinking may skip an easy prompt. Test the parser with a fixture. Build a message whose content starts with a thinking block, then assert on the text. The test needs no API call.

```python
from types import SimpleNamespace as NS

def test_reply_text_skips_thinking_block():
    message = NS(content=[NS(type="thinking", thinking=""), NS(type="text", text="ok")])
    assert reply_text(message) == "ok"
```

A grep gate in CI covers the rest of the codebase. Search for `content\[[0-9]\]\.text` and check each hit against the model it runs on.

## When this backfires

Replacing the index has a cost, and sometimes the cost buys nothing.

- Models with thinking off. On Opus 4.5 or Haiku 4.5 with no `thinking` field, `content[0].text` is correct today. Rewriting it adds diff noise and fixes nothing until the model ID changes. Anthropic's own use-case guides still use `content[0].text` with Haiku 4.5 ([Anthropic, llms-full.txt](https://platform.claude.com/llms-full.txt)).
- Teaching snippets. `content[0].text` is one short line that every reader recognizes, and a helper adds lines that teach nothing about the pattern on show. The counter-risk is that readers copy the line and swap in a current model ID.
- Replay code. Filtering by type is right for display and wrong for replay.
- Streaming code. Iterating `response.content` does nothing for a stream handler, so a page that shows only the non-streaming fix leaves streaming callers broken.

## Key Takeaways

- Read model output by block type and join every text block. Do not read it by index.
- On a thinking-default model the first block can be a thinking block, and adaptive thinking decides per request, so a trivial test prompt hides the bug.
- The break covers every model that runs adaptive thinking with no `thinking` field, not one release.
- Streaming handlers and tool-loop replay need their own fixes.
- Test the parser with a hand-built message that starts with a thinking block.

## Related

- [Perceived Model Degradation](perceived-model-degradation.md) — pinning model versions and building eval suites
- [Silent Adoption of Corrupted Tool Returns](silent-adoption-of-corrupted-tool-returns.md) — failures that pass unnoticed
- [Unsignalled Tool Failure](unsignalled-tool-failure-envelope.md) — success envelopes around unusable payloads
- [Framework-First Agent Development](framework-first.md) — raw LLM API understanding before abstraction
