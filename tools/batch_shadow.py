"""Rebuild every queued "Shadow picture of X prefecture.png" from Natural Earth.

For each: download the PNG and its description, write the Natural Earth source SVG,
fit with tools/rebuild_flagmap.py (solid fill), render a comparison, and record IoU.
Results at or above --min-iou go to files/shadow-<x>/ and upload/shadow-<x>/; the rest
stay in scratch/shadow/ for investigation. Writes tools/batch_shadow.json.
PNGs larger than --max-size px are left for a more detailed source.
usage: python tools/batch_shadow.py [--min-iou 0.93] [--max-size 500] [names...]
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from ne_prefecture_svg import prefecture_svg  # noqa: E402
from render_svg import render  # noqa: E402

UA = 'agentic-vectorization/0.1 (emma@topazcomputing.com)'
OUT = Path('tools/batch_shadow.json')


def fetch(url, dest):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    Path(dest).write_bytes(urllib.request.urlopen(req, timeout=60).read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--min-iou', type=float, default=0.93)
    ap.add_argument('--max-size', type=int, default=500)
    ap.add_argument('names', nargs='*')
    a = ap.parse_args()
    queue = Path('queue.md').read_text(encoding='utf8').split('## Already')[0]
    names = a.names or re.findall(r'^- \[File:Shadow picture of (.+?) prefecture\.png\]', queue, re.M)
    results = json.loads(OUT.read_text(encoding='utf8')) if OUT.exists() else {}
    for name in names:
        slug = 'shadow-' + name.lower().replace(' ', '-')
        png_name = f'Shadow picture of {name} prefecture.png'
        dl = Path('data_lake/downloads') / slug
        dl.mkdir(parents=True, exist_ok=True)
        png = dl / png_name
        if not png.exists():
            fetch('https://commons.wikimedia.org/wiki/Special:FilePath/' + urllib.parse.quote(png_name.replace(' ', '_')), png)
            desc = Path('data_lake/downloads/descriptions') / (png_name + '.wikitext')
            if desc.exists():
                shutil.copy(desc, dl / 'description.wikitext')
        work = Path('scratch/shadow') / slug
        work.mkdir(parents=True, exist_ok=True)
        try:
            src = work / 'natural-earth.svg'
            prefecture_svg(name, src)
        except StopIteration:
            results[name] = dict(status='no Natural Earth match')
            print(name, 'no Natural Earth match', flush=True)
            continue
        colour = Image.open(png).convert('RGBA')
        px = np.array(colour)
        opaque = px[..., 3] > 200
        fill = '#%02x%02x%02x' % tuple(int(v) for v in np.median(px[opaque][:, :3], 0))
        out_svg = work / png_name.replace('.png', '.svg')
        r = subprocess.run([sys.executable, 'tools/rebuild_flagmap.py', str(png), str(src), 'pref', fill, str(out_svg)],
                           capture_output=True, text=True)
        try:
            rep = json.loads(r.stdout)
        except json.JSONDecodeError:
            results[name] = dict(status='error', stderr=r.stderr[-400:])
            print(name, 'error', flush=True)
            continue
        # comparison image
        render(out_svg, work / 'render.png')
        A = px[..., 3] > 128
        B = np.array(Image.open(work / 'render.png').convert('RGBA'))[..., 3] > 128
        iou = float((A & B).sum() / (A | B).sum())
        o = np.full(A.shape + (3,), 255, np.uint8); o[A & ~B] = [255, 0, 0]; o[B & ~A] = [0, 0, 255]; o[A & B] = 0
        Image.fromarray(o).save(work / 'diff.png')
        big = max(px.shape[:2]) > a.max_size  # Natural Earth 1:10M is too coarse for big PNGs
        ok = iou >= a.min_iou and not big
        status = 'done' if ok else ('needs-detailed-source' if big else 'below-threshold')
        results[name] = dict(status=status, size=list(px.shape[1::-1]), iou=round(iou, 4), fill=fill,
                             y_over_x=rep.get('y_over_x_scale'), outline=rep.get('outline'))
        if ok:
            for dest in (Path('files') / slug, Path('upload') / slug):
                dest.mkdir(parents=True, exist_ok=True)
                shutil.copy(out_svg, dest / out_svg.name)
            (Path('files') / slug / 'rebuild-report.json').write_text(json.dumps(results[name], indent=1), encoding='utf8')
        print(name, results[name], flush=True)
        OUT.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding='utf8')


if __name__ == '__main__':
    main()
