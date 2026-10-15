"""Rebuild File:East Asia Cutout Projection.png, a 250x250 crop of the 2009-10-04 revision of
File:East Asia (orthographic projection).svg (the revision current when the crop was made, 2010-11-01):
that SVG unchanged except for its root size and a viewBox on the crop window, found by normalised
cross-correlation with the PNG (renders by tools/render_svg.py; resvg crashes on this file).
Run from the repo root."""
import re, sys
import numpy as np
from PIL import Image
from scipy.signal import fftconvolve
sys.path.insert(0, 'tools')
from render_svg import render

SRC = 'data_lake/downloads/east-asia-cutout/East Asia (orthographic projection) 2009-10-04.svg'
PNG = 'data_lake/downloads/east-asia-cutout/East Asia Cutout Projection.png'
OUT = 'files/east-asia-cutout/East Asia Cutout Projection.svg'
K = 4  # render scale for the search
render(SRC, 'scratch/ea_src_x4.png', K)
B = Image.open('scratch/ea_src_x4.png').convert('RGBA')
B = Image.alpha_composite(Image.new('RGBA', B.size, 'white'), B).convert('L')
a = np.asarray(Image.open(PNG).convert('L')).astype(float)
t = a - a.mean()


def search(widths):
    best = None
    for ws in widths:
        f = 250 / ws
        b = np.asarray(B.resize((round(B.width * f / K), round(B.height * f / K)), Image.LANCZOS)).astype(float)
        num = fftconvolve(b, t[::-1, ::-1], mode='valid')
        s1 = fftconvolve(b, np.ones_like(t), mode='valid')
        s2 = fftconvolve(b * b, np.ones_like(t), mode='valid')
        ncc = num / np.sqrt(np.maximum(s2 - s1 * s1 / t.size, 1e-9) * (t * t).sum())
        i = np.unravel_index(np.argmax(ncc), ncc.shape)
        if best is None or ncc[i] > best[0]:
            best = (float(ncc[i]), float(ws), i[1] / f, i[0] / f)
    return best


best = search(np.arange(266, 274.01, 0.25))
ncc, ws, x, y = best
print('ncc %.4f  viewBox %.2f %.2f %.2f %.2f' % (ncc, x, y, ws, ws))
s = open(SRC, encoding='utf8').read()
root = re.search(r'<svg\b[^>]*>', s, re.S).group(0)
new = re.sub(r'\swidth="[^"]*"', ' width="250"', root, count=1)
new = re.sub(r'\sheight="[^"]*"', ' height="250"', new, count=1)
new = re.sub(r'\sviewBox="[^"]*"', '', new)
new = new[:-1] + f' viewBox="{x:.2f} {y:.2f} {ws:.2f} {ws:.2f}">'
open(OUT, 'w', encoding='utf8').write(s.replace(root, new, 1))
render(OUT, 'scratch/ea_out.png')
o = Image.open('scratch/ea_out.png').convert('RGBA')
o = np.asarray(Image.alpha_composite(Image.new('RGBA', o.size, 'white'), o).convert('RGB')).astype(int)
p = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
print('pixels differing %.4f' % (np.abs(o - p).max(-1) > 48).mean())
Image.fromarray(np.concatenate([p, o], 1).astype(np.uint8)).save('scratch/arms/ea_cmp.png')
