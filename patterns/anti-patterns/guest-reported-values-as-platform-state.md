---
title: "Recording Guest-Reported Values as Platform State"
term: "Guest-Reported Values as Platform State"
description: "A value returned by code inside a sandbox is tenant input. Vercel's control plane recorded a guest-supplied snapshot record, and rewriting it restored another account's entire filesystem."
tags:
  - anti-pattern
  - security
  - agent-design
  - tool-agnostic
aliases:
  - trusting the guest in a sandbox control plane
  - guest-supplied values as platform state
  - sandbox self-reported result as platform state
last_reviewed: 2026-10-15
maturity: emerging
status: current
---

# Recording Guest-Reported Values as Platform State

> A value your sandbox reports is tenant input. Recording it as platform state gives the guest a write into state the host trusts.

Vercel states the rule without qualification: "Anything that crosses the boundary should be derived server-side or signed with a key the guest cannot reach" ([Vercel, 14 Oct 2026](https://vercel.com/blog/findings-from-the-1-million-dollar-vercel-sandbox-challenge)). Read strictly it covers the agent's own work product. What it governs in practice is the boundary value, one something other than the reporting sandbox resolves against later. That covers a storage path, an authorization scope, or a record a second request reads. A number shown back to the same tenant is not one. A rule applied to every crossing value leaves a sandbox that cannot report anything.

Vercel's control plane crossed that line on its snapshot record. Snapshotting a sandbox meant recording where the data landed as `{storage_url, size, checksum}`. Vercel describes the flaw: "that answer came from software running inside the guest, and services running on the host trusted it" ([Vercel, 14 Oct 2026](https://vercel.com/blog/findings-from-the-1-million-dollar-vercel-sandbox-challenge)). A researcher combined a documented container escape with that flaw and intercepted the snapshot response inside their own sandbox. They rewrote it, "swapping the storage objects of two snapshots belonging to two separate accounts they owned". Restoring one snapshot then produced the other account's entire filesystem, readable and writable.

## Containment is the wrong place to look

Trail of Bits flagged this root cause in the same engagement that cleared the isolation. They spent four engineer-weeks in the source and "concluded that our virtualization boundary is sound" ([Vercel, 14 Oct 2026](https://vercel.com/blog/findings-from-the-1-million-dollar-vercel-sandbox-challenge)). Each sandbox runs on its own Firecracker microVM with a dedicated guest kernel. So a harness on per-task microVMs can pass a virtualization review and still hand a tenant a cross-tenant write. The defect sits in the data path out of the sandbox, not in its isolation. That is why the remedy is a rule about the path.

## Why it works

Deriving the value host-side removes the write instead of filtering it. An attacker controlling the guest can then produce only values the host would have produced anyway. Nothing attacker-chosen reaches the record for a later request to resolve against. That is why the fix was relocation rather than stricter validation: "Snapshot creation moved out of the guest-reachable environment into a host-side service, and storage paths are project-scoped with strictly validated URLs" ([Vercel, 14 Oct 2026](https://vercel.com/blog/findings-from-the-1-million-dollar-vercel-sandbox-challenge)). Signing works for the same reason. It puts the value's authority in a component the attacker cannot execute code in.

## When this backfires

- The value is a claim about what happened inside. A test outcome or a build log has no host-side derivation short of re-running the work, and no outside signer can witness it. Treat it as a tenant assertion and keep it out of anything that decides.
- One tenant, one trust domain. Where no second account's data is reachable, the cross-tenant consequence does not exist and the work buys defense in depth at full price.
- Per-task telemetry. Counters, sizes, and durations cost host CPU to re-derive on every run. A snapshot record is state other requests resolve against; a progress percentage is not.
- Treating one fixed field as closure. Vercel reports no submission reached customer data, and SecurityWeek's coverage of the same challenge ends on what that result does not establish: "not finding a vulnerability does not mean there is no vulnerability" ([SecurityWeek, 2026](https://www.securityweek.com/1-million-sandbox-challenge-uncovers-linux-kernel-flaws/)).

## Example

Vercel's snapshot record before and after the fix, with every line from the write-up ([Vercel, 14 Oct 2026](https://vercel.com/blog/findings-from-the-1-million-dollar-vercel-sandbox-challenge)).

**Before — the control plane records the guest's answer:**

```text
record:        {storage_url, size, checksum}
produced by:   software running inside the guest
host services: trust it as authoritative
```

**After — a host-side service produces the record:**

```text
record:        {storage_url, size, checksum}
produced by:   a host-side service, outside the guest-reachable environment
storage_url:   project-scoped, strictly validated
binding:       every snapshot object bound to the project that created it
```

The counter-argument against doing this is strong, and the source answers it. Vercel states that "Aiming the swap at a specific victim required knowing that victim's internal snapshot storage key, a random 96-bit identifier the platform generates per snapshot and never exposes through the API". The key appears only inside the victim's own sandbox, and "there was no demonstrated path for a stranger to target another tenant". On that reading the researcher needed to own both accounts, and the realistic exposure was corrupting their own records. The fix shipped within a week anyway, "because a boundary that depends on a secret staying secret is not a boundary".

Apply that test to your own harness. List the guest-reported fields your orchestrator writes down, and for each one name what stops a tenant choosing its value. If the answer is a secret that lives inside the sandbox, you have the same defect at a different severity.

## Key Takeaways

- Sort the values crossing out of your sandbox by whether anything else later resolves against them. That subset is the boundary set, and it is much smaller than everything the sandbox reports.
- Relocate the work instead of validating the answer. Vercel moved snapshot creation into a host-side service and bound every snapshot object to the creating project rather than checking the guest's record harder.
- A sound virtualization boundary is not evidence about the control plane. Ask a sandbox vendor which crossing values it derives host-side, separately from how the isolation is built.
- The low-severity tail is the same bug. Vercel describes its Medium, Low, and Informative findings as small policy-boundary gaps, including "a field that trusted the guest more than it should".

## Related

- [Treating a Worktree as a Safety Boundary](worktree-as-safety-boundary.md) — the inverse error, where the isolation mechanism is weaker than it looks rather than sound and undone downstream
- [Renting a Cloud Agent's Execution Sandbox](../agent-design/rented-execution-sandbox.md) — the deployment shape that creates this seam, with execution in a supplied sandbox and output flowing back to the vendor's loop
- [Multi-Tenant Isolation Knobs for Shared-Container Agent SDK Hosting](../../security/multi-tenant-isolation-knobs-agent-sdk.md) — the per-tenant controls this defect routes around without defeating
- [Field-Level Source Ownership for Agent Capabilities](../../security/field-level-source-ownership.md) — the same question one layer up, asking which source is allowed to fill each field of a tool call
- [Silent Adoption of Corrupted Tool Returns by Agents](silent-adoption-of-corrupted-tool-returns.md) — the model-layer version, where the agent rather than the control plane adopts a returned value it should doubt
