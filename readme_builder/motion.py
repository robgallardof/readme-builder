"""Self-contained background-only SVG motion; existing artwork bytes remain recoverable."""
import re
import math
from urllib.parse import unquote
import base64
import xml.etree.ElementTree as ET

PRESETS = ('off', 'subtle', 'ambient')
START = '<!-- readme-builder:motion:start -->'
END = '<!-- readme-builder:motion:end -->'


def validate_svg(source, _depth=0):
    """Validate a self-contained SVG, including an embedded raster logo."""
    root = ET.fromstring(source)
    if root.tag != '{http://www.w3.org/2000/svg}svg':
        raise ValueError('expected an SVG document')
    for node in root.iter():
        if node.tag.rsplit('}', 1)[-1] != 'image' and any(key.rsplit('}', 1)[-1].lower() == 'href' for key in node.attrib):
            raise ValueError('SVG references must be embedded raster images')
        if node.tag.rsplit('}', 1)[-1] == 'image':
            uri = node.get('href') or node.get('{http://www.w3.org/1999/xlink}href', '')
            match = re.fullmatch(r'data:image/(png|jpeg|webp);base64,([A-Za-z0-9+/=]+)', uri)
            if not match or len(uri) > 3_000_000:
                raise ValueError('only embedded raster images are allowed')
            data = base64.b64decode(match[2], validate=True)
            signatures = {'png': b'\x89PNG\r\n\x1a\n', 'jpeg': b'\xff\xd8\xff', 'webp': b'RIFF'}
            if not data.startswith(signatures[match[1]]):
                raise ValueError('embedded raster does not match its media type')
        if node.tag.rsplit('}', 1)[-1] in ('script', 'foreignObject', 'use'):
            raise ValueError('motion requires self-contained SVG artwork')
        if any(key.lower().startswith('on') for key in node.attrib):
            raise ValueError('event handlers are not allowed')
    css_attributes = {'style', 'fill', 'stroke', 'filter', 'clip-path', 'mask', 'marker-start', 'marker-mid', 'marker-end'}
    css = '\n'.join(
        [''.join(node.itertext()) for node in root.iter() if node.tag.rsplit('}', 1)[-1] == 'style']
        + [value for node in root.iter() for key, value in node.attrib.items() if key in css_attributes]
    )
    if _depth > 2 or '@import' in css.lower():
        raise ValueError("external or recursive SVG CSS is not allowed")
    for match in re.finditer(r'''url\(\s*(?:"([^"\n]*)"|'([^'\n]*)'|([^\s)]+))\s*\)''', css, re.I):
        uri = next(value for value in match.groups() if value is not None)
        if uri.startswith('#'):
            continue
        font = re.fullmatch(r'data:font/woff2;base64,([A-Za-z0-9+/=]+)', uri)
        if font and len(uri) <= 2_000_000 and base64.b64decode(font[1], validate=True).startswith(b'wOF2'):
            continue
        if uri.startswith('data:image/svg+xml,') and len(uri) < 20_000:
            validate_svg(unquote(uri.split(',', 1)[1]), _depth + 1)
            continue
        raise ValueError("external SVG CSS is not allowed")
    return root


def animate_svg(source, preset='subtle'):
    """Animate an opted-in hero background; keep document furniture static."""
    if preset not in PRESETS:
        raise ValueError('motion must be off, subtle or ambient')
    source = re.sub(re.escape(START) + r'.*?' + re.escape(END), '', source, flags=re.S)
    source = re.sub(r' data-readme-motion="(?:subtle|ambient)"', '', source, count=1)
    root = validate_svg(source)
    if preset == 'off':
        return source
    # Preserve externally authored animations such as calendars and arcade games.
    if any(n.tag.rsplit('}',1)[-1] in ('animate','animateTransform','set') for n in root.iter()) or '@keyframes' in source:
        return source
    view = root.get('viewBox', '0 0 24 24').split()
    if len(view) != 4:
        raise ValueError('SVG viewBox must have four numbers')
    x, y, width, height = map(float, view)
    if not all(math.isfinite(v) for v in (x,y,width,height)) or width <= 0 or height <= 0:
        raise ValueError('invalid SVG dimensions')
    if not list(root):
        return source
    # Motion belongs only to an explicitly authored background layer. A generic
    # SVG may be an icon, divider, signature, diagram or a screenshot of text.
    if root.get('data-readme-component') != 'hero' or not any(
        'rb-ambient' in node.get('class', '').split() for node in root.iter()
    ):
        return source
    duration, low, high = ('20s', '.38', '.58') if preset == 'subtle' else ('16s', '.3', '.7')
    css = f'''<style data-readme-builder-motion="1">
@keyframes rb-atmosphere {{0%,100%{{opacity:{low}}}50%{{opacity:{high}}}}}
svg[data-readme-motion] .rb-ambient{{animation:rb-atmosphere {duration} ease-in-out -5s infinite}}
@media (prefers-reduced-motion:reduce){{svg[data-readme-motion] .rb-ambient{{animation:none!important;opacity:.48}}}}
</style>'''
    marker = START + css + END
    opening = re.search(r'<svg\b[^>]*>',source)
    if opening is None:
        raise ValueError('SVG root was not found')
    source = source[:opening.end()-1] + f' data-readme-motion="{preset}">' + source[opening.end():]
    closing = source.rfind('</svg>')
    return source[:closing] + marker + source[closing:]
