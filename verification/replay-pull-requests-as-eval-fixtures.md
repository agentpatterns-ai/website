---
title: "Replaying Real Pull Requests as Eval Fixtures for Event-Driven Agents"
term: "Pull Request Replay Fixture"
description: "Cursor's Agent SDK turns a real pull request into signed webhook payloads and saves them as eval fixtures, so a GitHub-driven agent is tested without waiting for a push."
tags:
  - testing-verification
  - evals
  - cursor
aliases:
  - pull request replay fixtures
  - webhook replay eval fixtures
  - replay a real pull request into an eval
last_reviewed: 2026-10-31
maturity: emerging
status: current
---

# Replaying Real Pull Requests as Eval Fixtures for Event-Driven Agents

> Replay a real pull request as signed webhook payloads, save them as fixtures, and assert on which tools the agent ran.

An agent that wakes on pull request events is hard to test without a new push to the repository. Cursor's Agent SDK removes that wait for the pull request path. `agent-sdk github replay <pr-url>` "turns a real pull request into signed webhook payloads and sends them to the bot, so GitHub-driven bots can be tested without waiting for a push" ([Cursor changelog, 2026-10-20](https://cursor.com/changelog/agent-sdk)). The evidence is one vendor changelog entry, so treat the command shapes as documented and the results as untested here.

## How replay and fixtures work

Three commands carry the technique ([Cursor changelog](https://cursor.com/changelog/agent-sdk)):

| Command | Effect |
|---------|--------|
| `agent-sdk github replay <pr-url>` | Sends the pull request's signed webhook payloads to the bot |
| `agent-sdk github replay <pr-url> --dry-run --fixtures-dir fixtures/` | Saves the payloads as eval fixtures instead |
| `agent-sdk eval` | Runs evals locally or in CI |

A pull request replay fixture is a saved set of signed webhook payloads from a real pull request. Commit them next to the agent project, and every later run sees the same input. The SDK defines an agent as "a folder of code" ([Cursor changelog](https://cursor.com/changelog/agent-sdk)). That folder holds `instructions.md`, `tools/`, `skills/`, `mcp-connections/`, and `channels/`. Put the fixtures in the same tree as the prompt and the tools. The layout is covered in [Choosing an Integration Layer for an Embedded Agent Harness](../patterns/agent-design/embedded-harness-integration-layer.md).

## What the eval asserts

An eval "sends a fixed message to the bot and asserts on what it did: which tools ran, with what input, and the shape of the reply" ([Cursor changelog](https://cursor.com/changelog/agent-sdk)). That grades behavior, not wording. A replayed pull request fits the same check: the fixture fixes the input, and the assertion names the tool calls the agent should make.

## Why replay instead of waiting for a push

The agent wakes on "pull request, comment, and CI events from GitHub, GitLab, and Bitbucket" among other triggers ([Cursor changelog](https://cursor.com/changelog/agent-sdk)). The changelog describes `github replay` as turning an existing pull request into signed webhook payloads. That lets you exercise the pull request path without waiting for a new push.

## Example

```bash
# Save the events of an existing pull request as fixtures
agent-sdk github replay https://github.com/<owner>/<repo>/pull/<number> \
  --dry-run --fixtures-dir fixtures/

# Run the evals
agent-sdk eval
```

The changelog does not say how an eval refers to a saved fixture. Check the Agent SDK documentation for that step before you rely on this command to run against the files in `fixtures/`.

Pick a pull request whose correct handling you already know, such as one a human reviewer flagged. The fixture then encodes a case the agent should catch.

## When this backfires

- Each fixture is one pull request, so the suite covers the cases you chose and no others. See [Cut-Point Replay](cut-point-replay-agent-regression-tests.md) for the same one-input limit on recorded runs.
- Payloads from a real pull request carry that pull request's content. Review them before you commit them to a shared repository.
- The changelog gives no fixture format, no assertion syntax, and no list of the events a replay emits. Confirm those in the SDK docs before you build a suite on them.
- A fixture fixes the input, not the model's output. Re-run the suite after every model or prompt change, and compare tool calls, not text.
- The command belongs to one vendor's SDK. Other harnesses need their own capture step.

## Key Takeaways

- Capture events from a real pull request with `--dry-run --fixtures-dir`, then commit the files.
- Assert on tool calls and their inputs, not on prose.
- Read the saved files before asserting on them, because the source documents no format.
- The suite is as wide as the pull requests you replay. Choose ones with a known correct outcome.

## Related

- [Choosing an Integration Layer for an Embedded Agent Harness](../patterns/agent-design/embedded-harness-integration-layer.md)
- [Cursor SDK: Programmable TypeScript Agent Runtime](../tools/cursor/cursor-sdk.md)
- [Cut-Point Replay: Test a Fix Against a Recorded Agent Run](cut-point-replay-agent-regression-tests.md)
- [Local Git Remotes as Agent Eval Fixtures](local-git-remote-eval-fixtures.md)
- [Emulated APIs for Agent Skill Evals](emulated-apis-for-skill-evals.md)
