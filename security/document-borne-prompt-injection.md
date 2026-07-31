---
title: "Document-Borne Prompt Injection Through Agent Read Tools"
term: "Document-Borne Prompt Injection"
description: "A file that crossed a provenance boundary is untrusted the moment a read tool returns it. Copilot for Word strips formatting before inference, so concealed text stays invisible to the reviewer and legible to the model, then copies itself into the next document."
tags:
  - security
  - agent-design
  - tool-agnostic
aliases:
  - document-borne prompt injection
  - document channel prompt injection
  - self-propagating document injection
last_reviewed: 2026-07-31
maturity: emerging
status: current
---

# Document-Borne Prompt Injection Through Agent Read Tools

> A file an agent opens is untrusted input once it crossed a provenance boundary — the read tool, not the network, carries the payload.

Draw the trust boundary at the tool result, and scope it by where the file came from rather than how it arrived. A market analysis downloaded from a compromised site, a shared spreadsheet, a vendored dependency, an artifact another agent wrote — each is third-party content the moment a read tool returns it, exactly like a fetched web page. A file your own team authored in a repository it controls is not. That distinction is the whole control; a blanket rule over every read is both unaffordable and ineffective.

## Why the document path gets missed

Teams build their untrusted-input model around fetches, because a fetch looks like it reaches outside. A file read looks like the opposite: the user asked for it, so it reads as intent rather than third-party content. Harnesses encode that assumption. GitHub Security Lab's assessment of VS Code agent mode records that sensitive tools require confirmation but "some standard tools, such as `read-files`, are automatically executed", because "prompting users to approve every tool invocation would be tedious" ([Stepankin, 2026](https://github.blog/security/vulnerability-research/safeguarding-vs-code-against-prompt-injections/)).

