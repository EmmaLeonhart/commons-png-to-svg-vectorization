"""Rebuild File:W-asia.png (a locator map of Western Asia, 155x149) from Natural Earth 10m admin-1 data (public domain),
merged per country: an equirectangular projection fitted to the PNG's land mask
(IoU 0.87: the PNG's coastlines are generalised by hand; Mercator fits worse), the countries the PNG paints green (read off the PNG;
the loose fit makes a pixel vote unreliable) green, Sinai in its light green, the rest grey, white sea and white country borders. Run from the repo root; `fit`
refits."""
import json, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import optimize
from shapely.geometry import shape, box
from shapely.ops import unary_union, transform as stransform

PNG = 'data_lake/downloads/w-asia/W-asia.png'
NE = 'data_lake/downloads/natural-earth/ne_10m_admin_1_states_provinces.geojson'
OUT = 'files/w-asia/W-asia.svg'
PAR = 'files/w-asia/params.json'
GREEN, GREY, SEA, LIGHT = '#00e000', '#ccc2cb', '#fefefe', '#c0e0c0'
GREEN_SET = ['TUR', 'GEO', 'ARM', 'AZE', 'CYP', 'CYN', 'SYR', 'LBN', 'ISR', 'PSX', 'JOR', 'IRQ', 'IRN', 'SAU', 'KWT', 'BHR',
             'QAT', 'ARE', 'OMN', 'YEM']
SINAI = ("Shamal Sina'", "Janub Sina'")  # Egyptian governorates (Natural Earth names), drawn light green
VIEW = box(20, 0, 80, 50)

a = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
H, W = a.shape[:2]
land_px = np.abs(a - [254, 254, 254]).sum(2) > 30
green_px = np.abs(a - [0, 224, 0]).sum(2) < 40

fc = json.load(open(NE, encoding='utf8'))
by = {}
for f in fc['features']:
    g = shape(f['geometry'])
    if g.intersects(VIEW):
        by.setdefault(f['properties']['adm0_a3'], []).append(g.intersection(VIEW))
countries = {k: unary_union(v).buffer(0) for k, v in by.items()}


def proj(p):
    sx, sy, tx, ty = p
    return lambda x, y, z=None: (np.asarray(x) * sx + tx, -np.asarray(y) * sy + ty)


def polys(g):
    return [q for q in (g.geoms if hasattr(g, 'geoms') else [g]) if q.geom_type == 'Polygon']


def raster(gs, f):
    img = Image.new('1', (W, H), 0); d = ImageDraw.Draw(img)
    for g in gs:
        for q in polys(stransform(f, g)):
            d.polygon(list(q.exterior.coords), fill=1)
            for r in q.interiors:
                d.polygon(list(r.coords), fill=0)
    return np.asarray(img)


def loss(p):
    m = raster(countries.values(), proj(p))
    return 1 - (m & land_px).sum() / (m | land_px).sum()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'fit':
        best = None
        for s in np.linspace(2.0, 3.6, 9):
            for lon0 in np.linspace(25, 40, 7):
                for lat0 in np.linspace(38, 48, 6):
                    p = [s, s, -lon0 * s, lat0 * s]
                    l = loss(p)
                    if best is None or l < best[0]:
                        best = (l, p)
        r = optimize.minimize(loss, best[1], method='Nelder-Mead', options={'maxiter': 1500, 'xatol': 1e-4, 'fatol': 1e-7})
        f = proj(r.x)
        json.dump({'p': list(r.x), 'iou': 1 - r.fun}, open(PAR, 'w'), indent=1)
    P = json.load(open(PAR))
    f = proj(P['p'])
    print('land IoU %.3f' % P['iou'])

    def d_of(g):
        return ''.join('M' + ' '.join(f'{x:.2f},{y:.2f}' for x, y in r.coords) + 'Z'
                       for q in polys(stransform(f, g.simplify(0.02))) for r in [q.exterior, *q.interiors])
    grey_d = ''.join(d_of(g) for k, g in countries.items() if k not in GREEN_SET)
    green_d = ''.join(d_of(g) for k, g in countries.items() if k in GREEN_SET)
    sinai = unary_union([shape(f_['geometry']) for f_ in fc['features'] if f_['properties']['adm0_a3'] == 'EGY'
                         and f_['properties']['name'] in SINAI]).buffer(0)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
           f'<rect width="{W}" height="{H}" fill="{SEA}"/>\n'
           f'<path d="{grey_d}" fill="{GREY}" stroke="#ffffff" stroke-width="0.6" stroke-linejoin="round"/>\n'
           f'<path d="{d_of(sinai)}" fill="{LIGHT}" stroke="#ffffff" stroke-width="0.6" stroke-linejoin="round"/>\n'
           f'<path d="{green_d}" fill="{GREEN}" stroke="#ffffff" stroke-width="0.6" stroke-linejoin="round"/>\n</svg>\n')
    open(OUT, 'w', encoding='utf8').write(svg)
    print('wrote', OUT)
