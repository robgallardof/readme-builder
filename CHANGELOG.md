# Changelog

## 2026-10-27 / Showcase kit

- New `kit` module: buttons, stat strips, animated wave dividers, numbered headings, project cards, bento grids and chip/list panels, all with light/dark variants and reduced-motion support.
- `kit render` fills `<!-- kit:ID -->` README blocks from a bilingual JSON spec; `kit upgrade` converts link rows, for-the-badge navigation and back-to-top links into buttons and adds wave dividers.
- `build` now emits kit navigation, language buttons, dividers and back-to-top.
- Overflowing card and bento copy is refused instead of clipped.

## 2026-10-26 / Header-matched footers

- Added full-width owner closing banners that reuse the accepted header palette and logo treatment.
- Kept headers and motion unchanged; imported header SVGs are read-only.


## 2026-10-26 / Reading rhythm and background motion

- Replaced progress-like traces and finite flashes with an opt-in, continuous hero background.
- Kept icons, separators, diagrams and signatures static; respected reduced motion.
- Used native headings and feature text, short navigation and compact owner signatures.


## 0.1.0 — 2026-10-26

- Offline Python CLI for authored Markdown and original SVG components.
- Three palettes, explicit light/dark assets and eight reusable component families.
- JSON/content authoring, deterministic builds, hash ownership and drift checks.
- Dry-run emoji migration with local icons, stable aliases and code-example preservation.
- Local link/anchor auditing, executable-SVG checks and a component proof sheet.
- Bilingual self-generated READMEs, an executable example, reusable agent prompts,
  role contracts and cross-platform CI configuration.

See [verification status](docs/STATUS.md) for actual execution and limitations.

## 2026-10-26 — Reading flow and owner signature

- Explicit section stages support beginner-first reading.
- Optional, validated owner logo/profile branding; signature is always last.
- Archify export import with local light/dark assets and preserved embedded notices.
- Authoring prompts prioritize Archify when requested and keep integrations inside usage sections.
