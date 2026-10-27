"""Motion contracts using real SVGs, files and CLI processes."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from readme_builder.motion import animate_svg
from readme_builder.build import render
from test_builder import configuration, ROOT


class MotionTests(unittest.TestCase):
    def test_reversible_idempotent_and_preserves_text_geometry(self):
        source='<svg xmlns="http://www.w3.org/2000/svg" data-readme-component="hero" viewBox="0 0 900 320"><g class="rb-ambient"><circle cx="800" cy="60" r="100"/></g><text x="50" y="50">Readable &amp; static</text></svg>\n'
        animated=animate_svg(source)
        ET.fromstring(animated)
        self.assertIn('prefers-reduced-motion',animated)
        self.assertIn('20s ease-in-out -5s infinite',animated)
        self.assertNotIn('stroke-dash',animated)
        self.assertNotIn('filter:',animated)
        self.assertIn('<text x="50" y="50">Readable &amp; static</text>',animated)
        self.assertEqual(animate_svg(animated),animated)
        self.assertEqual(animate_svg(animated,'off'),source)
        self.assertIn('16s ease-in-out -5s infinite',animate_svg(source,'ambient'))

    def test_real_cli_dry_run_and_switch_off(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder).resolve()/'banner with spaces.svg'
            source='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 100"/>'
            # Full closing tags are used by the current generator; arbitrary valid SVG roots are supported too.
            source=source.replace('/>',' data-readme-component="hero"><g class="rb-ambient"><circle r="20"/></g></svg>')
            path.write_text(source,encoding='utf-8')
            command=[sys.executable,'-m','readme_builder','animate',str(path)]
            subprocess.run(command,cwd=ROOT,check=True,capture_output=True)
            self.assertEqual(path.read_text(),source)
            subprocess.run([*command,'--write'],cwd=ROOT,check=True,capture_output=True)
            self.assertNotEqual(path.read_text(),source)
            subprocess.run([*command,'--write','--preset','off'],cwd=ROOT,check=True,capture_output=True)
            self.assertEqual(path.read_text(),source)

    def test_hostile_and_invalid_inputs_are_refused(self):
        for body in ('<script/>','<image href="https://example.invalid/x"/>','<path onclick="run()"/>'):
            with self.assertRaises(ValueError):
                animate_svg('<svg xmlns="http://www.w3.org/2000/svg">'+body+'</svg>')
        with self.assertRaises(ValueError):animate_svg('<svg/>')
        with self.assertRaises(ValueError):animate_svg('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 nan 20"/>')

    def test_generated_components_honor_motion_presets(self):
        config=configuration()
        for preset in ('subtle','ambient','off'):
            config['motion']=preset
            outputs=render(config,ROOT)
            self.assertEqual('data-readme-motion' in outputs['assets/readme-builder/en/hero-dark.svg'],preset!='off')

    def test_existing_arcade_animation_is_preserved(self):
        source='<svg xmlns="http://www.w3.org/2000/svg"><animate attributeName="opacity" values="0;1"/></svg>'
        self.assertEqual(animate_svg(source),source)

    def test_document_furniture_is_static_and_legacy_loading_overlay_is_removed(self):
        for source in ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M0 0h24"/></svg>',
                       '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 174"><text y="90">Owner</text></svg>']:
            self.assertEqual(animate_svg(source),source)
            old=source.replace('</svg>','<!-- readme-builder:motion:start --><path class="rb-motion-line"/><!-- readme-builder:motion:end --></svg>')
            self.assertEqual(animate_svg(old),source)

    def test_embedded_raster_logo_is_preserved_and_remote_svg_is_rejected(self):
        source='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 100"><image href="data:image/jpeg;base64,/9j/"/></svg>'
        self.assertEqual(animate_svg(animate_svg(source),'off'),source)
        with self.assertRaises(ValueError):
            animate_svg(source.replace('image/jpeg','image/svg+xml'))
