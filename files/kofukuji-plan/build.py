"""Rebuild File:Kōfukuji plan.png by construction: the plan is 1 px black lines drawn anti-aliased between pixel rows
and columns (so each shows as a pair of grey rows or columns). Every horizontal and vertical line is measured at its
darkness-weighted sub-pixel position and written as an exact segment; the two octagons (whose 45° edges are not
horizontal or vertical) are fitted as polygons to their outlines; the black triangle is its filled hull.
Run from the repo root."""
import glob
import numpy as np
from PIL import Image
from scipy import ndimage
from shapely.geometry import MultiPoint

PNG = glob.glob('data_lake/downloads/kofukuji-plan/*.png')[0]
OUT = 'files/kofukuji-plan/Kōfukuji plan.svg'
a = np.asarray(Image.open(PNG).convert('L')).astype(float)
H, W = a.shape
dark = 255 - a
ink = dark > 30
black = a < 40


def lines(ink, dark, min_len=6):
    """horizontal lines: (y, x0, x1) with sub-pixel y from the darkness of the rows around each run"""
    segs = []
    for y in range(ink.shape[0]):
        r = np.concatenate([[0], ink[y].astype(int), [0]]); d = np.diff(r)
        for s, e in zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]):
            if e - s < min_len:
                continue
            w = dark[max(0, y - 1):y + 2, s:e].sum(1)
            cy = (w * np.arange(max(0, y - 1), y + 2)[:len(w)]).sum() / max(w.sum(), 1) + 0.5
            segs.append((round(float(cy), 2), int(s), int(e)))
    out = []
    for cy, s, e in sorted(segs):  # a line shows on two rows: keep one
        if out and abs(out[-1][0] - cy) < 1.0 and abs(out[-1][1] - s) <= 2 and abs(out[-1][2] - e) <= 2:
            continue
        out.append((cy, s, e))
    return out


# octagons: components whose outline has diagonal edges; find them by their bounding boxes in the PNG
lab, n = ndimage.label(ndimage.binary_dilation(ink))  # dilated: anti-aliased diagonals break up otherwise
octs, oct_mask = [], np.zeros_like(ink)
for i, sl in enumerate(ndimage.find_objects(lab), 1):
    comp = (lab[sl] == i) & ink[sl]
    h, w = comp.shape
    if 25 <= h <= 70 and 25 <= w <= 70 and abs(h - w) <= 6 and not comp[:4, :4].any() and comp[:4, w // 2].any():
        ys, xs = np.nonzero(comp)
        hull = MultiPoint(np.c_[xs + sl[1].start + 0.5, ys + sl[0].start + 0.5]).convex_hull
        for tol in np.arange(0.5, 6, 0.25):
            s = hull.simplify(tol)
            if len(s.exterior.coords) - 1 <= 8:
                break
        octs.append(s)
        oct_mask[sl] |= comp
tri = black & ~oct_mask
ty, tx = np.nonzero(tri)
tri_poly = MultiPoint(np.c_[tx + 0.5, ty + 0.5]).convex_hull.simplify(0.75) if len(tx) else None
lin_ink = ink & ~oct_mask & ~ndimage.binary_dilation(tri, iterations=2)
hs = lines(lin_ink, dark * lin_ink)
vs = lines(lin_ink.T, (dark * lin_ink).T)
d = ''.join(f'M{s},{y}H{e}' for y, s, e in hs) + ''.join(f'M{x},{s}V{e}' for x, s, e in vs)
d += ''.join('M' + ' '.join(f'{x:.2f},{y:.2f}' for x, y in list(o.exterior.coords)[:-1]) + 'Z' for o in octs)
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
       f'<rect width="{W}" height="{H}" fill="#ffffff"/>\n'
       f'<path d="{d}" fill="none" stroke="#000000" stroke-width="0.75" stroke-linecap="square"/>\n'
       + (f'<path d="M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in list(tri_poly.exterior.coords)[:-1]) + 'Z"/>\n'
          if tri_poly is not None else '') + '</svg>\n')
open(OUT, 'w', encoding='utf8').write(svg)
print(len(hs), 'horizontal,', len(vs), 'vertical,', len(octs), 'octagons, triangle', tri_poly is not None)
