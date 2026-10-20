"""Connector geometry for files/ajaxmassdelete/build.py: each connector style's core colour (exact in the PNG) is thinned
to centrelines, which are simplified and snapped to horizontal and vertical runs; arrowheads are found as the blobs
wider than a shaft and rebuilt as triangles pointing along the shaft's end. Writes connectors.json."""
import json
import numpy as np
from PIL import Image
from scipy import ndimage

PNG = 'data_lake/downloads/ajaxmassdelete-flowchart/AjaxMassDelete FlowChart.png'
a = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
H, W = a.shape[:2]
STYLES = {'green': [0, 204, 0], 'red': [153, 51, 51], 'orange': [255, 153, 51]}


def thin(m):
    img = m.astype(np.uint8)
    def nb(I):
        P = np.pad(I, 1)
        return [P[0:-2, 1:-1], P[0:-2, 2:], P[1:-1, 2:], P[2:, 2:], P[2:, 1:-1], P[2:, 0:-2], P[1:-1, 0:-2], P[0:-2, 0:-2]]
    while True:
        ch = 0
        for step in (0, 1):
            p2, p3, p4, p5, p6, p7, p8, p9 = nb(img)
            B = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9
            seq = [p2, p3, p4, p5, p6, p7, p8, p9, p2]
            A = sum(((seq[i] == 0) & (seq[i + 1] == 1)).astype(int) for i in range(8))
            c1 = p2 * p4 * p6 if step == 0 else p2 * p4 * p8
            c2 = p4 * p6 * p8 if step == 0 else p2 * p6 * p8
            k = (img == 1) & (B >= 2) & (B <= 6) & (A == 1) & (c1 == 0) & (c2 == 0)
            img[k] = 0; ch += k.sum()
        if not ch:
            return img.astype(bool)


def trace(S):
    K = np.ones((3, 3), int); K[1, 1] = 0
    deg = ndimage.convolve(S.astype(int), K, mode='constant') * S
    nodes = S & (deg != 2)
    pts = set(zip(*np.nonzero(S)))
    off = [(-1, 0), (0, 1), (1, 0), (0, -1), (-1, 1), (1, 1), (1, -1), (-1, -1)]
    seen, paths = set(), []
    starts = list(zip(*np.nonzero(nodes)))
    if not starts and pts:  # a closed loop
        starts = [next(iter(pts))]
    for n in starts:
        for dy, dx in off:
            b = (n[0] + dy, n[1] + dx)
            if b in pts and (n, b) not in seen:
                path = [n, b]
                while not nodes[path[-1]] and len(path) < 100000:
                    cur = path[-1]
                    nxt = [(cur[0] + dy2, cur[1] + dx2) for dy2, dx2 in off
                           if (cur[0] + dy2, cur[1] + dx2) in pts and (cur[0] + dy2, cur[1] + dx2) not in path[-3:]]
                    if not nxt:
                        break
                    path.append(nxt[0])
                seen.add((n, b)); seen.add((path[-1], path[-2]))
                if len(path) > 6:
                    paths.append([(x, y) for y, x in path])
    return paths


def dp(P, eps=2.0):
    P = np.asarray(P, float)
    if len(P) < 3:
        return P
    a_, b_ = P[0], P[-1]; d = b_ - a_; L = np.hypot(*d) or 1
    dist = np.abs(d[0] * (P[:, 1] - a_[1]) - d[1] * (P[:, 0] - a_[0])) / L
    i = int(np.argmax(dist))
    if dist[i] > eps:
        return np.vstack([dp(P[:i + 1], eps)[:-1], dp(P[i:], eps)])
    return np.vstack([a_, b_])


def orthogonal(P):
    """snap each run to horizontal or vertical: shared coordinates averaged; short corner bevels removed"""
    P = [list(p) for p in P]
    # drop bevel points: a vertex whose neighbouring runs are both short diagonals
    keep = [P[0]]
    for i in range(1, len(P) - 1):
        d0 = np.subtract(P[i], keep[-1]); d1 = np.subtract(P[i + 1], P[i])
        if min(abs(d0[0]), abs(d0[1])) > 2 and np.hypot(*d0) < 25:
            keep[-1] = P[i]
            continue
        keep.append(P[i])
    keep.append(P[-1])
    P = keep
    for i in range(len(P) - 1):
        dx, dy = P[i + 1][0] - P[i][0], P[i + 1][1] - P[i][1]
        if abs(dx) >= abs(dy):
            y = (P[i][1] + P[i + 1][1]) / 2; P[i][1] = P[i + 1][1] = y
        else:
            x = (P[i][0] + P[i + 1][0]) / 2; P[i][0] = P[i + 1][0] = x
    # recompute corners as intersections of consecutive runs
    for i in range(1, len(P) - 1):
        a0, a1 = np.subtract(P[i], P[i - 1]), np.subtract(P[i + 1], P[i])
        if abs(a0[0]) >= abs(a0[1]) and abs(a1[1]) > abs(a1[0]):
            P[i] = [P[i + 1][0], P[i - 1][1]]
        elif abs(a0[1]) > abs(a0[0]) and abs(a1[0]) >= abs(a1[1]):
            P[i] = [P[i - 1][0], P[i + 1][1]]
    return [[round(x, 1), round(y, 1)] for x, y in P]


