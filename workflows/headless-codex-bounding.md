---
title: "Bounding a Headless Codex Run Without a Turn Cap"
description: "codex exec has no --max-turns equivalent, so an unattended Codex run is bounded by its sandbox policy, the caller's wall clock, and a JSON Schema output contract."
tags:
  - workflows
  - agent-design
  - automation
  - cost-performance
  - tool-agnostic
aliases:
  - "headless codex exec"
  - "codex exec in CI"
  - "non-interactive Codex run"
last_reviewed: 2026-08-23
maturity: emerging
---

# Bounding a Headless Codex Run Without a Turn Cap

> `codex exec` has no turn cap, so bounding an unattended Codex run falls to the sandbox policy and the caller's wall clock.

OpenAI's Codex CLI runs non-interactively through `codex exec`, and it has no equivalent of Claude Code's `--max-turns`. That flag was requested as [openai/codex#12336](https://github.com/openai/codex/issues/12336) and closed as not planned. The `codex exec` event loop carries no iteration ceiling: it runs until the task completes, the client shuts down, or an interrupt arrives ([`exec/src/lib.rs`](https://github.com/openai/codex/blob/rust-v0.149.0/codex-rs/exec/src/lib.rs)).

Carry the Claude bounding model across unchanged and the pipeline ships with no ceiling at all. Codex bounds a run on a different axis, and the three layers below are what a caller supplies instead.

## Why approvals switch off in headless mode

An agent with no human at the terminal has two options at a permission boundary: block on a prompt nobody will answer, or stop asking. Codex takes the second. `codex exec` resolves the approval policy to `AskForApproval::Never` by default, and the source comment says so directly: "Default to never ask for approvals in headless mode" ([`exec/src/lib.rs`](https://github.com/openai/codex/blob/rust-v0.149.0/codex-rs/exec/src/lib.rs)).

A headless Codex run therefore never pauses for permission. Any control written as an approval gate stops existing the moment the run goes non-interactive. The [deferred permission pattern](../patterns/agent-design/deferred-permission-pattern.md) covers what Claude Code does with the same problem, pausing the session and resuming it after out-of-band approval. Codex offers no such rung, so the gate has to move down to the sandbox.

## Three layers of bound

### Layer 1: sandbox policy bounds blast radius

`--sandbox` (short form `-s`) selects "the sandbox policy to use when executing model-generated shell commands" ([`utils/cli/src/shared_options.rs`](https://github.com/openai/codex/blob/rust-v0.149.0/codex-rs/utils/cli/src/shared_options.rs)). The policy `codex exec` resolves from the active permission profile is one of read-only, workspace-write, or full access ([`exec/src/lib.rs`](https://github.com/openai/codex/blob/rust-v0.149.0/codex-rs/exec/src/lib.rs)).

This is the only bound the agent itself enforces, which makes it worth pinning per invocation rather than leaving to a config file. Read-only suits analysis, review, and report generation. Workspace-write is the minimum for a run that has to open a pull request. A third flag, `--dangerously-bypass-approvals-and-sandbox`, is documented as "Skip all confirmation prompts and execute commands without sandboxing" ([`utils/cli/src/shared_options.rs`](https://github.com/openai/codex/blob/rust-v0.149.0/codex-rs/utils/cli/src/shared_options.rs)). It removes the last agent-level bound, so it belongs only where the run is already contained by something else, such as an ephemeral runner (see [blast radius containment](../security/blast-radius-containment.md)).

### Layer 2: the caller's wall clock bounds runtime and cost

Nothing inside Codex limits how long a run continues. The `codex exec` CLI defines no turn or step flag ([`exec/src/cli.rs`](https://github.com/openai/codex/blob/rust-v0.149.0/codex-rs/exec/src/cli.rs)), and the request to add one was declined ([openai/codex#12336](https://github.com/openai/codex/issues/12336)). The ceiling has to come from the process that invoked it: `timeout-minutes` on a GitHub Actions job, `timeout` in front of the command in a cron entry, or an equivalent supervisor limit.

Spend stays observable even though it is not capped in advance. Under `--json`, the run emits `turn.completed` carrying a usage record with `input_tokens`, `cached_input_tokens`, `cache_write_input_tokens`, `output_tokens`, and `reasoning_output_tokens` ([`exec/src/exec_events.rs`](https://github.com/openai/codex/blob/rust-v0.149.0/codex-rs/exec/src/exec_events.rs)). Recording those figures per run gives you retrospective cost data, which is weaker than a budget flag because it reports the overrun rather than preventing it. Where the spend has to be capped rather than watched, the bound belongs one level down in the API client. [Per-run budget reservation](../patterns/agent-design/per-run-budget-reservation.md) holds worst-case cost against a run-scoped balance before each call, so the run refuses a request it cannot afford.

### Layer 3: the output contract bounds what the pipeline accepts

Three flags decide what a downstream step consumes ([`exec/src/cli.rs`](https://github.com/openai/codex/blob/rust-v0.149.0/codex-rs/exec/src/cli.rs)):

| Flag | Documented behavior |
|---|---|
| `--output-schema` | "Path to a JSON Schema file describing the model's final response shape." |
| `-o` / `--output-last-message` | "Specifies file where the last message from the agent should be written." |
| `--json` | "Print events to stdout as JSONL." |

The stream split is strict, and that is what makes the contract usable without a filtering step. In default mode "it is paramount that the only thing written to stdout is the final message (if any)", with diagnostics, warnings, and progress on stderr ([`exec/src/lib.rs`](https://github.com/openai/codex/blob/rust-v0.149.0/codex-rs/exec/src/lib.rs)). Under `--json`, stdout carries valid JSONL and everything else still goes to stderr.

The JSONL stream is also where the failure signal lives. Its event types are `thread.started`, `turn.started`, `turn.completed`, `turn.failed`, `item.started`, `item.updated`, `item.completed`, and `error`, where `turn.failed` embeds an error message and `error` marks an unrecoverable stream failure ([`exec/src/exec_events.rs`](https://github.com/openai/codex/blob/rust-v0.149.0/codex-rs/exec/src/exec_events.rs)). Gate on those rather than on prose in the final message.

## Triggers and constraints

| Trigger | What bounds the run |
|---|---|
| Scheduled (cron, Actions schedule) | Supervisor timeout is mandatory; nothing else stops a stalled run |
| Push or pull request | Job `timeout-minutes` plus a read-only sandbox for review-only work |
| Manual dispatch | Same as scheduled; an operator watching the log is not a ceiling |

Session state persists across invocations unless you opt out. `--ephemeral` means "Run without persisting session files to disk" ([`exec/src/cli.rs`](https://github.com/openai/codex/blob/rust-v0.149.0/codex-rs/exec/src/cli.rs)), and `codex exec` also carries `resume` and `fork` subcommands. On a shared or long-lived runner, prompts and traces accumulate outside the job's own artifacts until `--ephemeral` is passed.

## How this differs from headless Claude

[Headless Claude in CI](headless-claude-ci.md) documents the same rung for Claude Code, drawing the flags below from the [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference). The flag names differ, and so does the design.

| Concern | Claude Code | Codex CLI |
|---|---|---|
| Step ceiling | `--max-turns <N>`, exits with an error at the limit | None; request closed as not planned |
| Budget ceiling | `--max-budget-usd <amount>` | None; usage reported after the fact on `turn.completed` |
| Approvals with no TTY | `--permission-mode dontAsk`, `auto`, or `--allowedTools` | Resolved to never ask |
| Final output | `--output-format json` wraps the response | `--output-schema` constrains the response shape |

## Why it works

The two tools bound different quantities. A turn cap bounds cost and runtime, which is why `--max-turns` sits beside `--max-budget-usd` in Claude Code. A sandbox bounds reach: what the run can touch, however long it takes. Codex removes the step axis from the agent, makes the filesystem boundary the agent-level control, and resolves approvals to never so nothing blocks on an absent human ([`exec/src/lib.rs`](https://github.com/openai/codex/blob/rust-v0.149.0/codex-rs/exec/src/lib.rs)).

Cost and runtime bounding is delegated upward to whatever launched the process. That composes correctly where the supervisor already owns wall clock, which a CI job with `timeout-minutes` does. It composes badly where no supervisor exists, because then no layer holds the ceiling. The [agent turn model](../patterns/agent-design/agent-turn-model.md) explains why the step axis matters at all: one user-facing turn is an iterative sequence of inference and tool-call steps, so an unbounded loop is unbounded in both time and tokens.

## When this backfires

- Underspecified goals on a writable sandbox. A wall-clock kill lands mid-tool-call rather than at a turn boundary. Under `--sandbox workspace-write` that leaves a partially modified workspace and no completion event to gate on, which is worse than a `--max-turns` exit that fails at a turn edge with a non-zero status.
- Rich output schemas. Gating on schema validity turns decoder coverage limits into what looks like agent failure. On the hardest real-world schema set it evaluated, [JSONSchemaBench](https://arxiv.org/abs/2501.10868v3) measured compliance of 69% for Guidance against 6% for Outlines, and reports that closed-source implementations combine "low empirical coverage" with "very high compliance rates". A deeply nested schema is a flakiness source before it is a safety net.
- Controls that needed a human decision. There is no headless pause-and-ask rung, so a policy expressed as an approval gate has to be rewritten as a sandbox boundary or moved off the headless path.
- Invocations with no process supervisor. A developer shell or a bare cron line has no `timeout-minutes` equivalent unless one is added. The Codex bounding model assumes the caller owns wall clock.
- Treating read-only as containment. A read-only sandbox still reads credential files. It does gate the network — every sandbox policy carries a `network_access` flag, and the policy summary appends "(network access enabled)" only where it is set ([`utils/sandbox-summary/src/sandbox_summary.rs`](https://github.com/openai/codex/blob/rust-v0.149.0/codex-rs/utils/sandbox-summary/src/sandbox_summary.rs)) — but that flag is a boolean rather than a host allowlist. Once a run has network access, per-host egress filtering is still a separate control.

Format restriction at the prompt level does cost reasoning accuracy: adding a schema restriction to a JSON prompt dropped GPT-3.5-Turbo on GSM8K from 74.70% to 49.25% ([Tam et al., 2024](https://arxiv.org/abs/2408.02442v3)). Grammar-enforced decoding is a different mechanism, and JSONSchemaBench measured it going the other way, "consistently improves the performance of downstream tasks up to 4%, even for tasks with minimal structure like GSM8k" ([arXiv:2501.10868v3](https://arxiv.org/abs/2501.10868v3)). `--output-schema` is the second kind, so coverage is its limitation rather than answer quality.

## Example

A scheduled brief-generation run, following the pipeline shape in Shuai Guo's [walkthrough](https://towardsdatascience.com/running-codex-as-a-headless-agent/), with the three bounds made explicit. The prompt arrives on stdin, the JSONL trace goes to a file, and the supervisor supplies the ceiling Codex does not:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Layer 2: the ceiling Codex has no flag for.
timeout 600 codex --search exec \
  --model gpt-5.6-sol \
  --sandbox read-only \
  --json \
  --output-schema schemas/evidence_brief.schema.json \
  -o outputs/brief.json \
  - < prompts/brief.md > outputs/run.jsonl

# Layer 3: gate on the event stream, not on the final prose.
if grep -q '"turn.failed"' outputs/run.jsonl; then
  echo "codex run failed" >&2
  exit 1
fi

# The schema-constrained final message is now safe to parse.
jq -e '.summary' outputs/brief.json > /dev/null
```

`timeout 600` is the only runtime bound in that script. Remove it and the run has none.

## Key Takeaways

- Audit any `codex exec` invocation for a step or budget flag before trusting it as bounded; neither exists, so a CI file that appears to carry one is unbounded.
- Set `--sandbox` explicitly per invocation, because it is the only bound the agent enforces on itself.
- Supply the wall clock from the caller: `timeout-minutes` in GitHub Actions, `timeout` in cron.
- Gate on `turn.failed` and `error` in the `--json` stream, then validate the `-o` file against the schema passed to `--output-schema`.
- Pass `--ephemeral` on shared runners so session files do not accumulate outside the job's artifacts.

## Related

- [Headless Claude in CI: Using -p and --max-turns for Safe Pipeline Integration](headless-claude-ci.md)
- [Deferred Permission Pattern](../patterns/agent-design/deferred-permission-pattern.md)
- [Model a Single Agent Turn as Many Inference and Tool-Call Iterations](../patterns/agent-design/agent-turn-model.md)
- [Blast Radius Containment](../security/blast-radius-containment.md)
- [Continuous AI: Agentic CI/CD Pipelines](continuous-ai-agentic-cicd.md)
