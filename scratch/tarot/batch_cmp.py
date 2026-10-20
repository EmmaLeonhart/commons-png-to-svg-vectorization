import glob, io, os, subprocess, sys
import numpy as np, resvg_py
from PIL import Image
CODE = ('import sys, io, numpy as np, resvg_py; from PIL import Image\n'
        'def r(p): return np.array(Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=open(p, encoding="utf8").read(), width=543)))).convert("RGB")).astype(float)\n'
        'A=r(sys.argv[1]); B=r(sys.argv[2]); mse=((A-B)**2).mean(); d=np.abs(A-B).max(2)\n'
        'print(f"{10*np.log10(255**2/max(mse,1e-9)):.1f} {100*(d>24).mean():.2f} {100*(d>48).mean():.2f}")')
rows = []
for f in sorted(glob.glob('data_lake/downloads/tarot/*.svg')):
    n = os.path.basename(f); o = os.path.join('tarot', n)
    r = subprocess.run([sys.executable, '-X', 'utf8', '-c', CODE, f, o], capture_output=True, text=True)
    s = r.stdout.split() if r.returncode == 0 else ['crash', '-', '-']
    rows.append((n, os.path.getsize(f) / 1e6, os.path.getsize(o) / 1e6, *s))
for row in rows:
    print('%-36s %5.2f -> %5.2f MB  PSNR %s  >24: %s%%  >48: %s%%' % row)
