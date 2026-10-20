import json, urllib.request, os, time
UA = {'User-Agent': 'agentic-vectorization/0.1 (emma@topazcomputing.com)'}
d = json.load(open('scratch/tarot_info.json', encoding='utf8'))
for t, v in d.items():
    out = os.path.join('data_lake/downloads/tarot', t[5:])
    if os.path.exists(out) and os.path.getsize(out) == v['size']:
        continue
    for k in range(4):
        try:
            open(out, 'wb').write(urllib.request.urlopen(urllib.request.Request(v['url'], headers=UA), timeout=120).read()); break
        except Exception as e:
            time.sleep(3 * (k + 1))
    time.sleep(0.3)
ok = sum(1 for t, v in d.items() if os.path.exists(os.path.join('data_lake/downloads/tarot', t[5:])) and os.path.getsize(os.path.join('data_lake/downloads/tarot', t[5:])) == v['size'])
print(ok, 'of', len(d), 'downloaded intact')
