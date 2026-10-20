"""Rebuild File:Shadow picture of Nagasaki prefecture.png from MLIT 国土数値情報 N03 (2000). The PNG has two framed insets,
Tsushima (left, below and left of a stepped frame line) and Iki (the box at the top), so a single fit fails
(tools/shadow_rotfit.py: IoU 0.31). Each part (the rest of the prefecture, 対馬市, 壱岐市) is fitted to the ink in its
own region with scale, aspect, rotation and offset; the 1 px frame lines are measured. A 1 px outline matches the
PNG's slightly bolder silhouettes. Run from the repo root; `fit`
refits."""
import json, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import optimize
from shapely.geometry import shape
from shapely.ops import unary_union, transform as stransform


SRC = 'data_lake/downloads/shadow-nagasaki/Shadow picture of Nagasaki prefecture.png'
OUT = 'files/shadow-nagasaki/Shadow picture of Nagasaki prefecture.svg'
PAR = 'files/shadow-nagasaki/projection.json'
FRAME_COL = '#202020'
IKI_BOX = [(195.5, 7), (195.5, 70.5), (112.5, 70.5), (112.5, 8)]  # its top is the canvas edge, left open as in the PNG
STEP = [(112.5, 70.5), (112.5, 74.5), (86.5, 107.5), (86.5, 169.5), (43.5, 225.5), (11, 225.5)]
TSUSHIMA_REGION = [(0, 0), (112.5, 0), *STEP[1:5], (0, 225.5)]

im = Image.open(SRC).convert('RGBA')
ink = np.asarray(Image.alpha_composite(Image.new('RGBA', im.size, 'white'), im).convert('L')) < 128
H, W = ink.shape


def poly_mask(pts):
    img = Image.new('1', (W, H), 0)
    ImageDraw.Draw(img).polygon(pts, fill=1)
    return np.asarray(img)


fimg = Image.new('1', (W, H), 0)
d = ImageDraw.Draw(fimg)
d.line(IKI_BOX, fill=1, width=3); d.line(STEP, fill=1, width=3)
frame_px = np.asarray(fimg)
regions = {'tsushima': poly_mask(TSUSHIMA_REGION) & ~frame_px,
           'iki': poly_mask([(112.5, 0), (195.5, 0), (195.5, 70.5), (112.5, 70.5)]) & ~frame_px}
regions['main'] = ~(regions['tsushima'] | regions['iki']) & ~frame_px

# N03 of 2000-10-01, the era of the PNG's source data (2024's adds the Isahaya Bay reclamation, which it lacks). Then
# Tsushima was the towns of 上県郡 and 下県郡, Iki those of 壱岐郡
import io, zipfile, shapefile
z = zipfile.ZipFile('data_lake/downloads/n03/2000/N03-001001_42_GML.zip')
base = 'N03-001001_42-g_AdministrativeBoundary'
rd = shapefile.Reader(shp=io.BytesIO(z.read(base + '.shp')), shx=io.BytesIO(z.read(base + '.shx')),
                      dbf=io.BytesIO(z.read(base + '.dbf')), encoding='cp932')
feats = [(sr.record[2] or '', shape(sr.shape.__geo_interface__)) for sr in rd.iterShapeRecords()]
groups = {'tsushima': [g for gun, g in feats if gun in ('上県郡', '下県郡')], 'iki': [g for gun, g in feats if gun == '壱岐郡'],
          'main': [g for gun, g in feats if gun not in ('上県郡', '下県郡', '壱岐郡')]}
parts, centre = {}, {}
for k, fs in groups.items():
    g = unary_union(fs).buffer(0)
    parts[k] = [q for q in (g.geoms if hasattr(g, 'geoms') else [g]) if q.area > 1e-7]
    centre[k] = g.centroid.coords[0]


def proj(p, c0):
    sc, asp, rot, tx, ty = p
    c, sn = np.cos(np.radians(rot)), np.sin(np.radians(rot))

    def f(x, y, z=None):
        X = (np.asarray(x) - c0[0]) * sc
        Y = -(np.asarray(y) - c0[1]) * sc * asp
        return X * c - Y * sn + tx, X * sn + Y * c + ty
    return f


def raster(ps, f):
    img = Image.new('1', (W, H), 0)
    dd = ImageDraw.Draw(img)
    for g in ps:
        q = stransform(f, g)
        dd.polygon(list(q.exterior.coords), fill=1)
        for r in q.interiors:
            dd.polygon(list(r.coords), fill=0)
    return np.asarray(img)


def iou(m, t):
    return (m & t).sum() / max(1, (m | t).sum())


def path_d(ps, f):
    return ''.join('M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in r.coords) + 'Z'
                   for g in ps for q in [stransform(f, g.simplify(0.0003))] for r in [q.exterior, *q.interiors])


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'fit':
        P = {}
        for k in ('main', 'tsushima', 'iki'):
            t = ink & regions[k]
            ys, xs = np.nonzero(t)
            gx0, gy0, gx1, gy1 = unary_union(parts[k]).bounds
            s0 = max((xs.max() - xs.min()) / (gx1 - gx0), (ys.max() - ys.min()) / (gy1 - gy0) / 1.2)
            loss = lambda p, k=k, t=t: 1 - iou(raster(parts[k], proj(p, centre[k])) & regions[k], t)
            best = None
            for rot in range(-40, 41, 5):
                for sc in (0.8 * s0, s0, 1.2 * s0):
                    p0 = [sc, 1.2, rot, xs.mean(), ys.mean()]
                    l = loss(p0)
                    if best is None or l < best[0]:
                        best = (l, p0)
            r = optimize.minimize(loss, best[1], method='Nelder-Mead', options={'maxiter': 2000, 'xatol': 1e-3, 'fatol': 1e-8})
            P[k] = list(r.x)
            print(k, 'IoU %.4f' % (1 - r.fun))
        json.dump(P, open(PAR, 'w'))
    P = json.load(open(PAR))
    fs = {k: proj(P[k], centre[k]) for k in P}
    m = np.zeros_like(ink)
    for k in fs:
        mk = raster(parts[k], fs[k])
        print(k, 'region IoU %.4f' % iou(mk & regions[k], ink & regions[k]))
        m |= mk
    print('whole IoU %.4f' % iou(m | frame_px, ink | frame_px))
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<path fill="#000000" fill-rule="evenodd" stroke="#000000" stroke-width="1" stroke-linejoin="round" d="{"".join(path_d(parts[k], fs[k]) for k in fs)}"/>',
         f'<path fill="none" stroke="{FRAME_COL}" stroke-width="1" d="M' + ' '.join(f'{x},{y}' for x, y in IKI_BOX)
         + 'M' + ' '.join(f'{x},{y}' for x, y in STEP) + '"/>', '</svg>']
    open(OUT, 'w', encoding='utf8').write('\n'.join(o) + '\n')
    print('wrote', OUT)
