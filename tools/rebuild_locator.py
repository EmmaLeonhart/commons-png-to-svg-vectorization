"""Rebuild a PNG locator map from the SVG it was made from (no tracing).

usage: python tools/rebuild_locator.py TARGET.png BASE.svg OUT.svg [--land-fill COLOUR]

Steps: give every land unit in BASE a unique flat colour and render it; register the
PNG against that render (scale + offset, FFT search then local refinement); read each
unit's fill and outline colour from the PNG; write BASE cropped to the PNG's extent
with those colours. Assumes the Inkscape structure of the Commons "Provinces of
Japan" family: land units are elements with a fill style, coast strokes in their own
layer. Prints a JSON report (transform, agreement, highlighted units).
"""
import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from lxml import etree
from numpy.fft import irfft2, rfft2
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from render_svg import render  # noqa: E402

NS = 'http://www.w3.org/2000/svg'
Q = lambda t: f'{{{NS}}}{t}'
STYLE_FILL = re.compile(r'fill:(#[0-9a-fA-F]{6}|[a-z]+)')


def style_get(el, key):
    m = re.search(rf'(?:^|;){key}:([^;]*)', el.get('style', ''))
    return m.group(1).strip() if m else el.get(key)


def restyle(el, **props):
    st = el.get('style', '')
    for k, v in props.items():
        k = k.replace('_', '-')
        if re.search(rf'(^|;){k}:', st):
            st = re.sub(rf'(^|;){k}:[^;]*', rf'\g<1>{k}:{v}', st)
        else:
            st = f'{st};{k}:{v}' if st else f'{k}:{v}'
    el.set('style', st)


def hexc(c):
    return '#%02x%02x%02x' % tuple(int(x) for x in c)


def land_units(root, land_fill):
    """Top-level land elements: elements with the land fill whose ancestors don't have it."""
    out = []
    for el in root.iter(Q('g'), Q('path')):
        if style_get(el, 'fill') == land_fill and not any(style_get(a, 'fill') == land_fill for a in el.iterancestors()):
            out.append(el)
    return out


