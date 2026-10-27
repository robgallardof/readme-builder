# Authoring contract

Use JSON encoded as UTF-8. Run from a clone with Python 3.11+:

```sh
python -m readme_builder build examples/project.json --output demo
```

Top-level fields:

| Field | Meaning |
|---|---|
| `version` | Required; currently `1`. |
| `name` | Required; 1–64 characters. |
| `theme` | `aurora` (default), `ember`, or `ocean`. |
| `motion` | `subtle` (default; slow continuous background opacity), `ambient` (slightly stronger), or `off`. Only explicitly authored hero background layers animate. Icons, headings, dividers, signatures and diagrams stay static. Reduced-motion preference always wins. |
| `documents` | One or more documents with distinct languages and output filenames. |

Owner signatures use the hero's 1200-unit canvas, large logo, rounded frame and
theme palette. The closing banner is shorter and remains static. For an existing
cover, optional `branding.headers` accepts `light` and `dark` local SVG paths;
the footer takes its background and accent colours from `bg`, `brand` and `name`
gradients. Header files are read and validated, never rewritten. Without an SVG
header, the configured theme supplies the palette.

Each document:

| Field | Meaning |
|---|---|
| `file` | `README.md` or `README.language.md`; root-level output only. |
| `language` | Unique lowercase identifier, 1–16 characters (`en`, `es`, `pt-br`). |
| `label` | Language switcher label. |
| `tagline` | Required; 1–140 characters. |
| `eyebrow` | Small upper label; up to 65 characters. |
| `features` | Up to six `{title, text, icon}` cards; title ≤24, text ≤140 characters. |
| `metrics` | Up to four `{value, label}` pairs; value ≤14, label ≤28 characters. |
| `pipeline` | Up to six step strings, ≤28 characters each. |
| `terminal` | `{title, lines}`; at most fourteen lines of ≤110 characters. A static authored example. |
| `sections` | Ordered `{id, title, icon, body}` or `{id, title, icon, source}` entries. |

Section titles are ≤90 characters. IDs are unique word/hyphen identifiers. A `source`
is a Markdown path relative to the JSON file, contained within its directory tree;
`body` is inline Markdown. Source takes precedence when both are present. Icon names
come from `python -m readme_builder icons`. Omitted icons default to `spark` or `layers`.
Visual labels reject emoji; use the icon field. Markdown bodies can be migrated safely.

Generated files live under `assets/readme-builder/`, plus the chosen README filenames
and `.readme-builder-manifest.json`. The manifest records hashes of files this build owns.
Existing changed/unowned files are refused before writing begins unless `--force` is
explicitly supplied. `--check` is read-only and returns 1 when generated output differs.
Stale assets are retained so a later manual reference is not silently broken.

Each file replacement is atomic, but a multi-file build is not a filesystem transaction.
Keep work in Git and review the diff before publishing. The generator does not execute
Markdown, evaluate prompts, fetch URLs, install hooks or invoke project build commands.

## Reading order, owner branding and diagrams

`stage` is optional on sections: `overview`, `start`, `use`, `advanced`, `contribute`,
`license`. When every section specifies it, the builder orders those stages and keeps
original order within each stage. Otherwise it preserves the authored order.
The signature is always last; `check` reports content appended after its closing marker.

```json
{
  "diagram_preference": "archify",
  "branding": {
    "author": "Your name",
    "logo": "assets/brand/logo.jpg",
    "profile": "https://github.com/your-account"
  }
}
```

Branding is opt-in. PNG/JPEG content is validated and embedded in both footer themes;
local paths cannot escape the config directory. Your reusable template stays unbranded
until its author opts in. Profile links must use credential-free HTTPS.

An authored section may add an already exported diagram:

```json
{
  "id": "workflow",
  "title": "How it works",
  "stage": "advanced",
  "diagram": {
    "provider": "archify",
    "light": "assets/diagrams/workflow-light.svg",
    "dark": "assets/diagrams/workflow-dark.svg",
    "alt": "The verified path from request to result"
  }
}
```

The builder validates and copies local SVGs. It does not pretend to render Archify,
execute tools or verify their source claims. `diagram_preference` (`archify`, `svg`,
`mermaid`) tells an authoring agent what to prefer; an explicit user choice wins.
Archify runs separately: [official skill](https://github.com/tt-a1i/archify).
Self-contained exported WOFF2 fonts and safe embedded SVG icons are accepted; remote
URLs, scripts, event handlers and recursive external content are refused.
