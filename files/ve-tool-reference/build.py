"""Rebuild File:VisualEditor tool reference-ltr.png (a VisualEditor onboarding illustration, 500x300; a PNG in the
VisualEditor repository too) by construction, every coordinate measured in the PNG:
  - the article page: frame, grey side panel with its circle, a T and text lines, two yellow highlights holding a quote
    mark and the reference numbers [1] and [2] (real <text>);
  - the blue lines from the references to the sources;
  - the sources as line art: an open book (covers, pages, spine, page lines) and a newspaper (page, rolled edge, header
    bar, picture box, text lines).
Run from the repo root."""
OUT = 'files/ve-tool-reference/VisualEditor tool reference-ltr.svg'
W, H = 500, 300
SLATE, GREY_LINE, ICON, BLUE, YELLOW = '#797d94', '#797d94', '#555555', '#3366ff', '#ffffdf'

page = [f'<rect x="80" y="51" width="40" height="165" fill="#f1f1f1"/>',
        f'<circle cx="98.5" cy="74" r="12.3" fill="#c5c5c5"/>',
        f'<rect x="76.75" y="48.75" width="125" height="169.5" fill="none" stroke="{SLATE}" stroke-width="1.5"/>',
        f'<rect x="130" y="104" width="58" height="30" fill="{YELLOW}"/>',
        f'<rect x="130" y="178" width="58" height="30" fill="{YELLOW}"/>']
lines = [(158, 181, 69.5), (157, 178, 79.5), (136, 178, 89.5), (138, 180, 99.5), (138, 181, 139.5), (138, 180, 148.5),
         (135, 177, 158.5), (135, 177, 168.5)]
page.append(f'<path d="{"".join(f"M{a},{y}H{b}" for a, b, y in lines)}" fill="none" stroke="{GREY_LINE}" stroke-width="1.6" '
            'stroke-linecap="round"/>')
text = [f'<text x="137.5" y="80" font-family="Georgia, \'Times New Roman\', serif" font-size="16" fill="{SLATE}">T</text>',
        f'<text x="133" y="134.5" font-family="Georgia, \'Times New Roman\', serif" font-size="30" font-weight="bold" fill="#5e5e50">“</text>',
        f'<text x="133" y="208.5" font-family="Georgia, \'Times New Roman\', serif" font-size="30" font-weight="bold" fill="#5e5e50">“</text>',
        f'<text x="156.5" y="127.5" font-family="Arial, \'Liberation Sans\', sans-serif" font-size="19" font-weight="bold" fill="{BLUE}">[1]</text>',
        f'<text x="156.5" y="201.5" font-family="Arial, \'Liberation Sans\', sans-serif" font-size="19" font-weight="bold" fill="{BLUE}">[2]</text>']
links = f'<path d="M181,117.5L299.5,59M181,197.5L300.5,255.5" fill="none" stroke="{BLUE}" stroke-width="1.5"/>'

# open book: back covers, the two pages, the spine, page lines on the left page
book = ('M322.5,104V31Q322.5,25 327,24M322.5,104Q322.5,111 330,112.5L370,118.5Q374,119 378,118.5L418,112.5Q425.5,111 425.5,104V31'
        'Q425.5,25 421,24'                                                     # covers (outer outline)
        'M327.5,102V24Q327.5,18 333,18.5L374,29.5L415,18.5Q420.5,18 420.5,24V102Q420.5,107 414,108.5L374,117.5L334,108.5'
        'Q327.5,107 327.5,102Z'                                                # the two pages
        'M374,29.5V117.5')                                                     # spine
page_lines = ''.join(f'M337,{y}L367,{y + 9}' for y in (32, 40, 47.5, 54.5, 62, 69.5, 77, 84, 91.5))
# newspaper: page with a rounded foot, rolled edge with its slot, header bar, picture box, text lines
paper = ('M323.5,196.5H404.5V268M323.5,196.5V266Q323.5,276 333.5,276H418Q426,276 426,268V218.5'
         'M412,226V264Q412,269.5 416.5,269.5Q421,269.5 421,264V220')
boxes = ('<rect x="333" y="205" width="62" height="9.5" fill="none" stroke="{c}" stroke-width="2"/>'
         '<rect x="332.5" y="225" width="26" height="22" fill="none" stroke="{c}" stroke-width="2"/>').format(c=ICON)
tl = [(363, 393, 225.5), (363, 389, 233), (363, 386, 240.5), (363, 382, 248), (332, 354, 255), (363, 379, 255),
      (332, 358, 262.5), (363, 374, 262)]
paper_lines = ''.join(f'M{a},{y}H{b}' for a, b, y in tl)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
       f'<rect width="{W}" height="{H}" fill="#ffffff"/>\n' + '\n'.join(page) + '\n' + '\n'.join(text) + '\n' + links + '\n'
       f'<path d="{book}" fill="none" stroke="{ICON}" stroke-width="2" stroke-linejoin="round"/>\n'
       f'<path d="{page_lines}" fill="none" stroke="{ICON}" stroke-width="1.4" stroke-linecap="round"/>\n'
       f'<path d="{paper}" fill="none" stroke="{ICON}" stroke-width="2" stroke-linejoin="round"/>\n'
       f'{boxes}\n<path d="{paper_lines}" fill="none" stroke="{ICON}" stroke-width="2.2"/>\n</svg>\n')
open(OUT, 'w', encoding='utf8').write(svg)
print('wrote', OUT)
