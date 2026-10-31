---
title: "Declaring the Authoritative Tool Output (Evidence Substitution)"
term: "Evidence Substitution"
description: "Offloading a long tool result gives the agent a choice of which file to read, and some models read the one they wrote themselves. Naming the authoritative output recovered 6.3 to 7.9 points for three GPT models."
aliases:
  - evidence substitution
  - authoritative output declaration
  - answering from self-authored tool output
tags:
  - context-engineering
  - cost-performance
  - arxiv
  - tool-agnostic
last_reviewed: 2026-10-23
maturity: emerging
status: current
---

# Declaring the Authoritative Tool Output (Evidence Substitution)

> Naming which tool output is authoritative recovered 6.3 to 7.9 points over plain retrieval for three GPT models that answered from their own files.

Move a long tool result out of the context window and the agent gains a new decision about which file to read. Where the workspace also holds files the agent wrote itself, some models read those instead of the tool's own report. On 158 execution-verified simulator items, GPT-5.1 lost 11.3 accuracy points and GPT-5.2 lost 7.9 points. The other three models in the main analysis had no measurable net change ([arXiv:2610.26836v1](https://arxiv.org/abs/2610.26836v1)).

## When the cost appears

Three conditions hold together in the measured cases. The agent can create its own output artifacts, so a rival file exists to read. The answer turns on how a number is printed, because for the numeric items here distractors "typically differ from the key in the last printed digit" ([arXiv:2610.26836v1](https://arxiv.org/abs/2610.26836v1)). And the model is one of the affected ones. Pooled over every run per item, the table-of-contents interface moved accuracy against inline delivery like this:

| Model | Change vs inline (pp) | 95% interval |
|---|---|---|
| Claude Opus 4.6 | −0.6 | [−3.8, +2.5] |
| Claude Sonnet 4.6 | −0.5 | [−3.8, +3.2] |
| GPT-5.4 | +0.2 | [−5.5, +5.7] |
| GPT-5.2 | −7.9 | [−14.9, −0.9] |
| GPT-5.1 | −11.3 | [−18.0, −4.9] |

Only the GPT-5.1 difference survives Holm correction over the five models (p=0.005). GPT-5.2's does not (p=0.128, unadjusted 0.032). The split does not follow vendor lines ([arXiv:2610.26836v1](https://arxiv.org/abs/2610.26836v1)).

## Why it works

Retrieval withholds nothing. Every number in the inline report was one read away, so the two interfaces carry the same facts. What changes is the decision the agent has to make: "Inline, one source is in view; under retrieval, the report competes with the files the agent wrote itself, and models that choose badly lose accuracy" ([arXiv:2610.26836v1](https://arxiv.org/abs/2610.26836v1)).

Two documented tendencies make this failure plausible, per the authors: models prefer self-generated context over retrieved context, and they round to significant digits unreliably ([arXiv:2610.26836v1](https://arxiv.org/abs/2610.26836v1)). The self-authored file also prints more digits than the report, so answering from it needs a rounding step, and the GPT models truncated instead. Shown a value that rounds to the key but truncates to a neighboring option, GPT-5.2 picked the neighbor in 26 of 35 trajectories and GPT-5.1 in 19 of 27. Claude Sonnet 4.6 did so in 1 of 35 ([arXiv:2610.26836v1](https://arxiv.org/abs/2610.26836v1)).

The agents were not lazy. Re-running all 11,007 logged simulator calls showed GPT-5.1 and GPT-5.2 computed the keyed value about as often under every interface. Under retrieval the two also took more steps than inline, 9.1 against 7.2. The paper names the failure evidence substitution, "answering from output the agent defined itself instead of the tool's canonical report" ([arXiv:2610.26836v1](https://arxiv.org/abs/2610.26836v1)).

A second study measures a delivery-interface cost in long-memory question answering. Its four-harness comparison includes a 37.9-point drop: "The sharpest regression is Codex with GPT-5.4, which falls from 93.1% under inline grep to 55.2% under programmatic grep" ([arXiv:2605.15184v1](https://arxiv.org/abs/2605.15184v1)). Its reading: "programmatic routing trades context bandwidth for compositional tool competence; gains are realized only when the agent reliably closes the loop".

## What to change

The authors tested two interventions and a rounding-only control against the retrieval interface. They report the first beating the control by +7.3 pp [+0.6, +13.9] and +5.1 pp [−1.6, +12.0] ([arXiv:2610.26836v1](https://arxiv.org/abs/2610.26836v1)). Each row names its own baseline.

| Intervention | Effect | Reading behavior |
|---|---|---|
| Name the authoritative output in the tool description | +7.9 (GPT-5.2), +6.3 (GPT-5.1), +7.8 pp (GPT-5.4) over all retrieval runs | Skipping fell to 0.0% and 1.6%; closure rose to 98.8% and 99.2% |
| Inline the reports that fit the budget | +4.6 (GPT-5.2) and +8.0 pp (GPT-5.1) over the retrieval control | Skipping nearly disappeared; closure returned to its inline level |
| Ask the agent to round correctly | +0.6 and +1.2 pp over all retrieval runs | Agents still skipped, and still truncated in 17 of 25 and 14 of 19 trap cases |

The authors put each three-sentence instruction in the tool description and repeated it in every tool result. The difference is that one named a file and the other gave only a rounding rule. "Telling the agents how to round does not stop the misrounding; directing them to the value already printed at the right precision does" ([arXiv:2610.26836v1](https://arxiv.org/abs/2610.26836v1)). Naming the output also cut mean input tokens per item, from 58.0k to 49.7k for GPT-5.2 and from 34.2k to 30.8k for GPT-5.1.

## Why a net-zero comparison does not clear a harness

GPT-5.4 is the warning. It substituted evidence too, skipping the report in 41.8% of retrieval trajectories, and lost 2.6 pp in exposure and 7.2 pp in closure. Its simulations also produced the keyed value more often under retrieval, worth +4.1 pp [+0.0, +8.1] in build. The two terms offset each other. The net change was −4.4 pp [−12.4, +3.4] on numeric items and +0.2 pp pooled over all runs, neither distinguishable from zero. Both evidence-use terms stayed negative, with intervals excluding zero ([arXiv:2610.26836v1](https://arxiv.org/abs/2610.26836v1)). The naming instruction still lifted GPT-5.4 by 7.8 pp.

The authors' recommendation is therefore a measurement rule as much as a design one: "Output delivery should be validated for each model a harness serves, and by where accuracy is lost rather than by final accuracy alone, since a net effect near zero can hide an evidence-use loss" ([arXiv:2610.26836v1](https://arxiv.org/abs/2610.26836v1)).

## When this backfires

- Your agents cannot author artifacts that duplicate tool output. Here they could add `SELECTED_OUTPUT` or `USER_PUNCH` blocks printing the same quantity with extra digits ([arXiv:2610.26836v1](https://arxiv.org/abs/2610.26836v1)). The paper tests only workspaces where agents can add `SELECTED_OUTPUT` or `USER_PUNCH`.
- The answer survives rounding. The truncation trap covered about two thirds of trajectories that saw the right value and still answered wrongly ([arXiv:2610.26836v1](https://arxiv.org/abs/2610.26836v1)). This error path depends on the printed digit deciding the answer.
- Your model is in the no-cost group. Claude Sonnet 4.6 skipped the report in only 10.5% of retrieval trajectories ([arXiv:2610.26836v1](https://arxiv.org/abs/2610.26836v1)). Reverting to inline delivery on its behalf spends context headroom for no measured net gain, though GPT-5.4 still gained 7.8 pp from the naming instruction alone.
- No window holds the output. Reports reached 846.8k characters. The inline arm retained a head-and-tail excerpt of 100,000 characters; 33 of 158 items exceeded that budget ([arXiv:2610.26836v1](https://arxiv.org/abs/2610.26836v1)). Past that size only the naming instruction applies.
- The prevailing advice runs the other way, with its own evidence. Anthropic's guidance has agents keep "lightweight identifiers (file paths, stored queries, web links, etc.) and use these references to dynamically load data into context at runtime using tools" ([Anthropic, 29 September 2025](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)). A benchmark over 2326 test cases found that "the optimal choice between RAG and LC depends on a complex interplay of factors", among them model size, task type and chunk characteristics ([arXiv:2502.09977v2](https://arxiv.org/abs/2502.09977v2)).

## Example

The condition-specific `execute_phreeqc` system-prompt text from Appendix B, Figure 3 ([arXiv:2610.26836v1](https://arxiv.org/abs/2610.26836v1)).

**Before** — the retrieval description, naming no authority:

```text
Run PHREEQC on an input file. Returns metadata and a TOC for result.out.
File contents are NOT included — use read_file to inspect results.
```

**After** — the added naming instruction:

```text
IMPORTANT: The authoritative values are in result.out, printed at the
precision the answer options use. Before answering, read the section of
result.out that contains the quantity you need and take the value exactly
as printed there. Do not answer from SELECTED_OUTPUT or USER_PUNCH files:
they print unrounded values that can match a neighboring option.
```

On item 121 under the first description, a GPT-5.1 agent defined its own output file in its first call, read that file, and answered A. Its own file printed 2.75065; option A was 2.750. The report it never opened printed the keyed value, 2.751, at line 120, and the paper's abridged trajectory records exactly that as unread at line 120 ([arXiv:2610.26836v1](https://arxiv.org/abs/2610.26836v1)). The paper gives the agent's own reasoning for this class of error as "gives pH = 2.75065, which rounds to 2.750" against a key of 2.751.

## Key Takeaways

- Check whether your agents can write artifacts that duplicate a tool's output. Where they can, offloading the tool's report creates a rival source, which is the precondition for the loss.
- Put the authority in the tool description, not in a rounding rule. Naming the canonical file recovered 6.3 to 7.9 points and cut input tokens; telling the model how to round moved accuracy by 1.2 points or less.
- Measure each stage of evidence use alongside final accuracy. GPT-5.4's roughly ten points of evidence-use loss were invisible in a net result of +0.2 pp.
- Run the comparison per model. Three of five models paid no net cost, so a result measured on one model does not transfer to the next one you route to.
- The paper ran six closed API-served models on one simulator and retained five in its main analysis. Gemini 3 Flash supplied no parseable answer on 46% of inline items and 71% under retrieval, so the authors excluded it. The inline tool description also discouraged extra reads where the retrieval descriptions required them, which the authors flag as a possible confound in reading behavior.

## Related

- [Context Compression Strategies: Offloading and Summarization](context-compression-strategies.md) — the offloading decision this page picks up after
- [Shortening Old Tool Results Under Context Pressure (Half-Life Truncation)](half-life-tool-result-truncation.md) — the other way to keep long tool output from filling the window
- [Observation Masking: Filter Tool Outputs from Context](observation-masking.md) — removing tool output rather than relocating it
- [Long Context vs Retrieval: The Break-Even Decision](long-context-vs-retrieval-break-even.md) — the cost side of the same inline-or-retrieve choice
- [Silent Handoff Failure in Delegated Code Search](silent-handoff-failure-delegated-search.md) — a neighboring case where the evidence reaching the answer is not the evidence that was found
