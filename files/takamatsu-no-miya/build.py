"""Rebuild File:Takamatsu no miya.png (the Takamatsu-no-miya crest) from the crest group (g3132) of
File:Emblem of Nobuhito, Prince Takamatsu (Collar of the Order of Charles III).svg: the collar and
everything else dropped, gold fills recoloured black and the dark-gold outlines white, then scaled
and placed against the PNG's ink. Run from the repo root."""
import io, re
import numpy as np, resvg_py
from PIL import Image

SRC = 'data_lake/downloads/kamon/Emblem of Nobuhito, Prince Takamatsu (Collar of the Order of Charles III).svg'
OUT = 'files/takamatsu-no-miya/Takamatsu no miya.svg'
png_im = Image.open('data_lake/downloads/order-life-arms/png/Takamatsu no miya.png').convert('RGBA')
W, H = png_im.size
bg = Image.new('RGBA', png_im.size, 'white')
ink = np.asarray(Image.alpha_composite(bg, png_im).convert('L')) < 128

import xml.etree.ElementTree as ET
s = open(SRC, encoding='utf8').read()
for p, u in re.findall(r'xmlns:(\w+)="([^"]+)"', s):
    ET.register_namespace(p, u)
ET.register_namespace('', 'http://www.w3.org/2000/svg')
root = ET.fromstring(s)
N = '{http://www.w3.org/2000/svg}'
outer = root.find(N + 'g')
for c in list(outer):
    if c.get('id') != 'g3132':
        outer.remove(c)
# defs only as far as the crest uses them
crest_xml = ET.tostring(outer).decode()
used = set(re.findall(r'url\(#([^)]+)\)|href="#([^"]+)"', crest_xml))
body = crest_xml
for old in ('#fee46e', '#e7cd54', '#ffefa7'):
    body = body.replace(old, '#000000')
body = body.replace('#ac8800', '#ffffff')
STROKE = float(__import__('os').environ.get('STROKE', '1'))  # outline width factor (the PNG's separations are thinner)
body = re.sub(r'stroke-width:([0-9.]+)', lambda m: f'stroke-width:{float(m.group(1)) * STROKE:.4f}', body)
body = re.sub(r'stroke-width="([0-9.]+)"', lambda m: f'stroke-width="{float(m.group(1)) * STROKE:.4f}"', body)
x0, y0, w0, h0 = 0, 0, float(root.get('width')), float(root.get('height'))


def svg(scale, cx, cy):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<rect width="{W}" height="{H}" fill="#ffffff"/>'
            f'<g transform="translate({cx:.2f},{cy:.2f}) scale({scale:.5f}) translate({-CX:.3f},{-CY:.3f})">{body}</g></svg>')


def render(sv):
    im = Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=sv)))).convert('RGBA')
    return np.asarray(Image.alpha_composite(Image.new('RGBA', im.size, 'white'), im).convert('L')) < 128


# crest centre and size in source units, from a render at known scale
probe = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w0*4:.0f}" height="{h0*4:.0f}" viewBox="0 0 {w0} {h0}">{body}</svg>')
m = render(probe)
ys, xs = np.nonzero(m)
CX, CY = (xs.min() + xs.max()) / 8, (ys.min() + ys.max()) / 8
size = (xs.max() - xs.min()) / 4
ys, xs = np.nonzero(ink)
pcx, pcy, psize = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2, xs.max() - xs.min()
k0 = psize / size
score = lambda sv: (lambda r: (r & ink).sum() / (r | ink).sum())(render(sv))
best = max((score(svg(k, pcx + dx, pcy + dy)), k, pcx + dx, pcy + dy)
           for k in k0 * np.arange(0.97, 1.031, 0.01) for dx in (-2, 0, 2) for dy in (-2, 0, 2))
print('ink IoU %.4f scale %.4f centre %.1f,%.1f' % best)
open(OUT, 'w', encoding='utf8').write(svg(*best[1:]))
