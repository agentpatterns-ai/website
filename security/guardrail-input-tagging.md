---
title: "Input Tags Define a Guardrail's Inspection Scope"
term: "Guardrail Input Tagging"
description: "Bedrock input tags select the text a guardrail inspects. Configure Claude gateway tagging with its coverage limits, including unexamined tool results."
tags:
  - security
  - claude
  - context-engineering
  - agent-design
aliases:
  - guardrail input tagging
  - Bedrock prompt inspection scope
applies_to: "claude-code@2.x"
last_reviewed: 2026-11-06
maturity: emerging
---

# Input Tags Define a Guardrail's Inspection Scope

> Input tags select text for Bedrock guardrail inspection; the prompt-attack filter requires them on InvokeModel requests and does not evaluate tool results.

Input tagging tells a guardrail which prompt regions to inspect. Bedrock requires tags for prompt-attack filtering through `InvokeModel` and `InvokeModelWithResponseStream`. Without them, that filter skips those requests ([AWS prompt-attack documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-prompt-attack.html)).

Legitimate instructions can resemble attacks. AWS recommends marking user input while leaving the developer's system prompt outside evaluation. The tag selects inspection scope; it does not establish that the content is safe ([AWS guidance](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-prompt-attack.html)).

## Tagging changes other filters too

Once input tags are present, guardrails skip content outside them. Without tags, other filters process the complete prompt, while prompt-attack filtering remains the exception. Enabling tags can therefore narrow existing inspection while enabling attack detection ([AWS tagging rules](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-tagging.html)).

XML input tags apply to the two InvokeModel APIs. The Converse API uses content-block configuration instead ([AWS API scope](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-tagging.html)). For XML tags, AWS recommends a fresh random suffix per request to reduce attacks that close a predictable tag. Nesting tags is unsupported ([AWS tag syntax](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-tagging.html)).

## Choose the gateway's message scope

Claude apps gateway supports `guardrail.input_tagging` from version 2.1.316. The default adds no tags, so filters that require tagged input do not run on gateway traffic. Every Bedrock upstream must use the same value ([gateway configuration](https://code.claude.com/docs/en/claude-apps-gateway-config#add-guardrail-input-tags)).

The modes select different text:

| Mode | Tagged region |
|---|---|
| `last_message` | User messages since Claude's last reply (a tool call counts as a reply); if empty, mid-conversation system messages since that reply |
| `user_messages` | User messages |
| `all_messages` | User and assistant messages |
| `all_messages_and_system` | System prompt and every message, including mid-conversation system messages |

These modes select messages. The gateway warns of system-prompt false positives under `all_messages_and_system` and system-reminder false positives under `user_messages` ([mode definitions](https://code.claude.com/docs/en/claude-apps-gateway-config#add-guardrail-input-tags)).

With `last_message`, the next prompt can pass, and Claude then receives the blocked prompt as part of the conversation. The other modes can keep blocking until the developer removes that prompt. Test both outcomes before deployment ([gateway behavior](https://code.claude.com/docs/en/claude-apps-gateway-config#add-guardrail-input-tags)).

## Tool results remain outside prompt-attack inspection

AWS explicitly excludes tool results and tool definitions from prompt-attack evaluation ([filter limits](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-prompt-attack.html)). For a coding agent, this leaves fetched files and web pages outside that filter's coverage when they return as tool results.

Anthropic also reports that its word-filter test skipped tool results with and without tags. No tagging mode covers every request field ([gateway exclusions](https://code.claude.com/docs/en/claude-apps-gateway-config#what-input-tags-dont-cover)). Keep permission and egress controls for the actions that untrusted tool content could induce.

## Key Takeaways

- Test ordinary prompts as well as attacks before changing which text existing filters inspect.
- Include a follow-up turn in blocked-prompt tests; message scope changes how history affects later requests.
- Evaluate tool-result attacks separately. A passing prompt-filter test does not cover that input channel.

## Related

- [Subagent Return Framing](subagent-return-framing.md) — provenance markers on a different input channel
- [Per-Agent Capability Scoping](per-agent-capability-scoping.md) — restrict the actions available after content reaches an agent
- [Single-Layer Prompt Injection Defense Anti-Pattern](../patterns/anti-patterns/single-layer-injection-defence.md) — limits of relying on one filtering layer
