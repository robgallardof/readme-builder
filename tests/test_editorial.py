"""Editorial order, owner identity and real exported diagram contracts."""
import copy
from pathlib import Path
import tempfile
import unittest
from readme_builder.build import render,write_outputs
from readme_builder.cli import inspect
from readme_builder.motion import validate_svg
from test_builder import configuration,ROOT


class EditorialTests(unittest.TestCase):
    def test_explicit_stages_put_start_before_advanced_and_signature_last(self):
        config=configuration()
        config['documents'][0]['sections']=[{'title':'Internals','id':'internals','stage':'advanced','body':'Deep details.'},
            {'title':'Get started','id':'get-started','stage':'start','body':'A short working example.'}]
        output=render(config,ROOT)['README.md']
        self.assertLess(output.index('id="get-started"'),output.index('id="internals"'))
        self.assertTrue(output.rstrip().endswith('<!-- readme-builder:signature:end -->'))
        self.assertLess(output.index('Back to top'),output.index('<!-- readme-builder:signature:start -->'))

    def test_supplied_logo_is_embedded_and_footer_append_is_reported(self):
        config=configuration()
        config['branding']={'author':'Roberto Gallardo','logo':'assets/brand/rg-logo.jpg','profile':'https://github.com/robgallardof'}
        output=render(config,ROOT)
        svg=output['assets/readme-builder/en/footer-light.svg']
        self.assertIn('data:image/jpeg;base64,',svg)
        self.assertIn('Roberto Gallardo',svg)
        validate_svg(svg)
        with tempfile.TemporaryDirectory() as directory:
            write_outputs(output,directory)
            self.assertEqual(inspect(directory),[])
            readme=Path(directory)/'README.md'
            readme.write_text(readme.read_text(encoding='utf-8')+'\n## Stray integration\n',encoding='utf-8')
            self.assertIn('footer-order',[finding['kind'] for finding in inspect(directory)])

    def test_branding_is_opt_in_and_unsafe_inputs_fail_before_writes(self):
        self.assertNotIn('Roberto Gallardo',render(configuration(),ROOT)['assets/readme-builder/en/footer-dark.svg'])
        for logo,url in [('../private.jpg','https://github.com/example'),('assets/brand/rg-logo.jpg','javascript:run()')]:
            config=configuration();config['branding']={'author':'Owner','logo':logo,'profile':url}
            with self.assertRaises(ValueError):render(config,ROOT)

    def test_imports_real_archify_exports_without_running_external_commands(self):
        config=configuration()
        config['documents'][0]['sections'][0]['diagram']={'provider':'archify','alt':'A verified authoring path',
            'light':'assets/diagrams/authoring-light.svg','dark':'assets/diagrams/authoring-dark.svg'}
        output=render(config,ROOT)
        imported=output['assets/readme-builder/en/diagram-01-light.svg']
        self.assertIn('data-quality-profile="showcase"',imported)
        self.assertIn('Write the story',imported)
        self.assertIn('A verified authoring path',output['README.md'])
        with tempfile.TemporaryDirectory() as directory:
            write_outputs(output,directory)
            self.assertEqual(inspect(directory),[])

    def test_remote_css_and_executable_embedded_icons_are_rejected(self):
        for css in ['url(https://example.invalid/font.woff2)',
                    'url("data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%3E%3Cscript/%3E%3C/svg%3E")']:
            source='<svg xmlns="http://www.w3.org/2000/svg"><style>path{fill:'+css+'}</style></svg>'
            with self.assertRaises(ValueError):validate_svg(source)

    def test_xml_entities_cannot_hide_remote_css(self):
        source='<svg xmlns="http://www.w3.org/2000/svg"><style>@im&#112;ort "https://example.invalid/style.css";</style></svg>'
        with self.assertRaises(ValueError):validate_svg(source)

    def test_external_element_references_are_rejected(self):
        for element in ['<a href="https://example.invalid/">text</a>',
                        '<feImage href="https://example.invalid/image.png"/>']:
            with self.assertRaises(ValueError):
                validate_svg('<svg xmlns="http://www.w3.org/2000/svg">'+element+'</svg>')

    def test_footer_matches_an_authored_header_palette_and_width(self):
        config=configuration()
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/'logo.jpg').write_bytes((ROOT/'assets/brand/rg-logo.jpg').read_bytes())
            (root/'header.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 300"><defs><linearGradient id="bg"><stop stop-color="#102030"/><stop offset="1" stop-color="#203040"/></linearGradient><linearGradient id="brand"><stop stop-color="#345678"/><stop offset="1" stop-color="#456789"/></linearGradient></defs></svg>',encoding='utf-8')
            config['branding']={'author':'Owner','logo':'logo.jpg','profile':'https://github.com/example',
                'headers':{'light':'header.svg','dark':'header.svg'}}
            output=render(config,root)
            svg=output['assets/readme-builder/en/footer-dark.svg']
            validate_svg(svg)
            self.assertIn('viewBox="0 0 1200 260"',svg)
            for color in ('#102030','#203040','#345678','#456789'):
                self.assertIn(color,svg)
            self.assertNotIn('@keyframes',svg)
            self.assertNotIn('width="360"',output['README.md'])
