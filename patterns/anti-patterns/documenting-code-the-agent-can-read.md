---
title: "Documenting Code the Agent Can Already Read"
term: "Redundant Agent Documentation"
description: "Static file-level documentation beat the issue alone by at most one task across five source-present settings; the full-length version resolved 4 of 15 django tasks against 9."
aliases:
  - redundant agent documentation
  - documentation that restates readable code
tags:
  - anti-pattern
  - context-engineering
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-28
maturity: emerging
---

# Documenting Code the Agent Can Already Read

> Documentation of a file the agent can open beat the issue alone by at most one task, and the longest form was worst wherever tested.

Before you document a file for a coding agent, ask what the document carries that the agent cannot get by opening that file. If the answer is nothing, the measured return is indistinguishable from zero. Arman and Molybog optimized a describe prompt to near-perfect regeneration fidelity, then tested those descriptions on real issue resolution: "When the source is present, neither static compact documentation nor retrieved context beats the issue alone" ([arXiv:2609.31587v1](https://arxiv.org/abs/2609.31587v1)).

## What the null actually covers

Five settings, two model families, three kinds of documentation. The largest run put all three conditions head to head on SWE-ContextBench Lite with Gemini 3.8 Flash. On the 58 tasks scorable under every condition, the issue alone resolved 33, the benchmark's retrieved past-task context 30, and a roughly eighty-word static description 29. McNemar's exact test returns p=0.22 for issue versus compact and p=0.25 for issue versus context, so that gap is not a measured loss either.

The direction reverses by setting. In two runs on the same SWE-ContextBench django tasks with Gemini 3.1 Pro, documentation came out one task ahead: retrieved context resolved 15 against 14 on the 29 tasks scored under both, a compact description 16 against 15 on 32. The authors decline to bank it, writing that "The compact advantage is a single task, which a paired test cannot distinguish from zero". So what holds across the table is narrower than a claim that documentation never helps: "No documentation condition improves on issue-only by more than a single task, and the full-length description is the worst condition wherever it was run."

The full-length description is where a penalty shows. On 15 paired django fixtures with Gemini 3.1 Pro the issue alone resolved 9, the compact description 8, and the full-length optimized description 4.

## Why it works

A faithful description of a readable file is that file again in other words. It adds no information and still costs attention, because "a restatement adds nothing when the original is already in context". The cost is distraction rather than volume: "in our data description length does not predict the penalty, so we treat distraction from redundant content, rather than length alone, as the operative mechanism". The behavior it produces is specific. "The longer the documentation, the worse the agent does, because a complete description of a file the agent can already read invites it to rewrite rather than patch" ([arXiv:2609.31587v1](https://arxiv.org/abs/2609.31587v1)).

So a document is worth its tokens in proportion to what the code does not show.

## When this backfires

Four conditions answer the purchase test the other way. The fifth is how the answer goes wrong.

- The source does not fit, or is withheld. With the target file removed, optimized descriptions were the best condition on ten of eleven fixtures, "lifting the mean test-pass fraction from 0.08 to 0.71" ([arXiv:2609.31587v1](https://arxiv.org/abs/2609.31587v1)).
- The contract is not in the code. On three hand-built codebases whose intended behavior the code never enforces, the description moved a weak agent "from zero of three attempts to three of three on each of the three codebases". The rule the authors draw: "documentation helps only when it carries intent or a contract the code does not expose".
- The file dwarfs its description. On lambdify, "the largest fixture where the description still fits", the agent without it stalled one test short on every attempt while the agent with it resolved all three, at fewer tokens than loading the file.
- The bug is specification-dependent. Injecting 3GPP excerpts into telecom issue-resolution tasks raised resolve rates on specification-dependent bugs "while the gains on generic defensive checks remain limited" ([arXiv:2604.26278v1](https://arxiv.org/abs/2604.26278v1)).
- The document is generated from the code. A generator that reads the source can only report the source, and an external documentation tool scored 0 of 4 on the contract task: "A tool that documents what the code does cannot supply a contract the code does not exhibit".

The null carries limits of its own: "the largest run uses a single economical model and one summary length near eighty words", the stronger-model replications sit on django subsets, and tasks where some condition produced no edit drop out of the paired comparison ([arXiv:2609.31587v1](https://arxiv.org/abs/2609.31587v1)).

## Example

Both cases below come from the study, not from a constructed scenario.

**Before — a faithful description restating a file the agent can open.** This is the describe stage's own output for the `contains` fixture, reproduced verbatim from Appendix G with two marked cuts:

```markdown
# Module: sympy.sets.contains

This module defines the Contains class, which represents
the boolean assertion that an element x is a member of a
set S.

[...]

### Class Method: eval

@classmethod
def eval(cls, x, s)

Evaluates the membership assertion of an element x in a
set s.
- Inputs: x, any SymPy expression representing the
  element; s, an instance of Set representing the set.
- Returns: S.true or S.false if membership can be
  definitively determined; an instance of Set if the
  evaluation of s.contains(x) results in a Set; None if
  the relation cannot be resolved to a boolean constant
  or a set, which signals SymPy to construct and return
  an unevaluated Contains(x, s) object.
- Raises: TypeError if s is not an instance of Set. The
  error message is "expecting Set, not <type_name>",
  where <type_name> is the class name of s.

[...]
```

"This description regenerates its file at fidelity 1.00", and the authors note that it specifies "the level of internal detail that human-facing documentation typically omits" ([arXiv:2609.31587v1](https://arxiv.org/abs/2609.31587v1)). The source-present runs tested two lengths of description like this one. The full-length form resolved 4 of 15 django fixtures against the issue alone's 9, and 11 of 43 against 14 on the multi-file set with a local Qwen 3.6 agent. A roughly eighty-word compression resolved 29 of 58 against 33 in the largest run, and in a separate django run came out one task ahead at 16 against 15, so read that comparison as no measurable gain rather than reliable harm.

**After — the part the code does not exhibit.** In the study's access-control fixture the engine scans rules in the order supplied. The intended contract, that rules are evaluated by priority and that a deny overrides an allow at equal priority, "is stated only in the description and is nowhere visible in the code's behavior" ([arXiv:2609.31587v1](https://arxiv.org/abs/2609.31587v1)). A documentation generator pointed at that same source scored 0 of 4 on the task, because "it correctly reported that the engine processes rules in input order and does not use priority, which is the observed behavior but the opposite of the contract the task requires". The hand-written contract description scored 4 of 4.

## Key Takeaways

- Across five source-present settings and two model families, no documentation condition beat the issue alone by more than one task ([arXiv:2609.31587v1](https://arxiv.org/abs/2609.31587v1)).
- The measured direction reverses by setting. Documentation was one task ahead on two Gemini 3.1 Pro django runs and three to four tasks behind on the 58-task Gemini 3.8 Flash run, at p=0.22 against compact and p=0.25 against context. Read the result as no measurable gain, not as a general law that documentation hurts.
- The full-length description was the worst condition in both settings where it ran: 9, 8, and 4 resolved on the same 15 django fixtures for issue only, compact, and full-length.
- Apply a purchase test per document. Content the agent can recover by opening the file is a second copy. Content it cannot recover moved the mean test-pass fraction from 0.08 to 0.71 when the file was out of reach.
- The boundary, in the authors' words: "documentation of this kind pays when the source cannot be loaded and is redundant when it can".

## Related

- [Distractor Interference: Relevance Is Not Enough](distractor-interference.md) — the same attention cost, measured on instructions rather than file descriptions
- [The Infinite Context](infinite-context.md) — why context that changes nothing still charges the agent for reading it
- [Semantic Density Optimization for Agent Codebases](../../context-engineering/semantic-density-optimization.md) — the complementary move: raise information per token in the code instead of describing it twice
- [Source Code Minification for State-in-Context Agents](../../context-engineering/source-code-minification-trade-off.md) — another compression lever on the same payload, with its own measured cost
- [Documentation Read Counts Measure Retrievability, Not Value](../../instructions/documentation-read-counts.md) — why usage traces cannot tell you whether a document earned its place
