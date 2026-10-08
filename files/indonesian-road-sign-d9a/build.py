"""Rebuild File:Indonesian Road Sign d9a.png: blue rounded sign (box and corner radius from the mask's
area), red cross and white bed as straight-edged polygons whose corners are fitted to the colour masks
(tools/fit_polygons.py, Douglas-Peucker tolerance 1.6 px). Run from the repo root.
"""
import sys
from math import pi
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, 'tools')
from fit_polygons import polygons, to_path_d  # noqa: E402

HERE = Path(__file__).parent
PNG = Path('data_lake/downloads/indonesian-road-sign-d9a/Indonesian Road Sign d9a.png')
OUT = HERE / 'Indonesian Road Sign d9a.svg'
BLUE, RED, WHITE = '#000090', '#da000b', '#ffffff'


def main():
    A = np.array(Image.open(PNG).convert('RGBA')).astype(int)
    H, W = A.shape[:2]
    op = A[..., 3] > 127
    white = op & (A[..., :3].min(2) > 200)
    red = op & (A[..., 0] > 150) & (A[..., 1] < 100) & (A[..., 2] < 100)
    ys, xs = np.nonzero(op)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    r = (((x1 - x0) * (y1 - y0) - op.sum()) / (4 - pi)) ** 0.5
    OUT.write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <title>Indonesian road sign d9a (hospital)</title>
  <rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="{r:.1f}" fill="{BLUE}"/>
  <path id="cross" d="{to_path_d(polygons(red, 1.6))}" fill="{RED}"/>
  <path id="bed" d="{to_path_d(polygons(white, 1.6))}" fill="{WHITE}"/>
</svg>
''', encoding='utf8')
    print(OUT)


if __name__ == '__main__':
    main()
