"""Rebuild File:Greater Macedonia.png from boundary data: Natural Earth 10m land and country borders (PD) in a Lambert
conformal conic fitted to the PNG's land mask, and the region of Macedonia as the union of the units the PNG shows
blue: North Macedonia, Bulgaria's Blagoevgrad province (Natural Earth admin-1) and the Greek municipalities
(geoBoundaries GRC ADM3, CC BY 4.0, EuroGeographics). Colours are the PNG's: grey land, white sea and borders, blue
region with a white outline. usage (repo root): python files/greater-macedonia/build.py [fit]"""
import json, sys
import numpy as np
from PIL import Image, ImageDraw
from pyproj import Transformer
from scipy import optimize
from shapely.geometry import shape, box
from shapely.ops import transform as stransform, unary_union

PNG = 'data_lake/downloads/greater-macedonia/Greater Macedonia.png'
OUT = 'files/greater-macedonia/Greater Macedonia.svg'
PAR = 'files/greater-macedonia/projection.json'
NE = 'data_lake/downloads/natural-earth/'
GB = 'data_lake/downloads/geoboundaries/geoBoundaries-GRC-ADM3.geojson'
LAND, SEA, BLUE = '#cdc3cc', '#ffffff', '#4d6df3'
BBOX = box(5, 30, 40, 52)

im = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
H, W = im.shape[:2]
land_px = im.sum(2) < 700                        # grey or blue land (white sea and borders excluded)
blue_px = (im[..., 2] > 200) & (im[..., 0] < 120)


def load(path, keep=lambda p: True):
    fc = json.load(open(path, encoding='utf8'))
    return [(f['properties'], shape(f['geometry'])) for f in fc['features']
            if keep(f['properties']) and shape(f['geometry']).intersects(BBOX)]


land = [g.intersection(BBOX) for _, g in load(NE + 'ne_10m_land.geojson')]
borders = [g.intersection(BBOX) for _, g in load(NE + 'ne_10m_admin_0_boundary_lines_land.geojson')]
adm1 = load(NE + 'ne_10m_admin_1_states_provinces.geojson', lambda p: p['adm0_a3'] in ('MKD', 'BGR'))
units = [(p['adm0_a3'] + ' ' + p['name'], g) for p, g in adm1] + [('GRC ' + p['shapeName'], g) for p, g in load(GB)]


def projector(p):
    lon0, lat1, lat2, s, tx, ty = p
    lat1, lat2 = float(np.clip(lat1, 5, 85)), float(np.clip(lat2, 5, 85))
    t = Transformer.from_crs('EPSG:4326', f'+proj=lcc +lon_0={lon0} +lat_1={lat1} +lat_2={lat2} +lat_0=40 '
                             '+ellps=WGS84 +units=m', always_xy=True)

    def f(x, y, z=None):
        X, Y = t.transform(x, y)
        return np.asarray(X) * s / 1e4 + tx, -np.asarray(Y) * s / 1e4 + ty
    return f


def polys(g):
    return [q for q in (g.geoms if hasattr(g, 'geoms') else [g]) if q.geom_type == 'Polygon']


def raster(geoms, f, scale=1):
    img = Image.new('1', (W * scale, H * scale), 0)
    d = ImageDraw.Draw(img)
    for g in geoms:
        for q in polys(stransform(f, g)):
            d.polygon([(x * scale, y * scale) for x, y in q.exterior.coords], fill=1)
            for r in q.interiors:
                d.polygon([(x * scale, y * scale) for x, y in r.coords], fill=0)
    return np.asarray(img)


def loss(p):
    m = raster(land, projector(p))
    return 1 - (m & land_px).sum() / (m | land_px).sum()


def path_d(g, f, close=True):
    out = []
    g = stransform(f, g)
    for q in (g.geoms if hasattr(g, 'geoms') else [g]):
        rings = [q.exterior, *q.interiors] if q.geom_type == 'Polygon' else [q]
        for r in rings:
            c = np.asarray(r.coords)
            if len(c) >= 2:
                out.append('M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in c) + ('Z' if close else ''))
    return ''.join(out)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'fit':
        p0 = [22.0, 37.0, 45.0, 2.9, 200.0, 169.0]
        # scale and offset first (projection fixed), then everything
        r = optimize.minimize(lambda q: loss(p0[:3] + list(q)), p0[3:], method='Nelder-Mead',
                              options={'maxiter': 400, 'xatol': 1e-3, 'fatol': 1e-6})
        r = optimize.minimize(loss, p0[:3] + list(r.x), method='Nelder-Mead',
                              options={'maxiter': 1200, 'xatol': 1e-3, 'fatol': 1e-6})
        json.dump(list(r.x), open(PAR, 'w'))
        print('fitted land IoU %.4f' % (1 - r.fun), [round(v, 4) for v in r.x])
    p = json.load(open(PAR))
    f = projector(p)
    print('land IoU %.4f' % (1 - loss(p)))
    # the region of Macedonia as usually drawn: North Macedonia, Bulgaria's Blagoevgrad (Pirin Macedonia), and Greek
    # Macedonia = the West and Central Macedonia regions, Mount Athos, and East Macedonia west of the Nestos (Kavala,
    # Drama and Thasos municipalities); a colour threshold on the PNG picked up neighbours where the fit is loose
    adm2 = {p['shapeName']: g for p, g in load(GB.replace('ADM3', 'ADM2'))}
    whole = unary_union([adm2['Dytikis Makedonias'], adm2['Kentrikis Makedonias'], adm2['Agion Oros']])
    east = adm2['Anatolikis Makedonias kai Thr*']
    region = [(n, g) for n, g in units if n.startswith('MKD') or n == 'BGR Blagoevgrad']
    for n, g in units:
        if n.startswith('GRC'):
            c = g.representative_point()
            if whole.contains(c) or (east.contains(c) and c.x < 24.8):
                region.append((n, g))
    m = raster([g for _, g in region], f)
    print(len(region), 'units; blue agreement %.3f' % ((m & blue_px).sum() / (m | blue_px).sum()))
    reg = unary_union([g for _, g in region]).buffer(0)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="{SEA}"/>',
         f'<path d="{"".join(path_d(g, f) for g in land)}" fill="{LAND}" stroke="{SEA}" stroke-width="1"/>',
         f'<path d="{"".join(path_d(g, f, False) for g in borders)}" fill="none" stroke="{SEA}" stroke-width="1.6" '
         'stroke-linejoin="round"/>',
         f'<path d="{path_d(reg.intersection(unary_union(land)), f)}" fill="{BLUE}"/>',
         f'<path d="{"".join(path_d(g, f, False) for g in borders)}" fill="none" stroke="{SEA}" stroke-width="1.6" '
         'stroke-linejoin="round"/>',
         '</svg>']
    open(OUT, 'w', encoding='utf8').write('\n'.join(o) + '\n')
    print('wrote', OUT)
