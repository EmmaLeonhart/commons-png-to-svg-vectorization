"""Rebuild File:DPM icon.png (58x58, Detroit People Mover) by construction: the #546684 square, the white
car as corner-fitted straight-edged polygons (tools/fit_polygons.py on the white coverage, upsampled 8x so
the antialiased edges fall at sub-pixel positions), and the grey band under the windows as a rectangle.
Run from the repo root."""
import io, sys
import numpy as np, resvg_py
from PIL import Image
sys.path.insert(0, 'tools')
from fit_polygons import polygons, to_path_d

PNG = 'data_lake/downloads/batch2/DPM icon.png'
OUT = 'files/dpm-icon/DPM icon.svg'
K = 8
im = Image.open(PNG).convert('RGB')
a = np.asarray(im).astype(float)
BG = np.array([84, 102, 132.0])
WH = np.array([251, 253, 252.0])
cov = np.clip(((a - BG) * (WH - BG)).sum(-1) / ((WH - BG) ** 2).sum(), 0, 1)  # white coverage per pixel
big = np.asarray(Image.fromarray((cov * 255).astype(np.uint8)).resize((58 * K, 58 * K), Image.BICUBIC)) > 127
polys = polygons(big, tol=K * 0.6, min_area=K * K)
d = to_path_d(polys)
# grey band: rows where the car's middle columns are a mid grey
cand = [y for y in range(58) if 120 < a[y, 20:38].mean(-1).mean() < 200 and a[y, 20:38].std() < 20]
runs = np.split(np.array(cand), np.nonzero(np.diff(cand) > 1)[0] + 1) if cand else []
band_rows = list(max(runs, key=len)) if runs else []  # the longest run of grey rows
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="58" height="58" viewBox="0 0 58 58">'
       f'<rect width="58" height="58" fill="#546684"/>'
       f'<path d="{d}" fill="#fbfdfc" transform="scale({1 / K})"/>'
       + (f'<rect x="12" y="{min(band_rows)}" width="34" height="{max(band_rows) - min(band_rows) + 1}" fill="#8992a1"/>' if band_rows else '')
       + '</svg>')
open(OUT, 'w', encoding='utf8').write(svg)
o = np.asarray(Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=svg)))).convert('RGB')).astype(float)
print('polygons', len(polys), 'vertices', sum(len(p.exterior.coords) - 1 for p in polys), 'band', band_rows,
      'mean abs diff %.1f' % np.abs(o - a).mean(), 'pixels differing %.4f' % (np.abs(o - a).max(-1) > 64).mean())
Image.fromarray(np.concatenate([a, o], 1).astype(np.uint8)).resize((464 * 2, 464), Image.NEAREST).save('scratch/arms/dpm_cmp.png')
