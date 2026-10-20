"""Rebuild File:Japan Chubu Region large.png from Natural Earth 10m admin-1 data (PD): Japan's 47 prefectures in a
Lambert conformal conic fitted to the PNG's land mask, the nine Chūbu prefectures in the PNG's dark green, the rest
in its light green, the southern Kuril Islands (claimed by Japan) in its pink, and Okinawa refitted into the PNG's
inset, whose rounded black frame is measured. Black coast, thin prefecture borders.
usage (repo root): python files/japan-chubu-region/build.py [fit]"""
import json, sys
import numpy as np
from PIL import Image, ImageDraw
from pyproj import Transformer
from scipy import optimize
from shapely.geometry import shape, box
from shapely.ops import unary_union, transform as stransform

PNG = 'data_lake/downloads/japan-chubu-region/Japan Chubu Region large.png'
OUT = 'files/japan-chubu-region/Japan Chubu Region large.svg'
PAR = 'files/japan-chubu-region/projection.json'
NE = 'data_lake/downloads/natural-earth/ne_10m_admin_1_states_provinces.geojson'
LIGHT, DARK, PINK = '#94cf97', '#5f8f61', '#cf7d7d'
CHUBU = {'Niigata', 'Toyama', 'Ishikawa', 'Fukui', 'Yamanashi', 'Nagano', 'Gifu', 'Shizuoka', 'Aichi'}
INSET = (792, 1200)  # left and top of the inset frame (rounded corner, radius 200)

im = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
H, W = im.shape[:2]
near = lambda c: np.abs(im - [int(c[i:i + 2], 16) for i in (1, 3, 5)]).sum(2) < 30
land_px = near(LIGHT) | near(DARK) | near(PINK)
yy, xx = np.mgrid[:H, :W]
in_inset = (xx > INSET[0] + 4) & (yy > INSET[1] + 4)

fc = json.load(open(NE, encoding='utf8'))
pref = {f['properties']['name']: shape(f['geometry']).buffer(0) for f in fc['features'] if f['properties']['adm0_a3'] == 'JPN'}
kuril_box = box(145.0, 43.2, 149.6, 45.7)
kurils = unary_union([shape(f['geometry']).intersection(kuril_box) for f in fc['features']
                      if f['properties']['adm0_a3'] == 'RUS' and shape(f['geometry']).intersects(kuril_box)])
main = {k: v for k, v in pref.items() if k != 'Okinawa'}
okinawa = pref['Okinawa'].intersection(box(122, 23, 130, 28))  # the inset leaves out the Daito Islands


def projector(p):
    lon0, lat1, lat2, s, tx, ty = p
    t = Transformer.from_crs('EPSG:4326', f'+proj=lcc +lon_0={lon0} +lat_1={float(np.clip(lat1, 5, 85))} '
                             f'+lat_2={float(np.clip(lat2, 5, 85))} +lat_0=36 +ellps=WGS84 +units=m', always_xy=True)

    def f(x, y, z=None):
        X, Y = t.transform(x, y)
        return np.asarray(X) * s / 1e4 + tx, -np.asarray(Y) * s / 1e4 + ty
    return f


def polys(g):
    return [q for q in (g.geoms if hasattr(g, 'geoms') else [g]) if q.geom_type == 'Polygon']


def raster(geoms, f):
    img = Image.new('1', (W, H), 0)
    d = ImageDraw.Draw(img)
    for g in geoms:
        for q in polys(stransform(f, g)):
            d.polygon(list(q.exterior.coords), fill=1)
            for r in q.interiors:
                d.polygon(list(r.coords), fill=0)
    return np.asarray(img)


def iou(m, region):
    t = land_px & region
    return ((m & t).sum()) / max(1, ((m & region) | t).sum())


def loss_main(p):
    return 1 - iou(raster(list(main.values()) + [kurils], projector(p)), ~in_inset)


def inset_proj(p, q):
    f = projector(p)
    s, dx, dy = q
    return lambda x, y, z=None: (lambda X, Y: (X * s + dx, Y * s + dy))(*f(x, y))


def loss_inset(p, q):
    return 1 - iou(raster([okinawa], inset_proj(p, q)), in_inset)


def path_d(g, f):
    return ''.join('M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in r.coords) + 'Z'
                   for q in polys(stransform(f, g.simplify(0.002))) for r in [q.exterior, *q.interiors])


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'fit':
        # start from Hokkaido's and Kyushu's extents in the PNG, then Nelder-Mead
        p0 = [137.0, 33.0, 43.0, 4.2, 900.0, 830.0]
        best = None
        for s in np.linspace(3.0, 5.6, 14):
            for tx in np.linspace(600, 1100, 11):
                for ty in np.linspace(600, 1100, 11):
                    l = loss_main([137.0, 33.0, 43.0, s, tx, ty])
                    if best is None or l < best[0]:
                        best = (l, [137.0, 33.0, 43.0, s, tx, ty])
        r = optimize.minimize(loss_main, best[1], method='Nelder-Mead', options={'maxiter': 800, 'xatol': 1e-3, 'fatol': 1e-7})
        p = list(r.x)
        f = projector(p)
        cx, cy = f(*okinawa.centroid.coords[0])
        ys, xs = np.nonzero(land_px & in_inset)
        q0 = [1.0, xs.mean() - float(cx), ys.mean() - float(cy)]
        rq = optimize.minimize(lambda q: loss_inset(p, q), q0, method='Nelder-Mead', options={'maxiter': 600})
        json.dump({'main': p, 'inset': list(rq.x)}, open(PAR, 'w'))
    P = json.load(open(PAR))
    f, fi = projector(P['main']), inset_proj(P['main'], P['inset'])
    print('main land IoU %.4f, inset IoU %.4f' % (1 - loss_main(P['main']), 1 - loss_inset(P['main'], P['inset'])))
    light = [g for k, g in main.items() if k not in CHUBU]
    dark = [g for k, g in main.items() if k in CHUBU]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         '<g stroke="#000000" stroke-width="0.8" stroke-linejoin="round">',
         f'<path fill="{LIGHT}" d="{"".join(path_d(g, f) for g in light)}{path_d(okinawa, fi)}"/>',
         f'<path fill="{DARK}" d="{"".join(path_d(g, f) for g in dark)}"/>',
         f'<path fill="{PINK}" d="{path_d(kurils, f)}"/>', '</g>',
         f'<path fill="none" stroke="#000000" stroke-width="2" stroke-linejoin="round" d="'
         f'{"".join(path_d(g, f) for g in [unary_union(list(main.values())), kurils])}{path_d(okinawa, fi)}"/>',
         f'<path fill="none" stroke="#000000" stroke-width="3" d="M{INSET[0]},{H} V{INSET[1] + 200} '
         f'A200,200 0 0 1 {INSET[0] + 200},{INSET[1]} H{W}"/>', '</svg>']
    open(OUT, 'w', encoding='utf8').write('\n'.join(o) + '\n')
    print('wrote', OUT)
