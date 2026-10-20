"""Construct File:Kounoke kamon.png: an octagonal ring (inner octagon fitted to the white field, exact to 1 px; the
outer edge is that octagon offset by 58 px with round corners, as drawn) and three wave bands whose six edges are one
sine wave (amplitude 12.1 px, period 205.3 px; each edge fitted to under 1 px RMS) between straight sides at x 150 and
475. Data: octagon.json, waves.json (fits from the PNG). Run from the repo root."""
import json
import numpy as np
from shapely.geometry import Polygon

D = 'files/kounoke-kamon/'
inner = Polygon(json.load(open(D + 'octagon.json'))['inner'])
outer = inner.buffer(58, join_style=1, quad_segs=8)
fits = json.load(open(D + 'waves.json'))
A = np.mean([abs(f[1]) for f in fits])
P = np.mean([f[3] for f in fits])
phase = np.mean([f[2] if f[1] > 0 else f[2] + f[3] / 2 for f in fits])
X0, X1 = 150, 475


def ring(p):
    return 'M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in list(p.exterior.coords)[:-1]) + 'Z'


def edge(c, xs):
    return [(x, c + A * np.sin(2 * np.pi * (x - phase) / P)) for x in xs]


xs = np.linspace(X0, X1, 66)
bands = []
for k in range(3):
    top = edge(fits[2 * k][0], xs)
    bot = edge(fits[2 * k + 1][0], xs[::-1])
    bands.append('M' + ' '.join(f'{x:.1f},{y:.2f}' for x, y in top + bot) + 'Z')
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="622" height="587" viewBox="0 0 622 587">\n'
       f'<rect width="622" height="587" fill="#ffffff"/>\n'
       f'<path fill="#000000" fill-rule="evenodd" d="{ring(outer)}{ring(inner)}"/>\n'
       f'<path fill="#000000" d="{"".join(bands)}"/>\n</svg>\n')
open(D + 'Kounoke kamon.svg', 'w', encoding='utf8').write(svg)
print(f'A {A:.2f} P {P:.2f} phase {phase:.2f}')
