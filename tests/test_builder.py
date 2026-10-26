"""Behaviour tests: real files and CLI processes, not mocks of the filesystem."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

from readme_builder.build import local, render, write_outputs
from readme_builder.cli import inspect, migrate_file
from readme_builder.icons import PATHS, icon
from readme_builder.markdown import migrate

ROOT = Path(__file__).resolve().parents[1]


def configuration():
    return {"version": 1, "name": "Demo & <test>", "theme": "aurora", "documents": [{
        "file": "README.md", "language": "en", "tagline": "Authored copy, portable assets.",
        "features": [{"title": "Local", "text": "No remote rendering.", "icon": "shield"}],
        "metrics": [{"value": "0", "label": "runtime dependencies"}],
        "pipeline": ["Author", "Build", "Review"],
        "terminal": {"lines": ["$ echo '<script>'", "example, not measured output"]},
        "sections": [{"title": "Start", "id": "start", "icon": "rocket", "body": "Run `python --version`."}]}]}


class BuilderTests(unittest.TestCase):
    def test_all_themes_and_components_are_valid_escaped_svg(self):
        from readme_builder.svg import THEMES
        for theme in THEMES:
            config = configuration()
            config["theme"] = theme
            files = render(config, ROOT)
            for name, content in files.items():
                if name.endswith(".svg"):
                    tree = ET.fromstring(content)
                    self.assertEqual(tree.tag, "{http://www.w3.org/2000/svg}svg")
                    self.assertNotIn("<script>", content)
                    self.assertNotIn("foreignObject", content)
            self.assertIn("&lt;test&gt;", files["assets/readme-builder/en/hero-dark.svg"])
            self.assertIn("<h2><picture>", files["README.md"])

    def test_all_original_icons_parse(self):
        for name in PATHS:
            ET.fromstring(icon(name))

    def test_build_is_deterministic_and_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            files = render(configuration(), ROOT)
            self.assertEqual(files, render(configuration(), ROOT))
            write_outputs(files, directory)
            self.assertEqual(write_outputs(files, directory, check=True), [])
            self.assertEqual(write_outputs(files, directory), [])
            self.assertEqual(inspect(directory), [])

    def test_refuses_unowned_or_edited_files_without_partial_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("Human work", encoding="utf-8")
            with self.assertRaises(ValueError):
                write_outputs(render(configuration(), ROOT), root)
            self.assertFalse((root / "assets").exists())
            write_outputs(render(configuration(), ROOT), root, force=True)
            (root / "README.md").write_text("Human edit", encoding="utf-8")
            with self.assertRaises(ValueError):
                write_outputs(render(configuration(), ROOT), root)
            self.assertEqual((root / "README.md").read_text(), "Human edit")

    def test_output_and_source_traversal_are_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            for name in ("../escape", "/absolute", "C:/absolute", "nested\\file"):
                with self.assertRaises(ValueError):
                    local(directory, name)
            config = configuration()
            config["documents"][0]["sections"][0]["source"] = "../outside.md"
            with self.assertRaises(ValueError):
                render(config, directory)

    def test_validation_rejects_overflow_and_duplicate_outputs(self):
        for mutation in (lambda c: c.update(theme="unknown"),
                         lambda c: c.update(name="x" * 65),
                         lambda c: c["documents"].append(copy.deepcopy(c["documents"][0])),
                         lambda c: c["documents"][0].update(language="../bad"),
                         lambda c: c["documents"][0]["features"][0].update(icon="arbitrary-svg")):
            config = configuration()
            mutation(config)
            with self.assertRaises(ValueError):
                render(config, ROOT)

    def test_migration_preserves_literal_examples_and_old_navigation(self):
        original = '# 🚀 Quick start\n\n[Go](#-quick-start)\n\n```text\n✅ literal sample\n```\n\n`🔒 key` and 🛡️ safe.\n'
        updated, assets = migrate(original)
        self.assertIn('<a id="-quick-start"></a>', updated)
        self.assertIn('</a>\n\n# <img', updated)
        self.assertIn('```text\n✅ literal sample\n```', updated)
        self.assertIn('`🔒 key`', updated)
        self.assertIn("shield.svg", updated)
        self.assertEqual(migrate(updated)[0], updated)
        self.assertEqual(len(assets), 2)

    def test_shortcodes_mermaid_and_html_attributes(self):
        original = '# Demo :movie_camera:\n<img alt="📦 project" src="local.svg" />\n```mermaid\nA["🤖 Agent"]\n```\n'
        updated, assets = migrate(original)
        self.assertIn('id="demo-movie_camera"', updated)
        self.assertIn('alt=" project"', updated)
        self.assertIn('A["Agent"]', updated)
        self.assertIn("assets/readme-builder/icons/play.svg", assets)

    def test_nested_badges_keep_valid_fragment_links(self):
        source = '[![SQLite](https://example.com/badge.svg)](#%EF%B8%8F-cómo-funciona)\n<a id="️-cómo-funciona"></a>\n'
        updated, _ = migrate(source)
        self.assertIn('(#-c%C3%B3mo-funciona)', updated)
        self.assertIn('id="-cómo-funciona"', updated)
        self.assertEqual(migrate(updated)[0], updated)

    def test_duplicate_heading_aliases_and_unicode_text(self):
        updated, _ = migrate("## 🚀 Inicio\n## 🚀 Inicio\nTexto español: acción, útil, México. 日本語\n")
        self.assertIn('id="-inicio"', updated)
        self.assertIn('id="-inicio-1"', updated)
        self.assertIn("acción, útil, México. 日本語", updated)

    def test_audit_rejects_executable_svg(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            assets = root / "assets" / "readme-builder"
            assets.mkdir(parents=True)
            (assets / "bad.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>', encoding="utf-8")
            self.assertEqual(inspect(root)[0]["kind"], "svg")

    def test_migration_is_dry_run_and_preserves_bom_and_crlf(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "README.md"
            original = b"\xef\xbb\xbf" + '# 🚀 Inicio\r\n\r\nTexto español.\r\n'.encode()
            path.write_bytes(original)
            self.assertTrue(migrate_file(path)[0])
            self.assertEqual(path.read_bytes(), original)
            migrate_file(path, True)
            actual = path.read_bytes()
            self.assertTrue(actual.startswith(b"\xef\xbb\xbf"))
            self.assertEqual(actual.count(b"\n"), actual.count(b"\r\n"))
            self.assertFalse(migrate_file(path, True)[0])

    def test_audit_reports_broken_links_conflicts_and_emoji(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text('# 🚀 Demo\n[bad](#missing)\n![bad](missing.svg)\n<<<<<<< HEAD\n', encoding="utf-8")
            self.assertEqual({i["kind"] for i in inspect(root)}, {"emoji", "anchor", "local-link", "conflict"})

    def test_cli_build_check_and_error_exit_codes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "project.json"
            config.write_text(json.dumps(configuration()), encoding="utf-8")
            args = [sys.executable, "-m", "readme_builder", "build", str(config), "--output", str(root)]
            def cli(arguments):
                return subprocess.run(arguments, cwd=ROOT, capture_output=True, text=True, timeout=20)
            self.assertEqual(cli(args + ["--check"]).returncode, 1)
            self.assertFalse((root / "README.md").exists())
            self.assertEqual(cli(args).returncode, 0)
            self.assertEqual(cli(args + ["--check"]).returncode, 0)
            (root / "README.md").write_text("edited", encoding="utf-8")
            self.assertEqual(cli(args).returncode, 2)


if __name__ == "__main__":
    unittest.main()
