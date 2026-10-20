"""Rebuild File:Seeman douman.png by construction: the Seimei kikyō (a regular pentagram, drawn as one closed stroke)
and the kuji grid (4 vertical and 5 horizontal strokes), 10 px black strokes with round caps and joins, at positions
measured in the PNG (the pentagram's points sit 5 px, half a stroke, inside its ink extremes). Run from the repo root."""
import numpy as np

OUT = 'files/seeman-douman/Seeman douman.svg'
W, H = 700, 350
SW = 10
CX, CY, R = 184.0, 169.1, 145.1  # pentagram: centre and circumradius (point to point 276 px wide)
VX = [436.5, 477.5, 518.0, 559.0]  # grid verticals, from y 56 to 285
HY = [90.0, 130.5, 171.5, 212.5, 253.5]  # grid horizontals, from x 384 to 614
pts = [(CX + R * np.sin(np.radians(144 * k)), CY - R * np.cos(np.radians(144 * k))) for k in range(5)]
star = 'M' + ' '.join(f'{x:.2f},{y:.2f}' for x, y in pts) + 'Z'
grid = ''.join(f'M{x},56V285' for x in VX) + ''.join(f'M384,{y}H614' for y in HY)
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
     f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
     f'<path fill="none" stroke="#000000" stroke-width="{SW}" stroke-linecap="round" stroke-linejoin="round" '
     f'd="{star}{grid}"/>', '</svg>']
open(OUT, 'w', encoding='utf8').write('\n'.join(o) + '\n')
print('wrote', OUT)
