"""Rebuild File:Shiogama Jinja plan.png by construction. The plan is axis-parallel lines of two kinds: dark outlines
(1 px black lines drawn anti-aliased between pixel rows or columns, so each shows as a pair of greys, 191 and 150; their
coverage adds up to 0.66 px) and light paths and steps (single 1 px grey #c1c1c1 lines on the pixel grid), plus two
small circles. Every horizontal and vertical run is measured (dark ones at their darkness-weighted sub-pixel position,
as for the Kōfukuji plan) and written as an exact segment; the circles are fitted. Run from the repo root."""
import numpy as np
from PIL import Image
from scipy import ndimage

PNG = 'data_lake/downloads/shiogama-plan/Shiogama Jinja plan.png'
OUT = 'files/shiogama-plan/Shiogama Jinja plan.svg'
a = np.asarray(Image.open(PNG).convert('L')).astype(float)
H, W = a.shape
dark_core = a < 175
_lab, _n = ndimage.label(dark_core)  # single dark pixels are crossings of two light lines, not dark lines
dark_core &= np.isin(_lab, np.nonzero(np.bincount(_lab.ravel()) >= 3)[0]) & (_lab > 0)
dark = ndimage.binary_dilation(dark_core) & (a < 230)  # the pair: the 150 row and its 191 neighbour
light = (((a > 185) & (a < 200)) | ((a < 175) & ~dark_core)) & ~dark


def runs(m, min_len):
    out = []
    for y in range(m.shape[0]):
        r = np.concatenate([[0], m[y].astype(int), [0]]); d = np.diff(r)
        out += [(y, s, e) for s, e in zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]) if e - s >= min_len]
    return out


def dark_lines(m, wgt, min_len=4):
    """horizontal dark lines (y, x0, x1), y at the darkness-weighted centre of the pair of rows"""
    segs = []
    for y, s, e in runs(m, min_len):
        w = wgt[max(0, y - 1):y + 2, s:e].sum(1)
        ys = np.arange(max(0, y - 1), y + 2)[:len(w)]
        segs.append((round(float((w * ys).sum() / max(w.sum(), 1)) + 0.5, 2), int(s), int(e)))
    out = []
    for cy, s, e in sorted(segs):  # one line shows on two rows: keep one
        if out and abs(out[-1][0] - cy) < 1.0 and abs(out[-1][1] - s) <= 2 and abs(out[-1][2] - e) <= 2:
            continue
        out.append((cy, s, e))
    return out


# circles: dark components that are neither long horizontal nor vertical runs
lab, n = ndimage.label(a < 245, np.ones((3, 3)))  # all ink: the anti-aliased rings break up under the dark mask
circles, circ_mask = [], np.zeros_like(dark)
for i, sl in enumerate(ndimage.find_objects(lab), 1):
    m = lab[sl] == i
    h, w = m.shape
    if 6 <= h <= 30 and abs(h - w) <= 2 and not m[h // 2, w // 2]:  # small ring, hollow centre
        ys, xs = np.nonzero(m & (a[sl] < 180))  # the ring's darkest pixels
        X, Y = xs + sl[1].start + 0.5, ys + sl[0].start + 0.5
        A = np.c_[2 * X, 2 * Y, np.ones(len(X))]
        cx, cy, c = np.linalg.lstsq(A, X ** 2 + Y ** 2, rcond=None)[0]
        circles.append((cx, cy, np.sqrt(c + cx ** 2 + cy ** 2)))
        circ_mask[sl] |= m
dk = dark & ~circ_mask
light &= ~circ_mask
wgt = (255 - a) * dk
hs = dark_lines(dk, wgt)
vs = dark_lines(dk.T, wgt.T)
lh = runs(light, 4)
lv = runs(light.T, 4)
d_dark = ''.join(f'M{s},{y}H{e}' for y, s, e in hs) + ''.join(f'M{x},{s}V{e}' for x, s, e in vs)
d_light = ''.join(f'M{s},{y + 0.5}H{e}' for y, s, e in lh) + ''.join(f'M{x + 0.5},{s}V{e}' for x, s, e in lv)
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
       f'<rect width="{W}" height="{H}" fill="#ffffff"/>\n'
       f'<path d="{d_light}" fill="none" stroke="#c1c1c1" stroke-width="1"/>\n'
       f'<path d="{d_dark}" fill="none" stroke="#000000" stroke-width="0.66" stroke-linecap="square"/>\n'
       + ''.join(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="none" stroke="#000000" stroke-width="0.66"/>\n'
                 for x, y, r in circles) + '</svg>\n')
open(OUT, 'w', encoding='utf8').write(svg)
print(len(hs), 'dark horizontal,', len(vs), 'dark vertical,', len(lh), 'light h,', len(lv), 'light v,', len(circles), 'circles')
