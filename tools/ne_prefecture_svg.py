"""Write one Japanese prefecture from Natural Earth admin-1 (public domain) as an SVG in
plain longitude/latitude (x = lon, y = -lat, scaled by 1000). This is the projection of
Shigenobu Aoki's "Shadow picture" PNGs, so tools/rebuild_flagmap.py only has to fit
scale and offset. usage: python tools/ne_prefecture_svg.py NAME OUT.svg
"""
import json
import sys
from pathlib import Path

NE = Path('data_lake/downloads/natural-earth/ne_10m_admin_1_states_provinces.geojson')
_cache = {}


def prefecture_svg(name, out, k=1000):
    if 'd' not in _cache:
        _cache['d'] = json.loads(NE.read_text(encoding='utf8'))
    norm = lambda s: s.lower().translate(str.maketrans('ōū', 'ou'))
    f = next(f for f in _cache['d']['features']
             if f['properties'].get('adm0_a3') == 'JPN' and norm(f['properties']['name']) == norm(name))
    g = f['geometry']
    polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
    xs = [x for p in polys for r in p for x, _ in r]
    ys = [y for p in polys for r in p for _, y in r]
    d = ' '.join('M' + ' L'.join(f'{x * k:.2f},{-y * k:.2f}' for x, y in ring) + 'Z' for poly in polys for ring in poly)
    pad = 0.05 * k * max(max(xs) - min(xs), max(ys) - min(ys))
    vb = (min(xs) * k - pad, -max(ys) * k - pad, (max(xs) - min(xs)) * k + 2 * pad, (max(ys) - min(ys)) * k + 2 * pad)
    Path(out).write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" viewBox="{" ".join(f"{v:.2f}" for v in vb)}">'
        f'<path id="pref" d="{d}" fill="#000000" fill-rule="evenodd"/></svg>', encoding='utf8')
    return f['properties']['name']


if __name__ == '__main__':
    print(prefecture_svg(sys.argv[1], sys.argv[2]))
