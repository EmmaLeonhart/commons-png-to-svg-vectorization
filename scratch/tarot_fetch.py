import json, urllib.request, urllib.parse, os, sys
UA = {'User-Agent': 'agentic-vectorization/0.1 (emma@topazcomputing.com)'}
def api(**kw):
    kw.update(format='json', formatversion=2)
    return json.load(urllib.request.urlopen(urllib.request.Request('https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(kw), headers=UA)))
seen, files, todo = set(), [], ['Category:Vectorized_Tarot_by_Immanuelle']
while todo:
    c = todo.pop()
    if c in seen: continue
    seen.add(c)
    for m in api(action='query', list='categorymembers', cmtitle=c, cmlimit=500)['query']['categorymembers']:
        if m['ns'] == 14: todo.append(m['title'])
        elif m['ns'] == 6: files.append(m['title'])
files = sorted(set(files))
print(len(files), 'files from', len(seen), 'categories')
info = {}
for i in range(0, len(files), 40):
    d = api(action='query', titles='|'.join(files[i:i + 40]), prop='imageinfo', iiprop='url|size|extmetadata')
    for p in d['query']['pages']:
        ii = p['imageinfo'][0]; md = ii.get('extmetadata', {})
        info[p['title']] = dict(url=ii['url'], size=ii['size'], w=ii.get('width'), h=ii.get('height'),
                                lic=md.get('LicenseShortName', {}).get('value'))
json.dump(info, open('scratch/tarot_info.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)
import collections
print(collections.Counter(v['lic'] for v in info.values()))
print('total MB', round(sum(v['size'] for v in info.values()) / 1e6, 1), 'ext', collections.Counter(t.rsplit('.', 1)[-1] for t in info))
