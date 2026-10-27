"""Showcase kit contracts: safe SVG, reduced motion, marker filling and idempotent upgrades."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

from readme_builder import kit
from readme_builder.kitbuild import loc, render, upgrade
from readme_builder.motion import animate_svg, validate_svg
from test_builder import ROOT


class ComponentTests(unittest.TestCase):
    def components(self):
        yield kit.button("Docs & <API>", "rocket", "primary", "dark", trailing=True)[0]
        yield kit.button("Español", "lucide-globe", "outline", "light", small=True)[0]
        yield kit.stats([{"value": "7+", "label": "years"}, {"value": "MSc", "label": "Architecture"}])
        yield kit.wave()
        yield kit.heading("01", "About", "Readable & honest", "layers", "light")
        yield kit.card("Tool", "Short text <b>not markup</b>.", ["Rust", "MCP"], "code", "dark", kicker="kicker", badge="New")
        yield kit.bento([{"span": 2, "title": "A", "text": "B"}, {"title": "C", "text": "D"}])
        yield kit.panels([{"title": "X", "items": ["a", "b"]}], style="list")

    def test_components_are_self_contained_and_escaped(self):
        for source in self.components():
            root = validate_svg(source)
            self.assertNotIn("<b>", "".join(root.itertext()).replace("<b>not", ""))
            self.assertIn("prefers-reduced-motion", source)
            self.assertNotIn("<script", source)
            self.assertEqual(animate_svg(source), source)
        self.assertIn("Docs &amp; &lt;API&gt;", kit.button("Docs & <API>")[0])

    def test_overflowing_copy_is_refused_not_clipped(self):
        with self.assertRaises(ValueError):
            kit.card("T", "word " * 120)
        with self.assertRaises(ValueError):
            kit.colors("neon")

    def test_localised_values(self):
        self.assertEqual(loc({"en": "Hi", "es": "Hola"}, "es"), "Hola")
        self.assertEqual(loc({"label": {"en": "Hi", "es": "Hola"}, "n": 1}, "en"), {"label": "Hi", "n": 1})


class BuildTests(unittest.TestCase):
    def test_render_fills_markers_and_is_stable(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "README.md").write_text("A\n<!-- kit:go -->\n<!-- /kit:go -->\n<!-- kit:w -->old<!-- /kit:w -->\n", encoding="utf-8")
            config = {"version": 1, "documents": {"README.md": "en"}, "blocks": [
                {"id": "go", "type": "buttons", "items": [{"label": "Start", "href": "#start", "icon": "rocket"}]},
                {"id": "w", "type": "divider"}]}
            files = render(config, root)
            self.assertIn('href="#start"', files["README.md"])
            self.assertNotIn("old", files["README.md"])
            self.assertIn("assets/kit/wave.svg", files)
            (root / "README.md").write_text(files["README.md"], encoding="utf-8")
            self.assertEqual(render(config, root)["README.md"], files["README.md"])

    def test_unknown_marker_and_unsafe_folder_are_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "README.md").write_text("<!-- kit:nope --><!-- /kit:nope -->", encoding="utf-8")
            with self.assertRaises(ValueError):
                render({"version": 1, "documents": {"README.md": "en"}, "blocks": []}, root)
            with self.assertRaises(ValueError):
                render({"version": 1, "assets": "../x", "documents": {"README.md": "en"}, "blocks": []}, root)

    def test_upgrade_is_idempotent_and_skips_fences(self):
        source = ('<p align="center"><a href="README.md">English</a> · <a href="README.es.md">Español</a></p>\n\n'
                  '## One\n\ntext\n\n```md\n## not a heading\n<p align="center"><a href="#x">X</a></p>\n```\n\n'
                  '<a id="two"></a>\n\n## Two\n\n<p align="center"><a href="#top">Back to top</a></p>\n')
        once, files = upgrade(source)
        self.assertEqual(upgrade(once)[0], once)
        self.assertEqual(once.count("wave.svg"), 1)
        self.assertLess(once.index("wave.svg"), once.index('<a id="two">'))
        self.assertIn('<p align="center"><a href="#x">X</a></p>', once)
        self.assertIn("btn-english-primary-sm-dark.svg", once)
        self.assertIn("assets/readme-builder/kit/btn-back-to-top-outline-sm-light.svg", files)

    def test_cli_upgrade_dry_run_then_write(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "README.md"
            path.write_text("# T\r\n\r\n## A\r\n\r\n## B\r\n", encoding="utf-8", newline="")
            command = [sys.executable, "-m", "readme_builder", "kit", "upgrade", str(path)]
            subprocess.run(command, cwd=ROOT, check=True, capture_output=True)
            self.assertNotIn("wave", path.read_text(encoding="utf-8"))
            subprocess.run([*command, "--write"], cwd=ROOT, check=True, capture_output=True)
            text = path.read_bytes().decode()
            self.assertIn("wave.svg", text)
            self.assertNotIn("\n\n", text.replace("\r\n", ""))
            ET.parse(Path(folder) / "assets/readme-builder/kit/wave.svg")


if __name__ == "__main__":
    unittest.main()
