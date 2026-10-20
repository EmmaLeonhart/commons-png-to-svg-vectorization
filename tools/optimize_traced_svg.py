"""Shrink an auto-traced SVG (one flat-colour <path> per region, each in its own <g>, hundreds of near-identical colours)
without visibly changing it:
  1. merge colours closer than --de in CIELAB (ΔE76) into their area-weighted mean, so the palette is the drawing's
     real colours instead of hundreds of tracing variants;
  2. regroup paths by colour where that cannot change the stacking: a path joins an earlier group of its colour only
     if no differently coloured path in between overlaps its bounding box; inside a group, paths whose boxes do not
     touch are combined into one <path> (fill-rule evenodd is then safe), the rest stay separate in one <g fill>;
  3. drop the per-path <g> wrappers and repeated styles, and optionally drop specks smaller than --speck px².
Path data compaction (precision, relative commands) is left to svgo, run afterwards.
usage: python tools/optimize_traced_svg.py IN.svg OUT.svg [--de 4] [--speck 0]"""
import argparse, re
import numpy as np
from lxml import etree

NUM = re.compile(r'-?\d*\.?\d+(?:e-?\d+)?')


def srgb_to_lab(rgb):
    c = np.asarray(rgb, float) / 255
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    xyz = c @ np.array([[0.4124, 0.2126, 0.0193], [0.3576, 0.7152, 0.1192], [0.1805, 0.0722, 0.9505]])
    xyz /= [0.95047, 1.0, 1.08883]
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    return np.stack([116 * f[:, 1] - 16, 500 * (f[:, 0] - f[:, 1]), 200 * (f[:, 1] - f[:, 2])], 1)


def bbox(d):
    v = np.array([float(x) for x in NUM.findall(d)])
    if len(v) < 2:
        return None
    xs, ys = v[0::2][:len(v) // 2], v[1::2][:len(v) // 2]
    return xs.min(), ys.min(), xs.max(), ys.max()


def hit(a, b):
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src'); ap.add_argument('out')
    ap.add_argument('--de', type=float, default=4.0)
    ap.add_argument('--speck', type=float, default=0.0)
    a = ap.parse_args()
    tree = etree.parse(a.src, etree.XMLParser(huge_tree=True, remove_comments=True))
    root = tree.getroot()
    ns = root.nsmap.get(None, 'http://www.w3.org/2000/svg')
    paths = []
    for el in root.iter('{%s}path' % ns):
        st = el.get('style', '')
        fill = el.get('fill') or (re.search(r'fill:(#[0-9a-fA-F]{6})', st) or [None, None])[1]
        m = re.search(r'opacity:([\d.]+)', st)
        if fill is None or (m and float(m.group(1)) < 1):
            raise SystemExit(f'unexpected path (fill {fill}, style {st}); this tool expects opaque flat fills')
        d = el.get('d')
        b = bbox(d)
        if b is None:
            continue
        paths.append([fill.lower(), d, b])
    n0 = len(paths)
    if a.speck > 0:
        paths = [p for p in paths if (p[2][2] - p[2][0]) * (p[2][3] - p[2][1]) >= a.speck]
    # 1. colour merge: greedy clustering in Lab, biggest colours (by total bbox area) first
    cols = sorted({p[0] for p in paths})
    rgb = np.array([[int(c[i:i + 2], 16) for i in (1, 3, 5)] for c in cols])
    lab = srgb_to_lab(rgb)
    area = {c: 0.0 for c in cols}
    for p in paths:
        area[p[0]] += max(1.0, (p[2][2] - p[2][0]) * (p[2][3] - p[2][1]))
    w = np.array([area[c] for c in cols])
    order = np.argsort(-w)
    label = -np.ones(len(cols), int)
    centres = []
    for i in order:
        if label[i] >= 0:
            continue
        k = len(centres)
        near = (label < 0) & (np.linalg.norm(lab - lab[i], axis=1) < a.de)
        label[near] = k
        centres.append(i)
    newcol = {}
    for k in range(len(centres)):
        m = label == k
        mean = (rgb[m] * w[m, None]).sum(0) / w[m].sum()
        hexc = '#%02x%02x%02x' % tuple(np.round(mean).astype(int))
        for c in np.array(cols)[m]:
            newcol[c] = hexc
    for p in paths:
        p[0] = newcol[p[0]]
    # 2. stacking-safe regrouping
    groups = []  # [colour, [(d, bbox)], union bbox]
    for col, d, b in paths:
        target = None
        for g in reversed(groups):
            if g[0] == col:
                target = g
                break
            if hit(g[2], b):
                break
        if target is None:
            groups.append([col, [(d, b)], b])
        else:
            target[1].append((d, b))
            u = target[2]
            target[2] = (min(u[0], b[0]), min(u[1], b[1]), max(u[2], b[2]), max(u[3], b[3]))
    # combine non-touching paths inside a group into compound paths (greedy, first fit)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{root.get("width")}" height="{root.get("height")}"'
           + (f' viewBox="{root.get("viewBox")}"' if root.get('viewBox') else
              f' viewBox="0 0 {float(re.sub("[a-z]", "", root.get("width")))} {float(re.sub("[a-z]", "", root.get("height")))}"')
           + ' fill-rule="evenodd" clip-rule="evenodd">']
    n_paths = 0
    for col, items, _ in groups:
        bins = []  # [list of d, list of bbox]
        for d, b in items:
            for bn in bins:
                if not any(hit(b, x) for x in bn[1]):
                    bn[0].append(d); bn[1].append(b)
                    break
            else:
                bins.append([[d], [b]])
        ds = [' '.join(bn[0]) for bn in bins]
        n_paths += len(ds)
        if len(ds) == 1:
            out.append(f'<path fill="{col}" d="{ds[0]}"/>')
        else:
            out.append(f'<g fill="{col}">' + ''.join(f'<path d="{d}"/>' for d in ds) + '</g>')
    out.append('</svg>')
    open(a.out, 'w', encoding='utf8').write('\n'.join(out) + '\n')
    print(f'{a.src}: {n0} paths, {len(cols)} colours -> {len(centres)} colours, {len(groups)} groups, {n_paths} paths')


if __name__ == '__main__':
    main()
