---
title: "Cross-Layer Evidence for Agent Attack Detection"
description: "Pair kernel syscall traces with application telemetry when agents run in per-session containers, you train your own detector, and post-hoc verdicts are enough, because the attack mechanic fixes which layer carries the evidence."
term: "Cross-Layer Evidence"
tags:
  - security
  - observability
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - kernel evidence for agent security
  - cross-view detection
  - paired application and kernel telemetry
last_reviewed: 2026-09-28
maturity: emerging
---

# Cross-Layer Evidence for Agent Attack Detection

> Pair kernel and application telemetry when one session bounds both, you train your own detector, and post-hoc verdicts suffice; the attack mechanic fixes the layer.

Cross-layer evidence means scoring an agent session on two feature sets at once: the in-container syscall trace of the tool process tree, and the served tool manifest plus the agent transcript. On ACE, a corpus of 4,047 paired sessions across 17 threat models, composing the two gave the highest AUROC for all 10 detectors in distribution and for seven of 10 on held-out attack families ([King et al., 2026](https://arxiv.org/abs/2609.28915v1)). This is narrower than "collect more telemetry". An attack's effect lands in one channel or the other depending on what the attack does, and a detector reading one channel drops below the paper's 0.75 discrimination threshold on the mechanics that land in the other ([King et al., 2026](https://arxiv.org/abs/2609.28915v1)).

## When this applies

Three preconditions decide whether kernel evidence is available to you at all.

- Each session runs in a container or another bounded process scope. ACE attaches one `strace` to one root process inside one Docker PID namespace, which is what binds every recorded event to that session. The paper puts three shapes outside the guarantee: "bare-process agents on shared hosts launched without a wrapper, long-running agent daemons that predate sensor attach, and agents embedded in IDEs or desktop applications". An agent running inside an editor is the third case.
- You will train a detector on your own paired sessions rather than point a stock rule pack at the trace. That gap is most of the result.
- You want post-hoc session verdicts. ACE's defender is an auditor reading one completed session, and the paper states that "Containment is out of scope for this work". The credential has already left the host by the time the score exists.

Below those conditions, the second stream costs a sensor, a capture pipeline and a labeled corpus, and returns a number you cannot act on in time.

## Where the signal lives

These are in-distribution AUROCs for all 12 mechanics in the corpus, averaged across the 10 detectors, with 0.75 as the paper's acceptable-discrimination threshold ([King et al., 2026](https://arxiv.org/abs/2609.28915v1)).

| Attack mechanic | App-View | Kernel-View | Cross-View |
|---|---|---|---|
| Silent exfil via logging | .586 | .976 | .970 |
| Audit-log poisoning | .608 | .932 | .954 |
| Schema-shape tampering | .672 | .844 | .867 |
| Preference manipulation | .687 | .701 | .834 |
| Metadata prompt injection | .783 | .756 | .902 |
| Network redirect exfil | .791 | .794 | .871 |
| Bash command injection | .812 | .846 | .915 |
| Credential direct read | .876 | .882 | .978 |
| Multi-stage persistence | .883 | .867 | .982 |
| Retrieval reference injection | .906 | .703 | .927 |
| Resource exhaustion | .915 | .939 | .973 |
| Output directive write | .967 | .962 | .970 |

Two rows decide the argument. Silent exfil via logging is the corpus's strongest kernel cell and its weakest application cell, because "neither the credential read nor its write to a log sink ever surfaces in the transcript". Retrieval reference injection inverts that: the application layer resolves it at .906 while the kernel drops to .703, because the attack's whole effect is "a text-surface manipulation carrying no distinctive syscall footprint" ([King et al., 2026](https://arxiv.org/abs/2609.28915v1)). Preference manipulation is the one mechanic neither single layer resolves, and composition clears the threshold at .834.

Adding kernel features to application features raised mean AUROC on all 12 mechanics, and the Cross-View was the only view clearing 0.75 on all 12. The margins run from +.384 on silent exfil to .003 on output directive write, and the paper calls the small ones descriptive rather than significant against its error bars ([King et al., 2026](https://arxiv.org/abs/2609.28915v1)).

## Why it works

The two layers are two observation channels, and the mechanic decides which one the attack crosses. A tampered MCP server that reads a credential file during a legitimate tool call and writes to a log sink produces `openat` and `sendto` events and no transcript anomaly. A poisoned retrieval reference does the reverse: altered text in the transcript, and a syscall trace indistinguishable from a normal read. Concatenating a 57-feature kernel vector with a 29-feature application vector sharpens neither channel. It removes the per-mechanic blind spot. Cross-View tops 11 of the 12 mechanics, but the margins at the strong end are small (.003 over App-View on output directive write, .006 behind Kernel-View on silent exfil), so the durable gain is coverage ([King et al., 2026](https://arxiv.org/abs/2609.28915v1)).

The off-the-shelf products fail in opposite directions here. Cisco's mcp-scanner reads the served manifest before the agent runs and caught 15.9% of confirmed-effect attacks at a 16.3% false-positive rate on the tampered-MCP subset, because 52 of the 82 malicious fixtures there change server behavior without touching the manifest. A ported subset of Falco's default rules reads the same syscall stream the trained detectors read and reached 0.565 AUROC in distribution: "Every rule that would fire on a malicious agent session also fires on the corresponding benign session running under the same CLI" ([King et al., 2026](https://arxiv.org/abs/2609.28915v1)). The evidence stream carries the signal; the stock scoring function does not extract it.

## When this backfires

- The agent does not run in a bounded process scope. Attribution is the precondition, not the detector: without one tracer on one root process, kernel events cannot be bound to the session that produced them.
- You deploy default rules instead of training a detector. Falco's ported defaults sit 16 to 35 AUROC points below the trained detectors on the identical stream ([King et al., 2026](https://arxiv.org/abs/2609.28915v1)).
- The attack is textual, or signature-free on both layers. Three mechanic classes are invisible by construction: "Pure tool-return content manipulation, inter-call timing channels, and whitespace steganography produce no signature on either evidence layer by construction" ([King et al., 2026](https://arxiv.org/abs/2609.28915v1)).
- Your operating point comes from this corpus. "The median benign session matches the median malicious session feature-by-feature on the discriminative kernel features" ([King et al., 2026](https://arxiv.org/abs/2609.28915v1)). Separation lives in the upper tail, so a lab-tuned threshold will not survive a production base rate.
- All non-loopback traffic in ACE hits an in-lab sinkhole, so exfiltration succeeds at the syscall layer instead of failing. The captured network fingerprint "differs from the shape a real-deployment capture would record for the same attack" ([King et al., 2026](https://arxiv.org/abs/2609.28915v1)), and that is the fingerprint the exfil mechanics lean on.
- Prevention was the cheaper buy. Argument-level provenance contracts stop some of these attack classes before the syscall happens, and PACT reports 100% security on the three strongest of the five models it ran in full AgentDojo deployments ([Fan et al., 2026](https://arxiv.org/abs/2605.11039v1)).

## What transfer showed

Every ACE capture used one runtime, `claude-haiku-4-5` inside the Claude Code CLI. Transfer was tested once, on a 592-session companion corpus under Mistral's Devstral 2 123B, where three of four detector families held mean AUROC above 0.75. TabPFN fell to 0.662, and permutation importance traced the drop to one featurizer field counting distinct `/tmp` paths, non-zero on every ACE session and zero on 57% of the companion sessions ([King et al., 2026](https://arxiv.org/abs/2609.28915v1)). A feature that encodes one runtime's housekeeping habits is not a feature about attacks, and running the transfer is how you find it.

Sensor cost stays open: ACE used `strace` over 15 tracepoints and reports no overhead figure. AgentSight reaches the same layer through eBPF and states in its abstract that the technique "incurs less than 3% performance overhead" ([Zheng et al., 2025](https://arxiv.org/abs/2508.02736v2)), which is that path's published claim rather than a measurement of the ACE pipeline.

## Key Takeaways

- Kernel evidence discriminates on its own. Every non-linear detector cleared 0.72 AUROC on held-out attack families from the syscall trace alone, and the paper's strongest out-of-distribution result, 0.922, reads only the kernel view ([King et al., 2026](https://arxiv.org/abs/2609.28915v1)).
- Composition wins on coverage, and its margins at the strong end are small: top AUROC for all 10 detectors in distribution and seven of 10 out of it, with three still best on kernel evidence alone ([King et al., 2026](https://arxiv.org/abs/2609.28915v1)).
- Check the per-mechanic table against your own tool surface before deciding whether a second sensor pays.
- Attribution decides availability. Agents running in an editor or as bare processes put the kernel view out of reach however good the numbers look.
- A stock rule pack on the same stream is near random here, so the cost is a trained detector, not a sensor install.

## Related

- [Agentic Detection and Response at the MCP Boundary](agentic-detection-response-mcp.md) — the application-layer sensor this pattern pairs a kernel view with, instrumented at the MCP transport
- [Behavioral Firewall for Tool-Call Trajectories](behavioral-firewall-tool-call-trajectories.md) — enforcement over the same application-layer evidence, applied before the call rather than after the session
- [Trajectory as the Monitoring Unit for Production Agents](../observability/trajectory-as-monitoring-unit.md) — why the session, not the prediction, is the unit both evidence layers attach to
- [Subprocess PID Namespace Sandboxing in Claude Code](subprocess-pid-namespace-sandboxing.md) — the containment side of the container boundary that makes session attribution work
- [Four-Layer Taxonomy of Agent Security Risks](four-layer-agent-security-taxonomy.md) — where a runtime evidence layer sits relative to the other control surfaces
