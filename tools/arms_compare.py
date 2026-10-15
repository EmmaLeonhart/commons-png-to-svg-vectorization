"""Compare a generator-built coat of arms with the raster it replaces.

Both images are cropped to their shield (non-background pixels), scaled to the same box, and each
pixel is snapped to the nearest heraldic tincture. Reports the share of shield pixels whose tincture
agrees, and writes a side-by-side picture (PNG left, SVG right).
Usage: python tools/arms_compare.py file.png file.svg picture.png [--box x0,y0,x1,y1]
--box crops the PNG first (fractions of its size), for shields inside a garter or achievement.
"""
import argparse, io
import numpy as np
import resvg_py
from PIL import Image, ImageDraw

TINCTURES = {  # rough RGB of each tincture as Commons artists draw them, plus outline black
    'or': (252, 221, 9), 'argent': (255, 255, 255), 'gules': (218, 18, 26), 'azure': (0, 101, 189),
    'vert': (0, 149, 64), 'sable': (0, 0, 0), 'purpure': (128, 0, 128), 'tenne': (210, 120, 30),
    'grey': (160, 160, 160),
}
NAMES = list(TINCTURES)
PAL = np.array([TINCTURES[n] for n in NAMES], float)
BOX = (200, 240)


def shield(im):
    im = im.convert('RGBA')
    a = np.asarray(im)
    rgb = a[..., :3].astype(int)
    alpha = a[..., 3] > 128
    # background: transparent, or the corner colour when the image is opaque
    corner = rgb[0, 0]
    fg = alpha & (np.abs(rgb - corner).sum(-1) > 40) if alpha.all() else alpha
    ys, xs = np.nonzero(fg)
    im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).resize(BOX, Image.LANCZOS)
    a = np.asarray(im).astype(float)
    mask = a[..., 3] > 128
    if mask.all():
        corner = a[0, 0, :3]
        mask = np.abs(a[..., :3] - corner).sum(-1) > 40
    return im, classify(a[..., :3]), mask


def classify(rgb):
    """Tincture class per pixel by hue, so textured or darker artists' colours still count:
    0 argent, 1 sable, 2 or, 3 gules, 4 azure, 5 vert, 6 purpure, 7 tenne, 8 grey/untinctured."""
    from colorsys import rgb_to_hsv
    import numpy as np
    r, g, b = (rgb[..., i] / 255 for i in range(3))
    mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
    v, s = mx, np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    d = np.maximum(mx - mn, 1e-6)
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    out = np.full(r.shape, 8)
    grey = s < 0.25
    out[grey & (v > 0.75)] = 0
    out[grey & (v < 0.3)] = 1
    out[~grey & (v < 0.18)] = 1
    col = ~grey & (v >= 0.18)
    out[col & ((h < 18) | (h >= 330))] = 3
    out[col & (h >= 18) & (h < 38)] = 7
    out[col & (h >= 38) & (h < 70)] = 2
    out[col & (h >= 70) & (h < 170)] = 5
    out[col & (h >= 170) & (h < 260)] = 4
    out[col & (h >= 260) & (h < 330)] = 6
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('png'); ap.add_argument('svg'); ap.add_argument('out')
    ap.add_argument('--box')
    args = ap.parse_args()
    ref = Image.open(args.png)
    if args.box:
        x0, y0, x1, y1 = map(float, args.box.split(','))
        w, h = ref.size
        ref = ref.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h)))
    ours = Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=open(args.svg, encoding='utf-8').read(), width=600))))
    ri, rl, rm = shield(ref)
    oi, ol, om = shield(ours)
    both = rm & om
    agree = (rl == ol)[both].mean()
    sil = (rm & om).sum() / max((rm | om).sum(), 1)
    sheet = Image.new('RGB', (2 * BOX[0] + 30, BOX[1] + 40), 'white')
    for i, im in enumerate((ri, oi)):
        bg = Image.new('RGBA', im.size, 'white')
        sheet.paste(Image.alpha_composite(bg, im.convert('RGBA')).convert('RGB'), (10 + i * (BOX[0] + 10), 10))
    ImageDraw.Draw(sheet).text((10, BOX[1] + 15), f'tincture agreement {agree:.3f}   silhouette IoU {sil:.3f}', fill='black')
    sheet.save(args.out)
    print(f'tincture agreement {agree:.3f}  silhouette IoU {sil:.3f}')


if __name__ == '__main__':
    main()
