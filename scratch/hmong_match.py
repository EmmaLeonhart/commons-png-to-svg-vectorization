import io, numpy as np, resvg_py
from PIL import Image
from fontTools.ttLib import TTFont
F = 'data_lake/downloads/fonts/noto-pahawh-hmong/NotoSansPahawhHmong-Regular.ttf'
cmap = TTFont(F).getBestCmap()
im = Image.open('data_lake/downloads/indigenous-of-asia/Indigenous of Asia.png').convert('RGBA')
ink = np.array(Image.alpha_composite(Image.new('RGBA', im.size, 'white'), im).convert('L')) < 128
cols = ink.any(0); xs = np.nonzero(cols)[0]
segs = []; s = xs[0]; p = xs[0]
for x in xs[1:]:
    if x - p > 3: segs.append((s, p + 1)); s = x
    p = x
segs.append((s, p + 1))
def render(t):
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300"><text x="100" y="220" font-size="150" font-family="Noto Sans Pahawh Hmong">{t}</text></svg>'
    r = Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=svg, width=400, font_files=[F], skip_system_fonts=True)))).convert('RGBA')
    return np.array(r)[..., 3] > 128
def crop(m):
    ys, xs = np.nonzero(m); return m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
bases = [c for c in range(0x16B00, 0x16B30) if c in cmap]
marks = [c for c in range(0x16B30, 0x16B37) if c in cmap]
cands = {chr(b): crop(render(chr(b))) for b in bases}
cands.update({chr(b) + chr(m): crop(render(chr(b) + chr(m))) for b in bases for m in marks})
# extra: other Pahawh signs (punctuation etc.)
for c in range(0x16B37, 0x16B90):
    if c in cmap:
        m = render(chr(c))
        if m.any(): cands[chr(c)] = crop(m)
out = []
for a, b in segs:
    g = crop(ink[:, a:b]); best = []
    for t, c in cands.items():
        T = np.array(Image.fromarray(c).resize((g.shape[1], g.shape[0])))
        iou = (T & g).sum() / (T | g).sum()
        ar = abs(np.log((c.shape[1] / c.shape[0]) / (g.shape[1] / g.shape[0])))
        best.append((iou - 0.3 * ar, t, round(float(iou), 2)))
    best.sort(reverse=True)
    out.append((a, b, best[:2]))
    print(a, b, [(' '.join('%X' % ord(ch) for ch in t), i) for _, t, i in best[:2]])
