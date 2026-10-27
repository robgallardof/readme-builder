| Component | Designed for |
|---|---|
| **Hero** | An original geometric mark, clear identity and a short promise. Explicit light/dark variants. |
| **Section** | Numbered bands with line icons, real heading semantics and stable anchors. |
| **Divider** | A quiet gradient rule to separate ideas without visual noise. |
| **Features** | Up to six cards, with authored benefits and their own icons. |
| **Terminal** | A copyable example shown as a terminal widget; no invented execution result. |
| **Metrics** | Up to four declared facts. Use measurements only when you have their evidence. |
| **Pipeline** | A compact sequence of up to six steps. |
| **Footer** | A matching closing signature. |

Three palettes: **Aurora** (violet/cyan), **Ember** (orange/rose), **Ocean** (blue/teal).
Component layouts and the original icon set are MIT licensed. An optional, bundled set of **39 Lucide icons** retains its ISC / Feather-derived MIT notices ([attribution](THIRD_PARTY_NOTICES.md)). No remote fonts,
scripts, tracking pixels or third-party image rendering. List the icon vocabulary:

```sh
python -m readme_builder icons
```

See the [component guide](docs/COMPONENTS.md) for layout limits and preview instructions.

### Motion and alignment

Generated hero, widget, divider and footer rows are centered. All SVGs default to
`"motion": "subtle"`: a decorative accent makes two passes and stops after four seconds.
Text and data geometry remain still. Choose `"ambient"` for a slow continuous effect
or `"off"` for static output. Every preset honors `prefers-reduced-motion`.

```sh
python -m readme_builder animate assets/banner.svg                # dry run
python -m readme_builder animate assets/banner.svg --write
python -m readme_builder animate assets/banner.svg --preset off --write
```

Use icon names such as `lucide-brain-circuit`, `lucide-shield-check`,
`lucide-clapperboard` and `lucide-layout-template`. All geometry is bundled:
no CDN or JavaScript is needed. Existing SVG/SMIL animations are preserved.

Owner branding is optional: provide your logo and profile through `branding`. The final signature remains last. For a requested diagram, prefer Archify and import its verified light/dark SVG exports.

Headings and feature descriptions use real Markdown so text wraps at the reader's font size. Text never moves; only decorative accents do.

### Showcase kit

Plain link rows and walls of text become designed pieces. Every kit component has
light and dark variants, slow CSS-only motion and a `prefers-reduced-motion` off switch.

| Component | Use it for | Motion |
|---|---|---|
| **Button** | Links, navigation, language switch, back to top | A sheen on primary buttons |
| **Stats** | A row of short, declared facts instead of `a · b · c` text | A glint on each top rule |
| **Wave** | The divider between sections | Two lines flow in opposite directions |
| **Heading** | A numbered section opener for profiles and landing pages | A light travels along the rule |
| **Card** | Linkable project cards, two per row | A status pulse on badges |
| **Bento** | An about grid with cells of different widths | Soft orbs on wide cells |
| **Panels** | Grouped chips (a stack) or short lists (a toolbox) | Still |

Fill marked blocks from a JSON spec, or upgrade an existing README in place:

```sh
python -m readme_builder kit render kit.json             # fills <!-- kit:ID --> blocks
python -m readme_builder kit upgrade README.md            # dry run
python -m readme_builder kit upgrade README*.md --write   # buttons and wave dividers
```

`build` already uses kit buttons and waves. See the [kit guide](docs/KIT.md); the
[profile](https://github.com/robgallardof) is built entirely with it.
