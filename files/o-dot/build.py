"""Rebuild File:O-dot.png: the Pe̍h-ōe-jī letters o͘ and O͘ (o / O + U+0358 COMBINING DOT ABOVE RIGHT) as real <text>
in a serif face with U+0358 (Noto Serif first; Times-like faces lack the mark). Font size from the capital O's ink
height in the PNG; each letter placed at its measured left edge and baseline with a <tspan>, keeping the font's own
proportions (the PNG's face is Times-like, so the dots sit slightly differently). Run from the repo root."""
import io
import numpy as np, resvg_py
from PIL import Image
from scipy import ndimage

PNG = 'data_lake/downloads/o-dot/O-dot.png'
OUT = 'files/o-dot/O-dot.svg'
FONT = 'data_lake/downloads/fonts/noto-serif/NotoSerif-Regular.ttf'
im = Image.open(PNG).convert('RGBA')
W, H = im.size
ink = np.asarray(Image.alpha_composite(Image.new('RGBA', im.size, 'white'), im).convert('L')) < 128
lab, n = ndimage.label(ink)
boxes = sorted(ndimage.find_objects(lab), key=lambda s: -(s[0].stop - s[0].start) * (s[1].stop - s[1].start))
big = sorted(boxes[:2], key=lambda s: s[1].start)  # the two letter bodies: o, O
o_box, O_box = [(s[1].start, s[1].stop, s[0].start, s[0].stop) for s in big]


def ink_of(t, size):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="2000" height="1600"><text x="500" y="1100" font-size="{size}" '
           f'font-family="Noto Serif">{t}</text></svg>')
    m = np.asarray(Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=svg, width=2000, font_files=[FONT],
                                                                     skip_system_fonts=True)))).convert('RGBA'))[..., 3] > 128
    ys, xs = np.nonzero(m)
    return xs.min() - 500, xs.max() - 500, ys.min() - 1100, ys.max() - 1100


# size from the full height of O͘ (its dot's top to the O's bottom), so the mark stays on the canvas: Noto's dot sits
# higher than the PNG font's
dots = [(s[1].start, s[1].stop, s[0].start, s[0].stop) for s in boxes[2:4]]
dot_top = min(d[2] for d in dots if d[0] > O_box[0])
x0, x1, y0, y1 = ink_of('O͘', 1000)
size = 1000 * (O_box[3] - dot_top) / (y1 - y0 + 1)
base = O_box[3] - (y1 + 1) * size / 1000  # baseline from the O's bottom
xo = ink_of('o', size)[0]
xO = ink_of('O', size)[0]
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
       f'<text font-family="\'Noto Serif\', \'DejaVu Serif\', serif" font-size="{size:.1f}" fill="#000000">'
       f'<tspan x="{o_box[0] - xo:.1f}" y="{base:.1f}">o͘</tspan> '
       f'<tspan x="{O_box[0] - xO:.1f}" y="{base:.1f}">O͘</tspan></text>\n</svg>\n')
open(OUT, 'w', encoding='utf8').write(svg)
r = np.asarray(Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=svg, width=W, font_files=[FONT],
                                                                 skip_system_fonts=True)))).convert('RGBA'))[..., 3] > 128
print(f'size {size:.1f}, IoU {(r & ink).sum() / (r | ink).sum():.3f}')
c = Image.new('L', (W * 2 + 10, H), 128)
c.paste(Image.fromarray(np.where(ink, 0, 255).astype('uint8')), (0, 0))
c.paste(Image.fromarray(np.where(r, 0, 255).astype('uint8')), (W + 10, 0))
c.save('scratch/odot_cmp.png')
