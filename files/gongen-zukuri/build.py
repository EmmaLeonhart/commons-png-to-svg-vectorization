"""Rebuild File:Gongen Zukuri.png (権現造平面図): yellow axis bands as rectangles (components of the yellow mask with
the black lines crossing them closed over), then the aliased black line art as exact segments and the pillars as
circles (tools/rebuild_tree.extract), drawn over the yellow as in the PNG. Run from the repo root.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as nd

sys.path.insert(0, 'tools')
from rebuild_tree import extract  # noqa: E402

HERE = Path(__file__).parent
PNG = Path('data_lake/downloads/gongen-zukuri/Gongen Zukuri.png')
OUT = HERE / 'Gongen Zukuri.svg'
YELLOW = '#ffcc00'


def merge(hseg, vseg):
    """Stack 1 px runs of the same extent on adjacent rows (or columns) into one line of that width."""
    out = []
    for segs, horiz in ((hseg, True), (vseg, False)):
        groups = {}
        for c, a0, a1 in segs:
            groups.setdefault((a0, a1), []).append(c)
        for (a0, a1), cs in groups.items():
            cs.sort()
            for run in np.split(np.array(cs), np.where(np.diff(cs) > 1)[0] + 1):
                k, mid = len(run), (run[0] + run[-1] + 1) / 2
                if horiz:
                    out.append(f'    <path d="M{a0},{mid} H{a1 + 1}" stroke-width="{k}"/>')
                else:
                    out.append(f'    <path d="M{mid},{a0} V{a1 + 1}" stroke-width="{k}"/>')
    return out


def main():
    A = np.array(Image.open(PNG).convert('RGB')).astype(int)
    H, W = A.shape[:2]
    yel = np.all(A == [255, 204, 0], 2)
    blk = np.all(A == 0, 2)
    # axis bands, measured from the yellow components (black lines split them into pieces)
    rects = [(255, 16, 13, 610),                      # vertical axis
             (90, 120, 160, 13), (273, 120, 160, 13),  # upper hall
             (135, 304, 115, 15), (273, 304, 115, 15), # connecting hall
             (1, 476, 249, 15), (273, 476, 250, 15)]   # lower hall
    hseg, vseg, diag, vdot, hdot, circles, left = extract(blk)
    lines = merge(hseg, vseg)
    d = ' '.join(f'M{x0 + 0.5},{y0 + 0.5} L{x1 + 0.5},{y1 + 0.5}' for x0, y0, x1, y1 in diag)
    OUT.write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <title>権現造平面図 (Gongen-zukuri plan)</title>
  <rect width="{W}" height="{H}" fill="#ffffff"/>
  <g id="axes" fill="{YELLOW}">
{chr(10).join(f'    <rect x="{x}" y="{y}" width="{w}" height="{h}"/>' for x, y, w, h in rects)}
  </g>
  <g id="lines" style="fill:none;stroke:#000000">
{chr(10).join(lines)}
    <path d="{d}" style="stroke-width:1"/>
  </g>
  <g id="pillars" fill="#000000">
{chr(10).join(f'    <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}"/>' for cx, cy, r in circles)}
  </g>
</svg>
''', encoding='utf8')
    print(OUT, f'{len(rects)} rects, {len(hseg)}+{len(vseg)}+{len(diag)} segments, {len(circles)} pillars, {left} black px unexplained')


if __name__ == '__main__':
    main()
