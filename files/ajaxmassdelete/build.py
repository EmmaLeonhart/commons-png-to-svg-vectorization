"""Rebuild File:AjaxMassDelete FlowChart.png (Rillke's 2011 control-flow chart for AjaxMassDelete) by construction. The
chart is made of a few node styles drawn from templates (blue-bordered process boxes, decision diamonds, asynchronous
calls, terminals, dialog steps, stacks), connectors, labels and two background regions. Node boxes were found by their
#3298ff border (node_boxes.json); types and texts are transcribed from the PNG. Gradients run left to right between
colours sampled from the PNG. Run from the repo root."""
import json, sys
import numpy as np
from PIL import Image

PNG = 'data_lake/downloads/ajaxmassdelete-flowchart/AjaxMassDelete FlowChart.png'
OUT = 'files/ajaxmassdelete/AjaxMassDelete FlowChart.svg'
a = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
H, W = a.shape[:2]

BORDER, SHADOW = '#3298ff', '#226ab2'
STYLE = {  # gradient left, right, text colour
    'proc': ('#8b8baf', '#cbcbff', '#000000'), 'red': ('#8e4646', '#ca6464', '#000000'),
    'dec': ('#aeaeae', '#ffffff', '#333333'), 'async': ('#afafaf', '#ffffff', '#00ff99'),
    'green': ('#008c22', '#00cb32', '#ffffff'), 'orange': ('#ad6700', '#ff9800', '#ffffff'),
}
# (type, x, y, w, h, text); text lines split by '|'
NODES = [
    ('green', 29, 11, 129, 65, 'Perfom batch task'), ('proc', 318, 22, 100, 74, 'findOriginal|Uploader'),
    ('async', 497, 23, 100, 50, 'ApiCall'), ('dec', 175, 70, 100, 99, 'page-type'), ('proc', 45, 83, 100, 74, 'mdStartMd'),
    ('proc', 620, 83, 100, 74, 'findOriginal|UploaderCB'), ('proc', 45, 172, 100, 74, 'mdContinue'),
    ('async3', 655, 217, 116, 65, 'ApiCall'), ('async', 499, 222, 100, 50, 'Setting up the|selection Dialog'),
    ('async', 155, 227, 100, 50, 'ApiCall'), ('proc', 45, 273, 100, 74, 'mdFind|Uploads'),
    ('proc', 770, 282, 100, 74, 'mdQueriedFile'), ('proc', 235, 284, 100, 74, 'mdFind|UploadsCB'),
    ('proc', 438, 284, 100, 74, 'mdGenIThumbs'), ('proc', 567, 284, 100, 74, 'mdSendNext|Queries'),
    ('dec', 45, 351, 100, 99, 'Batch of files|queried?'), ('proc', 206, 410, 100, 74, 'mdQueryMore|(Thumbs)'),
    ('proc', 45, 485, 100, 74, 'mdQueryFile|Done'), ('orange', 452, 508, 100, 49, 'destroy dialog'),
    ('async', 610, 534, 100, 50, 'ApiCall'), ('green', 851, 554, 124, 62, 'mdExecute|Ready'),
    ('dec', 363, 570, 100, 99, 'user pressed|button'), ('red', 360, 700, 100, 74, 'mdExecute'),
    ('proc', 35, 742, 43, 32, ''), ('proc', 360, 803, 100, 74, 'mdExecute|Continue'), ('async', 612, 737, 100, 50, 'ApiCall'),
    ('red', 33, 907, 44, 32, ''), ('dec', 362, 912, 100, 99, 'files selected'), ('dec', 500, 912, 100, 99, 'Task'),
    ('async', 612, 899, 100, 50, 'ApiCall'), ('async', 241, 969, 100, 50, 'Setting up the|selection Dialog'),
    ('async3', 36, 987, 113, 66, 'HTTP request|index.php'), ('dec', 500, 1026, 100, 99, 'Task'),
    ('proc', 169, 1044, 100, 74, 'mdRv|GenOThumbs'), ('proc', 49, 1129, 100, 74, 'mdRv|QueriedFile'),
    ('orange', 697, 1176, 99, 49, 'destroy dialog'), ('dec', 169, 1222, 99, 99, 'All files|processed?'),
    ('dec', 596, 1222, 99, 99, 'user pressed|button'), ('proc', 330, 1234, 100, 74, 'mdRv|AllFilesQueried'),
    ('async3', 327, 1337, 113, 66, 'HTTP request|index.php'), ('proc', 163, 1353, 100, 74, 'mdReverted'),
    ('proc', 448, 1353, 100, 74, 'mdRevert|Image'), ('red', 596, 1353, 100, 74, 'mdRvEval|Selction'),
]


