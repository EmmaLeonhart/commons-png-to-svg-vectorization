"""Kagoshima Prefecture outline for the geo-stub, from MLIT N03 (2024) via tools/n03_prefecture_svg.py,
limited to the islands the PNG shows (north of 30.0 N: the mainland, Koshikijima, Tanegashima, Yakushima,
Kuchinoerabu, Mishima; not Tokara or Amami). Writes data_lake/downloads/kagoshima-geo-stub/outline.svg."""
import sys
from pathlib import Path
from shapely.geometry import box, shape
from shapely.ops import unary_union
sys.path.insert(0, 'tools')
import n03_prefecture_svg as N

d = N.load(46)
geom = unary_union([shape(f['geometry']).simplify(0.000125, preserve_topology=True).buffer(0) for f in d['features']])
geom = geom.buffer(1e-6).buffer(-1e-6).intersection(box(129.0, 30.0, 132.0, 33.0)).simplify(0.0005, preserve_topology=True)
polys = [p for p in getattr(geom, 'geoms', [geom]) if p.area > 1e-5]
k = 1000
parts = []
for p in polys:
    for ring in [p.exterior, *p.interiors]:
        parts.append('M' + ' L'.join(f'{x * k:.2f},{-y * k:.2f}' for x, y in list(ring.coords)[:-1]) + 'Z')
x0, y0, x1, y1 = unary_union(polys).bounds
pad = 0.05 * max(x1 - x0, y1 - y0)
vb = ((x0 - pad) * k, -(y1 + pad) * k, (x1 - x0 + 2 * pad) * k, (y1 - y0 + 2 * pad) * k)
Path('data_lake/downloads/kagoshima-geo-stub/outline.svg').write_text(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" viewBox="{" ".join(f"{v:.2f}" for v in vb)}">'
    f'<g id="pref"><path d="{" ".join(parts)}" fill="#000000" fill-rule="evenodd"/></g></svg>', encoding='utf8')
print(len(polys), 'polygons')