def id_render(base, land_fill, scale, work):
    tree = etree.parse(str(base))
    root = tree.getroot()
    units = land_units(root, land_fill)
    for el in root.iter(Q('g'), Q('path'), Q('rect'), Q('text')):
        st = el.get('style', '')
        if el not in units and not any(a in units for a in el.iterancestors()):
            if el.tag in (Q('path'), Q('rect'), Q('text')) and 'display:none' not in st:
                if style_get(el, 'fill') in (None, 'none') or el.tag == Q('text'):
                    restyle(el, display='none')
                else:  # lakes and the background: not land
                    restyle(el, fill='#000000', stroke='none', fill_opacity='1', opacity='1')
    for k, el in enumerate(units, start=1):
        col = '#%02x%02x%02x' % (k // 256, k % 256, 200)
        for e in [el, *el.iter(Q('path'))]:
            restyle(e, fill=col, stroke='none', fill_opacity='1', opacity='1', shape_rendering='crispEdges')
    svg_path = work / 'ids.svg'
    tree.write(str(svg_path))
    png = work / 'ids.png'
    render(svg_path, png, scale)
    a = np.array(Image.open(png).convert('RGB')).astype(int)
    idx = np.where(a[..., 2] == 200, a[..., 0] * 256 + a[..., 1], 0)
    return idx, units


def register(target, idx, scale):
    T = target.astype(int)
    common = Counter(map(tuple, T[::3, ::3].reshape(-1, 3).tolist())).most_common(2)
    land_px = idx > 0
    # the two commonest colours are taken to be land and sea (which is which is tried both
    # ways); everything else (highlights, lines, text) is ignored when matching
    c1, c2 = (np.abs(T - np.array(c[0])).sum(2) < 20 for c in common)
    near_top = c1
    best = None
    H, W = T.shape[:2]
    src_lo = np.array(Image.fromarray(land_px.astype(np.uint8) * 255).resize(
        (land_px.shape[1] // scale, land_px.shape[0] // scale), Image.BILINEAR)).astype(float) / 127.5 - 1
    for polarity in (1, -1):
        tgt = (np.where(c1, -1.0, 0.0) + np.where(c2, 1.0, 0.0)) * polarity
        lo, hi = 0.02, max(src_lo.shape) / max(H, W) * 1.05
        for s in np.geomspace(lo, hi, 120):
            n_w, n_h = max(4, round(W * s)), max(4, round(H * s))
            if n_w > src_lo.shape[1] or n_h > src_lo.shape[0]:
                continue
            t = np.array(Image.fromarray((tgt + 1).astype(np.float32)).resize((n_w, n_h), Image.BILINEAR)) - 1
            P = (src_lo.shape[0] + n_h, src_lo.shape[1] + n_w)
            F = irfft2(rfft2(src_lo, P) * np.conj(rfft2(t, P)), P)
            F = F[:src_lo.shape[0] - n_h + 1, :src_lo.shape[1] - n_w + 1]
            i = np.unravel_index(np.argmax(F), F.shape)
            sc = F[i] / (n_w * n_h)
            if best is None or sc > best[0]:
                best = (sc, s, i[1], i[0], polarity)
    _, s, ox, oy, polarity = best
    tgt = (np.where(c1, -1, 0) + np.where(c2, 1, 0)) * polarity
    vv, uu = np.mgrid[0:H:max(1, H // 400), 0:W:max(1, W // 400)]
    t = tgt[vv, uu]
    keep = t != 0
    vv, uu, t = vv[keep], uu[keep], t[keep]

    def score(s, ox, oy):
        x = ((ox + s * uu) * scale).astype(int)
        y = ((oy + s * vv) * scale).astype(int)
        ok = (x >= 0) & (y >= 0) & (x < land_px.shape[1]) & (y < land_px.shape[0])
        v = np.where(land_px[y.clip(0, land_px.shape[0] - 1), x.clip(0, land_px.shape[1] - 1)] & ok, 1, -1)
        return (v == t).mean()

    import itertools
    cur = (score(s, ox, oy), s, ox, oy)
    for it in range(4):
        f = 3 ** it
        for ds, dx, dy in itertools.product(np.linspace(-0.04, 0.04, 9) * s / f, np.linspace(-2, 2, 9) / f, np.linspace(-2, 2, 9) / f):
            sc = score(cur[1] + ds, cur[2] + dx, cur[3] + dy)
            if sc > cur[0]:
                best_local = (sc, cur[1] + ds, cur[2] + dx, cur[3] + dy)
                cur = best_local
    return cur, polarity


def dist(a, b):
    return sum(abs(int(x) - int(y)) for x, y in zip(a, b))


def sample_colours(target, idx, xf, scale):
    """Per-unit fill (None = plain land) and outline, plus sea, land, coast, border colours."""
    from scipy import ndimage as nd
    agree, s, ox, oy = xf
    H, W = target.shape[:2]
    vv, uu = np.mgrid[0:H, 0:W]
    x = ((ox + s * uu) * scale).astype(int).clip(0, idx.shape[1] - 1)
    y = ((oy + s * vv) * scale).astype(int).clip(0, idx.shape[0] - 1)
    k = idx[y, x]
    T = target.astype(int)
    q = (T // 8) * 8 + 4                                  # quantised, for robust modes
    notdark = T.sum(2) > 200                              # skip text
    sea = Counter(map(tuple, q[(k == 0) & notdark].tolist())).most_common(1)[0][0]
    interior = nd.binary_erosion(k > 0, iterations=3) & notdark
    land = Counter(map(tuple, q[interior].tolist())).most_common(1)[0][0]

    def darkest(mask):
        px = T[mask]
        px = px[px.sum(1) > 60]          # skip black text
        if len(px) < 5:
            return None
        px = px[px.sum(1) <= np.percentile(px.sum(1), 25)]
        return tuple(int(c) for c in np.median(px, 0))

    fills, outlines = {}, {}
    for u in sorted(set(k.ravel()) - {0}):
        inner = nd.binary_erosion(k == u, iterations=3) & notdark
        if inner.sum() < 10:
            continue
        cnt = Counter(map(tuple, q[inner].tolist()))
        other = [(c, n) for c, n in cnt.most_common(6) if dist(c, land) > 30 and dist(c, (255, 255, 255)) > 30]
        if other and other[0][1] >= 0.15 * inner.sum():
            # exact colour: mode of the unquantised pixels in that bin
            fills[u] = Counter(map(tuple, T[inner & np.all(q == other[0][0], 2)].tolist())).most_common(1)[0][0]

    # coast and border colours come only from edges of plain (unhighlighted) units
    plain = (k > 0) & ~np.isin(k, list(fills))
    shift = lambda a, dy, dx: np.roll(np.roll(a, dy, 0), dx, 1)
    offs = ((2, 0), (-2, 0), (0, 2), (0, -2))
    nk = [shift(k, dy, dx) for dy, dx in offs]
    nplain = [shift(plain, dy, dx) for dy, dx in offs]
    coast_ring = plain & np.any([n == 0 for n in nk], 0)
    inner_ring = plain & np.any([(n != k) & p for n, p in zip(nk, nplain)], 0)
    coast, border = darkest(coast_ring), darkest(inner_ring)

    for u in fills:
        m = k == u
        o = darkest(m & ~nd.binary_erosion(m, iterations=2))
        if o and border and coast and dist(o, border) > 60 and dist(o, coast) > 60:
            outlines[u] = o
    exact = lambda c: Counter(map(tuple, T[np.all(q == c, 2)].tolist())).most_common(1)[0][0]
    return fills, outlines, exact(sea), exact(land), coast, border


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('target'); ap.add_argument('base'); ap.add_argument('out')
    ap.add_argument('--land-fill', default='#fcf5e3')
    ap.add_argument('--scale', type=int, default=4)
    ap.add_argument('--work', default='scratch/locator')
    a = ap.parse_args()
    work = Path(a.work); work.mkdir(parents=True, exist_ok=True)
    target = np.array(Image.open(a.target).convert('RGB'))
    idx, units = id_render(Path(a.base), a.land_fill, a.scale, work)
    xf, _ = register(target, idx, a.scale)
    fills, outlines, sea, land, coast, border = sample_colours(target, idx, xf, a.scale)

    # antialiasing shifts thin-line colours; keep the base map's own colour when close
    snap = lambda c, orig: orig if c and dist(c, orig) < 40 else c
    border = snap(border, (0x78, 0x78, 0x78))
    coast = snap(coast, (0x27, 0xaa, 0xea))
    sea = snap(sea, (0xda, 0xf0, 0xfd))
    land = snap(land, (0xfc, 0xf5, 0xe3))

    tree = etree.parse(a.base)
    root = tree.getroot()
    if root.get('viewBox'):
        raise SystemExit('base with viewBox not supported yet')
    units = land_units(root, a.land_fill)
    for el in root.iter(Q('g'), Q('path')):
        if style_get(el, 'fill') == a.land_fill:
            restyle(el, fill=hexc(land), **({'stroke': hexc(border)} if border else {}))
    highlighted = []
    for k, el in enumerate(units, start=1):
        if k in fills:
            extra = {'stroke': hexc(outlines[k])} if k in outlines else {}
            for e in [el, *el.iter(Q('path'))]:
                restyle(e, fill=hexc(fills[k]), **extra)
            highlighted.append(dict(id=el.get('id'), fill=hexc(fills[k]), outline=hexc(outlines[k]) if k in outlines else None))
    if coast:
        for el in root.iter(Q('g'), Q('path')):
            if style_get(el, 'stroke') == '#27aaea':
                restyle(el, stroke=hexc(coast))
    # other fills: lakes and background take the sea colour
    for el in root.iter(Q('path'), Q('rect')):
        if style_get(el, 'fill') == '#daf0fd':
            restyle(el, fill=hexc(sea))
    agree, s, ox, oy = xf
    H, W = target.shape[:2]
    root.set('viewBox', f'{ox:.4f} {oy:.4f} {W * s:.4f} {H * s:.4f}')
    root.set('width', str(W)); root.set('height', str(H))
    tree.write(a.out, xml_declaration=True, encoding='UTF-8')
    report = dict(agreement=round(float(agree), 4), scale=float(s), offset=[float(ox), float(oy)],
                  sea=hexc(sea), land=hexc(land), coast=hexc(coast) if coast else None, border=hexc(border) if border else None,
                  highlighted=highlighted)
    print(json.dumps(report, indent=1))


if __name__ == '__main__':
    main()