# the two background regions (initially uploaded / overwritten images), measured edges
BLUE_REGION = 'M14,6H979V1146H358V960H14Z'
OLIVE_REGION = 'M14,964H354V1149H834V1495H14Z'


# grey document stacks (helper functions): bounding box of the stack, text; three documents offset 10 px
STACKS = [(817, 150, 98, 99, 'mdExtract|Tags|~License'), (714, 536, 101, 102, 'mdInsert|Permission'),
          (716, 682, 101, 102, 'mdPrepend|Template|notifyUploaders'), (716, 844, 101, 102, 'mdPrepend|Template|notifyUploaders'),
          (28, 1282, 98, 99, 'mdRv|CreateImg|RevisionMatrix')]
# 'wait for user input' shapes: downward-narrowing trapezoids
WAITS = [(232, 517, 51, 52), (562, 1171, 51, 52)]
LEGEND_BOX = (19, 684, 327, 265)
# free labels: text, rough box (x0, x1, y0, y1), weight, colour; 'rot' boxes are set rotated -90 degrees
LABELS = [('Image', (252, 295, 67, 85)), ('other', (180, 219, 169, 188)), ('first time only', (337, 427, 315, 334)),
          ('Yes', (65, 96, 451, 470)), ('scroll /', (265, 313, 486, 504)), ('more>>', (265, 321, 500, 518)),
          ('cancel', (455, 500, 599, 618)), ('proceed', (415, 470, 669, 688)), ('OTRS and other', (563, 687, 589, 608)),
          ('mdCreate', (735, 798, 667, 684)), ('RequestSubpage', (715, 818, 679, 697)), ('delete', (612, 657, 713, 732)),
          ('listRequest', (730, 803, 766, 784)), ('Subpage', (740, 795, 779, 797)),
          ('no permission, source,', (567, 703, 863, 881)), ('speedy', (611, 660, 875, 894)), ('>0', (460, 483, 945, 961)),
          ('=0', (444, 468, 1059, 1076)), ('OTRS and other', (683, 773, 1057, 1076)),
          ('delete, no permission,', (322, 456, 1167, 1186)), ('source, speedy', (347, 435, 1180, 1199)),
          ('cancel', (700, 743, 1252, 1271)), ('revert images', (652, 740, 1321, 1340)),
          ('silent call', (24, 40, 442, 503), 'rot', '#000000'),
          ('decision', (78, 150, 695, 718), 'normal'), ('function/', (78, 160, 737, 760), 'normal'),
          ('process', (78, 150, 755, 778), 'normal'), ('helper function/', (78, 240, 797, 820), 'normal'),
          ('sequence collection', (78, 240, 815, 837), 'normal'), ('asynchronous execution/', (78, 287, 847, 870), 'normal'),
          ('calls back', (78, 287, 865, 888), 'normal'), ('reading user input; this is in', (78, 305, 902, 925), 'normal'),
          ('context of a dialog', (78, 305, 920, 943), 'normal'),
          ('initially uploaded', (735, 975, 23, 56), 'bold', '#000099'), ('images', (870, 975, 54, 86), 'bold', '#000099'),
          ('overwritten', (16, 188, 1430, 1462), 'bold', '#cc6633'), ('images', (16, 120, 1458, 1492), 'bold', '#cc6633')]


