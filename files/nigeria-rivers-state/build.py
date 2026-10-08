"""Rebuild File:Nigeria Rivers State map.png from the revision of File:Nigeria location map.svg
it was made from (2010-02-11). That revision has no state polygons, only border lines, so
the Rivers State polygon is cut out of the land shape along those lines (the piece under
the PNG's red area) and inserted between the land and the borders.
Run from the repo root: python files/nigeria-rivers-state/build.py
"""
import re
from pathlib import Path

import numpy as np
import svgelements as se
from PIL import Image
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

HERE = Path(__file__).parent
DL = Path('data_lake/downloads/nigeria-rivers-state')
SRC = DL / 'Nigeria location map (2010-02-11 revision).svg'
PNG = DL / 'Nigeria Rivers State map.png'
OUT = HERE / 'Nigeria Rivers State map.svg'
FILL = '#c00000'  # read from the PNG


def pts(path, tol=0.2):
    out = []
    for seg in path:
        if isinstance(seg, se.Move):
            out.append([(seg.end.x, seg.end.y)])
        elif isinstance(seg, (se.Line, se.Close)):
            if seg.end is not None:
                out[-1].append((seg.end.x, seg.end.y))
        else:
            n = max(2, int(seg.length() / tol))
            out[-1] += [(p.x, p.y) for p in (seg.point(t / n) for t in range(1, n + 1))]
    return [o for o in out if len(o) >= 2]


def main():
    svg = se.SVG.parse(str(SRC), reify=True)
    land, cuts = [], []  # cuts: state lines, national border and rivers
    for e in svg.elements():
        if not isinstance(e, se.Shape):
            continue
        style = str(e.values.get('style', ''))
        p = se.Path(e)
        if 'fill:#fefee4' in style and 'stroke:none' in style:
            land += [Polygon(r).buffer(0) for r in pts(p) if len(r) >= 3]
        elif ('stroke:#808080' in style and 'stroke-width:1.5' in style) or 'stroke:#646464' in style                 or ('fill:none' in style and 'stroke:#0978ab' in style):
            cuts += [LineString(r) for r in pts(p)]
    land = unary_union(land)
    # The PNG's red area was flood-filled, so it stops at rivers as well as borders: cut the
    # land along all of those lines and keep every piece that is mostly red in the PNG.
    T = np.array(Image.open(PNG).convert('RGB')).astype(int)
    red = (T[..., 0] > 150) & (T[..., 1] < 60) & (T[..., 2] < 60)
    k = float(svg.width) / T.shape[1]
    gap = 1.0
    pieces = land.difference(unary_union(cuts).buffer(gap))
    pieces = list(pieces.geoms) if hasattr(pieces, 'geoms') else [pieces]
    keep = []
    for g in pieces:
        x0, y0, x1, y1 = g.bounds
        xs = np.arange(int(x0 / k), int(x1 / k) + 1); ys = np.arange(int(y0 / k), int(y1 / k) + 1)
        inside = [(x, y) for y in ys for x in xs if 0 <= x < T.shape[1] and 0 <= y < T.shape[0]
                  and g.contains(Point((x + 0.5) * k, (y + 0.5) * k))]
        if inside and np.mean([red[y, x] for x, y in inside]) > 0.5:
            keep.append(g)
    rivers = unary_union([g.buffer(gap) for g in keep]).intersection(land)
    polys = list(rivers.geoms) if hasattr(rivers, 'geoms') else [rivers]
    d = ' '.join('M' + ' L'.join(f'{x:.2f},{y:.2f}' for x, y in list(ring.coords)[:-1]) + 'Z'
                 for p in polys for ring in [p.exterior, *p.interiors])
    s = SRC.read_text(encoding='utf8')
    m = re.search(r'<path[^>]*fill:#fefee4;stroke:none[^>]*/>', s, re.S)
    new = (f'\n  <path id="rivers-state" d="{d}" style="fill:{FILL};fill-rule:evenodd;stroke:none">'
           f'<title>Rivers State</title></path>')
    OUT.write_text(s[:m.end()] + new + s[m.end():], encoding='utf8')
    print(OUT, f'{len(keep)} pieces kept, area {rivers.area:.0f}')


if __name__ == '__main__':
    main()
