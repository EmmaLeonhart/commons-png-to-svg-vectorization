#!/bin/sh
# Rebuild File:Ottoman Turkish in Nastaliq (vertical).png: each of its two lines (split at the blank band between
# them) fitted as real <text> in Noto Nastaliq Urdu by tools/glyph_specimen.py, then merged. Run from the repo root.
set -e
P='data_lake/downloads/ottoman-nastaliq/Ottoman Turkish in Nastaliq (vertical).png'
F=data_lake/downloads/fonts/noto-nastaliq-urdu/NotoNastaliqUrdu-Regular.ttf
W=scratch/ottoman-nastaliq; mkdir -p $W
python - "$P" $W <<'PY'
import sys, numpy as np
from PIL import Image
im = Image.open(sys.argv[1]).convert('RGBA')
flat = Image.alpha_composite(Image.new('RGBA', im.size, 'white'), im).convert('RGB')
a = np.asarray(flat.convert('L')) < 128
rows = np.nonzero(a.any(1))[0]; k = int(np.argmax(np.diff(rows))); cut = (rows[k] + rows[k + 1]) // 2
for i, (y0, y1) in enumerate([(0, cut), (cut, im.height)], 1):
    b = np.asarray(flat).copy(); m = np.ones(b.shape[:2], bool); m[y0:y1] = False; b[m] = 255
    Image.fromarray(b).save(f'{sys.argv[2]}/l{i}.png')
PY
PYTHONIOENCODING=utf8 python tools/glyph_specimen.py $W/l1.png $W/l1.svg "لسان" $F "Noto Nastaliq Urdu" | tail -1
PYTHONIOENCODING=utf8 python tools/glyph_specimen.py $W/l2.png $W/l2.svg "عثمانی" $F "Noto Nastaliq Urdu" | tail -1
OUT='files/ottoman-nastaliq/Ottoman Turkish in Nastaliq (vertical).svg'
{ head -1 $W/l1.svg; grep '<text' $W/l1.svg; grep '<text' $W/l2.svg; echo '</svg>'; } > "$OUT"
echo wrote "$OUT"
