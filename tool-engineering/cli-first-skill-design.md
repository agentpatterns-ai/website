---
title: "CLI-First Skill Design"
description: "Design agent skills as CLI tools so the same interface serves both humans debugging locally and agents automating through shell tool calls."
term: "CLI-First Skill Design"
tags:
  - agent-design
  - tool-engineering
  - tool-agnostic
  - skills
aliases:
  - dual-use skill design
  - CLI-first skills
last_reviewed: 2026-05-27
maturity: adopted
---

# CLI-First Skill Design

> Design agent skills as CLI tools so the same interface serves both humans debugging locally and agents automating through shell tool calls.

Related lesson: [The Unix CLI as a Tool Interface](https://learn.agentpatterns.ai/tool-engineering/unix-cli-as-tool-interface/) — this concept features in a hands-on lesson with quizzes.

Write a skill as a shell script, and a human can run it from a terminal while an agent invokes it through a `Bash` or `run()` tool call. You need no separate interfaces. The [awesome-agentic-patterns catalog](https://github.com/nibzard/awesome-agentic-patterns/blob/main/patterns/cli-first-skill-design.md) documents this design, and Claude Code best practices call CLI tools "the most context-efficient way to interact with external services" ([Claude Code best practices](https://code.claude.com/docs/en/best-practices)).

## Core principles

One executable per skill. Each capability lives in a single script at `~/.claude/skills/<name>/scripts/<name>.sh`. Compose with Unix pipes rather than building one monolithic skill.

Subcommands for CRUD. Structure operations as positional arguments:

```bash
trello.sh boards              # list
trello.sh cards <BOARD_ID>    # read
trello.sh create <LIST_ID> "Title"  # write
```

This mirrors how `gh`, `aws`, and other agent-friendly CLIs work — tools the agent already knows from pretraining.

Adaptive output. Return JSON for programmatic use, and human-readable text when attached to a TTY. Detect the terminal with `[ -t 1 ]` (POSIX) or [`sys.stdout.isatty()`](https://docs.python.org/3/library/io.html#io.IOBase.isatty) in Python. The agent always gets structured output. A human running the script gets formatted text.

Standard exit codes. Use POSIX conventions ([IEEE Std 1003.1](https://pubs.opengroup.org/onlinepubs/9699919799/)): `0` success, `1` error, `2` usage problem, `127` command not found. Agents branch on exit codes rather than parsing error messages.

Credentials via environment variables. Follow the [12-Factor App config principle](https://12factor.net/config): never hardcode tokens or API keys. Read from environment variables such as `$TRELLO_API_KEY` and `$GITHUB_TOKEN`. The agent sets these before calling the script. Humans export them in their shell profile.

Non-interactive by default. Skills must not block on prompts. Expose `--yes` or `--force` flags for destructive operations. An agent has no stdin to answer questions.

## Why CLI-first beats API-first for dual-use skills

| Property | CLI-first | In-process function | Structured API |
|----------|-----------|---------------------|----------------|
| Debuggable without agent | Yes — run from terminal | No — requires agent context | Partial — needs HTTP client |
| Unix composability | Yes — pipes, `&&`, `||` | No | No |
| Agent transcript visibility | Yes — commands appear in transcript | No | Partial |
| Testability | Straightforward — call the script | Requires agent harness | Requires mock server |
| Cross-tool portability | Yes — any agent that can shell out | No | No |
| Complex data structures | Limited — shell arrays are awkward | Full | Full |
| Process spawn overhead | Per call | None | Per call |
| Persistent state | Not native | Easy | Session-based |

CLI-first wins when skills run infrequently (seconds between calls), operate on text or JSON, and need to be debuggable by a human. It loses when a skill is called hundreds of times per task, needs rich object graphs, or streams data in real time.

## Composition via pipes

One script per skill pays off in Unix composability. Here is a priority report that draws from three services:

```bash
#!/usr/bin/env bash
# priority-report.sh — compose three skill CLIs
{
  trello.sh cards "$TRELLO_BOARD" --json
  asana.sh tasks --project "$ASANA_PROJECT" --json
  github.sh issues --repo "$GITHUB_REPO" --json
} | jq -s '
  [ .[][] | select(.priority == "high") ]
  | sort_by(.due_date)
  | .[:10]
'
```

Each skill is independently testable, and the composition script is a thin orchestrator. The agent calls `priority-report.sh` and receives a bounded JSON array, not three separate tool calls with three outputs to reconcile.

## When to choose something else

- High call frequency — process spawn overhead adds up, so use an in-process function or [consolidate into a single tool](consolidate-agent-tools.md)
- Complex object graphs — shell arrays and associative maps are fragile, so use a Python or Node script with proper data structures
- Real-time streaming — shell scripts cannot hold open WebSocket or SSE connections gracefully
- Windows without WSL — POSIX scripts need a compatibility layer, so check whether your audience is only Unix-based

## Example

A GitHub skill CLI that follows all six principles:

```bash
#!/usr/bin/env bash
# github.sh — skill CLI for GitHub issues
set -euo pipefail

REPO="${GITHUB_REPO:-}"
TOKEN="${GITHUB_TOKEN:-}"

usage() { echo "Usage: github.sh issues|create|close <args>" >&2; exit 2; }
[[ $# -lt 1 ]] && usage

case "$1" in
  issues)
    result=$(gh issue list --repo "$REPO" --json number,title,labels --limit 20)
    if [ -t 1 ]; then
      # human-readable
      echo "$result" | jq -r '.[] | "#\(.number) \(.title)"'
    else
      echo "$result"
    fi
    ;;
  create)
    [[ $# -lt 2 ]] && usage
    gh issue create --repo "$REPO" --title "$2" ${3:+--body "$3"}
    ;;
  close)
    [[ $# -lt 2 ]] && usage
    gh issue close --repo "$REPO" "$2"
    ;;
  *)
    usage
    ;;
esac
```

An agent calling `github.sh issues` receives a JSON array it can filter with `jq`. A developer running the same command from a terminal sees `#42 Fix auth bug` — no flags needed, no separate interface.

## Key Takeaways

- One script per skill, subcommands for operations, JSON output for agents, human-readable for TTY
- POSIX exit codes (0/1/2/127) let agents branch on failure without parsing error text
- Credentials always via environment variables — never hardcoded
- Composition via pipes replaces complex multi-service skills with thin orchestration scripts
- Choose a different approach for high-frequency calls, complex data structures, or real-time streaming

## Related

- [Skill Authoring Patterns](skill-authoring-patterns.md)
- [Unix CLI as Native Tool Interface](unix-cli-native-tool-interface.md)
- [CLI Scripts as Agent Tools](cli-scripts-as-agent-tools.md)
- [Override Interactive Commands](override-interactive-commands.md)
- [Consolidate Agent Tools](consolidate-agent-tools.md)
- [Token-Efficient Tool Design](../token-engineering/token-efficient-tool-design.md)
- [Skill as Knowledge Pattern](skill-as-knowledge.md)
- [Batch File Operations via Bash Scripts](batch-file-operations.md)
- [Rewriting a CLI Into a JSON Payload for Agents](../patterns/anti-patterns/cli-json-payload-rewrite.md) — why JSON stays adaptive output and a programmatic-caller option here, not a replacement for the flag interface agents already know
