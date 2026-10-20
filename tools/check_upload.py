"""Check everything staged in upload/ before it is uploaded: each folder has an SVG and a notes.md, every SVG parses
as XML and renders (resvg) to something non-blank, and no file contains stray control characters.
usage (repo root): python tools/check_upload.py"""
import glob, io, os, re, subprocess, sys
import xml.dom.minidom as md
import numpy as np, resvg_py
from PIL import Image

RENDER = ('import sys, io, numpy as np, resvg_py; from PIL import Image; '
          'raw = open(sys.argv[1], encoding="utf8").read(); '
          'a = np.array(Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=raw, width=200)))).convert("RGBA")); '
          'print("blank" if a[..., 3].max() == 0 else "ok")')
CTRL = re.compile(rb'[\x00-\x08\x0b\x0c\x0e-\x1f]')
probs, n = [], 0
for d in sorted(glob.glob('upload/*/')):
    svgs = glob.glob(d + '*.svg')
    if not svgs:
        if glob.glob(d + '*'):
            print('(no SVG, left alone):', d)
        continue
    if not os.path.exists(d + 'notes.md'):
        probs.append((d, 'no notes.md'))
    elif CTRL.search(open(d + 'notes.md', 'rb').read()):
        probs.append((d, 'control character in notes.md'))
    for s in svgs:
        n += 1
        if os.environ.get("TRACE"): print(s, flush=True)
        raw = open(s, 'rb').read()
        if CTRL.search(raw):
            probs.append((s, 'control character'))
        try:
            md.parseString(raw)
        except Exception as e:
            probs.append((s, 'XML: ' + str(e)[:80]))
            continue
        # render in a child process: resvg can crash outright (stack overflow) on very large files; fall back to
        # Chrome (tools/render_svg.py) for those
        r = subprocess.run([sys.executable, '-X', 'utf8', '-c', RENDER, s], capture_output=True, text=True)
        if r.returncode != 0:
            png = 'scratch/check_upload.png'
            subprocess.run([sys.executable, '-X', 'utf8', 'tools/render_svg.py', s, png, '0.25'], capture_output=True)
            ok = os.path.exists(png) and np.array(Image.open(png).convert('RGBA'))[..., 3].max() > 0
            if os.path.exists(png):
                os.remove(png)
            if not ok:
                probs.append((s, 'does not render (resvg crashed, Chrome blank)'))
            else:
                print('(resvg crashed, Chrome renders it):', s)
        elif r.stdout.strip() == 'blank' and 'null' not in s.lower():
            probs.append((s, 'renders blank'))
print(n, 'SVGs checked,', len(probs), 'problems')
for p in probs:
    print(' ', *p)
