"""Rebuild an aliased line-art family tree (MS Paint style: 1 px black lines, flat-coloured vertical
names) as SVG: lines are extracted as exact straight segments, filled dots as circles, dotted lines
as dashed segments; names come from a JSON spec as real vertical <text> for SVGTranslate.

usage: python tools/rebuild_tree.py SPEC.json
spec: {"png": ..., "out": ..., "title": ..., "font_size": 16,
       "colours": {"red": "#ff0000", ...},
       "names": [{"text": "名" or ["right column", "left column"], "colour": "red", "bold": false,
                  "box": [x0, x1, y0, y1]}, ...],
       "notes": [{"text": ..., "box": [...], "size": 12, "colour": "#000000"}]}
Prints a report with the number of black pixels not explained by any segment.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as nd

FONT = "'Noto Sans CJK JP', 'Noto Sans JP', 'MS Gothic', sans-serif"


def runs(line, min_len):
    r = np.nonzero(line)[0]
    if len(r) == 0:
        return []
    return [(int(q[0]), int(q[-1])) for q in np.split(r, np.where(np.diff(r) > 1)[0] + 1) if len(q) >= min_len]


def extract(black, min_len=3):
    H, W = black.shape
    work = black.copy()
    circles = []
    # filled dots: what survives an opening with a 5x5 square (1 px lines do not), grown back
    blobs = nd.binary_dilation(nd.binary_opening(black, structure=np.ones((5, 5))), structure=np.ones((3, 3))) & black
    lab, n = nd.label(blobs)
    for i, (sy, sx) in enumerate(nd.find_objects(lab), start=1):
        h, w = sy.stop - sy.start, sx.stop - sx.start
        comp = lab[sy, sx] == i
        if h >= 6 and w >= 6 and abs(h - w) <= 2:
            circles.append(((sx.start + sx.stop) / 2, (sy.start + sy.stop) / 2, (w + h) / 4))
            work[sy, sx] &= ~comp
    covered = np.zeros_like(work)
    hseg, vseg = [], []
    for y in range(H):
        for x0, x1 in runs(work[y], min_len):
            hseg.append((y, x0, x1)); covered[y, x0:x1 + 1] = True
    for x in range(W):
        for y0, y1 in runs(work[:, x], min_len):
            vseg.append((x, y0, y1)); covered[y0:y1 + 1, x] = True
    left = work & ~covered
    # dotted vertical lines: isolated pixels every 2 px in one column
    dotted = []
    for x in range(W):
        ys = np.nonzero(left[:, x])[0]
        if len(ys) >= 3:
            for q in np.split(ys, np.where(np.diff(ys) != 2)[0] + 1):
                if len(q) >= 3:
                    dotted.append((x, int(q[0]), int(q[-1]))); left[q, x] = False
    return hseg, vseg, circles, dotted, int(left.sum())


def main():
    spec = json.loads(Path(sys.argv[1]).read_text(encoding='utf8'))
    im = Image.open(spec['png']).convert('RGB')
    T = np.array(im).astype(int)
    W, H = im.size
    black = np.all(T == 0, 2)
    hseg, vseg, circles, dotted, leftover = extract(black)
    fs = spec.get('font_size', 16)
    cols = spec['colours']
    d = ' '.join([f'M{x0},{y + 0.5} H{x1 + 1}' for y, x0, x1 in hseg] +
                 [f'M{x + 0.5},{y0} V{y1 + 1}' for x, y0, y1 in vseg])
    dots = ' '.join(f'M{x + 0.5},{y0} V{y1 + 1}' for x, y0, y1 in dotted)
    names = []
    for nm in spec['names']:
        x0, x1, y0, y1 = nm['box']
        style = f"fill:{cols[nm['colour']]}" + (';font-weight:bold' if nm.get('bold') else '')
        top = y0 - spec.get('top', 0.5)
        if isinstance(nm['text'], list):
            xr, xl = x1 + 1 - fs / 2, x0 + fs / 2
            body = (f'<tspan x="{xr:.1f}" y="{top:.1f}">{nm["text"][0]}</tspan>'
                    f'<tspan x="{xl:.1f}" y="{top:.1f}">{nm["text"][1]}</tspan>')
            names.append(f'    <text writing-mode="tb" style="{style}">{body}</text>')
        else:
            names.append(f'    <text x="{(x0 + x1 + 1) / 2:.1f}" y="{top:.1f}" writing-mode="tb" style="{style}">'
                         f'{nm["text"]}</text>')
    notes = []
    for nt in spec.get('notes', []):
        x0, x1, y0, y1 = nt['box']
        notes.append(f'    <text x="{(x0 + x1 + 1) / 2:.1f}" y="{y1 + 1:.1f}" text-anchor="middle" '
                     f'style="font-size:{nt.get("size", 12)}px;fill:{nt.get("colour", "#000000")}">{nt["text"]}</text>')
    circ = '\n'.join(f'    <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}"/>' for cx, cy, r in circles)
    Path(spec['out']).write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <title>{spec.get('title', '')}</title>
  <rect width="{W}" height="{H}" fill="#ffffff"/>
  <g id="lines" style="fill:none;stroke:#000000;stroke-width:1">
    <path d="{d}"/>
    {f'<path d="{dots}" style="stroke-dasharray:1,1"/>' if dots else ''}
  </g>
  <g id="dots" style="fill:#000000">
{circ}
  </g>
  <g id="names" style="font-family:{FONT};font-size:{fs}px">
{chr(10).join(names)}
  </g>
  <g id="notes" style="font-family:{FONT}">
{chr(10).join(notes)}
  </g>
</svg>
''', encoding='utf8')
    print(json.dumps(dict(h_segments=len(hseg), v_segments=len(vseg), circles=len(circles),
                          dotted=dotted, unexplained_black_pixels=leftover)))


if __name__ == '__main__':
    main()
