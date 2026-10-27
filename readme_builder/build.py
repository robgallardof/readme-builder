"""Manifest-driven README generation with explicit ownership and path boundaries."""

from html import escape
import base64
from urllib.parse import urlsplit
import hashlib
import json
from pathlib import Path
import re
import tempfile
import os

from . import svg
from .motion import animate_svg, validate_svg, PRESETS
from .icons import PATHS, icon
from .markdown import migrate, slug
from .markdown import EMOJI

MANIFEST = ".readme-builder-manifest.json"


def local(root, name):
    """Resolve a relative output path without crossing symlink/root boundaries."""
    path = Path(name)
    if path.is_absolute() or ".." in path.parts or "\\" in name or ":" in name:
        raise ValueError(f"unsafe relative path: {name}")
    root = Path(root).resolve()
    target = root / path
    if not target.resolve().is_relative_to(root):
        raise ValueError(f"path escapes output root: {name}")
    return target


def atomic_write(path, content):
    """Replace a text file atomically; preserve exact requested newlines."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        try:
            handle.write(content)
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def picture(base, alt):
    """Emit GitHub-compatible explicit light/dark selection."""
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="{base}-dark.svg" />'
            f'<img src="{base}-light.svg" alt="{escape(alt, quote=True)}" width="100%" /></picture>')


def bounded(value, name, maximum):
    """Fail on overflowing copy rather than clipping it silently."""
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ValueError(f"{name} must be nonempty text, at most {maximum} characters")
    if EMOJI.search(value):
        raise ValueError(f"{name}: use an SVG icon name instead of emoji")
    return value


def validate(config):
    """Validate the small JSON authoring contract before any files are written."""
    if config.get("version") != 1:
        raise ValueError("config version must be 1")
    bounded(config.get("name"), "name", 64)
    if config.get("theme", "aurora") not in svg.THEMES:
        raise ValueError("theme must be aurora, ember or ocean")
    if config.get("motion", "subtle") not in PRESETS:
        raise ValueError("motion must be off, subtle or ambient")
    if config.get("diagram_preference", "archify") not in ("archify", "svg", "mermaid"):
        raise ValueError("diagram_preference must be archify, svg or mermaid")
    branding = config.get("branding")
    if branding is not None:
        if not isinstance(branding, dict):
            raise ValueError("branding must be an object")
        bounded(branding.get("author"), "branding author", 64)
        if not isinstance(branding.get("logo"), str):
            raise ValueError("branding logo must name a local PNG or JPEG file")
        profile = urlsplit(branding.get("profile", ""))
        if profile.scheme != "https" or not profile.hostname or profile.username or profile.password:
            raise ValueError("branding profile must be a credential-free HTTPS URL")
    documents = config.get("documents")
    if not isinstance(documents, list) or not documents:
        raise ValueError("documents must be a nonempty list")
    outputs = set()
    languages = set()
    for doc in documents:
        output = doc.get("file", "README.md")
        if not re.fullmatch(r"README(?:\.[A-Za-z0-9_-]+)?\.md", output):
            raise ValueError("document file must be README.md or README.language.md")
        if output in outputs:
            raise ValueError("duplicate document output")
        outputs.add(output)
        bounded(doc.get("tagline"), "tagline", 140)
        if not re.fullmatch(r"[a-z0-9-]{1,16}", doc.get("language", "en")):
            raise ValueError("language must be a short lowercase identifier")
        if doc.get("language", "en") in languages:
            raise ValueError("document languages must be distinct")
        languages.add(doc.get("language", "en"))
        bounded(doc.get("eyebrow", "OPEN SOURCE / BUILT WITH INTENT"), "eyebrow", 65)
        for item in doc.get("features", []):
            bounded(item.get("title"), "feature title", 24)
            bounded(item.get("text"), "feature text", 140)
            if item.get("icon", "spark") not in PATHS:
                raise ValueError("unknown feature icon")
        if len(doc.get("features", [])) > 6:
            raise ValueError("at most six features")
        for item in doc.get("metrics", []):
            bounded(item.get("value"), "metric value", 14)
            bounded(item.get("label"), "metric label", 28)
        if len(doc.get("metrics", [])) > 4:
            raise ValueError("at most four metrics")
        for step in doc.get("pipeline", []):
            bounded(step, "pipeline step", 28)
        if len(doc.get("pipeline", [])) > 6:
            raise ValueError("at most six pipeline steps")
        transcript = doc.get("terminal", {})
        for line in transcript.get("lines", []):
            if not isinstance(line, str) or len(line) > 110:
                raise ValueError("terminal lines must be text at most 110 characters")
        if len(transcript.get("lines", [])) > 14:
            raise ValueError("at most fourteen terminal lines")
        bounded(transcript.get("title", "quickstart"), "terminal title", 64)
        ids = set()
        for section in doc.get("sections", []):
            bounded(section.get("title"), "section title", 90)
            identifier = section.get("id", slug(section["title"]))
            if not re.fullmatch(r"[\w-]+", identifier) or identifier in ids:
                raise ValueError("section IDs must be distinct word/hyphen identifiers")
            ids.add(identifier)
            if section.get("stage") not in (None, "overview", "start", "use", "advanced", "contribute", "license"):
                raise ValueError("unknown section stage")
            diagram = section.get("diagram")
            if diagram is not None:
                if not isinstance(diagram, dict) or diagram.get("provider", "archify") not in ("archify", "svg"):
                    raise ValueError("diagram provider must be archify or svg")
                bounded(diagram.get("alt"), "diagram alternative", 180)
                if not all(isinstance(diagram.get(mode), str) for mode in ("light", "dark")):
                    raise ValueError("diagrams need local light and dark SVG paths")
            if section.get("icon", "layers") not in PATHS:
                raise ValueError("unknown section icon")


def render(config, source_root):
    """Compile authored JSON and content files to an in-memory output mapping."""
    validate(config)
    files = {}
    branding = config.get("branding")
    if branding:
        branding = dict(branding)
        logo = local(source_root, branding["logo"]).read_bytes()
        if len(logo) > 2_000_000:
            raise ValueError("branding logo is larger than 2 MB")
        mime = "image/png" if logo.startswith(b"\x89PNG\r\n\x1a\n") else "image/jpeg" if logo.startswith(b"\xff\xd8\xff") else None
        if mime is None:
            raise ValueError("branding logo must contain PNG or JPEG bytes")
        branding["logo_data"] = "data:" + mime + ";base64," + base64.b64encode(logo).decode("ascii")
    theme = config.get("theme", "aurora")
    files["assets/readme-builder/divider.svg"] = svg.divider(theme)
    for doc in config["documents"]:
        language = doc.get("language", "en")
        prefix = f"assets/readme-builder/{language}"
        parts = ['<a id="top"></a>', '<!-- Generated by readme-builder; edit the JSON/content source. -->',
                 picture(prefix + "/hero", config["name"] + " — " + doc["tagline"]),
                 '<p align="center"><strong>' + escape(doc["tagline"]) + '</strong></p>']
        sections = doc.get("sections", [])
        if sections and all(section.get("stage") for section in sections):
            stages = ("overview", "start", "use", "advanced", "contribute", "license")
            sections = sorted(sections, key=lambda section: stages.index(section["stage"]))
        if sections:
            parts.append('<p align="center">' + " · ".join(
                f'<a href="#{s.get("id", slug(s["title"]))}">{escape(s["title"])}</a>' for s in sections[:3]) + '</p>')
        if len(config["documents"]) > 1:
            parts.append('<p align="center">' + " · ".join(
                f'<a href="{d.get("file", "README.md")}">{escape(d.get("label", d.get("language", "en")))}</a>'
                for d in config["documents"]) + '</p>')
        for mode in ("light", "dark"):
            files[f"{prefix}/hero-{mode}.svg"] = svg.hero(config["name"], doc["tagline"], doc.get("eyebrow", "OPEN SOURCE / BUILT WITH INTENT"), theme, mode)
        for widget, renderer in [("features", svg.features), ("metrics", svg.metrics), ("pipeline", svg.pipeline)]:
            if doc.get(widget):
                for mode in ("light", "dark"):
                    files[f"{prefix}/{widget}-{mode}.svg"] = renderer(doc[widget], theme, mode)
                alt = " · ".join(doc[widget]) if widget == "pipeline" else " · ".join(
                    (i["title"] + ": " + i["text"]) if widget == "features" else (i["value"] + " " + i["label"])
                    for i in doc[widget])
                if widget == "features":
                    parts.append("\n".join("- **" + item["title"] + ".** " + item["text"] for item in doc[widget]))
                else:
                    parts.append(picture(f"{prefix}/{widget}", alt))
        if doc.get("terminal", {}).get("lines"):
            terminal = doc["terminal"]
            for mode in ("light", "dark"):
                files[f"{prefix}/terminal-{mode}.svg"] = svg.terminal(terminal["lines"], terminal.get("title", "quickstart"), theme, mode)
            parts.append(picture(f"{prefix}/terminal", " / ".join(terminal["lines"])))
        for index, section in enumerate(sections, 1):
            identifier = section.get("id", slug(section["title"]))
            # A real h2 preserves the document outline; its image has full text
            # alternative and the explicit anchor never depends on an emoji slug.
            for mode in ("light", "dark"):
                files[f"{prefix}/section-{index:02}-{mode}.svg"] = svg.section(section["title"], index, section.get("icon", "layers"), theme, mode)
            symbol = section.get("icon", "layers")
            files[f"assets/readme-builder/icons/{symbol}.svg"] = icon(symbol)
            parts.append(f'<a id="{identifier}"></a>\n\n## <img src="assets/readme-builder/icons/{symbol}.svg" width="24" height="24" alt="" /> ' + escape(section["title"]))
            if "source" in section:
                body = local(source_root, section["source"]).read_text(encoding="utf-8")
            else:
                body = section.get("body", "")
            body, icons = migrate(body)
            files.update(icons)
            parts.append(body.strip())
            if section.get("diagram"):
                diagram = section["diagram"]
                base = f"{prefix}/diagram-{index:02}"
                for mode in ("light", "dark"):
                    content = local(source_root, diagram[mode]).read_text(encoding="utf-8")
                    validate_svg(content)
                    files[f"{base}-{mode}.svg"] = content
                parts.append(picture(base, diagram["alt"]))
        for mode in ("light", "dark"):
            files[f"{prefix}/footer-{mode}.svg"] = svg.footer(config["name"], theme, mode, branding)
        parts.append('<p align="center"><a href="#top">' + ("Volver al inicio" if language == "es" else "Back to top") + '</a></p>')
        signature = picture(f"{prefix}/footer", config["name"])
        if branding:
            signature = signature.replace('width="100%"', 'width="360"')
        if branding:
            signature = f'<a href="{escape(branding["profile"], quote=True)}">{signature}</a>'
        parts.append('<!-- readme-builder:signature:start -->\n<p align="center">' + signature + '</p>\n<!-- readme-builder:signature:end -->')
        files[doc.get("file", "README.md")] = "\n\n".join(
            '<p align="center">' + part + '</p>' if part.startswith(("<picture>", "<img ")) else part
            for part in parts) + "\n"
    return {name: animate_svg(content, config.get("motion", "subtle")) if name.endswith(".svg") else content
            for name, content in files.items()}


def write_outputs(files, root, check=False, force=False):
    """Check all conflicts before writing; own only paths recorded in the manifest."""
    root = Path(root).resolve()
    manifest = local(root, MANIFEST)
    previous = json.loads(manifest.read_text(encoding="utf-8")) if manifest.exists() else {}
    changed = []
    for name, content in files.items():
        target = local(root, name)
        if target.exists():
            existing = target.read_bytes()
            if existing == content.encode():
                continue
            if not check and not force and previous.get(name) != hashlib.sha256(existing).hexdigest():
                raise ValueError(f"refusing to replace an unowned or edited file: {name}; use --force after review")
        changed.append(name)
    if check:
        return changed
    for name in changed:
        atomic_write(local(root, name), files[name])
    hashes = {name: hashlib.sha256(content.encode()).hexdigest() for name, content in files.items()}
    atomic_write(manifest, json.dumps(hashes, sort_keys=True, indent=2) + "\n")
    return changed
