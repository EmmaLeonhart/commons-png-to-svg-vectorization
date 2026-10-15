"""Per order.life person with arms on Wikidata (P94): where their SVG coat of arms is.

Writes files/arms/person_arms_status.tsv with one of:
  svg            the Wikidata image is already an SVG
  vector-exists  Commons has a vector version of the raster image (named)
  rebuilt        rebuilt here; SVG staged under upload/ (path given)
  generator-gap  blazon known, waiting on the arms generator (files/arms/generator-gaps.md)
  raster-original  a seal, manuscript painting, carving or photo: not vectorized
  todo           not worked yet
Classification of raster files comes from files/arms/arms.json, the rebuilt kamon folders and
files/arms/raster_status.json. Run from the repo root."""
import csv, json, re
from pathlib import Path

rows = list(csv.DictReader(open('data_lake/downloads/order-life-arms/person_arms.tsv', encoding='utf-8'), delimiter='\t'))
triage = json.loads(Path('data_lake/downloads/order-life-arms/arms_triage.json').read_text(encoding='utf-8'))
spec = json.loads(Path('files/arms/arms.json').read_text(encoding='utf-8'))
manual = json.loads(Path('files/arms/raster_status.json').read_text(encoding='utf-8'))
by_png = {}
for slug, s in spec.items():
    if s.get('status') == 'accepted':
        by_png[s['png']] = ('rebuilt', f'upload/arms-{slug}/{slug}.svg')
    elif s.get('status') == 'generator-gap':
        by_png[s['png']] = ('generator-gap', slug)
for up in Path('upload').iterdir():  # rebuilt kamon etc.: notes.md names the PNG
    n = up / 'notes.md'
    if n.exists():
        m = re.match(r'# File:(.+?) → SVG', n.read_text(encoding='utf-8'))
        svgs = list(up.glob('*.svg'))
        if m and svgs:
            by_png.setdefault(m.group(1), ('rebuilt', svgs[0].as_posix()))
out = []
for r in rows:
    f = r['file']
    if r['ext'] == 'svg':
        st = ('svg', f)
    elif f in by_png:
        st = by_png[f]
    elif f in manual:
        st = tuple(manual[f])
    elif triage.get(f, {}).get('same_name_svg') or triage.get(f, {}).get('vector_version'):
        t = triage[f]
        st = ('vector-exists', t['same_name_svg'] or t['vector_version'][0])
    else:
        st = ('todo', '')
    out.append([r['qid'], r['label'], r['wikidata_qid'], f, *st])
with open('files/arms/person_arms_status.tsv', 'w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh, delimiter='\t')
    w.writerow(['qid', 'label', 'wikidata_qid', 'wikidata_image', 'status', 'detail'])
    w.writerows(out)
from collections import Counter
print(Counter(o[4] for o in out))
