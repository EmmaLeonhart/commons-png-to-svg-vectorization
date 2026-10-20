"""Rebuild File:Flag of the Indonesian Marine Corps.png: a #9b0000 field with a measured gold frame (an 11 px line
63.5 px in from each edge, starting from a ring in each corner) and the Korps Marinir emblem from
File:Korps Marinir.svg, placed by registration and recoloured as on the flag. The flag shows the emblem in gold:
gold, dark red and bright red all become gold, the waves stay blue. The SVG's black path holds outlines, the lettering
and the islands in one path, and the flag colours those differently (black, red, gold), so it is split into
subpaths; each hole is kept with the subpath that contains it, and each outline group takes the flag's majority
colour over its area. Run from the repo root."""
import re
from collections import Counter

import numpy as np
from PIL import Image, ImageDraw
from shapely.geometry import Polygon, Point
from svgelements import Path, Move, Line, CubicBezier, QuadraticBezier, Close

SRC = 'data_lake/downloads/indonesian-marine-corps-flag/Korps Marinir.svg'
PNG = 'data_lake/downloads/indonesian-marine-corps-flag/Flag of the Indonesian Marine Corps.png'
OUT = 'files/indonesian-marine-corps-flag/Flag of the Indonesian Marine Corps.svg'
FIELD, GOLD, BLUE, BLACK = '#9b0000', '#ffcd00', '#0085eb', '#000000'
N = 1280
W_EMB, OX, OY = 878, 200, 199          # emblem width in flag px and its offset (registered: 97.6% agreement)
VB = 510.23779                          # emblem viewBox width
GT = (-42.526367, -42.518555)           # translate of its surface group
RECOLOUR = {'#ffcc00': GOLD, '#990000': GOLD, '#ff0000': GOLD, '#0082e8': BLUE}

svg = open(SRC, encoding='utf8').read()
flag = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
k = W_EMB / VB


def to_px(x, y):
    return OX + (x + GT[0]) * k, OY + (y + GT[1]) * k


def poly(sub):
    pts = [to_px(p.x, p.y) for p in (sub.point(t) for t in np.linspace(0, 1, max(24, int(sub.length() * k / 2))))]
    g = Polygon(pts)
    return g if g.is_valid else g.buffer(0)


def flag_colour(region):
    img = Image.new('1', (N, N), 0)
    d = ImageDraw.Draw(img)
    for g in (region.geoms if hasattr(region, 'geoms') else [region]):
        if g.is_empty or g.geom_type != 'Polygon':
            continue
        d.polygon(list(g.exterior.coords), fill=1)
        for r in g.interiors:
            d.polygon(list(r.coords), fill=0)
    m = np.asarray(img)
    if m.sum() == 0:
        return BLACK
    ref = {BLACK: (0, 0, 0), FIELD: (0x9b, 0, 0), GOLD: (0xff, 0xcd, 0), BLUE: (0, 0x85, 0xeb)}
    px = flag[m]
    near = np.argmin([np.abs(px - np.array(v)).sum(1) for v in ref.values()], axis=0)
    return list(ref)[Counter(near.tolist()).most_common(1)[0][0]]


def absd(segs):
    """absolute path data for svgelements segments (its own Subpath.d() loses the current point)"""
    o = []
    for g in segs:
        if isinstance(g, Move):
            o.append(f'M{g.end.x:.4f},{g.end.y:.4f}')
        elif isinstance(g, Close):
            o.append('Z')
        elif isinstance(g, Line):
            o.append(f'L{g.end.x:.4f},{g.end.y:.4f}')
        elif isinstance(g, CubicBezier):
            o.append(f'C{g.control1.x:.4f},{g.control1.y:.4f} {g.control2.x:.4f},{g.control2.y:.4f} '
                     f'{g.end.x:.4f},{g.end.y:.4f}')
        elif isinstance(g, QuadraticBezier):
            o.append(f'Q{g.control.x:.4f},{g.control.y:.4f} {g.end.x:.4f},{g.end.y:.4f}')
        else:
            raise ValueError(type(g))
    return ''.join(o)


def split_black(d):
    subs = [absd(list(s)) for s in Path(d).as_subpaths()]
    polys = [poly(Path(s)) for s in subs]
    reps = [p.representative_point() if not p.is_empty else Point(-1, -1) for p in polys]
    # depth = how many other subpaths contain this one; even depth = filled outline, odd = hole of its parent
    parent = {}
    for i, r in enumerate(reps):
        cont = [j for j, q in enumerate(polys) if j != i and not q.is_empty and q.area > polys[i].area and q.contains(r)]
        depth = len(cont)
        if depth % 2:
            parent[i] = min(cont, key=lambda j: polys[j].area)
    groups = {}
    for i in range(len(subs)):
        if i in parent:
            continue
        holes = [j for j, p in parent.items() if p == i]
        region = polys[i]
        for j in holes:
            region = region.difference(polys[j])
        c = flag_colour(region)
        groups.setdefault(c, []).extend([i] + holes)
    return {c: ''.join(subs[i] for i in idx) for c, idx in groups.items()}


m = re.search(r'<path\s+style="fill:#000000[^"]*"\s+d="([^"]+)"', svg)
parts = split_black(m.group(1))
print({c: d.count('M') + d.count('m') for c, d in parts.items()})
paths = []
for col, d in re.findall(r'<path\s+style="fill:(#[0-9a-fA-F]{6})[^"]*"\s+d="([^"]+)"', svg):
    if col.lower() == '#000000':
        for c in (GOLD, FIELD, BLACK):  # gold islands first, then red lettering, black outlines on top
            if c in parts:
                paths.append(f'<path fill="{c}" fill-rule="evenodd" d="{parts[c]}"/>')
    else:
        paths.append(f'<path fill="{RECOLOUR[col.lower()]}" fill-rule="evenodd" d="{d}"/>')
corner = [(95, 95), (N - 95, 95), (95, N - 95), (N - 95, N - 95)]
frame = (f'<path d="M95,63.5H{N - 95}M{N - 63.5},95V{N - 95}M{N - 95},{N - 63.5}H95M63.5,{N - 95}V95" fill="none" '
         f'stroke="{GOLD}" stroke-width="11"/>' +
         ''.join(f'<circle cx="{x}" cy="{y}" r="31.5" fill="none" stroke="{GOLD}" stroke-width="11"/>' for x, y in corner))
out = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{N}" height="{N}" viewBox="0 0 {N} {N}">\n'
       f'<rect width="{N}" height="{N}" fill="{FIELD}"/>\n{frame}\n'
       f'<g transform="translate({OX},{OY}) scale({k:.6f}) translate({GT[0]},{GT[1]})">\n' + '\n'.join(paths) +
       '\n</g>\n</svg>\n')
open(OUT, 'w', encoding='utf8').write(out)
print('wrote', OUT)
