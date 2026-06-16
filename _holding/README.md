# Holding area (`docs/_holding/`)

A staging directory for **emerging/experimental drafts** that are not ready to
surface to readers or answer engines. A page parked here is excluded from:

- **The site nav** — via the `_holding/` entry in `mkdocs.yml` `exclude_docs:`
  (the build never renders it), reinforced by `hide: true` in this directory's
  `.pages`.
- **`docs/llms.txt` AND `docs/llms-full.txt`** — via `HOLDING_DIRS` in
  `scripts/generate-llms-txt.py`, which drops the directory from *both* indexes
  (unlike `OPTIONAL_SECTIONS`, which still ship in `llms-full.txt`).

The two mechanisms are independent — keep the `mkdocs.yml exclude_docs` entry
and the `HOLDING_DIRS` set in sync so a draft never leaks through one path.

## When to use it

Park a draft here when it exists in the repo but should not yet appear on the
site or in AI-discoverability indexes — e.g. an experimental pattern under
active iteration, or content awaiting a decision on where it belongs.

This is **not** the same as `docs/emerging/`: that section is nav-visible and
ships in `llms-full.txt` (it is an `OPTIONAL_SECTIONS` entry). `_holding/` is
fully hidden.

## Promote-out path

When a draft is ready to publish:

1. **Move the file** out of `docs/_holding/` into its real section
   (e.g. `git mv docs/_holding/my-draft.md docs/patterns/my-draft.md`).
2. **Add a `redirects.yml` entry** if the public slug changes from any URL the
   draft was ever cited under. Format (relative to site root, no leading slash):

   ```yaml
   _holding/my-draft: patterns/my-draft
   ```

   Pages in `_holding/` are not built, so a redirect is only needed if the draft
   was previously published elsewhere; for a brand-new page no redirect entry is
   required.
3. **Verify nav + indexes pick it up**: run `make nav-check` and, on `main`
   only, `/refresh-llms-txt` (the generator is CI-owned — never regenerate
   `llms.txt` on a feature branch). The moved page now appears in nav and the
   llms indexes like any normal page.

## Verifying the exclusion

To confirm the holding area is excluded, drop a probe page in
`docs/_holding/`, run `uv run mkdocs build --strict`, and check that its URL
appears in neither `site/` nav output nor a freshly generated `llms.txt` /
`llms-full.txt`. Remove the probe afterward.