def stack_doc(x, y, w, h):
    """one document: rounded top corners, a wavy bottom edge"""
    r = 6
    return (f'M{x},{y + r}A{r},{r} 0 0 1 {x + r},{y}H{x + w - r}A{r},{r} 0 0 1 {x + w},{y + r}V{y + h * 0.84:.1f}'
            f'C{x + w * 0.7:.1f},{y + h * 0.70:.1f} {x + w * 0.42:.1f},{y + h * 1.08:.1f} {x},{y + h * 0.93:.1f}Z')


def stack(i, x, y, w, h, outline='#ffffff', sw=2.5):
    out, step = [], round(w * 0.1)
    fw, fh = w - 2 * step, h - 2 * step
    for k in range(3):
        out.append(f'<path d="{stack_doc(x + k * step, y + k * step, fw, fh)}" fill="url(#s{i})" stroke="{outline}" '
                   f'stroke-width="{sw}"/>')
    return out


def text_lines(k, x, y, w, h, t):
    """ink boxes of a node's text lines: pixels near its text colour inside the node, split at empty rows"""
    if not t:
        return []
    col = STYLE['async' if k == 'async3' else k][2] if k in STYLE or k == 'async3' else '#000000'
    rgb = [int(col[i:i + 2], 16) for i in (1, 3, 5)]
    if k == 'async3':
        x, y, w, h = x + 14, y + 14, w - 14, h - 14
    ix, iy = (10, 24) if k == 'dec' else (6, 6)  # diamonds: their middle band only, clear of connector tips
    x, y, w, h = x + ix - 6, y + iy - 6, w - 2 * (ix - 6), h - 2 * (iy - 6)
    if k == 'red':  # the dialog checkbox sits under the text
        h -= 24
    sub = a[y + 6:y + h - 6, x + 6:x + w - 6]
    dark = sub.sum(2) < (150 if k == 'red' else 330)  # the dialog gradient is dark itself
    m = (np.abs(sub - rgb).sum(2) < 60) | (dark if col != '#ffffff' else False)
    if col != '#ffffff' and not (np.abs(sub - rgb).sum(2) < 60).sum() > 20:
        col = '#000000' if (sub[dark].mean() < 30 if dark.any() else True) else '#333333'
    rows = np.nonzero(m.sum(1) > 0)[0]
    lines = t.split('|')
    groups = np.split(rows, np.nonzero(np.diff(rows) > 1)[0] + 1)
    groups = [g for g in groups if len(g) >= 4]
    if len(groups) > len(lines):  # stray rows (node edges, the dialog checkbox): keep the lines with the most ink
        groups = sorted(sorted(groups, key=lambda g: -m[g.min():g.max() + 1].sum())[:len(lines)], key=lambda g: g.min())
    if len(groups) != len(lines):
        print('  line count mismatch', t, len(groups)); return []
    out = []
    for line, g in zip(lines, groups):
        cols = np.nonzero(m[g.min():g.max() + 1].sum(0) > 0)[0]
        out.append((line, (x + 6 + cols.min(), x + 6 + cols.max(), y + 6 + g.min(), y + 6 + g.max()), col))
    return out


def fit_texts(family='Verdana', weight='bold'):
    sys.path.insert(0, 'tools')
    from fit_text import fit
    out = []
    for k, x, y, w, h, t in NODES + [('stack', *b) for b in STACKS] + [('wait', *b, 'wait for|user|input') for b in WAITS]:
        for line, box, col in text_lines(k, x, y, w, h, t):
            out.append(dict(fit(line, box, family, weight, canvas=(W, H)), text=line, fill=col))
    return out


