"""Build every coat of arms listed in files/arms/arms.json with Emma's generator (read-only) and
compare each with the raster it replaces. Writes files/arms/<slug>/<slug>.svg, a comparison picture
per file into the screenshots folder, a contact sheet of all of them, and files/arms/results.tsv.
Usage (repo root): python tools/build_arms.py [slug ...]
"""
import json, re, subprocess, sys, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).parent))
from generator_render import build, generator_commit  # noqa: E402

PNG = Path('data_lake/downloads/order-life-arms/png')
SHOTS = Path(r'C:\Users\Emma\Documents\claude-screenshots\agentic-vectorization_2026-10-15')


def licences(files):
    """Commons licence of each reused source file."""
    if not files:
        return {}
    q = urllib.parse.urlencode({'action': 'query', 'titles': '|'.join(files), 'prop': 'imageinfo',
                                'iiprop': 'extmetadata', 'format': 'json', 'formatversion': 2})
    req = urllib.request.Request('https://commons.wikimedia.org/w/api.php?' + q,
                                 headers={'User-Agent': 'agentic-vectorization/0.1 (emma@topazcomputing.com)'})
    with urllib.request.urlopen(req, timeout=60) as r:
        pages = json.load(r)['query']['pages']
    out = {}
    for p in pages:
        md = (p.get('imageinfo') or [{}])[0].get('extmetadata', {})
        out[p['title']] = md.get('LicenseShortName', {}).get('value', '?') + ', by ' + re.sub(r'<[^>]+>', '', md.get('Artist', {}).get('value', '?')).strip()
    return out


def notes_md(slug, s, full, sources, gaps, agree, iou, commit):
    lic = licences(sources)
    src = '\n'.join(f'- [[:{f}]] ({lic.get(f, "?")})' for f in sources) or '- none (geometry drawn by the generator)'
    gap = '\n'.join(f'- {c}: {d}' for c, d in gaps) or '- none'
    return f"""# {slug}

Replaces (as a vector drawing of the same arms): [[:File:{s['png']}]]

Blazon used: **{s['blazon']}** (fully parsed: {full})

Built with Emma's Sodacan-arms-svg-generator at commit {commit}, imported read-only by
`tools/generator_render.py`; the shield and drawings are in Sodacan's Commons style, not the PNG
artist's. Status: **{s.get('status', 'unchecked')}**. {s.get('note', '')}

Check against the PNG (`tools/arms_compare.py`): tincture agreement {agree}, silhouette IoU {iou}
(the silhouette differs because Sodacan's heater shield is a different shape).

Drawings reused from Commons (licence and author; the SVG inherits share-alike where these are CC BY-SA):
{src}

What the generator could not draw:
{gap}
"""


def main():
    spec = json.loads(Path('files/arms/arms.json').read_text(encoding='utf-8'))
    slugs = sys.argv[1:] or list(spec)
    rows, pics = [], []
    commit = generator_commit()
    for slug in slugs:
        s = spec[slug]
        svg, full, sources, gaps = build(s['blazon'], detail=True)
        d = Path('files/arms') / slug
        d.mkdir(parents=True, exist_ok=True)
        (d / f'{slug}.svg').write_text(svg, encoding='utf-8')
        pic = SHOTS / f'cmp_{slug}.png'
        cmd = [sys.executable, 'tools/arms_compare.py', str(PNG / re.sub(r'[\/:*?"<>|]', '_', s['png'])), str(d / f'{slug}.svg'), str(pic)]
        if s.get('box'):
            cmd += ['--box', s['box']]
        out = subprocess.run(cmd, capture_output=True, text=True).stdout.split()
        agree, iou = out[2], out[5]
        rows.append((slug, s['png'], s['blazon'], full, agree, iou, s.get('status', ''), '; '.join(f'{c}: {g}' for c, g in gaps)))
        (d / 'notes.md').write_text(notes_md(slug, s, full, sources, gaps, agree, iou, commit), encoding='utf-8')
        if s.get('status') == 'accepted':
            up = Path('upload') / f'arms-{slug}'
            up.mkdir(parents=True, exist_ok=True)
            (up / f'{slug}.svg').write_text(svg, encoding='utf-8')
            (up / 'notes.md').write_text((d / 'notes.md').read_text(encoding='utf-8'), encoding='utf-8')
        pics.append(pic)
        print(slug, full, agree, iou, flush=True)
    res = Path('files/arms/results.tsv')
    keep = {}
    if res.exists():  # a partial run updates its rows and keeps the others
        for line in res.read_text(encoding='utf-8').splitlines()[2:]:
            keep[line.split('\t')[0]] = line.split('\t')
    keep.update({r[0]: list(map(str, r)) for r in rows})
    with res.open('w', encoding='utf-8') as f:
        f.write(f'# generator commit {commit}\nslug\tpng\tblazon\tfully_parsed\ttincture_agreement\tsilhouette_iou\tstatus\tgenerator_gaps\n')
        for slug in spec:
            if slug in keep:
                f.write('\t'.join(keep[slug]) + '\n')
    ims = [Image.open(p) for p in pics]
    cols = 4
    w, h = ims[0].size
    sheet = Image.new('RGB', (cols * w, -(-len(ims) // cols) * h), 'white')
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % cols) * w, (i // cols) * h))
    sheet.save(SHOTS / 'arms_sheet.png')


if __name__ == '__main__':
    main()
