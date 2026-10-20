import glob, os, re, json, urllib.request, urllib.parse
UA = {'User-Agent': 'agentic-vectorization/0.1 (emma@topazcomputing.com)'}
items = {}
for d in sorted(glob.glob('upload/*/')):
    n = os.path.join(d, 'notes.md')
    t = open(n, encoding='utf8').read() if os.path.exists(n) else ''
    m = re.search(r'File:([^\]\n]+?\.(?:png|jpg|jpeg|gif|PNG|JPG))', t)
    items[os.path.basename(os.path.normpath(d))] = m.group(1).strip() if m else None
names = sorted({v for v in items.values() if v})
lic = {}
for i in range(0, len(names), 40):
    q = urllib.parse.urlencode({'action': 'query', 'titles': '|'.join('File:' + x for x in names[i:i + 40]),
                                'prop': 'templates|imageinfo', 'iiprop': 'extmetadata', 'tllimit': 'max',
                                'format': 'json', 'formatversion': 2})
    d = json.load(urllib.request.urlopen(urllib.request.Request('https://commons.wikimedia.org/w/api.php?' + q, headers=UA)))
    norm = {x['to']: x['from'] for x in d['query'].get('normalized', [])}
    for p in d['query']['pages']:
        md = (p.get('imageinfo') or [{}])[0].get('extmetadata', {})
        lic[p['title'][5:]] = (md.get('LicenseShortName', {}).get('value'),
                               md.get('License', {}).get('value'),
                               [t['title'] for t in p.get('templates', []) if re.search(r'GFDL|Cc-|CC-|PD|License migration|Self', t['title'])][:12])
json.dump({'items': items, 'lic': lic}, open('scratch/lic.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)
print(len(items), 'items;', sum(1 for v in items.values() if not v), 'without a source name')
for k, v in items.items():
    if not v:
        print('  no source:', k)
