"""Portable CLI: generate, inspect, migrate and preview without network access."""

import argparse
from html import escape
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

from . import __version__
from .motion import animate_svg, validate_svg, PRESETS
from .build import atomic_write, local, render, write_outputs
from .icons import PATHS, icon
from .kit import KIT_THEMES
from .kitbuild import render as kit_render_files, upgrade_file
from .markdown import EMOJI, SHORTCODE, migrate, slug

EXCLUDED = {".git", "node_modules", "target", ".venv", "vendor", "dist", "build"}


def readmes(root):
    """Discover repository-owned README Markdown files without following symlinks."""
    root = Path(root).resolve()
    git = subprocess.run(["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                         capture_output=True, check=False)
    candidates = [root / s for s in git.stdout.decode("utf-8").split("\0") if s] if git.returncode == 0 else root.rglob("*")
    return sorted(p for p in candidates if p.is_file() and p.name.lower().startswith("readme")
                  and p.suffix.lower() == ".md" and not p.is_symlink()
                  and not (set(p.relative_to(root).parts) & EXCLUDED) and p.resolve().is_relative_to(root))


def visible_lines(source):
    """Yield non-fenced lines; literal code examples are not presentation defects."""
    fence, length = None, 0
    for number, line in enumerate(source.splitlines(), 1):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)", line)
        if marker:
            if fence is None:
                fence, length = marker[1][0], len(marker[1])
            elif marker[1][0] == fence and len(marker[1]) >= length and not marker[2].strip():
                fence = None
            continue
        if fence is None:
            yield number, line


def inspect(root):
    """Find presentation issues and broken local README references."""
    root = Path(root).resolve()
    issues = []
    for path in readmes(root):
        name = path.relative_to(root).as_posix()
        source = path.read_text(encoding="utf-8-sig")
        if "<!-- readme-builder:signature:end -->" in source:
            tail = source.split("<!-- readme-builder:signature:end -->", 1)[1].strip()
            if tail:
                issues.append(dict(file=name, line=0, kind="footer-order", message="content appears after the signature"))
        rows = list(visible_lines(source))
        ids = set(re.findall(r'<a\s+(?:id|name)=["\x27]([^"\x27]+)', source))
        ids.update(slug(m[1]) for _, line in rows if (m := re.match(r"^#{1,6} (.+)", line)))
        for number, line in rows:
            outside_code = re.sub(r"`[^`]*`", "", line)
            if EMOJI.search(outside_code) or SHORTCODE.search(outside_code):
                issues.append(dict(file=name, line=number, kind="emoji", message="decorative emoji; migrate to SVG"))
            if re.match(r"^(<<<<<<<|=======|>>>>>>>)", line):
                issues.append(dict(file=name, line=number, kind="conflict", message="unresolved merge marker"))
            references = re.findall(r'(?:src|srcset|href)=["\x27]([^"\x27]+)', line)
            references += re.findall(r"\]\(([^\s)]+)\)", line)
            for reference in references:
                decoded = unquote(reference)
                parsed = urlsplit(decoded)
                if parsed.scheme or parsed.netloc:
                    continue
                if not parsed.path:
                    if parsed.fragment and parsed.fragment not in ids:
                        issues.append(dict(file=name, line=number, kind="anchor", message=reference))
                    continue
                target = (path.parent / parsed.path).resolve()
                if not target.is_relative_to(root) or not target.exists():
                    issues.append(dict(file=name, line=number, kind="local-link", message=reference))
    asset_dir = root / "assets" / "readme-builder"
    if asset_dir.exists():
        for path in asset_dir.rglob("*.svg"):
            if not path.resolve().is_relative_to(root):
                issues.append(dict(file=str(path), line=0, kind="svg", message="asset escapes repository"))
                continue
            try:
                validate_svg(path.read_text(encoding="utf-8"))
            except (ET.ParseError, ValueError) as error:
                issues.append(dict(file=path.relative_to(root).as_posix(), line=0, kind="svg", message=str(error)))
    return issues


def migrate_file(path, write=False):
    """Dry-run by default; only presentation edits and new local icons are written."""
    path = Path(path).resolve()
    original = path.read_bytes()
    bom = original.startswith(b"\xef\xbb\xbf")
    text = original.decode("utf-8-sig")
    updated, files = migrate(text)
    if write and updated != text:
        # Preflight icon collisions before mutating the README.
        for name, content in files.items():
            target = local(path.parent, name)
            if target.exists() and target.read_bytes() != content.encode():
                raise ValueError(f"icon collision: {name}")
        if path.read_bytes() != original:
            raise ValueError(f"file changed during migration: {path}")
        for name, content in files.items():
            atomic_write(local(path.parent, name), content)
        atomic_write(path, ("\ufeff" if bom else "") + updated)
    return updated != text, len(files)


def preview(root, output):
    """Create a local component contact sheet, not a GitHub HTML emulator."""
    root, output = Path(root).resolve(), Path(output).resolve()
    items = []
    import os
    for asset in sorted((root / "assets" / "readme-builder").rglob("*.svg")):
        relative = Path(os.path.relpath(asset, output.parent)).as_posix()
        items.append(f'<figure><figcaption>{escape(asset.relative_to(root).as_posix())}</figcaption><img src="{escape(relative, quote=True)}" alt="{escape(asset.stem)}" /></figure>')
    atomic_write(output, '<!doctype html><html lang="en"><meta charset="utf-8"><title>Readme Builder / components</title>'
                 '<style>body{background:#080c17;color:#cbd5e1;font:14px system-ui;margin:32px auto;max-width:1200px}figure{margin:24px 0;padding:20px;border:1px solid #25304a;border-radius:16px}img{max-width:100%;height:auto}figcaption{margin-bottom:16px}figure:has(img[src*="icons/"]) img{width:48px}</style>'
                 '<h1>Component proof sheet</h1><p>Local SVGs, both colour modes. View the README on GitHub for its final Markdown layout.</p>' + "".join(items) + '</html>')


def main(argv=None):
    """Execute one explicit, local authoring command."""
    parser = argparse.ArgumentParser(prog="readme-builder", description="Offline README design system / original SVGs")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="compile an authored JSON config")
    build.add_argument("config", type=Path)
    build.add_argument("--output", type=Path, default=Path("."))
    build.add_argument("--check", action="store_true", help="report output drift without writing")
    build.add_argument("--force", action="store_true", help="replace edited/unowned output after review")
    migration = commands.add_parser("migrate", help="replace decorative emoji in a README; dry-run by default")
    migration.add_argument("files", nargs="+", type=Path)
    migration.add_argument("--write", action="store_true")
    for command in ("audit", "check"):
        audit = commands.add_parser(command, help="inspect README presentation and local references")
        audit.add_argument("roots", nargs="+", type=Path)
        audit.add_argument("--json", action="store_true")
    gallery = commands.add_parser("preview", help="write a local SVG contact sheet")
    gallery.add_argument("root", type=Path)
    gallery.add_argument("--output", type=Path, default=Path("preview.html"))
    animation = commands.add_parser("animate", help="animate local SVG assets; dry-run by default")
    animation.add_argument("files", nargs="+", type=Path)
    animation.add_argument("--preset", choices=PRESETS, default="subtle")
    animation.add_argument("--write", action="store_true")
    kitting = commands.add_parser("kit", help="showcase kit: buttons, stats, waves, headings, cards, bento, panels")
    kit_commands = kitting.add_subparsers(dest="kit_command", required=True)
    kit_render = kit_commands.add_parser("render", help="fill <!-- kit:ID --> blocks from a kit JSON spec")
    kit_render.add_argument("config", type=Path)
    kit_render.add_argument("--check", action="store_true", help="report drift without writing")
    kit_upgrade = kit_commands.add_parser("upgrade", help="turn link rows, nav shields and back-to-top into kit buttons; add wave dividers")
    kit_upgrade.add_argument("files", nargs="+", type=Path)
    kit_upgrade.add_argument("--theme", default="nebula", choices=sorted(KIT_THEMES))
    kit_upgrade.add_argument("--write", action="store_true")
    commands.add_parser("icons", help="list available original icons")
    args = parser.parse_args(argv)
    try:
        if args.command == "animate":
            changes = []
            for path in args.files:
                if path.suffix.lower() != ".svg" or any(p.is_symlink() for p in (path, *path.parents)):
                    raise ValueError(f"expected a regular local SVG path: {path}")
                source = path.read_bytes().decode("utf-8")
                result = animate_svg(source, args.preset)
                if result != source:
                    changes.append((path, source, result))
            if args.write and any(path.read_bytes().decode("utf-8") != source for path, source, _ in changes):
                raise ValueError("SVG changed while planning; nothing was written")
            for path, source, result in changes:
                if args.write:
                    atomic_write(path, result)
                print(f"{path}: {args.preset}; {'updated' if args.write else 'dry-run'}")
            return 0
        if args.command == "kit":
            if args.kit_command == "render":
                root = args.config.parent.resolve()
                files = kit_render_files(json.loads(args.config.read_text(encoding="utf-8-sig")), root)
                changed = [name for name, content in files.items()
                           if not local(root, name).exists() or local(root, name).read_bytes() != content.encode()]
                if not args.check:
                    for name in changed:
                        atomic_write(local(root, name), files[name])
                print(json.dumps({"changed": changed, "files": len(files), "check": args.check}, indent=2))
                return int(args.check and bool(changed))
            for path in args.files:
                changed, count = upgrade_file(path, args.write, args.theme)
                print(f'{path}: {"updated" if args.write else "dry-run"}; changed={changed}; assets={count}')
            return 0
        if args.command == "build":
            config = json.loads(args.config.read_text(encoding="utf-8-sig"))
            files = render(config, args.config.parent)
            changed = write_outputs(files, args.output, args.check, args.force)
            print(json.dumps({"changed": changed, "files": len(files), "check": args.check}, indent=2))
            return int(args.check and bool(changed))
        if args.command == "migrate":
            for path in args.files:
                changed, count = migrate_file(path, args.write)
                print(f'{path}: {"updated" if args.write else "dry-run"}; changed={changed}; icons={count}')
            return 0
        if args.command in ("audit", "check"):
            report = [{"root": str(root), "readmes": len(readmes(root)), "issues": inspect(root)} for root in args.roots]
            print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else "\n".join(
                f'{item["root"]}: {item["readmes"]} READMEs, {len(item["issues"])} findings\n' + "\n".join(
                    f'  {issue["file"]}:{issue["line"]} {issue["kind"]}: {issue["message"]}' for issue in item["issues"]) for item in report))
            return int(args.command == "check" and any(item["issues"] for item in report))
        if args.command == "preview":
            preview(args.root, args.output)
            print(args.output.resolve())
        if args.command == "icons":
            print("\n".join(PATHS))
        return 0
    except (ValueError, OSError, KeyError, TypeError, ET.ParseError) as error:
        print(f"readme-builder: {error}", file=sys.stderr)
        return 2
