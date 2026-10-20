"""Rebuild File:Matsuura-gun.png from MLIT 国土数値情報 N03 boundaries of 2000-10-01 (Fukuoka, Saga, Nagasaki, Kumamoto
municipalities; the era of the generalised File:Japan map.png the PNG was cut from): Saga and Nagasaki land white,
other prefectures grey, the municipalities the PNG shows yellow (Meiji-era Matsuura District) in yellow, coast blue,
municipal borders black, prefecture borders red, in an equirectangular projection fitted to the PNG's land mask. The
sea boundary lines are the PNG's own pixel runs; the legend (現在 / 明治期 / 郡役所) is constructed, its labels real
<text>. Run from the repo root."""
import io, json, sys, zipfile
import numpy as np, shapefile
from PIL import Image, ImageDraw
from scipy import optimize, ndimage
from shapely.geometry import shape, box
from shapely.ops import unary_union, transform as stransform

sys.path.insert(0, 'tools')
from fit_text import fit  # noqa: E402

PNG = 'data_lake/downloads/matsuura-gun/Matsuura-gun.png'
OUT = 'files/matsuura-gun/Matsuura-gun.svg'
PAR = 'files/matsuura-gun/projection.json'
SEA, LAND, GREY, YELLOW, COAST, RED = '#64fefe', '#ffffff', '#dadada', '#ffff00', '#0000fe', '#fa0000'
COS = np.cos(np.radians(33.2))
VIEW = box(128.3, 32.3, 130.5, 34.8)
LEGEND = (229, 281, 400, 433)

im = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
H, W = im.shape[:2]
near = lambda c, t=12: np.abs(im - [int(c[i:i + 2], 16) for i in (1, 3, 5)]).sum(2) < t
sea_px = near(SEA, 20)
yellow_px = near(YELLOW)
land_px = near(LAND) | near(GREY) | yellow_px | near('#dedede')
lx0, lx1, ly0, ly1 = LEGEND
in_legend = np.zeros((H, W), bool)
in_legend[ly0 - 1:ly1 + 2, lx0 - 1:lx1 + 2] = True
known = (sea_px | land_px) & ~in_legend


def load(code):
    z = zipfile.ZipFile(f'data_lake/downloads/n03/2000/N03-001001_{code}_GML.zip')
    base = f'N03-001001_{code}-g_AdministrativeBoundary'
    r = shapefile.Reader(shp=io.BytesIO(z.read(base + '.shp')), shx=io.BytesIO(z.read(base + '.shx')),
                         dbf=io.BytesIO(z.read(base + '.dbf')), encoding='cp932')
    out = {}
    for sr in r.iterShapeRecords():
        g = shape(sr.shape.__geo_interface__)
        if g.intersects(VIEW):
            out.setdefault((code, sr.record[2], sr.record[3]), []).append(g.intersection(VIEW))
    return {k: unary_union(v).buffer(0) for k, v in out.items()}


munis = {}
for c in ('40', '41', '42', '43'):
    munis.update(load(c))
land = unary_union(list(munis.values()))
prefs = {c: unary_union([g for k, g in munis.items() if k[0] == c]) for c in ('40', '41', '42', '43')}


def proj(p):
    if len(p) == 3:
        p = [p[0], p[0], p[1], p[2]]
    sx, sy, tx, ty = p  # separate scales: Japan map.png is not equirectangular at this latitude
    return lambda x, y, z=None: (np.asarray(x) * COS * sx + tx, -np.asarray(y) * sy + ty)


def polys(g):
    return [q for q in (g.geoms if hasattr(g, 'geoms') else [g]) if q.geom_type == 'Polygon' and not q.is_empty]


def raster(g, f):
    img = Image.new('1', (W, H), 0)
    d = ImageDraw.Draw(img)
    for q in polys(stransform(f, g)):
        d.polygon(list(q.exterior.coords), fill=1)
        for rr in q.interiors:
            d.polygon(list(rr.coords), fill=0)
    return np.asarray(img)


def loss(p):
    m = raster(land, proj(p))
    return 1 - ((m & land_px) & known).sum() / ((m | land_px) & known).sum()


def d_of(g, f, close=True):
    return ''.join('M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in rr.coords) + ('Z' if close else '')
                   for q in polys(stransform(f, g)) for rr in [q.exterior, *q.interiors])


