---
title: "Replacing the LLM Filter Stage With a Fine-Tuned Classifier"
term: "Fine-Tuned Classifier Filter Stage"
description: "GitHub replaced its LLM secret-scanning pipeline with regex candidate generation plus a fine-tuned ModernBERT classifier, and reports five gains, every one of them relative to that single predecessor."
tags:
  - testing-verification
  - tool-agnostic
  - cost-performance
aliases:
  - classifier filter stage
  - small classifier instead of an LLM judge
  - encoder classifier second stage
last_reviewed: 2026-10-16
maturity: emerging
---

# Replacing the LLM Filter Stage With a Fine-Tuned Classifier

> A fine-tuned classifier can replace the LLM that adjudicates a gate's candidates, and the conditions that make it work are narrow.

GitHub shipped a new secret scanner built as two stages, regex candidate generation followed by a fine-tuned ModernBERT classifier, replacing what it calls "the previous LLM pipeline". Against that predecessor it reports higher precision, higher recall, higher owner-weighted customer acceptance, lower median post-push scan execution time, and lower serving cost ([Ozturkler and Fu, 2026](https://github.blog/ai-and-ml/githubs-model-for-secret-detection-finding-more-secrets-with-less-noise/)). The post does not describe how the previous pipeline was structured, so the comparison is pipeline against pipeline. What it does detail is the new adjudicating stage, and that stage is what this page is about: the one in your own gate.

## When the swap applies

GitHub states three conditions as a lesson it drew from the work: "We also learned that model size is not the same as model usefulness. A smaller fine-tuned classifier can be the right answer when the task is narrow, the decision boundary is measurable, and serving efficiency is critical" ([GitHub Blog](https://github.blog/ai-and-ml/githubs-model-for-secret-detection-finding-more-secrets-with-less-noise/)).

A fourth condition sits in how the model was built rather than in that sentence. The training set draws on product feedback with human validation, human-annotated regex candidates with weak labels, and synthetic rows aimed at sparse and difficult cases, and the operating point was chosen on that evidence: "We select thresholds through offline evaluation and then validate behavior on production-like traffic before broader rollout." Both halves of that need labels. A gate with no history of adjudicated true and false positives has nothing to fit and no evidence to pick a threshold on.

## What each stage decides

Stage one stays deterministic and wide. "Regex filters scan content for potential secrets with high recall," and the model is additive to it: "The important design choice is that the model does not replace deterministic scanning."

Stage two reads a bounded window around each candidate. "Each model input includes the candidate value, file path, secret type, and a bounded amount of surrounding context." What it hands back is one number: "The output is a classification score used by the scanner to decide whether the candidate should proceed" ([GitHub Blog](https://github.blog/ai-and-ml/githubs-model-for-secret-detection-finding-more-secrets-with-less-noise/)).

## What GitHub reports, and under which conditions

| Figure | Condition GitHub attaches to it |
|---|---|
| 13% higher precision, 19% higher recall | Offline, post-push scanning, same public traffic, against the previous LLM pipeline |
| 11.5% higher acceptance | Online customer A/B; acceptance weighted by repository owner "to reduce the influence of customers who bulk-resolve large volumes of alerts at once" |
| 86% lower median scan execution time | Post-push scanning, against the previous LLM-based pipeline |
| More than 98% lower serving cost | "Cost of the compact classifier compared with remote LLM calls" |

Source: [Ozturkler and Fu, 2026](https://github.blog/ai-and-ml/githubs-model-for-secret-detection-finding-more-secrets-with-less-noise/).

Every figure is relative to GitHub's own previous LLM pipeline. The post publishes no absolute precision or recall, no false-positive rate, no alert volumes and no dataset sizes, so the set gives a direction of travel rather than a target to import. It also never says whether the model in that previous pipeline had been fine-tuned, which leaves the size question and the tuning question tangled together.

The latency figure moved an existing check earlier. Push protection and post-push scanning were already the two moments GitHub's secret scanning runs at; what the speed changed is which detections reach the earlier one. GitHub writes that the efficiency "made it practical to extend generic secret detection to push protection, returning results before developers push changes, not only after code is committed." The post does not claim the previous pipeline missed a deadline. It claims the new one made the extension practical.

## Why it works

Two causes, both stated by the source. The first is that generation is overhead for a stage that only needs a score. ModernBERT gives "contextual understanding comparable to an LLM without the latency and computational overhead of generating natural-language output."

The second is that the model is fitted to the decision the scanner actually makes: "For secret scanning, the model needs to make a calibrated decision over short candidate windows with high throughput and low latency. That makes a fine-tuned encoder classifier a better serving shape than a general-purpose LLM for this stage of the pipeline. The model can be trained directly on our decision boundary, and evaluated using the same recall and precision metrics that matter to secret scanning quality." The deployment detail is ordinary engineering: "The trained model is exported to ONNX format with 8-bit quantization, enabling fast inference" ([GitHub Blog](https://github.blog/ai-and-ml/githubs-model-for-secret-detection-finding-more-secrets-with-less-noise/)).

## When this backfires

- Size may not be what wins. On a 54,148-instance benchmark of secrets in GitHub issue reports, "smaller models such as RoBERTa and CodeBERT greatly improve performance (F1 = 92.70%)" while "fine-tuned open-source larger LLMs such as Qwen and LLaMA reach up to 94.49% F1" ([Ahmed et al., arXiv:2410.23657v4](https://arxiv.org/abs/2410.23657v4)). On that benchmark the larger fine-tuned LLMs scored above the smaller encoder models.
- Your corpus is not the one these numbers came from. The same authors validated on a different corpus, 178 real-world GitHub repositories, "achieving an F1-score of 81.6% which demonstrates our approach's strong ability to generalize to in-the-wild scenarios" ([Ahmed et al., arXiv:2410.23657v4](https://arxiv.org/abs/2410.23657v4)). That sits below both of their benchmark figures, and the authors read it as strong generalization.
- The retraining loop is future work. GitHub lists it under what comes next: "We will use production feedback loops to identify new false negatives and false positives, turning real-world signals into higher-quality training and evaluation data" ([GitHub Blog](https://github.blog/ai-and-ml/githubs-model-for-secret-detection-finding-more-secrets-with-less-noise/)). A boundary that shifts every quarter needs that loop in place before the swap.
- The stage cannot explain itself. Skipping "the latency and computational overhead of generating natural-language output" is where part of the speed comes from, and the output skipped is the rationale. Where your gate has to tell a developer or an agent why it blocked, that is the part you wanted.
- Volume and hosting decide whether the cost figure means anything. The 98% compares a compact model on GitHub's own inference infrastructure against remote LLM calls. At a few thousand calls a month, or with nowhere to serve a model, the saving is nominal and the operating work moves onto your team.

## Example

GitHub's post pairs each credential shape with the harmless twin that matches the same pattern:

| Likely real credential | Likely harmless lookalike |
|---|---|
| A password assigned beside a production database URL | The same password-shaped value in a test fixture |
| A connection string in deployment configuration | A localhost connection string in a setup guide |
| A high-entropy value bound to an API credential | A high-entropy checksum, build ID, or asset hash |

Source: [Ozturkler and Fu, 2026](https://github.blog/ai-and-ml/githubs-model-for-secret-detection-finding-more-secrets-with-less-noise/).

Both columns clear stage one, because both match the regex. Only the context around the value separates them, which is why the second stage reads that context and the first cannot. The transferable move is what the table argues for: a recurring false-positive class is a reason to train on context. GitHub names the cost of the alternative directly. "Adding more rules can suppress some of them, but each exception risks hiding a real secret."

## Key Takeaways

- Check four conditions before swapping the adjudicator: a narrow task, a measurable decision boundary, a binding serving cost, and a store of adjudicated examples. GitHub names the first three; the fourth shows up only in how it built the model.
- Keep the deterministic first stage. The shipped design is explicit that "the model does not replace deterministic scanning", so the regex stays and the classifier filters what it emits.
- Carry GitHub's figures with their conditions or do not carry them. Every one is relative to a single predecessor, and no absolute precision, recall, or false-positive rate is published.
- Cost the retraining loop into the decision. GitHub describes its own production feedback loop in the future tense.

## Related

- [Static-First Shell Command Gating with Selective Escalation](../security/static-first-shell-command-gating.md) — the companion decision about which candidates reach a second stage at all.
- [Specialized Small Language Models as Agent Sub-Tools](../patterns/agent-design/specialized-slm-as-agent-tool.md) — a small model behind a tool call, placed there to absorb context rather than to adjudicate candidates.
- [Deterministic Guardrails](deterministic-guardrails.md) — where a rule beats a model outright, and how to tell which half of a gate you are writing.
- [Sizing Secret Defense at the Push as Agent Volume Grows](../security/push-boundary-secret-defense-agent-volume.md) — the capacity argument for moving secret handling to the push boundary.
