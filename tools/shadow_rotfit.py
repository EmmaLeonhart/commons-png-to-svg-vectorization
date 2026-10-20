"""Rebuild a "Shadow picture of X prefecture.png" from MLIT 国土数値情報 N03 (2024): the prefecture fitted to the PNG's
black by IoU with scale, aspect, rotation and offset. For the shadow pictures that tools/batch_shadow.py (scale and
offset only) cannot fit, e.g. Ehime, which is drawn rotated about 29°.
usage (repo root): python tools/shadow_rotfit.py SLUG N03-CODE [fit]
  reads data_lake/downloads/shadow-SLUG/Shadow picture of <Slug> prefecture.png (or $SHADOW_TITLE.png), writes
  files/shadow-SLUG/"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import optimize
from shapely.geometry import shape
from shapely.ops import unary_union, transform as stransform

sys.path.insert(0, 'tools')
from n03_prefecture_svg import load  # noqa: E402

SLUG, CODE = sys.argv[1], int(sys.argv[2])
NAME = os.environ.get('SHADOW_TITLE', f'Shadow picture of {SLUG.capitalize()} prefecture')  # override for odd titles
SRC = f'data_lake/downloads/shadow-{SLUG}/{NAME}.png'
OUT = f'files/shadow-{SLUG}/{NAME}.svg'
PAR = f'files/shadow-{SLUG}/projection.json'

im = Image.open(SRC).convert('RGBA')
a = np.asarray(Image.alpha_composite(Image.new('RGBA', im.size, 'white'), im).convert('L'))
H, W = a.shape
ink = a < 128
# optional: leave out districts (N03_003, comma-separated) and islands east of a longitude, for maps drawn without them
DROP = set(filter(None, os.environ.get('SHADOW_DROP_DISTRICTS', '').split(',')))
MAX_LON = float(os.environ.get('SHADOW_MAX_LON', '999'))
geo = unary_union([shape(f['geometry']) for f in load(CODE)['features']
                   if f['properties'].get('N03_003') not in DROP]).buffer(0)
# optional: cut out lakes (MLIT 国土数値情報 W09, data_lake/downloads/w09-lakes/) of at least this area in square
# degrees, for pictures that show them as holes (N03 administrative areas include lake surfaces)
LAKES_MIN = float(os.environ.get('SHADOW_LAKES_MIN_AREA', '0'))
if LAKES_MIN:
    import io, zipfile, shapefile
    z = zipfile.ZipFile('data_lake/downloads/w09-lakes/W09-05_GML.zip')
    rd = shapefile.Reader(shp=io.BytesIO(z.read('W09-05-g_Lake.shp')), shx=io.BytesIO(z.read('W09-05-g_Lake.shx')),
                          dbf=io.BytesIO(z.read('W09-05-g_Lake.dbf')), encoding='cp932')
    lakes = [shape(r.shape.__geo_interface__).buffer(0) for r in rd.iterShapeRecords()]
    lakes = [g for g in lakes if g.area >= LAKES_MIN and g.intersects(geo)]
    geo = geo.difference(unary_union(lakes)).buffer(0)
SW = os.environ.get('SHADOW_STROKE')  # optional outline width (px) for pictures with slightly bolder silhouettes
STROKE = f' stroke="#000000" stroke-width="{SW}" stroke-linejoin="round"' if SW else ''
BBOX = os.environ.get('SHADOW_BBOX')  # optional: keep only islands inside 'minlon,minlat,maxlon,maxlat'
if BBOX:
    from shapely.geometry import box
    geo = geo.intersection(box(*map(float, BBOX.split(',')))).buffer(0)
parts = [g for g in (geo.geoms if hasattr(geo, 'geoms') else [geo]) if g.area > 1e-7 and g.centroid.x < MAX_LON]


CX0, CY0 = geo.centroid.x, geo.centroid.y


def proj(p):
    sc, asp, rot, tx, ty = p
    c, sn = np.cos(np.radians(rot)), np.sin(np.radians(rot))

    def f(x, y, z=None):
        X = (np.asarray(x) - CX0) * sc
        Y = -(np.asarray(y) - CY0) * sc * asp
        return X * c - Y * sn + tx, X * sn + Y * c + ty
    return f


def raster(f):
    img = Image.new('1', (W, H), 0)
    d = ImageDraw.Draw(img)
    for g in parts:
        q = stransform(f, g)
        d.polygon(list(q.exterior.coords), fill=1)
        for r in q.interiors:
            d.polygon(list(r.coords), fill=0)
    return np.asarray(img)


def loss(p):
    m = raster(proj(p))
    return 1 - (m & ink).sum() / (m | ink).sum()


if __name__ == '__main__':
    if len(sys.argv) > 3 and sys.argv[3] == 'fit':
        ys, xs = np.nonzero(ink)
        best = None
        gx0, gy0, gx1, gy1 = unary_union(parts).bounds
        s0 = (xs.max() - xs.min()) / (gx1 - gx0)  # seed scale from the extents
        for rot in range(-40, 41, 5):  # coarse grid over rotation and scale, then Nelder-Mead
            for sc in (0.8 * s0, s0, 1.2 * s0):
                p0 = [sc, 1.2, rot, xs.mean(), ys.mean()]
                l = loss(p0)
                if best is None or l < best[0]:
                    best = (l, p0)
        r = optimize.minimize(loss, best[1], method='Nelder-Mead', options={'maxiter': 2000, 'xatol': 1e-3, 'fatol': 1e-8})
        json.dump(list(r.x), open(PAR, 'w'))
    p = json.load(open(PAR))
    f = proj(p)
    print('IoU %.4f' % (1 - loss(p)))
    d = ''.join('M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in r.coords) + 'Z'
                for g in parts for q in [stransform(f, g.simplify(0.0003))] for r in [q.exterior, *q.interiors])
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<path fill="#000000" fill-rule="evenodd"{STROKE} d="{d}"/>', '</svg>']
    open(OUT, 'w', encoding='utf8').write('\n'.join(o) + '\n')
    print('wrote', OUT, len(parts), 'parts')
