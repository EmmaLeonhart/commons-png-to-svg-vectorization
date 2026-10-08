"""Sort the remaining queue by how the image looks: fetch a 300 px thumbnail of every file still to
vectorize and measure its colour complexity. Photos, paintings and screenshots have thousands of
distinct colours; flat graphics (maps, diagrams, flags, logos) have few. Writes
tools/visual_triage.json and saves thumbnails under scratch/thumbs/. Memory-light: one image at a time.
Run from the repo root: python tools/visual_triage.py
"""
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image

UA = 'agentic-vectorization/0.1 (emma@topazcomputing.com)'
OUT = Path('tools/visual_triage.json')
THUMBS = Path('scratch/thumbs')


def thumb(name):
    p = THUMBS / (re.sub(r'[<>:"/\\|?*]', '_', name)[:90] + '.png')
    if not p.exists():
        url = 'https://commons.wikimedia.org/wiki/Special:FilePath/' + urllib.parse.quote(name.replace(' ', '_')) + '?width=300'
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        p.write_bytes(urllib.request.urlopen(req, timeout=60).read())
        time.sleep(0.2)
    return p


def measure(p):
    im = Image.open(p).convert('RGBA')
    a = np.array(im)
    opaque = a[..., 3] > 0
    rgb = a[..., :3][opaque]
    if len(rgb) == 0:
        return dict(colours=0, top8=1.0)
    q = (rgb // 8).astype(np.int32)
    keys = q[:, 0] * 1024 + q[:, 1] * 32 + q[:, 2]
    _, counts = np.unique(keys, return_counts=True)
    counts = np.sort(counts)[::-1]
    return dict(colours=int(len(counts)), top8=round(float(counts[:8].sum() / counts.sum()), 3))


def main():
    THUMBS.mkdir(parents=True, exist_ok=True)
    queue = Path('queue.md').read_text(encoding='utf8').split('## Already')[0]
    lines = [l for l in queue.split('\n') if l.startswith('- [File:')]
    res = json.loads(OUT.read_text(encoding='utf8')) if OUT.exists() else {}
    for l in lines:
        n = re.match(r'- \[File:(.+?)\]\(', l).group(1)
        if n in res:
            continue
        try:
            m = measure(thumb(n))
        except Exception as e:
            res[n] = dict(error=str(e)[:120]); continue
        # top8: share of pixels in the 8 commonest colours; flat graphics are dominated by a few
        m['kind'] = 'flat' if m['top8'] >= 0.85 else ('mixed' if m['top8'] >= 0.6 else 'photo-like')
        res[n] = m
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=0), encoding='utf8')
    from collections import Counter
    print(Counter(v.get('kind', 'error') for v in res.values()))


if __name__ == '__main__':
    main()
