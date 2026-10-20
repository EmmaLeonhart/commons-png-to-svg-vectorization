"""Rebuild File:Higashimuro District Map.png from MLIT 国土数値情報 N03 boundaries of 2006 (the PNG's own date): Wakayama's
30 municipalities of that year in an equirectangular projection (x scaled by cos 34°) fitted to the PNG's land mask,
Higashimuro District (東牟婁郡: Kushimoto, Kozagawa, Taiji, Nachikatsuura and the Kitayama exclave) in magenta, the
PNG's colours, and its five labels as real <text> fitted to its lettering (DejaVu Sans). Run from the repo root."""
import io, json, sys, zipfile
import numpy as np, shapefile
from PIL import Image, ImageDraw
from scipy import optimize
from shapely.geometry import shape
from shapely.ops import unary_union, transform as stransform

sys.path.insert(0, 'tools')
from fit_text import fit  # noqa: E402

PNG = 'data_lake/downloads/higashimuro/Higashimuro District Map.png'
ZIP = 'data_lake/downloads/n03/N03-06_30_GML.zip'
OUT = 'files/higashimuro-district-map/Higashimuro District Map.svg'
PAR = 'files/higashimuro-district-map/projection.json'
GREEN, MAGENTA, EDGE = '#99cc66', '#ff0080', '#2f6b1f'
COS = np.cos(np.radians(34.0))

im = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
H, W = im.shape[:2]
land_px = (np.abs(im - [0x99, 0xcc, 0x66]).sum(2) < 60) | (np.abs(im - [0xff, 0, 0x80]).sum(2) < 60)

z = zipfile.ZipFile(ZIP)
base = 'N03-06_30-g_AdministrativeBoundary'
r = shapefile.Reader(shp=io.BytesIO(z.read(base + '.shp')), shx=io.BytesIO(z.read(base + '.shx')),
                     dbf=io.BytesIO(z.read(base + '.dbf')), encoding='cp932')
parts = {}
for sr in r.iterShapeRecords():
    parts.setdefault((sr.record[2], sr.record[3]), []).append(shape(sr.shape.__geo_interface__))
munis = {k: unary_union(v).buffer(0) for k, v in parts.items()}
pref = unary_union(list(munis.values()))


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
    m = raster(pref, proj(p))
    return 1 - (m & land_px).sum() / (m | land_px).sum()


def d_of(g, f):
    out = []
    for q in polys(stransform(f, g.simplify(0.0003))):
        out.append(''.join('M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in rr.coords) + 'Z'
                           for rr in [q.exterior, *q.interiors]))
    return ''.join(out)


LABELS = [('Osaka Prefecture', (146, 364, 15, 33)), ('Inland Sea', (14, 145, 145, 164)),
          ('Nara Prefecture', (422, 620, 179, 198)), ('Mie', (567, 608, 315, 334)),
          ('Prefecture', (567, 695, 347, 365)), ('Pacific Ocean', (215, 383, 564, 583))]

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'fit':
        x0, y0, x1, y1 = pref.bounds
        ys, xs = np.nonzero(land_px)
        s = (ys.max() - ys.min()) / (y1 - y0)
        p0 = [s, xs.min() - x0 * COS * s, ys.min() + y1 * s]
        res = optimize.minimize(loss, p0, method='Nelder-Mead', options={'maxiter': 600, 'xatol': 1e-3, 'fatol': 1e-7})
        json.dump(list(res.x), open(PAR, 'w'))
        json.dump([fit(t, b, 'DejaVu Sans', 'normal', canvas=(W, H)) for t, b in LABELS],
                  open(PAR.replace('projection', 'labels'), 'w'))
    p = json.load(open(PAR))
    f = proj(p)
    print('land IoU %.4f' % (1 - loss(p)))
    hm = [g for (gun, _), g in munis.items() if gun == '東牟婁郡']
    rest = [g for (gun, _), g in munis.items() if gun != '東牟婁郡']
    texts = [f'<text x="{q["x"]}" y="{q["y"]}" font-size="{q["size"]}"'
             + (f' letter-spacing="{q["ls"]}"' if abs(q['ls']) > 0.05 else '') + f'>{t}</text>'
             for (t, _), q in zip(LABELS, json.load(open(PAR.replace('projection', 'labels'))))]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<g stroke="{EDGE}" stroke-width="1" stroke-linejoin="round">',
         f'<path fill="{GREEN}" d="{"".join(d_of(g, f) for g in rest)}"/>',
         f'<path fill="{MAGENTA}" d="{"".join(d_of(g, f) for g in hm)}"/>', '</g>',
         '<g font-family="DejaVu Sans, sans-serif" fill="#000000">', *texts, '</g>', '</svg>']
    open(OUT, 'w', encoding='utf8').write('\n'.join(o) + '\n')
    print('wrote', OUT, len(munis), 'municipalities,', len(hm), 'in Higashimuro')
