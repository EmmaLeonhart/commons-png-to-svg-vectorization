import json, re, urllib.request, urllib.parse, html
UA = {'User-Agent': 'agentic-vectorization/0.1 (emma@topazcomputing.com)'}
d = json.load(open('scratch/lic.json', encoding='utf8'))
names = sorted(set(d['items'].values()))
art = {}
for i in range(0, len(names), 40):
    q = urllib.parse.urlencode({'action': 'query', 'titles': '|'.join('File:' + x for x in names[i:i + 40]),
                                'prop': 'imageinfo', 'iiprop': 'extmetadata', 'format': 'json', 'formatversion': 2})
    r = json.load(urllib.request.urlopen(urllib.request.Request('https://commons.wikimedia.org/w/api.php?' + q, headers=UA)))
    for p in r['query']['pages']:
        md = (p.get('imageinfo') or [{}])[0].get('extmetadata', {})
        a = md.get('Artist', {}).get('value', '')
        a = html.unescape(re.sub(r'<[^>]+>', '', a)).strip()
        art[p['title'][5:]] = re.sub(r'\s+', ' ', a)[:200]
d['artist'] = art
json.dump(d, open('scratch/lic.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)
print(sum(1 for v in art.values() if v), 'with an artist of', len(art))
