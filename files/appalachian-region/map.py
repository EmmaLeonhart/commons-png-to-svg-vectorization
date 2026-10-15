"""Map layers of the Appalachian region rebuild: which census counties the PNG shows as Appalachian
(white), read from the PNG's colour at points inside each county, then states (blue), the region
(white), state lines and the region's outline. Writes members.json and layers.svg (no text yet)."""
import json
import numpy as np
from PIL import Image
from shapely.ops import unary_union
import shapely
import common as C

P = json.load(open('files/appalachian-region/projection.json'))
proj = C.projector(P)
a = np.asarray(Image.open(C.PNG).convert('RGB')).astype(int)
WHITE = (a.min(-1) > 245)
BLUE = (np.abs(a - [135, 164, 199]).max(-1) < 25)
counties = C.read('cb_2018_us_county_5m')
states = C.read('cb_2018_us_state_5m')

members, unsure = [], []
for rec, g in counties:
    # sample a grid of interior points, kept away from the edges (lines and labels sit there)
    inner = g.buffer(-0.04)
    if inner.is_empty:
        inner = g.representative_point().buffer(0.001)
    x0, y0, x1, y1 = inner.bounds
    gx, gy = np.meshgrid(np.linspace(x0, x1, 9), np.linspace(y0, y1, 9))
    ok = shapely.contains_xy(inner, gx, gy)
    X, Y = proj(gx[ok], gy[ok])
    X, Y = np.round(X).astype(int), np.round(Y).astype(int)
    inside = (X >= 1) & (X < C.W - 1) & (Y >= 34) & (Y < 569)
    if not inside.any():
        continue
    w = WHITE[Y[inside], X[inside]].sum()
    b = BLUE[Y[inside], X[inside]].sum()
    if w + b == 0:
        continue
    if w > b:
        members.append(rec['GEOID'])
    if min(w, b) > 0.25 * (w + b):
        unsure.append((rec['GEOID'], rec['NAME'], int(w), int(b)))
# places too small to sample (Virginia's independent cities) count when members surround them
region = unary_union([g for rec, g in counties if rec['GEOID'] in set(members)]).buffer(0.002)
from shapely.geometry import Polygon
region = unary_union([Polygon(p.exterior) for p in getattr(region, 'geoms', [region])])  # holes filled
for rec, g in counties:
    if rec['GEOID'] not in members and g.difference(region).area < 0.02 * g.area:
        members.append(rec['GEOID'])
print(len(members), 'Appalachian counties in view;', len(unsure), 'mixed:', unsure[:20])
json.dump(sorted(members), open('files/appalachian-region/members.json', 'w'))
