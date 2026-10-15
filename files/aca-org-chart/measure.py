"""Measure File:Agency for Cultural Affairs Organizational chart 20230327.png (aliased, so exact):
boxes (2 px black frames), the text lines inside each box, connector segments and the grey
"Tokyo office" area. Writes files/aca-org-chart/measure.json. Run from the repo root."""
import json
import numpy as np
from PIL import Image
from scipy import ndimage

PNG = 'data_lake/downloads/aca-org-chart/Agency for Cultural Affairs Organizational chart 20230327.png'
a = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
H, W = a.shape[:2]
black = a.sum(-1) == 0
grey = (a == 166).all(-1)

# boxes: non-black regions whose bounding box is framed by 2 px of black on all four sides
lab, n = ndimage.label(~black)
boxes = []
for i, sl in enumerate(ndimage.find_objects(lab), 1):
    y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
    if y1 - y0 < 40 or x1 - x0 < 100 or y0 < 2 or x0 < 2 or y1 > H - 2 or x1 > W - 2:
        continue
    frame = [black[y0 - 2:y0, x0:x1], black[y1:y1 + 2, x0:x1], black[y0:y1, x0 - 2:x0], black[y0:y1, x1:x1 + 2]]
    if all(f.mean() > 0.97 for f in frame):
        inner = black[y0:y1, x0:x1]
        rows = inner.any(1)
        bands, y = [], 0
        while y < len(rows):
            if rows[y]:
                s = y
                while y < len(rows) and rows[y]:
                    y += 1
                xs = np.nonzero(inner[s:y].any(0))[0]
                bands.append([int(x0 + xs.min()), int(x0 + xs.max()), int(y0 + s), int(y0 + y - 1)])
            y += 1
        fill = a[y0 + 3, x0 + 3]
        boxes.append({'x': int(x0 - 2), 'y': int(y0 - 2), 'w': int(x1 - x0 + 4), 'h': int(y1 - y0 + 4),
                      'fill': '#%02x%02x%02x' % tuple(fill), 'lines': bands})
boxes.sort(key=lambda b: (b['y'] // 20, b['x']))

# connectors: black outside the boxes, as horizontal and vertical runs
inbox = np.zeros_like(black)
for b in boxes:
    inbox[b['y']:b['y'] + b['h'], b['x']:b['x'] + b['w']] = True
dark = a.mean(-1) < 100  # line pixels, aliased on white and antialiased on the grey
con = dark & ~inbox


def runs(mask, axis):
    """Straight runs of >= 8 dark pixels along axis, merged across neighbouring rows/columns into one
    line each: (start, end, centre across)."""
    m = mask if axis == 0 else mask.T
    groups = []  # [start, end, [rows]]
    for y in range(m.shape[0]):
        xs = np.nonzero(m[y])[0]
        if len(xs) == 0:
            continue
        for r in np.split(xs, np.nonzero(np.diff(xs) > 1)[0] + 1):
            if len(r) < 8:
                continue
            for g in groups:
                if g[2][-1] == y - 1 and min(g[1], r[-1]) - max(g[0], r[0]) > 0.8 * min(g[1] - g[0], r[-1] - r[0]):
                    g[0], g[1] = int(min(g[0], r[0])), int(max(g[1], r[-1]))
                    g[2].append(int(y))
                    break
            else:
                groups.append([int(r[0]), int(r[-1]), [int(y)]])
    return [(g[0], g[1] + 1, float(np.mean(g[2])) + 0.5) for g in groups]


segs = [['h', x0, x1, y] for x0, x1, y in runs(con, 0)] + [['v', x, y0, y1] for y0, y1, x in runs(con, 1)]

# grey area: grey pixels plus the boxes standing in it, as row runs
area = grey.copy()
for b in boxes:
    ring = np.r_[a[b['y'] - 3, b['x']:b['x'] + b['w']], a[b['y'] + b['h'] + 2, b['x']:b['x'] + b['w']]] if b['y'] >= 3 and b['y'] + b['h'] + 2 < H else np.zeros((0, 3))
    if len(ring) and ((ring == 166).all(-1).mean() > 0.3):
        area[b['y']:b['y'] + b['h'], b['x']:b['x'] + b['w']] = True
area |= ndimage.binary_closing(area, iterations=3) & con  # connector pixels crossing the grey
json.dump({'W': W, 'H': H, 'boxes': boxes, 'segs': segs}, open('files/aca-org-chart/measure.json', 'w'), indent=1)
np.save('scratch/aca_area.npy', area)
for i, b in enumerate(boxes):
    print(i, b['x'], b['y'], b['w'], b['h'], b['fill'], len(b['lines']))
print(len(segs), 'segments:', segs)
