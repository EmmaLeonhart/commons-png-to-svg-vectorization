"""Rebuild File:Ch-1422a.png (Swiss field sign of 1422, aliased, transparent background) by corner-fitting
its straight-edged shapes with tools/fit_polygons.py: the pennant outline (red and white together) and the
white cross, each reduced to its real corners. Colours as the PNG. Run from the repo root."""
import sys
import numpy as np
from PIL import Image
sys.path.insert(0, 'tools')
from fit_polygons import polygons, to_path_d

PNG = 'data_lake/downloads/batch2/Ch-1422a.png'
OUT = 'files/ch-1422a/Ch-1422a.svg'
a = np.asarray(Image.open(PNG).convert('RGBA')).astype(int)
H, W = a.shape[:2]
solid = a[..., 3] > 128
white = solid & (a[..., :3].min(-1) > 200)
flag = polygons(solid, tol=1.0)
cross = polygons(white, tol=1.0)
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
       f'<path d="{to_path_d(flag)}" fill="#fc0404"/><path d="{to_path_d(cross)}" fill="#fcfcfc"/></svg>')
open(OUT, 'w', encoding='utf8').write(svg)
import io, resvg_py
o = np.asarray(Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=svg)))).convert('RGBA')).astype(int)
on_white = lambda x: x[..., :3] * (x[..., 3:] / 255) + 255 * (1 - x[..., 3:] / 255)
print('vertices', sum(len(p.exterior.coords) - 1 for p in flag), sum(len(p.exterior.coords) - 1 for p in cross),
      'pixels differing %.4f' % (np.abs(on_white(o) - on_white(a)).max(-1) > 64).mean())
