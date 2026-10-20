"""Rebuild File:The Letter "i" in Different European Languages.png from its stated source, File:Blank map of Europe
cropped.svg (its current revision; the PNG was painted over a 2017 render of it):
  - framed to the PNG (scale and offset fitted on the land masks, IoU 0.91);
  - each country filled with the colour the PNG paints it (majority vote of the PNG's palette colours under the
    country; countries it leaves unpainted in the PNG's grey);
  - Wales, which the PNG paints apart from the rest of the UK but the map does not divide, from Natural Earth 10m
    admin-1 (the Welsh units, public domain) in a Lambert azimuthal equal-area projection fitted to the map's own UK
    (IoU 0.94), inserted beside the UK in the same coordinate space;
  - the IPA labels as real <text> fitted to the PNG's lettering.
Run from the repo root (after fit_wales.py); `fit` refits the frame, the colours and the labels (cached in
params.json)."""
import io, json, re, sys
import numpy as np, resvg_py
from PIL import Image, ImageDraw
from scipy import optimize

sys.path.insert(0, 'tools')

SRC = 'data_lake/downloads/letter-i/Blank map of Europe cropped.svg'
PNG = 'data_lake/downloads/letter-i/The Letter i in Different European Languages.png'
NE = 'data_lake/downloads/natural-earth/ne_10m_admin_1_states_provinces.geojson'
OUT = 'files/letter-i/The Letter i in Different European Languages.svg'
PAR = 'files/letter-i/params.json'
PAL = {'grey': '#7f7f7f', 'steel': '#7092be', 'blue': '#00a2e8', 'beige': '#efe4b0', 'cyan': '#99d9ea', 'lavender': '#c8bfe7'}
LABELS = ['[iː]', '[ɪː]', '[ɪ]', '[aɪ]', '[i]', '[iː]', '[ɪ]', '[i]', '[i]', '[i]']  # in the order of the PNG's label boxes, top to bottom
WALES_COLOUR = 'blue'
VBW = 1613.0037

s = open(SRC, encoding='utf8').read()
p = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
H, W = p.shape[:2]


def group_span(s, gid):
    st = s.rfind('<g', 0, s.index(f'id="{gid}"'))
    if s[s.index('>', st) - 1] == '/':
        return None
    depth, j = 0, st
    pat = re.compile(r'<(/?)g\b([^>]*)>')
    while True:
        mm = pat.search(s, j)
        if mm.group(1) == '' and not mm.group(2).rstrip().endswith('/'):
            depth += 1
        elif mm.group(1) == '/':
            depth -= 1
        j = mm.end()
        if depth == 0:
            return st, j


def country_ids(s):
    out = []
    for m in re.finditer(r'<g\b[^>]*\bid="(g[A-Z]{3})"', s):
        sp = group_span(s, m.group(1))
        if sp and not any(a <= sp[0] < b for _, (a, b) in out):
            out.append((m.group(1), sp))
    return out


def recolour(s, colours):
    """every shape of each country group gets an explicit fill (overriding its class) and keeps its stroke"""
    spans = sorted(country_ids(s), key=lambda t: t[1][0])
    pieces, last = [], 0
    for gid, (a, b) in spans:
        if a < last:
            continue
        c = colours.get(gid)
        blk = s[a:b]
        if c:
            blk = re.sub(r'<(path|polygon|rect|circle|ellipse)\b([^>]*?)(/?)>',
                         lambda m: f'<{m.group(1)}{re.sub(r"\sstyle=\"[^\"]*\"", "", m.group(2))} style="fill:{c}"{m.group(3)}>', blk)
        pieces += [s[last:a], blk]
        last = b
    pieces.append(s[last:])
    return ''.join(pieces)


def framed(svg, F):
    head = re.search(r'<svg\b[^>]*>', svg, re.S).group(0)
    new = re.sub(r'\s(width|height|viewBox)="[^"]*"', '', head)
    new = new[:-1] + (f' width="{W}" height="{H}" viewBox="{-F["tx"] / F["sc"]:.3f} {-F["ty"] / F["sc"]:.3f} '
                      f'{W / F["sc"]:.3f} {H / F["sc"]:.3f}">')
    return svg.replace(head, new, 1)


def render(svg, **kw):
    r = Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=svg, **kw)))).convert('RGBA')
    return np.asarray(r).astype(int)


def fit_frame():
    land_s = render(s, width=int(VBW))
    land_s = (land_s[..., 3] > 0) & (land_s[..., :3].min(2) < 245)
    land_p = p.min(2) < 250

    def loss(q):
        sc, tx, ty = q
        yy, xx = np.mgrid[0:H:2, 0:W:2]
        u, v = (xx - tx) / sc, (yy - ty) / sc
        ok = (u >= 0) & (u < land_s.shape[1] - 1) & (v >= 0) & (v < land_s.shape[0] - 1)
        m = np.zeros(u.shape, bool); m[ok] = land_s[v[ok].astype(int), u[ok].astype(int)]
        t = land_p[::2, ::2]
        return 1 - (m & t).sum() / (m | t).sum()
    r = optimize.minimize(loss, [1.6067, -100.36, -210.25], method='Nelder-Mead', options={'maxiter': 300, 'xatol': 1e-3, 'fatol': 1e-6})
    print('frame IoU %.3f' % (1 - r.fun))
    return dict(sc=r.x[0], tx=r.x[1], ty=r.x[2])


