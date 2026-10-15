"""Rebuild File:Map Icon - Hotel.png (5334x5334, semi-transparent) by construction: an outer disc
(#07395b, alpha 128), an inner disc (#07395b, alpha 217) and four light shapes (#8da4b4, alpha 236): the
slanted bar (a rotated rectangle from its principal axis), the head (a circle cut flat at the bottom), the
pillow line and the bed (a rounded rectangle). Every size measured from the alpha mask. Run from the repo root."""
import io
import numpy as np, resvg_py
from PIL import Image
from scipy import ndimage

PNG = 'data_lake/downloads/batch3/Map Icon - Hotel.png'
OUT = 'files/map-icon-hotel/Map Icon - Hotel.svg'
a = np.asarray(Image.open(PNG).convert('RGBA')).astype(int)
H, W = a.shape[:2]
al = a[..., 3]
anyp = al > 64
inner = ndimage.binary_fill_holes(al > 200)
light = (np.abs(al - 236) < 6) & (a[..., 0] > 100)


def disc(mask):
    ys, xs = np.nonzero(mask)
    return (xs.min() + xs.max() + 1) / 2, (ys.min() + ys.max() + 1) / 2, np.sqrt(mask.sum() / np.pi)


ox, oy, orad = disc(anyp)
ix, iy, irad = disc(inner)
parts = [f'<circle cx="{ox:.1f}" cy="{oy:.1f}" r="{orad:.1f}" fill="#07395b" fill-opacity="{128 / 255:.3f}"/>',
         f'<circle cx="{ix:.1f}" cy="{iy:.1f}" r="{irad:.1f}" fill="#07395b" fill-opacity="{217 / 255:.3f}"/>']
lab, n = ndimage.label(light)
report = []
for i, sl in enumerate(ndimage.find_objects(lab), 1):
    m = lab == i
    if m.sum() < 2000:
        continue
    ys, xs = np.nonzero(m)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    fill = m.sum() / ((x1 - x0) * (y1 - y0))
    P = np.c_[xs, ys].astype(float)
    mu = P.mean(0)
    u = np.linalg.svd(P - mu, full_matrices=False)[2][0]
    ang = np.degrees(np.arctan2(u[1], u[0])) % 180
    if 5 < ang < 175 and fill < 0.5:  # the slanted bar
        s = (P - mu) @ u
        v = np.array([-u[1], u[0]])
        w = (P - mu) @ v
        L, T = np.ptp(s) + 1, m.sum() / (np.ptp(s) + 1)
        parts.append(f'<rect x="{-L / 2:.1f}" y="{-T / 2:.1f}" width="{L:.1f}" height="{T:.1f}" '
                     f'transform="translate({mu[0]:.1f},{mu[1]:.1f}) rotate({np.degrees(np.arctan2(u[1], u[0])):.2f})"/>')
        report.append(('bar', round(L), round(T), round(np.degrees(np.arctan2(u[1], u[0])), 1)))
    elif 0.7 < fill < 0.82 and (x1 - x0) < 1.6 * (y1 - y0) * 2:  # half disc: area pi r^2 / 2 in a 2r x r box
        r = (x1 - x0) / 2
        cx, base = (x0 + x1) / 2, y1
        parts.append(f'<path d="M{cx - r:.1f},{base:.1f} A{r:.1f},{r:.1f} 0 0 1 {cx + r:.1f},{base:.1f} Z"/>')
        report.append(('head', round(r)))
    else:
        # rectangle, rounded when its corners are empty
        corner = m[y0:y0 + 40, x0:x0 + 40]
        rr = 0
        if not corner[0, 0]:
            rr = float(np.argmax(m[y0, x0:x1]))  # inset of the top edge = corner radius (approx.)
        parts.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="{rr:.1f}"/>')
        report.append(('rect', x1 - x0, y1 - y0, round(rr)))
# each region of the PNG has its own alpha (not layered), so the ring and the disc are cut out with masks
shapes = ''.join(parts[2:])
inner_c = parts[1].replace(' fill="#07395b" fill-opacity="%.3f"' % (217 / 255), '')
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
       f'<defs><mask id="ring"><rect width="{W}" height="{H}" fill="#fff"/>{inner_c.replace("/>", " fill=\"#000\"/>")}</mask>'
       f'<mask id="disc"><rect width="{W}" height="{H}" fill="#fff"/><g fill="#000">{shapes}</g></mask></defs>'
       f'<g mask="url(#ring)">{parts[0]}</g><g mask="url(#disc)">{parts[1]}</g>'
       f'<g fill="#8da4b4" fill-opacity="{236 / 255:.3f}">{shapes}</g></svg>')
open(OUT, 'w', encoding='utf8').write(svg)
o = np.asarray(Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=svg, width=667)))).convert('RGBA')).astype(int)
p = np.asarray(Image.open(PNG).convert('RGBA').resize((667, 667), Image.LANCZOS)).astype(int)
print(report, 'outer r %.0f inner r %.0f' % (orad, irad), 'pixels differing (at 1/8) %.4f' % (np.abs(o - p).max(-1) > 40).mean())
on_white = lambda x: x[..., :3] * (x[..., 3:] / 255) + 255 * (1 - x[..., 3:] / 255)
Image.fromarray(np.concatenate([on_white(p), on_white(o)], 1).astype(np.uint8)).save('scratch/arms/hotel_cmp.png')
