"""Showcase kit: buttons, stat strips, wave dividers, headings, cards, bento and panels.

Every component is a self-contained SVG with light and dark variants. Motion is
CSS-only, slow, decorative and switched off by ``prefers-reduced-motion``.
Text never moves; only accents (sheen, wave, travelling dot, status pulse) do.
"""

from html import escape
import textwrap

from .icons import glyph

KIT_THEMES = {
    "nebula": ("#7c3aed", "#4f46e5", "#0ea5e9"),
    "aurora": ("#8b5cf6", "#6366f1", "#22d3ee"),
    "ember": ("#f97316", "#f43f5e", "#fb7185"),
    "ocean": ("#0284c7", "#0891b2", "#14b8a6"),
}
FONT = "font-family:'Segoe UI',-apple-system,BlinkMacSystemFont,'Helvetica Neue',Inter,Arial,sans-serif"
REDUCED = "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"


def colors(theme="nebula", mode="dark"):
    """Resolve a kit palette; values are constants, never user CSS."""
    if theme not in KIT_THEMES:
        raise ValueError(f"unknown kit theme: {theme}")
    a, m, b = KIT_THEMES[theme]
    dark = mode == "dark"
    return dict(a=a, m=m, b=b,
                panel="#10162a" if dark else "#ffffff",
                panel2="#151c33" if dark else "#f6f8fc",
                fg="#e8edf7" if dark else "#0f172a",
                muted="#9aa7bf" if dark else "#516079",
                line="#253150" if dark else "#dfe5ef",
                accent="#a78bfa" if dark else "#6d28d9")


def width_of(value, size, weight=400):
    """Estimate rendered width for system sans fonts; generous so text never clips."""
    total = 0.0
    for char in str(value):
        if char in "il.,:;'|!·":
            total += .29
        elif char in "fjrtI() -/":
            total += .38
        elif char in "mwMW@%":
            total += .86
        elif char.isupper() or char.isdigit():
            total += .64
        else:
            total += .55
    return total * size * (1.06 if weight >= 600 else 1.0)


def t(x, y, value, size, fill, weight=400, anchor="start", spacing=None, cls=None):
    """Escaped text node."""
    extra = f' letter-spacing="{spacing}"' if spacing else ""
    extra += f' class="{cls}"' if cls else ""
    return (f'<text x="{x:g}" y="{y:g}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}"{extra}>{escape(str(value))}</text>')


def wrap(value, size, width):
    """Wrap text to a pixel width using the width estimate."""
    chars = max(8, int(width / (size * .5)))
    return textwrap.wrap(str(value), chars)


