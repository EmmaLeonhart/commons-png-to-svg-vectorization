"""Rebuild File:Shadow picture of Hokkaido prefecture.png from MLIT 国土数値情報 N03 (2024). Outside its inset the PNG is
pixel-identical to File:Shadow picture of Hokkaido prefecture edit.png, so the main map is that rebuild's geometry and
fit (files/shadow-hokkaido-edit/projection.json, via tools/shadow_rotfit.py). The inset (top right, behind a 2 px frame)
holds what the edit leaves out: N03's Shikotan, Kunashiri, Etorofu, Shana and Shibetoro districts and the Habomai islets,
fitted to the inset's ink with their own scale, aspect, rotation and offset. Run from the repo root; `fit` refits the
inset."""
import json, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import optimize
from shapely.geometry import shape
from shapely.ops import unary_union, transform as stransform

sys.path.insert(0, 'tools')
from n03_prefecture_svg import load  # noqa: E402

SRC = 'data_lake/downloads/shadow-hokkaido/Shadow picture of Hokkaido prefecture.png'
OUT = 'files/shadow-hokkaido/Shadow picture of Hokkaido prefecture.svg'
MAIN_PAR = 'files/shadow-hokkaido-edit/projection.json'
PAR = 'files/shadow-hokkaido/inset.json'
KURILS = {'色丹郡', '国後郡', '択捉郡', '紗那郡', '蘂取郡'}
MAX_LON = 145.84  # Habomai islets lie east of this, in Nemuro city
FRAME = [(333, 1), (333, 104), (383, 154), (550, 154)]

im = Image.open(SRC).convert('RGBA')
ink = np.asarray(Image.alpha_composite(Image.new('RGBA', im.size, 'white'), im).convert('L')) < 128
H, W = ink.shape
yy, xx = np.mgrid[:H, :W]
in_inset = (xx > 335) & (yy < 152) & (xx - yy > -69)  # right of the frame and above it
ink_inset = ink & in_inset

feats = load(1)['features']
main_geo = unary_union([shape(f['geometry']) for f in feats if f['properties'].get('N03_003') not in KURILS]).buffer(0)
main_parts = [g for g in main_geo.geoms if g.area > 1e-7 and g.centroid.x < MAX_LON]
inset_parts = [g for g in main_geo.geoms if g.area > 1e-7 and g.centroid.x >= MAX_LON]
inset_parts += [g for f in feats if f['properties'].get('N03_003') in KURILS
                for g in (lambda s: s.geoms if hasattr(s, 'geoms') else [s])(shape(f['geometry']).buffer(0)) if g.area > 1e-7]


def proj(p, centre):
    sc, asp, rot, tx, ty = p
    c, sn = np.cos(np.radians(rot)), np.sin(np.radians(rot))

    def f(x, y, z=None):
        X = (np.asarray(x) - centre[0]) * sc
        Y = -(np.asarray(y) - centre[1]) * sc * asp
        return X * c - Y * sn + tx, X * sn + Y * c + ty
    return f


def raster(parts, f):
    img = Image.new('1', (W, H), 0)
    d = ImageDraw.Draw(img)
    for g in parts:
        q = stransform(f, g)
        d.polygon(list(q.exterior.coords), fill=1)
        for r in q.interiors:
            d.polygon(list(r.coords), fill=0)
    return np.asarray(img)


def iou(m, t):
    return (m & t).sum() / max(1, (m | t).sum())


def path_d(parts, f):
    return ''.join('M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in r.coords) + 'Z'
                   for g in parts for q in [stransform(f, g.simplify(0.0003))] for r in [q.exterior, *q.interiors])


# the main map's centre is the edit rebuild's: shadow_rotfit takes the centroid of everything outside the dropped
# districts, Habomai included
main_centre = main_geo.centroid.coords[0]
inset_centre = unary_union(inset_parts).centroid.coords[0]
fm = proj(json.load(open(MAIN_PAR)), main_centre)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'fit':
        ys, xs = np.nonzero(ink_inset)
        gx0, gy0, gx1, gy1 = unary_union(inset_parts).bounds
        s0 = (xs.max() - xs.min()) / (gx1 - gx0)
        loss = lambda p: 1 - iou(raster(inset_parts, proj(p, inset_centre)) & in_inset, ink_inset)
        best = None
        for rot in range(-40, 41, 5):
            for sc in (0.8 * s0, s0, 1.2 * s0):
                p0 = [sc, 1.37, rot, xs.mean(), ys.mean()]
                l = loss(p0)
                if best is None or l < best[0]:
                    best = (l, p0)
        r = optimize.minimize(loss, best[1], method='Nelder-Mead', options={'maxiter': 2000, 'xatol': 1e-3, 'fatol': 1e-8})
        json.dump(list(r.x), open(PAR, 'w'))
    fi = proj(json.load(open(PAR)), inset_centre)
    m = raster(main_parts, fm) | raster(inset_parts, fi)
    print('main IoU %.4f (outside the inset), inset IoU %.4f, whole IoU %.4f' % (
        iou(raster(main_parts, fm) & ~in_inset, ink & ~in_inset),
        iou(raster(inset_parts, fi) & in_inset, ink_inset), iou(m, ink)))
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<path fill="#000000" fill-rule="evenodd" d="{path_d(main_parts, fm)}{path_d(inset_parts, fi)}"/>',
         '<path fill="none" stroke="#000000" stroke-width="2" d="M' + ' '.join(f'{x},{y}' for x, y in FRAME) + '"/>',
         '</svg>']
    open(OUT, 'w', encoding='utf8').write('\n'.join(o) + '\n')
    print('wrote', OUT)
