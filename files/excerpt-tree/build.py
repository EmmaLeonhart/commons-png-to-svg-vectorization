"""Rebuild File:Excerpt tree.png (transparent, 600x600) by construction: rounded black boxes measured from
the alpha mask, arrows as a straight shaft plus a triangular head (shaft width, tip and head base fitted
to each arrow's pixels), and the labels as white <text> in Liberation Sans (Arial metrics), size and
position from each word's ink. Run from the repo root."""
import io
import numpy as np, resvg_py
from PIL import Image, ImageFont
from scipy import ndimage

PNG = 'data_lake/downloads/excerpt-tree/Excerpt tree.png'
OUT = 'files/excerpt-tree/Excerpt tree.svg'
ARIAL = r'C:\Windows\Fonts\arial.ttf'
FAMILY = "'Liberation Sans', Arial, Helvetica, sans-serif"
LABELS = ['Philosophy', 'Ethics', 'Metaphysics', 'Logic', 'Ontology', 'Causality', 'Substance', 'Accident']
im = np.asarray(Image.open(PNG).convert('RGBA')).astype(int)
H, W = im.shape[:2]
alpha = im[..., 3] / 255.0
solid = alpha > 0.5
white = (im[..., :3].min(-1) > 128) & solid

# boxes: solid components that, with their text holes filled, are nearly their bounding box
filled = ndimage.binary_fill_holes(solid | white)
opened = ndimage.binary_opening(filled, structure=np.ones((15, 15)))  # drops the thin arrow shafts
lab, n = ndimage.label(opened)
boxes = []
for i, sl in enumerate(ndimage.find_objects(lab), 1):
    y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
    comp = filled[y0:y1, x0:x1]
    if comp.mean() > 0.9 and (x1 - x0) > 40:
        # corner radius: how far the top row's solid run is inset from the side
        row = np.nonzero(filled[y0, x0:x1])[0]
        r = max(row.min(), 1)
        boxes.append((x0, y0, x1, y1, r + 2))
inbox = np.zeros_like(solid)
for x0, y0, x1, y1, _ in boxes:
    inbox[y0:y1, x0:x1] = True

# arrows: what is left of the solid mask
arrows = []
lab, n = ndimage.label(solid & ~ndimage.binary_dilation(inbox, iterations=1))
for i, sl in enumerate(ndimage.find_objects(lab), 1):
    ys, xs = np.nonzero(lab == i)
    if len(xs) < 50:
        continue
    P = np.c_[xs + 0.5, ys + 0.5]
    m = P.mean(0)
    u = np.linalg.svd(P - m)[2][0]
    if u[1] > 0:
        u = -u  # point up: arrows point to the parent above
    s = (P - m) @ u
    v = np.array([-u[1], u[0]])
    w = (P - m) @ v
    # width profile along the arrow: the head is where it is widest
    bins = np.linspace(s.min(), s.max(), 60)
    idx = np.digitize(s, bins)
    width = np.array([np.ptp(w[idx == k]) + 1 if (idx == k).sum() > 1 else 0 for k in range(1, 61)])
    shaft = float(np.median(width[5:30]))
    head_w = float(width.max())
    k_head = int(np.argmax(width > shaft * 1.6))
    base_s = bins[k_head]
    tip = m + u * s.max()
    tail = m + u * s.min()
    # the measured arrow stops where the boxes' 1 px margin was cut: run each end on to its box
    for _ in range(8):
        if inbox[int(tip[1]), int(tip[0])]:
            break
        tip = tip + u
    for _ in range(8):
        if inbox[int(tail[1]), int(tail[0])]:
            break
        tail = tail - u
    base_c = m + u * base_s
    arrows.append(dict(tail=tail, tip=tip, base=base_c, v=v, shaft=shaft, head=head_w))

texts = []
for x0, y0, x1, y1, _ in boxes:
    sub = white[y0:y1, x0:x1]
    ys, xs = np.nonzero(sub)
    bx0, bx1, by0, by1 = xs.min() + x0, xs.max() + x0, ys.min() + y0, ys.max() + y0
    # which label: by order of position and width (top to bottom, left to right)
    texts.append((bx0, bx1, by0, by1))
order = sorted(range(len(texts)), key=lambda i: (texts[i][2] // 40, texts[i][0]))
parts = []
for name, i in zip(LABELS, order):
    bx0, bx1, by0, by1 = texts[i]
    best = min((abs(ImageFont.truetype(ARIAL, s).getbbox(name, anchor='ls')[2] - ImageFont.truetype(ARIAL, s).getbbox(name, anchor='ls')[0] - (bx1 - bx0 + 1)), s) for s in np.arange(8, 50, 0.1))[1]
    f = ImageFont.truetype(ARIAL, best)
    l, tp, r, b = f.getbbox(name, anchor='ls')
    parts.append(f'<text x="{bx0 - l:.1f}" y="{by0 - tp:.1f}" font-size="{best:.1f}">{name}</text>')

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
       '<g fill="#000">']
for x0, y0, x1, y1, r in boxes:
    svg.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="{r}"/>')
for ar in arrows:
    t, tl, bc, v = ar['tip'], ar['tail'], ar['base'], ar['v']
    svg.append(f'<path d="M{tl[0]:.1f},{tl[1]:.1f}L{bc[0]:.1f},{bc[1]:.1f}" stroke="#000" stroke-width="{ar["shaft"]:.1f}"/>')
    p1, p2 = bc + v * ar['head'] / 2, bc - v * ar['head'] / 2
    svg.append(f'<path d="M{t[0]:.1f},{t[1]:.1f}L{p1[0]:.1f},{p1[1]:.1f}L{p2[0]:.1f},{p2[1]:.1f}Z"/>')
svg.append(f'</g><g font-family="{FAMILY}" fill="#fff">' + ''.join(parts) + '</g></svg>')
svg = ''.join(svg)
open(OUT, 'w', encoding='utf8').write(svg)
o = np.asarray(Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=svg, font_files=[ARIAL], skip_system_fonts=True)))).convert('RGBA')).astype(int)
on_white = lambda x: (x[..., :3] * (x[..., 3:] / 255) + 255 * (1 - x[..., 3:] / 255))
d = np.abs(on_white(o) - on_white(im)).max(-1) > 64
print('boxes', len(boxes), 'arrows', len(arrows), [(round(a_['shaft'], 1), round(a_['head'], 1)) for a_ in arrows], 'pixels differing %.4f' % d.mean())
Image.fromarray(np.concatenate([on_white(im), on_white(o)], 1).astype(np.uint8)).save('scratch/arms/ext_cmp.png')
