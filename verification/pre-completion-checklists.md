---
title: "Pre-Completion Checklists for AI Agent Development"
term: "Pre-Completion Checklists"
description: "Block agent completion signals with a mandatory verification sequence — agents must pass explicit checks before they are allowed to declare a task done."
tags:
  - agent-design
  - testing-verification
  - tool-agnostic
last_reviewed: 2026-06-12
maturity: adopted
---

# Pre-Completion Checklists for AI Agent Development

> Block agent completion signals with a mandatory verification sequence — agents must pass explicit checks before they are allowed to declare a task done.

Learn it hands-on with [the Pre-Completion Checklist guided lesson](https://learn.agentpatterns.ai/verification/the-pre-completion-checklist/), which includes quizzes.

## The premature completion problem

Agents optimize for task completion, not task correctness. Without an explicit gate, an agent declares success after a partial implementation, a failing test it chose not to investigate, or a code change that compiles but does not satisfy the requirement.

A pre-completion checklist intercepts the completion signal and forces the agent through a verification sequence before it can finish.

## Impact

[LangChain's deep agent benchmark experiments](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/) found that a combination of harness changes — including self-verification — improved task scores from 52.8% to 66.5% with no model changes. Self-verification was identified as a high-impact component, but the improvement reflects multiple structural changes working together, not self-verification alone.

## Checklist structure

The verification sequence covers four phases:

1. Planning — did you understand the requirement before starting?
2. Building — did you implement what was specified, not a simpler substitute?
3. Verification — did you run the end-to-end tests that [incremental verification](incremental-verification.md) treats as the checkpoint? Did you check for regressions? Does the output satisfy the stated requirement?
4. Fixing — did you address every issue found in verification, tracked in a [verification ledger](verification-ledger.md), before declaring done?

Each phase must finish before the next begins. The checklist is not a suggestion. It is a gate.

## Implementation options

### As a mandatory final step in agent instructions

Add this to the system prompt: "Before completing any task, you must explicitly work through this checklist. Do not declare the task done until each item passes."

### As a PostToolUse hook

Watch for completion signals: task done, STOP calls, summary messages. On detection, inject the checklist as a continuation prompt before the agent terminates. Hooks run outside the LLM's reasoning chain, so they enforce the checklist even when the agent forgets the instruction under context pressure or long sessions. [Prompt-based instructions achieve 70 to 90% compliance, while hooks achieve near-100% because they run at the system level](https://www.dotzlaw.com/insights/claude-hooks/).

### As a PreCompletionChecklist middleware

A dedicated harness component wraps the agent's completion path and blocks it until the checklist returns PASS. This keeps the verification logic out of the prompt and makes it testable on its own.

## Checklist items

Effective checklist items are specific and verifiable, not vague:

- "Run the test suite and confirm all tests pass" — not "check your work"
- "Review the original requirement and confirm each acceptance criterion is met"
- "Check that no existing tests were removed or modified"
- "Verify the implementation works end-to-end, not just at the unit level"

## Relationship to feature list files

Pre-completion checklists and feature list files are complementary. The feature list defines what "done" means per feature; the pre-completion checklist is the verification process the agent follows before updating that status.

## Example

The following shows the checklist implemented as a `PostToolUse` hook that intercepts task completion signals, forcing the agent through a verification sequence before it can finish.

`.claude/settings.json` — hook configuration that monitors for completion signals:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Task",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/pre-completion-check.sh"
          }
        ]
      }
    ]
  }
}
```

`.claude/hooks/pre-completion-check.sh` — injects the checklist as a continuation prompt:

```bash
#!/usr/bin/env bash
# Reads the tool result from stdin; exits 2 with checklist if task is marked done
result=$(cat)
if echo "$result" | grep -qi '"status".*"done"\|task complete\|STOP'; then
  echo "Before completing: you must verify each of the following and report PASS or FAIL for each item:
1. Run the test suite and confirm all tests pass: \`npm test\`
2. Review the original requirement and confirm each acceptance criterion is met
3. Check that no existing tests were removed or modified
4. Verify the implementation works end-to-end, not just at the unit level
Do not declare the task done until all four items report PASS." >&2
  exit 2
fi
```

