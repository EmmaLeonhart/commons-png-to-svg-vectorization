"""Rebuild File:RSAFinfoboxflag.png (a simplified Republic of Singapore Air Force flag, 1000x667) by construction from
measurements of the PNG: light blue field; the red canton (500x333) with the white crescent (a white circle cut by a
second red circle, drawn in the PNG's slightly different red) and five regular five-pointed stars at their measured
centres; the roundel (white, red, white circles) with the straight-edged red emblem as a 12-vertex polygon (corners
from the PNG's outline, rounded anti-aliased corners restored by intersecting their edges). Run from the repo root."""
import numpy as np

OUT = 'files/rsaf-flag/RSAFinfoboxflag.svg'
W, H = 1000, 667
BLUE, RED, RED2, WHITE = '#5faaff', '#ed2939', '#ee2436', '#ffffff'
CANTON = (500, 333)
CRESCENT_OUT = (211.5, 166.5, 122.5)  # white circle (cx, cy, r)
CRESCENT_IN = (267.5, 166.5, 122.5)  # the red circle cutting it
STARS = [(278.37, 96.38), (211.39, 145.17), (345.32, 145.17), (236.97, 223.59), (319.71, 223.63)]
STAR_R = 29.7
ROUNDEL = (805.5, 504.0, [(132.5, WHITE), (126.0, RED), (106.5, WHITE)])
EMBLEM = [(794.8, 418.4), (852.5, 428.3), (885.4, 466.2), (877.5, 517.4), (838.5, 536.2), (803.5, 560.1),
          (778.5, 592.5), (741.5, 548.5), (746.2, 520.5), (785.9, 484.5), (741.5, 495.3), (738.7, 460.4)]


def star(cx, cy, r):
    ri = r * np.sin(np.radians(18)) / np.sin(np.radians(126))  # inner radius of a regular pentagram
    pts = [(cx + (r if k % 2 == 0 else ri) * np.sin(np.radians(36 * k)),
            cy - (r if k % 2 == 0 else ri) * np.cos(np.radians(36 * k))) for k in range(10)]
    return 'M' + ' '.join(f'{x:.2f},{y:.2f}' for x, y in pts) + 'Z'


cx, cy, rings = ROUNDEL
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
     f'<rect width="{W}" height="{H}" fill="{BLUE}"/>',
     f'<rect width="{CANTON[0]}" height="{CANTON[1]}" fill="{RED}"/>',
     f'<circle cx="{CRESCENT_OUT[0]}" cy="{CRESCENT_OUT[1]}" r="{CRESCENT_OUT[2]}" fill="{WHITE}"/>',
     f'<circle cx="{CRESCENT_IN[0]}" cy="{CRESCENT_IN[1]}" r="{CRESCENT_IN[2]}" fill="{RED2}"/>',
     f'<path fill="{WHITE}" d="{"".join(star(x, y, STAR_R) for x, y in STARS)}"/>',
     *[f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{c}"/>' for r, c in rings],
     f'<path fill="{RED}" d="M' + ' '.join(f'{x},{y}' for x, y in EMBLEM) + 'Z"/>',
     '</svg>']
open(OUT, 'w', encoding='utf8').write('\n'.join(o) + '\n')
print('wrote', OUT)
