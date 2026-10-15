"""Step 2: each element of the registered ru geometry shifted on its own (the ru drawing places some
structures a few pixels off the PNG's) and its stroke width scaled, by grid search on chamfer distance
plus uncovered nearby ink against the PNG. North arrow left out (the PNG's is elsewhere; built in
build.py). Writes files/abusir-map/elements.json. Run from the repo root with PYTHONPATH=files/abusir-map."""
import json, re
import numpy as np
import geometry as G

NORTH = {'path3528', 'path3532', 'path3534'}
g = json.load(open('files/abusir-map/geometry.json'))
elems = [e for e in G.keep if re.search(r'\sid="([^"]+)"', e).group(1) not in NORTH]


def with_width(e, k):
    return re.sub(r'stroke-width:([0-9.]+)(px)?', lambda m: f'stroke-width:{float(m.group(1)) * k:.3f}', e)


def cost(e, dx, dy, k):
    body = f'<g transform="translate({dx / g["scale"]:.3f},{dy / g["scale"]:.3f})">{with_width(e, k)}</g>'
    m = G.mask(G.svg(g['scale'], g['tx'], g['ty'], body))
    if not m.any():
        return 1e9
    near = G.ndimage.binary_dilation(m, iterations=6) & G.ink
    return G.dist[m].mean() + 3 * (1 - (m & G.ink).sum() / max(near.sum(), 1))


out = []
for e in elems:
    eid = re.search(r'\sid="([^"]+)"', e).group(1)
    c, dx, dy = min((cost(e, dx, dy, 1.6), dx, dy) for dx in range(-8, 9, 2) for dy in range(-8, 9, 2))
    c, dx, dy = min((cost(e, x, y, 1.6), x, y) for x in np.arange(dx - 1.5, dx + 1.6, 0.5) for y in np.arange(dy - 1.5, dy + 1.6, 0.5))
    c, k = min((cost(e, dx, dy, k), k) for k in np.arange(0.8, 3.21, 0.2))
    print(eid, 'shift %.1f,%.1f width x%.1f cost %.3f' % (dx, dy, k, c), flush=True)
    out.append({'id': eid, 'dx': float(dx), 'dy': float(dy), 'k': float(k), 'cost': float(c),
                'xml': f'<g transform="translate({dx / g["scale"]:.3f},{dy / g["scale"]:.3f})">{with_width(e, k)}</g>'})
json.dump(out, open('files/abusir-map/elements.json', 'w'), indent=1)
