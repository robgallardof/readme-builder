"""Original 24px line icons; all paths are authored in this project, MIT licensed."""

from html import escape

PATHS = {
    "spark": '<path d="m12 3 2.4 6.6L21 12l-6.6 2.4L12 21l-2.4-6.6L3 12l6.6-2.4Z"/>',
    "link": '<path d="m9 15 6-6m-7 3-2 2a4 4 0 0 0 6 6l2-2m-4-12 2-2a4 4 0 0 1 6 6l-2 2"/>',
    "shield": '<path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6Z"/><path d="m8 12 3 3 5-6"/>',
    "box": '<path d="m12 3 9 5v9l-9 5-9-5V8Zm-9 5 9 5 9-5m-9 5v9M7.5 5.5l9 5"/>',
    "code": '<path d="m8 6-6 6 6 6m8-12 6 6-6 6M14 3l-4 18"/>',
    "branch": '<circle cx="6" cy="5" r="2"/><circle cx="6" cy="19" r="2"/><circle cx="18" cy="5" r="2"/><path d="M6 7v10m12-10v2a5 5 0 0 1-5 5H6"/>',
    "repeat": '<path d="M5 7h14l-4-4m4 4-4 4M19 17H5l4 4m-4-4 4-4"/>',
    "users": '<circle cx="9" cy="8" r="3"/><path d="M3 21v-3a6 6 0 0 1 12 0v3m1-17a4 4 0 0 1 0 8m3 9v-3a5 5 0 0 0-2-4"/>',
    "terminal": '<rect x="2" y="4" width="20" height="16" rx="3"/><path d="m6 9 3 3-3 3m6 0h5"/>',
    "rocket": '<path d="M13 4c4-2 8-1 8-1s1 4-1 8l-7 7-7-7Zm-7 7-3 1-1 5 6-1m5 2-1 4 5-1 1-6M6 18l-3 3"/><circle cx="16" cy="8" r="2"/>',
    "search": '<circle cx="10" cy="10" r="7"/><path d="m15 15 6 6"/>',
    "lock": '<rect x="4" y="10" width="16" height="12" rx="3"/><path d="M8 10V6a4 4 0 0 1 8 0v4m-4 5v3"/>',
    "chart": '<path d="M3 3v18h18M7 16v-4m5 4V8m5 8V5"/>',
    "check": '<circle cx="12" cy="12" r="9"/><path d="m7 12 3 3 7-7"/>',
    "close": '<circle cx="12" cy="12" r="9"/><path d="m8 8 8 8m0-8-8 8"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><ellipse cx="12" cy="12" rx="4" ry="10"/><path d="M2 12h20"/>',
    "layers": '<path d="m12 3 10 5-10 5L2 8Zm-10 9 10 5 10-5M2 16l10 5 10-5"/>',
    "cpu": '<rect x="6" y="6" width="12" height="12" rx="2"/><path d="M9 2v4m6-4v4M9 18v4m6-4v4M2 9h4m-4 6h4m12-6h4m-4 6h4M10 10h4v4h-4Z"/>',
    "file": '<path d="M14 2H5v20h14V7Zm0 0v5h5M8 12h8m-8 4h6"/>',
    "book": '<path d="M12 5C8 2 3 3 2 4v16c4-2 7-1 10 1 3-2 6-3 10-1V4c-1-1-6-2-10 1Zm0 0v16"/>',
    "arrow-up": '<path d="M12 21V3m-7 7 7-7 7 7"/>',
    "play": '<circle cx="12" cy="12" r="10"/><path d="m10 7 7 5-7 5Z"/>',
    "settings": '<circle cx="12" cy="12" r="4"/><path d="M12 2v3m0 14v3M2 12h3m14 0h3M5 5l2 2m10 10 2 2M5 19l2-2M17 7l2-2"/>',
    "palette": '<path d="M12 2a10 10 0 1 0 0 20h2a3 3 0 0 0 0-6h-1a2 2 0 0 1 0-4h4a5 5 0 0 0 5-5c-2-3-5-5-10-5Z"/><path d="M7 7h.01M5 12h.01M9 17h.01M13 6h.01"/>',
    "download": '<path d="M12 2v13m-5-5 5 5 5-5M3 16v5h18v-5"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "database": '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 4 18 4 18 0V5M3 12c0 4 18 4 18 0"/>',
    "heart": '<path d="M12 21 3 12C-3 4 8-2 12 6c4-8 15-2 9 6Z"/>',
    "bot": '<rect x="3" y="7" width="18" height="14" rx="4"/><path d="M12 2v5M8 12v2m8-2v2m-8 4h8M1 12v5m22-5v5"/>',
    "workflow": '<rect x="2" y="3" width="7" height="6" rx="2"/><rect x="15" y="15" width="7" height="6" rx="2"/><path d="M9 6h6a4 4 0 0 1 4 4v5M5 9v9h10"/>',
    "flag": '<path d="M5 22V3c5-5 9 5 15 0v12c-6 5-10-5-15 0"/>',
    "bolt": '<path d="m14 2-11 12h8l-1 8 11-13h-8Z"/>',
}


def glyph(name: str, color: str = "#8b5cf6", transform: str = "") -> str:
    """Render a trusted icon name inside an SVG group."""
    if name not in PATHS:
        raise ValueError(f"unknown icon: {name}")
    return (f'<g transform="{escape(transform, quote=True)}" fill="none" '
            f'stroke="{escape(color, quote=True)}" stroke-width="1.7" '
            f'stroke-linecap="round" stroke-linejoin="round">{PATHS[name]}</g>')


def icon(name: str, color: str = "#8b5cf6") -> str:
    """Return a complete, accessible, self-contained icon."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
            f'width="24" height="24" role="img" aria-label="{escape(name)}">'
            f'<title>{escape(name)}</title>{glyph(name, color)}</svg>\n')
