"""Self-contained, bounded SVG motion; existing artwork bytes remain recoverable."""
import re
import math
import base64
import xml.etree.ElementTree as ET

PRESETS = ('off', 'subtle', 'ambient')
START = '<!-- readme-builder:motion:start -->'
END = '<!-- readme-builder:motion:end -->'


def animate_svg(source, preset='subtle'):
    """Add decorative motion without moving text; off restores the original SVG."""
    if preset not in PRESETS:
        raise ValueError('motion must be off, subtle or ambient')
    source = re.sub(re.escape(START) + r'.*?' + re.escape(END), '', source, flags=re.S)
    source = re.sub(r' data-readme-motion="(?:subtle|ambient)"', '', source, count=1)
    root = ET.fromstring(source)
    if root.tag != '{http://www.w3.org/2000/svg}svg':
        raise ValueError('expected an SVG document')
    for node in root.iter():
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
    if re.search(r'@import|url\(\s*["\x27]?(?!#)[^\s)]',source,re.I):
        raise ValueError('external SVG CSS is not allowed')
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
    duration, repeat = ('2s','2') if preset == 'subtle' else ('8s','infinite')
    css = f'''<style data-readme-builder-motion="1">
@keyframes rb-accent {{0%,100%{{filter:brightness(1)}}50%{{filter:brightness(1.3)}}}}
@keyframes rb-trace {{from{{stroke-dashoffset:{width:g}}}to{{stroke-dashoffset:0}}}}
svg[data-readme-motion] .rb-motion-line{{animation:rb-trace {duration} ease-in-out {repeat};stroke-dasharray:{width*.12:g} {width:g};stroke-dashoffset:0;opacity:.55}}
svg[data-readme-motion] &gt; path,svg[data-readme-motion] &gt; g:not(.rb-motion-layer){{animation:rb-accent {duration} ease-in-out {repeat}}}
@media (prefers-reduced-motion:reduce){{svg[data-readme-motion] .rb-motion-line,svg[data-readme-motion] &gt; path,svg[data-readme-motion] &gt; g:not(.rb-motion-layer){{animation:none!important;filter:none!important}}}}
</style>'''
    # Keep the accent in the top margin; never alter charts, prose, or data geometry.
    line = '' if width <= 64 else f'<g class="rb-motion-layer" aria-hidden="true" pointer-events="none"><path class="rb-motion-line" d="M{x+width*.04:g} {y+min(2,height*.02):g}h{width*.92:g}" fill="none" stroke="#8b5cf6" stroke-width="{min(2,height*.04):g}" stroke-linecap="round"/></g>'
    marker = START + css + line + END
    opening = re.search(r'<svg\b[^>]*>',source)
    if opening is None:
        raise ValueError('SVG root was not found')
    source = source[:opening.end()-1] + f' data-readme-motion="{preset}">' + source[opening.end():]
    closing = source.rfind('</svg>')
    return source[:closing] + marker + source[closing:]
