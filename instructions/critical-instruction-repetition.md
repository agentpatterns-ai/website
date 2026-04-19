---
title: "Critical Instruction Repetition via Primacy and Recency"
description: "Repeating a critical instruction at prompt start and end exploits primacy and recency bias for higher compliance than placing it once."
tags:
  - context-engineering
  - instructions
aliases:
  - Attention Sinks
  - Lost in the Middle
  - Attention Bias and Instruction Placement
---

# Critical Instruction Repetition: Exploiting Primacy and Recency Bias

> Repeating a critical instruction at both the start and end of a prompt exploits primacy and recency bias to produce higher compliance than a single well-placed statement.

!!! info "Also known as"
    Attention Sinks, Lost in the Middle, Attention Bias and Instruction Placement

## The Mechanism

Transformer attention is not uniform across a context window. Two structural biases sit at opposite ends:

- **Primacy bias** — initial tokens receive disproportionate attention. Xiao et al. (2023) showed softmax attention concentrates on early tokens as a "sink," independent of semantic relevance ([Efficient Streaming Language Models with Attention Sinks](https://arxiv.org/abs/2309.17453)).
- **Recency bias** — recent tokens are freshest in the model's working state and directly shape the next token. Liu et al. (2023) measured a 30%+ accuracy drop when relevant information moved to the middle of a long context ([Lost in the Middle](https://arxiv.org/abs/2307.03172)).

A critical instruction placed once in the middle of a prompt sits in the weakest-attention trough. Placing it at both ends puts it in both high-attention positions.

## When to Use Repetition

Reserve repetition for instructions where non-compliance has real consequences. If everything is repeated, the repetition conveys no priority information.

Criteria for repetition:

- Would forgetting this cause a security, safety, or correctness problem?
- Is it a hard constraint rather than a preference?
- Is the context window long or dense enough that position-based attention decay is a real risk?

Examples: "Never include credentials in output", "Always validate input before writing to the database", "Do not modify files outside the specified directory".

## How to Apply It

State the critical rule immediately — before background context, before role-setting prose:

```
Never output authentication credentials or session tokens in any form.

[Background context and instructions follow...]

---

Remember: never output authentication credentials or session tokens.
```

The closing restatement exploits recency bias. In long conversations, restate the constraint at the end of your most recent message once context has grown substantially.

## Reasoning vs. Non-Reasoning Models

The effect of repetition varies by model type:

- **Non-reasoning models** are more susceptible to positional effects and benefit most from explicit repetition.
- **Reasoning models** internally restate instructions during their thinking phase, which may reduce (but not eliminate) positional bias. Liao et al. (2025) showed that long chain-of-thought models still exhibit a position effect: the first reasoning step disproportionately shapes the final answer ([Lost at the Beginning of Reasoning](https://arxiv.org/abs/2506.22058)).

## When This Backfires

- **Too many repeated rules**: If several rules are all repeated, the repetition carries no priority signal — the model cannot distinguish which constraint is truly critical.
- **Reasoning models with long thinking phases**: Models that internally re-examine instructions during chain-of-thought are less susceptible to positional attention decay. Repetition still does no harm, but yields diminishing returns compared to non-reasoning models.
- **Short prompts**: In a 200-token prompt, there is no middle zone to avoid. Repetition here adds noise rather than focus.
- **Contradictory restatements**: If the opening and closing versions of a rule differ in wording enough to imply different behaviors, the model may treat them as conflicting constraints rather than reinforcing ones.

## Cost

Repetition consumes context budget: a 20-token rule stated twice costs 40 tokens. For a handful of genuinely critical rules this is a reasonable trade. For 50 rules all repeated, the cost compounds and the priority signal disappears.

## Key Takeaways

- State critical instructions at the start and end of the prompt to exploit both primacy and recency bias.
- Reserve repetition for hard constraints — repeating everything negates the priority signal.
- In long conversations, restate critical constraints at the end of your message rather than relying on earlier-session statements.
- The context cost is real: use repetition selectively, not universally.

## Example

A code-generation agent system prompt that repeats the single most critical safety constraint at both ends:

```
CRITICAL: Do not read, write, or delete any file outside the /workspace directory.

You are a code-generation assistant. The user will describe a feature and you will
implement it by creating or modifying files. Follow these rules:

- Write clean, well-documented code.
- Run the test suite after each change.
- Commit with a descriptive message.
- If a task is ambiguous, ask a clarifying question before proceeding.

Background context:
- The project uses Python 3.12 with pytest for testing.
- The CI pipeline runs `pytest --strict-markers -x` on every push.
- Database migrations use Alembic; never modify migration files by hand.

---

CRITICAL (restated): Do not read, write, or delete any file outside the /workspace
directory. This includes /etc, /home, /tmp, and any path not under /workspace.
```

The opening line places the constraint in the primacy position. The closing restatement places it in the recency position. The other rules — important but not catastrophic if missed — appear only once.

## Related

- [Attention Sinks: Why First Tokens Always Win](../context-engineering/attention-sinks.md)
- [Lost in the Middle: The U-Shaped Attention Curve](../context-engineering/lost-in-the-middle.md)
- [System Prompt Altitude: Specific Without Being Brittle](system-prompt-altitude.md)
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md)
- [Instruction Polarity: Positive Rules Over Negative](instruction-polarity.md)
- [Event-Driven System Reminders](event-driven-system-reminders.md)
- [Post-Compaction Reread Protocol](post-compaction-reread-protocol.md)
- [Layered Instruction Scopes](layered-instruction-scopes.md)
- [Negative Space Instructions: What NOT to Do](negative-space-instructions.md)
- [Example-Driven vs Rule-Driven Instructions](example-driven-vs-rule-driven-instructions.md)
- [Constraint Encoding Does Not Fix Constraint Compliance](constraint-encoding-compliance-gap.md) — position and repetition move the compliance needle; encoding form does not