def join(paths, reach=26):
    """rounded corners split the skeleton: join two path ends that are close and run perpendicular, at the corner
    where their lines meet; repeat until nothing joins"""
    def end(p, first):
        e, f = (p[0], p[1]) if first else (p[-1], p[-2])
        return np.array(e, float), np.subtract(e, f)
    changed = True
    while changed:
        changed = False
        for i in range(len(paths)):
            for j in range(len(paths)):
                if i == j:
                    continue
                for fi in (True, False):
                    for fj in (True, False):
                        (ei, di), (ej, dj) = end(paths[i], fi), end(paths[j], fj)
                        if np.hypot(*(ei - ej)) > reach:
                            continue
                        hi, hj = abs(di[0]) >= abs(di[1]), abs(dj[0]) >= abs(dj[1])
                        if hi == hj:
                            continue
                        corner = [ej[0], ei[1]] if hi else [ei[0], ej[1]]
                        A = paths[i] if not fi else paths[i][::-1]
                        B = paths[j] if fj else paths[j][::-1]
                        A = A[:-1] + [corner]; B = [corner] + B[1:]
                        merged = A + B[1:]
                        paths = [p for k, p in enumerate(paths) if k not in (i, j)] + [merged]
                        changed = True
                        break
                    if changed: break
                if changed: break
            if changed: break
    return paths


def extract(rgb, shaft_r=3.4):
    m = np.abs(a - rgb).sum(2) < 12
    edt = ndimage.distance_transform_edt(m)
    heads = ndimage.binary_dilation(edt > shaft_r, iterations=6) & m
    lab, n = ndimage.label(heads)
    big = [i + 1 for i in range(n) if (lab == i + 1).sum() > 60]  # arrowheads; small blobs are thick corners
    heads = np.isin(lab, big)
    blobs = [np.argwhere(lab == i)[:, ::-1].astype(float) for i in big]
    shafts = m & ~ndimage.binary_dilation(heads, iterations=1)
    paths = [orthogonal(dp(p)) for p in trace(thin(ndimage.binary_closing(shafts, iterations=1)))]
    paths = [p for p in paths if sum(np.hypot(*np.subtract(p[i + 1], p[i])) for i in range(len(p) - 1)) > 4]
    paths = join(paths)
    arrows = []
    for b in blobs:
        c = b.mean(0)
        # the nearest path end, and the shaft direction there
        best = None
        for p in paths:
            for e, f in ((p[0], p[1]), (p[-1], p[-2])):
                d = np.hypot(*np.subtract(e, c))
                if best is None or d < best[0]:
                    best = (d, e, f)
        if best is None or best[0] > 30:
            continue
        _, e, f = best
        u = np.subtract(e, f); u = u / np.hypot(*u)
        t = (b - e) @ u
        # the standard head (measured): 10 px long, 17 px across its core, at the blob's tip
        tip = np.add(e, u * t.max()); base = tip - u * 10
        arrows.append({'base': base.tolist(), 'tip': tip.tolist(), 'half': 8.5})
        # the shaft runs on to the head's base
        for p in paths:
            for j, k in ((0, 1), (-1, -2)):
                if p[j] == list(e):
                    p[j] = [round(base[0], 1), round(base[1], 1)]
    return {'paths': paths, 'arrows': arrows}


if __name__ == '__main__':
    out = {k: extract(rgb, 4.6 if k == 'red' else 3.4) for k, rgb in STYLES.items()}
    json.dump(out, open('files/ajaxmassdelete/connectors.json', 'w'), indent=0)
    for k, v in out.items():
        print(k, len(v['paths']), 'paths', len(v['arrows']), 'arrows')
