"""Crude birth and death rates of Japan 1950-2019 (per 1000) from the vital-statistics table of
en.wikipedia "Demographics of Japan" (sources: IPSS, Statistics Bureau of Japan), saved in
data_lake/downloads/japan-birth-death/. Writes files/japan-birth-death-rate/rates.csv."""
import json, re

t = json.load(open('data_lake/downloads/japan-birth-death/Demographics_of_Japan.wikitext.json', encoding='utf8'))['parse']['wikitext']
k = t.find('===Statistics since 1873===')
tab = t[k:t.find('\n|}', k)]
rows = {}
for r in tab.split('\n|-'):
    cells = [re.sub(r'^.*\|', '', c).strip() for c in re.split(r'\n\||\|\|', r)[1:]]
    if cells and re.fullmatch(r'\d{4}', cells[0]) and 1950 <= int(cells[0]) <= 2019:
        rows[int(cells[0])] = (float(cells[5].replace('−', '-')), float(cells[6].replace('−', '-')))
assert len(rows) == 70, len(rows)
with open('files/japan-birth-death-rate/rates.csv', 'w') as f:
    f.write('year,crude_birth_rate,crude_death_rate\n')
    for y in sorted(rows):
        f.write(f'{y},{rows[y][0]},{rows[y][1]}\n')
print(rows[1950], rows[1966], rows[2019])
