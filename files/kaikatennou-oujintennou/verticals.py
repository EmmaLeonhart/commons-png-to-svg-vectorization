"""Measure the anti-aliased vertical connector lines of Kaikatennou oujintennou.png (1 px lines drawn between pixel
columns, so they show as pairs of grey columns) and put them into spec.json as exact SVG lines ("extra"):
x is the darkness-weighted centre of each run, y its extent. Run before tools/rebuild_tree.py."""
import json
import numpy as np
from PIL import Image

SPEC = 'files/kaikatennou-oujintennou/spec.json'
spec = json.load(open(SPEC, encoding='utf8'))
im = Image.open(spec['png']).convert('RGBA')
a = np.asarray(Image.alpha_composite(Image.new('RGBA', im.size, 'white'), im).convert('L')).astype(float)
dark = 255 - a
mask = np.zeros(a.shape, bool)
for x0, x1, y0, y1 in spec['mask']:
    mask[y0:y1 + 1, x0:x1 + 1] = True
ink = (dark > 40) & ~mask
H, W = a.shape
segs = []
for x in range(W - 1):
    col = ink[:, x] | ink[:, x + 1]
    r = np.concatenate([[0], col.astype(int), [0]]); d = np.diff(r)
    for s, e in zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]):
        if e - s < 12:
            continue
        w = dark[s:e, max(0, x - 1):x + 3]
        cx = (w * np.arange(max(0, x - 1), x + 3)[None, :]).sum() / max(w.sum(), 1) + 0.5
        segs.append((round(float(cx), 2), int(s), int(e)))
merged = []  # pairs of adjacent columns report the same line: keep one per (x, y-range)
for cx, s, e in sorted(segs):
    if merged and abs(merged[-1][0] - cx) < 1.0 and abs(merged[-1][1] - s) <= 2 and abs(merged[-1][2] - e) <= 2:
        continue
    merged.append((cx, s, e))
spec['extra'] = [f'<path d="M{cx},{s} V{e}" stroke="#000000" stroke-width="1" fill="none"/>' for cx, s, e in merged]
json.dump(spec, open(SPEC, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
print(len(merged), 'vertical lines:', merged)
