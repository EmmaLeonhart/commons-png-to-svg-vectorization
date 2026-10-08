"""Fetch description wikitext + file info for every file in queue.md and sort them
by how they can be vectorized. Writes data_lake/downloads/descriptions/<name>.wikitext,
tools/triage.json and triage.md. Run from the repo root: python tools/triage.py
"""
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

API = 'https://commons.wikimedia.org/w/api.php'
UA = 'agentic-vectorization/0.1 (emma@topazcomputing.com)'
DESC = Path('data_lake/downloads/descriptions')
OUT_JSON = Path('tools/triage.json')
OUT_MD = Path('triage.md')


def api(**params):
    params.update(format='json', formatversion=2)
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(API, data=data, headers={'User-Agent': UA})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception:
            time.sleep(2 ** attempt)
    raise RuntimeError(params)


def safe(name):
    s = re.sub(r'[<>:"/\\|?*]', '_', name)
    if len(s) > 100:  # stay under Windows' path limit
        import hashlib
        s = s[:90] + '~' + hashlib.sha1(name.encode()).hexdigest()[:8]
    return s


def classify(text, cats, info):
    t = text.lower()
    svg_links = sorted(set(re.findall(r'(?:file|image):\s*([^\]\|\n}]+?\.svg)', text, re.I)))
    if re.search(r'\{\{\s*(vector version available|vva|superseded|svg available)', t):
        return 'has-svg-already', svg_links
    if svg_links:
        return 'svg-source-linked', svg_links
    if re.search(r'\{\{\s*(convert to svg|should be svg|svg-logo)', t):
        return 'tagged-convert-to-svg', []
    photoish = any(k in t for k in ('{{photo', 'photograph', 'ukiyo-e', 'painting', 'woodblock', 'scan'))
    catsl = ' '.join(cats).lower()
    if photoish or any(k in catsl for k in ('photograph', 'paintings', 'ukiyo-e', 'woodblock prints')):
        return 'photo-or-artwork', []
    if any(k in catsl or k in t for k in ('map', 'diagram', 'chart', 'logo', 'flag', 'coat of arms', 'icon', 'family tree', 'genealog', 'symbol', 'kamon', 'crest')):
        return 'diagram-like-no-source', []
    return 'unclear', []


def main():
    names = re.findall(r'^- \[File:(.+?)\]\(', Path('queue.md').read_text(encoding='utf8'), re.M)
    DESC.mkdir(parents=True, exist_ok=True)
    res = json.loads(OUT_JSON.read_text(encoding='utf8')) if OUT_JSON.exists() else {}
    todo = [n for n in names if n not in res]
    for i in range(0, len(todo), 50):
        batch = todo[i:i + 50]
        r = api(action='query', titles='|'.join('File:' + n for n in batch), prop='revisions|imageinfo|categories',
                rvprop='content', rvslots='main', iiprop='size|mime|url', cllimit='max', redirects=1)
        norm = {x['from']: x['to'] for x in r['query'].get('normalized', [])}
        redir = {x['from']: x['to'] for x in r['query'].get('redirects', [])}
        pages = {p['title']: p for p in r['query']['pages']}
        for n in batch:
            t = redir.get(norm.get('File:' + n, 'File:' + n), norm.get('File:' + n, 'File:' + n))
            p = pages.get(t, {})
            text = p.get('revisions', [{}])[0].get('slots', {}).get('main', {}).get('content', '') if p.get('revisions') else ''
            ii = (p.get('imageinfo') or [{}])[0]
            cats = [c['title'][9:] for c in p.get('categories', [])]
            (DESC / (safe(n) + '.wikitext')).write_text(text, encoding='utf8')
            kind, links = classify(text, cats, ii)
            res[n] = dict(kind=kind, svg=links, size=ii.get('size'), w=ii.get('width'), h=ii.get('height'),
                          url=ii.get('url'), local_desc=not text and bool(ii))
        OUT_JSON.write_text(json.dumps(res, ensure_ascii=False, indent=0), encoding='utf8')
        print(f'{min(i + 50, len(todo))}/{len(todo)}', flush=True)
        time.sleep(0.5)

    groups = {}
    for n in names:
        groups.setdefault(res[n]['kind'], []).append(n)
    total = sum((res[n]['size'] or 0) for n in names)
    lines = ['# Triage', '', f'{len(names)} queued files, {total / 1e9:.2f} GB of PNG in total. Built by `tools/triage.py`.', '']
    order = ['svg-source-linked', 'tagged-convert-to-svg', 'diagram-like-no-source', 'unclear', 'has-svg-already', 'photo-or-artwork']
    for k in order:
        lines.append(f'- **{k}**: {len(groups.get(k, []))}')
    for k in order:
        lines += ['', f'## {k} ({len(groups.get(k, []))})', '']
        for n in groups.get(k, []):
            extra = f' ← {"; ".join(res[n]["svg"][:3])}' if res[n]['svg'] else ''
            lines.append(f'- File:{n} ({res[n]["w"]}×{res[n]["h"]}){extra}')
    OUT_MD.write_text('\n'.join(lines) + '\n', encoding='utf8')
    print({k: len(v) for k, v in groups.items()}, f'{total / 1e9:.2f} GB')


if __name__ == '__main__':
    main()
