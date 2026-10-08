"""Write one Japanese prefecture from MLIT 国土数値情報 N03 (administrative areas) as an SVG
in plain longitude/latitude (x = lon, y = -lat, scaled by 1000), the projection of
Shigenobu Aoki's "Shadow picture" PNGs. Municipal polygons are merged into the
prefecture outline and simplified to `tol` degrees.
Data: https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2024.html (CC BY 4.0-compatible
terms; credit 「国土数値情報（行政区域データ）」（国土交通省）).
usage: python tools/n03_prefecture_svg.py CODE OUT.svg [tol]
"""
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

from shapely.geometry import shape
from shapely.ops import unary_union

DL = Path('data_lake/downloads/n03')
URL = 'https://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2024/N03-20240101_{code:02d}_GML.zip'


def load(code):
    z = DL / f'N03-20240101_{code:02d}_GML.zip'
    if not z.exists():
        DL.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(URL.format(code=code), headers={'User-Agent': 'agentic-vectorization/0.1'})
        z.write_bytes(urllib.request.urlopen(req, timeout=300).read())
    with zipfile.ZipFile(z) as zf:
        name = next(n for n in zf.namelist() if n.endswith('.geojson') and 'subprefecture' not in n)
        return json.loads(zf.read(name).decode('utf8'))


def prefecture_svg(code, out, tol=0.0005, k=1000):
    d = load(code)
    # simplify each municipality before merging, and drop the parsed JSON early: Hokkaido's
    # 44 MB of GeoJSON merged at full detail is the likely cause of a low-memory stop
    feats = [shape(f['geometry']).simplify(tol / 4, preserve_topology=True).buffer(0) for f in d['features']]
    del d
    geom = unary_union(feats)
    del feats
    geom = geom.buffer(1e-6).buffer(-1e-6)  # close hairline gaps between municipalities
    geom = geom.simplify(tol, preserve_topology=True)
    polys = list(geom.geoms) if hasattr(geom, 'geoms') else [geom]
    big = max(p.area for p in polys)
    polys = [p for p in polys if p.area > 1e-4 * big]
    parts = []
    for p in polys:
        for ring in [p.exterior, *p.interiors]:
            c = list(ring.coords)[:-1]
            parts.append('M' + ' L'.join(f'{x * k:.2f},{-y * k:.2f}' for x, y in c) + 'Z')
    x0, y0, x1, y1 = unary_union(polys).bounds
    pad = 0.05 * max(x1 - x0, y1 - y0)
    vb = ((x0 - pad) * k, -(y1 + pad) * k, (x1 - x0 + 2 * pad) * k, (y1 - y0 + 2 * pad) * k)
    Path(out).write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" viewBox="{" ".join(f"{v:.2f}" for v in vb)}">'
        f'<path id="pref" d="{" ".join(parts)}" fill="#000000" fill-rule="evenodd"/></svg>', encoding='utf8')
    return sum(len(p.exterior.coords) for p in polys)


if __name__ == '__main__':
    print(prefecture_svg(int(sys.argv[1]), sys.argv[2], *(float(a) for a in sys.argv[3:4])))
