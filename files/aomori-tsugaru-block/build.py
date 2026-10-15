"""Rebuild File:Aomori Tsugaru-block.png from MLIT 国土数値情報 N03 administrative areas as of
2000-10-01 (the municipalities before the 2005 mergers, as drawn in the PNG): Aomori's 67 municipalities
with municipal borders, the Tsugaru ones (the five Tsugaru districts and Aomori, Hirosaki, Kuroishi and
Goshogawara cities) filled green; Hokkaido, Iwate and Akita as plain land. Plain lon/lat projection,
affine fitted to the PNG's lines by chamfer distance. Colours are the PNG's. Run from the repo root."""
import io, json, sys, zipfile
import numpy as np, resvg_py, shapefile
from PIL import Image
from scipy import ndimage, optimize
from shapely.geometry import shape, box
from shapely.ops import unary_union

PNG = 'data_lake/downloads/aomori-tsugaru/Aomori Tsugaru-block.png'
OUT = 'files/aomori-tsugaru-block/Aomori Tsugaru-block.svg'
SEA, LAND, GREEN, MUNI, COAST, PREF = '#c0ffff', '#ffffff', '#80ff80', '#000000', '#0000ff', '#ff0000'
TSUGARU_DISTRICTS = {'東津軽郡', '西津軽郡', '南津軽郡', '中津軽郡', '北津軽郡'}
TSUGARU_CITIES = {'青森市', '弘前市', '黒石市', '五所川原市'}
VIEW = box(139.3, 40.0, 142.2, 41.9)  # lon/lat window comfortably larger than the PNG


def load(code):
    z = zipfile.ZipFile(f'data_lake/downloads/n03/2000/N03-001001_{code}_GML.zip')
    base = f'N03-001001_{code}-g_AdministrativeBoundary'
    r = shapefile.Reader(shp=io.BytesIO(z.read(base + '.shp')), shx=io.BytesIO(z.read(base + '.shx')),
                         dbf=io.BytesIO(z.read(base + '.dbf')), encoding='cp932')
    out = []
    for sr in r.iterShapeRecords():
        g = shape(sr.shape.__geo_interface__)
        if g.intersects(VIEW):
            out.append((sr.record, g.intersection(VIEW)))
    return out


aomori = load('02')
munis = {}
for rec, g in aomori:
    munis.setdefault(rec[6], [rec, []])[1].append(g)
munis = {k: (rec, unary_union(gs)) for k, (rec, gs) in munis.items()}
green = {k for k, (rec, g) in munis.items() if rec[2] in TSUGARU_DISTRICTS or rec[3] in TSUGARU_CITIES}
others = {c: unary_union([g for _, g in load(c)]) for c in ('01', '03', '05')}
aom = unary_union([g for _, g in munis.values()])
land = unary_union([aom, *others.values()])
pref_border = unary_union([aom.boundary.intersection(o.buffer(0.002)) for o in others.values()])
TOL = 0.003


def path(geom, f):
    """SVG path data of a (multi)polygon or (multi)line, through the projection f."""
    geom = geom.simplify(TOL, preserve_topology=True)
    parts = []
    def ring(coords, close):
        pts = [f(x, y) for x, y in coords]
        return 'M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts) + ('Z' if close else '')
    for g in getattr(geom, 'geoms', [geom]):
        if g.geom_type == 'Polygon':
            parts.append(ring(g.exterior.coords, True))
            parts += [ring(i.coords, True) for i in g.interiors]
        elif g.geom_type in ('LineString', 'LinearRing'):
            parts.append(ring(g.coords, False))
        elif hasattr(g, 'geoms'):
            parts.append(path(g, f))
    return ''.join(parts)


png = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
H, W = png.shape[:2]
lines = (png.sum(-1) < 100) | ((png[..., 2] > 200) & (png[..., 0] < 50) & (png[..., 1] < 50)) | \
        ((png[..., 0] > 200) & (png[..., 1] < 50) & (png[..., 2] < 50))
dist = ndimage.distance_transform_edt(~lines)


def proj(p):
    sx, sy, lon0, lat0 = p
    return lambda x, y: ((x - lon0) * sx, (lat0 - y) * sy)


def svg(p, lines_only=False):
    f = proj(p)
    fill = lambda c: 'none' if lines_only else c
    body = [f'<rect width="{W}" height="{H}" fill="{fill(SEA)}"/>' if not lines_only else '',
            f'<path d="{path(unary_union(list(others.values())), f)}" fill="{fill(LAND)}" stroke="none"/>',
            f'<g stroke="{MUNI}" stroke-width="1" stroke-linejoin="round">']
    for k, (rec, g) in sorted(munis.items()):
        body.append(f'<path id="m{k}" d="{path(g, f)}" fill="{fill(GREEN if k in green else LAND)}"/>')
    body.append('</g>')
    body.append(f'<path id="coast" d="{path(land.boundary.difference(pref_border.buffer(0.004)), f)}" fill="none" stroke="{COAST}" stroke-width="1"/>')
    body.append(f'<path id="prefecture-border" d="{path(pref_border, f)}" fill="none" stroke="{PREF}" stroke-width="1"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            + ''.join(body) + '</svg>')


def render(s):
    im = Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=s)))).convert('RGBA')
    return np.asarray(Image.alpha_composite(Image.new('RGBA', im.size, 'white'), im).convert('RGB')).astype(int)


def cost(p):
    m = render(svg(p, lines_only=True)).sum(-1) < 600
    return dist[m].mean() if m.any() else 1e9


if __name__ == '__main__':
    if 'fit' in sys.argv:
        # starting guess: west coast of Tsugaru (139.85 E) at x=0, Hokkaido tip (41.65 N) at y=0
        p0 = (177.0, 166.0, 139.85, 41.68)
        best = min((cost((sx, sy, p0[2], p0[3])), sx, sy) for sx in (150, 165, 180, 195) for sy in (120, 135, 150, 165, 180))
        r = optimize.minimize(cost, (best[1], best[2], p0[2], p0[3]), method='Nelder-Mead',
                              options={'xatol': 1e-4, 'fatol': 1e-4, 'maxiter': 600, 'initial_simplex': None})
        json.dump(list(r.x), open('files/aomori-tsugaru-block/projection.json', 'w'))
        print('chamfer %.3f' % r.fun, r.x)
    p = json.load(open('files/aomori-tsugaru-block/projection.json'))
    s = svg(p)
    open(OUT, 'w', encoding='utf8').write(s)
    out = render(s)
    same = (np.abs(out - png).max(-1) < 60).mean()
    g_png = (png[..., 0] == 128) & (png[..., 1] == 255)
    g_out = (np.abs(out - [128, 255, 128]).max(-1) < 30)
    print('pixels matching colour %.4f  green IoU %.4f' % (same, (g_png & g_out).sum() / (g_png | g_out).sum()))
    c = np.concatenate([png, out], 1).astype(np.uint8)
    Image.fromarray(c).resize((c.shape[1] * 3, c.shape[0] * 3), Image.NEAREST).save('scratch/arms/tsugaru_cmp.png')
