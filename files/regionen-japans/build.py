"""Rebuild File:Regionen japans.png from Natural Earth 10m admin-1 data (PD): Japan's prefectures in a Lambert conformal
conic, each filled with its region's colour (the colour is read from the PNG at the
prefecture's projected interior and snapped to the nearest of the PNG's eight region colours), black prefecture
borders, and Okinawa Island in the PNG's inset, whose grey frame is measured. The PNG's outline is hand-drawn,
so the real map is laid out to fill the PNG's land extent rather than overlaid on it.
Run from the repo root; `fit` recomputes the layout."""
import json, sys
import numpy as np
from PIL import Image, ImageDraw
from pyproj import Transformer
from shapely.geometry import shape, box
from shapely.ops import unary_union, transform as stransform

PNG = 'data_lake/downloads/regionen-japans/Regionen japans.png'
OUT = 'files/regionen-japans/Regionen japans.svg'
PAR = 'files/regionen-japans/projection.json'
NE = 'data_lake/downloads/natural-earth/ne_10m_admin_1_states_provinces.geojson'
REGIONS = {'#b00000': 'Hokkaidō', '#005d0d': 'Tōhoku', '#22009f': 'Kantō', '#aa5400': 'Chūbu', '#00656b': 'Kansai',
           '#6e9200': 'Chūgoku', '#cc5e5e': 'Shikoku', '#d6c521': 'Kyūshū'}
# the eight regions, standard; the PNG agrees wherever its colours can be read (its outline is hand-drawn and only
# overlays the real geography at land IoU 0.58, too loose to read every prefecture's colour reliably)
MEMBERS = {'Hokkaidō': ['Hokkaidō'], 'Tōhoku': ['Aomori', 'Iwate', 'Akita', 'Miyagi', 'Yamagata', 'Fukushima'],
           'Kantō': ['Ibaraki', 'Tochigi', 'Gunma', 'Saitama', 'Chiba', 'Tokyo', 'Kanagawa'],
           'Chūbu': ['Niigata', 'Toyama', 'Ishikawa', 'Fukui', 'Yamanashi', 'Nagano', 'Gifu', 'Shizuoka', 'Aichi'],
           'Kansai': ['Mie', 'Shiga', 'Kyōto', 'Ōsaka', 'Hyōgo', 'Nara', 'Wakayama'],
           'Chūgoku': ['Tottori', 'Shimane', 'Okayama', 'Hiroshima', 'Yamaguchi'],
           'Shikoku': ['Tokushima', 'Kagawa', 'Ehime', 'Kōchi'],
           'Kyūshū': ['Fukuoka', 'Saga', 'Nagasaki', 'Kumamoto', 'Ōita', 'Miyazaki', 'Kagoshima', 'Okinawa']}
COLOUR = {r: c for c, r in REGIONS.items()}
FRAME = [(458, 486), (394, 486), (356.5, 536), (356.5, 584)]  # the inset's grey frame, measured
INSET_X, INSET_Y = 358, 488  # the inset lies right of and below the frame

im = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
H, W = im.shape[:2]
cols = np.array([[int(c[i:i + 2], 16) for i in (1, 3, 5)] for c in REGIONS])
land_px = (np.abs(im[..., None, :] - cols).sum(3) < 40).any(2) | (im.sum(2) < 60)
yy, xx = np.mgrid[:H, :W]
in_inset = (xx > INSET_X) & (yy > INSET_Y) & (yy + xx * (50 / 38) > 536 + 356.5 * (50 / 38))

fc = json.load(open(NE, encoding='utf8'))
pref = {f['properties']['name']: shape(f['geometry']).buffer(0) for f in fc['features'] if f['properties']['adm0_a3'] == 'JPN'}
VIEW = box(128.5, 30.0, 146.0, 45.7)  # the PNG's frame: no Izu south of Hachijō, Ogasawara or other far islands
main = {k: v.intersection(VIEW) for k, v in pref.items() if k != 'Okinawa'}
okinawa = pref['Okinawa'].intersection(box(127.55, 26.0, 128.4, 26.95))  # the inset shows Okinawa Island only


