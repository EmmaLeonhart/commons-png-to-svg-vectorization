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


def text_lines(k, x, y, w, h, t):
    """ink boxes of a node's text lines: pixels near its text colour inside the node, split at empty rows"""
    if not t:
        return []
    col = STYLE['async' if k == 'async3' else k][2]
    rgb = [int(col[i:i + 2], 16) for i in (1, 3, 5)]
    if k == 'async3':
        x, y, w, h = x + 14, y + 14, w - 14, h - 14
    ix, iy = (20, 22) if k == 'dec' else (6, 6)  # diamonds: their centre only, clear of connector tips
    x, y, w, h = x + ix - 6, y + iy - 6, w - 2 * (ix - 6), h - 2 * (iy - 6)
    sub = a[y + 6:y + h - 6, x + 6:x + w - 6]
    dark = sub.sum(2) < 330
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
    for k, x, y, w, h, t in NODES:
        for line, box, col in text_lines(k, x, y, w, h, t):
            out.append(dict(fit(line, box, family, weight, canvas=(W, H)), text=line, fill=col))
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
        json.dump(fit_texts(), open(PAR, 'w', encoding='utf8'), ensure_ascii=False, indent=0)
    T = json.load(open(PAR, encoding='utf8'))
    defs = [grad(i, 'async' if k == 'async3' else k) for i, (k, *_) in enumerate(NODES)]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         '<defs>', *defs, '</defs>',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" fill="none" stroke="#000000"/>',
         f'<path fill="#99ccff" d="{BLUE_REGION}"/>', f'<path fill="#cccc99" d="{OLIVE_REGION}"/>']
    for i, (k, x, y, w, h, t) in enumerate(NODES):
        o += node(i, k, x, y, w, h)
    for q in T:
        ls = f' letter-spacing="{q["ls"]}"' if 0.05 < abs(q['ls']) < 5 else ''
        o.append(f'<text x="{q["x"]}" y="{q["y"]}" font-size="{q["size"]}"{ls} font-weight="bold" fill="{q["fill"]}" '
                 f'font-family="{FONT}">{q["text"]}</text>')
    o.append('</svg>')
    open(OUT, 'w', encoding='utf8').write('\n'.join(o) + '\n')
    print('wrote', OUT)
