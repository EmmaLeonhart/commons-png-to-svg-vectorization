"""Find coloured vertical name columns in a family-tree PNG and write zoomed contact sheets."""
import sys, json
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as nd
png, out = sys.argv[1], sys.argv[2]
im = Image.open(png).convert('RGB'); T = np.array(im).astype(int)
colours = {'red': (255, 0, 0), 'blue': (0, 0, 255), 'yellow': (204, 204, 0)}
cols = []
for name, c in colours.items():
    m = np.all(T == c, 2)
    lab, n = nd.label(nd.binary_dilation(m, structure=np.ones((9, 3))))
    for y, x in nd.find_objects(lab):
        if m[y, x].sum() > 20:
            cols.append(dict(colour=name, x0=x.start + 1, x1=x.stop - 1, y0=y.start + 4, y1=y.stop - 4))
cols.sort(key=lambda c: (c['y0'], c['x0']))
json.dump(cols, open(out + '.json', 'w'))
tiles = []
for i, c in enumerate(cols):
    t = im.crop((c['x0'] - 2, max(0, c['y0'] - 2), c['x1'] + 3, c['y1'] + 3)); tiles.append((i, t.resize((t.width * 3, t.height * 3), Image.NEAREST)))
k = 0; part = 0
while k < len(tiles):
    sub = []; wsum = 0
    while k < len(tiles) and wsum + tiles[k][1].width + 20 < 1600:
        sub.append(tiles[k]); wsum += tiles[k][1].width + 20; k += 1
    sheet = Image.new('RGB', (wsum, max(t.height for _, t in sub) + 30), 'white'); d = ImageDraw.Draw(sheet); x = 0
    for i, t in sub:
        sheet.paste(t, (x, 25)); d.text((x + 2, 2), str(i), fill=(0, 0, 0)); x += t.width + 20
    sheet.save(f'{out}_sheet{part}.png'); part += 1
for i, c in enumerate(cols): print(i, c)
print(part, 'sheets')