def projector(p):
    lon0, lat1, lat2, s, tx, ty = p
    t = Transformer.from_crs('EPSG:4326', f'+proj=lcc +lon_0={lon0} +lat_1={float(np.clip(lat1, 5, 85))} '
                             f'+lat_2={float(np.clip(lat2, 5, 85))} +lat_0=36 +ellps=WGS84 +units=m', always_xy=True)

    def f(x, y, z=None):
        X, Y = t.transform(x, y)
        return np.asarray(X) * s / 1e4 + tx, -np.asarray(Y) * s / 1e4 + ty
    return f


def polys(g):
    return [q for q in (g.geoms if hasattr(g, 'geoms') else [g]) if q.geom_type == 'Polygon' and not q.is_empty]


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
    return (m & t).sum() / max(1, ((m & region) | t).sum())


def loss_main(p):
    return 1 - iou(raster(list(main.values()), projector(p)), ~in_inset)


def inset_proj(p, q):
    f = projector(p)
    s, dx, dy = q
    return lambda x, y, z=None: (lambda X, Y: (X * s + dx, Y * s + dy))(*f(x, y))


def loss_inset(p, q):
    return 1 - iou(raster([okinawa], inset_proj(p, q)), in_inset)


def path_d(g, f):
    return ''.join('M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in r.coords) + 'Z'
                   for q in polys(stransform(f, g.simplify(0.002))) for r in [q.exterior, *q.interiors])


def region_colour(g, f):
    """the PNG's region colour inside the projected prefecture (eroded, so borders don't count)"""
    m = raster([g.buffer(-0.03) if not g.buffer(-0.03).is_empty else g], f)
    px = im[m]
    if not len(px):
        return None
    d = np.abs(px[:, None, :] - cols).sum(2)
    votes = np.bincount(d.argmin(1)[d.min(1) < 60], minlength=len(cols))
    return list(REGIONS)[int(votes.argmax())] if votes.sum() else None


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'fit':
        # the PNG's outline is hand-drawn and squeezes the west (an overlap fit pushes Kyūshū off the canvas), so the
        # real map is laid out to fill the PNG's land extent instead: the largest scale that fits its bounding box,
        # centred in it; Okinawa Island is scaled into the inset island's box the same way
        ys, xs = np.nonzero(land_px & ~in_inset)
        f0 = projector([137.0, 33.0, 43.0, 1.0, 0.0, 0.0])
        b = stransform(f0, unary_union(list(main.values()))).bounds
        s0 = min((xs.max() - xs.min()) / (b[2] - b[0]), (ys.max() - ys.min()) / (b[3] - b[1]))
        cx, cy = (xs.max() + xs.min() + 1) / 2, (ys.max() + ys.min() + 1) / 2
        p = [137.0, 33.0, 43.0, s0, cx - (b[0] + b[2]) / 2 * s0, cy - (b[1] + b[3]) / 2 * s0]
        bi = stransform(projector(p), okinawa).bounds
        k = min((432 - 414) / (bi[2] - bi[0]), (552 - 516) / (bi[3] - bi[1]))
        q = [k, (414 + 432 + 1) / 2 - (bi[0] + bi[2]) / 2 * k, (516 + 552 + 1) / 2 - (bi[1] + bi[3]) / 2 * k]
        json.dump({'main': p, 'inset': q}, open(PAR, 'w'))
    P = json.load(open(PAR))
    f, fi = projector(P['main']), inset_proj(P['main'], P['inset'])
    print('main land IoU %.4f, inset IoU %.4f' % (1 - loss_main(P['main']), 1 - loss_inset(P['main'], P['inset'])))
    by_col = {}
    agree = 0
    for name, g in sorted(main.items()):
        c = COLOUR[next(r for r, ms in MEMBERS.items() if name in ms)]
        read = region_colour(g, f)
        agree += read == c
        by_col.setdefault(c, []).append(g)
    print(f'{agree} of {len(main)} prefectures read as their region colour in the PNG')
    c_ok = COLOUR['Kyūshū']
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         '<g stroke="#000000" stroke-width="1" stroke-linejoin="round">']
    for c, gs in by_col.items():
        o.append(f'<path fill="{c}" d="{"".join(path_d(g, f) for g in gs)}{path_d(okinawa, fi) if c == c_ok else ""}"/>')
    o += ['</g>',
          f'<path fill="none" stroke="#404040" stroke-width="2.5" d="M' + ' '.join(f'{x},{y}' for x, y in FRAME) + '"/>',
          '</svg>']
    open(OUT, 'w', encoding='utf8').write('\n'.join(o) + '\n')
    print('wrote', OUT)