Retrieval widens the gap, because the user need not choose the file at all. Håkon Måløy's disclosure shows Microsoft 365 Copilot searching a victim's OneDrive, pulling in a malicious document filed outside the relevant folder, and executing its instructions ([Måløy, 2026](https://enklypesalt.com/posts/context-collapse-part3-ai-worming-through-word/)). Frank Dickson of IDC puts the strongest lever here rather than at the model: "the most useful lever right now sits outside the model entirely, in how much untrusted content Copilot is allowed to pull into a session without a human choosing it" ([CSO Online, 2026](https://www.csoonline.com/article/4203630/microsoft-confirms-an-ai-worm-is-propagating-through-copilot-and-other-ms-apps.html)).

## Why it works

Concealment is free because the human's rendering and the model's rendering diverge. Måløy reports that "Copilot for Word strips all text formatting like color and font size before passing the text into the underlying Large Language Model (LLM), this text remains fully readable to Copilot even though the victim cannot see it" ([Måløy, 2026](https://enklypesalt.com/posts/context-collapse-part3-ai-worming-through-word/)). His payload was white text at font size 8. The strip is a one-way filter: every channel a container format offers for text a reader will not see — color, size, comments, tracked changes, metadata — arrives as plain tokens.

Detection cannot be delegated to the model doing the reading, because reading is the compromise. The model has to process external content to judge whether it contains an attack, and by then, Måløy writes, "the attacker-controlled tokens are already influencing the computation that produces it. The content being inspected participates in the act of inspection." That is why two Microsoft mitigations over the 144-day disclosure — a revised "Edit with Copilot" experience and a model upgrade — closed the reported payloads without closing the class, and testing "reproduced the attack with all current mitigations deployed" ([Måløy, 2026](https://enklypesalt.com/posts/context-collapse-part3-ai-worming-through-word/)).

## The propagation step

Documents differ from web pages in one further way: the agent writes them. A payload that tells the agent to copy itself into the output turns each generated file into the next carrier. Måløy's payload framed that instruction as source tracking and the concealment instruction as a readability improvement. By stage two the original malicious document was no longer attached, and the attack still triggered from the previously generated report ([Måløy, 2026](https://enklypesalt.com/posts/context-collapse-part3-ai-worming-through-word/)).

The chain breaks at three points, none of them inside the model:

- Restrict what enters context without a human choosing it. Narrowing automatic document discovery removes one of the two footholds.
- Strip concealed content on write. Refusing to emit text the reader will not see denies the payload its hiding place.
- Diff what the agent changed. IDC recommends "a visible diff or redline of anything Copilot changes in a financial or otherwise consequential document" with human approval — "not a technical fix, it's a workflow one, and it's available today" ([CSO Online, 2026](https://www.csoonline.com/article/4203630/microsoft-confirms-an-ai-worm-is-propagating-through-copilot-and-other-ms-apps.html)).

Provenance metadata stops nothing, but it restores traceability once the carriers are internal, legitimately authored files. Måløy recommends the same: "generated documents should preserve provenance for source material and model-performed edits in metadata".

## When this backfires

- Every file read is treated as untrusted. Confirming every read reinstates the tedium VS Code omitted the gate to avoid ([Stepankin, 2026](https://github.blog/security/vulnerability-research/safeguarding-vs-code-against-prompt-injections/)), and [confirmation fatigue](prompt-injection-threat-model.md) turns high-volume gates into theater.
- The label has no gate consuming it. VS Code already separates tool output as `role: "tool"`, and frontier models follow it anyway ([Stepankin, 2026](https://github.blog/security/vulnerability-research/safeguarding-vs-code-against-prompt-injections/)). A provenance tag with no capability restriction attached changes nothing.
- The workflow needs the document to carry procedure. Måløy's own caveat: "the distinction between data and instructions is not always clear in real-world workflows", such as an agent booking a trip from a document holding the booking procedure ([CSO Online, 2026](https://www.csoonline.com/article/4203630/microsoft-confirms-an-ai-worm-is-propagating-through-copilot-and-other-ms-apps.html)).
- Nothing crosses a boundary. A repository your team wrote, with no downloads, shared files, or third-party dependencies in scope, has no channel to police.
- The agent never authors. Where it only summarizes, the propagation half does not apply and the anti-worm controls buy nothing.
- Severity is oversold. Tyler Reguly of Fortra calls it a "laboratory vulnerability" needing "a perfect storm", noting the concealed prompts sat on an extra apparently blank page. Mike Wilkes of Aikido Security agrees it "is not a conventional worm that spreads automatically" — a user or workflow must still pull the file into context ([CSO Online, 2026](https://www.csoonline.com/article/4203630/microsoft-confirms-an-ai-worm-is-propagating-through-copilot-and-other-ms-apps.html)).

## Example

Måløy's proof of concept used a mock market analysis. The payload sat at the end of the file in white text, split into an instruction that halved every financial figure in the drafted report and an instruction that appended the whole payload to the output in white text at size 8. The employee saw a plausible quarterly report and shared it. A colleague later used that report as source material, and Copilot halved the figures again and copied the payload forward — with the original document no longer attached anywhere ([Måløy, 2026](https://enklypesalt.com/posts/context-collapse-part3-ai-worming-through-word/)).

The propagation shape is not new; the channel is. [Morris II](https://arxiv.org/abs/2403.02817) demonstrated self-replicating prompts spreading through retrieval-backed email assistants. Måløy's contribution is "among the first public demonstrations of document-borne AI-worm self-propagation through normal workflows in a mainstream commercial productivity suite".

## Key Takeaways

- Scope the boundary by provenance, not transport: a file that crossed an organizational or third-party boundary is untrusted the moment a read tool returns it.
- Read tools usually carry no confirmation gate, so the document channel sits outside the untrusted-input model most teams build around fetches.
- Formatting is stripped before inference, so concealed text is invisible to the reviewer and fully legible to the model.
- An agent that writes documents can propagate a payload it read, turning legitimately authored internal files into carriers.
- The controls that work sit outside the model: restrict automatic discovery, strip concealed content on write, diff generated changes, and record provenance in metadata.

## Related

- [Prompt Injection: A First-Class Threat to Agentic Systems](prompt-injection-threat-model.md) — the general threat model this channel is one instance of
- [Authority Confusion: Untrusted Context Must Not Authorize Side Effects](authority-confusion-untrusted-context.md) — separating what informs a plan from what authorizes an action
- [CaMeL: Defeating Prompt Injections by Separating Control and Data Flow](camel-control-data-flow-injection.md) — the architectural fix for content that must enter context anyway
- [Destyling Untrusted Input as a Prompt Injection Defense](destyling-untrusted-input.md) — a representational-layer transform applied to untrusted input before the model sees it
- [Improper Output Handling: Validate Agent Output Before Downstream Use](improper-output-handling-downstream-sinks.md) — the write side, where an authored document becomes the next input
