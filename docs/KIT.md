# Showcase kit

The kit turns README chrome — link rows, navigation, plain fact lines, section
breaks — into designed SVG components. Everything is local, escaped and
self-contained. Motion is CSS-only, slow, decorative and disabled by
`prefers-reduced-motion`. Text never moves.

Themes: `nebula` (default: violet → indigo → sky), `aurora`, `ember`, `ocean`.

## Two ways to use it

### 1. Upgrade an existing README

```sh
python -m readme_builder kit upgrade README.md README.es.md            # dry run
python -m readme_builder kit upgrade README.md README.es.md --write
```

Conservative, idempotent rules; fenced code is never touched:

| Found | Becomes |
|---|---|
| `<p align="center"><a href="…">A</a> · <a href="…">B</a></p>` | A row of small outline buttons |
| A link to `README.md` / `README.xx.md` in such a row | A globe button; the current file is primary |
| A link to `https://…` in such a row | A primary button with an arrow |
| `<a href="…"><img src="…for-the-badge…" alt="Label"></a>` on its own line | A button with the same label and link |
| `Back to top` / `Volver arriba` / `Volver al inicio` | A small button with an up arrow |
| Every `##` heading after the first | A wave divider above it (and above its `<a id>` anchor) |

Assets are written to `assets/readme-builder/kit/`. Live shields (stars, CI,
versions) and tech badges stay as they are.

### 2. Author blocks from a spec

Put markers in your README; the content between them is regenerated:

```md
<!-- kit:links -->
<!-- /kit:links -->
```

```json
{
  "version": 1,
  "theme": "nebula",
  "assets": "assets/kit",
  "documents": {"README.md": "en", "README.es.md": "es"},
  "blocks": [
    {"id": "links", "type": "buttons", "items": [
      {"label": "Docs", "href": "https://example.com", "icon": "lucide-book-open", "variant": "primary", "trailing": true},
      {"label": {"en": "Install", "es": "Instalar"}, "href": "#install", "small": true}
    ]}
  ]
}
```

```sh
python -m readme_builder kit render kit.json
python -m readme_builder kit render kit.json --check   # exit 1 on drift
```

Any string may be `{"en": "…", "es": "…"}`. A marker may appear more than once
(useful for `divider`). Unknown markers are an error.

| Type | Fields |
|---|---|
| `buttons` | `align`, `items[]`: `label`, `href`, `icon`, `variant` (`primary`/`outline`), `trailing`, `small` |
| `stats` | `items[]`: `value`, `label` — declared facts, never live numbers |
| `divider` | none — the animated wave |
| `heading` | `number`, `kicker`, `title`, `icon` — pair it with your own `<a id>` anchor |
| `cards` | `items[]`: `title`, `text` (≤ 4 lines), `href`, `icon`, `kicker`, `tags`, `badge` |
| `bento` | `columns`, `cells[]`: `span`, `icon`, `kicker`, `title`, `text` (≤ 3 lines) |
| `panels` | `style` (`chips`/`list`), `columns`, `groups[]`: `title`, `icon`, `items` |
| `terminal` | `title`, `lines` — a static authored transcript |

Copy that would overflow a card or bento cell is refused, not clipped.
Icons come from `python -m readme_builder icons`.

The [profile README](https://github.com/robgallardof/robgallardof/blob/main/kit.json)
is a complete example.
