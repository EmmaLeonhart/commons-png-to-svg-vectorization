"""Rebuild File:Shu logo.png (Seton Hall University's text logo, PD-textlogo): "SETON HALL" as real <text> in white on
the PNG's blue, over a drop shadow (the same text in the PNG's darker blue, offset by the shift that best overlaps the
PNG's shadow pixels). The logo's face is a Garamond-like serif with its own letter spacing, so each word is one <text>
whose glyphs are positioned by an x list: every letter fitted (tools/fit_text.py) to its own ink columns in the PNG,
at the letters' median size. Run from the repo root."""
import sys
import numpy as np
from PIL import Image

sys.path.insert(0, 'tools')
from fit_text import fit  # noqa: E402

PNG = 'data_lake/downloads/shu-logo/Shu logo.png'
OUT = 'files/shu-logo/Shu logo.svg'
BLUE, SHADOW = '#004488', '#003b76'
FAMILY = 'Garamond'
FONT_STACK = "Garamond, 'EB Garamond', 'Adobe Garamond Pro', 'Times New Roman', serif"

a = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
H, W = a.shape[:2]
white = a.min(2) > 200
shadow = (np.abs(a - [0, 59, 118]).sum(2) < 12)
cols = white.any(0)
runs, x = [], 0
while x < W:  # each letter's ink columns
    if cols[x]:
        s = x
        while x < W and cols[x]:
            x += 1
        runs.append((s, x - 1))
    else:
        x += 1
letters = 'SETONHALL'
assert len(runs) == len(letters), runs
qs = []
for ch, (x0, x1) in zip(letters, runs):
    ys = np.nonzero(white[:, x0:x1 + 1].any(1))[0]
    qs.append(fit(ch, (x0, x1, int(ys.min()), int(ys.max())), FAMILY, 'normal', canvas=(W, H)))
size = float(np.median([q['size'] for q in qs]))
y = float(np.median([q['y'] for q in qs]))
xs = [q['x'] + ((x0 + x1) / 2 - (q['final_box'][0] + q['final_box'][1]) / 2) for q, (x0, x1) in zip(qs, runs)]
dx, dy = max(((np.roll(np.roll(white, j, 0), i, 1) & shadow).sum(), i, j) for i in range(12) for j in range(12))[1:]


def words(ox, oy, fill):
    return ''.join(f'<text x="{" ".join(f"{v + ox:.2f}" for v in xs[a:b])}" y="{y + oy:.2f}" fill="{fill}">{t}</text>'
                   for t, a, b in (('SETON', 0, 5), ('HALL', 5, 9)))


svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
       f'<rect width="{W}" height="{H}" fill="{BLUE}"/>\n'
       f'<g font-family="{FONT_STACK}" font-size="{size:.2f}">\n{words(dx, dy, SHADOW)}\n{words(0, 0, "#ffffff")}\n</g>\n'
       '</svg>\n')
open(OUT, 'w', encoding='utf8').write(svg)
print('wrote', OUT, 'size %.2f, shadow offset (%d, %d)' % (size, dx, dy))
