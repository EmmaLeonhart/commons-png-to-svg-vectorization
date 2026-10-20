"""Rebuild File:Shadow picture of Shimane prefecture.png from MLIT 国土数値情報 N03 (2024). The PNG puts the Oki Islands
(隠岐郡) in a framed inset at the top left and Takeshima (in N03 part of 隠岐の島町; here the part north of 37°N) in a
small framed box in its corner, so a single fit fails (tools/shadow_rotfit.py: IoU 0.895). The rest of the prefecture,
Oki and Takeshima are each fitted to the ink in their own region with scale, aspect, rotation and offset; the frames
(two greys) are measured, and Lake Shinji and Nakaumi are cut out (MLIT 国土数値情報 W09 lakes of at least 0.0005 square
degrees), as the PNG shows them as holes. Run from the repo root; `fit` refits."""
import json, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import optimize
from shapely.geometry import shape
from shapely.ops import unary_union, transform as stransform


SRC = 'data_lake/downloads/shadow-shimane/Shadow picture of Shimane prefecture.png'
OUT = 'files/shadow-shimane/Shadow picture of Shimane prefecture.svg'
PAR = 'files/shadow-shimane/projection.json'
OKI_FRAME = [(164.5, 24), (164.5, 99.5), (69.5, 169.5), (19, 169.5)]  # #202020
TAKE_FRAME = [(62.5, 26), (62.5, 58.5), (21, 58.5)]  # #626262
OKI_REGION = [(0, 0), (164.5, 0), (164.5, 99.5), (69.5, 169.5), (0, 169.5)]
TAKE_REGION = [(0, 0), (62.5, 0), (62.5, 58.5), (0, 58.5)]

im = Image.open(SRC).convert('RGBA')
ink = np.asarray(Image.alpha_composite(Image.new('RGBA', im.size, 'white'), im).convert('L')) < 128
H, W = ink.shape


def poly_mask(pts):
    img = Image.new('1', (W, H), 0)
    ImageDraw.Draw(img).polygon(pts, fill=1)
    return np.asarray(img)


fimg = Image.new('1', (W, H), 0)
d = ImageDraw.Draw(fimg)
d.line(OKI_FRAME, fill=1, width=3); d.line(TAKE_FRAME, fill=1, width=3)
frame_px = np.asarray(fimg)
regions = {'takeshima': poly_mask(TAKE_REGION) & ~frame_px}
regions['oki'] = poly_mask(OKI_REGION) & ~regions['takeshima'] & ~frame_px
regions['main'] = ~(regions['oki'] | regions['takeshima']) & ~frame_px

sys.path.insert(0, 'tools')
from n03_prefecture_svg import load  # noqa: E402
import io, zipfile, shapefile
from shapely.geometry import box
feats = [(f['properties'].get('N03_003') or '', shape(f['geometry'])) for f in load(32)['features']]
z = zipfile.ZipFile('data_lake/downloads/w09-lakes/W09-05_GML.zip')
rd = shapefile.Reader(shp=io.BytesIO(z.read('W09-05-g_Lake.shp')), shx=io.BytesIO(z.read('W09-05-g_Lake.shx')),
                      dbf=io.BytesIO(z.read('W09-05-g_Lake.dbf')), encoding='cp932')
lakes = unary_union([g for g in (shape(r.shape.__geo_interface__).buffer(0) for r in rd.iterShapeRecords())
                     if g.area >= 0.0005 and g.intersects(box(131.5, 34.9, 133.5, 35.7))])
oki_all = unary_union([g for gun, g in feats if gun == '隠岐郡']).buffer(0)
groups = {'main': [unary_union([g for gun, g in feats if gun != '隠岐郡']).buffer(0).difference(lakes)],
          'oki': [oki_all.difference(box(130, 37, 133, 38))], 'takeshima': [oki_all.intersection(box(130, 37, 133, 38))]}
parts, centre = {}, {}
for k, fs in groups.items():
    g = unary_union(fs).buffer(0)
    parts[k] = [q for q in (g.geoms if hasattr(g, 'geoms') else [g]) if q.area > 1e-9]
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
        for k in ('main', 'oki', 'takeshima'):
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
         f'<path fill="#000000" fill-rule="evenodd" d="{"".join(path_d(parts[k], fs[k]) for k in fs)}"/>',
         *[f'<path fill="none" stroke="{c}" stroke-width="1" d="M' + ' '.join(f'{x},{y}' for x, y in fr) + '"/>'
           for c, fr in (('#202020', OKI_FRAME), ('#626262', TAKE_FRAME))], '</svg>']
    open(OUT, 'w', encoding='utf8').write('\n'.join(o) + '\n')
    print('wrote', OUT)
