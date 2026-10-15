"""Rebuild File:COL-city icon.png from its two stated sources: File:Ciudad.svg (Ecelan) with its two white
building shapes (path6403, path6405) filled with the bands of the flag of Colombia (File:Flag of
Colombia.svg's 2:1:1 layout, in the colours the PNG has, those of the flag file in 2013). Band edges
measured from the PNG; canvas 500 px as the PNG. Run from the repo root."""
import re
import numpy as np
from PIL import Image
import sys
sys.path.insert(0, 'tools')
from render_svg import render

SRC = 'data_lake/downloads/col-city-icon/Ciudad.svg'
PNG = 'data_lake/downloads/col-city-icon/COL-city icon.png'
OUT = 'files/col-city-icon/COL-city icon.svg'
LAYER_DY = 65.855373  # layer1 is translated by (-69.34421, -65.855373)
LAYER_DX = 69.34421
BLUE_TOP, RED_TOP, RED_BOTTOM = 243.2 / 2.5, 346.6 / 2.5, 450 / 2.5   # PNG px / 2.5 = Ciudad units
band = RED_TOP - BLUE_TOP
SKY_R = 15  # inner corner radius of the frame (Ciudad units)
YELLOW_TOP = BLUE_TOP - 2 * band

s = open(SRC, encoding='utf8').read()


def copy_of(pid):
    """the geometry of a path (its d and transform) without its style, for the outline."""
    el = re.search(r'<path[^>]*id="%s".*?/>' % pid, s, re.S).group(0)
    d = re.search(r'\sd="([^"]+)"', el).group(1)
    tr = re.search(r'transform="([^"]+)"', el)
    return f'<path d="{d}"' + (f' transform="{tr.group(1)}"' if tr else '') + '/>'


OUTLINE = copy_of('path6403') + copy_of('path6405')
# the PNG differs from Ciudad.svg beyond the fill: its sky is white (Ciudad's is part of the black frame)
# and the buildings carry a 5-unit black outline (measured: frame and outline both 12-13 px at 500 px)
sky = (f'<rect id="sky" x="{LAYER_DX + 5}" y="{LAYER_DY + 5}" width="190" height="{RED_BOTTOM - 5:.3f}" rx="{SKY_R}" fill="#fff"/>'
       f'<g fill="#000" stroke="#000" stroke-width="10" stroke-linejoin="miter">{OUTLINE}</g>')
bands = (sky + f'<clipPath id="buildings"><use xlink:href="#path6403"/><use xlink:href="#path6405"/></clipPath>'
         f'<g id="flag-of-colombia" clip-path="url(#buildings)">'
         f'<rect x="{LAYER_DX - 5}" y="{YELLOW_TOP + LAYER_DY:.3f}" width="210" height="{2 * band:.3f}" fill="#fcd116"/>'
         f'<rect x="{LAYER_DX - 5}" y="{BLUE_TOP + LAYER_DY:.3f}" width="210" height="{band:.3f}" fill="#003893"/>'
         f'<rect x="{LAYER_DX - 5}" y="{RED_TOP + LAYER_DY:.3f}" width="210" height="{band:.3f}" fill="#ce1126"/></g>')
# insert after the second building path, before the windows
m = re.search(r'<path[^>]*id="path6405".*?/>', s, re.S)
assert m
s = s[:m.end()] + bands + s[m.end():]
if 'xmlns:xlink' not in s[:2000]:
    s = s.replace('<svg', '<svg xmlns:xlink="http://www.w3.org/1999/xlink"', 1)
root = re.search(r'<svg\b[^>]*>', s, re.S).group(0)
new = re.sub(r'\swidth="[^"]*"', ' width="500"', root, count=1)
new = re.sub(r'\sheight="[^"]*"', ' height="500"', new, count=1)
new = new[:-1] + ' viewBox="0 0 200 200.02023">'
s = s.replace(root, new, 1)
open(OUT, 'w', encoding='utf8').write(s)
render(OUT, 'scratch/col_out.png')
on_white = lambda im: np.asarray(Image.alpha_composite(Image.new('RGBA', im.size, 'white'), im.convert('RGBA')).convert('RGB')).astype(int)
o, p = on_white(Image.open('scratch/col_out.png')), on_white(Image.open(PNG))
print('pixels differing %.4f' % (np.abs(o - p).max(-1) > 48).mean())
Image.fromarray(np.concatenate([p, o], 1).astype(np.uint8)).save('scratch/arms/col_cmp.png')