def line_d(g, f):
    out = []
    for q in (g.geoms if hasattr(g, 'geoms') else [g]):
        if q.geom_type == 'LineString':
            out.append('M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in stransform(f, q).coords))
        elif hasattr(q, 'geoms'):
            out.append(line_d(q, f))
    return ''.join(out)


def runs(m):
    out = []
    for y in range(m.shape[0]):
        r = np.concatenate([[0], m[y].astype(int), [0]]); dd = np.diff(r)
        out += [(y, s, e) for s, e in zip(np.nonzero(dd == 1)[0], np.nonzero(dd == -1)[0])]
    return out


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'fit':
        x0, y0, x1, y1 = (129.3, 32.5, 130.5, 34.7)  # roughly the PNG's window; coarse grid then Nelder-Mead
        best = None
        for s in np.linspace(200, 420, 12):
            for tx in np.linspace(-0.3, 0.3, 9) * W:
                for ty in np.linspace(-0.3, 0.3, 9) * H:
                    q = [s, W / 2 - 129.6 * COS * s + tx, H / 2 + 33.4 * s + ty]
                    l = loss(q)
                    if best is None or l < best[0]:
                        best = (l, q)
        r = optimize.minimize(loss, best[1], method='Nelder-Mead', options={'maxiter': 800, 'xatol': 1e-3, 'fatol': 1e-7})
        rows = []
        bk = im.sum(2) < 100
        for t, (a, b) in zip(['現在', '明治期', '郡役所'], [(401, 411), (412, 422), (423, 433)]):
            ys, xs = np.nonzero(bk[a:b + 1, 245:lx1])
            rows.append(fit(t, (245 + xs.min(), 245 + xs.max(), a + ys.min(), a + ys.max()), 'MS Gothic', 'normal',
                            canvas=(W, H)))
        json.dump({'p': list(r.x), 'legend': rows}, open(PAR, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    P = json.load(open(PAR, encoding='utf8'))
    f = proj(P['p'])
    print('land IoU %.4f' % (1 - loss(P['p'])))
    yellow, white, grey = [], [], []
    # Meiji-era Matsuura District: every municipality of 2000 in a 松浦郡 (東・西・北・南松浦郡), plus the cities made out
    # of it by 2000 (Hirado, Matsuura, Fukue, Imari, Karatsu); chosen by name, since the PNG's generalised coast is too
    # loose for its colours to pick the Goto towns reliably
    MEIJI_CITIES = {'平戸市', '松浦市', '福江市', '伊万里市', '唐津市'}
    for k, g in munis.items():
        if '松浦郡' in (k[1] or '') or k[2] in MEIJI_CITIES:
            yellow.append(g)
        elif k[0] in ('41', '42'):
            white.append(g)
        else:
            grey.append(g)
    print(len(yellow), 'municipalities yellow')
    borders = unary_union([g.boundary for g in munis.values()]).intersection(land.buffer(-0.0005))
    pref_b = unary_union([prefs[a].boundary.intersection(prefs[b].buffer(0.001))
                          for a in prefs for b in prefs if a < b])
    # sea lines (green maritime line, dashed black and red sea boundaries): the PNG's own pixel runs over the sea
    near_land = ndimage.binary_dilation(raster(land, f), iterations=2)
    marks = []
    for col, t in (('#008000', 12), ('#000000', 60), (RED, 30)):
        m = near(col, t) & ~near_land & ~in_legend
        rr = runs(m)
        if rr:
            marks.append(f'<path fill="{col}" d="' + ''.join(f'M{s},{y}h{e - s}v1h{s - e}z' for y, s, e in rr) + '"/>')
    leg = [f'<rect x="{lx0}" y="{ly0}" width="{lx1 - lx0 + 1}" height="{ly1 - ly0 + 1}" fill="#dedede"/>',
           '<rect x="231" y="402" width="13" height="7" fill="#00ff00"/>',
           f'<rect x="231" y="413" width="13" height="7" fill="{YELLOW}"/>',
           f'<circle cx="237" cy="428" r="2" fill="none" stroke="{RED}" stroke-width="1"/>']
    for t, q in zip(['現在', '明治期', '郡役所'], P['legend']):
        ls = f' letter-spacing="{q["ls"]}"' if 0.05 < abs(q['ls']) < 3 else ''
        leg.append(f'<text x="{q["x"]}" y="{q["y"]}" font-size="{q["size"]}"{ls} '
                   "font-family=\"'MS Gothic', 'IPAGothic', 'Noto Sans CJK JP', sans-serif\">" + t + '</text>')
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="{SEA}"/>', *marks,
         f'<path fill="{GREY}" d="{"".join(d_of(g, f) for g in grey)}"/>',
         f'<path fill="{LAND}" d="{"".join(d_of(g, f) for g in white)}"/>',
         f'<path fill="{YELLOW}" d="{"".join(d_of(g, f) for g in yellow)}"/>',
         f'<path fill="none" stroke="#000000" stroke-width="0.8" d="{line_d(borders, f)}"/>',
         f'<path fill="none" stroke="{RED}" stroke-width="1" d="{line_d(pref_b, f)}"/>',
         f'<path fill="none" stroke="{COAST}" stroke-width="1" stroke-linejoin="round" d="{d_of(land, f)}"/>',
         *leg, '</svg>']
    open(OUT, 'w', encoding='utf8').write('\n'.join(o) + '\n')
    print('wrote', OUT)
