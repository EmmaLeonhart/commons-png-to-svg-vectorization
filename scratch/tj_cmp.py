import io, glob, re, resvg_py
from pathlib import Path
from PIL import Image
F = ['data_lake/downloads/fonts/dejavu/DejaVuSans-Bold.ttf', 'data_lake/downloads/fonts/dejavu/DejaVuSansCondensed-Bold.ttf']
fs = sorted(glob.glob('data_lake/downloads/transjakarta/*.png'))
w = lambda x: Image.alpha_composite(Image.new('RGBA', x.size, '#dddddd'), x).convert('RGB')
pairs = []
for f in fs:
    n = Path(f).stem
    slug = re.sub(r'[^a-z0-9]+', '-', n.lower()).strip('-')
    a = Image.open(f).convert('RGBA'); a.thumbnail((200, 200))
    s = open(f'files/{slug}/{n}.svg', encoding='utf8').read()
    b = Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=s, width=200, font_files=F, skip_system_fonts=True)))).convert('RGBA')
    pairs.append((w(a), w(b)))
cols = min(len(pairs), 8)
rows = -(-len(pairs) // cols)
c = Image.new('RGB', (210 * cols, 420 * rows), 'white')
for k, (x, y) in enumerate(pairs):
    c.paste(x, ((k % cols) * 210, (k // cols) * 420)); c.paste(y, ((k % cols) * 210, (k // cols) * 420 + 205))
c.save('scratch/arms/tj_cmp.png')
