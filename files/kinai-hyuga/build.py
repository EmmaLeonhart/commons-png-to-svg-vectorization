"""Rebuild File:Kinai-and-Hyuga-Province-in-Japan-RA.png as an SVG from its source,
File:Provinces_of_Japan.svg. Run from the repo root: python files/kinai-hyuga/build.py

The crop and the province choices were found by registering the source against the PNG
(94.6% pixel agreement); see notes.md. All labels are real <text> so SVGTranslate works.
"""
import re
from pathlib import Path
from lxml import etree

HERE = Path(__file__).parent
SRC = Path('data_lake/downloads/kinai-hyuga/Provinces_of_Japan.svg')
OUT = HERE / 'Kinai-and-Hyuga-Province-in-Japan-RA.svg'
NS = 'http://www.w3.org/2000/svg'
Q = lambda t: f'{{{NS}}}{t}'

# PNG pixel -> source user units: x = OX + S*u, y = OY + S*v
S, OX, OY = 0.2335, 37.7778, 432.9111
SIZE = 1400

SEA, LAND = '#d5e1fe', '#fbfbfb'
COAST, BORDER = '#0050e8', '#737373'
HIGHLIGHT = {
    'g2700': '#ffe9b8',   # Hyuga
    'g8791': '#fab9d5',   # Izumo
    'g23010': '#8be3b2',  # Yamashiro
    'g15010': '#8be3b2',  # Settsu
    'g23919': '#8be3b2',  # Kawachi
    'g15898': '#8be3b2',  # Izumi
    'g22122': '#8be3b2',  # Yamato
}

FONT = "'Noto Serif CJK JP', 'Noto Serif JP', serif"
# (id, x, baseline y, size, anchor, text)
LABELS = [
    ('label-izumo-ja', 635, 361, 80, 'middle', '出雲'),
    ('label-izumo', 635, 436, 80, 'middle', 'Izumo'),
    ('label-kinai-ja', 1150, 297, 80, 'middle', '畿内'),
    ('label-kinai', 1150, 371, 80, 'middle', 'Kinai'),
    ('label-kinai-count', 1150, 439, 80, 'middle', '(5 Provinces)'),
    ('label-hyuga-ja', 451, 1040, 80, 'middle', '日向'),
    ('label-hyuga', 451, 1117, 80, 'middle', 'Hyuga'),
    ('label-hyuga-alt', 451, 1185, 80, 'middle', '(Himuka)'),
    ('num-1', 1200, 536, 58, 'middle', '1'),
    ('num-2', 1139, 556, 58, 'middle', '2'),
    ('num-3', 1181, 606, 58, 'middle', '3'),
    ('num-4', 1138, 636, 58, 'middle', '4'),
    ('num-5', 1221, 677, 58, 'middle', '5'),
    ('legend-title', 1055, 945, 80, 'middle', 'KINAI'),
    ('legend-1', 766, 1022, 80, 'start', '1 Yamashiro 山城'),
    ('legend-2', 766, 1100, 80, 'start', '2 Settsu 摂津'),
    ('legend-3', 766, 1179, 80, 'start', '3 Kawachi 河内'),
    ('legend-4', 766, 1256, 80, 'start', '4 Izumi 和泉'),
    ('legend-5', 766, 1335, 80, 'start', '5 Yamato 大和'),
]


def restyle(el, **props):
    st = el.get('style', '')
    for k, v in props.items():
        k = k.replace('_', '-')
        if re.search(rf'(^|;){k}:', st):
            st = re.sub(rf'(^|;){k}:[^;]*', rf'\g<1>{k}:{v}', st)
        else:
            st = f'{st};{k}:{v}' if st else f'{k}:{v}'
    el.set('style', st)


def main():
    src = etree.parse(str(SRC)).getroot()
    layer1 = src.find(f".//{Q('g')}[@id='layer1']")   # provinces + lakes
    layer2 = src.find(f".//{Q('g')}[@id='layer2']")   # coastline strokes

    for el in layer1.iter(Q('g'), Q('path')):
        st = el.get('style', '')
        if 'fill:#fcf5e3' in st:
            restyle(el, fill=LAND, stroke=BORDER)
        elif 'fill:#daf0fd' in st:
            restyle(el, fill=SEA, stroke=COAST)
    for gid, colour in HIGHLIGHT.items():
        g = layer1.find(f".//*[@id='{gid}']")
        for el in [g, *g.iter(Q('path'))]:
            restyle(el, fill=colour)
    for el in layer2.iter(Q('g'), Q('path')):
        restyle(el, stroke=COAST)

    svg = etree.Element(Q('svg'), nsmap={None: NS}, width=str(SIZE), height=str(SIZE),
                        viewBox=f'0 0 {SIZE} {SIZE}', version='1.1')
    title = etree.SubElement(svg, Q('title'))
    title.text = 'Hyuga, Izumo, and the five provinces of Kinai'
    etree.SubElement(svg, Q('rect'), id='sea', width=str(SIZE), height=str(SIZE), fill=SEA)
    k = 1 / S
    m = etree.SubElement(svg, Q('g'), id='map',
                         transform=f'matrix({k:.6f},0,0,{k:.6f},{-OX * k:.4f},{-OY * k:.4f})')
    m.append(layer1)
    m.append(layer2)
    etree.SubElement(svg, Q('rect'), id='label-panel', x='936', y='208', width='464', height='251',
                     fill='#ffffff', **{'fill-opacity': '0.5'})
    labels = etree.SubElement(svg, Q('g'), id='labels', style=(
        f'font-family:{FONT};fill:#000000;stroke:#ffffff;stroke-width:6;'
        'stroke-linejoin:round;paint-order:stroke'))
    for lid, x, y, size, anchor, text in LABELS:
        t = etree.SubElement(labels, Q('text'), id=lid, x=str(x), y=str(y),
                             style=f'font-size:{size}px;text-anchor:{anchor}')
        t.text = text

    etree.ElementTree(svg).write(str(OUT), xml_declaration=True, encoding='UTF-8', pretty_print=True)
    print(OUT)


if __name__ == '__main__':
    main()
