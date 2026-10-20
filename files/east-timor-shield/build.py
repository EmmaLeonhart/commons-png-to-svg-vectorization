"""Rebuild File:Shield Coat of arms of East Timor.png from its stated source, File:Coat of arms of East Timor.svg, in the
revision current when the PNG was made (2012-03-17; the 2017 and 2021 redraws differ: magenta reds, black rifle). The
shield is that SVG's own vector art: the outer rings and all lettering (the circular legend, RDTL, the motto and the
scroll's red outlines) are removed, the scroll's white body stays (it covers the shield's base as in the PNG), and the
viewBox is set so the shield's ink box matches the PNG's on a white background. Run from the repo root."""
import io, re
import numpy as np, resvg_py
from PIL import Image

SRC = 'data_lake/downloads/east-timor-shield/Coat of arms of East Timor (2012-03-17).svg'
PNG = 'data_lake/downloads/east-timor-shield/Shield Coat of arms of East Timor.png'
OUT = 'files/east-timor-shield/Shield Coat of arms of East Timor.svg'
# rings, the guide circles of the lettering, and the motto scroll (its red outline and white body)
DROP_IDS = ['path2208', 'path3181', 'path2162', 'path2166', 'path3155', 'path3166', 'path3174', 'path5121', 'path8230',
            'path9047', 'path9053', 'path9055']  # (path11039, also white, is the star: kept)

s = open(SRC, encoding='utf8').read()
for i in DROP_IDS:
    s, n = re.subn(r'<path\b[^>]*\bid="%s"[^>]*/>' % re.escape(i), '', s, flags=re.S)
    assert n == 1, i
s, n1 = re.subn(r'<g\b[^>]*\bid="text\d+"[^>]*>.*?</g>', '', s, flags=re.S)  # lettering groups
s, n2 = re.subn(r'<path\b[^>]*\bid="text\d+"[^>]*/>', '', s, flags=re.S)  # lettering converted to paths
print('removed', len(DROP_IDS), 'paths,', n1, 'lettering groups,', n2, 'lettering paths')


def ink_box(a):
    m = a.min(2) < 235
    ys, xs = np.nonzero(m)
    return xs.min(), xs.max() + 1, ys.min(), ys.max() + 1


r = Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=s)))).convert('RGBA')
ra = np.asarray(Image.alpha_composite(Image.new('RGBA', r.size, 'white'), r).convert('RGB')).astype(int)
pa = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
H, W = pa.shape[:2]
W0 = float(re.search(r'<svg\b[^>]*?\swidth="([\d.]+)"', s, re.S).group(1))
H0 = float(re.search(r'<svg\b[^>]*?\sheight="([\d.]+)"', s, re.S).group(1))
sx0, sx1, sy0, sy1 = ink_box(ra)  # in source px (rendered at the source's own size: 1 px = 1 user unit)
px0, px1, py0, py1 = ink_box(pa)
k = ((px1 - px0) / (sx1 - sx0) + (py1 - py0) / (sy1 - sy0)) / 2  # PNG px per source unit
vx, vy = sx0 - px0 / k, sy0 - py0 / k
head = re.search(r'<svg\b[^>]*>', s, re.S).group(0)
new = re.sub(r'\s(width|height|viewBox)="[^"]*"', '', head)
new = new[:-1] + f' width="{W}" height="{H}" viewBox="{vx:.3f} {vy:.3f} {W / k:.3f} {H / k:.3f}">'
s = s.replace(head, new + f'<rect x="{vx:.3f}" y="{vy:.3f}" width="{W / k:.3f}" height="{H / k:.3f}" fill="#ffffff"/>', 1)
open(OUT, 'w', encoding='utf8').write(s)
print('wrote', OUT, 'scale %.4f' % k, 'source', W0, H0)
