"""Rebuild File:Appalachian region of United States.png: map layers from layers.py and every label as
<text>. State names are italic serif small capitals (capital letters, the rest in a smaller <tspan>),
Liberation Serif (Times metrics); title, date and source italic Liberation Sans (Arial metrics). Each
label's size, position (and for Maryland, angle) is fitted to its ink in the PNG. Run from the repo root
with PYTHONPATH=files/appalachian-region after fit.py and map.py."""
import numpy as np
from PIL import Image, ImageFont
from scipy import ndimage
import common as C
from layers import layers

OUT = 'files/appalachian-region/Appalachian region of United States.svg'
TIMES_I = r'C:\Windows\Fonts\timesi.ttf'
ARIAL_I, ARIAL_BI = r'C:\Windows\Fonts\ariali.ttf', r'C:\Windows\Fonts\arialbi.ttf'
SERIF = "'Liberation Serif', 'Times New Roman', Times, serif"
SANS = "'Liberation Sans', Arial, Helvetica, sans-serif"
SC = 0.8  # small capitals 8 px against capitals 10 px (measured on New York and Tennessee)
a = np.asarray(Image.open(C.PNG).convert('RGB')).astype(int)
lum = a.mean(-1)

STATES = {  # label: ink window (x0, x1, y0, y1) in the PNG
    'New York': (420, 512, 44, 63), 'Pennsylvania': (382, 500, 124, 142), 'Ohio': (244, 292, 168, 186),
    'Kentucky': (124, 212, 288, 306), 'Virginia': (399, 476, 295, 314), 'Tennessee': (70, 162, 363, 381),
    'North Carolina': (358, 500, 373, 391), 'South Carolina': (296, 432, 434, 452),
    'Mississippi': (11, 91, 512, 530), 'Alabama': (111, 187, 535, 553), 'Georgia': (237, 311, 507, 525),
}


def ink_box(win, thr=120, max_h=16):
    x0, x1, y0, y1 = win
    m = lum[y0:y1, x0:x1] < thr
    lab, n = ndimage.label(m)
    keep = np.zeros_like(m)
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if h <= max_h and w <= 16:
            keep |= lab == i
    ys, xs = np.nonzero(keep)
    return xs.min() + x0, xs.max() + x0, ys.min() + y0, ys.max() + y0, keep


def runs_of(name):
    """small capitals: [(text, is_capital)] in display order."""
    out = []
    for word_i, word in enumerate(name.split(' ')):
        if word_i:
            out.append((' ', False))
        out += [(word[0].upper(), True), (word[1:].upper(), False)]
    return out


def sc_width(name, S):
    big, small = ImageFont.truetype(TIMES_I, S), ImageFont.truetype(TIMES_I, S * SC)
    return sum((big if cap else small).getlength(t) for t, cap in runs_of(name))


def sc_text(name, x, y, S, extra=''):
    parts = ''.join(t if cap else f'<tspan font-size="{S * SC:.2f}">{t}</tspan>' for t, cap in runs_of(name))
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{S:.2f}"{extra}>{parts}</text>'


CAP = 0.662  # cap height of Times italic, in em


def glyphs(win, thr=130):
    """glyph boxes in a label window: dark components of glyph size (lines and noise dropped)."""
    x0, x1, y0, y1 = win
    lab, n = ndimage.label(lum[y0:y1, x0:x1] < thr)
    out = []
    for sl in ndimage.find_objects(lab):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if 4 <= h <= 13 and w <= 14:
            out.append((sl[1].start + x0, sl[1].stop + x0, sl[0].start + y0, sl[0].stop + y0))
    return sorted(out)


def spaced(name, gl):
    """size, letter-spacing and start of a small-capital label from its glyphs."""
    base = int(np.median([g[3] for g in gl]))
    S = 10 / CAP  # every state label has 10 px capitals
    ink_w = max(g[1] for g in gl) - gl[0][0]
    n = len(name)
    ls = (ink_w - sc_width(name, S)) / (n - 1)
    lb = ImageFont.truetype(TIMES_I, S).getbbox(name[0], anchor='ls')[0]
    return S, ls, gl[0][0] - lb, base


labels = []
for name, win in STATES.items():
    S, ls, x, base = spaced(name, glyphs(win))
    labels.append(sc_text(name, x, base, S, f' letter-spacing="{ls:.2f}"'))

# West Virginia: mixed case italic, not small capitals, same capital height
gl = glyphs((318, 412, 233, 252))
base = int(np.median([g[3] for g in gl]))
S = 10 / CAP
f = ImageFont.truetype(TIMES_I, S)
ls = ((max(g[1] for g in gl) - gl[0][0]) - (f.getlength('West Virginia') - f.getbbox('W', anchor='ls')[0])) / 12
labels.append(f'<text x="{gl[0][0] - f.getbbox("W", anchor="ls")[0]:.1f}" y="{base}" font-size="{S:.2f}" '
              f'letter-spacing="{ls:.2f}">West Virginia</text>')

# Maryland: along a slant, measured on the PNG: baseline from (462, 210) to (527.5, 251.3)
(mx0, my0), (mx1, my1) = (462.0, 210.0), (527.5, 251.3)
ang = float(np.degrees(np.arctan2(my1 - my0, mx1 - mx0)))
length = float(np.hypot(mx1 - mx0, my1 - my0))
S = 10 / CAP
ls = (length - sc_width('Maryland', S)) / 7
labels.append(f'<g transform="translate({mx0:.1f},{my0:.1f}) rotate({ang:.1f})">'
              + sc_text('Maryland', 0, 0, S, f' letter-spacing="{ls:.2f}"') + '</g>')
serif = f'<g font-family="{SERIF}" font-style="italic" fill="#000">' + ''.join(labels) + '</g>'


def sans_line(t, win, path, color, weight=''):
    x0, x1, y0, y1, _ = ink_box(win, thr=170, max_h=20)
    best = min((abs(ImageFont.truetype(path, s).getbbox(t, anchor='ls')[2] - ImageFont.truetype(path, s).getbbox(t, anchor='ls')[0] - (x1 - x0 + 1)), s) for s in np.arange(8, 24, 0.05))[1]
    f = ImageFont.truetype(path, best)
    l, tp, r, b = f.getbbox(t, anchor='ls')
    w = ' font-weight="bold"' if weight else ''
    return f'<text x="{x0 - l:.1f}" y="{y0 - tp:.1f}" font-size="{best:.2f}" fill="{color}"{w}>{t}</text>'


sans = (f'<g font-family="{SANS}" font-style="italic">'
        + sans_line('The Appalachian Region', (2, 192, 5, 29), ARIAL_I, '#000')
        + sans_line('October 8, 2008', (484, 569, 551, 568), ARIAL_I, '#404040')
        + sans_line('Source: Appalachian Regional Commission', (2, 210, 570, 585), ARIAL_I, '#404040') + '</g>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{C.W}" height="{C.H}" viewBox="0 0 {C.W} {C.H}">'
       f'<rect width="{C.W}" height="{C.H}" fill="#fff"/>{layers()}{serif}{sans}</svg>')
open(OUT, 'w', encoding='utf8').write(svg)
o = C.render(svg, [TIMES_I, ARIAL_I, ARIAL_BI])
print('Maryland angle %.1f size %.1f  pixels differing %.4f' % (ang, S, (np.abs(o - a).max(-1) > 64).mean()))
Image.fromarray(np.concatenate([a, o], 1).astype(np.uint8)).save('scratch/arms/app_cmp.png')
