"""Fit Natural Earth's UK, in a Lambert azimuthal equal-area projection (52N 10E), to the UK of File:Blank map of
Europe cropped.svg (scale and offset, on the rasterised outlines) so Wales can be placed in the map's units. Writes
files/letter-i/wales_fit.json; used by build.py. Run from the repo root."""
import io, json, re
import numpy as np, resvg_py
from PIL import Image, ImageDraw
from pyproj import Transformer
from scipy import optimize
from shapely.geometry import shape
from shapely.ops import unary_union, transform as stransform

SRC = 'data_lake/downloads/letter-i/Blank map of Europe cropped.svg'
NE = 'data_lake/downloads/natural-earth/ne_10m_admin_1_states_provinces.geojson'
s = open(SRC, encoding='utf8').read()
# the map's UK alone, in viewBox units (1 px per unit)
st = s.index('<g', s.rfind('<g', 0, s.index('id="gGBR"')))
st = s.rfind('<g', 0, s.index('id="gGBR"'))
depth, j = 0, st
pat = re.compile(r'<(/?)g\b([^>]*)>')
while True:
    mm = pat.search(s, j)
    if mm.group(1) == '' and not mm.group(2).rstrip().endswith('/'):
        depth += 1
    elif mm.group(1) == '/':
        depth -= 1
    j = mm.end()
    if depth == 0:
        break
gbr = s[st:j]
head = s[:s.index('>', s.index('<svg')) + 1]
defs = re.search(r'<defs\b.*?</defs>', s, re.S)
gbr = re.sub(r'\s(style|class|fill|stroke)="[^"]*"', '', gbr)
doc = head + re.sub(r'<(path|polygon)\b', r'<\1 style="fill:#000;stroke:none"', gbr) + '</svg>'
VBW = 1613.0037
r = np.asarray(Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=doc, width=int(VBW))))).convert('RGBA'))[..., 3] > 128
ys, xs = np.nonzero(r); print('GBR in map units', xs.min(), xs.max(), ys.min(), ys.max())
fc = json.load(open(NE, encoding='utf8'))
uk = [f for f in fc['features'] if f['properties']['adm0_a3'] == 'GBR']
geo_uk = unary_union([shape(f['geometry']) for f in uk]).buffer(0)
wales = unary_union([shape(f['geometry']) for f in uk if f['properties'].get('geonunit') == 'Wales']).buffer(0)
print('wales units', sum(1 for f in uk if f['properties'].get('geonunit') == 'Wales'))
T = Transformer.from_crs('EPSG:4326', '+proj=laea +lat_0=52 +lon_0=10 +ellps=WGS84', always_xy=True)
laea = lambda x, y, z=None: T.transform(x, y)
uk_p = stransform(laea, geo_uk)
H, W = r.shape


def raster(g, p):
    s_, tx, ty = p
    img = Image.new('1', (W, H), 0); d = ImageDraw.Draw(img)
    for q in (g.geoms if hasattr(g, 'geoms') else [g]):
        if q.area * s_ * s_ < 1:
            continue
        d.polygon([(x * s_ + tx, -y * s_ + ty) for x, y in q.exterior.coords], fill=1)
    return np.asarray(img)


def loss(p):
    m = raster(uk_p, p)
    return 1 - (m & r).sum() / max(1, (m | r).sum())


b = uk_p.bounds
s0 = (xs.max() - xs.min()) / (b[2] - b[0])
p0 = [s0, xs.min() - b[0] * s0, ys.min() + b[3] * s0]
print('seed IoU', 1 - loss(p0))
res = optimize.minimize(loss, p0, method='Nelder-Mead', options={'maxiter': 800, 'xatol': 1e-9, 'fatol': 1e-7})
print('fit IoU', 1 - res.fun, list(res.x))
json.dump({'laea': '+proj=laea +lat_0=52 +lon_0=10 +ellps=WGS84', 'p': list(res.x)}, open('files/letter-i/wales_fit.json', 'w'))
