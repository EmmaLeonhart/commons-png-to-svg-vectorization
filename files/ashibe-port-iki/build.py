"""Rebuild File:Position of Ashibe Port Iki City.png from MLIT 国土数値情報 N03 (2024) boundaries of Iki City, Nagasaki:
the islands in an equirectangular projection (x scaled by cos 33.78°) fitted to the PNG's land mask, the PNG's colours
and black coast, the port's shore in blue (the real coastline inside the PNG's blue-marked area, mapped back through
the fitted projection), and the labels as real <text> fitted to the PNG's lettering. The PNG's outline is schematic
(hand-drawn), so the real outline differs visibly. Run from the repo root."""
import json, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import optimize
from shapely.geometry import shape, box, Point
from shapely.ops import unary_union, transform as stransform

sys.path.insert(0, 'tools')
from n03_prefecture_svg import load  # noqa: E402
from fit_text import fit  # noqa: E402

PNG = 'data_lake/downloads/ashibe-port-iki/Position of Ashibe Port Iki City.png'
OUT = 'files/ashibe-port-iki/Position of Ashibe Port Iki City.svg'
PAR = 'files/ashibe-port-iki/projection.json'
SEA, LAND, BLUE = '#99d9ea', '#b5e61d', '#3f48cc'
COS = np.cos(np.radians(33.78))

im = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
H, W = im.shape[:2]
sea_px = (np.abs(im - [0x99, 0xd9, 0xea]).sum(2) < 40)
land_px = ~sea_px & ~((np.abs(im - [0x3f, 0x48, 0xcc]).sum(2) < 60))
MARK = (161, 200, 104, 124)  # the blue shore marking's box in the PNG (x0, x1, y0, y1)

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
    s, tx, ty = p
    inv = lambda x, y: ((x - tx) / (COS * s), (ty - y) / s)
    mx0, mx1, my0, my1 = MARK
    (lo0, la1), (lo1, la0) = inv(mx0, my0), inv(mx1, my1)
    shore = unary_union([g.exterior for g in islands]).intersection(box(lo0, la0, lo1, la1))
    labels = [('壱岐島', (79, 157, 133, 156), 'bold', '#000000'), ('芦辺', (189, 221, 74, 88), 'normal', BLUE),
              ('漁港', (189, 221, 94, 108), 'normal', BLUE)]
    fam = "'MS Gothic', 'IPAGothic', 'Noto Sans CJK JP', sans-serif"
    texts = []
    for t, bx, wt, col in labels:
        q = fit(t, bx, 'MS Gothic', wt, canvas=(W, H))
        ls = f' letter-spacing="{q["ls"]}"' if abs(q['ls']) > 0.05 else ''
        texts.append(f'<text x="{q["x"]}" y="{q["y"]}" font-family="{fam}" font-weight="{wt}" '
                     f'font-size="{q["size"]}"{ls} fill="{col}">{t}</text>')
    lines = [shore] if shore.geom_type == 'LineString' else list(shore.geoms)
    sd = ''.join('M' + ' '.join(f'{x:.2f},{y:.2f}' for x, y in stransform(f, ln).coords) for ln in lines)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="{SEA}"/>',
         f'<path d="{"".join(d_of(g, f) for g in islands)}" fill="{LAND}" stroke="#000" stroke-width="1" '
         'stroke-linejoin="round"/>',
         f'<path d="{sd}" fill="none" stroke="{BLUE}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>',
         *texts, '</svg>']
    open(OUT, 'w', encoding='utf8').write('\n'.join(o) + '\n')
    print('wrote', OUT, len(islands), 'islands;', len(lines), 'shore runs')