When the hook exits with code `2`, the agent receives the checklist as stderr feedback and must work through it before the completion signal is accepted. The system prompt addition reinforces this with an explicit gate:

```markdown
<!-- In CLAUDE.md or system prompt -->
## Completion Gate
Before declaring any task done, you must explicitly work through the pre-completion checklist.
Run `npm test` and paste the result. Do not summarize — show the actual output.
```

This combination — a `PostToolUse` hook plus an explicit system prompt instruction — ensures the checklist runs even when the agent does not remember the instruction from earlier in the conversation.

## Why it works

Mandatory self-verification interrupts the premature-closure bias built into agent training. The agent re-engages with the original requirement after it generates output. That second pass catches drift between intent and implementation.

The mechanism is established in LLM research: self-verification that checks conclusions backward against initial conditions — rather than only forward reasoning — measurably improves accuracy across arithmetic, commonsense, and logical tasks ([Weng et al., 2022](https://arxiv.org/abs/2212.09561)).

Implementing the gate as a hook rather than a prompt exploits the same principle at the system level, outside the LLM's reasoning context — execution is guaranteed regardless of what the model remembers.

## When this backfires

Pre-completion checklists introduce risk in several conditions:

- Unsatisfiable checklist items create infinite loops. If the agent cannot make a failing test pass — because the test is flawed, the requirement is contradictory, or the underlying capability is missing — the checklist becomes a deadlock that [loop detection](../observability/loop-detection.md) is meant to break. Add a maximum retry count or an explicit escalation path for persistent failures.
- Vague items give false confidence. A checklist item like "check your work" passes without verifying anything. Agents satisfy the surface form of the instruction, not the intent — the [anti-reward-hacking](anti-reward-hacking.md) failure shape. Every item must specify a concrete, observable output.
- Latency compounds in long pipelines. Each verification pass adds one full LLM round-trip. In a multi-step pipeline with a pre-completion gate at every stage, total latency can exceed the cost of running the end-to-end tests directly.

## FAQ

**Why implement the checklist as a hook rather than a prompt instruction?**

Hooks run outside the LLM's reasoning chain, so they fire even when the agent forgets the instruction under context pressure or in a long session. [Prompt-based instructions achieve 70 to 90% compliance, while hooks achieve near-100% because they run at the system level](https://www.dotzlaw.com/insights/claude-hooks/). Pairing both is stronger still: the hook enforces the gate, the prompt explains it.

**What makes a checklist item effective?**

Specificity. "Run the test suite and confirm all tests pass" names a concrete, observable output; "check your work" passes without verifying anything, because agents satisfy the surface form of an instruction rather than its intent. Items that make the agent re-read the original requirement, confirm each acceptance criterion, and check that no existing tests were removed hold up the same way.

**What happens when a checklist item can never pass?**

The gate becomes a deadlock. If the agent cannot make a failing test pass — because the test is flawed, the requirement is contradictory, or the underlying capability is missing — the checklist loops until loop detection breaks it. Add a maximum retry count or an explicit escalation path so persistent failures reach a human instead of burning iterations.

## Key Takeaways

- Agents stop when output looks plausible, not when it is verified correct — without intervention
- Self-verification was a high-impact component in harness changes that improved task scores from 52.8% to 66.5% in LangChain benchmark experiments
- Implement the checklist as a hook or middleware, not just a prompt instruction — hooks execute at the system level and are not subject to context pressure that degrades prompt compliance
- Checklist items must be specific and verifiable; vague items are not executed meaningfully
- The verification sequence has four phases: planning, building, verification, fixing

## Related

- [Feature List Files](../instructions/feature-list-files.md)
- [Agent Harness](../patterns/agent-design/agent-harness.md)
- [Loop Detection](../observability/loop-detection.md)
- [Incremental Verification](incremental-verification.md)
- [Hooks for Enforcement vs Prompts for Guidance](../instructions/hooks-vs-prompts.md)
- [TDD for Agent Development](tdd-agent-development.md)
- [Verification Ledger](verification-ledger.md)
- [PostToolUse Hooks: Automatic Formatting and Linting After Every File Edit](../tools/claude/posttooluse-auto-formatting.md)
