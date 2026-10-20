"""Rebuild File:Itsukushima-island.png from MLIT 国土数値情報 N03 boundaries of 2000-10-01 (Hiroshima and Yamaguchi
municipalities, the era of the generalised File:Japan map.png the PNG was cut from): land white, sea #c0ffff, coast and
municipal borders #0000ff, Itsukushima (宮島町) green, in an equirectangular projection fitted to the PNG's land mask;
the 16 place labels as real <text> (transcribed, fitted to the PNG's lettering), and the leader lines, arrows and red
underlines as the PNG's own straight pixel runs. Run from the repo root."""
import io, json, sys, zipfile
import numpy as np, shapefile
from PIL import Image, ImageDraw
from scipy import optimize
from shapely.geometry import shape, box
from shapely.ops import unary_union, transform as stransform

sys.path.insert(0, 'tools')
from fit_text import fit  # noqa: E402

PNG = 'data_lake/downloads/itsukushima-island/Itsukushima-island.png'
OUT = 'files/itsukushima-island/Itsukushima-island.svg'
PAR = 'files/itsukushima-island/projection.json'
SEA, LAND, LINE, GREEN, GREY, ORANGE, RED = '#c0ffff', '#ffffff', '#0000ff', '#80ff80', '#404040', '#ff6300', '#ff0000'
COS = np.cos(np.radians(34.25))
VIEW = box(131.9, 33.9, 132.7, 34.5)

im = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
H, W = im.shape[:2]
near = lambda c: np.abs(im - [int(c[i:i + 2], 16) for i in (1, 3, 5)]).sum(2) < 10
sea_px, land_px = near(SEA), near(LAND) | near(GREEN)
known = sea_px | land_px


def load(code):
    z = zipfile.ZipFile(f'data_lake/downloads/n03/2000/N03-001001_{code}_GML.zip')
    base = f'N03-001001_{code}-g_AdministrativeBoundary'
    r = shapefile.Reader(shp=io.BytesIO(z.read(base + '.shp')), shx=io.BytesIO(z.read(base + '.shx')),
                         dbf=io.BytesIO(z.read(base + '.dbf')), encoding='cp932')
    out = {}
    for sr in r.iterShapeRecords():
        g = shape(sr.shape.__geo_interface__)
        if g.intersects(VIEW):
            out.setdefault((sr.record[2], sr.record[3]), []).append(g.intersection(VIEW))
    return {k: unary_union(v).buffer(0) for k, v in out.items()}


munis = {**load('34'), **load('35')}
land = unary_union(list(munis.values()))
miya = munis[next(k for k in munis if k[1] == '宮島町')]


def proj(p):
    s, tx, ty = p
    return lambda x, y, z=None: (np.asarray(x) * COS * s + tx, -np.asarray(y) * s + ty)


def polys(g):
    return [q for q in (g.geoms if hasattr(g, 'geoms') else [g]) if q.geom_type == 'Polygon']


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


def d_of(g, f):
    return ''.join('M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in rr.coords) + 'Z'
                   for q in polys(stransform(f, g)) for rr in [q.exterior, *q.interiors])


# (text, x0, x1, y0, y1, colour, vertical) — boxes around each label's ink, leaders excluded
LABELS = [('厳島', 11, 31, 24, 33, GREY, False), ('(宮島)', 7, 35, 36, 45, GREY, False),
          ('大奈佐美島', 31, 81, 13, 22, GREY, False), ('似島', 85, 95, 0, 21, GREY, True),
          ('金輪島', 97, 126, 13, 22, GREY, False), ('広島湾', 51, 80, 35, 44, ORANGE, False),
          ('峠島', 111, 131, 37, 46, GREY, False), ('江田島', 118, 150, 51, 60, GREY, False),
          ('音戸瀬戸', 127, 166, 61, 70, ORANGE, False), ('阿多田島', 29, 67, 73, 82, GREY, False),
          ('大黒神島', 20, 60, 95, 104, GREY, False), ('甲島', 22, 40, 107, 116, GREY, False),
          ('情島', 135, 145, 85, 104, GREY, True), ('長島', 67, 86, 110, 119, GREY, False),
          ('倉橋島', 132, 161, 120, 129, GREY, False), ('安芸灘', 21, 52, 126, 135, ORANGE, False),
          ('手島', 74, 94, 129, 138, GREY, False)]
