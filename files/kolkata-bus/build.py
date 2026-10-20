"""Construct File:Kolkata bus.png from measured shapes (colours are the PNG's): sloped blue roof and body, light-blue
destination sign, grey windscreen frame with rounded corners and a centre pillar, yellow band, black grille and
bumper bars, outlined yellow headlights, black base. Run from the repo root."""
grille = ''.join(f'<rect x="126" y="{y}" width="127" height="8"/>' for y in (236, 250, 264, 278, 292, 306))
bumper = ''.join(f'<rect x="113" y="{y}" width="152" height="8"/>' for y in (325, 337))
lamps = ''.join(f'<rect x="{x}" y="{y}" width="45" height="29" rx="6" fill="#000000"/>'
                f'<rect x="{x + 3}" y="{y + 3}" width="39" height="23" rx="4" fill="#fff200"/>' for x, y in ((34, 323), (294, 322)))
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="371" height="388" viewBox="0 0 371 388">
<rect width="371" height="388" fill="#ffffff"/>
<path d="M12,24 L154,0 H233 L360,24 V193 H12 Z" fill="#00a2e8"/>
<rect x="12" y="288" width="348" height="71" fill="#00a2e8"/>
<rect x="12" y="197" width="348" height="91" fill="#ffc90e"/>
<rect x="154" y="3" width="79" height="21" fill="#d7f0f7"/>
<rect x="26" y="36" width="320" height="157" rx="16" fill="#7f7f7f"/>
<rect x="33" y="44" width="152" height="142" rx="8" fill="#d7f0f7"/>
<rect x="193" y="44" width="146" height="142" rx="8" fill="#d7f0f7"/>
<g fill="#000000">{grille}{bumper}<rect x="1" y="363" width="370" height="25"/></g>
{lamps}
</svg>
'''
open('files/kolkata-bus/Kolkata bus.svg', 'w', encoding='utf8').write(svg)
