"""Rebuild File:Eastern Europe (Robinson projection).png from the world map it descends from: BlankMap-World6.svg
(now BlankMap-World.svg) as of 2011-01-03, the revision current when the PNG was made. Countries in that file are
styled by CSS class (landxx), so this renders an index image of them, registers it against the PNG with
tools/rebuild_locator.register (scale + offset), samples each country's colour, and writes the base SVG cropped to
the PNG's window with those colours. Run from the repo root."""
import re, sys
from collections import Counter
from pathlib import Path

import numpy as np
from lxml import etree
from PIL import Image

sys.path.insert(0, 'tools')
from rebuild_locator import register  # noqa: E402
from render_svg import render  # noqa: E402

PNG = 'data_lake/downloads/eastern-europe-robinson/Eastern Europe (Robinson projection).png'
BASE = 'data_lake/downloads/eastern-europe-robinson/BlankMap-World6 (2010 revision).svg'
OUT = 'files/eastern-europe-robinson/Eastern Europe (Robinson projection).svg'
WORK = Path('scratch/eeu')
SCALE = 2
NS = '{http://www.w3.org/2000/svg}'


def countries(root):
    """Top-level land units: elements whose class has landxx and that have no landxx ancestor."""
    out = []
    for el in root.iter():
        if not isinstance(el.tag, str) or 'landxx' not in (el.get('class') or ''):
            continue
        if any('landxx' in (a.get('class') or '') for a in el.iterancestors()):
            continue
        out.append(el)
    return out


def id_render():
    tree = etree.parse(BASE)
    root = tree.getroot()
    for st in root.iter(NS + 'style'):
        st.getparent().remove(st)
    units = countries(root)
    css = ['* { fill: none; stroke: none; }']
    for k, u in enumerate(units, start=1):
        u.set('data-k', str(k))
        css.append(f'[data-k="{k}"], [data-k="{k}"] * {{ fill: #{k // 256:02x}{k % 256:02x}c8 !important; '
                   'stroke: none !important; opacity: 1 !important; shape-rendering: crispEdges !important; }')
    st = etree.SubElement(root, NS + 'style')
    st.text = '\n'.join(css)
    root.insert(0, st)
    WORK.mkdir(parents=True, exist_ok=True)
    tree.write(str(WORK / 'ids.svg'))
    render(WORK / 'ids.svg', WORK / 'ids.png', SCALE)
    a = np.array(Image.open(WORK / 'ids.png').convert('RGB')).astype(int)
    return np.where(a[..., 2] == 200, a[..., 0] * 256 + a[..., 1], 0), units


def hexc(c):
    return '#%02x%02x%02x' % tuple(c)


if __name__ == '__main__':
    target = np.array(Image.open(PNG).convert('RGB'))
    H, W = target.shape[:2]
    idx, units = id_render()
    vb = [float(v) for v in etree.parse(BASE).getroot().get('viewBox').split()]
    xf = register(target, idx, SCALE)
    agree, s, ox, oy = xf
    print('agreement %.4f, %.4f base units per PNG px, offset %.1f, %.1f' % (agree, s, ox, oy))
    # two land colours: grey (plain) and green (Eastern Europe); classify each country by its interior pixels
    from scipy import ndimage as nd
    vv, uu = np.mgrid[0:H, 0:W]
    kk = idx[((oy + s * vv) * SCALE).astype(int).clip(0, idx.shape[0] - 1),
             ((ox + s * uu) * SCALE).astype(int).clip(0, idx.shape[1] - 1)]
    T = target.astype(int)
    green = (T[..., 1] - T[..., 0] > 25) & (T[..., 1] - T[..., 2] > 25)
    greyish = (np.abs(T[..., 0] - T[..., 1]) < 8) & (np.abs(T[..., 1] - T[..., 2]) < 8) & (T.sum(2) < 700) & (T.sum(2) > 300)
    mode = lambda m: Counter(map(tuple, T[m].tolist())).most_common(1)[0][0]
    G, L = mode(green), mode(greyish & (kk > 0))
    sea = mode(kk == 0)
    fills = {}
    for u in sorted(set(kk.ravel()) - {0}):
        inner = nd.binary_erosion(kk == u, iterations=3)
        if inner.sum() >= 10 and green[inner].mean() > 0.5:
            fills[u] = G
    land, border = L, (255, 255, 255)
    print('sea', hexc(sea), 'land', hexc(land), 'green', hexc(G), 'highlighted', len(fills))
    tree = etree.parse(BASE)
    root = tree.getroot()
    us = countries(root)
    hl = []
    for k, u in enumerate(us, start=1):
        if k in fills:
            hl.append(u.get('id'))
            u.set('style', f'fill:{hexc(fills[k])}')
            for c in u.iter():
                if c is not u and isinstance(c.tag, str):
                    c.set('style', f'fill:{hexc(fills[k])}')
    # register() works in rendered px (the SVG's width x height); the viewBox has another aspect ratio, so it is
    # fitted with preserveAspectRatio's default (uniform 'meet' scale, centred)
    bw, bh = float(root.get('width')), float(root.get('height'))
    k = min(bw / vb[2], bh / vb[3])
    dx, dy = (bw - vb[2] * k) / 2, (bh - vb[3] * k) / 2
    ox, oy, s = vb[0] + (ox - dx) / k, vb[1] + (oy - dy) / k, s / k
    root.set('viewBox', f'{ox:.3f} {oy:.3f} {W * s:.3f} {H * s:.3f}')
    root.set('width', str(W))
    root.set('height', str(H))
    bg = etree.Element(NS + 'rect', x=f'{ox:.3f}', y=f'{oy:.3f}', width=f'{W * s:.3f}', height=f'{H * s:.3f}',
                       fill=hexc(sea))
    first = [c for c in root if isinstance(c.tag, str) and c.tag not in (NS + 'defs', NS + 'style')][0]
    first.addprevious(bg)
    for st in root.iter(NS + 'style'):  # plain land and borders in the PNG's colours
        st.text = re.sub(r'(\.landxx\s*\{[^}]*?fill:)#[0-9a-fA-F]{6}', r'\g<1>' + hexc(land), st.text)
        if border:
            st.text = re.sub(r'(\.landxx\s*\{[^}]*?stroke:)#[0-9a-fA-F]{6}', r'\g<1>' + hexc(border), st.text)
    tree.write(OUT, xml_declaration=True, encoding='UTF-8')
    print('highlighted:', ' '.join(sorted(x or '?' for x in hl)))
