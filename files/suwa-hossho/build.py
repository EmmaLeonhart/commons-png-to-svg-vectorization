"""Rebuild File:Suwa Hosshō Banner - 諏訪法性旗.png: the red banner with the brush inscription 南無諏方南宮法性上下大明神 as
real <text> in gold, set vertically as one <text> with a positioned <tspan> per character (no writing-mode needed),
spaced evenly down the PNG's column of lettering and sized to its width, in a kaisho (brush) face, outlined
in the same gold (10 px) so its weight matches the brush lettering's (same amount of gold). Run from the repo
root."""
import numpy as np
from PIL import Image

PNG = 'data_lake/downloads/suwa-hossho/Suwa Hosshō Banner - 諏訪法性旗.png'
OUT = 'files/suwa-hossho/Suwa Hosshō Banner - 諏訪法性旗.svg'
TEXT = '南無諏方南宮法性上下大明神'
RED, GOLD = '#c83230', '#e4c46d'
FONT = "KaiTi, SimKai, 'HGSeikaishotaiPRO', 'AR PL UKai', 'Noto Serif CJK JP', serif"

a = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
H, W = a.shape[:2]
gold = a[..., 1] > 120
ys, xs = np.nonzero(gold)
x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
n = len(TEXT)
pitch = (y1 - y0) / n
size = min(x1 - x0, pitch) * 1.04  # the brush glyphs fill the column; a kaisho face's ink is a little inside its em
cx = (x0 + x1) / 2
spans = ''.join(f'<tspan x="{cx:.1f}" y="{y0 + (i + 0.5) * pitch + 0.37 * size:.1f}">{ch}</tspan>' for i, ch in enumerate(TEXT))
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
       f'<rect width="{W}" height="{H}" fill="{RED}"/>\n'
       f'<text font-family="{FONT}" font-size="{size:.1f}" text-anchor="middle" fill="{GOLD}" stroke="{GOLD}" stroke-width="10" stroke-linejoin="round">{spans}</text>\n</svg>\n')
open(OUT, 'w', encoding='utf8').write(svg)
print('wrote', OUT, 'column', x0, x1, y0, y1, 'size %.1f pitch %.1f' % (size, pitch))
