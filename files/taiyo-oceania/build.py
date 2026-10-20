"""Rebuild File:大洋.png (a map of Oceania cut from a world map centred in the Pacific) from Natural Earth 10m land
(public domain): Robinson with its central meridian, scales and offset fitted to the PNG's land mask; each land
polygon filled with the colour most of its pixels have in the PNG (Oceania green, Southeast Asia mauve); polygons
too small to show in the PNG left out. Run from the repo root; `fit` refits."""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
from pyproj import Transformer
from scipy import optimize
from shapely.geometry import shape, box
from shapely.ops import transform as stransform

PNG = 'data_lake/downloads/taiyo-oceania/大洋.png'
NE = 'data_lake/downloads/natural-earth/ne_10m_land.geojson'
OUT = 'files/taiyo-oceania/大洋.svg'
PAR = 'files/taiyo-oceania/params.json'
SEA, COLS = '#e6ffff', ['#1e411d', '#c4b3c2']
PROJ = os.environ.get('TAIYO_PROJ', 'robin')
MIN_AREA = 1.5  # px²: smaller islets do not show in the PNG

a = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
H, W = a.shape[:2]
land_px = (np.abs(a - [230, 255, 255]).sum(2) > 30) & (a.min(2) < 250)
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
    t = land_px[::ds, ::ds][:m.shape[0], :m.shape[1]]
    return 1 - (m & t).sum() / (m | t).sum()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'fit':
        best = None
        for lon0 in (130, 140, 150, 160, 170):
            ps = parts(lon0)
            ps = [q for q in ps if q.area > 1e9]  # big land only for the coarse fit
            T = Transformer.from_crs('EPSG:4326', f'+proj={PROJ} +lon_0={lon0} +datum=WGS84', always_xy=True)
            (x0, x1), (y0, y1) = T.transform([95, 182], [20, -47])  # roughly the PNG's corners
            s = W / (x1 - x0)
            p0 = [s, s, -x0 * s, y0 * s]
            r = optimize.minimize(loss, p0, args=(ps, 2), method='Nelder-Mead', options={'maxiter': 800})
            print(lon0, 1 - r.fun)
            if best is None or r.fun < best[0]:
                best = (r.fun, lon0, list(r.x))
        _, lon0, p = best
        ps = parts(lon0)
        r = optimize.minimize(loss, p, args=(ps, 1), method='Nelder-Mead', options={'maxiter': 600, 'xatol': 1e-9})
        json.dump({'lon0': float(lon0), 'p': list(map(float, r.x)), 'iou': 1 - r.fun}, open(PAR, 'w'), indent=1)
    P = json.load(open(PAR))
    f = place(P['p'])
    print('lon_0 %.2f, land IoU %.3f' % (P['lon0'], P['iou']))
    paths = {c: [] for c in COLS}
    frame = box(0, 0, W, H)
    for q in parts(P['lon0']):
        qq = stransform(f, q).intersection(frame)
        if qq.is_empty or qq.area < MIN_AREA:
            continue
        m = raster([q], f)
        ys, xs = np.nonzero(m)
        if len(ys):
            px = a[ys, xs]
            votes = [(np.abs(px - [int(c[i:i + 2], 16) for i in (1, 3, 5)]).sum(1) < 30).sum() for c in COLS]
        else:
            px = a[min(int(qq.centroid.y), H - 1), min(int(qq.centroid.x), W - 1)][None]
            votes = [(np.abs(px - [int(c[i:i + 2], 16) for i in (1, 3, 5)]).sum(1) < 30).sum() for c in COLS]
        if max(votes) == 0:
            continue  # falls on sea in the PNG: an islet the PNG leaves out
        col = COLS[int(np.argmax(votes))]
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
