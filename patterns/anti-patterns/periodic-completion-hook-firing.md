---
title: "Periodic Completion Hooks and Duplicate Side Effects"
term: "Periodic Completion Hook Firing"
description: "Check when completion hooks fire and make their writes safe to repeat. A fixed SubagentStop bug shows why event names cannot prove completion."
tags:
  - anti-pattern
  - agent-design
  - claude
  - hooks
  - observability
last_reviewed: 2026-10-31
applies_to: "claude-code@2.x"
maturity: emerging
---

# Periodic Completion Hooks and Duplicate Side Effects

> Periodic completion hooks repeat side effects when the runtime fires an event before completion; check event timing and make writes safe to repeat.

The anti-pattern is treating each completion-hook invocation as proof that a worker finished and needs a new completion record. Claude Code documents [`SubagentStop`](https://code.claude.com/docs/en/hooks#subagentstop) as firing when a sub-agent finishes responding. Its [2.1.311 changelog](https://code.claude.com/docs/en/changelog#2-1-311) records a fix for periodic firing while sub-agents were still running. The entry separates the intended [lifecycle contract](../../tool-engineering/hooks-lifecycle-events.md) from observed runtime behavior.

## Why repeated firing duplicates writes

The reported bug breaks two expectations. The completion predicate fails because the worker is still running. The cadence fails because the runtime invokes the hook repeatedly. The same entry describes about 2 invocations per minute for each running sub-agent ([changelog](https://code.claude.com/docs/en/changelog#2-1-311)). Version 2.1.311 fixes that behavior. The entry does not name the first affected version.

The per-worker rate implies that concurrent workers multiply hook invocations. This is an inference from the changelog, not a measured cost result. Repeated invocations become repeated writes when the handler appends a record or posts a fresh comment each time. [AWS describes the same duplicate-effect problem](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) for retried writes.

## Log each invocation before suppressing duplicates

Use a disposable run to test your installed version before attaching external writes. Record an entry for every invocation, including duplicates you suppress. Include a timestamp, runtime version, event name, session ID, and agent ID. These fields let you compare timing for the same worker. Claude Code documents `session_id`, `hook_event_name`, and `agent_id` in [hook input](https://code.claude.com/docs/en/hooks#subagentstop-input).

Compare the entries with the worker's actual completion. Check for calls while it runs, then repeat with concurrent workers. Test both timing and multiplicity. Also distinguish a hook that asks the worker to continue: `SubagentStop` can block stopping and return feedback to that worker ([decision control](https://code.claude.com/docs/en/hooks#subagentstop)).

## Deduplicate writes without certifying completion

Apply [idempotent operations](../agent-design/idempotent-agent-operations.md) to each intended effect. Define a stable identity for that effect and reuse it on duplicates. AWS recommends caller-provided request identifiers and atomic recording of the identifier with the mutation ([AWS idempotency guidance](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)). A separate check followed by an unprotected write leaves a concurrency gap.

Keep the identity tied to the intended completion record. A fresh timestamp on every invocation defeats deduplication. A worker ID alone also needs a clear scope if that worker can have several legitimate completions. This applies AWS's distinction between a repeated request and a new intent to hook writes.

Deduplication limits repeated effects. It does not establish that the first invocation occurred after completion. Check that predicate separately before publishing a completion record. The fixed Claude Code bug supplies the counterexample.

## Key Takeaways

- Test whether a completion hook fires while its worker is still running.
- Keep invocation logs even when the handler suppresses duplicate writes.
- Deduplicate each intended effect; separately check whether completion occurred.

## Related

- [Hooks and Lifecycle Events](../../tool-engineering/hooks-lifecycle-events.md) — event contracts and hook placement
- [Idempotent Agent Operations](../agent-design/idempotent-agent-operations.md) — safe repeated writes
- [Treating a Model-Judged Hook as a Deterministic Control](model-judged-hook-as-deterministic-control.md) — another hook assumption that fails without a deterministic check
- [Enforcing Agent Behavior with Hooks](../../instructions/enforcing-agent-behavior-with-hooks.md) — completion gates and enforcement patterns
