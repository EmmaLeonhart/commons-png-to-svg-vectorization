"""Fit the projection (Albers centre and a similarity transform) so that census state borders and
shorelines land on the PNG's border lines (chamfer distance). Writes projection.json."""
import json
import numpy as np
from scipy import ndimage, optimize
from PIL import Image
from shapely.ops import unary_union
import common as C

states = C.read('cb_2018_us_state_5m')
borders = unary_union([g.boundary for _, g in states]).intersection(C.VIEW)
a = np.asarray(Image.open(C.PNG).convert('RGB')).astype(int)
dark = a.mean(-1) < 90
dark[:30] = False
dark[560:] = False
dist = ndimage.distance_transform_edt(~dark)


def cost(p):
    proj = C.projector(p)
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{C.W}" height="{C.H}">'
         f'<path d="{C.path(borders, proj, 0.01)}" fill="none" stroke="#000" stroke-width="1"/></svg>')
    m = C.render(s).mean(-1) < 128
    m[:30] = False
    m[560:] = False
    return dist[m].mean() if m.any() else 1e9


# start from two control points read off the PNG: Lake Michigan's south tip (87.3 W, 41.6 N) at
# pixel (150, 120) and the New York / Pennsylvania / New Jersey corner (74.69 W, 41.36 N) at (555, 110)
lon0, lat0 = -82.0, 37.5
f = C.albers(lon0, lat0)
(x1, y1), (x2, y2) = f(-87.3, 41.6), f(-74.69, 41.36)
s0 = np.hypot(555 - 150, 110 - 120) / np.hypot(x2 - x1, y2 - y1)
rot0 = np.degrees(np.arctan2(-(110 - 120), 555 - 150) - np.arctan2(y2 - y1, x2 - x1))
c, si = np.cos(np.radians(rot0)), np.sin(np.radians(rot0))
tx0 = 150 - s0 * (c * x1 - si * y1)
ty0 = 120 + s0 * (si * x1 + c * y1)
p0 = [lon0, lat0, s0, rot0, tx0, ty0]
print('start', p0, 'cost', cost(p0))
r = optimize.minimize(cost, p0, method='Nelder-Mead',
                      options={'maxiter': 2000, 'xatol': 1e-3, 'fatol': 1e-4,
                               'initial_simplex': np.array([p0] + [list(np.array(p0) + d) for d in np.diag([1, 1, 60, 1, 8, 8])])})
print('chamfer %.3f' % r.fun, list(r.x))
json.dump(list(r.x), open('files/appalachian-region/projection.json', 'w'))
