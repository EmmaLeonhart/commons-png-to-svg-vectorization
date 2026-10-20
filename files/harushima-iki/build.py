"""Rebuild File:Harushima Iki.png from MLIT 国土数値情報 N03 (2024) boundaries of Iki City, Nagasaki: the islands in
an equirectangular projection (x scaled by cos 33.78°) fitted to the PNG's land mask, Harushima (the island under
the PNG's red mark) in red, the PNG's colours and black coast, and the two labels as real <text> fitted to the PNG's
lettering. The PNG's outline is schematic (hand-drawn), so the real outline differs visibly (land IoU 0.76).
Run from the repo root."""
import json, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import optimize
from shapely.geometry import shape, box, Point
from shapely.ops import unary_union, transform as stransform

sys.path.insert(0, 'tools')
from n03_prefecture_svg import load  # noqa: E402
from fit_text import fit  # noqa: E402

PNG = 'data_lake/downloads/harushima-iki/Harushima Iki.png'
OUT = 'files/harushima-iki/Harushima Iki.svg'
PAR = 'files/harushima-iki/projection.json'
SEA, LAND, RED = '#99d9ea', '#b5e61d', '#ed1c24'
COS = np.cos(np.radians(33.78))

im = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
H, W = im.shape[:2]
sea_px = (np.abs(im - [0x99, 0xd9, 0xea]).sum(2) < 40)
land_px = ~sea_px
red_px = (np.abs(im - [0xed, 0x1c, 0x24]).sum(2) < 60)

iki = unary_union([shape(f['geometry']) for f in load(42)['features'] if f['properties'].get('N03_004') == '壱岐市'])
iki = iki.intersection(box(129.5, 33.6, 129.95, 33.95))
islands = [g for g in (iki.geoms if hasattr(iki, 'geoms') else [iki]) if g.area > 1e-8]


def proj(p):
    s, tx, ty = p
    return lambda x, y, z=None: (np.asarray(x) * COS * s + tx, -np.asarray(y) * s + ty)


def raster(geoms, f):
    img = Image.new('1', (W, H), 0)
    d = ImageDraw.Draw(img)
    for g in geoms:
        q = stransform(f, g)
        d.polygon(list(q.exterior.coords), fill=1)
        for r in q.interiors:
            d.polygon(list(r.coords), fill=0)
    return np.asarray(img)


def loss(p):
    m = raster(islands, proj(p))
    return 1 - (m & land_px).sum() / (m | land_px).sum()


def d_of(g, f):
    q = stransform(f, g)
    return ''.join('M' + ' '.join(f'{x:.2f},{y:.2f}' for x, y in r.coords) + 'Z' for r in [q.exterior, *q.interiors])


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'fit':
        x0, y0, x1, y1 = iki.bounds
        ys, xs = np.nonzero(land_px)
        s = (ys.max() - ys.min()) / (y1 - y0)
        p0 = [s, xs.min() - x0 * COS * s, ys.min() + y1 * s]
        r = optimize.minimize(loss, p0, method='Nelder-Mead', options={'maxiter': 600, 'xatol': 1e-3, 'fatol': 1e-7})
        json.dump(list(r.x), open(PAR, 'w'))
    p = json.load(open(PAR))
    f = proj(p)
    print('land IoU %.4f' % (1 - loss(p)))
    # Harushima from OpenStreetMap (Nominatim: 原島, 壱岐市 at 33.7244 N, 129.6482 E); the PNG's red mark is too
    # schematic to pick the island by position
    hs = int(np.argmin([g.distance(Point(129.6482, 33.7244)) for g in islands]))
    labels = [('壱岐島', (79, 159, 126, 148), 'bold', '#000000'), ('原島', (22, 58, 241, 257), 'normal', RED)]
    fam = "'MS Gothic', 'IPAGothic', 'Noto Sans CJK JP', sans-serif"
    texts = []
    for t, bx, wt, col in labels:
        q = fit(t, bx, 'MS Gothic', wt, canvas=(W, H))
        ls = f' letter-spacing="{q["ls"]}"' if abs(q['ls']) > 0.05 else ''
        texts.append(f'<text x="{q["x"]}" y="{q["y"]}" font-family="{fam}" font-weight="{wt}" '
                     f'font-size="{q["size"]}"{ls} fill="{col}">{t}</text>')
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="{SEA}"/>',
         f'<path d="{"".join(d_of(g, f) for i, g in enumerate(islands) if i != hs)}" fill="{LAND}" stroke="#000" '
         'stroke-width="1" stroke-linejoin="round"/>',
         f'<path d="{d_of(islands[hs], f)}" fill="{RED}" stroke="#000" stroke-width="1"/>', *texts, '</svg>']
    open(OUT, 'w', encoding='utf8').write('\n'.join(o) + '\n')
    print('wrote', OUT, len(islands), 'islands; Harushima index', hs)
