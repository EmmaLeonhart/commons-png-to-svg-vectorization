"""Rebuild File:EdinburghTramsGeneric.png: a grey disc (ellipse from the PNG's opaque mask moments) crossed by
two red and two white straight bands (centre line and half-width fitted to each colour mask), clipped to the
disc and stacked as in the PNG. Run from the repo root: python files/edinburgh-trams-generic/build.py
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).parent
PNG = Path('data_lake/downloads/edinburgh-trams-generic/EdinburghTramsGeneric.png')
OUT = HERE / 'EdinburghTramsGeneric.svg'
BANDS = json.loads((HERE / 'bands.json').read_text(encoding='utf8'))
GREY, RED, WHITE = '#949393', '#8a0d04', '#ffffff'
ORDER = ['red1', 'white0', 'white1', 'red0']  # bottom to top, as the crossings in the PNG show


def ellipse():
    a = np.array(Image.open(PNG).convert('RGBA'))[..., 3] > 127
    a = np.array(__import__('scipy.ndimage', fromlist=['x']).binary_opening(a, iterations=3))
    ys, xs = np.nonzero(a)
    cx, cy = xs.mean(), ys.mean()
    cov = np.cov(np.stack([xs - cx, ys - cy]))
    w, v = np.linalg.eigh(cov)
    rx, ry = 2 * np.sqrt(w)  # a uniform ellipse has variance r^2/4 along each axis
    ang = np.degrees(np.arctan2(v[1, 1], v[0, 1]))
    return cx + 0.5, cy + 0.5, ry, rx, ang


def band(b, L=1500):
    c, d, hw = np.array(b['c']) + 0.5, np.array(b['d']), b['hw'] + 0.5
    n = np.array([-d[1], d[0]])
    pts = [c + d * L + n * hw, c - d * L + n * hw, c - d * L - n * hw, c + d * L - n * hw]
    return 'M' + ' L'.join(f'{x:.2f},{y:.2f}' for x, y in pts) + 'Z'


def main():
    cx, cy, rx, ry, ang = ellipse()
    disc = f'<ellipse cx="{cx:.2f}" cy="{cy:.2f}" rx="{rx:.2f}" ry="{ry:.2f}" transform="rotate({ang:.2f} {cx:.2f} {cy:.2f})"'
    paths = '\n'.join(f'    <path id="{k}" d="{band(BANDS[k])}" fill="{RED if k.startswith("red") else WHITE}"/>' for k in ORDER)
    OUT.write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="1000" height="909" viewBox="0 0 1000 909">
  <title>Edinburgh Trams symbol</title>
  <defs><clipPath id="disc">{disc}/></clipPath></defs>
  {disc} fill="{GREY}"/>
  <g clip-path="url(#disc)">
{paths}
  </g>
</svg>
''', encoding='utf8')
    print(OUT, dict(cx=round(cx, 1), cy=round(cy, 1), rx=round(rx, 1), ry=round(ry, 1), angle=round(ang, 1)))


if __name__ == '__main__':
    main()
