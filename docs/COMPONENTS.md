# Component guide

All icons and components are original artwork under the project's MIT license.
They use ordinary SVG paths, shapes and escaped text. Assets contain no embedded
scripts, HTML, raster images, remote font requests or external references.

| Family | Output size | Copy budget |
|---|---|---|
| Hero | 1200 × 360 | Name ≤64; tagline ≤140; eyebrow ≤65 |
| Section | 1200 × 76 | Title ≤90; number + one 24px icon |
| Divider | 1200 × 32 | Decorative |
| Features | 1200 × variable | Up to six cards, maximum three columns |
| Terminal | 1200 × variable | Fourteen lines maximum |
| Metrics | 1200 × 140 | Four values maximum |
| Pipeline | 1200 × 130 | Six steps maximum |
| Footer | 1200 × 100 | Project identity |

`<picture>` selects explicit light/dark variants, including section headings and widgets.
All meaningful images carry text alternatives; numbered sections sit inside real `h2`
elements with explicit anchors. Examples should also appear as copyable code in prose.

Visual review:

```sh
python -m readme_builder preview . --output preview.html
```

Open the generated file in a browser. Review both modes, long titles, accents, line
wrapping and 375px/768px/1200px widths. The contact sheet shows components, not the
GitHub Markdown renderer. Check the actual repository page before calling the full
README layout verified. Thin text will naturally shrink when a wide SVG is scaled;
put essential instructions in normal Markdown, too.

Design direction: generous space, one restrained accent gradient, consistent corner
radii, an editorial hierarchy, and repeated components only where they help scanning.
Prefer useful content over adding every available widget.

## Motion and reusable icons

Set top-level `motion` to `subtle`, `ambient`, or `off`. Motion decorates the top edge; it never moves text or changes chart values. Subtle motion stops after four seconds. CSS reduced-motion media queries disable every injected effect. The static layout remains useful in renderers without CSS animation.

The optional `lucide-` vocabulary contains 39 vendored icons with original notices; see [licenses](../THIRD_PARTY_NOTICES.md). `animate` previews file changes by default, refuses executable/external SVG markup, and can remove only its own animation block with `--preset off`. Existing animation from another generator is preserved.