def fit_labels(family='Verdana'):
    sys.path.insert(0, 'tools')
    from fit_text import fit
    out = []
    for t, (x0, x1, y0, y1), *opt in LABELS:
        weight = opt[0] if opt else 'bold'
        col = opt[1] if len(opt) > 1 else '#000000'
        rgb = [int(col[i:i + 2], 16) for i in (1, 3, 5)]
        sub = a[y0:y1, x0:x1]
        m = np.abs(sub - rgb).sum(2) < (100 if col == '#000000' else 150)  # black text, not the #333 outlines
        ys, xs = np.nonzero(m)
        if len(xs) < 10:
            print('  no ink for label', t, (x0, x1, y0, y1)); continue
        bx0, bx1, by0, by1 = x0 + xs.min(), x0 + xs.max(), y0 + ys.min(), y0 + ys.max()
        if weight == 'rot':
            cx, cy, hw, hh = (bx0 + bx1) / 2, (by0 + by1) / 2, (by1 - by0) / 2, (bx1 - bx0) / 2
            q = fit(t, (cx - hw, cx + hw, cy - hh, cy + hh), family, 'normal', canvas=(W, H)); q['rotate'] = [-90, cx, cy]
            weight = 'normal'
        else:
            q = fit(t, (bx0, bx1, by0, by1), family, weight, canvas=(W, H))
        out.append(dict(q, text=t, fill=col, weight=weight))
    return out


def grad(i, kind):
    l, r, _ = STYLE[kind]
    return f'<linearGradient id="g{i}"><stop offset="0" stop-color="{l}"/><stop offset="1" stop-color="{r}"/></linearGradient>'


def shape(kind, x, y, w, h, inset=0):
    """the outline of a node type, inset by `inset` px"""
    x, y, w, h = x + inset, y + inset, w - 2 * inset, h - 2 * inset
    if kind == 'dec':
        return f'<path d="M{x + w / 2},{y}L{x + w},{y + h / 2}L{x + w / 2},{y + h}L{x},{y + h / 2}Z"'
    if kind in ('async', 'async3'):
        r = h / 2
        return f'<path d="M{x + 6},{y}H{x + w - r}A{r},{r} 0 0 1 {x + w - r},{y + h}H{x + 6}A6,6 0 0 1 {x},{y + h - 6}V{y + 6}A6,6 0 0 1 {x + 6},{y}Z"'
    if kind in ('green', 'orange'):
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}"'
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{max(9 - inset, 3)}"'


def node(i, kind, x, y, w, h):
    base = 'async' if kind == 'async3' else kind
    out = []
    copies = [(-14, -14), (-7, -7), (0, 0)] if kind == 'async3' else [(0, 0)]
    if kind == 'async3':  # a stack of three: the back two offset up and left
        w, h = w - 14, h - 14
        x, y = x + 14, y + 14
    for dx, dy in copies:
        X, Y = x + dx, y + dy
        out.append(shape(kind, X, Y, w, h) + f' fill="{BORDER}"/>')
        if base in ('proc', 'red'):
            out.append(shape(kind, X + 2, Y + 2, w - 1, h - 1, 5.5) + f' fill="{SHADOW}"/>')
        out.append(shape(kind, X, Y, w, h, 5.5) + f' fill="url(#g{i})"/>')
    return out


