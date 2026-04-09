---
title: "The Prompt Tinkerer Anti-Pattern in Agent Workflows"
description: "Endlessly refining prompts to prevent errors that structural controls would eliminate deterministically. Use hooks and constraints instead of instruction bloat."
tags:
  - human-factors
  - instructions
aliases:
  - prompt bloat
  - instruction bloat
---

# The Prompt Tinkerer

> Endlessly refining prompts to prevent errors that structural controls would eliminate deterministically.

## The Pattern

Each time an agent makes a recurring mistake, the prompt grows: another sentence, another rule, another "IMPORTANT:" prefix. The prompt becomes a long list of prohibitions, and the agent still violates some of them. This is the Prompt Tinkerer anti-pattern — using probabilistic tools (instructions) to enforce things that need deterministic tools (structure).

## Why Prompts Fail at Enforcement

Agents do not process instructions the way a compiler processes code. A prompt is not a contract. Instructions compete with each other, with context, and with the model's training distribution. The longer the instruction set, the more likely any single rule is ignored `[unverified]`.

Adding "IMPORTANT:" or "NEVER do X" to a prompt applies social emphasis to a system that has no concept of social emphasis. It changes token distribution slightly but does not enforce the rule.

## The Escalation Ladder

When an agent repeats the same error, apply this sequence:

1. **Prompt** — rephrase the instruction, place it closer to the relevant context
2. **Skill** — encode the correct behavior as a reusable skill the agent invokes
3. **Hook** — block the bad output at the boundary with a pre/post-commit hook or validation step
4. **Tool restriction** — remove the agent's ability to perform the action entirely
5. **Accept and verify** — if none of the above is cost-effective, add a human verification gate

Stop at the step that eliminates the error. Do not continue prompt-tweaking when a lower-rung fix would work.

## When Prompts Are the Right Tool

Prompts work for guidance, not enforcement:

| Use prompts for | Use structure for |
|-----------------|-------------------|
| Tone and style | Binary rules ("never delete files") |
| Approach selection | Output format enforcement |
| Creative direction | Security constraints |
| Interpretation guidance | Permission boundaries |

If "correct" has a valid range of interpretations, prompts are appropriate. If the behavior must be exactly right every time, use structure.

## Symptoms

- The prompt contains more than 5 negation rules ("never", "do not", "avoid")
- The same category of error recurs despite prompt updates
- You have added "IMPORTANT:" more than once
- You are explaining context in the prompt that should be in project files or skills

## Example

An agent keeps writing files outside the project directory. The developer adds prohibitions to the prompt:

```text
# System prompt (attempt 4)
You are a coding assistant.
IMPORTANT: Never write files outside the /project directory.
IMPORTANT: Do not use absolute paths.
NEVER create files in /tmp, /home, or any parent directory.
Do NOT use "../" in any file path. This is critical.
Always check that your output path starts with /project.
```

The prompt now has five rules addressing the same failure, and the agent still occasionally writes to `/tmp` for intermediate work. Each rule competes with the others for the model's attention.

The structural fix replaces all five rules with a single hook:

```bash
# .hooks/pre-write.sh
#!/usr/bin/env bash
# Block any write outside the project directory
realpath="$(realpath --relative-to="$PROJECT_DIR" "$TARGET_PATH" 2>/dev/null)"
if [[ "$realpath" == ../* ]]; then
  echo "BLOCKED: write target $TARGET_PATH is outside $PROJECT_DIR" >&2
  exit 1
fi
```

The hook eliminates the error deterministically. The prompt can drop all five prohibition lines and replace them with a single sentence of guidance: "Write all output files inside the project directory."

## Key Takeaways

- Prompts are probabilistic; hooks, schemas, and tool restrictions are deterministic
- Use the escalation ladder: prompt → skill → hook → tool restriction → verify
- Prompts suit guidance with a valid interpretation range; structure suits binary correctness
- A long prohibition list is a signal that structural controls are overdue

## Unverified Claims

- Longer instruction sets making any single rule more likely to be ignored `[unverified]`

## Related

- [The Anthropomorphized Agent](anthropomorphized-agent.md)
- [Cargo Cult Agent Setup](cargo-cult-agent-setup.md)
- [Abstraction Bloat](abstraction-bloat.md)
- [Distractor Interference](distractor-interference.md)
- [The Infinite Context](infinite-context.md)
- [The Implicit Knowledge Problem](implicit-knowledge-problem.md)
- [Spec Complexity Displacement](spec-complexity-displacement.md)
