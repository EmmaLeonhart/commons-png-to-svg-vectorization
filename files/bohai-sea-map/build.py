"""Rebuild File:Bohai Sea map.png from Natural Earth 10m data (PD): land, lakes, country borders and the
Huang He and Yangtze, in a Lambert conformal conic projection fitted to the PNG's land mask; graticule,
cities, labels (real <text>), north arrow and scale bar as in the PNG. Colours are the PNG's.
usage (repo root): python files/bohai-sea-map/build.py [fit]"""
import io, json, sys
import numpy as np, resvg_py
from PIL import Image, ImageDraw
from pyproj import Transformer
from scipy import optimize
from shapely.geometry import shape, box, mapping
from shapely.ops import transform as stransform

PNG = 'data_lake/downloads/bohai-sea-map/Bohai Sea map.png'
OUT = 'files/bohai-sea-map/Bohai Sea map.svg'
PAR = 'files/bohai-sea-map/projection.json'
NE = 'data_lake/downloads/natural-earth/'
LAND, SEA, LINE, RIVER, GRID = '#fcfed4', '#85c2fc', '#646464', '#3c78d8', '#7aaee0'
BBOX = box(100, 20, 150, 52)  # lon/lat window comfortably larger than the map
MIN_ISLAND = 12  # px²: the PNG is generalised and leaves out islets smaller than about this

im = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
H, W = im.shape[:2]
land_px = (im[..., 2] < 230) & (im[..., 0] > 230)  # pale yellow land; sea, lines and text excluded


def load(name, clip=True):
    fc = json.load(open(NE + name + '.geojson', encoding='utf8'))
    out = []
    for f in fc['features']:
        g = shape(f['geometry'])
        if g.intersects(BBOX):
            out.append((f['properties'], g.intersection(BBOX) if clip else g))
    return out


land = [g for _, g in load('ne_10m_land')]
lakes = [g for p, g in load('ne_10m_lakes') if (p.get('scalerank') or 9) <= 3]
borders = [g for q, g in load('ne_10m_admin_0_boundary_lines_land')
           if q.get('NAME') != 'Korean Demilitarized Zone']  # the PNG draws only the demarcation line
rivers = [g for p, g in load('ne_10m_rivers_lake_centerlines')
          if p.get('name') in ('Huang', 'Chang Jiang', 'Yangtze', 'Huang He', 'Yellow')]


def projector(p):
    lon0, lat1, lat2, s, tx, ty = p
    t = Transformer.from_crs('EPSG:4326', f'+proj=lcc +lon_0={lon0} +lat_1={lat1} +lat_2={lat2} +lat_0=35 '
                             '+ellps=WGS84 +units=m', always_xy=True)

    def f(x, y, z=None):
        X, Y = t.transform(x, y)
        return np.asarray(X) * s / 1e4 + tx, -np.asarray(Y) * s / 1e4 + ty
    return f


def polys(g):
    return list(g.geoms) if hasattr(g, 'geoms') else [g]


def raster(p, scale=0.5):
    f = projector(p)
    img = Image.new('1', (int(W * scale), int(H * scale)), 0)
    d = ImageDraw.Draw(img)
    for g in land:
        for q in polys(stransform(f, g)):
            if q.geom_type != 'Polygon':
                continue
            d.polygon([(x * scale, y * scale) for x, y in q.exterior.coords], fill=1)
            for r in q.interiors:
                d.polygon([(x * scale, y * scale) for x, y in r.coords], fill=0)
    return np.asarray(img)


