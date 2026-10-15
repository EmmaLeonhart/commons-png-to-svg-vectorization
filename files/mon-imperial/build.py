"""Rebuild File:Mon-Imperial.png: File:Imperial Seal of Japan.svg (public domain geometry) on a
flat red square. Seal size and centre fitted to the PNG's gold pixels; colours are the PNG's
median red and gold (its red has a woven texture, drawn here as flat colour). Run from the repo root."""
import io
import numpy as np, resvg_py
from PIL import Image

a = np.asarray(Image.open('data_lake/downloads/order-life-arms/png/Mon-Imperial.png').convert('RGB')).astype(int)
H, W = a.shape[:2]
gold = (a[..., 0] > 180) & (a[..., 1] > 150) & (a[..., 2] < 120)
red = (a[..., 0] > 120) & (a[..., 1] < 90)
hexc = lambda px: '#%02x%02x%02x' % tuple(np.median(px, 0).astype(int))
RED, GOLD = hexc(a[red & ~gold]), hexc(a[gold])
ys, xs = np.nonzero(gold)
cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
seal = open('data_lake/downloads/kamon/Imperial Seal of Japan.svg', encoding='utf8').read()
inner = seal[seal.index('<use'):seal.rindex('</svg>')].replace('#ffd700', GOLD)


def svg(r, cx, cy, stroke):
    # the seal's viewBox is -99..99 with petal tips at radius 97; r is the tip radius in PNG pixels
    s = r / 97
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<rect width="{W}" height="{H}" fill="{RED}"/>'
            f'<g transform="translate({cx:.2f},{cy:.2f}) scale({s:.5f})">{inner.replace("stroke=\"#000\"", f"stroke=\"{stroke}\"")}</g></svg>')


def score(s):
    im = np.asarray(Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=s)))).convert('RGB')).astype(int)
    g = (im[..., 0] > 180) & (im[..., 1] > 150) & (im[..., 2] < 120)
    return (g & gold).sum() / (g | gold).sum()


r0 = (xs.max() - xs.min()) / 2
best = max((score(svg(r, cx + dx, cy + dy, RED)), r, cx + dx, cy + dy)
           for r in np.arange(r0 - 4, r0 + 4.1, 0.5) for dx in (-1, 0, 1) for dy in (-1, 0, 1))
print('gold IoU %.4f  r %.1f  centre %.1f,%.1f' % best, RED, GOLD)
open('files/mon-imperial/Mon-Imperial.svg', 'w', encoding='utf8').write(svg(*best[1:], RED))