def svg(width, height, label, body, p, css="", component="kit"):
    """Wrap a component with gradients, fonts, motion CSS and an accessible label."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:g}" height="{height:g}" '
            f'viewBox="0 0 {width:g} {height:g}" role="img" aria-label="{escape(label, quote=True)}" '
            f'data-readme-component="{component}"><title>{escape(label)}</title><defs>'
            f'<linearGradient id="kb" x2="1" y2="0"><stop stop-color="{p["a"]}"/>'
            f'<stop offset=".55" stop-color="{p["m"]}"/><stop offset="1" stop-color="{p["b"]}"/></linearGradient>'
            f'<linearGradient id="kbd" x2="1" y2="1"><stop stop-color="{p["a"]}"/>'
            f'<stop offset=".55" stop-color="{p["m"]}"/><stop offset="1" stop-color="{p["b"]}"/></linearGradient>'
            f'</defs><style>text{{{FONT}}}{css}{REDUCED}</style>{body}</svg>\n')


def icon_at(name, x, y, size, color):
    """Place a 24-unit icon at a pixel size."""
    return glyph(name, color, f"translate({x:g} {y:g}) scale({size / 24:g})")


# ---------------------------------------------------------------- buttons

def button(label, symbol=None, variant="primary", mode="dark", theme="nebula", trailing=False, small=False):
    """A pill button. Primary buttons carry a slow sheen; outline buttons stay still."""
    p = colors(theme, mode)
    h, size, pad = (34, 13, 12) if small else (44, 15, 18)
    isize = 15 if small else 18
    w = pad + (isize + 9 if symbol else 0) + width_of(label, size, 600) + (9 + isize - 2 if trailing else 0) + pad
    w = round(w)
    primary = variant == "primary"
    ink = "#ffffff" if primary else p["fg"]
    iconc = "#ffffff" if primary else p["accent"]
    body = '<clipPath id="pill"><rect width="%d" height="%d" rx="%g"/></clipPath>' % (w, h, h / 2)
    if primary:
        body += f'<rect width="{w}" height="{h}" rx="{h / 2:g}" fill="url(#kb)"/>'
        body += (f'<g clip-path="url(#pill)"><rect class="sheen" x="-70" y="-10" width="46" height="{h + 20}" '
                 f'fill="#ffffff" opacity=".22" transform="skewX(-20)"/></g>')
        body += f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="{(h - 1) / 2:g}" fill="none" stroke="#ffffff" stroke-opacity=".18"/>'
    else:
        body += f'<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="{(h - 1.5) / 2:g}" fill="{p["panel"]}" stroke="{p["line"]}" stroke-width="1.5"/>'
        body += f'<path d="M{h / 2:g} {h - .75:g}h{w - h:g}" stroke="url(#kb)" stroke-width="1.5" opacity=".7"/>'
    x = pad
    if symbol:
        body += icon_at(symbol, x, (h - isize) / 2, isize, iconc)
        x += isize + 9
    body += t(x, h / 2 + size * .36, label, size, ink, 600)
    if trailing:
        ax = w - pad - isize + 2
        body += icon_at("lucide-arrow-right", ax, (h - isize + 2) / 2, isize - 2, iconc)
    css = (f".sheen{{animation:sheen 7s ease-in-out infinite}}"
           f"@keyframes sheen{{0%,72%{{transform:translateX(0) skewX(-20deg)}}100%{{transform:translateX({w + 140}px) skewX(-20deg)}}}}") if primary else ""
    return svg(w, h, label, body, p, css, "button"), w, h


# ---------------------------------------------------------------- stats

def stats(items, mode="dark", theme="nebula"):
    """A strip of declared facts: big gradient value, short label. Not live data."""
    p = colors(theme, mode)
    n, gap, W, H = len(items), 14, 1200, 144
    cell = (W - gap * (n - 1)) / n
    body = ""
    for i, item in enumerate(items):
        x = i * (cell + gap)
        body += f'<rect x="{x + .75:g}" y=".75" width="{cell - 1.5:g}" height="{H - 1.5}" rx="18" fill="{p["panel"]}" stroke="{p["line"]}" stroke-width="1.5"/>'
        body += f'<rect x="{x + 22:g}" y="0" width="{cell - 44:g}" height="3" rx="1.5" fill="url(#kb)"/>'
        body += f'<rect class="glint" style="animation-delay:{i * .9:g}s" x="{x + 22:g}" y="0" width="34" height="3" rx="1.5" fill="#ffffff" opacity="0"/>'
        vsize = 42
        while width_of(item["value"], vsize, 800) > cell - 36 and vsize > 20:
            vsize -= 2
        body += t(x + cell / 2, 66, item["value"], vsize, "url(#kb)", 800, "middle", "-1")
        for j, line in enumerate(wrap(item["label"], 16, cell - 26)[:2]):
            body += t(x + cell / 2, 98 + j * 20, line, 16, p["muted"], 500, "middle")
    css = (f".glint{{animation:glint 9s ease-in-out infinite}}"
           f"@keyframes glint{{0%,80%{{opacity:0;transform:translateX(0)}}85%{{opacity:.85}}100%{{opacity:0;transform:translateX({cell - 80:g}px)}}}}")
    label = " · ".join(f'{i["value"]} {i["label"]}' for i in items)
    return svg(W, H, label, body, p, css, "stats")


# ---------------------------------------------------------------- divider

def wave(theme="nebula"):
    """A flowing two-line wave that fades at both ends; reads on light and dark."""
    a, m, b = KIT_THEMES[theme]
    W, H = 1200, 44

    def path(period, amp, y):
        d = f"M{-period} {y}"
        x = -period
        while x < W + period:
            d += f" q{period / 4:g} {-amp} {period / 2:g} 0 t{period / 2:g} 0"
            x += period
        return d
    body = ('<defs><linearGradient id="fade" x2="1"><stop stop-color="#fff" stop-opacity="0"/>'
            '<stop offset=".2" stop-color="#fff"/><stop offset=".8" stop-color="#fff"/>'
            '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<mask id="edge"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask></defs>')
    body += '<g mask="url(#edge)">'
    body += f'<path class="w1" d="{path(160, 9, 22)}" fill="none" stroke="url(#kb)" stroke-width="2" stroke-linecap="round" opacity=".75"/>'
    body += f'<path class="w2" d="{path(240, 6, 22)}" fill="none" stroke="url(#kb)" stroke-width="1.2" opacity=".35"/>'
    body += '</g>'
    body += f'<rect x="{W / 2 - 7:g}" y="{H / 2 - 7:g}" width="14" height="14" rx="3" transform="rotate(45 {W / 2:g} {H / 2:g})" fill="{m}"/>'
    body += f'<circle class="pulse" cx="{W / 2:g}" cy="{H / 2:g}" r="12" fill="none" stroke="{b}" stroke-width="1.2"/>'
    css = (".w1{animation:flow 9s linear infinite}.w2{animation:flow2 14s linear infinite}"
           "@keyframes flow{to{transform:translateX(160px)}}@keyframes flow2{to{transform:translateX(-240px)}}"
           f".pulse{{transform-origin:{W / 2:g}px {H / 2:g}px;animation:pulse 4s ease-out infinite}}"
           "@keyframes pulse{0%{opacity:.7;transform:scale(.6)}70%,100%{opacity:0;transform:scale(1.6)}}")
    return svg(W, H, "Section divider", body, dict(a=a, m=m, b=b), css, "divider")


# ---------------------------------------------------------------- heading

def heading(number, kicker, title, symbol="layers", mode="dark", theme="nebula"):
    """Section opener: numbered tile, small kicker, title, and a line with a travelling light."""
    p = colors(theme, mode)
    W, H = 1200, 112
    body = f'<rect x="1" y="16" width="70" height="70" rx="20" fill="{p["panel"]}" stroke="url(#kbd)" stroke-width="2"/>'
    body += icon_at(symbol, 22, 37, 28, p["accent"])
    body += t(96, 42, f"{number} — {kicker}".upper(), 12.5, p["accent"], 700, spacing="2.4")
    size = 32
    while width_of(title, size, 750) > 800 and size > 20:
        size -= 2
    body += t(95, 80, title, size, p["fg"], 750, spacing="-.6")
    body += f'<path d="M95 {H - 6}H{W - 2}" stroke="{p["line"]}" stroke-width="1.5"/>'
    body += f'<path d="M95 {H - 6}h140" stroke="url(#kb)" stroke-width="2.5" stroke-linecap="round"/>'
    body += f'<circle class="run" cx="95" cy="{H - 6}" r="3.5" fill="{p["b"]}"/>'
    body += f'<circle cx="{W - 6}" cy="{H - 6}" r="4" fill="{p["panel"]}" stroke="{p["muted"]}" stroke-width="1.5"/>'
    css = (f".run{{animation:run 7s cubic-bezier(.6,0,.4,1) infinite}}"
           f"@keyframes run{{0%{{transform:translateX(0);opacity:0}}10%,85%{{opacity:1}}100%{{transform:translateX({W - 107}px);opacity:0}}}}")
    return svg(W, H, f"{number} {kicker}: {title}", body, p, css, "heading")


# ---------------------------------------------------------------- cards

def card(title, text, tags=(), symbol="layers", mode="dark", theme="nebula", kicker=None, badge=None):
    """A project card meant to be wrapped in a link; transparent 8px outer margin."""
    p = colors(theme, mode)
    W, H, m = 600, 282, 8
    cw, ch = W - 2 * m, H - 2 * m
    body = f'<g transform="translate({m} {m})">'
    body += f'<rect x=".75" y=".75" width="{cw - 1.5}" height="{ch - 1.5}" rx="20" fill="{p["panel"]}" stroke="{p["line"]}" stroke-width="1.5"/>'
    body += f'<path d="M28 .75h150" stroke="url(#kb)" stroke-width="3" stroke-linecap="round"/>'
    body += f'<rect x="26" y="28" width="54" height="54" rx="16" fill="url(#kbd)" opacity=".16"/>'
    body += f'<rect x="26.75" y="28.75" width="52.5" height="52.5" rx="15.5" fill="none" stroke="url(#kbd)" stroke-opacity=".55"/>'
    body += icon_at(symbol, 40, 42, 26, p["accent"])
    size = 23
    while width_of(title, size, 750) > cw - 200 and size > 16:
        size -= 1
    body += t(98, 54, title, size, p["fg"], 750, spacing="-.3")
    if kicker:
        body += t(99, 77, kicker.upper(), 12.5, p["muted"], 650, spacing="1.6")
    # corner arrow, rotated to point up-right
    body += f'<g transform="rotate(-45 {cw - 38} 46)">' + icon_at("lucide-arrow-right", cw - 49, 35, 22, p["muted"]) + '</g>'
    if badge:
        bw = width_of(badge, 11, 700) + 34
        bx = cw - 70 - bw
        body += f'<rect x="{bx:g}" y="33" width="{bw:g}" height="24" rx="12" fill="{p["panel2"]}" stroke="{p["line"]}"/>'
        body += f'<circle class="live" cx="{bx + 13:g}" cy="45" r="4" fill="#22c55e"/>'
        body += t(bx + 23, 49, badge.upper(), 11, p["fg"], 700, spacing="1.2")
    lines = wrap(text, 17, cw - 52)
    if len(lines) > 4:
        raise ValueError(f"card text for {title!r} needs {len(lines)} lines; keep it to four")
    for j, line in enumerate(lines):
        body += t(28, 116 + j * 24, line, 17, p["muted"], 400)
    x = 28
    for tag in tags:
        tw = width_of(tag, 13.5, 600) + 24
        if x + tw > cw - 28:
            break
        body += f'<rect x="{x:g}" y="{ch - 50}" width="{tw:g}" height="28" rx="8" fill="{p["panel2"]}" stroke="{p["line"]}"/>'
        body += t(x + tw / 2, ch - 31.5, tag, 13.5, p["fg"], 600, "middle")
        x += tw + 8
    body += '</g>'
    css = (".live{animation:live 2.4s ease-in-out infinite}"
           "@keyframes live{0%,100%{opacity:1}50%{opacity:.25}}")
    return svg(W, H, f"{title}: {text}", body, p, css, "card")


# ---------------------------------------------------------------- bento

def bento(cells, mode="dark", theme="nebula", columns=3):
    """A bento grid: cells span 1..columns; rows fill left to right."""
    p = colors(theme, mode)
    W, gap, rh = 1200, 14, 196
    unit = (W - gap * (columns - 1)) / columns
    rows, row, used = [], [], 0
    for cell in cells:
        span = min(columns, int(cell.get("span", 1)))
        if used + span > columns:
            rows.append(row)
            row, used = [], 0
        row.append((cell, span))
        used += span
    if row:
        rows.append(row)
    body = ""
    for r, items in enumerate(rows):
        x = 0.0
        y = r * (rh + gap)
        for k, (cell, span) in enumerate(items):
            w = unit * span + gap * (span - 1)
            feature = span > 1
            body += f'<rect x="{x + .75:g}" y="{y + .75:g}" width="{w - 1.5:g}" height="{rh - 1.5}" rx="20" fill="{p["panel"]}" stroke="{p["line"]}" stroke-width="1.5"/>'
            if feature:
                body += f'<circle class="orb" style="animation-delay:{r * 1.3:g}s" cx="{x + w - 64:g}" cy="{y + 48:g}" r="26" fill="url(#kbd)" opacity=".12"/>'
            body += f'<rect x="{x + 24:g}" y="{y + 24:g}" width="40" height="40" rx="12" fill="url(#kbd)" opacity=".15"/>'
            body += icon_at(cell.get("icon", "layers"), x + 33, y + 33, 22, p["accent"])
            if cell.get("kicker"):
                body += t(x + 78, y + 49, cell["kicker"].upper(), 13, p["accent"], 700, spacing="1.8")
            body += t(x + 24, y + 100, cell["title"], 23, p["fg"], 700)
            lines = wrap(cell.get("text", ""), 17, w - 44)
            if len(lines) > 3:
                raise ValueError(f"bento text for {cell['title']!r} needs {len(lines)} lines; keep it to three")
            for j, line in enumerate(lines):
                body += t(x + 24, y + 130 + j * 22, line, 17, p["muted"])
            x += w + gap
    H = len(rows) * rh + (len(rows) - 1) * gap
    css = ".orb{animation:orb 10s ease-in-out infinite}@keyframes orb{0%,100%{opacity:.08}50%{opacity:.22}}"
    label = " · ".join(f'{c["title"]}: {c.get("text", "")}' for c in cells)
    return svg(W, H, label, body, p, css, "bento")


# ---------------------------------------------------------------- panels

def panels(groups, mode="dark", theme="nebula", columns=3, style="chips"):
    """Grouped panels listing chips or lines, e.g. a tech stack or a toolbox."""
    p = colors(theme, mode)
    W, gap = 1200, 14
    columns = min(columns, len(groups))
    pw = (W - gap * (columns - 1)) / columns
    layouts = []
    for g in groups:
        parts, x, y = [], 24.0, 78.0
        if style == "chips":
            for item in g["items"]:
                cw = width_of(item, 14, 600) + 22
                if x + cw > pw - 24:
                    x, y = 24.0, y + 38
                parts.append((x, y, cw, item))
                x += cw + 8
            height = y + 30 + 24
        else:
            for item in g["items"]:
                for j, line in enumerate(wrap(item, 16.5, pw - 64)):
                    parts.append((44 if j == 0 else 44, y, j == 0, line))
                    y += 24
                y += 7
            height = y + 12
        layouts.append((g, parts, height))
    rows = [layouts[i:i + columns] for i in range(0, len(layouts), columns)]
    body, top = "", 0.0
    for row in rows:
        rh = max(h for _, _, h in row)
        for c, (g, parts, _) in enumerate(row):
            x0 = c * (pw + gap)
            body += f'<g transform="translate({x0:g} {top:g})">'
            body += f'<rect x=".75" y=".75" width="{pw - 1.5:g}" height="{rh - 1.5:g}" rx="18" fill="{p["panel"]}" stroke="{p["line"]}" stroke-width="1.5"/>'
            body += f'<path d="M24 .75h90" stroke="url(#kb)" stroke-width="3" stroke-linecap="round"/>'
            body += icon_at(g.get("icon", "layers"), 24, 24, 22, p["accent"])
            body += t(56, 42, g["title"], 19, p["fg"], 700)
            body += f'<path d="M24 58H{pw - 24:g}" stroke="{p["line"]}"/>'
            for part in parts:
                if style == "chips":
                    x, y, cw, item = part
                    body += f'<rect x="{x:g}" y="{y - 4:g}" width="{cw:g}" height="30" rx="9" fill="{p["panel2"]}" stroke="{p["line"]}"/>'
                    body += t(x + cw / 2, y + 16, item, 14, p["fg"], 600, "middle")
                else:
                    x, y, first, line = part
                    if first:
                        body += f'<rect x="26" y="{y - 9:g}" width="7" height="7" rx="2" transform="rotate(45 29.5 {y - 5.5:g})" fill="url(#kbd)"/>'
                    body += t(x, y, line, 16.5, p["fg"] if first else p["muted"], 500 if first else 400)
            body += '</g>'
        top += rh + gap
    H = top - gap
    label = " · ".join(g["title"] + ": " + ", ".join(g["items"]) for g in groups)
    return svg(W, H, label, body, p, "", "panels")


# ---------------------------------------------------------------- markup

def picture(base, alt, width=None, height=None):
    """GitHub-compatible light/dark picture with explicit size."""
    size = (f' width="{width}"' if width else "") + (f' height="{height}"' if height else "")
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="{escape(base, quote=True)}-dark.svg" />'
            f'<img src="{escape(base, quote=True)}-light.svg" alt="{escape(alt, quote=True)}"{size} /></picture>')


def linked(href, inner):
    return f'<a href="{escape(href, quote=True)}">{inner}</a>'
