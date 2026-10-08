"""Rebuild a PNG "flag map" (a region's silhouette filled with its flag) from vector sources.

usage: python tools/rebuild_flagmap.py TARGET.png OUTLINE.svg GROUP_ID FLAG.svg OUT.svg

OUTLINE.svg holds the region as the paths under element GROUP_ID (their union is the
silhouette). The silhouette is fitted to the PNG's opaque pixels (uniform scale +
offset), then the flag is fitted inside it by matching the PNG's colours, and an
outline is added when the PNG has one. Prints a JSON report.
"""
import copy
import itertools
import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from lxml import etree
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from render_svg import render  # noqa: E402

NS = 'http://www.w3.org/2000/svg'
Q = lambda t: f'{{{NS}}}{t}'
WORK = Path('scratch/flagmap')


def chain(el):
    """The element's ancestors' transforms, outermost first."""
    return [a.get('transform') for a in reversed(list(el.iterancestors())) if a.get('transform')]


def element_geometry(svg, eid, tol=0.2):
    """Shapely geometry of every path under element eid (transforms applied, evenodd)."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    import svgelements as se
    el = next(e for e in svg.elements() if getattr(e, 'id', None) == eid)
    shapes = [e for e in (el if isinstance(el, se.Group) else [el]).select() if isinstance(e, se.Shape)] \
        if isinstance(el, se.Group) else [el]
    geoms = []
    for sh in shapes:
        path = se.Path(sh)
        path.reify()
        rings = None
        for sub in path.as_subpaths():
            sub = se.Path(sub)
            pts = []
            for seg in sub:
                if isinstance(seg, se.Move):
                    pts.append((seg.end.x, seg.end.y))
                elif isinstance(seg, (se.Line, se.Close)):
                    if seg.end is not None:
                        pts.append((seg.end.x, seg.end.y))
                else:
                    n = max(2, int(seg.length() / tol))
                    pts += [(p.x, p.y) for p in (seg.point(t / n) for t in range(1, n + 1))]
            if len(pts) >= 3:
                ring = Polygon(pts).buffer(0)
                rings = ring if rings is None else rings.symmetric_difference(ring)
        if rings is not None:
            geoms.append(rings)
    return unary_union(geoms)


def region_geometry(outline, spec):
    """spec 'a+b-c-d': union of a and b minus c and d. Returns (viewBox, [(d, [])])."""
    import svgelements as se
    svg = se.SVG.parse(str(outline), reify=True)
    plus, minus = [], []
    for sign, eid in re.findall(r'([+-]?)([^+-]+)', spec):
        (minus if sign == '-' else plus).append(eid)
    from shapely.ops import unary_union
    region = unary_union([element_geometry(svg, e) for e in plus])
    if minus:
        region = region.difference(unary_union([element_geometry(svg, e) for e in minus]).buffer(0.05))
    region = region.buffer(0)
    if minus:
        # drop debris: slivers along neighbour borders (opening) and pieces touching the frame
        fx0, fy0, fx1, fy1 = unary_union([element_geometry(svg, e) for e in plus]).bounds
        e = max(fx1 - fx0, fy1 - fy0) / 800
        region = region.buffer(-e).buffer(e)
        from shapely.geometry import box
        inner = box(fx0, fy0, fx1, fy1).buffer(-2 * e)
        parts = list(region.geoms) if hasattr(region, 'geoms') else [region]
        region = unary_union([p for p in parts if inner.contains(p)])
    x0, y0, x1, y1 = region.bounds
    region = region.simplify(max(x1 - x0, y1 - y0) / 3000, preserve_topology=True)
    polys = list(region.geoms) if hasattr(region, 'geoms') else [region]
    big = max(p.area for p in polys)
    polys = [p for p in polys if p.area > 2e-3 * big]  # drop specks (they also spoil the bbox fit)
    region = unary_union(polys)
    d = []
    for p in polys:
        for ring in [p.exterior, *p.interiors]:
            c = list(ring.coords)
            d.append('M' + ' L'.join(f'{x:.2f},{y:.2f}' for x, y in c[:-1]) + 'Z')
    x0, y0, x1, y1 = region.bounds
    pad = 0.02 * max(x1 - x0, y1 - y0)
    return [x0 - pad, y0 - pad, x1 - x0 + 2 * pad, y1 - y0 + 2 * pad], [(' '.join(d), [])]


def region_paths(outline, gid):
    if re.search(r'[+-]', gid.lstrip('+-')):
        return region_geometry(outline, gid)
    root = etree.parse(str(outline)).getroot()
    g = root.find(f".//*[@id='{gid}']")
    vb = [float(x) for x in root.get('viewBox').split()]
    ds = []
    for p in ([g] if g.tag == Q('path') else g.iter(Q('path'))):
        ts = chain(p) + ([p.get('transform')] if p.get('transform') else [])
        ds.append((p.get('d'), ts))
    return vb, ds


def paths_markup(ds, style):
    out = []
    for d, ts in ds:
        el = f'<path d="{d}" style="{style}"/>'
        for t in reversed(ts):
            el = f'<g transform="{t}">{el}</g>'
        out.append(el)
    return ''.join(out)


def mask_of(svg_text, name, scale=1.0):
    p = WORK / f'{name}.svg'
    p.write_text(svg_text, encoding='utf8')
    render(p, WORK / f'{name}.png', scale)
    a = np.array(Image.open(WORK / f'{name}.png').convert('RGB')).astype(int)
    return a


def fit_silhouette(target_mask, vb, ds):
    """Find ax, ay, tx, ty with pixel = (ax*x + tx, ay*y + ty). Separate x/y scales absorb
    the projection difference between the PNG and the vector source over a small area."""
    x0, y0, w, h = vb
    S = 2000 / max(w, h)
    svg = (f'<svg xmlns="{NS}" width="{w * S:.0f}" height="{h * S:.0f}" viewBox="{x0} {y0} {w} {h}">'
           f'{paths_markup(ds, "fill:#ffffff;stroke:none;fill-rule:evenodd")}</svg>')
    m = mask_of(svg, 'silhouette').sum(2) > 384
    ys, xs = np.nonzero(m)
    tys, txs = np.nonzero(target_mask)
    bx0, bx1, by0, by1 = xs.min(), xs.max(), ys.min(), ys.max()
    tx0, tx1, ty0, ty1 = txs.min(), txs.max(), tys.min(), tys.max()
    kx = (tx1 - tx0) / (bx1 - bx0)  # target px per render px
    ky = (ty1 - ty0) / (by1 - by0)
    ox, oy = tx0 - kx * bx0, ty0 - ky * by0
    H, W = target_mask.shape
    st = max(1, max(H, W) // 250)
    vv, uu = np.mgrid[0:H:st, 0:W:st]
    t = target_mask[vv, uu]

    def score(kx, ky, ox, oy):
        x = ((uu - ox) / kx).astype(int); y = ((vv - oy) / ky).astype(int)
        ok = (x >= 0) & (y >= 0) & (x < m.shape[1]) & (y < m.shape[0])
        v = m[y.clip(0, m.shape[0] - 1), x.clip(0, m.shape[1] - 1)] & ok
        return (v & t).sum() / max(1, (v | t).sum())
    cur = (score(kx, ky, ox, oy), kx, ky, ox, oy)
    for it in range(6):
        f = 2 ** it
        for dkx, dky, dx, dy in itertools.product(np.linspace(-0.04, 0.04, 5) * kx / f, np.linspace(-0.04, 0.04, 5) * ky / f,
                                                  np.linspace(-4, 4, 5) / f, np.linspace(-4, 4, 5) / f):
            sc = score(cur[1] + dkx, cur[2] + dky, cur[3] + dx, cur[4] + dy)
            if sc > cur[0]:
                cur = (sc, cur[1] + dkx, cur[2] + dky, cur[3] + dx, cur[4] + dy)
    iou, kx, ky, ox, oy = cur
    ax, ay = kx * S, ky * S  # unit -> target px: px = a*(unit - x0) + o
    return iou, ax, ay, ox - ax * x0, oy - ay * y0


def flag_info(flag):
    root = etree.parse(str(flag)).getroot()
    vb = [float(x) for x in root.get('viewBox').split()]
    inner = ''.join(etree.tostring(c, encoding='unicode') for c in root if isinstance(c.tag, str))
    fills = Counter(re.findall(r'fill="(#[0-9a-fA-F]{3,6})"', etree.tostring(root, encoding='unicode')))
    return vb, inner


def fit_flag(target, inside, fvb, finner):
    """Fit flag placement (scale f, offset) in target px by colour agreement inside the silhouette."""
    x0, y0, w, h = fvb
    R = 1200 / w
    svg = f'<svg xmlns="{NS}" width="{w * R:.0f}" height="{h * R:.0f}" viewBox="{x0} {y0} {w} {h}">{finner}</svg>'
    F = mask_of(svg, 'flag')
    cols = [c for c, _ in Counter(map(tuple, (F[::4, ::4] // 16 * 16).reshape(-1, 3).tolist())).most_common(3)]
    Fl = np.argmin([np.abs(F - (np.array(c) + 8)).sum(2) for c in cols[:2]], 0)  # flag label per px
    T = target[..., :3].astype(int)
    fcols = [tuple(int(v) for v in np.median(F[Fl == i], 0)) for i in range(2)]
    Tl = np.argmin([np.abs(T - np.array(c)).sum(2) for c in fcols], 0)
    H, W = inside.shape
    vv, uu = np.mgrid[0:H:2, 0:W:2]
    sel = inside[vv, uu]
    vv, uu, tl = vv[sel], uu[sel], Tl[vv, uu][sel]

    def score(s, ox, oy):  # s: target px per flag render px
        x = ((uu - ox) / s).astype(int); y = ((vv - oy) / s).astype(int)
        ok = (x >= 0) & (y >= 0) & (x < Fl.shape[1]) & (y < Fl.shape[0])
        lab = np.where(ok, Fl[y.clip(0, Fl.shape[0] - 1), x.clip(0, Fl.shape[1] - 1)], 0)
        return (lab == tl).mean()
    best = None
    ys, xs = np.nonzero(inside)
    cx, cy = xs.mean(), ys.mean()
    for s in np.geomspace(0.1, 4, 40) * W / Fl.shape[1]:
        for fx, fy in itertools.product(np.linspace(-0.6, 0.6, 13), repeat=2):
            ox = cx - s * Fl.shape[1] * (0.5 + fx); oy = cy - s * Fl.shape[0] * (0.5 + fy)
            sc = score(s, ox, oy)
            if best is None or sc > best[0]:
                best = (sc, s, ox, oy)
    cur = best
    for it in range(5):
        f = 2 ** it
        for ds_, dx, dy in itertools.product(np.linspace(-0.08, 0.08, 7) * cur[1] / f, np.linspace(-8, 8, 7) / f, np.linspace(-8, 8, 7) / f):
            sc = score(cur[1] + ds_, cur[2] + dx, cur[3] + dy)
            if sc > cur[0]:
                cur = (sc, cur[1] + ds_, cur[2] + dx, cur[3] + dy)
    agree, s, ox, oy = cur
    a = s * R  # target px per flag unit
    return agree, a, ox - a * x0, oy - a * y0, fcols


def main():
    target_p, outline, gid, flag, out = sys.argv[1:6]
    WORK.mkdir(parents=True, exist_ok=True)
    img = Image.open(target_p).convert('RGBA')
    W, H = img.size
    f = min(1.0, 500 / max(W, H))  # fit on a copy at most 500 px across
    if f < 1:
        img = img.resize((round(W * f), round(H * f)), Image.LANCZOS)
    target = np.array(img)
    alpha = target[..., 3] > 128
    vb, ds = region_paths(Path(outline), gid)
    iou, ax, ay, bx, by = fit_silhouette(alpha, vb, ds)
    ax, ay, bx, by = ax / f, ay / f, bx / f, by / f
    a = (ax + ay) / 2

    from scipy import ndimage as nd
    inside = nd.binary_erosion(alpha, iterations=3)
    if flag.startswith('#'):  # solid silhouette, no flag
        c = flag.lstrip('#')
        fcols = [tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))]
        agree, fa, fx, fy, finner = 1.0, 1, 0, 0, ''
    else:
        fvb, finner = flag_info(Path(flag))
        agree, fa, fx, fy, fcols = fit_flag(target, inside, fvb, finner)
        fa, fx, fy = fa / f, fx / f, fy / f

    ring = alpha & ~nd.binary_erosion(alpha, iterations=2)
    rc = target[ring][:, :3].astype(int)
    rc = rc[target[ring][:, 3] > 200]
    edge = tuple(int(v) for v in np.median(rc[rc.sum(1) <= np.percentile(rc.sum(1), 40)], 0))
    # flag colour under the ring, for comparison
    near_field = sum(abs(e - c) for e, c in zip(edge, fcols[0]))  # vs the flag's field colour
    has_outline = near_field > 100  # antialiased edges of solid shapes are not an outline
    hexc = '#%02x%02x%02x' % edge
    width = 2 / a  # about 1 px each side of the edge, in outline units

    field = '#%02x%02x%02x' % fcols[0]
    flag_g = (f'<g id="flag" transform="matrix({fa:.6f},0,0,{fa:.6f},{fx:.4f},{fy:.4f})">{finner}</g>' if finner else '')
    region_fill = paths_markup(ds, 'fill:#000000;stroke:none;clip-rule:evenodd')
    outline_g = (f'<g id="outline" transform="matrix({ax:.6f},0,0,{ay:.6f},{bx:.4f},{by:.4f})">'
                 f'{paths_markup(ds, f"fill:{hexc};fill-rule:evenodd;stroke:{hexc};stroke-width:{width * 2:.4f};stroke-linejoin:round")}</g>'
                 if has_outline else '')
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="{NS}" version="1.1" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs><clipPath id="region"><g transform="matrix({ax:.6f},0,0,{ay:.6f},{bx:.4f},{by:.4f})">{region_fill}</g></clipPath></defs>
{outline_g}
<g clip-path="url(#region)"><rect id="field" width="{W}" height="{H}" fill="{field}"/>{flag_g}</g>
</svg>
'''
    # clipPath children must be shapes, not groups, in SVG 1.1: flatten transforms onto paths
    svg = re.sub(r'<clipPath id="region">.*?</clipPath>', lambda m: flatten_clip(m.group(0)), svg, flags=re.S)
    Path(out).write_text(svg, encoding='utf8')
    print(json.dumps(dict(silhouette_iou=round(float(iou), 4), y_over_x_scale=round(float(ay / ax), 4), flag_agreement=round(float(agree), 4),
                          outline=hexc if has_outline else None, flag_colours=['#%02x%02x%02x' % c for c in fcols]), indent=1))


def flatten_clip(block):
    """Move nested <g transform> chains onto each <path transform> (allowed inside clipPath)."""
    root = etree.fromstring(f'<svg xmlns="{NS}"><defs>{block}</defs></svg>')
    cp = root.find(f'.//{Q("clipPath")}')
    paths = []
    for p in cp.iter(Q('path')):
        ts = [a.get('transform') for a in reversed(list(p.iterancestors())) if a.get('transform') and a is not cp]
        np_ = etree.Element(Q('path'), d=p.get('d'))
        np_.set('clip-rule', 'evenodd')
        if ts:
            np_.set('transform', ' '.join(ts))
        paths.append(np_)
    for c in list(cp):
        cp.remove(c)
    for p in paths:
        cp.append(p)
    return etree.tostring(cp, encoding='unicode').replace(f' xmlns="{NS}"', '')


if __name__ == '__main__':
    main()
