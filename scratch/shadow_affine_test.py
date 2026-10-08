"""Experiment: fit Natural Earth prefecture (lon/lat) to an Aoki shadow PNG with a moment-based affine."""
import json, sys, subprocess, urllib.request
import numpy as np
from PIL import Image
from scipy.linalg import sqrtm
sys.path.insert(0, 'tools')
from render_svg import render
name, pref = sys.argv[1], sys.argv[2]
png = f'scratch/shadow/{name}.png'
import os; os.makedirs('scratch/shadow', exist_ok=True)
if not os.path.exists(png):
    req = urllib.request.Request('https://commons.wikimedia.org/wiki/Special:FilePath/' + urllib.parse.quote(f'Shadow picture of {name} prefecture.png'.replace(' ', '_')), headers={'User-Agent': 'agentic-vectorization/0.1 (emma@topazcomputing.com)'})
    open(png, 'wb').write(urllib.request.urlopen(req).read())
t = np.array(Image.open(png).convert('RGBA'))[..., 3] > 128
H, W = t.shape
d = json.load(open('data_lake/downloads/natural-earth/ne_10m_admin_1_states_provinces.geojson', encoding='utf8'))
f = next(f for f in d['features'] if f['properties'].get('adm0_a3') == 'JPN' and f['properties']['name'] == pref)
g = f['geometry']; polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
pts = np.array([p for poly in polys for ring in poly for p in ring])
x0, x1, y0, y1 = pts[:, 0].min(), pts[:, 0].max(), pts[:, 1].min(), pts[:, 1].max()
S = 0.8 * min(W, H) / max(x1 - x0, y1 - y0)
dd = ' '.join('M' + ' L'.join(f'{(x - x0) * S + 0.1 * W:.2f},{(y1 - y) * S + 0.1 * H:.2f}' for x, y in ring) + 'Z' for poly in polys for ring in poly)
open('scratch/shadow/ne.svg', 'w').write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><path d="{dd}" fill="#000"/></svg>')
render('scratch/shadow/ne.svg', 'scratch/shadow/ne.png')
s = np.array(Image.open('scratch/shadow/ne.png').convert('RGBA'))[..., 3] > 128
def stats(M):
    ys, xs = np.nonzero(M); P = np.vstack([xs, ys]).astype(float); return P.mean(1), np.cov(P)
mt, Ct = stats(t); ms, Cs = stats(s)
Wt = np.real(sqrtm(Ct)); Wsi = np.linalg.inv(np.real(sqrtm(Cs)))
vv, uu = np.mgrid[0:H, 0:W]; T = np.vstack([uu.ravel(), vv.ravel()]).astype(float)
best = None
for th in np.radians(np.arange(-60, 61, 1.0)):
    R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    A = Wt @ R @ Wsi
    src = np.linalg.inv(A) @ (T - mt[:, None]) + ms[:, None]
    x = np.round(src[0]).astype(int); y = np.round(src[1]).astype(int)
    ok = (x >= 0) & (y >= 0) & (x < W) & (y < H)
    v = np.zeros(T.shape[1], bool); v[ok] = s[y[ok], x[ok]]; v = v.reshape(H, W)
    iou = (v & t).sum() / (v | t).sum()
    if best is None or iou > best[0]: best = (iou, np.degrees(th), A)
iou, th, A = best
U, Sv, Vt = np.linalg.svd(A)
rot = np.degrees(np.arctan2(A[1, 0] - A[0, 1], A[0, 0] + A[1, 1]))
print(f'{name}: IoU {iou:.3f}, rotation {rot:.1f} deg, scale ratio {Sv[0] / Sv[1]:.3f}')
