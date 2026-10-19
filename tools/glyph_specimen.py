"""Rebuild a script-specimen PNG (one glyph or a short run of text on a plain background) as SVG <text>:
the text is set in the given font and scaled and placed so its rendered (shaped) ink box matches the PNG's ink box.
Prints the pixel difference and IoU against the PNG and writes a side-by-side comparison.
usage: python tools/glyph_specimen.py in.png out.svg "<text>" font.ttf "Font Family" [weight] [cmp.png]
"""
import io, sys
import numpy as np, resvg_py
from PIL import Image

png, out, text, font, family, *rest = sys.argv[1:]
weight = rest[0] if rest else '400'
cmp_path = rest[1] if len(rest) > 1 else None

im = Image.open(png).convert('RGBA')
W, H = im.size
flat = Image.alpha_composite(Image.new('RGBA', im.size, 'white'), im).convert('L')
ink = np.array(flat) < 128
ys, xs = np.nonzero(ink)
bx0, bx1, by0, by1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
rgb = np.median(np.array(im.convert('RGB'))[ink], axis=0).astype(int)
colour = '#000000' if rgb.max() < 64 else '#%02x%02x%02x' % tuple(rgb)  # anti-aliasing tints black ink

def render(svg, w):
    r = Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=svg, width=w, font_files=[font],
                                                          skip_system_fonts=True)))).convert('RGBA')
    return r, np.array(Image.alpha_composite(Image.new('RGBA', r.size, 'white'), r).convert('L')) < 128


def doc(w, h, attrs):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
            f'<text{attrs} font-family="{family}" font-weight="{weight}" fill="{colour}">{text}</text>\n</svg>\n')


# measure the shaped run's ink at a probe size (shaping, joining and bidi are the renderer's), then fit
P = 200
pw = P * (len(text) + 2) * 2
_, probe = render(doc(pw, 3 * P, f' x="{P}" y="{2 * P}" font-size="{P}"'), pw)
ys, xs = np.nonzero(probe)
px0, px1, py0, py1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
k = (by1 - by0) / (py1 - py0)            # px per probe px, from the ink height
sx = (bx1 - bx0) / ((px1 - px0) * k)     # horizontal correction, kept as a scale() if it matters
if abs(sx - 1) <= 0.02:
    sx = 1.0
fs = P * k
tx = bx0 / sx - (px0 - P) * k
ty = by0 - (py0 - 2 * P) * k
tf = f' transform="scale({sx:.4f},1)"' if sx != 1.0 else ''
svg = doc(W, H, f'{tf} x="{tx:.2f}" y="{ty:.2f}" font-size="{fs:.2f}"')
open(out, 'w', encoding='utf8').write(svg)
r, rl = render(svg, W)
print(f'{out}: font-size {fs:.1f}, scale-x {sx:.3f}, differ {100 * (rl != ink).mean():.2f}%, '
      f'IoU {(rl & ink).sum() / (rl | ink).sum():.3f}')
if cmp_path:
    k = max(1, 240 // max(W, H))
    c = Image.new('RGB', (2 * W * k + 10, H * k), '#dddddd')
    c.paste(flat.convert('RGB').resize((W * k, H * k), 0), (0, 0))
    c.paste(Image.alpha_composite(Image.new('RGBA', r.size, 'white'), r).convert('RGB').resize((W * k, H * k), 0),
            (W * k + 10, 0))
    c.save(cmp_path)
