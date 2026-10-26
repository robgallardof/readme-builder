# Verification status — 2026-10-26

## Implemented

- Offline standard-library CLI: `build`, `migrate`, `audit`, `check`, `preview`, `icons`.
- Three palettes, explicit light/dark SVGs and eight component families: hero,
  section, divider, feature cards, terminal, metrics, pipeline and footer.
- Original MIT line-icon vocabulary, safe text escaping, portable relative assets,
  numbered heading semantics, authored bilingual READMEs and a runnable example.
- Deterministic generation, atomic per-file writes, hash-based output ownership,
  read-only drift checks, source/output path boundaries and collision refusal.
- Dry-run migration, existing code-example preservation, Mermaid label cleanup,
  local heading aliases, BOM/newline preservation and local-reference auditing.
- Prompts for design, migration and review; role contracts; contributor rules;
  a Windows/Linux/macOS CI matrix for Python 3.11 and 3.14.

## Executed locally

- Windows, Python 3.14: `python -m unittest discover -s tests -v` — 14 passed.
- Built this project's English/Spanish READMEs and the example project.
- `build readme.json --output . --check`: passed after generation.
- `check .`: passed after documentation was completed.
- Ran dry-run and write migration on Rekora's English/Spanish READMEs; its five
  tracked README Markdown files passed the local-reference/presentation audit.
- Browser proof sheet: all 49 self-documentation SVGs loaded. Browser text-box
  checks found no text outside their SVG canvases. Reviewed light/dark components
  visually; the proof sheet is not a GitHub Markdown renderer.
- Built a wheel in an isolated build environment, installed it without runtime
  dependencies in a temporary virtual environment, ran the installed command and
  generated the example project successfully. No package was installed globally.
- The local proof sheet at 375px had no horizontal overflow or missing images.

## Limits and not executed

- Python 3.11, Linux/macOS host execution and the new GitHub Actions matrix:
  **NOT EXECUTED locally**; CI is configured to run them on push.
- Package registry publication, remote link availability, screen-reader testing
  and third-party MCP/agent installations: **NOT EXECUTED**.
- Copy remains authored, metrics remain static, and the migration scanner does
  not implement the complete CommonMark grammar. Review nested/complex syntax.
- Generated output is not deleted automatically. Multi-file builds are not
  transactions; only each individual replacement is atomic.

Visual references were the public profile, Rekora, RepoRinse and the existing MCP
READMEs. Other repositories were read as references only and were not modified.
No private repository content is bundled in this public project.
