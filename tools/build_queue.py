"""Build queue.md from the PNG search-results list in data_lake/.

Every .png named in the list (whole or cut off by "...") is resolved to a real
Commons file: exact titles are checked in batches, and fragments are looked up
with a Commons title search. Run from the repo root: python tools/build_queue.py
"""
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

SRC = Path('data_lake/wikipedia-png-search-results.txt')
CACHE = Path('tools/.queue_cache.json')
OUT = Path('queue.md')
API = 'https://commons.wikimedia.org/w/api.php'
UA = 'agentic-vectorization/0.1 (emma@topazcomputing.com)'


def api(**params):
    params.update(format='json', formatversion=2)
    req = urllib.request.Request(API + '?' + urllib.parse.urlencode(params), headers={'User-Agent': UA})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception:
            time.sleep(2 ** attempt)
    raise RuntimeError(params)


def parse():
    """Return {candidate: (is_fragment, set(articles))}."""
    text = SRC.read_text(encoding='utf8').split('\n')
    end = next(i for i, l in enumerate(text) if l.startswith('Replace ".png"'))
    found, article = {}, None
    for line in text[1:end]:
        if line.startswith('\t'):
            article = line.strip()
            continue
        for k, seg in enumerate(line.split('...')):
            seg = seg.replace('↵', '\n')
            for m in re.finditer(r'(?:(File|Image)\s*:\s*)?([^\[\]|=\n{}:<>"]*?\.png)\b', seg, re.I):
                name = m.group(2).replace('_', ' ').strip(" '*#")
                if not name or name.lower() == '.png':
                    continue
                # a name is whole if File: precedes it, or it starts a param value / the segment
                frag = not m.group(1) and (k > 0 and m.start() == 0)
                if '/' in name:          # thumbnail paths like .../20px-Foo.svg.png
                    continue
                key = (name, frag)
                found.setdefault(key, set()).add(article)
    # titles listed in the trailing "Replace .png" block are files too
    for line in text[end:]:
        m = re.match(r'\s*File:(.+\.png)$', line)
        if m:
            found.setdefault((m.group(1).strip(), False), set()).add('(file-title list)')
    return found


def resolve(found, cache):
    exact = sorted({n for (n, frag) in found if not frag and n not in cache})
    for i in range(0, len(exact), 50):
        batch = exact[i:i + 50]
        r = api(action='query', titles='|'.join('File:' + n for n in batch), redirects=1)
        norm = {x['from']: x['to'] for x in r['query'].get('normalized', [])}
        redir = {x['from']: x['to'] for x in r['query'].get('redirects', [])}
        pages = {p['title']: p for p in r['query']['pages']}
        for n in batch:
            t = norm.get('File:' + n, 'File:' + n)
            t = redir.get(t, t)
            p = pages.get(t, {})
            cache[n] = t[5:] if p and not p.get('missing') and p.get('ns') == 6 else None
        time.sleep(0.5)
    # unresolved whole names and fragments: title search, keep a hit that ends with the fragment
    todo = sorted({n for (n, frag) in found if cache.get(n) is None and ('?' + n) not in cache})
    for n in todo:
        stem = n[:-4]
        words = re.findall(r'\w+', stem)[-4:]
        hits = []
        if words:
            r = api(action='query', list='search', srnamespace=6, srlimit=20,
                    srsearch=' '.join(f'intitle:{w}' for w in words) + ' filetype:bitmap')
            hits = [h['title'][5:] for h in r['query']['search']]
        match = [h for h in hits if h.replace('_', ' ').lower().endswith(n.lower())]
        cache['?' + n] = match[0] if len(match) == 1 else (match or None)
        time.sleep(0.3)
    return cache


def main():
    found = parse()
    cache = json.loads(CACHE.read_text(encoding='utf8')) if CACHE.exists() else {}
    cache = resolve(found, cache)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=0), encoding='utf8')

    files, unresolved = {}, {}
    for (n, frag), arts in found.items():
        hit = cache.get(n) or cache.get('?' + n)
        if isinstance(hit, str):
            files.setdefault(hit, set()).update(arts)
        else:
            unresolved.setdefault(n, (hit, set()))[1].update(arts)

    lines = ['# Queue', '',
             'PNG files from `data_lake/wikipedia-png-search-results.txt`, resolved against',
             'Commons by `tools/build_queue.py`. One line per file; delete a line when the file',
             'is done (record it in devlog.md). Prefer rebuilding from a vector source over tracing.', '',
             f'## To vectorize ({len(files)})', '']
    for f in sorted(files, key=str.lower):
        arts = ', '.join(sorted(a for a in files[f] if a))
        lines.append(f'- [ ] [File:{f}](https://commons.wikimedia.org/wiki/File:{urllib.parse.quote(f.replace(" ", "_"))}) — {arts}')
    lines += ['', f'## Unresolved names ({len(unresolved)})', '',
              'Cut off in the list and not matched uniquely on Commons. NEEDS-INVESTIGATION.', '']
    for n in sorted(unresolved, key=str.lower):
        hit, arts = unresolved[n]
        cands = f' — candidates: {"; ".join(hit)}' if isinstance(hit, list) else ''
        lines.append(f'- `{n}` ({", ".join(sorted(a for a in arts if a))}){cands}')
    OUT.write_text('\n'.join(lines) + '\n', encoding='utf8')
    print(len(files), 'files queued;', len(unresolved), 'unresolved')


if __name__ == '__main__':
    main()
