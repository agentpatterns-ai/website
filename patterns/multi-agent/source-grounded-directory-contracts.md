---
title: "Source-Grounded Directory Contracts: Chunked Scouts with Symbol Citations"
term: "Source-Grounded Directory Contracts"
description: "Generate per-directory README contracts bottom-up from read-only scouts that read source in definition-bounded chunks and cite a file and symbol for every entry."
tags:
  - multi-agent
  - context-engineering
  - tool-agnostic
aliases:
  - source-grounded bootstrap docs
  - chunked scout directory documentation
last_reviewed: 2026-11-03
maturity: emerging
---

# Source-Grounded Directory Contracts: Chunked Scouts with Symbol Citations

> Scouts read eligible production code in definition-bounded chunks, cite files and symbols, and pass leaf contracts to parents.

A source-grounded directory contract is a generated `README.md` that lists one directory's interface, invariants, and side effects, each entry citing its code. The worked example is `egm-bootstrap` from the [Elephant-Goldfish Model](elephant-goldfish-design-review.md) ([egm-bootstrap](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-bootstrap/SKILL.md#L15-L24)). Without such files, agents "lack context on local invariants, public interfaces, and side effects" ([bootstrap.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/designs/bootstrap.md#L17-L20)).

## Read caps make omissions

A per-file read cap hides every definition below the cap. Before [PR #109](https://github.com/google/elephant-goldfish-model/pull/109), scouts read most source files only to line 300, under a 50,000-byte directory cap. The design doc still describes both caps ([bootstrap.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/designs/bootstrap.md#L174-L187)). In the PR's run, the capped scout read lines 1 to 300 of a 1,965-line file and missed `parse_batch` and `BatchWriter`. The README marked that code "not yet documented", a [partial-result signal](../../tool-engineering/graceful-tool-output-truncation.md) that named the gap and left it open.

Another scout in that run ignored the cap and read 409 lines. On real codebases, the author reports, the skill wrote RPC methods, tables, and invariants inferred from names ([PR #109](https://github.com/google/elephant-goldfish-model/pull/109)).

## Chunk at definition boundaries

A worker targets chunks of about 1,500 lines at top-level definitions, never mid-body ([chunking rules](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-bootstrap/SKILL.md#L245-L253)). One scout per chunk runs in parallel, and the worker merges their JSON ([egm-bootstrap](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-bootstrap/SKILL.md#L245-L253)). A longer definition can exceed that target (inference; [chunking rules](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-bootstrap/SKILL.md#L245-L253)). Each chunk gets imports and a top-level definition list "so it can judge visibility" ([scout context](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-bootstrap/SKILL.md#L251-L253)).

Templates and configs retain 200-line caps, or 800 in config-only directories ([read limits](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-bootstrap/SKILL.md#L263-L266)). Scouts skip tests, `.css`, and `.scss` ([egm-bootstrap](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-bootstrap/SKILL.md#L255-L266)).

## Cite file and symbol, never infer from names

The scout prompt says "Never infer RPC methods, routes, status enums, or invariants from file or directory names alone". It must cite the exact `[file:symbol_or_flag]` for every entry, and write `["None"]` when the code shows no invariants or side effects ([scout prompt](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-bootstrap/SKILL.md#L204-L219)). It checks build-manifest dependencies and imports before it credits a local file with an RPC service or schema ([egm-bootstrap](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-bootstrap/SKILL.md#L253-L255)). Only the PR states a reason, the name-inferred contracts above.

## Leaf and parent contract shape

| Directory | Template | Sections |
|---|---|---|
| Has direct source files | Component Package ("Peanuts") | Overview, Interface, Invariants, Side Effects, Verification |
| Only subdirectories with code | Intermediate Blueprint ("Hay") | Overview, Subdirectories & Boundaries |
| The run root | Repository Root Blueprint | System overview, child index, global invariants, global side effects, verification |

The [templates](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-bootstrap/references/templates.md#L11-L67) define all three. Workers go leaves first and pass child interface summaries to each parent's scout as prompt context ([propagation](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-bootstrap/SKILL.md#L271-L281)).

## What enforces the rules

Prompts carry most of it. Where the host defines subagents at run time, scouts get no write or subagent tools ([scout prompt](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-bootstrap/SKILL.md#L204-L219)). The worker [schema](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-bootstrap/references/worker-return.schema.json#L1-L20) requires only `subtree_index` and a `path` and `summary` per entry. The repository ships no validator for it (inference). A final pass re-reads every contract for real symbols ([final verification](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-bootstrap/SKILL.md#L381-L391)). The writing run does that pass (inference), and the drift report is optional ([drift review](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-bootstrap/SKILL.md#L402-L416)). A failed scout leaves a placeholder, and the run continues ([fault tolerance](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-bootstrap/SKILL.md#L267-L269)).

## Evidence is one small manual run

The only evidence is one small manual run per version in PR #109. A fresh agent that did not know its version ran each skill on a 4-package Bazel/Python fixture in direct mode ([PR #109](https://github.com/google/elephant-goldfish-model/pull/109)).

- `[file:symbol]` citations rose from 0 to 52 across 5 READMEs.
- A pure helper went from 4 inferred properties to none explicit in code.
- READMEs that admitted unread or unverified code fell from 2 to 0.

The author calls this "evidence, not a benchmark". Name-inference, external-attribution, test-filtering, and Bazel checks already passed on the old skill, so those rules changed "without a measured improvement". No run covered the parallel swarm or correction of existing READMEs. The merging reviewer wrote "I did not rerun the reported fixture". The PR does not report whether each citation is correct.

## Costs

- The skill sets "No per-directory or per-file byte cap" ([egm-bootstrap](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-bootstrap/SKILL.md#L245-L246)), so scout calls grow with source size. The 1,965-line file took 2 chunks, not 1 ([PR #109](https://github.com/google/elephant-goldfish-model/pull/109)).
- Above 15 directories, the root must ask the user before it spawns workers ([safety gate](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-bootstrap/SKILL.md#L112-L124)). After approval it spawns all workers "without artificial concurrency limits" ([spawning](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-bootstrap/SKILL.md#L194-L196)).
- PR #109 reports no token or time figures for a bootstrap run.

## Example

PR #109 added this deterministic scenario. It checks the citation form, the `None` rule, and name inference ([test_scenarios.yaml](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-bootstrap/test_scenarios.yaml#L43-L59)):

```yaml
  - scenario_id: "bootstrap_code_grounding"
    description: "Verifies contracts cite real code symbols in [file:symbol] form, emit None for empty invariants, and do not infer interfaces from directory names."
    eval_type: "deterministic"
    system_prompt:
      skill_file: "skills/egm-bootstrap/SKILL.md"
    turns:
      - user_input: "Bootstrap a README for directory refund_service/. It contains one file, string_utils.py, defining a single pure helper. Show the generated Interface and Invariants sections."
        assertions:
          - type: "required_pattern"
            pattern: "\\[[\\w./-]*string_utils\\.py:\\w+(\\(\\))?\\]"
            message: "Interface entries must cite the source as [file:symbol_or_flag]."
          - type: "required_pattern"
            pattern: "(?i)invariants[\\s\\S]{0,120}none"
            message: "Invariants must be None when the code defines no explicit invariants."
          - type: "forbidden_pattern"
            pattern: "(?i)(issue_?refund|process_?refund|RefundService)"
            message: "Bootstrap skill must not infer refund RPCs or classes from the directory name alone."
```

The PR says the new scenarios "have not been run against a model", because the repository has no eval runner.

## Key Takeaways

- Size scout work by chunk, cut at top-level definitions, so a long file costs more scouts instead of losing its tail.
- Give each chunk the imports and definition list of its file, so the scout can judge visibility.
- Require a file and symbol citation plus an explicit `None`, then check the contracts with a separate pass, not the run that wrote them.
- Put a human approval gate in front of any fan-out that has no concurrency limit.
- Treat PR #109 as one run on four packages. Test large directories and existing READMEs yourself before you rely on the method.

## Related

- [Elephant-Goldfish Design Review](elephant-goldfish-design-review.md) — the full workflow this skill belongs to
- [LLM Map-Reduce Pattern](llm-map-reduce.md) — the general chunk, process, and merge shape
- [Typed Schemas at Agent Boundaries](typed-schemas-at-agent-boundaries.md) — schema-checked handoffs, where EGM's worker JSON is prompt-only
- [AST-Grounded Critic Loop for Documentation Maintenance](../agent-design/ast-grounded-doc-critic-loop.md) — keeping docs aligned with code after it changes
- [Continuous Documentation](../../workflows/continuous-documentation.md) — scheduled drift detection for generated docs
- [Chunking Strategy for RAG-Based Code Completion](../../context-engineering/chunking-strategy-rag-code-completion.md) — function chunks as a retrieval unit, a different job from read coverage
