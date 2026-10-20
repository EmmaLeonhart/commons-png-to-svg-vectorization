"""Stage a shadow picture rebuilt by tools/shadow_rotfit.py: render a side-by-side comparison into the screenshots
folder, copy the SVG and notes into upload/, take the item off queue.md and log it in devlog.md.
usage (repo root): python tools/shadow_package.py SLUG CODE IOU [extra note]"""
import io, json, os, shutil, sys, datetime
import resvg_py
from PIL import Image

slug, code, iou = sys.argv[1], sys.argv[2], float(sys.argv[3])
extra = (' ' + sys.argv[4]) if len(sys.argv) > 4 else ''
name = slug.capitalize()
title = os.environ.get('SHADOW_TITLE', f'Shadow picture of {name} prefecture')
svg_path = f'files/shadow-{slug}/{title}.svg'
png_path = f'data_lake/downloads/shadow-{slug}/{title}.png'
shots = os.path.join(os.path.expanduser('~'), 'Documents', 'claude-screenshots',
                     'agentic-vectorization_' + datetime.date.today().isoformat())
os.makedirs(shots, exist_ok=True)

r = Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=open(svg_path, encoding='utf8').read())))).convert('RGBA')
r = Image.alpha_composite(Image.new('RGBA', r.size, 'white'), r).convert('RGB')
p = Image.open(png_path).convert('RGBA')
p = Image.alpha_composite(Image.new('RGBA', p.size, 'white'), p).convert('RGB')
c = Image.new('RGB', (p.width * 2 + 10, p.height), 'white'); c.paste(p, (0, 0)); c.paste(r, (p.width + 10, 0))
c.thumbnail((1400, 800))
shot = os.path.join(shots, f'cmp_shadow-{slug}.png')
c.save(shot)

P = json.load(open(f'files/shadow-{slug}/projection.json'))
notes = f"""# {title}

- **Target:** [File:{title}.png](https://commons.wikimedia.org/wiki/File:{title.replace(' ', '_')}.png), {p.width}×{p.height}.
- **Rebuilt from:** 「国土数値情報（行政区域データ）」（国土交通省） N03-2024, municipalities merged into the
  prefecture and simplified to 0.0003°. Terms: Government of Japan Standard Terms of Use 2.0, compatible with
  CC BY 4.0. Release as CC BY 4.0 with that credit.
- **Method:** `python tools/shadow_rotfit.py {slug} {code} fit` (scale, aspect {P[1]:.2f}, rotation {P[2]:.1f}°, offset);
  silhouette IoU against the PNG {iou:.4f}. `tools/batch_shadow.py`, which fits scale and offset only, had parked it.{extra}
- **Text:** none.
- Comparison: `Documents\\claude-screenshots\\{os.path.basename(shots)}\\cmp_shadow-{slug}.png`.
"""
os.makedirs(f'upload/shadow-{slug}', exist_ok=True)
for d in (f'upload/shadow-{slug}', f'files/shadow-{slug}'):
    open(f'{d}/notes.md', 'w', encoding='utf8').write(notes)
shutil.copy(svg_path, f'upload/shadow-{slug}/')

q = open('queue.md', encoding='utf8').read().split('\n')
q2 = [l for l in q if f'File:{title}.png' not in l]
assert len(q) - len(q2) == 1, 'queue item not found exactly once'
open('queue.md', 'w', encoding='utf8').write('\n'.join(q2))
d = open('devlog.md', encoding='utf8').read()
open('devlog.md', 'w', encoding='utf8').write(
    d.rstrip('\n') + f"\n- **File:{title}.png → SVG** (`files/shadow-{slug}/`): `tools/shadow_rotfit.py`, IoU {iou:.3f}\n"
    f"  (rotation {P[2]:.1f}°). Staged in upload/.\n")
print('staged', slug, shot)
