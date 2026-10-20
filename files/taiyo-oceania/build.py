"""Rebuild File:大洋.png (a map of Oceania cut from a world map centred in the Pacific) from Natural Earth 10m land
(public domain), in a projection (TAIYO_PROJ, default the best of the fit) with its scales and offset fitted to the
PNG's land mask. The PNG's base map draws New Zealand enlarged (about 11 px per degree of longitude against 7.5 for
Australia and Borneo), so New Zealand is left out of the fit and the real outline replaces it; each land
polygon filled with the colour of the PNG's nearest land (Oceania green, Southeast Asia mauve); polygons
too small to show in the PNG left out. Run from the repo root; `fit` refits."""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
from pyproj import Transformer
from scipy import optimize, ndimage
from shapely.geometry import shape, box
from shapely.ops import transform as stransform

PNG = 'data_lake/downloads/taiyo-oceania/大洋.png'
NE = 'data_lake/downloads/natural-earth/ne_10m_land.geojson'
OUT = 'files/taiyo-oceania/大洋.svg'
PAR = 'files/taiyo-oceania/params.json'
SEA, COLS = '#e6ffff', ['#1e411d', '#c4b3c2']
PROJ = os.environ.get('TAIYO_PROJ', 'robin')
MIN_AREA = 0.15  # px²: keeps the Pacific islets the PNG marks; smaller specks dropped

a = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
H, W = a.shape[:2]
land_px = (np.abs(a - [230, 255, 255]).sum(2) > 30) & (a.min(2) < 250)
known = np.ones((H, W), bool)
known[455:, 440:] = False  # New Zealand, drawn enlarged in the PNG's base map
AUS_BOX = (140, 447, 266, 512)  # the PNG's mainland Australia, x0 x1 y0 y1
fc = json.load(open(NE, encoding='utf8'))
geo = [q for f in fc['features'] for g in [shape(f['geometry'])]
       for q in (g.geoms if hasattr(g, 'geoms') else [g])]


def parts(lon0):
    T = Transformer.from_crs('EPSG:4326', f'+proj={PROJ} +lon_0={lon0} +datum=WGS84', always_xy=True)
    win = box(lon0 - 70, -60, lon0 + 50, 30)  # around the PNG's window; avoids the antimeridian cut
    out = []
    for q in geo:
        for s in (-360, 0, 360):
            qq = stransform(lambda x, y, z=None: (np.asarray(x) + s, y), q) if s else q
            if qq.intersects(win):
                c = qq.intersection(win)
                for p in (c.geoms if hasattr(c, 'geoms') else [c]):
                    if p.geom_type == 'Polygon' and not p.is_empty:
                        out.append(stransform(lambda x, y, z=None: T.transform(x, y), p))
    return out


def place(p):
    sx, sy, tx, ty = p
    return lambda x, y, z=None: (np.asarray(x) * sx + tx, -np.asarray(y) * sy + ty)


def raster(ps, f, ds=1):
    img = Image.new('1', (W // ds, H // ds), 0); d = ImageDraw.Draw(img)
    for q in ps:
        qq = stransform(f, q)
        d.polygon([(x / ds, y / ds) for x, y in qq.exterior.coords], fill=1)
        for r in qq.interiors:
            d.polygon([(x / ds, y / ds) for x, y in r.coords], fill=0)
    return np.asarray(img)


def loss(p, ps, ds=2):
    m = raster(ps, place(p), ds)
    t = land_px[::ds, ::ds][:m.shape[0], :m.shape[1]]; k = known[::ds, ::ds][:m.shape[0], :m.shape[1]]
    return 1 - (m & t & k).sum() / ((m | t) & k).sum()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'fit':
        best = None
        for proj in ('robin', 'mill', 'merc', 'eqc'):
            PROJ = proj
            ps = [q for q in parts(150) if q.area > 1e9]
            aus = max(ps, key=lambda q: q.area if q.centroid.y < -1e6 else 0)  # Australia: largest land well south of the equator
            bx0, by0, bx1, by1 = aus.bounds
            x0, x1, y0, y1 = AUS_BOX
            sx, sy = (x1 - x0) / (bx1 - bx0), (y1 - y0) / (by1 - by0)
            p0 = [sx, sy, x0 - bx0 * sx, y0 + by1 * sy]
            r = optimize.minimize(loss, p0, args=(ps, 2), method='Nelder-Mead', options={'maxiter': 800})
            print(proj, 'from Australia %.3f, fitted %.3f' % (1 - loss(p0, ps), 1 - r.fun), flush=True)
            if best is None or r.fun < best[0]:
                best = (r.fun, proj, list(r.x))
        _, PROJ, p = best
        ps = parts(150)
        r = optimize.minimize(loss, p, args=(ps, 1), method='Nelder-Mead', options={'maxiter': 600, 'xatol': 1e-9})
        json.dump({'proj': PROJ, 'lon0': 150.0, 'p': list(map(float, r.x)), 'iou': 1 - r.fun}, open(PAR, 'w'), indent=1)
    P = json.load(open(PAR))
    PROJ = P.get('proj', PROJ)
    f = place(P['p'])
    print('%s lon_0 %.0f, land IoU %.3f (New Zealand excluded)' % (PROJ, P['lon0'], P['iou']))
    paths = {c: [] for c in COLS}
    kinds = np.stack([np.abs(a - [int(c[i:i + 2], 16) for i in (1, 3, 5)]).sum(2) < 30 for c in COLS])
    _, (iy, ix) = ndimage.distance_transform_edt(~kinds.any(0), return_indices=True)
    nearest = kinds[1][iy, ix].astype(int)
    frame = box(0, 0, W, H)
    for q in parts(P['lon0']):
        qq = stransform(f, q).intersection(frame)
        if qq.is_empty or qq.area < MIN_AREA:
            continue
        m = raster([q], f)
        ys, xs = np.nonzero(m)
        if not len(ys):
            c = qq.representative_point()
            ys, xs = np.array([min(int(c.y), H - 1)]), np.array([min(int(c.x), W - 1)])
        # each pixel's colour is that of the nearest land in the PNG, so islands the PNG's generalised base map
        # places elsewhere (New Zealand, Tasmania) still take their region's colour
        col = COLS[np.bincount(nearest[ys, xs], minlength=2).argmax()]
        for g in (qq.geoms if hasattr(qq, 'geoms') else [qq]):
            if g.geom_type == 'Polygon':
                g = g.simplify(0.3)
                paths[col].append(''.join('M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in rr.coords[:-1]) + 'Z'
                                          for rr in [g.exterior, *g.interiors]))
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="{SEA}"/>']
    o += [f'<path fill="{c}" fill-rule="evenodd" d="{"".join(d)}"/>' for c, d in paths.items() if d]
    open(OUT, 'w', encoding='utf8').write('\n'.join(o + ['</svg>']) + '\n')
    print('wrote', OUT, {c: len(d) for c, d in paths.items()})
