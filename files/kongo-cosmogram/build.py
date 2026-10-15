"""Rebuild File:Kongo Cosmogram - blank.png (1080x1000, black on transparent) by construction: a large
ellipse, four small ellipses at its ends, the cross between them, and four arrowed arcs. Ellipses and arc
circles are fitted algebraically to their stroke pixels (the centre line of each stroke), the cross lines by
principal axis, arrowheads by corner fitting (tools/fit_polygons.py). Stroke width from the line's pixels.
Run from the repo root."""
import io, sys
import numpy as np, resvg_py
from PIL import Image
from scipy import ndimage
sys.path.insert(0, 'tools')
from fit_polygons import polygons, to_path_d

PNG = 'data_lake/downloads/batch4/Kongo Cosmogram - blank.png'
OUT = 'files/kongo-cosmogram/Kongo Cosmogram - blank.svg'
a = np.asarray(Image.open(PNG).convert('RGBA')).astype(int)
H, W = a.shape[:2]
ink = a[..., 3] > 128
lab, n = ndimage.label(ink)
sizes = ndimage.sum(ink, lab, range(1, n + 1))
main = lab == (np.argmax(sizes) + 1)
arcs = [lab == i + 1 for i in range(n) if i != np.argmax(sizes)]


def ellipse_fit(xs, ys):
    ox, oy = xs.mean(), ys.mean()
    x, y = xs - ox, ys - oy
    D = np.c_[x * x, x * y, y * y, x, y, np.ones_like(x)]
    A, B, C, Dd, E, F = np.linalg.svd(D, full_matrices=False)[2][-1]
    den = B * B - 4 * A * C
    cx, cy = (2 * C * Dd - B * E) / den, (2 * A * E - B * Dd) / den
    M = np.array([[A, B / 2], [B / 2, C]])
    val = -(A * cx * cx + B * cx * cy + C * cy * cy + Dd * cx + E * cy + F)
    w, v = np.linalg.eigh(M / val)
    r = 1 / np.sqrt(w)
    ang = np.degrees(np.arctan2(v[1, 0], v[0, 0]))
    return cx + ox, cy + oy, r[0], r[1], ang


def centre_line(mask):
    """pixels on the middle of a stroke (skeleton by repeated thinning via distance maxima)."""
    dist = ndimage.distance_transform_edt(mask)
    mx = ndimage.maximum_filter(dist, size=3)
    return mask & (dist >= mx - 0.5) & (dist > 1)


sw = float(np.median(2 * ndimage.distance_transform_edt(main)[centre_line(main)]))
cl = centre_line(main)
ys, xs = np.nonzero(cl)
cx0, cy0 = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
# the cross: centre-line pixels within a few px of the vertical / horizontal through the middle
vert = np.abs(xs - np.median(xs[np.abs(ys - cy0) < 150])) < 4
horz = np.abs(ys - np.median(ys[np.abs(xs - cx0) < 150])) < 4
parts = []
ell = []
# small ellipses: centre-line pixels near each end, off the cross line
for name, sel in (('top', ys < 120), ('bottom', ys > H - 120), ('left', xs < 120), ('right', xs > W - 120)):
    s = sel & ~(vert if name in ('top', 'bottom') else horz) | (sel & ((ys < 60) | (ys > H - 60) | (xs < 40) | (xs > W - 40)))
    e = ellipse_fit(xs[s].astype(float), ys[s].astype(float))
    ell.append((name, e))
# big ellipse: centre-line pixels away from the cross and from the small ellipses
far = (np.abs(xs - cx0) > 40) & (np.abs(ys - cy0) > 40) & (xs > 130) & (xs < W - 130) & (ys > 130) & (ys < H - 130)
big = ellipse_fit(xs[far].astype(float), ys[far].astype(float))
ell.append(('big', big))
for name, (ex, ey, rx, ry, an) in ell:
    parts.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" transform="rotate({an:.2f} {ex:.1f} {ey:.1f})"/>')
E = dict(ell)
vx = float(np.median(xs[vert]))
hy = float(np.median(ys[horz]))
top, bottom, left, right = E['top'], E['bottom'], E['left'], E['right']
parts.append(f'<path d="M{vx:.1f},{top[1] + max(top[2], top[3]) * 0 + min(top[2], top[3]) if False else top[1] + (top[3] if abs(top[4]) < 45 else top[2]):.1f}'
             f'V{bottom[1] - (bottom[3] if abs(bottom[4]) < 45 else bottom[2]):.1f}"/>')
parts.append(f'<path d="M{left[0] + (left[2] if abs(left[4]) < 45 else left[3]):.1f},{hy:.1f}'
             f'H{right[0] - (right[2] if abs(right[4]) < 45 else right[3]):.1f}"/>')
heads = []
for m in arcs:
    d = ndimage.distance_transform_edt(m)
    head = ndimage.binary_opening(m, structure=np.ones((int(sw) + 3, int(sw) + 3)))  # only the head is that thick
    shaft = m & ~ndimage.binary_dilation(head, iterations=3)
    c = centre_line(shaft)
    yy, xx = np.nonzero(c)
    ox, oy = xx.mean(), yy.mean()
    X, Y = xx - ox, yy - oy
    A = np.c_[X, Y, np.ones_like(X)]
    sol = np.linalg.lstsq(A, -(X * X + Y * Y), rcond=None)[0]
    ccx, ccy = -sol[0] / 2 + ox, -sol[1] / 2 + oy
    R = np.sqrt((sol[0] / 2) ** 2 + (sol[1] / 2) ** 2 - sol[2])
    th = np.arctan2(yy - ccy, xx - ccx)
    hy_, hx_ = np.nonzero(head)
    thh = np.arctan2(hy_.mean() - ccy, hx_.mean() - ccx)
    # arc from the far end of the shaft to the head's base
    order = np.argsort(np.angle(np.exp(1j * (th - thh))))
    t0 = th[np.argmax(np.abs(np.angle(np.exp(1j * (th - thh)))))]
    t1 = th[np.argmin(np.abs(np.angle(np.exp(1j * (th - thh)))))]
    p0 = (ccx + R * np.cos(t0), ccy + R * np.sin(t0))
    p1 = (ccx + R * np.cos(t1), ccy + R * np.sin(t1))
    sweep = 1 if np.angle(np.exp(1j * (t1 - t0))) > 0 else 0
    parts.append(f'<path d="M{p0[0]:.1f},{p0[1]:.1f}A{R:.1f},{R:.1f} 0 0 {sweep} {p1[0]:.1f},{p1[1]:.1f}"/>')
    heads += polygons(head, tol=1.5, min_area=20)
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
       f'<g fill="none" stroke="#000" stroke-width="{sw:.2f}">' + ''.join(parts) + '</g>'
       f'<path d="{to_path_d(heads)}" fill="#000"/></svg>')
open(OUT, 'w', encoding='utf8').write(svg)
o = np.asarray(Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=svg)))).convert('RGBA'))[..., 3] > 128
print('stroke %.2f' % sw, [(k, [round(float(v), 1) for v in e]) for k, e in ell], 'ink IoU %.4f' % ((o & ink).sum() / (o | ink).sum()))
rgb = np.full((H, W, 3), 255, np.uint8); rgb[ink & ~o] = (0, 0, 255); rgb[o & ~ink] = (220, 0, 0); rgb[o & ink] = (90, 90, 90)
Image.fromarray(rgb).save('scratch/arms/kongo_diff.png')
