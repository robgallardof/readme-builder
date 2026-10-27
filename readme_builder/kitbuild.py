"""Kit authoring: fill marked README blocks from a JSON spec, or upgrade plain README chrome.

``render``  reads a kit spec and regenerates every ``<!-- kit:ID -->`` block.
``upgrade`` turns centred link rows, for-the-badge navigation shields and
"back to top" links into kit buttons, and puts a wave divider between sections.
Both are deterministic and idempotent; fenced code is never touched.
"""

import re
import unicodedata
from html import escape, unescape
from pathlib import Path

from . import kit, svg as base_svg
from .build import atomic_write, local
from .icons import PATHS

TYPES = ("buttons", "stats", "divider", "heading", "cards", "bento", "panels", "terminal")
BACK = {"back to top", "volver al inicio", "volver arriba", "subir"}


def loc(value, lang):
    """Resolve {lang: text} values recursively; plain values pass through."""
    if isinstance(value, dict):
        if value and all(re.fullmatch(r"[a-z]{2}(?:-[a-z]{2})?", k) for k in value):
            return value.get(lang) or next(iter(value.values()))
        return {k: loc(v, lang) for k, v in value.items()}
    if isinstance(value, list):
        return [loc(v, lang) for v in value]
    return value


def slugify(value):
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "item"


def check_icon(name):
    if name is not None and name not in PATHS:
        raise ValueError(f"unknown icon: {name}")
    return name


def both(files, base, make):
    for mode in ("light", "dark"):
        files[f"{base}-{mode}.svg"] = make(mode)


def block(spec, lang, folder, theme, files):
    """Render one block to files; return its Markdown/HTML markup."""
    kind, ident = spec.get("type"), spec.get("id", "")
    if kind not in TYPES:
        raise ValueError(f"unknown kit block type: {kind}")
    if not re.fullmatch(r"[a-z0-9-]{1,48}", ident):
        raise ValueError("kit block ids are lowercase words and hyphens")
    spec = loc(spec, lang)
    stem = f"{folder}/{ident}-{lang}"
    full = lambda alt: '<p align="center">' + kit.picture(stem, alt, "100%") + "</p>"
    if kind == "divider":
        files[f"{folder}/wave.svg"] = kit.wave(theme)
        return f'<p align="center"><img src="{folder}/wave.svg" alt="" width="100%" /></p>'
    if kind == "buttons":
        parts = []
        for i, item in enumerate(spec["items"]):
            item_stem = f"{stem}-{i + 1:02}"
            label = item["label"]
            for mode in ("light", "dark"):
                content, _, h = kit.button(label, check_icon(item.get("icon")), item.get("variant", "outline"), mode,
                                           theme, item.get("trailing", False), item.get("small", False))
                files[f"{item_stem}-{mode}.svg"] = content
            parts.append(kit.linked(item["href"], kit.picture(item_stem, label, height=h)))
        return f'<p align="{spec.get("align", "center")}">' + "&nbsp;\n".join(parts) + "</p>"
    if kind == "stats":
        both(files, stem, lambda m: kit.stats(spec["items"], m, theme))
        return full(" · ".join(f'{i["value"]} {i["label"]}' for i in spec["items"]))
    if kind == "heading":
        both(files, stem, lambda m: kit.heading(spec["number"], spec["kicker"], spec["title"],
                                                 check_icon(spec.get("icon", "layers")), m, theme))
        return full(spec["title"])
    if kind == "bento":
        for cell in spec["cells"]:
            check_icon(cell.get("icon", "layers"))
        both(files, stem, lambda m: kit.bento(spec["cells"], m, theme, spec.get("columns", 3)))
        return full(" · ".join(f'{c["title"]}: {c.get("text", "")}' for c in spec["cells"]))
    if kind == "panels":
        for group in spec["groups"]:
            check_icon(group.get("icon", "layers"))
        both(files, stem, lambda m: kit.panels(spec["groups"], m, theme, spec.get("columns", 3), spec.get("style", "chips")))
        return full(" · ".join(g["title"] + ": " + ", ".join(g["items"]) for g in spec["groups"]))
    if kind == "terminal":
        both(files, stem, lambda m: base_svg.terminal(spec["lines"], spec.get("title", "terminal"), "aurora", m))
        return full(" / ".join(spec["lines"]))
    parts = []
    for i, item in enumerate(spec["items"]):
        item_stem = f"{stem}-{i + 1:02}"
        both(files, item_stem, lambda m: kit.card(item["title"], item["text"], item.get("tags", []),
                                                   check_icon(item.get("icon", "layers")), m, theme,
                                                   item.get("kicker"), item.get("badge")))
        parts.append(kit.linked(item["href"], kit.picture(item_stem, f'{item["title"]}: {item["text"]}', "49%")))
    return '<p align="center">' + "".join(parts) + "</p>"


