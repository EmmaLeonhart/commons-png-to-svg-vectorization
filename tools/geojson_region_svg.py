"""Write a (Multi)Polygon from a GeoJSON file as an SVG path in plain longitude/latitude (x = lon,
y = -lat, scaled by 1000), for fitting with tools/rebuild_flagmap.py (path id "pref"). Accepts a
FeatureCollection, a Feature, a bare geometry, or a Nominatim result list (picks --index).
usage: python tools/geojson_region_svg.py IN.json OUT.svg [--index N]
"""
import argparse
import json
from pathlib import Path


def geometry(obj, index=0):
    if isinstance(obj, list):  # Nominatim search result
        return obj[index]['geojson']
    if obj.get('type') == 'FeatureCollection':
        return obj['features'][index]['geometry']
    if obj.get('type') == 'Feature':
        return obj['geometry']
    return obj


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src'); ap.add_argument('out'); ap.add_argument('--index', type=int, default=0)
    a = ap.parse_args()
    g = geometry(json.loads(Path(a.src).read_text(encoding='utf8')), a.index)
    polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
    k = 1000
    xs = [x for p in polys for r in p for x, _ in r]
    ys = [y for p in polys for r in p for _, y in r]
    d = ' '.join('M' + ' L'.join(f'{x * k:.3f},{-y * k:.3f}' for x, y in ring) + 'Z' for poly in polys for ring in poly)
    pad = 0.05 * k * max(max(xs) - min(xs), max(ys) - min(ys))
    vb = (min(xs) * k - pad, -max(ys) * k - pad, (max(xs) - min(xs)) * k + 2 * pad, (max(ys) - min(ys)) * k + 2 * pad)
    Path(a.out).write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" viewBox="{" ".join(f"{v:.2f}" for v in vb)}">'
        f'<path id="pref" d="{d}" fill="#000000" fill-rule="evenodd"/></svg>', encoding='utf8')
    print(a.out, sum(len(r) for p in polys for r in p), 'points')


if __name__ == '__main__':
    main()
