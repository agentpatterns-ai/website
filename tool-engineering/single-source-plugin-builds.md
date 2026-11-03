---
title: "Single-Source Plugin Builds with a Byte-Compared Distribution"
term: "Single-Source Plugin Build"
description: "Generate every host's plugin package from one tree with a builder that checks completeness, and fail CI when the checked-in copy differs from a fresh build."
tags:
  - tool-engineering
  - plugins
  - tool-agnostic
aliases:
  - byte-compared generated distribution
  - generated distribution freshness test
  - one source tree with host adapters
last_reviewed: 2026-11-03
maturity: emerging
---

# Single-Source Plugin Builds with a Byte-Compared Distribution

> A single-source plugin build generates each host's package from one tree and fails CI when the checked-in copy differs from a fresh build.

Keep one canonical set of skills and personas, and generate every host package from it with a builder that checks two things. Completeness means the package holds every file the skills read at run time. Freshness means a checked-in generated copy still matches what the builder produces today. In the Elephant-Goldfish Model (EGM), the harness guide states that "No harness gets a fork of the skill text" ([harnesses.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/harnesses.md#L3-L5)). See [Elephant-Goldfish design review](../patterns/multi-agent/elephant-goldfish-design-review.md) for the workflow and [plugin and extension packaging](../standards/plugin-packaging.md) for bundle layout and install trust.

## Thin host adapters

Each of EGM's 7 Claude reviewer adapters is a 17-line file that tells the agent to read the shared persona ([adapters](https://github.com/google/elephant-goldfish-model/tree/36343a16f0e0d830a7ed78b0da97695379ab3243/.claude-plugin/agents)). It adds `tools: [Read, Grep, Glob]`, `model: inherit`, and `omitClaudeMd: true` ([comprehension adapter](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/.claude-plugin/agents/comprehension.md#L1-L17)). The synthesizer and bootstrap adapters grant wider tools and omit `omitClaudeMd` ([synthesizer](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/.claude-plugin/agents/synthesizer.md#L1-L8), [bootstrap](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/.claude-plugin/agents/bootstrap_orchestrator.md#L1-L8)). Upstream gives the reason as "This avoids imposing Claude tool names on other hosts" ([harnesses.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/harnesses.md#L78-L81)). Codex ships no adapter, and a general-purpose child reads the persona file ([harnesses.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/harnesses.md#L64-L71)).

## Completeness: the package is a dependency closure

EGM warns that installers copying `skills/` alone break it, "because the skills read `agents/` and `resources/document_standards/` at run time" ([harnesses.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/harnesses.md#L21-L23)).

The builder encodes that closure in two lists. Glob allowlists select shared and per-host files for the `claude` and `openai` targets ([pack_plugin.py](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/scripts/pack_plugin.py#L12-L26)). A `REQUIRED_SHARED` list names 7 skills, 9 personas, 5 document standards, and the reference files the skills load ([pack_plugin.py](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/scripts/pack_plugin.py#L27-L54)). A missing required file raises an error before any output folder exists ([test_packaging.py](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/tests/unit/test_packaging.py#L287-L298)). The builder also rejects symlinks and paths outside the source tree ([pack_plugin.py](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/scripts/pack_plugin.py#L70-L74)), and any manifest that declares hooks, MCP servers, or apps ([pack_plugin.py](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/scripts/pack_plugin.py#L83-L87)).

The required list is kept by hand, and it fell behind at least once. Commit `05f8984` moved the bootstrap README templates into `references/templates.md` on 2026-10-28 ([commit 05f8984](https://github.com/google/elephant-goldfish-model/commit/05f8984cb6e0077b072ba034f66d95ffdde200ee)). The bootstrap skill tells the agent to read that file before writing any contract file ([egm-bootstrap](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-bootstrap/SKILL.md#L424-L427)). The builder added the file to its required list on 2026-10-30 ([commit e138d8a](https://github.com/google/elephant-goldfish-model/commit/e138d8a499d8490aa5994b09b7f628b5b06c3e78)). In those two days, a tree without the file would have built with no error (inference from the diff).

## Freshness: compare the checked-in copy byte for byte

EGM checks in one generated runtime, `distributions/claude/`, and submits that folder through Anthropic's directory portal ([directory.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/directory.md#L26-L30)). A unit test builds a fresh copy and asserts that both folders hold the same paths with the same bytes ([test_packaging.py](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/tests/unit/test_packaging.py#L352-L366)). The design adds the rule "Do not edit generated files independently" ([runtime_packaging.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/designs/runtime_packaging.md#L62-L64)). CI runs the unit suite on every pull request ([tests.yml](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/.github/workflows/tests.yml#L20-L23), [unit job](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/.github/workflows/tests.yml#L65-L79)).

For the archives, the builder sorts entries, stamps every ZIP entry 1980-01-01, and sets mode 0644 on every file ([pack_plugin.py](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/scripts/pack_plugin.py#L105-L120)). A test builds twice and compares the two archives byte for byte ([test_packaging.py](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/tests/unit/test_packaging.py#L38-L50)).

## Why it works

Upstream gives one reason for a single builder, that "Separate hand-maintained packages would drift" ([runtime_packaging.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/designs/runtime_packaging.md#L100-L102)). The byte comparison turns a stale copy into a failed pull-request check (inference). The required list catches a missing run-time dependency the same way, but only for files someone has added to it.

## Where the checks stop

- Reproducibility holds in one build environment. The design says "Do not claim reproducibility across untested toolchain versions" ([runtime_packaging.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/designs/runtime_packaging.md#L58-L60)).
- The freshness test guards the checked-in copy only. The Claude marketplace entry uses `"source": "./"`, the repository root ([marketplace.json](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/.claude-plugin/marketplace.json#L7-L9)), so a marketplace install does not read `distributions/claude/` (inference).
- Output handling is platform-specific. On Windows, exclusive file creation "can follow a dangling symlink". The builder therefore writes the ZIP in a temporary folder and hard-links it into place ([pack_plugin.py](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/scripts/pack_plugin.py#L105-L123), [commit ed06551](https://github.com/google/elephant-goldfish-model/commit/ed0655128c171dabbbd412dd4c270ad2387a9fe7)).
- Release attestation identifies the workflow run from `main`, and the tagged source that run checked out can be a different commit. The guide adds "Attestations do not establish host support or prove that the code is safe" ([releases.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/releases.md#L62-L70)).
- A complete, fresh package can still load differently on each host. The design says "Package validation does not establish directory approval or runtime support" ([runtime_packaging.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/designs/runtime_packaging.md#L13-L16)). Test each client as [per-surface plugin verification](per-surface-plugin-verification.md) describes.

## Cost

Each edit to an included file needs a regenerate step, and the pull request carries the change twice. Commit `05f8984` changed `SKILL.md` and `templates.md` under both `skills/` and `distributions/claude/` ([commit 05f8984](https://github.com/google/elephant-goldfish-model/commit/05f8984cb6e0077b072ba034f66d95ffdde200ee)). EGM writes the regenerate step into its release checklist ([releases.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/releases.md#L20-L21)). A plugin with no checked-in generated copy gains nothing from the freshness test (inference).

## Example

The EGM freshness test builds into a temporary folder and compares path-to-bytes maps ([test_packaging.py](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/tests/unit/test_packaging.py#L352-L366)):

```python
def test_published_claude_runtime_is_current(tmp_path: Path) -> None:
  """The directory subfolder must contain exactly the reviewed runtime."""
  generated, _ = build(ROOT, "claude", tmp_path)
  published = ROOT / "distributions/claude"

  def contents(folder: Path) -> dict[str, bytes]:
    return {p.relative_to(folder).as_posix(): p.read_bytes()
            for p in folder.rglob("*") if p.is_file()}

  assert contents(published) == contents(generated), (
      "Published Claude runtime differs from generated output. Regenerate "
      "with `python3 scripts/pack_plugin.py --target claude --output "
      "<output-dir>`; replace `distributions/claude` with the generated "
      "`egm-claude` folder."
  )
```

The dictionary comparison fails on an extra file, a missing file, or one changed byte. File timestamps play no part, because the test reads file contents only.

## Key Takeaways

- Add a file to the required list in the same commit that adds a run-time read of it. In EGM the two changes landed in separate commits, two days apart.
- Fix entry order, timestamps, and modes before you compare archive bytes, and claim reproducibility only for the toolchain you test.
- Check which path each marketplace entry installs from. A freshness test on a copy no marketplace installs protects that copy and nothing else.
- Keep provenance, package contents, and host behavior as three separate pieces of evidence. Release attestation and the byte test say nothing about host behavior.

## Related

- [Elephant-Goldfish Design Review](../patterns/multi-agent/elephant-goldfish-design-review.md) — the workflow this build packages
- [Per-Surface Verification of Agent Plugin Packages](per-surface-plugin-verification.md) — the host-behavior check that build output does not replace
- [Plugin and Extension Packaging](../standards/plugin-packaging.md) — bundle layout, distribution levels, and install trust
- [Portable Agent Definitions](../standards/portable-agent-definitions.md) — translating one definition into many host formats
- [Agent Config as a Managed Supply Chain](../instructions/agent-config-as-managed-supply-chain.md) — the consumer side, pinning the bytes you install
- [Skill Reuse as Vendored Forking](skill-reuse-as-vendored-forking.md) — what happens to copied skill text with no builder behind it