FONT = "'MS Gothic', 'IPAGothic', 'Noto Sans CJK JP', sans-serif"


def runs(m):
    out = []
    for y in range(m.shape[0]):
        r = np.concatenate([[0], m[y].astype(int), [0]])
        dd = np.diff(r)
        out += [(y, s, e) for s, e in zip(np.nonzero(dd == 1)[0], np.nonzero(dd == -1)[0])]
    return out


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'fit':
        x0, y0, x1, y1 = land.bounds
        p0 = [W / ((x1 - x0) * COS), -x0 * COS * W / ((x1 - x0) * COS), y1 * W / ((x1 - x0) * COS)]
        best = None
        for s in np.linspace(p0[0] * 0.8, p0[0] * 1.6, 9):  # coarse search, then Nelder-Mead
            for dx in np.linspace(-0.25, 0.25, 9) * W:
                for dy in np.linspace(-0.25, 0.25, 9) * H:
                    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
                    q = [s, W / 2 - cx * COS * s + dx, H / 2 + cy * s + dy]
                    l = loss(q)
                    if best is None or l < best[0]:
                        best = (l, q)
        res = optimize.minimize(loss, best[1], method='Nelder-Mead', options={'maxiter': 600, 'xatol': 1e-3, 'fatol': 1e-7})
        json.dump(list(res.x), open(PAR, 'w'))
        fits = []
        for t, a, b, c, d, col, vert in LABELS:
            if vert:
                fits.append(None)
            else:
                fits.append(fit(t, (a, b, c, d), 'MS Gothic', 'normal', canvas=(W, H)))
        json.dump(fits, open(PAR.replace('projection', 'labels'), 'w'))
    p = json.load(open(PAR))
    f = proj(p)
    print('land IoU %.4f' % (1 - loss(p)))
    fits = json.load(open(PAR.replace('projection', 'labels')))
    text_mask = np.zeros((H, W), bool)
    texts = []
    for (t, a, b, c, d, col, vert), q in zip(LABELS, fits):
        text_mask[max(0, c - 2):d + 2, max(0, a - 2):b + 2] = True  # padded: stray label ink is not a leader
        if vert:
            n, size = len(t), b - a
            pitch = (d - c) / n
            spans = ''.join(f'<tspan x="{(a + b) / 2:.1f}" y="{c + (i + 0.5) * pitch + 0.38 * size:.1f}">{ch}</tspan>'
                            for i, ch in enumerate(t))
            texts.append(f'<text font-size="{size}" text-anchor="middle" fill="{col}">{spans}</text>')
        else:
            ls = f' letter-spacing="{q["ls"]}"' if abs(q['ls']) > 0.05 else ''
            texts.append(f'<text x="{q["x"]}" y="{q["y"]}" font-size="{q["size"]}"{ls} fill="{col}">{t}</text>')
    marks = []
    for col in (GREY, ORANGE, RED):  # leaders, arrows, underlines: the PNG's own pixel runs outside the labels
        m = near(col) & ~text_mask
        if col == RED:
            m = near(col)
        rr = runs(m)
        if rr:
            marks.append(f'<path fill="{col}" d="' + ''.join(f'M{s},{y}h{e - s}v1h{s - e}z' for y, s, e in rr) + '"/>')
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="{SEA}"/>',
         f'<path d="{d_of(land.difference(miya), f)}" fill="{LAND}"/>',
         f'<path d="{d_of(miya, f)}" fill="{GREEN}"/>',
         f'<path d="{"".join(d_of(g, f) for g in munis.values())}" fill="none" stroke="{LINE}" stroke-width="1" '
         'stroke-linejoin="round"/>',
         *marks, f'<g font-family="{FONT}">', *texts, '</g>', '</svg>']
    open(OUT, 'w', encoding='utf8').write('\n'.join(o) + '\n')
    print('wrote', OUT, len(munis), 'municipalities')
