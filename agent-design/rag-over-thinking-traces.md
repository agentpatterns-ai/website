---
title: "RAG over Thinking Traces: Index Reasoning Trajectories Instead of Documents"
description: "Swap the corpus, not the retriever — for reasoning-intensive tasks, retrieving prior thinking trajectories outperforms retrieving documents and reduces inference cost."
tags:
  - agent-design
  - memory
  - context-engineering
  - tool-agnostic
aliases:
  - thinking trace retrieval
  - reasoning trace corpus
---

# RAG over Thinking Traces

> For math, code, and science tasks, the lever is the corpus, not the retriever — index intermediate reasoning trajectories from prior problem-solving attempts and the same retrieve-then-generate pipeline beats both no-RAG and document-RAG.

## The Corpus Is the Lever

Document RAG is widely treated as ineffective for reasoning-intensive tasks: a textbook chunk does not close the gap between problem and solution. Recent evidence pushes back — the limitation is the corpus, not retrieval. When the index holds **thinking traces** (intermediate trajectories produced by a model attempting similar problems), retrieve-then-generate consistently lifts reasoning performance ([Arabzadeh et al., 2026](https://arxiv.org/abs/2605.03344)).

On AIME 2025–2026, indexing traces produced by Gemini-2-thinking delivered relative gains of +56.3% for Gemini-2.5-Flash, +8.6% for GPT-OSS-120B, and +7.6% for GPT-5, with inference cost flat or down up to 15%. The pattern held on LiveCodeBench (code) and GPQA-Diamond (science), outperforming both no-RAG and retrieval over standard web corpora ([Arabzadeh et al., 2026](https://arxiv.org/abs/2605.03344)).

The mechanism is distribution match. Document chunks describe procedural knowledge; reasoning trajectories enact it. Retrieved exemplars in the same modality as the desired output narrow the gap the model must bridge — the same reason few-shot exemplars beat instruction-only prompting, applied to a retrieval index. Independent confirmation comes from [Buffer of Thoughts](https://arxiv.org/abs/2406.04271), which retrieves distilled "thought-templates", and [Procedural Knowledge at Scale](https://arxiv.org/html/2604.01348), which finds that injecting procedural traces into the thinking stream improves reasoning on math and coding.

## What Goes in the Index

A thinking-trace corpus is built offline from prior solve attempts. Three properties separate a usable corpus from a misleading one:

- **Provenance** — each trace records source model, prompt, and problem class so retrieval can prefer comparable solvers.
- **Outcome label** — successful and failed traces both carry signal, in different ways: successful trajectories serve as direct exemplars, failed ones for negative-example pruning.
- **Structure** — the T3 transform converts long, noisy traces into compact, retrieval-friendly representations, lifting retrieval precision and reducing inference cost ([Arabzadeh et al., 2026](https://arxiv.org/abs/2605.03344)).

```mermaid
graph TD
    A[Solve attempts] --> B[Raw thinking traces]
    B --> C[T3 transform:<br>structured / compact / diagnostic]
    C --> D[Trace index]
    E[New problem] --> F[Retrieve top-k traces]
    D --> F
    F --> G[Solver model]
    G --> H[Answer]
```

This sits next to but is distinct from agent memory patterns. [Episodic memory retrieval](episodic-memory-retrieval.md) stores problem-solving arcs from a single agent's history — typically per project or per session — for cross-session recall. Trace-RAG indexes a separate, larger corpus of trajectories — often from many runs or from a stronger model — used as a reasoning corpus the solver consults at inference time. Both argue the unit of storage matters; they differ on scope and source.

## When the Substitution Pays Off

The benchmark gains are real but not unconditional. The page lives or dies on the conditions, not the headline number.

**Pays off when:**

- The target tasks are reasoning-shaped — math, competitive programming, scientific QA, multi-step debugging — where chain-of-thought is the operative output.
- A trace corpus already exists or can be harvested cheaply — for example, traces produced by a stronger reasoning model on a representative training distribution, then run through a T3-style transform.
- The team can afford the offline pipeline: trace generation, structuring, embedding, periodic refresh.

**Does not pay off when:**

- The target distribution differs sharply from the corpus distribution — a coding agent on a proprietary codebase or internal DSL receives plausible but wrong-domain traces, biasing the solver.
- Traces lack provenance and outcome labels. A corpus that mixes successful and failed runs without distinguishing them propagates failure patterns; this is the trace-side of the [reasoning misalignment](https://arxiv.org/abs/2407.12216) failure mode that already plagues document-RAG.
- The bottleneck is elsewhere. If the agent is failing on tool reliability, prompt drift, or eval gaps, swapping the corpus does not address the cause. [Retrieval is Not Enough](https://arxiv.org/html/2504.14858) argues that even reasoning-shaped retrieval needs test-time critique to be reliable.
- Benchmark contamination risk is high. If the corpus contains traces for the exact items the system will be evaluated on, gains reflect leakage rather than transfer. Provenance metadata and held-out splits are non-negotiable for honest measurement.

The headline +56% on AIME attaches to a specific configuration: math benchmark, traces from a stronger reasoning model, and no contamination across the held-out split. Real production agents that look closer to engineering work than to AIME should expect smaller gains and harder corpus engineering.

## Operating the Corpus

Treat the trace index as a maintained artifact, not a one-time build.

| Concern | What to do |
|---------|------------|
| Freshness | Re-harvest traces when the target distribution shifts (new product area, framework upgrade, model rotation). Stale traces silently bias toward retired patterns. |
| Quality filter | Score traces by terminal outcome and intermediate consistency. Drop failed-without-recovery traces from the success-exemplar shard; keep them in a labelled negative shard for diagnostic retrieval. |
| Structuring | The T3 step is doing real work — compact representations both fit more exemplars in the context budget and improve retrieval precision over raw transcripts. |
| Evaluation | Hold out a slice of the target distribution that did not contribute traces to the corpus. Report gains against both no-RAG and document-RAG baselines, not just no-RAG. |
| Cost accounting | Track end-to-end cost including offline harvest and refresh, not just inference — the inference savings reported in the paper do not include build cost. |

## Example

A small team running an internal math-tutor agent has access to a frontier reasoning model for batch use but not for online inference (cost). They want the cheap online model to perform closer to the frontier on AIME-style problems.

**Before** — document-RAG over a math textbook corpus:

```text
Index: ~10k textbook paragraphs, embedded
Retrieval: top-3 paragraphs by query embedding
Solver: small online model, given paragraphs as context
Result on AIME held-out: roughly the same as no-RAG; paragraphs describe
techniques but the solver still has to instantiate them from scratch.
```

**After** — trace-RAG over T3-structured trajectories:

```text
Index: ~10k thinking traces from the frontier model on a separate AIME-shaped
       training set, T3-transformed into compact diagnostic representations,
       provenance-labelled, success-only shard
Retrieval: top-3 traces by problem-similarity
Solver: same small online model, given retrieved traces as context
Result on the held-out split: substantial relative lift; the retrieved trace
acts as a worked exemplar in the same output modality, narrowing the gap
the small model has to bridge.
```

The lift is not free — the team pays for periodic batch generation and the T3 transform — but online inference cost stays flat or drops, and the corpus refreshes on a slower cadence than user traffic.

## Key Takeaways

- For reasoning-intensive tasks, the high-leverage change is what you index, not how you retrieve. Documents under-deliver; thinking traces over-deliver.
- Trace corpora need provenance, outcome labels, and structuring (T3-style) to be safer than raw transcripts.
- Headline gains attach to math/code/science benchmarks with held-out splits. Production agents on novel distributions should expect smaller lifts and invest in the corpus, not just the pipeline.
- The pattern is orthogonal to per-agent [episodic memory](episodic-memory-retrieval.md) — same intuition (units of storage matter), different scope (cross-run reasoning corpus vs single-agent history).

## Related

- [Episodic Memory Retrieval](episodic-memory-retrieval.md)
- [Memory Synthesis from Execution Logs](memory-synthesis-execution-logs.md)
- [Subtask-Level Memory for Software Engineering Agents](subtask-level-memory.md)
- [Dual-Trace Memory Encoding](dual-trace-memory-encoding.md)
- [Abstention-Aware Memory Retrieval](abstention-aware-memory-retrieval.md)