def vote_colours(F):
    ids = country_ids(s)
    code = {gid: '#%02x%02x07' % ((k + 1) // 256, (k + 1) % 256) for k, (gid, _) in enumerate(ids)}
    r = render(framed(recolour(s, code), F))
    idx = r[..., 0] * 256 + r[..., 1]
    ok = (r[..., 2] == 7) & (r[..., 3] == 255)
    pal = {k: np.array([int(v[i:i + 2], 16) for i in (1, 3, 5)]) for k, v in PAL.items()}
    out = {}
    for gid, c in code.items():
        m = ok & (idx == int(c[1:3], 16) * 256 + int(c[3:5], 16))
        if m.sum() < 30:
            continue
        cnt = {k: int((np.abs(p[m] - v).sum(1) < 20).sum()) for k, v in pal.items()}
        if sum(cnt.values()) >= 20:
            out[gid] = max(cnt, key=cnt.get)
    return out


def wales_path(geo):
    """Natural Earth's Wales in the map's units: LAEA (52N 10E) and a fitted scale and offset against the map's UK"""
    from pyproj import Transformer
    from shapely.geometry import shape
    from shapely.ops import unary_union, transform as stransform
    fc = json.load(open(NE, encoding='utf8'))
    uk = [f for f in fc['features'] if f['properties']['adm0_a3'] == 'GBR']
    T = Transformer.from_crs('EPSG:4326', '+proj=laea +lat_0=52 +lon_0=10 +ellps=WGS84', always_xy=True)
    wl = stransform(lambda x, y, z=None: T.transform(x, y),
                    unary_union([shape(f['geometry']) for f in uk if f['properties'].get('geonunit') == 'Wales']).buffer(0))
    sc, tx, ty = geo
    return ''.join('M' + ' '.join(f'{x * sc + tx:.2f},{-y * sc + ty:.2f}' for x, y in q.exterior.coords) + 'Z'
                   for q in (wl.geoms if hasattr(wl, 'geoms') else [wl]) if q.area * sc * sc > 0.5)


def fit_labels():
    from fit_text import fit
    from scipy import ndimage
    black = p.max(2) < 90
    lab, n = ndimage.label(ndimage.binary_dilation(black, np.ones((15, 25))))
    boxes = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        m = (lab[sl] == i) & black[sl]
        if m.sum() < 100:
            continue
        ys, xs = np.nonzero(m)
        boxes.append((sl[1].start + xs.min(), sl[1].start + xs.max(), sl[0].start + ys.min(), sl[0].start + ys.max()))
    boxes.sort(key=lambda b: (b[2], b[0]))
    assert len(boxes) == len(LABELS), boxes
    return [dict(text=t, **{k: fit(t, b, 'Calibri', 'normal', canvas=(W, H))[k] for k in ('x', 'y', 'size', 'ls')})
            for t, b in zip(LABELS, boxes)]


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'fit':
        F = fit_frame()
        P = dict(frame=F, colours=vote_colours(F), wales=json.load(open('files/letter-i/wales_fit.json'))['p'], labels=fit_labels())
        json.dump(P, open(PAR, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    P = json.load(open(PAR, encoding='utf8'))
    colours = {gid: PAL['grey'] for gid, _ in country_ids(s)}
    colours.update({gid: PAL[c] for gid, c in P['colours'].items()})
    out = framed(recolour(s, colours), P['frame'])
    # land outside the country groups and the lakes, in the PNG's greys
    out = re.sub(r'fill:#b9b9b9', 'fill:#7f7f7f', out, flags=re.I)
    out = re.sub(r'fill:#cccccc', 'fill:#e0e0e0', out, flags=re.I)
    a, b = group_span(out, 'gGBR')
    out = out[:b] + f'<path id="Wales" d="{wales_path(P["wales"])}" style="fill:{PAL[WALES_COLOUR]};stroke:#ffffff;stroke-width:0.6"/>' + out[b:]
    texts = ''.join(f'<text x="{q["x"]}" y="{q["y"]}" font-size="{q["size"]}" fill="#000000">{q["text"]}</text>' for q in P['labels'])
    # labels in PNG pixels, outside the map's viewBox: an inner svg in PNG pixel units
    k = out.rindex('</svg>')
    out = (out[:k] + f'<svg x="{-P["frame"]["tx"] / P["frame"]["sc"]:.3f}" y="{-P["frame"]["ty"] / P["frame"]["sc"]:.3f}" '
           f'width="{W / P["frame"]["sc"]:.3f}" height="{H / P["frame"]["sc"]:.3f}" viewBox="0 0 {W} {H}">'
           f'<g font-family="Calibri, Carlito, \'DejaVu Sans\', sans-serif">{texts}</g></svg>' + out[k:])
    open(OUT, 'w', encoding='utf8').write(out)
    print('wrote', OUT, len(P['colours']), 'countries coloured')
