"""Fit one line of <text> to an ink box measured in a PNG: font size from the box height, letter-spacing from its
width, start position from its left/bottom edges. Start-anchored, so the result does not depend on how a renderer
treats trailing letter-spacing with text-anchor="middle".
usage (module): fit(text, box, family, weight='normal', canvas=(W, H), rounds=3) -> dict(x, y, size, ls)
  box = (x0, x1, y0, y1) ink extent in pixels (inclusive)
"""
from pathlib import Path

import numpy as np
from PIL import Image

from render_svg import render

WORK = Path('scratch/fit_text_tool')


PAD = 300  # the fit renders on a padded canvas so oversized trial text is never clipped


def _measure(text, family, weight, p, canvas):
    W, H = canvas[0] + 2 * PAD, canvas[1] + 2 * PAD
    WORK.mkdir(parents=True, exist_ok=True)
    st = f"font-family:{family};font-weight:{weight};font-size:{p['size']:.2f}px;fill:#000"
    if p['ls']:
        st += f";letter-spacing:{p['ls']:.2f}px"
    t = text.replace('&', '&amp;').replace('<', '&lt;')
    f = WORK / 'line.svg'
    f.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><rect width="100%" height="100%" fill="#fff"/>'
                 f'<text x="{p["x"] + PAD:.2f}" y="{p["y"] + PAD:.2f}" style="{st}">{t}</text></svg>', encoding='utf8')
    render(f, WORK / 'line.png')
    a = np.array(Image.open(WORK / 'line.png').convert('L')) < 128
    ys, xs = np.nonzero(a)
    return xs.min() - PAD, xs.max() - PAD, ys.min() - PAD, ys.max() - PAD


def fit(text, box, family, weight='normal', canvas=(1000, 1000), rounds=3):
    x0, x1, y0, y1 = box
    p = dict(x=x0, y=y1, size=(y1 - y0 + 1) / 0.72, ls=0.0)
    n = max(1, len(text) - 1)
    for r in range(rounds + 1):
        bx0, bx1, by0, by1 = _measure(text, family, weight, p, canvas)
        if r == 0:
            p['size'] *= (y1 - y0) / max(1, by1 - by0)
        else:
            p['ls'] += ((x1 - x0) - (bx1 - bx0)) / n
        p['x'] += x0 - bx0
        p['y'] += y1 - by1
    bx0, bx1, by0, by1 = _measure(text, family, weight, p, canvas)
    p['x'] += x0 - bx0
    p['y'] += y1 - by1
    p['final_box'] = tuple(int(v) for v in _measure(text, family, weight, p, canvas))
    return {k: (round(float(v), 2) if not isinstance(v, tuple) else v) for k, v in p.items()}
