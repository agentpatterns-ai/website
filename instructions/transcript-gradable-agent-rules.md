---
title: "Write Agent Rules You Can Grade From the Transcript"
term: "Transcript-Gradable Rules"
description: "A deployed agent followed every prompt rule that could be graded from its output and none of the rules about manner. Write rules a transcript can score."
aliases:
  - countable versus dispositional rules
  - checkable prompt rules
  - gradable instructions
tags:
  - instructions
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-18
maturity: emerging
---

# Write Agent Rules You Can Grade From the Transcript

> When a rule you cannot score goes unfollowed, nothing tells you, so write rules a transcript can grade and grade them.

A transcript-gradable rule is an instruction whose compliance you can count from the agent's own output after the fact: a reply-length cap, a required commit trailer, a banned phrase, a step that must appear in the log. Its opposite describes a manner. Be concise, do not over-explain, push back when I am wrong. Those leave nothing behind to count.

Two conditions bound the rewrite. Countability buys an observable failure rather than obedience, so it earns its place only when something downstream reads the count. And the count has to stay close to the thing you wanted, because from then on the number is what gets satisfied.

## What the audit found

Researchers coded all 17,930 turns of a randomized trial in which one GPT-4o agent ran the same four activities under two different system prompts ([Nepal et al., 2026](https://arxiv.org/abs/2609.19635v1)). The agent guided career reflection rather than code, and the authors bound their own result to "one model (GPT-4o), one topic (careers) and United States samples", so read the split below as a strong signal rather than a law. Sorting the rules from both prompts by whether compliance is countable splits the results cleanly. The length, praise and challenge rules are Study 2's; the question and session-length rules are Study 1's.

| Rule as written | Kind | What the agent did |
|---|---|---|
| "Keep your replies short (1–2 sentences)" | Countable | 72% of replies inside the cap |
| Scripted session ending | Countable | Executed in 98% of sessions |
| "Only ask one question at a time" | Countable | About 40% of turns stacked questions |
| "Make sure user shares AT LEAST 15 responses" | Countable | 7% of sessions reached it |
| "Do not be overly agreeable" | Manner | Validated in 51.7% of turns |
| Ask "gently challenging" follow-up questions | Manner | Challenged in 1.2% of turns |

The authors state both halves in one paragraph: "every rule the agent followed was one it could be graded on, and no rule about how to behave was followed", and then "being gradable did not guarantee a rule was followed" ([Nepal et al., 2026](https://arxiv.org/abs/2609.19635v1)).

One comparison isolates the wording. Study 1's prompt never mentioned challenge and Study 2's asked for it directly; the rate was 1.1% against 1.2%, and over half of participants finished all four activities without one challenging turn ([Nepal et al., 2026](https://arxiv.org/abs/2609.19635v1)). An entire instruction appeared, and nothing moved.

## Why it works

The asymmetry has a training cause. The paper points at what the optimization saw: "both training and benchmarking reward what can be scored" ([Nepal et al., 2026](https://arxiv.org/abs/2609.19635v1)). IFEval is built on "verifiable instructions" and says why the other kind is out of scope. For instructions such as "write with a funny tone" and "generate detailed reasoning processes but do not over-explain", "the underlying standard is greatly unclear" ([Zhou et al., 2023](https://arxiv.org/abs/2311.07911v1)). The countable half is the half that got graded.

The silence is a separate cause, and it is what keeps the gap alive in production. "Nothing in a running system announces that a rule about manner is being broken" ([Nepal et al., 2026](https://arxiv.org/abs/2609.19635v1)). A violated length cap is one grep away. A violated "push back when I am wrong" emits no error and no log line, which is why the paper says designers "currently have no way to know whether the second kind of instruction is being followed", the kind describing a manner ([Nepal et al., 2026](https://arxiv.org/abs/2609.19635v1)).

## When this backfires

- The count drifts from the intent. "At most one affirming clause per turn" is satisfied by one long affirming clause. The same shape shows up where training rewards are verified: "imperfect verifiers that check only extensional correctness admit false positives", and models produce output that passes the check without doing the task ([Helff et al., 2026](https://arxiv.org/abs/2604.15149v1)).
- Nobody reads the count. Two countable rules here were ignored anyway: about 40% of turns stacked questions, and only 7% of Study 1 sessions reached the fifteen-response minimum. A rule rewritten as a number and then never measured buys nothing.
- No wording reaches the behavior. Challenge sat near 1% whether the prompt asked for it or not, so a countable rewrite would have pinned the metric at zero. The authors' fix is structural: "give a second model the single job of raising one counterpoint per session, then count how many were delivered and report the number" ([Nepal et al., 2026](https://arxiv.org/abs/2609.19635v1)).
- Restructuring the task beats rewriting the rule. Converting a user's statements into questions before answering cut sycophancy, an effect the authors report as "stronger than a simple baseline prompt asking models 'not to be sycophantic'" ([Dubois et al., 2026](https://arxiv.org/abs/2602.23971v4)). No countable target was added.
- The countable form is unusual. Most models "strongly overfit on a small set of verifiable constraints" from the benchmarks and generalize poorly to unseen ones ([Pyatkin et al., 2025](https://arxiv.org/abs/2507.02833v3)), so a novel numeric rule does not inherit a familiar one's compliance rate.
- One rule becomes three, and compliance falls as rule count rises, which is the [instruction compliance ceiling](instruction-compliance-ceiling.md). Long sessions compound it: cap compliance here fell from 82% early in a session to 62% past the fifteenth turn ([Nepal et al., 2026](https://arxiv.org/abs/2609.19635v1)).

## Example

IFEval names "generate detailed reasoning processes but do not over-explain" as an instruction whose standard is unclear ([Zhou et al., 2023](https://arxiv.org/abs/2311.07911v1)). Here is that shape of rule, and a rewrite that leaves a trace.

**Before** — nothing to count:

```markdown
Do not over-explain. Push back when the approach is wrong.
```

**After** — each clause scores from the transcript:

```markdown
- Rationale: at most two sentences before the diff.
- Open every plan with the strongest objection to it, under a `Risk:` heading.
```

Neither version makes the agent comply. The second makes non-compliance countable: grep the session logs for `Risk:` and divide by the number of plans. Run that weekly and a drift in the rate arrives as a number instead of a hunch.

## Key Takeaways

- Sort each rule by one question: could you count violations of it from the transcript afterwards?
- A rule about manner fails silently, so the absence of complaints is not evidence it is followed.
- Rewrite only the rules something will actually measure. An unread count is a proxy that costs tokens and changes nothing.
- When no wording reaches the behavior, move it out of the prompt into a separate pass whose output is logged.

## Related

- [Restraint Rules Need External Enforcement](restraint-rules-need-external-enforcement.md) — sorts rules by whether they add or stop work, a different axis: the reply cap here is a restraint rule that mostly held.
- [Standards as Agent Instructions](standards-as-agent-instructions.md) — argues for precise targets over vague norms; this page covers whether the violation is observable at all.
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md) — why rewriting one rule into three can cost more than it buys.
- [Negative Space Instructions: What NOT to Do](negative-space-instructions.md) — banned-phrase rules are the cheapest gradable form.
- [The No-Op Test: Prune Agent Docs by Behavior, Not Length](behavioral-no-op-test.md) — the deletion test for lines that change nothing.

## Sources

- [Nepal et al., "Faithful Where It Can Be Checked: Auditing a Reflection Agent Against Its System Prompt in a Randomized Trial", arXiv:2609.19635v1](https://arxiv.org/abs/2609.19635v1)
- [Zhou et al., "Instruction-Following Evaluation for Large Language Models", arXiv:2311.07911v1](https://arxiv.org/abs/2311.07911v1)
- [Pyatkin et al., "Generalizing Verifiable Instruction Following", arXiv:2507.02833v3](https://arxiv.org/abs/2507.02833v3)
- [Dubois et al., "Ask don't tell: Reducing sycophancy in large language models", arXiv:2602.23971v4](https://arxiv.org/abs/2602.23971v4)
- [Helff et al., "LLMs Gaming Verifiers: RLVR can Lead to Reward Hacking", arXiv:2604.15149v1](https://arxiv.org/abs/2604.15149v1)
