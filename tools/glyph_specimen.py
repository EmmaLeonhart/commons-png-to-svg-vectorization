"""Rebuild a script-specimen PNG (one glyph or a short run of text on a plain background) as SVG <text>:
the text is set in the given font, scaled and placed so its ink box matches the PNG's ink box.
Prints the pixel difference and IoU against the PNG and writes a side-by-side comparison.
usage: python tools/glyph_specimen.py in.png out.svg "<text>" font.ttf "Font Family" [weight] [cmp.png]
"""
import io, sys
import numpy as np, resvg_py
from PIL import Image
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen

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

f = TTFont(font)
gs, cmap, upm = f.getGlyphSet(), f.getBestCmap(), f['head'].unitsPerEm
x, bounds = 0, [1e9, 1e9, -1e9, -1e9]
for ch in text:  # ink box of the run (no shaping: fine for one glyph or simple runs)
    g = cmap[ord(ch)]
    bp = BoundsPen(gs)
    gs[g].draw(bp)
    if bp.bounds:
        a, b, c, d = bp.bounds
        bounds = [min(bounds[0], x + a), min(bounds[1], b), max(bounds[2], x + c), max(bounds[3], d)]
    x += gs[g].width
gx0, gy0, gx1, gy1 = bounds
s = (by1 - by0) / (gy1 - gy0)          # font units -> px, from the ink height
sx = (bx1 - bx0) / ((gx1 - gx0) * s)    # horizontal correction, kept as a scale() if it matters
fs = s * upm
tx = bx0 / sx - gx0 * s
ty = by0 + gy1 * s
tf = f' transform="scale({sx:.4f},1)"' if abs(sx - 1) > 0.02 else ''
if not tf:
    tx = bx0 - gx0 * s
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
       f'<text{tf} x="{tx:.2f}" y="{ty:.2f}" font-family="{family}" font-weight="{weight}" '
       f'font-size="{fs:.2f}" fill="{colour}">{text}</text>\n</svg>\n')
open(out, 'w', encoding='utf8').write(svg)

r = Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=svg, width=W, font_files=[font],
                                                      skip_system_fonts=True)))).convert('RGBA')
rl = np.array(Image.alpha_composite(Image.new('RGBA', r.size, 'white'), r).convert('L')) < 128
print(f'{out}: font-size {fs:.1f}, scale-x {sx:.3f}, differ {100 * (rl != ink).mean():.2f}%, '
      f'IoU {(rl & ink).sum() / (rl | ink).sum():.3f}')
if cmp_path:
    k = max(1, 240 // max(W, H))
    c = Image.new('RGB', (2 * W * k + 10, H * k), '#dddddd')
    c.paste(flat.convert('RGB').resize((W * k, H * k), 0), (0, 0))
    c.paste(Image.alpha_composite(Image.new('RGBA', r.size, 'white'), r).convert('RGB').resize((W * k, H * k), 0),
            (W * k + 10, 0))
    c.save(cmp_path)
