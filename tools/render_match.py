"""For queued PNGs whose description links SVGs (tools/triage.json), render each linked SVG at
the PNG's size and compare. A near-identical render means the PNG is just a rasterisation
of an existing SVG, so a vector version already exists. Writes tools/render_match.json.
Run from the repo root: python tools/render_match.py [--max-diff 6]
"""
import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from render_svg import render  # noqa: E402

UA = 'agentic-vectorization/0.1 (emma@topazcomputing.com)'
WORK = Path('scratch/render_match')
OUT = Path('tools/render_match.json')


def fetch(name, dest):
    if dest.exists():
        return
    url = 'https://commons.wikimedia.org/wiki/Special:FilePath/' + urllib.parse.quote(name.replace(' ', '_'))
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    dest.write_bytes(urllib.request.urlopen(req, timeout=60).read())
    time.sleep(0.3)


def on_white(im):
    im = im.convert('RGBA')
    bg = Image.new('RGBA', im.size, 'white')
    bg.alpha_composite(im)
    return np.array(bg.convert('RGB')).astype(int)


def aligned_diff(A, svg_path, work):
    """Mean difference after fitting scale and offset (renders can be framed slightly differently).
    Memory-bounded: the SVG is rendered at about twice the PNG's size and compared on a grid of
    at most ~300 px across, in float32 (an unbounded first version ran a machine out of memory)."""
    import itertools
    H, W = A.shape[:2]
    head = svg_path.read_text(encoding='utf8', errors='replace')[:3000]
    m = re.search(r'<svg[^>]*?\swidth="([\d.]+)', head)
    native_w = float(m.group(1)) if m else W
    big = work / (svg_path.stem + '.render2x.png')
    render(svg_path, big, min(4.0, max(0.05, 2 * W / native_w)))
    B = on_white(Image.open(big)).astype(np.float32)
    bh, bw = B.shape[:2]
    st = max(1, max(H, W) // 300)
    vv, uu = np.mgrid[0:H:st, 0:W:st]
    At = A[vv, uu].astype(np.float32)

    def score(sc, ox, oy):
        x = ((uu - ox) / sc).astype(np.int32).clip(0, bw - 1); y = ((vv - oy) / sc).astype(np.int32).clip(0, bh - 1)
        return float(np.abs(At - B[y, x]).mean())
    s0 = W / bw
    best = (score(s0, 0, 0), s0, 0.0, 0.0)
    for it in range(5):
        f = 2 ** it
        for ds, dx, dy in itertools.product(np.linspace(-.04, .04, 9) * best[1] / f, np.linspace(-6, 6, 9) / f, np.linspace(-6, 6, 9) / f):
            sc = score(best[1] + ds, best[2] + dx, best[3] + dy)
            if sc < best[0]:
                best = (sc, best[1] + ds, best[2] + dx, best[3] + dy)
    return best[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--max-diff', type=float, default=6.0)
    a = ap.parse_args()
    tri = json.loads(Path('tools/triage.json').read_text(encoding='utf8'))
    queue = Path('queue.md').read_text(encoding='utf8').split('## Already')[0]
    names = [n for n in re.findall(r'^- \[File:(.+?)\]\(', queue, re.M) if tri.get(n, {}).get('svg')]
    res = json.loads(OUT.read_text(encoding='utf8')) if OUT.exists() else {}
    WORK.mkdir(parents=True, exist_ok=True)
    for n in names:
        if n in res:
            continue
        safe = re.sub(r'[<>:"/\\|?*]', '_', n)[:80]
        png = WORK / safe
        try:
            fetch(n, png)
            A = on_white(Image.open(png))
        except Exception as e:
            res[n] = dict(error=str(e)[:200]); continue
        best = None
        for svg_name in dict.fromkeys(s.replace('_', ' ').strip() for s in tri[n]['svg']):
            sp = WORK / (re.sub(r'[<>:"/\\|?*]', '_', svg_name)[:80])
            try:
                fetch(svg_name, sp)
                if not sp.read_bytes()[:400].lstrip().startswith((b'<?xml', b'<svg', b'\xef\xbb\xbf<')):
                    continue
                out = WORK / (sp.stem + '.render.png')
                render(sp, out)
                B = on_white(Image.open(out).resize((A.shape[1], A.shape[0]), Image.LANCZOS))
                diff = float(np.abs(A - B).mean())
            except Exception as e:
                diff = None
            if diff is not None and (best is None or diff < best[1]):
                best = (svg_name, diff)
        if best and a.max_diff < best[1] < 30:  # maybe the same art framed differently
            sp = WORK / (re.sub(r'[<>:"/\|?*]', '_', best[0])[:80])
            best = (best[0], min(best[1], aligned_diff(A, sp, WORK)))
        res[n] = dict(svg=best[0], diff=round(best[1], 2), match=best[1] <= a.max_diff) if best else dict(error='no renderable svg')
        print(n, res[n], flush=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding='utf8')
    print(sum(1 for v in res.values() if v.get('match')), 'matches of', len(res))


if __name__ == '__main__':
    main()
