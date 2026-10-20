"""Rebuild File:Shadow picture of Ehime prefecture.png from MLIT 国土数値情報 N03 (2024): the prefecture fitted to the
PNG's black by IoU with scale, aspect, rotation and offset. Unlike the other shadow pictures this one is drawn rotated
(about 29°; aspect 1.22 = 1/cos 35°, an equal-scale map at Ehime's latitude), which the batch fitter
(tools/batch_shadow.py) does not allow for. Run from the repo root; `fit` refits."""
import json, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import optimize
from shapely.geometry import shape
from shapely.ops import unary_union, transform as stransform

sys.path.insert(0, 'tools')
from n03_prefecture_svg import load  # noqa: E402

SRC = 'data_lake/downloads/shadow-ehime/Shadow picture of Ehime prefecture.png'
OUT = 'files/shadow-ehime/Shadow picture of Ehime prefecture.svg'
PAR = 'files/shadow-ehime/projection.json'

im = Image.open(SRC).convert('RGBA')
a = np.asarray(Image.alpha_composite(Image.new('RGBA', im.size, 'white'), im).convert('L'))
H, W = a.shape
ink = a < 128
geo = unary_union([shape(f['geometry']) for f in load(38)['features']]).buffer(0)
parts = [g for g in (geo.geoms if hasattr(geo, 'geoms') else [geo]) if g.area > 1e-7]


CX0, CY0 = geo.centroid.x, geo.centroid.y


def proj(p):
    sc, asp, rot, tx, ty = p
    c, sn = np.cos(np.radians(rot)), np.sin(np.radians(rot))

    def f(x, y, z=None):
        X = (np.asarray(x) - CX0) * sc
        Y = -(np.asarray(y) - CY0) * sc * asp
        return X * c - Y * sn + tx, X * sn + Y * c + ty
    return f


def raster(f):
    img = Image.new('1', (W, H), 0)
    d = ImageDraw.Draw(img)
    for g in parts:
        q = stransform(f, g)
        d.polygon(list(q.exterior.coords), fill=1)
        for r in q.interiors:
            d.polygon(list(r.coords), fill=0)
    return np.asarray(img)


def loss(p):
    m = raster(proj(p))
    return 1 - (m & ink).sum() / (m | ink).sum()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'fit':
        ys, xs = np.nonzero(ink)
        best = None
        for rot in range(-40, 41, 5):  # coarse grid over rotation and scale, then Nelder-Mead
            for sc in (250, 285, 320):
                p0 = [sc, 1.2, rot, xs.mean(), ys.mean()]
                l = loss(p0)
                if best is None or l < best[0]:
                    best = (l, p0)
        r = optimize.minimize(loss, best[1], method='Nelder-Mead', options={'maxiter': 2000, 'xatol': 1e-3, 'fatol': 1e-8})
        json.dump(list(r.x), open(PAR, 'w'))
    p = json.load(open(PAR))
    f = proj(p)
    print('IoU %.4f' % (1 - loss(p)))
    d = ''.join('M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in r.coords) + 'Z'
                for g in parts for q in [stransform(f, g.simplify(0.0003))] for r in [q.exterior, *q.interiors])
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<path fill="#000000" fill-rule="evenodd" d="{d}"/>', '</svg>']
    open(OUT, 'w', encoding='utf8').write('\n'.join(o) + '\n')
    print('wrote', OUT, len(parts), 'parts')
