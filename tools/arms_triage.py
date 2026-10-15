"""Triage the raster coats of arms of order.life people (from tools/person_arms.py).

For each distinct PNG/GIF file: does Commons already have a vector version (same-name SVG,
{{Vector version available}}, an .svg under other versions), and does its description give a
blazon ({{COAInformation}} or a 'blazon' line)? Saves each page's wikitext under
data_lake/downloads/descriptions/ and writes data_lake/downloads/order-life-arms/arms_triage.json.
Run from the repo root: python tools/arms_triage.py
"""
import csv, json, re, time, urllib.parse, urllib.request
from pathlib import Path

API = 'https://commons.wikimedia.org/w/api.php'
UA = 'agentic-vectorization/0.1 (emma@topazcomputing.com)'
DIR = Path('data_lake/downloads/order-life-arms')
DESC = Path('data_lake/downloads/descriptions')


def api(**params):
    params.update(format='json', formatversion=2)
    req = urllib.request.Request(API, data=urllib.parse.urlencode(params).encode(), headers={'User-Agent': UA})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception:
            time.sleep(2 ** attempt)
    raise RuntimeError(params)


def main():
    rows = list(csv.DictReader((DIR / 'person_arms.tsv').open(encoding='utf-8'), delimiter='\t'))
    people = {}
    for r in rows:
        if r['ext'] in ('png', 'gif'):
            people.setdefault(r['file'], []).append(f"{r['qid']} {r['label']}")
    names = sorted(people)
    out = {}
    for i in range(0, len(names), 20):
        chunk = names[i:i + 20]
        titles = ['File:' + n for n in chunk] + ['File:' + n.rsplit('.', 1)[0] + '.svg' for n in chunk]
        res = api(action='query', titles='|'.join(titles), prop='revisions|imageinfo',
                  rvprop='content', rvslots='main', iiprop='size|url')
        pages = {p['title']: p for p in res['query']['pages']}
        norm = {n['from']: n['to'] for n in res['query'].get('normalized', [])}
        for n in chunk:
            p = pages.get(norm.get('File:' + n, 'File:' + n), {})
            svgt = 'File:' + n.rsplit('.', 1)[0] + '.svg'
            same = pages.get(norm.get(svgt, svgt), {})
            text = p.get('revisions', [{}])[0].get('slots', {}).get('main', {}).get('content', '')
            DESC.mkdir(parents=True, exist_ok=True)
            (DESC / (re.sub(r'[\/:*?"<>|]', '_', n) + '.wikitext')).write_text(text, encoding='utf-8')
            vec = re.findall(r'\{\{\s*(?:vector version available|vva|SupersededSVG|superseded)\s*\|\s*([^}|]+)', text, re.I)
            other = re.findall(r'([^\[\]|=\n]+\.svg)', text, re.I)
            blazon = re.findall(r'blazon\w*\s*=\s*([^\n|]{8,})', text, re.I)
            ii = p.get('imageinfo', [{}])[0]
            out[n] = {
                'people': people[n],
                'missing': 'missing' in p,
                'size': [ii.get('width'), ii.get('height')],
                'same_name_svg': None if 'missing' in same or not same else same['title'],
                'vector_version': [v.strip() for v in vec],
                'svg_mentions': sorted({o.strip() for o in other})[:10],
                'blazon': [b.strip() for b in blazon],
                'coainfo': '{{coainformation' in text.lower(),
            }
        print(i, flush=True)
    (DIR / 'arms_triage.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')


if __name__ == '__main__':
    main()