def render(config, root):
    """Return {path: content} for assets and every document with filled blocks."""
    if config.get("version") != 1:
        raise ValueError("kit config version must be 1")
    theme = config.get("theme", "nebula")
    kit.colors(theme)
    folder = config.get("assets", "assets/kit").strip("/")
    local(root, folder)
    files = {}
    blocks = {b["id"]: b for b in config["blocks"]}
    for name, lang in config["documents"].items():
        path = local(root, name)
        text = path.read_text(encoding="utf-8")
        for ident, spec in blocks.items():
            pattern = re.compile(r"(<!-- kit:" + re.escape(ident) + r" -->)(.*?)(<!-- /kit:" + re.escape(ident) + r" -->)", re.S)
            if not pattern.search(text):
                continue
            markup = block(spec, lang, folder, theme, files)
            text = pattern.sub(lambda m: m[1] + "\n" + markup + "\n" + m[3], text)
        unknown = set(re.findall(r"<!-- kit:([a-z0-9-]+) -->", text)) - set(blocks)
        if unknown:
            raise ValueError(f"{name}: no kit block named {', '.join(sorted(unknown))}")
        files[name] = text
    return files


# ------------------------------------------------------------------ upgrade

LINK = re.compile(r'<a href="([^"]+)">([^<>]+)</a>')
ROW = re.compile(r'^\s*<p align="center">\s*((?:<a href="[^"]+">[^<>]+</a>\s*(?:·|&middot;|\|)?\s*)+)</p>\s*$')
SHIELD = re.compile(r'^(\s*)<a href="([^"]+)">\s*<img\b(?=[^>]*for-the-badge)[^>]*>\s*</a>\s*$')
ALT = re.compile(r'\balt="([^"]*)"')
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")


def upgrade(text, filename="README.md", folder="assets/readme-builder/kit", theme="nebula"):
    """Upgrade README chrome to kit components; returns (text, files)."""
    files = {}

    def button(label, href, variant="outline", symbol=None, trailing=False, small=True):
        stem = f"{folder}/btn-{slugify(label)}-{variant}{'-sm' if small else ''}"
        h = 0
        for mode in ("light", "dark"):
            content, _, h = kit.button(label, symbol, variant, mode, theme, trailing, small)
            files[f"{stem}-{mode}.svg"] = content
        return kit.linked(unescape(href), kit.picture(stem, label, height=h))

    def choose(label, href):
        label = unescape(label).strip()
        if href == "#top" or label.lower() in BACK:
            return button(label, href, symbol="arrow-up")
        if re.fullmatch(r"README(?:\.[\w-]+)?\.md", href):
            return button(label, href, "primary" if href == filename else "outline", "lucide-globe")
        if href.startswith(("http://", "https://")):
            return button(label, href, "primary", trailing=True, small=False)
        return button(label, href)

    out, fence, seen_h2 = [], None, False
    wave = f'<p align="center"><img src="{folder}/wave.svg" alt="" width="100%" /></p>'
    for line in text.split("\n"):
        marker = FENCE.match(line)
        if marker:
            fence = None if fence and line.strip().startswith(fence) else (fence or marker[1][:3])
            out.append(line)
            continue
        if fence:
            out.append(line)
            continue
        row = ROW.match(line)
        if row:
            links = LINK.findall(row[1])
            out.append('<p align="center">' + "&nbsp;\n".join(choose(label, href) for href, label in links) + "</p>")
            continue
        shield = SHIELD.match(line)
        if shield and ALT.search(line):
            out.append(shield[1] + choose(ALT.search(line)[1], shield[2]))
            continue
        if line.startswith("## "):
            if seen_h2:
                # Put the divider above an explicit anchor so links land on the wave.
                at = len(out)
                while at and not out[at - 1].strip():
                    at -= 1
                if at and re.fullmatch(r'<a (?:id|name)="[^"]+"></a>', out[at - 1].strip()):
                    at -= 1
                previous = [l for l in out[:at] if l.strip()]
                if not previous or "wave.svg" not in previous[-1]:
                    out[at:at] = [wave, ""]
            seen_h2 = True
        out.append(line)
    result = "\n".join(out)
    if "wave.svg" in result:
        files[f"{folder}/wave.svg"] = kit.wave(theme)
    return result, files


def upgrade_file(path, write=False, theme="nebula"):
    path = Path(path).resolve()
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    crlf = "\r\n" in text
    updated, files = upgrade(text.replace("\r\n", "\n"), path.name, theme=theme)
    if crlf:
        updated = updated.replace("\n", "\r\n")
    changed = updated != text
    if write:
        for name, content in files.items():
            atomic_write(local(path.parent, name), content)
        if changed:
            atomic_write(path, ("﻿" if bom else "") + updated)
    return changed, len(files)
