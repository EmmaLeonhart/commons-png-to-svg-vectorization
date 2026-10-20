"""Rebuild File:Tree of life kircher plain.png (the Kabbalistic Tree of Life after Kircher) by construction: ten circles
(centres and radius measured in the PNG), the 22 paths as double-lined channels (a black stroke under a narrower white
one, so their 2 px edges stand 8.7 px either side of the centre line), drawn in the PNG's order (the horizontal
channels pass over the others, the circles lie on top), and Da'at as a dotted circle (29 dots) over the channel through it. Run
from the repo root."""
OUT = 'files/tree-of-life-kircher/Tree of life kircher plain.svg'
W, H = 422, 655
S = {1: (207, 59), 2: (322.5, 125.5), 3: (91.5, 125.5), 4: (322.5, 259), 5: (91.5, 259), 6: (207, 325.5),
     7: (322.5, 392), 8: (91.5, 392), 9: (207, 459), 10: (207, 592)}
R = 33  # circle outline radius (2 px outline, inner white radius 32)
PATHS = [(1, 2), (1, 3), (1, 6), (2, 4), (2, 6), (3, 5), (3, 6), (4, 6), (4, 7), (5, 6), (5, 8), (6, 7), (6, 8), (6, 9),
         (7, 9), (7, 10), (8, 9), (8, 10), (9, 10)]
HORIZONTAL = [(2, 3), (4, 5), (7, 8)]  # drawn last of the channels: they pass over the others
OUTER, INNER = 20.4, 16.0
DAAT = (206.5, 190, 34)  # centre and radius; 29 dots


def seg(a, b):
    (x0, y0), (x1, y1) = S[a], S[b]
    return f'M{x0},{y0}L{x1},{y1}'


def channels(pairs):
    d = ''.join(seg(a, b) for a, b in pairs)
    return (f'<path d="{d}" fill="none" stroke="#000000" stroke-width="{OUTER}"/>\n'
            f'<path d="{d}" fill="none" stroke="#ffffff" stroke-width="{INNER}"/>\n')


cx, cy, r = DAAT
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
       f'<rect width="{W}" height="{H}" fill="#ffffff"/>\n'
       + channels(PATHS) + channels(HORIZONTAL)
       + f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#000000" stroke-width="3" stroke-linecap="round" '
         f'stroke-dasharray="0.01 {2 * 3.14159265 * r / 29 - 0.01:.3f}"/>\n'
       + ''.join(f'<circle cx="{x}" cy="{y}" r="{R}" fill="#ffffff" stroke="#000000" stroke-width="2.4"/>\n' for x, y in S.values())
       + '</svg>\n')
open(OUT, 'w', encoding='utf8').write(svg)
print('wrote', OUT, len(PATHS) + len(HORIZONTAL), 'paths')
