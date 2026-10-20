# One-off: recover the Unicode text of a Psalter Pahlavi PNG set in Noto Sans Psalter Pahlavi by beam search
# (build each segment right to left, render the shaped candidate, score against the ink).
import io, json, sys
import numpy as np, resvg_py
from PIL import Image

F = 'data_lake/downloads/fonts/noto-psalter-pahlavi/NotoSansPsalterPahlavi-Regular.ttf'
PNG = 'data_lake/downloads/cross-of-herat/Cross of Herat - Psalter Pahlavi Inscription.png'
ink = np.array(Image.open(PNG).convert('L')) < 128
H, W = ink.shape
LET = [chr(c) for c in range(0x10B80, 0x10B92)]
ZWJ = '‍'


def render(s, fs, cw, ch, xr, base):
    """ink of s, text-anchor end at xr (RTL run, so its visual right edge is near xr), canvas cw x ch"""
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{cw}" height="{ch}"><text x="{xr}" y="{base}" '
           f'font-size="{fs}" font-family="Noto Sans Psalter Pahlavi" direction="rtl" text-anchor="start">{s}</text></svg>')
    im = Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=svg, width=cw, font_files=[F],
                                                           skip_system_fonts=True)))).convert('RGBA')
    return np.array(im)[..., 3] > 128


def ink_box(m):
    ys, xs = np.nonzero(m)
    return (xs.min(), xs.max() + 1, ys.min(), ys.max() + 1) if len(xs) else None


def score(s, seg, fs, base, final):
    """IoU between the rendering of s (forced joining unless final) aligned at the segment's right edge and the
    segment's ink over the rendered columns; plus the rendered width."""
    T = seg
    ch, cw = T.shape[0], T.shape[1] + 200
    m = render(s + ('' if final else ZWJ), fs, cw, ch, cw - 100, base)
    b = ink_box(m)
    if b is None:
        return 0, 0
    # shift so the rendered ink's right edge sits on the segment's right edge
    dx = (T.shape[1]) - b[1]
    x0 = max(0, b[0] + dx)  # first segment column the rendering covers
    Rc = m[:, x0 - dx:T.shape[1] - dx]
    Tc = T[:, x0:]
    inter = (Tc & Rc).sum()
    uni = (Tc | Rc).sum()
    return inter / max(1, uni), T.shape[1] - x0


def decode(seg, fs, base, beam=24):
    hyps = [('', 0.0)]
    done = []
    for step in range(30):
        cand = []
        for s, _ in hyps:
            for L in LET + ([' '] if s and s[-1] != ' ' else []):
                t = s + L
                sc, w = score(t, seg, fs, base, final=False)
                cand.append((sc, w, t))
                if L != ' ':
                    scf, wf = score(t, seg, fs, base, final=True)
                    if wf >= seg.shape[1] - 6:
                        done.append((scf, t))
        cand = [c for c in cand if c[1] <= seg.shape[1] + 4]
        if not cand:
            break
        cand.sort(key=lambda c: (-c[0]))
        hyps = [(t, sc) for sc, w, t in cand[:beam]]
    done.sort(reverse=True)
    return done[:3]


if __name__ == '__main__':
    spec = json.loads(sys.argv[1])  # [[y0, y1, x0, x1], ...]
    fs, base = float(sys.argv[2]), float(sys.argv[3])
    for y0, y1, x0, x1 in spec:
        seg = ink[y0:y1, x0:x1]
        print(y0, x0, x1, [(round(float(a), 3), ' '.join('%X' % ord(c) if c != ' ' else '_' for c in t)) for a, t in decode(seg, fs, base - y0)], flush=True)
