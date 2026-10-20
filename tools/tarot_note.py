"""Add a one-comment provenance and licence note to each optimised tarot SVG in tarot/ (svgo strips comments).
usage (repo root): python tools/tarot_note.py"""
import glob, os
for f in sorted(glob.glob('tarot/*.svg')):
    s = open(f, encoding='utf8').read()
    if s.startswith('<!--'):
        continue
    name = os.path.basename(f)
    note = (f'<!-- {name}: size-optimised version of File:{name} (Wikimedia Commons, Category:Vectorized Tarot by '
            'Immanuelle). Near-identical colours merged (CIELAB distance under 6), structure and path data compacted '
            'with svgo (0.1 px precision). Public domain, as the original (Rider-Waite-Smith deck, 1909). -->\n')
    open(f, 'w', encoding='utf8', newline='\n').write(note + s)
print('noted', len(glob.glob('tarot/*.svg')))
