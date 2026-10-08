"""Rebuild File:Japanese flag during the Kenmu Restoration.png: a nobori banner (white banner, brown pole and
top bar, white loops with grey outlines) with the sixteen-petal chrysanthemum of File:Imperial Seal of Japan.svg
recoloured gold. All positions are measured from the PNG. Run from the repo root.
"""
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / 'Japanese flag during the Kenmu Restoration.svg'
W, H = 607, 1052
BROWN, WHITE, LOOP_EDGE, GOLD, GOLD_LINE = '#421f09', '#ffffff', '#ada097', '#c6ac01', '#ffd700'
LEFT_LOOPS = [30, 100, 170, 240, 309, 379, 449, 519, 589, 658, 728, 798, 868]  # top rows, 15 px tall
TOP_LOOPS = [96, 167, 238, 309, 380, 451, 522]                                # left columns, 16 px wide
SEAL_C, SEAL_SCALE = (317, 310), 144 / 97  # seal petals reach r 97 in its own units


def main():
    loops = [f'<rect x="67" y="{y}" width="45" height="15"/>' for y in LEFT_LOOPS]
    loops += [f'<rect x="{x}" y="1" width="16" height="44"/>' for x in TOP_LOOPS]
    cx, cy = SEAL_C
    OUT.write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <title>Japanese flag during the Kenmu Restoration</title>
  <rect id="pole" x="67.5" y="0" width="18.5" height="1042" fill="{BROWN}"/>
  <rect id="bar" x="67" y="2" width="539" height="18" fill="{BROWN}"/>
  <rect id="banner" x="97" y="31" width="440" height="852" fill="{WHITE}"/>
  <g id="loops" style="fill:{WHITE};stroke:{LOOP_EDGE};stroke-width:1.5;stroke-dasharray:3,2">
    {chr(10).join('    ' + l for l in loops).strip()}
  </g>
  <g id="chrysanthemum" transform="translate({cx},{cy}) scale({SEAL_SCALE:.4f})">
    <use xlink:href="#o" transform="rotate(11.25)"/>
    <g id="o" stroke="{GOLD_LINE}" stroke-width="0.9" fill="{GOLD}"><g id="q"><g id="s"><g id="r">
      <path id="p" d="m0 0 81-16c22 0 22 32 0 32z"/>
      <use xlink:href="#p" transform="rotate(22.5)"/>
    </g><use xlink:href="#r" transform="rotate(45)"/>
    </g><use xlink:href="#s" transform="rotate(90)"/>
    </g><use xlink:href="#q" transform="rotate(180)"/>
    <circle r="13"/>
    </g>
  </g>
</svg>
''', encoding='utf8')
    print(OUT)


if __name__ == '__main__':
    main()
