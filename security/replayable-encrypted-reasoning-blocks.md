---
title: "Replayable Encrypted Reasoning Blocks in Agent Traces"
term: "Replayable Encrypted Reasoning Block"
description: "Encrypted chain-of-thought blocks replay across sessions, users, and sibling models, so a persisted agent trace hides data its holder cannot audit."
aliases:
  - encrypted chain-of-thought replay
  - reasoning trace recovery
  - cross-model reasoning replay
tags:
  - security
  - agent-design
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-12
maturity: emerging
---

# Replayable Encrypted Reasoning Blocks in Agent Traces

> A persisted agent trace carries encrypted reasoning blocks its holder cannot read, so publishing one ships data nobody on your side has audited.

A replayable encrypted reasoning block is a provider-returned chain-of-thought payload that any holder can resubmit to the provider's API, because the envelope carries no binding to the session, user, or model that produced it. Providers return reasoning this way to keep the API stateless: the client stores the block and passes it back on the next request. Anthropic documents both the field and its portability. "Full thinking content is encrypted and returned in the `signature` field on each thinking block", and `signature` values "are compatible across platforms (the Claude API, Amazon Bedrock, and Google Cloud). Values generated on one platform work on another" ([Anthropic, Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking)).

## When this applies

Three conditions put a harness in scope. Outside them, existing log hygiene already covers the data.

- Reasoning blocks land somewhere that outlives the conversation: a transcript file, a session export, an observability backend.
- Traces get published, as trajectory datasets, bug reports carrying raw API logs, or evaluation artifacts in a repository.
- Blocks move between models, vendors, or tenants rather than replaying into the same conversation on the same model.

## What the replay attack demonstrated

Panfilov and colleagues found that encrypted reasoning blocks from Anthropic, OpenAI, and Google were "fully compatible and interchangeable across different sessions, users, and models". Injecting a strong model's trace into a weaker, less safeguarded sibling made the sibling decode and print it verbatim, without jailbreaking the capable model ([Panfilov et al., 2026](https://arxiv.org/abs/2608.09867v1)).

