"""Rebuild the TransJakarta corridor/route icons and roundels (a coloured disc with a white bold label)
by construction: the disc from the alpha mask, its colour as the median of its non-white pixels, and the
label (taken from the file name) as real <text>, white bold, sized and placed to the label's ink in the PNG
with DejaVu Sans Condensed Bold metrics, stretched vertically to the label's ink height.
Writes files/<slug>/ and upload/<slug>/ for each PNG given.
usage: python tools/transjakarta_icons.py data_lake/downloads/transjakarta/*.png"""
import io, json, re, sys
from pathlib import Path
import numpy as np, resvg_py
from PIL import Image, ImageFont

FONTS = Path('data_lake/downloads/fonts/dejavu')
BOLD, COND = FONTS / 'DejaVuSans-Bold.ttf', FONTS / 'DejaVuSansCondensed-Bold.ttf'


def label_of(name):
    m = re.search(r'Corridor (\w+) Icon|Route (\w+) Icon|roundel (\w+)', name)
    return next(g for g in m.groups() if g)


def fit(text, box, font):
    x0, x1, y0, y1 = box
    best = min((abs(ImageFont.truetype(str(font), s).getbbox(text, anchor='ls')[2] - ImageFont.truetype(str(font), s).getbbox(text, anchor='ls')[0] - (x1 - x0 + 1)), s)
               for s in np.arange(10, 2000, 1 if x1 - x0 > 300 else 0.25))[1]
    f = ImageFont.truetype(str(font), best)
    l, t, r, b = f.getbbox(text, anchor='ls')
    return best, x0 - l, y0 - t, (y1 - y0 + 1) / (b - t)


def build(png):
    name = Path(png).name
    text = label_of(name)
    im = Image.open(png).convert('RGBA')
    a = np.asarray(im).astype(int)
    H, W = a.shape[:2]
    disc = a[..., 3] > 128
    white = disc & (a[..., :3].min(-1) > 200)
    ys, xs = np.nonzero(disc)
    cx, cy = (xs.min() + xs.max() + 1) / 2, (ys.min() + ys.max() + 1) / 2
    r = np.sqrt(disc.sum() / np.pi)
    colour = '#%02x%02x%02x' % tuple(int(v) for v in np.median(a[disc & ~white][:, :3], 0))
    ys, xs = np.nonzero(white)
    box = (xs.min(), xs.max(), ys.min(), ys.max())
    # the PNG's typeface is narrower for its height than DejaVu: condensed bold, width fitted, then
    # stretched vertically to the label's ink height (still real <text>)
    font, family = COND, "'DejaVu Sans Condensed', 'DejaVu Sans'"
    size, x, _, hratio = fit(text, box, COND)
    l, t, rr, b = ImageFont.truetype(str(COND), size).getbbox(text, anchor='ls')
    base = box[2] - t * hratio
    def make(x, sx):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{colour}"/>'
                f'<text transform="translate({x:.1f},{base:.1f}) scale({sx:.4f},{hratio:.3f})" font-family="{family}" '
                f'font-weight="bold" font-size="{size:.1f}" fill="#fff">{text}</text></svg>')
    # one correction pass: the renderer's glyph advances differ slightly from PIL's, so measure the
    # rendered label and match its left edge and width to the PNG's
    sx = 1.0
    for _ in range(2):
        rr_ = np.asarray(Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=make(x, sx), font_files=[str(BOLD), str(COND)], skip_system_fonts=True)))).convert('RGB')).astype(int)
        wy, wx = np.nonzero(disc & (rr_.min(-1) > 200))
        if len(wx) == 0:
            break
        got_w = wx.max() - wx.min() + 1
        sx *= (box[1] - box[0] + 1) / got_w
        x += box[0] - wx.min() * 1.0 if abs(box[0] - wx.min()) < W / 4 else 0
    svg = make(x, sx)
    slug = re.sub(r'[^a-z0-9]+', '-', name[:-4].lower()).strip('-')
    for d in (Path('files') / slug, Path('upload') / slug):
        d.mkdir(parents=True, exist_ok=True)
        (d / (name[:-4] + '.svg')).write_text(svg, encoding='utf8')
    o = np.asarray(Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=svg, font_files=[str(BOLD), str(COND)], skip_system_fonts=True)))).convert('RGBA')).astype(int)
    on_white = lambda q: q[..., :3] * (q[..., 3:] / 255) + 255 * (1 - q[..., 3:] / 255)
    diff = float((np.abs(on_white(o) - on_white(a)).max(-1) > 64).mean())
    notes = (f'# File:{name} → SVG\n\nConstructed by `tools/transjakarta_icons.py`: a {colour} disc (r {r:.1f}, measured) and the '
             f'label "{text}" as white bold `<text>` in {family.split(",")[0]}, sized and placed to the PNG\'s label ink '
             f'(the PNG\'s own typeface differs a little, so glyph shapes differ). {diff * 100:.1f}% of pixels differ. '
             f'Licence: PD-simple, as the PNG.\n')
    for d in (Path('files') / slug, Path('upload') / slug):
        (d / 'notes.md').write_text(notes, encoding='utf8')
    return name, text, colour, family.split(',')[0], round(diff, 4)


if __name__ == '__main__':
    for p in sys.argv[1:]:
        print(build(p))
