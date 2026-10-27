"""Self-contained SVG components, using local fonts and escaped author copy."""

from html import escape
import textwrap

from .icons import glyph

THEMES = {
    "aurora": ("#8b5cf6", "#22d3ee"),
    "ember": ("#f97316", "#fb7185"),
    "ocean": ("#0284c7", "#14b8a6"),
}


def palette(theme="aurora", mode="dark"):
    """Resolve component colours; no user-supplied CSS is evaluated."""
    a, b = THEMES[theme]
    return dict(a=a, b=b, bg="#0b1020" if mode == "dark" else "#f8fafc",
                panel="#141c30" if mode == "dark" else "#ffffff",
                fg="#eef2ff" if mode == "dark" else "#111c35",
                muted="#a6b3ca" if mode == "dark" else "#4d6079",
                line="#29334d" if mode == "dark" else "#d8e0ef")


def text(x, y, value, size=18, color="#eef2ff", weight=400, **attrs):
    """Escape text and attributes at the SVG boundary."""
    extra = " ".join(f'{key.replace("_", "-")}="{escape(str(v), quote=True)}"' for key, v in attrs.items())
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" '
            f'font-weight="{weight}" {extra}>{escape(str(value))}</text>')


def frame(width, height, title, body, p):
    """Wrap an accessible SVG without network dependencies or executable markup."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title, quote=True)}">'
            f'<title>{escape(title)}</title><defs>'
            f'<linearGradient id="brand"><stop stop-color="{p["a"]}"/>'
            f'<stop offset="1" stop-color="{p["b"]}"/></linearGradient></defs>'
            '<style>text{font-family:Inter,Segoe UI,Arial,sans-serif}</style>'
            f'{body}</svg>\n')


def hero(name, tagline, eyebrow="OPEN SOURCE / BUILT WITH INTENT", theme="aurora", mode="dark"):
    """Render an editorial hero with a geometric document mark."""
    p = palette(theme, mode)
    b = f'<rect width="1200" height="360" rx="24" fill="{p["bg"]}"/>'
    for x in range(0, 1200, 40):
        b += f'<path d="M{x} 0v360" stroke="{p["line"]}" opacity=".28"/>'
    for y in range(0, 360, 40):
        b += f'<path d="M0 {y}h1200" stroke="{p["line"]}" opacity=".28"/>'
    b += '<path d="M0 1h1200" stroke="url(#brand)" stroke-width="3"/>'
    b += text(56, 61, eyebrow, 12, p["a"], 700, letter_spacing="2.6")
    size = min(78, max(24, int(790 / max(len(name), 1) / .58)))
    b += text(52, 159, name, size, p["fg"], 800, letter_spacing="-2")
    for i, line in enumerate(textwrap.wrap(tagline, 65)):
        b += text(56, 208 + i * 29, line, 21, p["muted"])
    b += text(56, 315, "DESIGN THE FIRST IMPRESSION.", 11, p["muted"], 600, letter_spacing="2")
    b += '<g transform="translate(930 76)">'
    b += f'<rect width="210" height="210" rx="42" fill="{p["panel"]}" stroke="{p["line"]}"/>'
    b += '<rect x="30" y="28" width="150" height="154" rx="18" fill="none" stroke="url(#brand)" stroke-width="2"/>'
    b += glyph("layers", p["a"], "translate(62 52) scale(3.5)")
    b += '<path d="M58 150h94m-94 14h60" stroke="url(#brand)" stroke-width="5" stroke-linecap="round"/></g>'
    return frame(1200, 360, f"{name} — {tagline}", b, p)


def divider(theme="aurora"):
    """Render a restrained gradient rule with a centre mark."""
    p = palette(theme)
    return frame(1200, 32, "Section divider", '<path d="M40 16h495m130 0h495" stroke="url(#brand)" opacity=".45"/>'
                 '<path d="m588 16 12-6 12 6-12 6Z" fill="none" stroke="url(#brand)"/>', p)


def section(title, number, symbol="layers", theme="aurora", mode="dark"):
    """Render a numbered heading band with an original SVG icon."""
    p = palette(theme, mode)
    b = f'<rect width="1200" height="76" rx="12" fill="{p["bg"]}"/>'
    b += text(23, 46, f"{number:02}", 13, p["a"], 700, letter_spacing="1")
    b += glyph(symbol, p["a"], "translate(65 25) scale(1.1)")
    size = min(26, max(15, int(1000 / max(len(title), 1) / .58)))
    b += text(108, 48, title, size, p["fg"], 700)
    b += '<path d="M0 75h1200" stroke="url(#brand)" opacity=".5"/>'
    return frame(1200, 76, f"{number:02} · {title}", b, p)


def features(items, theme="aurora", mode="dark"):
    """Render up to six feature cards; copy is authored, never inferred."""
    p = palette(theme, mode)
    columns = min(3, len(items))
    width = (1200 - 16 * (columns - 1)) // columns
    height = ((len(items) + columns - 1) // columns) * 230
    b = ""
    for i, item in enumerate(items):
        x, y = (i % columns) * (width + 16), (i // columns) * 230
        b += f'<g transform="translate({x} {y})"><rect x="1" y="1" width="{width-2}" height="210" rx="16" fill="{p["panel"]}" stroke="{p["line"]}"/>'
        b += glyph(item.get("icon", "spark"), p["a"], "translate(24 24) scale(1.2)")
        b += text(24, 88, item["title"], 20, p["fg"], 700)
        for j, line in enumerate(textwrap.wrap(item["text"], max(20, int((width - 48) / 8)))):
            b += text(24, 120 + 22 * j, line, 15, p["muted"])
        b += '</g>'
    return frame(1200, height, " · ".join(f'{i["title"]}: {i["text"]}' for i in items), b, p)


def terminal(lines, title="quickstart", theme="aurora", mode="dark"):
    """Render an authored transcript with a clear terminal frame."""
    p = palette(theme, mode)
    height = 92 + len(lines) * 27
    b = f'<rect x="1" y="1" width="1198" height="{height-2}" rx="18" fill="{p["panel"]}" stroke="{p["line"]}"/>'
    for x, c in [(28, "#fb7185"), (48, "#fbbf24"), (68, "#34d399")]:
        b += f'<circle cx="{x}" cy="27" r="5" fill="{c}"/>'
    b += text(100, 32, title, 13, p["muted"])
    b += f'<path d="M1 51h1198" stroke="{p["line"]}"/>'
    for i, line in enumerate(lines):
        b += text(28, 88 + i * 27, line, 17, p["b"] if line.startswith("$") else p["fg"], font_family="monospace")
    return frame(1200, height, title + ": " + " / ".join(lines), b, p)


def metrics(items, theme="aurora", mode="dark"):
    """Render declared facts, not fetched or fabricated live statistics."""
    p = palette(theme, mode)
    b = f'<rect x="1" y="1" width="1198" height="138" rx="18" fill="{p["panel"]}" stroke="{p["line"]}"/>'
    cell = 1200 // len(items)
    for i, item in enumerate(items):
        x = i * cell + 28
        b += text(x, 67, item["value"], 36, p["a"], 800)
        b += text(x, 103, item["label"], 14, p["muted"])
    return frame(1200, 140, " · ".join(f'{v["value"]} {v["label"]}' for v in items), b, p)


def pipeline(steps, theme="aurora", mode="dark"):
    """Render a static architecture/process strip with readable step labels."""
    p = palette(theme, mode)
    b = f'<rect width="1200" height="130" rx="18" fill="{p["bg"]}"/>'
    cell = 1200 // len(steps)
    for i, step in enumerate(steps):
        x = i * cell + 16
        b += f'<rect x="{x}" y="20" width="{cell-32}" height="90" rx="12" fill="{p["panel"]}" stroke="{p["line"]}"/>'
        b += text(x + 16, 47, f"{i+1:02}", 11, p["a"], 700)
        for j, line in enumerate(textwrap.wrap(step, max(10, int((cell - 64) / 8)))):
            b += text(x + 16, 73 + j * 19, line, 14, p["fg"], 600)
        if i < len(steps) - 1:
            b += f'<path d="m{x+cell-22} 62 7 4-7 4" fill="none" stroke="{p["a"]}"/>'
    return frame(1200, 130, " → ".join(steps), b, p)


def footer(name, theme="aurora", mode="dark", branding=None):
    """Render a small closing signature."""
    p = palette(theme, mode)
    if branding:
        b = f'<rect width="1200" height="174" rx="16" fill="{p["bg"]}"/>'
        b += '<path d="M32 1h1136" stroke="url(#brand)"/>'
        b += f'<image href="{escape(branding["logo_data"], quote=True)}" x="564" y="18" width="72" height="72"/>'
        b += text(600, 121, branding["author"], 23, p["fg"], 700, text_anchor="middle")
        b += text(600, 148, name, 13, p["muted"], text_anchor="middle")
        return frame(1200, 174, name + " / " + branding["author"], b, p)
    b = f'<rect width="1200" height="100" rx="16" fill="{p["bg"]}"/>'
    b += '<path d="M0 1h1200" stroke="url(#brand)"/>'
    b += text(30, 59, name, 23, p["fg"], 700)
    b += glyph("layers", p["a"], "translate(1138 34) scale(1.4)")
    return frame(1200, 100, name, b, p)
