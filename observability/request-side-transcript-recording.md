---
title: "Record the Request Side to Make a Transcript Replayable"
term: "Request-Side Transcript Recording"
description: "Claude Code 2.1.300 adds each API request's system prompt, tools, and parameters to the local transcript, but sharing still needs a disclosure check and replay environment."
tags:
  - observability
  - claude
  - workflows
aliases:
  - request-recording transcript
  - replayable agent transcript
last_reviewed: 2026-10-28
maturity: emerging
---

# Record the Request Side to Make a Transcript Replayable

> Recording each request's system prompt, tools, and parameters in a transcript can make that request reproducible.

A shared transcript helps reproduce a request when the reader can provide the recorded tools and parameters. Check the transcript for sensitive data and share only what the recipient is authorized to receive. A scan can miss credentials. Recording the request adds to what the hand-off discloses. The Claude Code 2.1.300 release "Changed local session transcripts to also record each API request's system prompt, tools and parameters, so a transcript you choose to share can reproduce a request exactly" ([Claude Code changelog 2.1.300](https://code.claude.com/docs/en/changelog#2-1-300)). The entry covers the request only, and sharing stays your choice.

## Why the request side cannot be reconstructed

The 2.1.300 changelog describes three ways the tool set the model sees could drift mid-conversation:

- After the API rejected an MCP tool's input schema, "Claude Code now sends that tool without parameters for the rest of the conversation". The tool is still listed; its parameters are gone.
- An MCP server that "finished connecting after a compaction" left Claude not told about its tools and instructions until its next tool call.
- Automatic tool search could turn "off part-way through a conversation, for example while MCP servers reconnect after a resume" ([Claude Code changelog 2.1.300](https://code.claude.com/docs/en/changelog#2-1-300)).

Each means the tool set as sent at turn 20 differs from what the repository declares. Only a per-turn record shows the difference.

## Why it works

A reader holding only the messages must infer the system prompt, tools, and parameters. Recording them removes the inference. The reproducibility literature names the gap between holding an artifact and being able to run it. A study of 640 LLM-for-software-engineering papers found that artifact-evaluation badges "often signal artifact presence but do not consistently guarantee execution fidelity or long-term reproducibility" ([Siddiq et al., 2025](https://arxiv.org/abs/2512.00651v1)).

## When this backfires

- The transcript crosses a trust boundary. The record carries each request's system prompt, tools, and parameters. Credentials can also enter through tool outputs, shell logs, and file reads. Xia and Park study that leakage toward the model provider: "LLM agents can leak privacy (e.g., paths, emails) and credentials (e.g., API keys) as agent observations (e.g., tool outputs, shell logs, and file reads) are appended to provider-bound transcripts". They call existing placeholder redaction brittle: it "can miss embedded or cross-turn references, over-redact benign lookalikes, and destroy the structure useful for reasoning" ([Xia and Park, 2026](https://arxiv.org/abs/2607.17147v1)). Their setting is provider-bound transcripts, not sharing with another person. Applying it to a shared transcript is this page's inference.
- Sampling changes what a replay returns. The cited study compares greedy, single-sample, and multi-sample decoding with the same model parameters. These policies expose different outputs ([Joshi et al., section 4.2.3](https://arxiv.org/html/2601.07239v2)). Applying that distinction to transcript replay is this page's inference: recording a request does not guarantee the same response.
- Replay happens months later against a model named by alias. The record does not identify which weights the provider serves under that alias. By analogy, the 640-paper survey lists "ambiguous model identifiers (e.g., latest rather than a specific commit or release)" as a versioning smell ([Siddiq et al., 2025](https://arxiv.org/abs/2512.00651v1), section 3.3.1). It does not study provider model aliases.

## Key takeaways

- A shared transcript records what was asked.
- Reach for it when the suspect is harness state: a dropped parameter, a late-connecting MCP server, a tool the session stopped describing.
- A richer transcript is a bigger disclosure, and the 2.1.300 entry frames sharing as your choice.
- Sampling changes what a replay returns.

## Related

- [Agent Chat History as a First-Class Artifact](agent-history-as-artifact.md) — treating the stored session record as queryable trace data rather than a chat archive
- [In-Session Transcript Search](transcript-search.md) — navigating the same transcript while the session is still open
- [Offline Trajectory Replay for Multi-Agent Workflow Debugging](offline-trajectory-replay-multi-agent-debugging.md) — scoring a replayed trajectory per node to find which call introduced the failure
- [Cut-Point Replay: Test a Fix Against a Recorded Agent Run](../verification/cut-point-replay-agent-regression-tests.md) — promoting one recorded run into a regression test
- [Public-Channel Agent Work as Lehrwerkstatt](../workflows/public-channel-agent-work.md) — the organizational form of the same disclosure question
