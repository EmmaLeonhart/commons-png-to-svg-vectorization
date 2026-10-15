"""Download every raster coat of arms in data_lake/downloads/order-life-arms/arms_triage.json
into data_lake/downloads/order-life-arms/png/ (skips files present). Run from the repo root."""
import json, re, time, urllib.parse, urllib.request
from pathlib import Path

DIR = Path('data_lake/downloads/order-life-arms')
UA = 'agentic-vectorization/0.1 (emma@topazcomputing.com)'


def main():
    names = json.loads((DIR / 'arms_triage.json').read_text(encoding='utf-8'))
    (DIR / 'png').mkdir(exist_ok=True)
    for n in names:
        dest = DIR / 'png' / re.sub(r'[\/:*?"<>|]', '_', n)
        if dest.exists():
            continue
        url = 'https://commons.wikimedia.org/wiki/Special:FilePath/' + urllib.parse.quote(n.replace(' ', '_'))
        for attempt in range(5):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=120) as r:
                    dest.write_bytes(r.read())
                break
            except Exception as e:
                print('retry', n, e)
                time.sleep(5 * (attempt + 1))
        time.sleep(0.5)


if __name__ == '__main__':
    main()