The measured exposure came from traces developers had already published. Decoding 315,320 reasoning blocks scraped from 6,708 public agent trajectories on GitHub and Hugging Face surfaced 704 sensitive artifacts, 367 of them personally identifiable information and 182 of them credentials. Narrowed to genuine user sessions rather than benchmark data, the haul included 62 API keys, 33 passwords, 24 access tokens, and 7 private keys. Sixty-four of the 704 artifacts appeared nowhere in the visible chat history ([Panfilov et al., 2026](https://arxiv.org/abs/2608.09867v1)).

Portability runs the other way too. An attacker plants an opaque block in a shared trace, a victim resuming that trace replays it, and "the signed reasoning block may be interpreted as part of the model's own prior reasoning" ([Panfilov et al., 2026](https://arxiv.org/abs/2608.09867v1)). That is the read-out mirror of the write-in attack in [forged reasoning trace attacks on agent memory](forged-reasoning-trace-memory-attack.md).

The disclosure status matters. Providers were notified before publication, and the authors report they "were unable to launch the same attacks" afterward, with the headline results "no longer reproducible" as of August 2026 ([Panfilov et al., 2026](https://arxiv.org/abs/2608.09867v1)). The demonstrated decrypt path is closed. Traces published before it closed are not.

## Why it works

Statelessness was paid for with an unbound bearer token. The paper describes the returned blocks as base64-encoded AEAD envelopes whose header carries model name, version, nonce, MAC, and ciphertext. Encryption supplied confidentiality in transit and integrity, but the envelope was never bound to the user, conversation, or model that produced it, so possession alone authorized decryption ([Panfilov et al., 2026](https://arxiv.org/abs/2608.09867v1)). Once any endpoint in a provider's family accepts an arbitrary envelope, that endpoint is a decryption oracle, and the attacker's remaining problem is finding a sibling willing to print the plaintext. The proposed fixes name the missing property: embed user and conversation identifiers into the AEAD payload, and reject envelopes from a different model version at the gateway ([Panfilov et al., 2026](https://arxiv.org/abs/2608.09867v1)).

The durable consequence is an inspection asymmetry. Trace holders "have no means for decryption" and "can only operate on the plaintext level", so they will "miss reasoning hidden in encrypted blocks" ([Panfilov et al., 2026](https://arxiv.org/abs/2608.09867v1)). You cannot grep a block you cannot read, which leaves a pre-publication secret scan structurally incomplete over these fields however good the scanner is.

## When this backfires

- Stripping in the wrong place breaks the agent. Anthropic's contract requires thinking blocks to be passed back "exactly as you received it", and the API rejects blocks whose content has been modified ([Anthropic, Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking)). Strip at the publication boundary, never in flight.
- Turning off the display does not shrink the record. With `display: "omitted"` the "`signature` field still carries the encrypted full thinking for multi-turn continuity", and that field "is identical whether `display` is `summarized` or `omitted`" ([Anthropic, Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking)). A harness that hides reasoning from users has changed nothing about what its transcripts hold.
- Claiming a live decrypt overstates the evidence. The authors note their evaluation covered only API versions available in early July 2026, against proprietary schemes "subject to unannounced changes" ([Panfilov et al., 2026](https://arxiv.org/abs/2608.09867v1)). Argue from unverifiability and from already-published logs.
- Reasoning blocks are the smaller leak. Only 64 of the 704 artifacts existed solely inside reasoning ([Panfilov et al., 2026](https://arxiv.org/abs/2608.09867v1)); hardening the encrypted half while committing plaintext transcripts fixes roughly a tenth of the problem.
- In-memory-only harnesses gain nothing. Where blocks never outlive the request cycle, a stripping stage costs continuity and removes no disclosure surface.

## Example

A single thinking block looks like this on the wire, with an empty summary because `display` defaults to omitted on newer models ([Anthropic, Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking)):

```json
{
  "type": "thinking",
  "thinking": "",
  "signature": "EosnCkYICxIMMb3LzNrMu..."
}
```

Two rules apply to the same object at different boundaries. Inside the conversation, pass it back byte-identical, and include `redacted_thinking` blocks in the round trip, because filtering on `block.type == "thinking"` alone silently drops them and breaks the multi-turn protocol ([Anthropic, Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking)). At the moment the transcript leaves your trust boundary, drop the block. The paper's guidance is to "systematically strip all reasoning blocks and opaque reasoning fields from transcripts prior to public release if any form of secret or private information was exposed to the agent system" ([Panfilov et al., 2026](https://arxiv.org/abs/2608.09867v1)).

## Key Takeaways

- Classify reasoning blocks as sensitive data at rest, not as sealed data, wherever a transcript outlives the conversation.
- Put the strip at the publication boundary and nowhere else; removing blocks in flight violates the pass-back-unchanged contract and breaks tool loops ([Anthropic, Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking)).
- Ask your provider whether its envelope binds to user, conversation, and model version. That binding, rather than the presence of encryption, is what makes replay fail ([Panfilov et al., 2026](https://arxiv.org/abs/2608.09867v1)).
- Audit traces you published before August 2026 for credentials, because those blocks were decodable while they sat in public repositories ([Panfilov et al., 2026](https://arxiv.org/abs/2608.09867v1)).
- Do not let a secret scanner over the plaintext fields stand in for coverage. Trace holders "have no means for decryption", so a clean scan is silent about the encrypted field rather than clearing it ([Panfilov et al., 2026](https://arxiv.org/abs/2608.09867v1)).

## Related

- [Forged Reasoning Trace Attacks on Agent Memory (FARMA)](forged-reasoning-trace-memory-attack.md) — the write-in half of the same surface; FARMA plants fake reasoning, this page covers reading real reasoning back out
- [Embedding Inversion: Vector Stores as a Source-Text Disclosure Surface](embedding-inversion-vector-store-disclosure.md) — the same shape in a different representation, where an artifact assumed to be one-way turns out to be reversible
- [Sandbox-Enforced PII Tokenization in Agent Workflows](pii-tokenization-in-agent-context.md) — keeping the sensitive value out of the trace in the first place, the control that survives a scanner which cannot read the field
- [System Prompt as Secret Store (OWASP LLM07)](system-prompt-not-a-secret-store.md) — the same failure one field over: treating a hidden part of the request as a confidentiality boundary is the design bug, not the leak that follows
- [Agent Chat History as a First-Class Artifact](../observability/agent-history-as-artifact.md) — the persistence decision that creates the store this threat needs
