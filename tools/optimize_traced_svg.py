"""Shrink an auto-traced SVG (hundreds or thousands of flat-colour paths with near-identical colours) without visibly
changing it. This step merges colours closer than --de in CIELAB (ΔE76) into their area-weighted mean, in place:
every fill and stroke colour (attribute or style) is rewritten, and nothing else in the document is touched (text,
transforms, rects, groups stay as they are). Structural compaction (collapsing groups, applying transforms, merging
non-intersecting paths with the same fill, shortening path data) is left to svgo, run afterwards with the config in
tools/svgo.tarot.config.js; optionally drop specks smaller than --speck px² (bounding box, local units).
usage: python tools/optimize_traced_svg.py IN.svg OUT.svg [--de 6] [--speck 0]"""
import argparse, re
import numpy as np
from lxml import etree

NUM = re.compile(r'-?\d*\.?\d+(?:e-?\d+)?')
HEX = re.compile(r'#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b')


def srgb_to_lab(rgb):
    c = np.asarray(rgb, float) / 255
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    xyz = c @ np.array([[0.4124, 0.2126, 0.0193], [0.3576, 0.7152, 0.1192], [0.1805, 0.0722, 0.9505]])
    xyz /= [0.95047, 1.0, 1.08883]
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    return np.stack([116 * f[:, 1] - 16, 500 * (f[:, 0] - f[:, 1]), 200 * (f[:, 1] - f[:, 2])], 1)


def full(c):
    c = c.lower()
    return '#' + ''.join(ch * 2 for ch in c[1:]) if len(c) == 4 else c


def area(el):
    d = el.get('d')
    if d:
        v = np.array([float(x) for x in NUM.findall(d)])
        if len(v) >= 4:
            xs, ys = v[0::2][:len(v) // 2], v[1::2][:len(v) // 2]
            return max(1.0, (xs.max() - xs.min()) * (ys.max() - ys.min())), True
        return 1.0, True
    try:
        return max(1.0, float(el.get('width', 1)) * float(el.get('height', 1))), False
    except ValueError:
        return 1.0, False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src'); ap.add_argument('out')
    ap.add_argument('--de', type=float, default=6.0)
    ap.add_argument('--speck', type=float, default=0.0)
    a = ap.parse_args()
    tree = etree.parse(a.src, etree.XMLParser(huge_tree=True))
    root = tree.getroot()
    els = [e for e in root.iter() if isinstance(e.tag, str) and (e.get('fill') or HEX.search(e.get('style', '')))]
    weight = {}
    dropped = 0
    for e in els:
        w, is_path = area(e)
        if a.speck and is_path and w < a.speck and etree.QName(e).localname == 'path':
            e.getparent().remove(e)
            dropped += 1
            continue
        for c in HEX.findall((e.get('fill') or '') + ' ' + (e.get('stroke') or '') + ' ' + e.get('style', '')):
            weight[full(c)] = weight.get(full(c), 0) + w
    cols = sorted(weight)
    rgb = np.array([[int(c[i:i + 2], 16) for i in (1, 3, 5)] for c in cols])
    lab = srgb_to_lab(rgb)
    w = np.array([weight[c] for c in cols])
    label = -np.ones(len(cols), int)
    k = 0
    for i in np.argsort(-w):  # biggest colours first; each claims the unclaimed colours within ΔE of it
        if label[i] >= 0:
            continue
        label[(label < 0) & (np.linalg.norm(lab - lab[i], axis=1) < a.de)] = k
        k += 1
    newcol = {}
    for j in range(k):
        m = label == j
        mean = np.round((rgb[m] * w[m, None]).sum(0) / w[m].sum()).astype(int)
        for c in np.array(cols)[m]:
            newcol[c] = '#%02x%02x%02x' % tuple(mean)
    sub = lambda s: HEX.sub(lambda mm: newcol.get(full(mm.group(0)), mm.group(0)), s)
    for e in root.iter():
        if not isinstance(e.tag, str):
            continue
        for at in ('fill', 'stroke', 'style', 'stop-color'):
            if e.get(at):
                e.set(at, sub(e.get(at)))
    tree.write(a.out, xml_declaration=True, encoding='UTF-8')
    print(f'{a.src}: {len(cols)} colours -> {k}' + (f', {dropped} specks dropped' if dropped else ''))


if __name__ == '__main__':
    main()
