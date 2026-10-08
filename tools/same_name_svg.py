"""For every file in queue.md, check whether Commons has an SVG of the same name
(Foo.png -> Foo.svg). Writes tools/same_name_svg.json {png: svg title or null}.
Run from the repo root: python tools/same_name_svg.py
"""
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

API = 'https://commons.wikimedia.org/w/api.php'
UA = 'agentic-vectorization/0.1 (emma@topazcomputing.com)'
OUT = Path('tools/same_name_svg.json')


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
    names = re.findall(r'^- \[File:(.+?)\]\(', Path('queue.md').read_text(encoding='utf8'), re.M)
    res = {}
    for i in range(0, len(names), 50):
        batch = names[i:i + 50]
        svgs = {n: 'File:' + n[:-4] + '.svg' for n in batch}
        r = api(action='query', titles='|'.join(svgs.values()), redirects=1)
        norm = {x['from']: x['to'] for x in r['query'].get('normalized', [])}
        redir = {x['from']: x['to'] for x in r['query'].get('redirects', [])}
        pages = {p['title']: p for p in r['query']['pages']}
        for n, t in svgs.items():
            t = norm.get(t, t)
            t = redir.get(t, t)
            p = pages.get(t, {})
            res[n] = t if p and not p.get('missing') else None
        time.sleep(0.5)
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=0), encoding='utf8')
    hits = {k: v for k, v in res.items() if v}
    print(len(hits), 'of', len(res), 'have a same-name SVG')


if __name__ == '__main__':
    main()
