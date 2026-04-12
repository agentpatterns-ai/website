---
title: "Pre-Completion Checklists for AI Agent Development"
description: "Block agent completion signals with a mandatory verification sequence — agents must pass explicit checks before they are allowed to declare a task done."
tags:
  - agent-design
  - testing-verification
---

# Pre-Completion Checklists

> Block agent completion signals with a mandatory verification sequence — agents must pass explicit checks before they are allowed to declare a task done.

## The Premature Completion Problem

Agents optimize for task completion, not task correctness. They stop as soon as output looks plausible — not when it is verified correct. Without an explicit gate, an agent will declare success after partial implementation, a failing test run it chose not to investigate, or a code change that compiles but does not satisfy the requirement.

A pre-completion checklist intercepts the completion signal and forces the agent through a verification sequence before it is allowed to finish.

## Impact

[LangChain's deep agent benchmark experiments](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/) found that a combination of harness changes — including self-verification — improved task scores from 52.8% to 66.5% with no model changes. Self-verification was identified as a high-impact component, but the improvement reflects multiple structural changes working together, not self-verification alone.

## Checklist Structure

The verification sequence covers four phases:

1. **Planning** — did you understand the requirement before starting?
2. **Building** — did you implement what was specified, not a simpler substitute?
3. **Verification** — did you run end-to-end tests? Did you check for regressions? Does output satisfy the stated requirement?
4. **Fixing** — did you address every issue found in verification before declaring done?

Each phase must complete before the next begins. The checklist is not a suggestion — it is a gate.

## Implementation Options

**As explicit mandatory final step in agent instructions:**

Add to the system prompt: "Before completing any task, you must explicitly work through this checklist. Do not declare the task done until each item passes."

**As a PostToolUse hook:**

Monitor for completion signals (task done, STOP calls, summary messages). On detection, inject the checklist as a continuation prompt before allowing the agent to terminate. Hooks execute outside the LLM's reasoning chain, so they enforce the checklist even when the agent forgets the instruction under context pressure or long sessions — [prompt-based instructions achieve 70–90% compliance, while hooks achieve near-100% because they run at the system level](https://www.dotzlaw.com/insights/claude-hooks/).

**As a PreCompletionChecklist middleware:**

A dedicated harness component that wraps the agent's completion path and blocks it until the checklist returns PASS. This keeps the verification logic out of the prompt and makes it independently testable.

## Checklist Items

Effective checklist items are specific and verifiable, not vague:

- "Run the test suite and confirm all tests pass" — not "check your work"
- "Review the original requirement and confirm each acceptance criterion is met"
- "Check that no existing tests were removed or modified"
- "Verify the implementation works end-to-end, not just at the unit level"

Vague items allow the agent to nominally complete them without actually verifying anything.

## Relationship to Feature List Files

Pre-completion checklists and feature list files are complementary. The feature list defines what "done" means per feature; the pre-completion checklist is the verification process the agent follows before updating that status. Together they create a closed loop: clear criteria plus a mandatory verification step before status can change.

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

## Why It Works

Mandatory self-verification interrupts the premature-closure bias built into agent training: models optimise for appearing done, not for being correct. Forcing the agent to re-engage with the original requirement after output is generated creates a second pass that catches drift between intent and implementation.

The mechanism is established in LLM research: self-verification that checks conclusions backward against initial conditions — rather than only forward reasoning — measurably improves accuracy across arithmetic, commonsense, and logical tasks. ([Weng et al., 2022](https://arxiv.org/abs/2212.09561))

Implementing the gate as a hook rather than a prompt instruction exploits the same principle: hooks execute at the system level, outside the LLM's reasoning context, guaranteeing execution independent of what the model remembers.

## When This Backfires

Pre-completion checklists introduce risk in several conditions:

- **Unsatisfiable checklist items create infinite loops.** If the agent cannot make a failing test pass — because the test is flawed, the requirement is contradictory, or the underlying capability is missing — the checklist becomes a deadlock. Add a maximum retry count or an explicit escalation path for persistent failures.
- **Vague items provide false confidence.** A checklist item like "check your work" nominally passes without verifying anything. Agents satisfy the surface form of the instruction, not the intent. Every item must specify a concrete, observable output.
- **Latency compounds in long pipelines.** Each verification pass adds one full LLM round-trip. In a multi-step pipeline with a pre-completion gate at every stage, total latency can exceed the cost of just running end-to-end tests directly.

## Key Takeaways

- Agents stop when output looks plausible, not when it is verified correct — without intervention
- Self-verification was a high-impact component in harness changes that improved task scores from 52.8% to 66.5% in LangChain benchmark experiments
- Implement the checklist as a hook or middleware, not just a prompt instruction — hooks execute at the system level and are not subject to context pressure that degrades prompt compliance
- Checklist items must be specific and verifiable; vague items are not executed meaningfully
- The verification sequence has four phases: planning, building, verification, fixing

## Related

- [Feature List Files](../instructions/feature-list-files.md)
- [Agent Harness](../agent-design/agent-harness.md)
- [Loop Detection](../observability/loop-detection.md)
- [Incremental Verification](incremental-verification.md)
- [Hooks for Enforcement vs Prompts for Guidance](hooks-vs-prompts.md)
- [TDD for Agent Development](tdd-agent-development.md)
- [Verification Ledger](verification-ledger.md)
- [PostToolUse Hooks: Automatic Formatting and Linting After Every File Edit](../workflows/posttooluse-auto-formatting.md)
