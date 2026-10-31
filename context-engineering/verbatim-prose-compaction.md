---
title: "Verbatim Prose Compaction for Lightweight Agents"
term: "Verbatim Prose Compaction"
description: "Keep every user and assistant sentence word for word, cut the tool output, and declare the gap; of three compaction methods tested, only this one never fell significantly behind on either probe set."
aliases:
  - verbatim prose compaction
  - transparent compaction
  - declared-gap compaction
tags:
  - context-engineering
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-15
maturity: emerging
---

# Verbatim Prose Compaction for Lightweight Agents

> Of three compaction methods tested, only verbatim prose retention never fell significantly behind another on either probe set.

Reach for this when the model behind your agent is small, local, or picked for volume. Reach for it also when the rules it must honor were said in conversation rather than written into the repository. The author says the method particularly suits both conditions: "For practitioners, transparent-compact particularly suits local and lightweight models, and sessions in which users state rules and preferences" ([Woolford, arXiv:2610.20116v1](https://arxiv.org/abs/2610.20116v1)). On the one frontier model tested, the harness's own model-written summary passed more commitment probes than the verbatim method, 74.1% against 69.1%. The study's overall comparison against that summary was not significant (p=0.15), and it reads the per-model pattern as "a pattern rather than a demonstrated interaction" ([Woolford, arXiv:2610.20116v1](https://arxiv.org/abs/2610.20116v1)).

## What the checkpoint keeps

The tested method, transparent-compact, is an extension for the Pi coding agent that replaces summary compaction with a deterministic checkpoint. For the compacted span it keeps every user message and all assistant prose word for word. It cuts each tool call to a one-line signature and removes tool outputs and the model's reasoning. The header states what went, down to the caveat that retained prose is "a record of what was said, not verification of its claims". One tool, `context_lookup`, passes a question to a subagent that reads the untouched session file and returns findings ([Woolford, arXiv:2610.20116v1](https://arxiv.org/abs/2610.20116v1)).

| Qwen3.8-27B, 27 probes x 3 repetitions | Verbatim prose | Model summary | Extraction |
|---|---|---|---|
| Commitment pass rate | 74.1% | 64.2% | 53.1% |
| Failed confidently | 14.8% | 22.2% | 40.7% |

Pass rates are the study's ANOVA cell means, with failed turns and missing cells counted as failures ([Woolford, arXiv:2610.20116v1](https://arxiv.org/abs/2610.20116v1)). Neither column generalizes evenly. On commitments the win over extraction ran the same direction on all four models and is significant as an overall method effect. The gap to the model summary is not significant, at p=0.15. The separate planted-fact probes measured recall after three compactions over 18 synthetic sessions. On this model, extraction matched the verbatim checkpoint there, 98.2% against 97.8%, while the model summary reached 75.3%.

## Why it works

Both alternatives select, and a selection rule is a prediction about which turn will need what. The template asks for constraints and decisions, so rules survive and values do not. The extractor matches patterns and positions, so a searchable record survives and a rule phrased in ordinary language does not. In the author's words, it "has no reliable place for a rule stated in ordinary language, and a model that does not know a rule exists does not search for it". Keeping all prose deletes the prediction instead of improving it. The method "pins every user message by construction, so it needs no step that decides which lines are rules". An exploratory case review covered 26 commitment probes on the main model, Qwen3.8-27B. The commitment stood in context word for word 22 times under the verbatim checkpoint, against 9 intact under extraction ([Woolford, arXiv:2610.20116v1](https://arxiv.org/abs/2610.20116v1)).

The author states the principle behind it: "Any rule for choosing what to keep encodes a guess about what later turns will need, and we expect a better template or a better extractor to move the blind spot rather than remove it". ([Woolford, arXiv:2610.20116v1](https://arxiv.org/abs/2610.20116v1))

The study shows how the two lossy methods fail. Of the model summary and the extractor, the author writes: "the errors tend to be confident, because the agent's context holds something that looks like the answer: a stale value beside the right one, a reworded rule, or code retrieved from the history" ([Woolford, arXiv:2610.20116v1](https://arxiv.org/abs/2610.20116v1)). The checkpoint is not exempt. Its confident-failure rate on commitments was 14.8% on Qwen and 23.5% on Sol, where the model summary also scored 23.5%. The study has no arm that isolates the declared gap, so treat the declaration as a design choice, not a tested effect. The inference here is the page's own: a doubting reply gives you a reason to check, and a confident one does not.

Recovery by search costs persistence a small model may not spend. The author writes that not selecting "matters most for lightweight models, which are least able to reason or search their way around a blind spot". The same deterministic extraction context produced "98% on Qwen, 46% on Luna and 68% on Gemma", while the verbatim checkpoint held between 93% and 98% across those three ([Woolford, arXiv:2610.20116v1](https://arxiv.org/abs/2610.20116v1)).

## When this backfires

- A frontier model in a rules-heavy session. On the frontier model, the model summary took the highest commitment pass rate of any condition. The author declines to generalize: "further testing would be required to endorse adoption exclusively for use with frontier models" ([Woolford, arXiv:2610.20116v1](https://arxiv.org/abs/2610.20116v1)).
- Verbatim retention costs more uncached prompt tokens. On the main model's commitment probes the verbatim turns processed on average 57,300 prompt tokens per turn that were not served from cache. Extraction processed 21,389, so verbatim used 2.7 times as many. On a second local model the ratio was 1.7 ([Woolford, arXiv:2610.20116v1](https://arxiv.org/abs/2610.20116v1)).
- Sessions long enough to exhaust the guarantee. The checkpoint's conversation section "is capped, by default at 25% of the model's window", which the author puts at around 10 rounds of compaction before capping starts to bite. Past that, "conservative truncation begins to be applied similarly to pi-vcc", with extractor-like behavior expected beyond 20 rounds. The author puts testing "large numbers of compactions" "beyond the scope of this study" ([Woolford, arXiv:2610.20116v1](https://arxiv.org/abs/2610.20116v1)).
- Named facts plus a model that keeps searching. Extraction matched the verbatim checkpoint on planted facts on the main model, 98.2% against 97.8%. The author's explanation is that the model "kept paging through pi-vcc's search results until it found the values" ([Woolford, arXiv:2610.20116v1](https://arxiv.org/abs/2610.20116v1)).
- The rule never entered the prose. On four of the 26 Qwen commitment probes no method held the commitment, because it "lived only in a document read through a tool or was never stated as a rule" ([Woolford, arXiv:2610.20116v1](https://arxiv.org/abs/2610.20116v1)).
- You judge on task success rather than on what the agent knows. Neither method in this comparison is this checkpoint, and it scores solve rate, not what the agent remembers. On SWE-bench Verified, masking older observations "halves cost relative to the Raw Agent while matching, and sometimes slightly exceeding, the solve rate of LLM-Summary" ([Lindenbauer et al., arXiv:2508.21433v3](https://arxiv.org/abs/2508.21433v3)).
- Weigh the provenance. "The author built transparent-compact". The stated mitigations are third-party methods run as shipped with their defaults, probes "written by models briefed without any mention of the methods", blind scoring, and a replication package ([Woolford, arXiv:2610.20116v1](https://arxiv.org/abs/2610.20116v1)).

## Example

A summary can keep the right value and lose what pinned it to its episode. In one session Pi's model-written summary recorded that a backfill job's batch size had moved to 7,500 after benchmarks. After a later episode about a different job, it also recorded "Chose 2750 because it runs clean". The summary was "no longer saying which job that referred to, and the agent then gave 2,750 as the agreed batch size" ([Woolford, arXiv:2610.20116v1](https://arxiv.org/abs/2610.20116v1)).

Both values were present. What compaction removed was the sentence that told them apart, and nothing in the summary said so, so the agent answered without hedging. It was not an isolated slip. The study reviewed 12 Qwen planted-fact sessions continued past three compactions. In Pi's model-written summary it found 7 cases where a detail was answered correctly and later answered confidently wrong. The right value was still in the summary every time, and in 5 a look-alike value from a later episode stood beside it ([Woolford, arXiv:2610.20116v1](https://arxiv.org/abs/2610.20116v1)). Those sessions were built to contain look-alikes, so read the count as a property of the material and the mechanism as the part that travels.

## Key Takeaways

- Scope the decision to your model class first. On commitments, the verbatim checkpoint's lead over a model-written summary lived on the lightweight models and ran the other way, though not significantly, on the frontier one. On planted facts the same frontier model recalled 99.3% against 75.6% for the summary, in an exploratory run (p<0.001) ([Woolford, arXiv:2610.20116v1](https://arxiv.org/abs/2610.20116v1)).
- Score compaction on confident wrong answers, not only on recall. A flagged miss costs a round trip, and a confident miss becomes an edit.
- A recovery tool is worth what the model will spend on it. The same searchable context yielded 98% and 46% recall on two different models.
- Price it in non-cached prompt tokens per turn, which is where verbatim retention costs 1.7 to 2.7 times the extractor.
- Check how many compactions your sessions reach. Capping starts around ten rounds. Only 12 Qwen planted-fact sessions went as far as eight compactions, and the author expects extractor-like behavior past twenty without testing it. A long session leaves the measured ground early.

## Related

- [Per-Type Retention Policy for Agent Compaction](per-type-retention-under-compaction.md) — the opposite move: classify each line and set fidelity per type, which this page's evidence treats as relocating the blind spot
- [Addressable Recall Compaction](addressable-recall-compaction.md) — verbatim retention applied to tool observations, held outside the context under stable IDs
- [Observation Masking](observation-masking.md) — stripping used tool output, the half of this checkpoint that is already common practice
- [Reasoning Retention and Compaction as Harness Settings](reasoning-retention-and-compaction.md) — what a harness does with private reasoning, which this checkpoint removes and declares
- [Stage Elision Before Summarization](stage-elision-before-summarization.md) — ordering a deterministic pass ahead of the summarizer when cost, not retention, is the binding constraint
