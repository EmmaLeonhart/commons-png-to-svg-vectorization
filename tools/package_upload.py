"""Package upload/ for uploading to Commons: one flat folder (and zip) of SVGs, each named after the file it replaces
(.png -> .svg) and carrying a licence comment: CC BY-SA 4.0, the original file, its author and licence, and any
data or drawing credits from its notes.md. Also writes LICENSE.txt explaining why one licence covers them all.
Needs scratch/lic.json (original file, licence and author per folder, fetched from the Commons API).
usage (repo root): python tools/package_upload.py OUT_DIR"""
import glob, json, os, re, shutil, sys, zipfile

out = sys.argv[1]
d = json.load(open('scratch/lic.json', encoding='utf8'))
CREDITS = [  # (pattern in notes.md, credit line)
    (r'国土数値情報', 'Boundaries: 「国土数値情報（行政区域データ）」（国土交通省） / MLIT National Land Numerical Information '
                 '(Government of Japan Standard Terms of Use 2.0, CC BY 4.0 compatible).'),
    (r'OpenStreetMap', 'Outline: © OpenStreetMap contributors (ODbL), as a produced work.'),
    (r'geoBoundaries|EuroGeographics', 'Greek boundaries: © EuroGeographics, via geoBoundaries (CC BY 4.0).'),
    (r'Natural Earth', 'Geography: Natural Earth (public domain).'),
    (r'Census|census', 'Boundaries: US Census Bureau (public domain).'),
]


def comment_text(t):
    return re.sub(r'-{2,}', '-', t)  # "--" is not allowed inside an XML comment


if os.path.exists(out):
    shutil.rmtree(out)
os.makedirs(out)
seen, rows = {}, []
for folder, png in sorted(d['items'].items()):
    src = os.path.join('upload', folder)
    svgs = glob.glob(os.path.join(src, '*.svg'))
    notes = open(os.path.join(src, 'notes.md'), encoding='utf8').read()
    name = re.sub(r'\.(png|jpe?g|gif)$', '.svg', png, flags=re.I)
    commons_name = name
    name = re.sub(r'[<>:"/\\|?*]', "'", name)  # Windows-safe; the intended Commons name is in the comment
    if name in seen:
        raise SystemExit(f'name clash: {name} ({folder}, {seen[name]})')
    seen[name] = folder
    lic = d['lic'][png][0] or 'see the original file page'
    author = d['artist'].get(png) or 'see the original file page'
    # OFL originals (renderings of a font) cannot be relicensed under CC BY-SA: they keep the OFL
    ofl = 'OFL' in lic
    lines = [f'{commons_name}: vector rebuild of File:{png} (Wikimedia Commons).',
             'Licence: SIL Open Font License 1.1 (OFL), as the original, https://openfontlicense.org' if ofl else
             'Licence: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0),',
             *([] if ofl else ['  https://creativecommons.org/licenses/by-sa/4.0/']),
             f'Original: File:{png}, by {author}, licensed {lic}.']
    lines += [c for p, c in CREDITS if re.search(p, notes)]
    reused = re.findall(r'\[\[:File:([^\]]+\.svg)\]\][^\n]*?\(([^)]*)\)', notes)
    if reused:
        lines.append('Drawings reused from Commons: ' + '; '.join(f'File:{f} ({l})' for f, l in reused) + '.')
    m = re.search(r'\[File:([^\]]+\.svg)\]\(https://commons', notes)
    if m and not reused:
        lines.append(f'Built from File:{m.group(1)} (Wikimedia Commons).')
    comment = '<!--\n' + comment_text('\n'.join(lines)) + '\n-->\n'
    svg = open(svgs[0], encoding='utf8').read().lstrip('﻿')
    decl = re.match(r'\s*<\?xml[^>]*\?>\s*', svg)
    svg = (svg[:decl.end()] + comment + svg[decl.end():]) if decl else (comment + svg)
    open(os.path.join(out, name), 'w', encoding='utf8', newline='\n').write(svg)
    rows.append(f'{name}\tFile:{png}\t{lic}\t{author}' + ('' if name == commons_name else f'\t(upload as {commons_name})'))

open(os.path.join(out, 'LICENSE.txt'), 'w', encoding='utf8').write(
    'All SVG files in this folder are released under CC BY-SA 4.0\n'
    '(https://creativecommons.org/licenses/by-sa/4.0/). Each file names, in a comment at its top, the Commons file it\n'
    'rebuilds, that file\'s author and licence, and any data or drawings it was built from.\n\n'
    'Why one licence covers them all: their sources are public domain, CC0, "copyrighted free use", CC BY 2.5/3.0/4.0,\n'
    'CC BY-SA 2.5/3.0/4.0 (which allow adaptations under later versions), GFDL files that are also CC BY-SA, the\n'
    'Government of Japan Standard Terms of Use 2.0 (CC BY 4.0 compatible; MLIT credit given), geoBoundaries (CC BY 4.0)\n'
    'and OpenStreetMap (ODbL; maps drawn from it are produced works that need only attribution). All of these can be\n'
    'adapted under CC BY-SA 4.0. Files whose originals are public domain stay free to use as public domain material.\n\n'
    'file\toriginal\toriginal licence\toriginal author\n' + '\n'.join(rows) + '\n')
z = out.rstrip('/\\') + '.zip'
with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
    for f in sorted(os.listdir(out)):
        zf.write(os.path.join(out, f), f)
print(len(rows), 'SVGs ->', out, 'and', z)
