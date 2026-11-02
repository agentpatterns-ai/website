---
title: "AI Training Preference Signals in robots.txt"
term: "AI Training Preference Signal"
description: "A robots.txt policy-token group states an AI training preference without touching crawl rules. The syntax, the two rules that bite, and why OpenAI has not yet implemented it."
aliases:
  - "robots.txt training preference signal"
  - "AI training usage preference"
tags:
  - geo
  - technique
  - tool-agnostic
last_reviewed: 2026-11-01
maturity: emerging
status: current
---

# AI Training Preference Signals in robots.txt

> A robots.txt group keyed to `__usage_ai-training` states a usage preference, which is independent of whether any crawler may fetch the page.

OpenAI announced on 30 October 2026 that it will honor a shared robots.txt signal for AI training preferences, and said "We aim to implement the signal in the coming months" ([OpenAI](https://openai.com/index/helping-websites-express-ai-training-preferences)). OpenAI has not announced a shipped implementation.

## Read the conditions before you write the file

The document OpenAI links is an individual Internet-Draft at revision 00 by Kevin Kelley of Anthropic. The IETF datatracker marks it "not endorsed by the IETF" with "no formal standing" in the standards process, and it expires on 3 May 2027 ([draft-kelley-aipref-training-preference-signal-00](https://datatracker.ietf.org/doc/draft-kelley-aipref-training-preference-signal/)).

The syntax is one of three in circulation, and the three disagree. The aipref working group's own document, intended for Proposed Standard, specifies "A Content-Usage directive for the Robots Exclusion Protocol" and writes the preference as `Content-Usage: train-ai=n` ([draft-ietf-aipref-attach-05](https://datatracker.ietf.org/doc/draft-ietf-aipref-attach/)). Cloudflare's Content Signals writes `Content-Signal: ai-train=no` ([contentsignals.org](https://contentsignals.org/)). Both of those sit inside a `User-Agent: *` group, which the signal OpenAI chose will not read as a preference at all.

Compliance is also unobservable. The IAB's AI-CONTROL workshop report names "a lack of any means of monitoring compliance with preferences" as the most-noted cause of distrust here, and records participants asking "whether communicating preferences is sufficient in all cases without an accompanying way to enforce them, or even to audit adherence to them" ([RFC 9969 §2.2](https://www.rfc-editor.org/rfc/rfc9969)).

## Writing the group

The draft binds a usage preference to paths through a policy token in the `User-Agent` line. A site declining training sitewide adds one group, beside whatever crawl rules it already has:

```text
User-Agent: GPTBot
Disallow: /private/

User-Agent: __usage_ai-training
Disallow: /
```

Per §4.3, "ExampleBot still checks whether there are rules for ExampleBot", so `GPTBot` keeps its own crawl rules while the policy-token group carries the training preference for every path. The working-group vocabulary the draft quotes defines AI training as "Using an asset to modify the learned parameters of a generative AI model", and adds that "The training of models that are used to perform exclusively non-generative tasks is not included in this category" ([§3](https://datatracker.ietf.org/doc/draft-kelley-aipref-training-preference-signal/)). The draft adds no directive names or grammar. A nonimplementing parser treats the token as an unrecognized user agent and ignores its group.

## Two rules that bite

A wildcard group does not carry the preference: "wildcard groups (i.e., User-Agent: *) MUST NOT be interpreted as matching the policy token" ([§4.2](https://datatracker.ietf.org/doc/draft-kelley-aipref-training-preference-signal/)). A site that disallows everything under `User-Agent: *` has expressed no training preference at all.

Inside the group, `Allow:` states a preference in favor of training. A disallowed path expresses a preference against the use, and "If it finds that the path is allowed, a preference in favor of that use has been expressed." Omitting the token is neutral. With no `User-Agent: __usage_ai-training` line in the file, "no preference has been expressed." Copying an existing `Allow: /` default into the new group therefore states a preference for training. Silence stated none.

## Why it works

A single cross-vendor token removes a cost that is documented rather than assumed. RFC 9969 records that publishers "need to consult with each AI vendor to understand how to opt out of training their products, as there is significant variance in each vendor's behavior", and must "continually monitor both new vendors and policy updates from the vendors they are aware of" ([RFC 9969 §2](https://www.rfc-editor.org/rfc/rfc9969)). OpenAI names the same cost: operators "would identify individual crawlers and maintain separate rules for each and every provider". One token makes that statement constant in the vendor count instead of growing with it. Deployed parsers skip groups whose user agent they do not recognize. Adding the block is therefore unlikely to change a current consumer's crawling. The draft notes that "some deployed parsers match more flexibly", and that the `__` prefix makes accidental matches unlikely ([§4.1](https://datatracker.ietf.org/doc/draft-kelley-aipref-training-preference-signal/)).

Orthogonality is what settles the trade-off a GEO reader expects to face. The draft states that content-usage preferences and traffic management signals "are independent and orthogonal", and that "This policy token is not a directive for crawling behavior" ([§4.3, §4.4](https://datatracker.ietf.org/doc/draft-kelley-aipref-training-preference-signal/)). The token is not a crawl directive, so it does not by itself block fetching. The draft still lets a consumer use a preference to inform crawling: it "MAY refrain from retrieving resources" with a preference against the use (§4.4). The tiered rules in [AI Crawler Policy](ai-crawler-policy.md) keep working beside it, and OpenAI confirms that "This new signal will not replace the controls we already provide through robots.txt."

## When this backfires

- Reported as a completed OpenAI opt-out. OpenAI has announced future support. Adding the group does not establish that OpenAI enforces it today.
- Crawl rules pasted into the policy-token group. The `Allow:` semantics above turn a copied default into an affirmative training preference.
- Syndicated or mirrored content. The preference uses the robots.txt in effect when the asset is retrieved. A copy served elsewhere answers to another site's file.
- A publisher already under a content licensing deal, because "Private agreements MAY override preferences expressed via this mechanism".
- A site that already blocks at the network layer. Exclusion is achieved, so the token adds a line to maintain and changes nothing observable.

## Key Takeaways

- The token is `__usage_ai-training` in a `User-Agent` line, and the group it heads states a usage preference rather than a fetch rule.
- `User-Agent: *` never carries the preference, and an `Allow:` line inside the group states a preference in favor of training.
- OpenAI aims to implement the signal in the coming months. The draft has no IETF standing, and three syntaxes circulate.
- Keep the per-vendor crawl rules in place. The two signals are orthogonal, so neither overrides the other. The token is not a crawl directive, but a consumer may use it to inform crawling (§4.4).

## Related

- [AI Crawler Policy](ai-crawler-policy.md) — the tiered crawl rules this signal sits beside
- [Agent-Readiness Discovery Surfaces](agent-readiness-discovery-surfaces.md) — which machine-readable surfaces are worth publishing, including Content Signals
- [llms.txt: Spec, Adoption, and Honest Limitations](llms-txt.md) — another declarative file with a thin consumer base
- [How AI Engines Cite](how-ai-engines-cite.md) — what citation reach actually depends on
