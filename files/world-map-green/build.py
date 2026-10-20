"""Rebuild File:World map green.png (a plain green world map in the Robinson projection, derived from the 2005 PNG of
'A large blank world map with oceans marked in blue', with borders and small islands removed and the seas cropped)
from Natural Earth 10m land (public domain): Robinson, scales and offset fitted to the PNG's land mask;
the big lakes the PNG shows as water (chosen by its pixels) cut out, and the Caspian filled in as the PNG has it; Antarctica
left out and islands below a minimum projected area dropped, as in the PNG; filled in the PNG's green. Run from the
repo root; `fit` refits."""
import json, sys
import numpy as np
from PIL import Image, ImageDraw
from pyproj import Transformer
from scipy import optimize
from shapely.geometry import shape
from shapely.ops import unary_union, transform as stransform

PNG = 'data_lake/downloads/world-map-green/World map green.png'
NE = 'data_lake/downloads/natural-earth/ne_10m_land.geojson'
OUT = 'files/world-map-green/World map green.svg'
PAR = 'files/world-map-green/params.json'
GREEN = '#1f6023'
MIN_AREA = 120  # px², at the PNG's scale: smaller islands are left out, as in the PNG

a = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
H, W = a.shape[:2]
land_px = a.max(2) < 200
T = Transformer.from_crs('EPSG:4326', '+proj=robin +lon_0=0 +datum=WGS84', always_xy=True)
fc = json.load(open(NE, encoding='utf8'))
from shapely.geometry import Polygon
lakes = {f['properties'].get('name'): shape(f['geometry']).buffer(0)
         for f in json.load(open('data_lake/downloads/natural-earth/ne_10m_lakes.geojson', encoding='utf8'))['features']
         if shape(f['geometry']).area > 2 and f['properties'].get('name')}
rob = lambda x, y, z=None: T.transform(x, y)


def build_parts(water):
    """land without Antarctica, the Caspian filled in (the PNG shows it as land), the named lakes cut out"""
    cut = unary_union([lakes[n] for n in water]) if water else None
    out = []
    for f in fc['features']:
        g = shape(f['geometry'])
        for q in (g.geoms if hasattr(g, 'geoms') else [g]):
            if q.bounds[3] > -60:
                holes = [r for r in q.interiors if not (45 < Polygon(r).centroid.x < 56 and 36 < Polygon(r).centroid.y < 48)]
                q = Polygon(q.exterior, holes)
                if cut is not None:
                    q = q.difference(cut).buffer(0)
                for qq in (q.geoms if hasattr(q, 'geoms') else [q]):
                    if not qq.is_empty:
                        out.append(stransform(rob, qq))
    return out


parts = build_parts([])


def place(p):
    sx, sy, tx, ty = p
    return lambda x, y, z=None: (np.asarray(x) * sx + tx, -np.asarray(y) * sy + ty)


def raster(f, min_area=0, ds=1):
    img = Image.new('1', (W // ds, H // ds), 0); d = ImageDraw.Draw(img)
    for q in parts:
        qq = stransform(f, q)
        if qq.area < min_area:
            continue
        d.polygon([(x / ds, y / ds) for x, y in qq.exterior.coords], fill=1)
        for r in qq.interiors:
            d.polygon([(x / ds, y / ds) for x, y in r.coords], fill=0)
    return np.asarray(img)


def loss(p, ds=4):
    m = raster(place(p), MIN_AREA, ds)
    t = land_px[::ds, ::ds][:m.shape[0], :m.shape[1]]
    return 1 - (m & t).sum() / (m | t).sum()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'fit':
        ys, xs = np.nonzero(land_px)
        allb = unary_union(parts).bounds
        s0 = (xs.max() - xs.min()) / (allb[2] - allb[0])
        p0 = [s0, s0, xs.min() - allb[0] * s0, ys.min() + allb[3] * s0]
        r = optimize.minimize(loss, p0, method='Nelder-Mead', options={'maxiter': 600, 'xatol': 1e-9, 'fatol': 1e-7})
        r2 = optimize.minimize(lambda p: loss(p, 2), r.x, method='Nelder-Mead', options={'maxiter': 300, 'xatol': 1e-9, 'fatol': 1e-7})
        f = place(r2.x)
        water = []  # the big lakes the PNG shows as water (most of their pixels white)
        for n, g in lakes.items():
            if 'Caspian' in n:
                continue
            img = Image.new('1', (W, H), 0); dr = ImageDraw.Draw(img)
            for q in ((g.geoms if hasattr(g, 'geoms') else [g])):
                dr.polygon(list(stransform(f, stransform(rob, q)).exterior.coords), fill=1)
            m = np.asarray(img)
            if m.sum() > 20 and (~land_px & m).sum() > 0.5 * m.sum():
                water.append(n)
        json.dump({'p': list(r2.x), 'iou': 1 - r2.fun, 'water': sorted(water)}, open(PAR, 'w'), indent=1)
    P = json.load(open(PAR))
    f = place(P['p'])
    parts = build_parts(P['water'])
    print('lakes as water:', ', '.join(P['water']))
    print('land IoU %.3f' % P['iou'])
    d = []
    for q in parts:
        qq = stransform(f, q)
        if qq.area < MIN_AREA:
            continue
        qq = qq.simplify(0.6)
        d.append(''.join('M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in rr.coords) + 'Z' for rr in [qq.exterior, *qq.interiors]))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
           f'<rect width="{W}" height="{H}" fill="#ffffff"/>\n<path fill="{GREEN}" fill-rule="evenodd" d="{"".join(d)}"/>\n</svg>\n')
    open(OUT, 'w', encoding='utf8').write(svg)
    print('wrote', OUT, len(d), 'land masses')