PAR = 'files/ajaxmassdelete/texts.json'
FONT = "Verdana, 'DejaVu Sans', sans-serif"

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'fit':
        json.dump(fit_texts() + fit_labels(), open(PAR, 'w', encoding='utf8'), ensure_ascii=False, indent=0)
    T = json.load(open(PAR, encoding='utf8'))
    defs = [grad(i, 'async' if k == 'async3' else k) for i, (k, *_) in enumerate(NODES)]
    defs += [f'<linearGradient id="s{i}"><stop offset="0" stop-color="#b8b8b8"/><stop offset="0.75" stop-color="#ffffff"/>'
             '</linearGradient>' for i in range(len(STACKS) + 1)]
    defs.append('<linearGradient id="lav"><stop offset="0" stop-color="#8b8baf"/><stop offset="1" stop-color="#cbcbff"/></linearGradient>')
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         '<defs>', *defs, '</defs>',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" fill="none" stroke="#000000"/>',
         f'<path fill="#99ccff" d="{BLUE_REGION}"/>', f'<path fill="#cccc99" d="{OLIVE_REGION}"/>']
    C = json.load(open('files/ajaxmassdelete/connectors.json'))
    pd = lambda p: 'M' + ' '.join(f'{x},{y}' for x, y in p)
    tri = lambda q: (lambda b, t, h: (lambda u: f'M{t[0]:.1f},{t[1]:.1f}L{b[0] - u[1] * h:.1f},{b[1] + u[0] * h:.1f}'
                     f'L{b[0] + u[1] * h:.1f},{b[1] - u[0] * h:.1f}Z')(np.subtract(t, b) / max(np.hypot(*np.subtract(t, b)), 1e-6)))(
                     q['base'], q['tip'], q['half'])
    conn = []
    for style, col, w, outline in (('white', '#ffffff', 5, True), ('green', '#00cc00', 5, True), ('red', '#993333', 7, False),
                                    ('orange', '#ff9933', 5, False)):
        d = ''.join(pd(p) for p in C[style]['paths']); arr = ''.join(tri(q) for q in C[style]['arrows'])
        if outline:
            conn.append(f'<path fill="none" stroke="#333333" stroke-width="{w + 2}" stroke-linejoin="round" d="{d}"/>')
            conn.append(f'<path fill="{col}" stroke="#333333" stroke-width="1" d="{arr}"/>')
        conn.append(f'<path fill="none" stroke="{col}" stroke-width="{w}" stroke-linejoin="round" d="{d}"/>')
        if not outline:
            conn.append(f'<path fill="{col}" d="{arr}"/>')
    o += conn
    lx, ly, lw, lh = LEGEND_BOX
    o.append(f'<rect x="{lx + 0.5}" y="{ly + 0.5}" width="{lw - 1}" height="{lh - 1}" fill="#ffffff" stroke="#000000"/>')
    for i, (k, x, y, w, h, t) in enumerate(NODES):
        o += node(i, k, x, y, w, h)
    for i, (x, y, w, h, t) in enumerate(STACKS):
        o += stack(i, x, y, w, h)
    o += stack(len(STACKS), 34, 793, 41, 41, BORDER, 1.5)  # legend: helper function
    o.append(f'<path d="M54,688L74,707.5L54,727L34,707.5Z" fill="url(#lav)" stroke="{BORDER}" stroke-width="2.5" '
             'stroke-linejoin="round"/>')  # legend: decision
    o.append(f'<path d="M37,860H66A10,10 0 0 1 66,880H37A3,3 0 0 1 34,877V863A3,3 0 0 1 37,860Z" fill="url(#s0)" '
             f'stroke="{BORDER}" stroke-width="1.5"/>')  # legend: asynchronous call
    for x, y, w, h in WAITS:
        o.append(f'<path d="M{x + 1},{y + 1}H{x + w - 1}L{x + w - 9},{y + h - 4}Q{x + w - 10},{y + h - 1} {x + w - 14},{y + h - 1}'
                 f'H{x + 14}Q{x + 10},{y + h - 1} {x + 9},{y + h - 4}Z" fill="url(#s0)" stroke="{BORDER}" stroke-width="2"/>')
    for q in T:
        ls = f' letter-spacing="{q["ls"]}"' if 0.05 < abs(q['ls']) < 5 else ''
        tr = f' transform="rotate({q["rotate"][0]} {q["rotate"][1]:.1f} {q["rotate"][2]:.1f})"' if 'rotate' in q else ''
        t = q['text'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        o.append(f'<text x="{q["x"]}" y="{q["y"]}" font-size="{q["size"]}"{ls} font-weight="{q.get("weight", "bold")}"{tr} '
                 f'fill="{q["fill"]}" font-family="{FONT}">{t}</text>')
    o.append('</svg>')
    open(OUT, 'w', encoding='utf8').write('\n'.join(o) + '\n')
    print('wrote', OUT)
