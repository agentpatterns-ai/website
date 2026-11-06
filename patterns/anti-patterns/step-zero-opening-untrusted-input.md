---
title: "Opening Untrusted Inputs as a Harmless Look (Step Zero)"
term: "Step-Zero attack"
description: "Unzip writes while it reads: 32 of 42 harness-model pairs overran a 4 MiB disk budget, 26 before the model saw any content, so content guards act too late."
tags:
  - anti-pattern
  - security
  - tool-agnostic
  - arxiv
aliases:
  - Step Zero
  - step-zero attack
  - harm before observability
last_reviewed: 2026-11-05
---

# Opening Untrusted Inputs as a Harmless Look (Step Zero)

> Extracting an untrusted archive can overrun a disk budget before the model sees a single file, so a guard on model content arrives too late.

A Step-Zero attack is harm done by the first call that processes an opaque input, such as unpacking an archive or saving a fetched response, before the model has read any of its content. The anti-pattern is treating that first call as a harmless preliminary to the real decision. It applies when the opening call writes while it reads. When the call only returns content to the model, a content check can still act before the harm.

## The anti-pattern

Asked what `./project.zip` contains, the agent runs `unzip`, because only opening the archive reveals its contents. [Qin et al. (2026)](https://arxiv.org/abs/2611.01953v1) tested this across 7 harnesses and 6 models with a crafted archive and a benign twin that lists identically. The prompt was the bare path, and the 4 MiB disk budget was never announced. Extraction overran the budget in 32 of 42 harness-model pairs and in 0 of 42 twins. In 26 of the 42, the overrun came before any member's content reached the model.

No extracting agent bounded the step. All 33 extracting cells used `unzip`, and none set a resource limit. In 17 breaches the agent had already read a listing ([Qin et al. 2026](https://arxiv.org/abs/2611.01953v1)). The attacker did not even need to lie about the size: an archive that truthfully declared 8 MiB breached in 28 of 28 cells.

## Why it works

The opening call couples observation with mutation. `unzip` writes decompressed bytes as it reads them, so the disk limit breaks inside the call, before any tool result returns. The paper proves that a guard reading only the model context can act on carrier content only once that content arrives, which is later than every immediate violation ([Qin et al. 2026](https://arxiv.org/abs/2611.01953v1)).

A listing does not close the gap. The ZIP local file header carries "a redundant copy of the metadata from the central directory header" ([Fifield](https://www.bamsoftware.com/hacks/zipbomb/)). `unzip -l` prints the central directory, and the extractor follows the local header, so the two copies can disagree.

The tool decides whether the harm lands at once or later. A fetch to standard output writes nothing, while `curl -OJ` and `wget --content-disposition` write the body under the server's declared name inside the call ([Qin et al. 2026](https://arxiv.org/abs/2611.01953v1)). On network and image inputs, all 131 cells that wrote the declared file did so after the body reached the model, so a content check had its chance there.

## What to do instead

Replace the opening tool in the harness's own tool layer. The paper's Step-Zero Safe Protocol splits it into two calls. A peek decompresses and reports sizes with zero writes. An extract stages into a private directory, counts produced bytes, and commits only if every member fits. With the gate installed in place of `unzip`, breaches fell from 28 of 28 cells to 0 of 28. On a task that required extracting the project and running its tests, agents completed 25 of 28 cells with the gate and 23 of 28 without it ([Qin et al. 2026](https://arxiv.org/abs/2611.01953v1)).

Offering a safe tool beside the shell does not work. Agents called the bounded tool in 5 of 28 cells, ran a raw extractor in 28 of 28, and breached in 28 of 28 ([Qin et al. 2026](https://arxiv.org/abs/2611.01953v1)).

## When this backfires

- A byte budget refuses large benign archives too, so a person needs a way to raise it per archive.
- A gate keyed on the command name misses an absolute-path call. One harness ran the system `unzip` by its absolute path and breached, so the gate belongs in the tool layer or in a disk quota below the agent.
- The bound is per call, so two gated calls under budget can together exceed it. A budget read from an environment variable is one the agent can override.
- In a disposable container with nothing to protect, a disk quota already caps the bytes. It does not stop an overwrite of an existing file, which an opaque TAR caused in 17 of 84 cells.

## Example

An agent asked to inspect an archive from an unknown source:

**Before — extract first, judge later:**

```bash
unzip -l project.zip        # prints the central directory: 3,896 bytes total
unzip project.zip           # follows the local headers: writes 8,392,440 bytes
```

**After — count the decompressed bytes before anything touches the disk:**

```bash
# Decompress to a pipe, stop one byte past the 4 MiB budget, print the count
unzip -p project.zip | head -c 4194305 | wc -c
# Extract into a staging directory only if the count is 4194304 or less
```

The byte counts in the first block come from the paper's main fixture ([Qin et al. 2026](https://arxiv.org/abs/2611.01953v1)). `unzip -p` extracts files "to pipe (stdout)" instead of to disk ([unzip man page](https://linux.die.net/man/1/unzip)). This shell version is only the peek half. The paper's gate also counts bytes during the real extract and commits by rename, and its code is not yet released.

## Key Takeaways

- Treat extraction, `curl -OJ`, and `tar -x` on untrusted data as writes, not reads.
- For write-while-read tools, a content guard sees the input only after the bytes are already on disk.
- Fix the tool, not the prompt: a staged, byte-counting extract cut breaches to 0 of 28 while 25 of 28 tasks still completed.
- The evidence is one preprint, with one fixture per network and image condition. Measure your own harness before you trust the numbers.

## Related

- [External Artifacts Treated as Data, Not Adversarial Input](external-artifacts-as-data.md) — the wider mental-model failure about content that crosses the read boundary
- [Single-Layer Prompt Injection Defense](single-layer-injection-defence.md) — why a content filter alone leaves gaps like this one
- [Enforced Versus Advisory Controls in LLM-Native IDEs](../../security/enforced-versus-advisory-controls.md) — a gate in the tool layer is enforced; the paper's advisory digest verdict was ignored once
- [Pre-Execution Risk Classification for Terminal Commands](../../security/pre-execution-command-risk-classification.md) — a badge on `unzip` sees the same command for the crafted archive and its twin
- [Dual-Boundary Sandboxing](../../security/dual-boundary-sandboxing.md) — the filesystem boundary below the agent that bounds what a bypassed gate can write