target = np.asarray(Image.fromarray(land_px).resize((W // 2, H // 2)))


def loss(p):
    m = raster(p)
    return 1 - (m & target).sum() / (m | target).sum()


def path_d(g, f, close=True):
    out = []
    for q in polys(stransform(f, g)):
        if q.geom_type == 'Polygon' and q.area < MIN_ISLAND:
            continue
        rings = [q.exterior, *q.interiors] if q.geom_type == 'Polygon' else [q]
        for r in rings:
            c = np.asarray(r.coords)
            if len(c) < 2:
                continue
            out.append('M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in c) + ('Z' if close else ''))
    return ''.join(out)


# city dots (centre, measured from the PNG) and labels: (text, ink box x0, x1, y0, y1, style)
DOTS = [(704.0, 134.0), (386.0, 213.0), (114.5, 291.5), (315.0, 349.0), (475.0, 352.0), (524.5, 425.5),
        (261.5, 491.5), (614.0, 539.0), (755.5, 572.0), (293.5, 737.5)]
SANS, SERIF_I, BOLD = ('Arial', 'normal'), ('Times New Roman;font-style:italic', 'normal'), ('Arial Narrow', 'bold')
LABELS = [('RUSSIA', 701, 783, 56, 74, SANS), ('Vladivostok', 710, 804, 109, 123, SANS),
          ('CHINA', 86, 158, 135, 153, SANS), ('Shenyang', 398, 477, 191, 208, SANS),
          ('Beijing', 126, 179, 268, 284, SANS), ('NORTH', 467, 535, 286, 301, SANS),
          ('KOREA', 469, 535, 313, 328, SANS), ('Dalian', 329, 377, 356, 370, SANS),
          ('Pyongyang', 483, 572, 358, 374, SANS), ('Seoul', 533, 583, 404, 420, SANS),
          ('SOUTH', 537, 604, 453, 468, SANS), ('Qingdao', 185, 253, 467, 484, SANS),
          ('KOREA', 539, 604, 480, 495, SANS), ('Busan', 553, 600, 518, 531, SANS),
          ('JAPAN', 827, 895, 521, 539, SANS), ('Hiroshima', 762, 842, 547, 561, SANS),
          ('Shanghai', 210, 285, 743, 760, SANS),
          ('Sea of', 743, 835, 283, 314, SERIF_I), ('Japan', 742, 826, 325, 354, SERIF_I),
          ('Bohai', 212, 286, 342, 363, SERIF_I), ('Sea', 227, 271, 379, 400, SERIF_I),
          ('Yellow', 343, 432, 526, 549, SERIF_I), ('Sea', 361, 409, 566, 589, SERIF_I),
          ('East China', 401, 555, 775, 798, SERIF_I), ('Sea', 454, 502, 816, 839, SERIF_I),
          ('NORTH', 784, 837, 831, 845, BOLD), ('0', 717, 724, 853, 863, SANS), ('100', 753, 778, 853, 863, SANS),
          ('200', 796, 822, 853, 863, SANS), ('300', 842, 867, 853, 863, SANS), ('400', 887, 912, 853, 863, SANS),
          ('Kilometres', 773, 847, 881, 893, SANS)]
RIVER_LABELS = ['Huang He River', 'Yangtze River']  # rotated, in the blue of the sea names
LABEL_JSON = 'files/bohai-sea-map/labels.json'
SEA_TEXT = '#0752a8'


def fit_labels():
    sys.path.insert(0, 'tools')
    from fit_text import fit
    out = [fit(t, (x0, x1, y0, y1), fam, wt, canvas=(W, H)) for t, x0, x1, y0, y1, (fam, wt) in LABELS]
    json.dump(out, open(LABEL_JSON, 'w'))
    return out


def river_labels():
    """Angle from the principal axis of each rotated label's blue ink; size and position fitted to its length
    and centre (the label is drawn centred and rotated about its centre)."""
    a = im
    blue = (a[..., 2] > 120) & (a[..., 0] < 80) & (a[..., 1] < 120)
    out = []
    for text, (x0, x1, y0, y1) in zip(RIVER_LABELS, [(0, 125, 430, 535), (50, 155, 700, 792)]):
        ys, xs = np.nonzero(blue[y0:y1, x0:x1])
        xs, ys = xs + x0, ys + y0
        cx, cy = xs.mean(), ys.mean()
        u, s, vt = np.linalg.svd(np.stack([xs - cx, ys - cy]), full_matrices=False)
        d = u[:, 0] if u[0, 0] > 0 else -u[:, 0]
        ang = np.degrees(np.arctan2(d[1], d[0]))
        proj = (xs - cx) * d[0] + (ys - cy) * d[1]
        length = proj.max() - proj.min()
        mid = (proj.max() + proj.min()) / 2
        out.append(dict(text=text, cx=float(cx + mid * d[0]), cy=float(cy + mid * d[1]), angle=float(ang),
                        length=float(length)))
    return out


def label_svg(t, p, fam, wt, fill):
    family, *style = fam.split(';')
    st = f' font-style="{style[0].split(":")[1]}"' if style else ''
    ls = f' letter-spacing="{p["ls"]}"' if abs(p['ls']) > 0.05 else ''
    return (f'<text x="{p["x"]}" y="{p["y"]}" font-family="{family}" font-weight="{wt}"{st} '
            f'font-size="{p["size"]}"{ls} fill="{fill}">{t}</text>')


def build_svg(p):
    f = projector(p)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="{SEA}"/>']
    grid = []
    for lat in range(20, 55, 5):
        pts = [f(lon, lat) for lon in np.arange(100, 150.1, 0.5)]
        grid.append('M' + ' '.join(f'{float(x):.1f},{float(y):.1f}' for x, y in pts))
    for lon in range(100, 155, 5):
        pts = [f(lon, lat) for lat in np.arange(20, 52.1, 0.5)]
        grid.append('M' + ' '.join(f'{float(x):.1f},{float(y):.1f}' for x, y in pts))
    o.append(f'<path d="{"".join(grid)}" fill="none" stroke="{GRID}" stroke-width="1"/>')
    o.append(f'<path d="{"".join(path_d(g, f) for g in land)}" fill="{LAND}" stroke="{LINE}" '
             f'stroke-width="1.5" stroke-linejoin="round"/>')
    o.append(f'<path d="{"".join(path_d(g, f, False) for g in borders)}" fill="none" stroke="{LINE}" '
             f'stroke-width="1.5" stroke-linejoin="round"/>')
    o.append(f'<path d="{"".join(path_d(g, f, False) for g in rivers)}" fill="none" stroke="{RIVER}" '
             f'stroke-width="1.5" stroke-linejoin="round"/>')
    o.append('<g fill="#000">' + ''.join(f'<circle cx="{x}" cy="{y}" r="6.5"/>' for x, y in DOTS) + '</g>')
    fits = json.load(open(LABEL_JSON))
    for (t, *_, (fam, wt)), q in zip(LABELS, fits):
        o.append(label_svg(t, q, fam, wt, SEA_TEXT if 'italic' in fam else '#000'))
    for r in json.load(open(LABEL_JSON.replace('labels', 'river_labels'))):
        o.append(f'<text transform="translate({r["cx"]:.1f},{r["cy"]:.1f}) rotate({r["angle"]:.1f})" '
                 f'text-anchor="middle" dy="0.35em" font-family="Times New Roman" font-style="italic" '
                 f'font-size="{r["size"]:.1f}" fill="{SEA_TEXT}">{r["text"]}</text>')
    # north arrow and scale bar (measured)
    o.append('<path d="M810.5,795.5 L836.2,828.2 L785,828.2Z" fill="#000"/>')
    o.append('<g stroke="#000" stroke-width="1"><rect x="719" y="866.3" width="181" height="8.7" fill="#fff"/>'
             '<rect x="719" y="866.3" width="46.5" height="8.7" fill="#000"/>'
             '<rect x="809.3" y="866.3" width="46.2" height="8.7" fill="#000"/></g>')
    o.append('</svg>')
    return '\n'.join(o) + '\n'


if __name__ == '__main__':
    p0 = [125.0, 30.0, 45.0, 0.36, 470.0, 440.0]
    if len(sys.argv) > 1 and sys.argv[1] == 'fit':
        r = optimize.minimize(loss, p0, method='Nelder-Mead',
                              options={'maxiter': 1500, 'xatol': 1e-3, 'fatol': 1e-6, 'initial_simplex': None})
        json.dump(list(r.x), open(PAR, 'w'))
        print('fitted IoU %.4f' % (1 - r.fun), [round(v, 4) for v in r.x])
    p = json.load(open(PAR))
    print('land IoU %.4f' % (1 - loss(p)))
    if len(sys.argv) > 1 and sys.argv[1] in ('fit', 'labels'):
        fit_labels()
        rl = river_labels()
        for r in rl:  # Times italic: ink length ~ 0.42 em per character as a start, refined by rendering
            r['size'] = r['length'] / (0.42 * len(r['text']))
        json.dump(rl, open(LABEL_JSON.replace('labels', 'river_labels'), 'w'))
    open(OUT, 'w', encoding='utf8').write(build_svg(p))
    print('wrote', OUT)
