"""Fit size and position of each text line of a build.py (TEXT list + params.json) to the PNG's ink
boxes: render each line alone, measure, rescale by height, then match width with letter-spacing
and place by the box. usage: python scratch/fit_text_lines.py files/<slug>/build.py PNG [rounds]"""
import importlib.util, json, sys, subprocess
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, 'tools')
from render_svg import render

bp, png = Path(sys.argv[1]), sys.argv[2]
rounds = int(sys.argv[3]) if len(sys.argv) > 3 else 3
spec = importlib.util.spec_from_file_location('b', bp); b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
work = Path('scratch/fit_text'); work.mkdir(parents=True, exist_ok=True)
params = json.loads(b.PARAMS.read_text(encoding='utf8')) if b.PARAMS.exists() else {}
for r in range(rounds):
    for t in b.TEXT:
        i, s, colour, scr, x0, x1, y0, y1 = t
        p = {**b.defaults(t), **params.get(i, {})}
        anchor = 'start' if i in b.LEFT_ALIGNED else 'middle'
        fam = b.LATIN if scr == 'latin' else b.CJK
        st = f"font-family:{fam};font-size:{p['size']:.2f}px;fill:#000" + (f";letter-spacing:{p['ls']:.2f}px" if p.get('ls') else '')
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{b.W}" height="{b.H}"><rect width="100%" height="100%" fill="#fff"/>'
               f'<text x="{p["x"]:.2f}" y="{p["y"]:.2f}" text-anchor="{anchor}" style="{st}">{s.replace("&", "&amp;")}</text></svg>')
        f = work / 'line.svg'; f.write_text(svg, encoding='utf8'); render(f, work / 'line.png')
        A = np.array(Image.open(work / 'line.png').convert('L')) < 128
        ys, xs = np.nonzero(A)
        bx0, bx1, by0, by1 = xs.min(), xs.max(), ys.min(), ys.max()
        k = (y1 - y0) / max(1, by1 - by0)
        if r == 0:
            p['size'] *= k; p['y'] = y1 - (y1 - p['y']) * k if False else p['y']
        # width: letter-spacing after the size is right
        n = max(1, len(s) - 1)
        if r > 0:
            p['ls'] = p.get('ls', 0) + ((x1 - x0) - (bx1 - bx0)) / n * 0.8
        # position: bottom of ink and centre (or left edge)
        p['y'] += y1 - by1
        if anchor == 'middle':
            p['x'] += (x0 + x1) / 2 - (bx0 + bx1) / 2
        else:
            p['x'] += x0 - bx0
        params[i] = {kk: round(float(v), 2) for kk, v in p.items()}
        print(r, i, 'box', (int(bx0), int(bx1), int(by0), int(by1)), 'target', (x0, x1, y0, y1), 'k', round(k, 3))
    b.PARAMS.write_text(json.dumps(params, indent=1), encoding='utf8')
