"""Rebuild an aliased line-art family tree (MS Paint style: 1 px lines, flat-coloured vertical names)
as SVG: lines are extracted as exact straight segments (horizontal, vertical, 45-degree), dotted
runs as dashed segments and filled dots as circles; names come from a JSON spec as real vertical
<text> for SVGTranslate.

usage: python tools/rebuild_tree.py SPEC.json
spec: {"png": ..., "out": ..., "title": ..., "font_size": 16, "top": 0.5,
       "colours": {"red": "#ff0000", ...},
       "names": [{"text": "名" or ["right column", "left column"], "colour": "red", "bold": false,
                  "box": [x0, x1, y0, y1]}, ...],
       "notes": [{"text": ..., "box": [...], "size": 12, "colour": "#000000", "vertical": false}],
       "line_colours": [{"rgb": [0, 0, 0], "stroke": "#000000"}, ...]  (drawn in this order),
       "mask": [[x0, x1, y0, y1], ...]  (left out of line extraction: note text, hand-made bits),
       "extra": ["<path .../>", ...]  (raw SVG for one-off shapes such as hops)}
Prints, per line colour, the segment counts and the pixels no segment explains.
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


def extract(px, min_len=3):
    H, W = px.shape
    work = px.copy()
    circles = []
    # filled dots: what survives an opening with a 5x5 square (1 px lines do not), grown back
    blobs = nd.binary_dilation(nd.binary_opening(px, structure=np.ones((5, 5))), structure=np.ones((3, 3))) & px
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
    vdot, hdot = [], []  # dotted runs: single pixels every 2 px
    for x in range(W):
        ys = np.nonzero(left[:, x])[0]
        for q in (np.split(ys, np.where(np.diff(ys) != 2)[0] + 1) if len(ys) >= 3 else []):
            if len(q) >= 3:
                vdot.append((x, int(q[0]), int(q[-1]))); left[q, x] = False
    for y in range(H):
        xs = np.nonzero(left[y])[0]
        for q in (np.split(xs, np.where(np.diff(xs) != 2)[0] + 1) if len(xs) >= 3 else []):
            if len(q) >= 3:
                hdot.append((y, int(q[0]), int(q[-1]))); left[y, q] = False
    diag = []  # 45-degree runs of 3+ pixels: (x0, y0, x1, y1)
    for sx in (1, -1):
        for y, x in zip(*np.nonzero(left)):
            if not left[y, x] or (y > 0 and 0 <= x - sx < W and left[y - 1, x - sx]):
                continue
            k = 0
            while y + k + 1 < H and 0 <= x + sx * (k + 1) < W and left[y + k + 1, x + sx * (k + 1)]:
                k += 1
            if k >= 2:
                diag.append((x, y, x + sx * k, y + k))
                for j in range(k + 1):
                    left[y + j, x + sx * j] = False
    return hseg, vseg, diag, vdot, hdot, circles, int(left.sum())


def main():
    spec = json.loads(Path(sys.argv[1]).read_text(encoding='utf8'))
    im = Image.open(spec['png']).convert('RGB')
    T = np.array(im).astype(int)
    W, H = im.size
    mask = np.zeros(T.shape[:2], bool)
    for x0, x1, y0, y1 in spec.get('mask', []):
        mask[y0:y1 + 1, x0:x1 + 1] = True
    layers, circles, report = [], [], {}
    for lc in spec.get('line_colours', [{'rgb': [0, 0, 0], 'stroke': '#000000'}]):
        px = np.all(T == lc['rgb'], 2) & ~mask
        hseg, vseg, diag, vdot, hdot, circ, leftover = extract(px)
        circles += [(c, lc['stroke']) for c in circ]
        d = ' '.join([f'M{x0},{y + 0.5} H{x1 + 1}' for y, x0, x1 in hseg] +
                     [f'M{x + 0.5},{y0} V{y1 + 1}' for x, y0, y1 in vseg] +
                     [f'M{x0 + 0.5},{y0 + 0.5} L{x1 + 0.5},{y1 + 0.5}' for x0, y0, x1, y1 in diag])
        dots = ' '.join([f'M{x + 0.5},{y0} V{y1 + 1}' for x, y0, y1 in vdot] +
                        [f'M{x0},{y + 0.5} H{x1 + 1}' for y, x0, x1 in hdot])
        layer = f'  <g style="fill:none;stroke:{lc["stroke"]};stroke-width:1">\n    <path d="{d}"/>'
        if dots:
            layer += f'\n    <path d="{dots}" style="stroke-dasharray:1,1"/>'
        layers.append(layer + '\n  </g>')
        report[lc['stroke']] = dict(h=len(hseg), v=len(vseg), diag=len(diag), circles=len(circ),
                                    dotted=len(vdot) + len(hdot), unexplained=leftover)
    fs = spec.get('font_size', 16)
    cols = spec['colours']
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
        st = f'font-size:{nt.get("size", 12)}px;fill:{nt.get("colour", "#000000")}'
        if nt.get('vertical'):
            notes.append(f'    <text x="{(x0 + x1 + 1) / 2:.1f}" y="{y0 - 0.5:.1f}" writing-mode="tb" '
                         f'style="{st}">{nt["text"]}</text>')
        else:
            notes.append(f'    <text x="{(x0 + x1 + 1) / 2:.1f}" y="{y1 + 1:.1f}" text-anchor="middle" '
                         f'style="{st}">{nt["text"]}</text>')
    circ = '\n'.join(f'    <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{c}"/>' for (cx, cy, r), c in circles)
    extra = '\n'.join('    ' + e for e in spec.get('extra', []))
    Path(spec['out']).write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <title>{spec.get('title', '')}</title>
  <rect width="{W}" height="{H}" fill="#ffffff"/>
{chr(10).join(layers)}
  <g id="extra" style="fill:none;stroke:#000000;stroke-width:1">
{extra}
  </g>
  <g id="dots">
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
    print(json.dumps(report))


if __name__ == '__main__':
    main()
